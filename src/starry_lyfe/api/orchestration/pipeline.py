"""HTTP chat request flow orchestration.

Implements the runtime contract from Msty message to validated SSE
response. Msty Crew bubble orchestration is client-side: each backend
request still produces exactly one assistant response for the routed
persona. **Phase 11 (2026-04-17):** when the incoming history carries
prior personas' assistant turns (Msty Crew Conversations in Contextual
mode), `_format_crew_prior_block` injects them into the focal persona's
``user_prompt`` so the focal persona can riff on what the prior personas
said. The injection is a no-op when ``prior_responses`` is empty,
preserving Phase H regression byte-identity for non-crew flows.
"""

from __future__ import annotations

import asyncio
import html
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
from starry_lyfe.db.retrieval import MemoryBundle, retrieve_alicia_home, retrieve_memories
from starry_lyfe.dreams.errors import DreamsLLMError
from starry_lyfe.dreams.llm import BDOne, StubBDOne
from starry_lyfe.scene.classifier import (
    SceneDirectorHints,
    SceneDirectorInput,
    classify_scene,
)
from starry_lyfe.validation.whyze_byte import ValidationResult, validate_response

from ..config import ApiSettings
from ..endpoints.metrics import http_sse_tokens_total
from ..routing.character import CharacterRoutingDecision, strip_inline_override
from ..routing.msty import MstyPreprocessed, PriorResponse
from ..schemas.chat import (
    ChatCompletionChunk,
    ChatCompletionChunkChoice,
    ChatCompletionDelta,
    ChatCompletionRequest,
)

# Phase 11: per-block char cap before truncation marker. Defends against
# a runaway prior-persona response chewing the focal persona's prompt
# budget. 800 chars is roughly 200 tokens — enough to carry a short turn
# verbatim without dominating Layer 1.
_PRIOR_BLOCK_CHAR_CAP: int = 800
_PRIOR_BLOCK_TRUNCATION_MARKER: str = " […truncated]"

logger = logging.getLogger(__name__)


@dataclass
class PipelineContext:
    """All inputs the chat flow needs to run."""

    request: ChatCompletionRequest
    routing: CharacterRoutingDecision
    msty: MstyPreprocessed
    session: AsyncSession
    canon: Canon
    llm_client: BDOne | StubBDOne
    embedding_service: EmbeddingService
    # Optional so tests can construct ``PipelineContext`` directly
    # without fabricating a full endpoint state.
    settings: ApiSettings | None = None
    request_id: str = field(default_factory=lambda: f"chat-{uuid.uuid4().hex[:12]}")


@dataclass
class PipelineResult:
    """Captured by the post-turn fire-and-forget tasks."""

    request_id: str
    character_id: str
    full_response_text: str
    validation: ValidationResult | None
    started_at: float
    finished_at: float
    scene_state: SceneState | None = None


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


def _format_crew_prior_block(
    prior_responses: list[PriorResponse],
    current_user_message: str,
) -> str:
    """Phase 11: prepend a cross-persona context frame to the user prompt.

    When Msty Studio runs a Crew Conversation in Contextual mode (per
    https://docs.msty.studio/conversations/crew-chats step 5 — *"Contextual
    where they are aware of persona responses before theirs"*), it fans
    out one HTTP request per persona's turn. Prior personas' responses
    arrive as ``role="assistant"`` messages with a ``name`` field set to
    the persona id. ``MstyPreprocessed.prior_responses`` carries them in
    chronological order.

    This helper renders those prior turns as a clearly-framed block in
    front of the current user message so the focal persona can riff on
    what the prior personas said (rather than answering the user as if
    speaking alone). When ``prior_responses`` is empty, the helper
    returns ``current_user_message`` unchanged — the no-op case
    preserves Phase H regression byte-identity for non-crew flows.

    Sanitation (Phase 8 R1-F3 lesson): each prior block is HTML-escaped
    via ``html.escape(text, quote=False)`` so a payload containing
    ``</response>`` or other markup cannot break the prompt frame, and
    truncated to ``_PRIOR_BLOCK_CHAR_CAP`` characters with a
    ``[…truncated]`` marker so a runaway prior response cannot dominate
    the focal persona's budget.

    Args:
        prior_responses: Chronological list of prior persona turns
            extracted by ``_extract_prior_responses``.
        current_user_message: The latest user-role message (already
            stripped of inline overrides).

    Returns:
        Either the bare ``current_user_message`` (no-op) or a frame:

            [Earlier in this conversation:
            **adelia:** <escaped, truncated text>
            **bina:** ...
            ]

            <current_user_message>
    """
    if not prior_responses:
        return current_user_message
    lines = ["[Earlier in this conversation:"]
    for prior in prior_responses:
        escaped = html.escape(prior.text or "", quote=False)
        if len(escaped) > _PRIOR_BLOCK_CHAR_CAP:
            escaped = (
                escaped[:_PRIOR_BLOCK_CHAR_CAP].rstrip()
                + _PRIOR_BLOCK_TRUNCATION_MARKER
            )
        lines.append(f"**{prior.character_id}:** {escaped}")
    lines.append("]")
    lines.append("")
    lines.append(current_user_message)
    return "\n".join(lines)


def _build_scene_state(
    ctx: PipelineContext,
    user_message_clean: str,
    *,
    alicia_home: bool,
) -> SceneState:
    """Classify the scene from the routed character plus Crew roster."""

    present = list(ctx.msty.scene_characters)
    if ctx.routing.character_id not in present:
        present.append(ctx.routing.character_id)
    director_input = SceneDirectorInput(
        user_message=user_message_clean,
        present_characters=present,
        alicia_home=alicia_home,
        hints=SceneDirectorHints(),
    )
    return classify_scene(director_input)


