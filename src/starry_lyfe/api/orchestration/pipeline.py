"""12-step request flow orchestration.

Implements the IMPLEMENTATION_PLAN_v7.1 §10 contract from Msty message
to validated SSE response. The full sequence:

    1.  Msty/OWUI sends OpenAI-compatible request
    2.  Msty Crew preprocessing + scene classification
    3.  Memory retrieval (canon + episodic + tier 8 Dreams state)
    4.  Activity-context auto-population from MemoryBundle.activities
    5.  Seven-layer prompt assembly
    6.  Stream upstream completion via BD-1
    7.  LLM honors Layer 7 constraints (no backend work)
    8.  Whyze-Byte validation on the buffered response
    9.  Sequential Crew validation (next speaker for multi-character)
    10. Validated response streamed back to client
    11. Shadow Persona is Msty-side, not backend
    12. Episodic memory extraction + relationship evaluator (post-stream)

Steps 9 + 12 (Crew bundling + post-turn fire-and-forget) live in their
own modules so this orchestrator stays a readable single function.
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from starry_lyfe.canon.loader import Canon
from starry_lyfe.context.assembler import assemble_context
from starry_lyfe.context.types import SceneState
from starry_lyfe.db.embed import EmbeddingService
from starry_lyfe.dreams.errors import DreamsLLMError
from starry_lyfe.dreams.llm import BDOne, StubBDOne
from starry_lyfe.scene.classifier import (
    SceneDirectorHints,
    SceneDirectorInput,
    classify_scene,
)
from starry_lyfe.validation.whyze_byte import ValidationResult, validate_response

from ..routing.character import CharacterRoutingDecision, strip_inline_override
from ..routing.msty import MstyPreprocessed
from ..schemas.chat import (
    ChatCompletionChunk,
    ChatCompletionChunkChoice,
    ChatCompletionDelta,
    ChatCompletionRequest,
)

logger = logging.getLogger(__name__)


@dataclass
class PipelineContext:
    """All inputs the 12-step flow needs to run.

    Constructed by the chat endpoint after auth + routing resolution;
    passed as a single immutable bundle so individual steps cannot
    mutate routing state mid-flow.
    """

    request: ChatCompletionRequest
    routing: CharacterRoutingDecision
    msty: MstyPreprocessed
    session: AsyncSession
    canon: Canon
    llm_client: BDOne | StubBDOne
    embedding_service: EmbeddingService
    request_id: str = field(default_factory=lambda: f"chat-{uuid.uuid4().hex[:12]}")


@dataclass
class PipelineResult:
    """Captured by the post-turn fire-and-forget tasks.

    Stored on ``app.state.last_pipeline_result`` for tests to assert
    against; production code never reads this field.
    """

    request_id: str
    character_id: str
    full_response_text: str
    validation: ValidationResult | None
    started_at: float
    finished_at: float


def _build_chunk(
    request_id: str,
    model: str,
    *,
    content: str | None = None,
    role: str | None = None,
    finish_reason: str | None = None,
    created: int | None = None,
) -> ChatCompletionChunk:
    return ChatCompletionChunk(
        id=request_id,
        created=created if created is not None else int(time.time()),
        model=model,
        choices=[
            ChatCompletionChunkChoice(
                index=0,
                delta=ChatCompletionDelta(role=role, content=content),  # type: ignore[arg-type]
                finish_reason=finish_reason,  # type: ignore[arg-type]
            )
        ],
    )


def _format_sse(chunk: ChatCompletionChunk) -> bytes:
    return f"data: {chunk.to_sse_data()}\n\n".encode()


def _format_done() -> bytes:
    return b"data: [DONE]\n\n"


def _format_error(message: str, code: str = "PIPELINE_ERROR") -> bytes:
    import json as _json

    payload = {"error": {"code": code, "message": message, "details": {}}}
    return f"data: {_json.dumps(payload)}\n\n".encode()


def _build_scene_state(
    ctx: PipelineContext,
    user_message_clean: str,
) -> SceneState:
    """Step 2: classify the scene from the routed character + Crew roster."""
    present = list(ctx.msty.scene_characters)
    if ctx.routing.character_id not in present:
        present.append(ctx.routing.character_id)
    director_input = SceneDirectorInput(
        user_message=user_message_clean,
        present_characters=present,
        alicia_home=True,  # Phase 7 default; Dreams life_state can override later
        hints=SceneDirectorHints(),
    )
    return classify_scene(director_input)


async def run_chat_pipeline(ctx: PipelineContext) -> AsyncIterator[bytes]:
    """Yield SSE-encoded bytes for the full 12-step flow.

    Each yielded bytes-string is an SSE event ready to be written to
    the wire by FastAPI's ``StreamingResponse``.
    """
    started_at = time.monotonic()

    # Step 2: Msty preprocessing already happened in the endpoint; inline
    # override is stripped here so the LLM sees clean user text.
    raw_user = ctx.msty.user_message or ""
    user_message_clean = strip_inline_override(raw_user)

    # Step 2b: scene classification.
    try:
        scene_state = _build_scene_state(ctx, user_message_clean)
    except Exception as exc:  # noqa: BLE001 — surface as terminal SSE chunk
        logger.warning("scene_classification_failed", exc_info=exc)
        yield _format_error(f"scene classification failed: {exc}", "SCENE_CLASSIFICATION_FAILED")
        yield _format_done()
        return

    # Steps 3-5: memory retrieval + 7-layer assembly. assemble_context
    # internally calls retrieve_memories (and Tier 8 activities feed into
    # Layer 6 per Phase 6 R3-F2). Step 4 activity_context auto-population
    # for the Scene Director is closed by the same retrieval — when Crew
    # mode advances to next-speaker scoring, the caller pulls it from
    # MemoryBundle.activities.
    try:
        prompt = await assemble_context(
            character_id=ctx.routing.character_id,
            scene_context=user_message_clean,
            scene_state=scene_state,
            session=ctx.session,
            embedding_service=ctx.embedding_service,
            canon=ctx.canon,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("context_assembly_failed", exc_info=exc)
        yield _format_error(f"context assembly failed: {exc}", "CONTEXT_ASSEMBLY_FAILED")
        yield _format_done()
        return

    # Step 1 of SSE: opening role chunk so OpenAI clients see an
    # assistant message.
    created = int(time.time())
    yield _format_sse(_build_chunk(ctx.request_id, ctx.routing.character_id, role="assistant", created=created))

    # Steps 6-7: stream the upstream completion.
    full_text_parts: list[str] = []
    try:
        async for delta in ctx.llm_client.stream_complete(
            system_prompt=prompt.prompt,
            user_prompt=user_message_clean,
            max_tokens=ctx.request.max_tokens or 1500,
            temperature=ctx.request.temperature if ctx.request.temperature is not None else 0.7,
        ):
            full_text_parts.append(delta)
            yield _format_sse(_build_chunk(
                ctx.request_id, ctx.routing.character_id, content=delta, created=created,
            ))
    except DreamsLLMError as exc:
        logger.warning("upstream_stream_failed", exc_info=exc)
        yield _format_error(f"upstream LLM failure: {exc}", "UPSTREAM_LLM_ERROR")
        yield _format_done()
        return

    full_text = "".join(full_text_parts)

    # Step 8: Whyze-Byte validation on the full buffered response.
    validation: ValidationResult | None = None
    try:
        validation = validate_response(
            character_id=ctx.routing.character_id,
            response_text=full_text,
            scene_state=scene_state,
        )
    except Exception as exc:  # noqa: BLE001 — validation MUST never wedge stream
        logger.warning("validation_failed_unexpectedly", exc_info=exc)

    # AC-7.12: Tier 1 FAIL violations land as a terminal error chunk so
    # downstream clients can flag the bad response. The response itself
    # has already been streamed (no way to retract); the error chunk is
    # the regenerate signal.
    if validation is not None and validation.fail_violations:
        codes = sorted({v.code for v in validation.fail_violations})
        yield _format_error(
            f"Whyze-Byte FAIL: {codes}", "WHYZE_BYTE_FAIL",
        )

    # Step 10: terminate the SSE stream with finish_reason + DONE.
    yield _format_sse(_build_chunk(
        ctx.request_id, ctx.routing.character_id,
        finish_reason="stop", created=created,
    ))
    yield _format_done()

    # Step 12: post-turn fire-and-forget (memory extraction + relationship
    # evaluator) is wired in P6. The pipeline returns the raw bundle so
    # the endpoint can hand it to ``schedule_post_turn_tasks``.
    finished_at = time.monotonic()
    result = PipelineResult(
        request_id=ctx.request_id,
        character_id=ctx.routing.character_id,
        full_response_text=full_text,
        validation=validation,
        started_at=started_at,
        finished_at=finished_at,
    )
    # Stash on the session for the endpoint to pick up. AsyncSession
    # already carries info dict via ``info``; we use it as a cheap side
    # channel so the orchestrator stays a pure async generator.
    ctx.session.info["pipeline_result"] = result
    # Yield nothing further — the generator end signals SSE close.


async def run_chat_pipeline_to_string(ctx: PipelineContext) -> str:
    """Helper for tests that want to assert on the joined SSE body.

    Drains the async generator into a single utf-8 string. Production
    code uses ``run_chat_pipeline`` directly via StreamingResponse.
    """
    parts: list[bytes] = []
    async for chunk in run_chat_pipeline(ctx):
        parts.append(chunk)
    # Give post-turn tasks a tick to settle — used only by tests that
    # assert on side effects after the stream completes.
    await asyncio.sleep(0)
    return b"".join(parts).decode("utf-8")