async def run_chat_pipeline(ctx: PipelineContext) -> AsyncIterator[bytes]:
    """Yield SSE-encoded bytes for the chat flow."""

    started_at = time.monotonic()

    # Msty preprocessing already happened in the endpoint; inline
    # overrides and legacy ``/all`` are stripped here so the LLM sees
    # clean user text.
    raw_user = ctx.msty.user_message or ""
    user_message_clean = strip_inline_override(raw_user)

    # Phase 11: when Msty Crew Conversations Contextual mode delivers
    # prior personas' assistant turns alongside the user message, prepend
    # them as a framed prior-speaker block so the focal persona can riff
    # on what the prior personas said. No-op when ``prior_responses`` is
    # empty (preserves Phase H regression for non-crew flows). The
    # augmented string is what reaches BD-1; ``user_message_clean``
    # remains the input to scene classification + Layer 6 retrieval so
    # soul-card activation does not over-trigger on cross-persona text.
    user_prompt_with_priors = _format_crew_prior_block(
        list(ctx.msty.prior_responses),
        user_message_clean,
    )

    # Resolve alicia_home from Tier 8 life_states before classification.
    try:
        alicia_home = await retrieve_alicia_home(ctx.session)
    except Exception as exc:  # noqa: BLE001
        logger.warning("alicia_home_resolution_failed", exc_info=exc)
        alicia_home = True

    try:
        scene_state = _build_scene_state(
            ctx, user_message_clean, alicia_home=alicia_home
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("scene_classification_failed", exc_info=exc)
        yield _format_error(
            f"scene classification failed: {exc}",
            "SCENE_CLASSIFICATION_FAILED",
        )
        yield _format_done()
        return

    # Retrieve memories once at the pipeline boundary so the assembler
    # can reuse the bundle rather than hitting the DB twice.
    memory_bundle: MemoryBundle | None = None
    try:
        memory_bundle = await retrieve_memories(
            session=ctx.session,
            embedding_service=ctx.embedding_service,
            scene_context=user_message_clean,
            character_id=ctx.routing.character_id,
            present_characters=scene_state.present_characters,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("memory_retrieval_failed", exc_info=exc)
        memory_bundle = None

    try:
        prompt = await assemble_context(
            character_id=ctx.routing.character_id,
            scene_context=user_message_clean,
            scene_state=scene_state,
            session=ctx.session,
            embedding_service=ctx.embedding_service,
            canon=ctx.canon,
            memory_bundle=memory_bundle,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("context_assembly_failed", exc_info=exc)
        yield _format_error(
            f"context assembly failed: {exc}",
            "CONTEXT_ASSEMBLY_FAILED",
        )
        yield _format_done()
        return

    # Opening role chunk so OpenAI clients see an assistant message.
    created = int(time.time())
    yield _format_sse(
        _build_chunk(
            ctx.request_id,
            ctx.routing.character_id,
            role="assistant",
            created=created,
        )
    )

    full_text_parts: list[str] = []
    validation: ValidationResult | None = None

    # Single-speaker stream. Msty Crew still reaches the backend one
    # persona request at a time; the roster informs scene classification
    # and Layer 6 retrieval, and (Phase 11) any prior-persona turns are
    # injected into ``user_prompt_with_priors`` so the focal persona
    # sees what the other personas just said.
    try:
        async for delta in ctx.llm_client.stream_complete(
            system_prompt=prompt.prompt,
            user_prompt=user_prompt_with_priors,
            max_tokens=ctx.request.max_tokens or 1500,
            temperature=ctx.request.temperature if ctx.request.temperature is not None else 0.7,
        ):
            full_text_parts.append(delta)
            http_sse_tokens_total.labels(character_id=ctx.routing.character_id).inc()
            yield _format_sse(
                _build_chunk(
                    ctx.request_id,
                    ctx.routing.character_id,
                    content=delta,
                    created=created,
                )
            )
    except DreamsLLMError as exc:
        logger.warning("upstream_stream_failed", exc_info=exc)
        yield _format_error(f"upstream LLM failure: {exc}", "UPSTREAM_LLM_ERROR")
        yield _format_done()
        return

    full_text = "".join(full_text_parts)

    try:
        validation = validate_response(
            character_id=ctx.routing.character_id,
            response_text=full_text,
            scene_state=scene_state,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("validation_failed_unexpectedly", exc_info=exc)

    if validation is not None and validation.fail_violations:
        codes = sorted({v.code for v in validation.fail_violations})
        yield _format_error(
            f"Whyze-Byte FAIL: {codes}",
            "WHYZE_BYTE_FAIL",
        )

    yield _format_sse(
        _build_chunk(
            ctx.request_id,
            ctx.routing.character_id,
            finish_reason="stop",
            created=created,
        )
    )
    yield _format_done()

    finished_at = time.monotonic()
    result = PipelineResult(
        request_id=ctx.request_id,
        character_id=ctx.routing.character_id,
        full_response_text=full_text,
        validation=validation,
        started_at=started_at,
        finished_at=finished_at,
        scene_state=scene_state,
    )
    ctx.session.info["pipeline_result"] = result


async def run_chat_pipeline_to_string(ctx: PipelineContext) -> str:
    """Helper for tests that want to assert on the joined SSE body."""

    parts: list[bytes] = []
    async for chunk in run_chat_pipeline(ctx):
        parts.append(chunk)
    await asyncio.sleep(0)
    return b"".join(parts).decode("utf-8")
