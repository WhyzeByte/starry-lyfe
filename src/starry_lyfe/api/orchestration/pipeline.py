"""12-step request flow orchestration.

Implements the IMPLEMENTATION_PLAN_v7.1 §10 contract from Msty message
to validated SSE response. The full sequence:

    1.  Msty sends OpenAI-compatible request
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
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from starry_lyfe.canon.loader import Canon
from starry_lyfe.context.assembler import assemble_context
from starry_lyfe.context.types import SceneState
from starry_lyfe.db.embed import EmbeddingService
from starry_lyfe.db.models.dyad_state_internal import DyadStateInternal
from starry_lyfe.db.retrieval import MemoryBundle, retrieve_alicia_home, retrieve_memories
from starry_lyfe.dreams.errors import DreamsLLMError
from starry_lyfe.dreams.llm import BDOne, StubBDOne
from starry_lyfe.scene.classifier import (
    SceneDirectorHints,
    SceneDirectorInput,
    classify_scene,
)
from starry_lyfe.scene.errors import NoValidSpeakerError
from starry_lyfe.scene.next_speaker import (
    NextSpeakerInput,
    build_dyad_state_provider,
    select_next_speaker,
)
from starry_lyfe.scene.turn_history import TurnEntry
from starry_lyfe.validation.whyze_byte import ValidationResult, validate_response

from ..config import ApiSettings
from ..endpoints.metrics import http_sse_tokens_total
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
    # F1 2026-04-15: settings carry ``crew_max_speakers`` + F3
    # ``health_bd1_probe``. Optional so legacy tests that construct a
    # ``PipelineContext`` directly without an endpoint do not have to
    # fabricate one — Crew mode uses a default of 3 when absent.
    settings: ApiSettings | None = None
    request_id: str = field(default_factory=lambda: f"chat-{uuid.uuid4().hex[:12]}")


@dataclass
class PipelineResult:
    """Captured by the post-turn fire-and-forget tasks.

    Stored on ``app.state.last_pipeline_result`` for tests to assert
    against; production code never reads this field.

    F2 (2026-04-15) added ``scene_state`` so integration tests can
    inspect the resolved ``alicia_home`` value + present_characters
    without re-classifying.
    """

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


_CANONICAL_WOMEN: frozenset[str] = frozenset({"adelia", "bina", "reina", "alicia"})


def _is_crew_mode(ctx: PipelineContext) -> bool:
    """F1 2026-04-15: detect whether this request should expand multi-speaker.

    Crew mode fires when either:

    1. The routing decision raised the ``all_override`` flag (inline
       ``/all`` marker in the user message — any client), or
    2. The Msty preprocessor detected ≥2 canonical women in the roster
       AND at least one prior persona response exists (Msty Crew
       Conversations replay prior turns; an empty prior_responses list
       implies single-speaker chat even if the roster is named).

    Single-character front-door requests always return False.
    """
    if ctx.routing.all_override:
        return True
    women_in_roster = [c for c in ctx.msty.scene_characters if c in _CANONICAL_WOMEN]
    return len(women_in_roster) >= 2 and len(ctx.msty.prior_responses) >= 1


def _build_turn_history(ctx: PipelineContext) -> list[TurnEntry]:
    """F1 2026-04-15: reconstruct recent turns for ``select_next_speaker``.

    Prior persona responses become ``TurnEntry(speaker=X, addressed_to="whyze")``
    since Msty replays character lines without an explicit addressee. The
    current user message is appended as a Whyze turn addressed to the
    focal character; this gives the scorer the two-whyze-chain trigger
    needed by the Talk-to-Each-Other Mandate.
    """
    history: list[TurnEntry] = []
    for idx, prior in enumerate(ctx.msty.prior_responses):
        history.append(
            TurnEntry(speaker=prior.character_id, addressed_to="whyze", turn_index=idx)
        )
    history.append(
        TurnEntry(
            speaker="whyze",
            addressed_to=ctx.routing.character_id,
            turn_index=len(history),
        )
    )
    return history


def _build_activity_context(bundle: MemoryBundle | None) -> str | None:
    """F2 2026-04-15: concatenate recent Dreams activity narrations.

    Read by the scorer's Rule 7 (narrative salience) — a candidate whose
    name appears in an active activity's narrator_script receives the
    small salience boost documented in ``next_speaker.py``.
    """
    if bundle is None or not bundle.activities:
        return None
    scripts: list[str] = []
    for activity in bundle.activities:
        script = getattr(activity, "narrator_script", None)
        if script:
            scripts.append(str(script))
    if not scripts:
        return None
    return " ".join(scripts)


def _format_crew_prior_block(
    prior_validated_speakers: list[tuple[str, str]], current_user_message: str
) -> str:
    """R2-F1 2026-04-15: build the Step 9 carry-forward user_prompt.

    For speakers 2+ in a Crew turn, prepend the earlier speakers'
    validated text so the downstream LLM sees what preceded and can
    respond to it — the anti-"NPC Competition collapse" contract from
    ``IMPLEMENTATION_PLAN_v7.1.md §7`` / Step 9. Speaker 1 (empty list)
    gets the unchanged cleaned user message.

    Output format:

        [Earlier this turn:
        **Adelia:** <her validated text>

        **Bina:** <her validated text>
        ]

        <current cleaned user message>
    """
    if not prior_validated_speakers:
        return current_user_message
    chunks = [
        f"**{speaker.title()}:** {text}" for speaker, text in prior_validated_speakers
    ]
    joined = "\n\n".join(chunks)
    return f"[Earlier this turn:\n{joined}\n]\n\n{current_user_message}"


async def _retrieve_dyads_for_scene(
    session: AsyncSession, present_women: list[str]
) -> list[DyadStateInternal]:
    """F1 2026-04-15: pull every active dyad spanning two present women.

    ``MemoryBundle.dyad_states_internal`` only carries dyads for the
    focal character. Crew mode needs every pair among the roster so the
    scorer can read intimacy/tension deltas for each candidate.
    """
    if len(present_women) < 2:
        return []
    result = await session.execute(
        select(DyadStateInternal).where(
            DyadStateInternal.member_a.in_(present_women),
            DyadStateInternal.member_b.in_(present_women),
            DyadStateInternal.is_currently_active.is_(True),
        )
    )
    return list(result.scalars().all())


def _build_scene_state(
    ctx: PipelineContext,
    user_message_clean: str,
    *,
    alicia_home: bool,
) -> SceneState:
    """Step 2: classify the scene from the routed character + Crew roster.

    F2 (2026-04-15): ``alicia_home`` is now sourced by the caller from
    Tier 8 ``life_states`` via ``retrieve_alicia_home``. When Dreams has
    not yet populated Alicia's row the helper defaults to ``True``
    (Alicia home), preserving the pre-F2 behavior for fresh DBs.
    """
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


async def _run_crew_turn(
    *,
    ctx: PipelineContext,
    scene_state: SceneState,
    memory_bundle: MemoryBundle | None,
    user_message_clean: str,
    turn_history: list[TurnEntry],
    activity_context: str | None,
    dyad_provider: Any,
    already_spoken: list[str],
    full_text_parts: list[str],
    max_speakers: int,
    created: int,
) -> AsyncIterator[bytes]:
    """F1 2026-04-15: Step 9 — Crew sequencing multi-speaker loop.

    Yields SSE chunks for each selected speaker in turn. Each speaker
    gets their own 7-layer prompt via ``assemble_context`` so the focal
    kernel + soul cards match the speaker's canon. Per-speaker
    ``http_sse_tokens_total`` increments carry the character label.

    Wire format (per PHASE_7 §10 plan): single OpenAI-compatible SSE
    stream; attribution is inline markdown (``**Name:** …``) followed
    by the speaker's deltas, separated by ``\\n\\n`` between speakers.

    Termination:
    - ``max_speakers`` cap (CLAUDE.md §16 project axiom; default 3).
    - ``NoValidSpeakerError`` from ``select_next_speaker`` — remaining
      candidates zeroed by hard gates (Alicia away + in-person, or all
      already spoke this turn).
    - Eligible candidate pool exhausted.
    """
    eligible_count = sum(
        1 for c in scene_state.present_characters if c != "whyze"
    )
    cap = max(1, min(max_speakers, eligible_count))

    # Validated carry-forward state. Only speakers whose output passed
    # Whyze-Byte validation are appended here; later speakers see these
    # earlier validated entries prepended to their ``user_prompt`` via
    # ``_format_crew_prior_block``. FAIL'd or unvalidated text is not
    # forwarded — Step 9 promises later speakers see earlier VALIDATED
    # output, not raw failed generations.
    prior_validated_speakers: list[tuple[str, str]] = []

    for _turn in range(cap):
        if len(already_spoken) >= eligible_count:
            break
        speaker_input = NextSpeakerInput(
            scene_state=scene_state,
            turn_history=list(turn_history),
            dyad_state_provider=dyad_provider,
            in_turn_already_spoken=list(already_spoken),
            activity_context=activity_context,
        )
        try:
            decision = select_next_speaker(speaker_input)
        except NoValidSpeakerError:
            # All remaining candidates zeroed by hard gates — stop here.
            break
        speaker = decision.speaker

        # Per-speaker assemble_context: each speaker gets their own
        # focal kernel. The assembler accepts an optional memory_bundle;
        # we pass the focal-character bundle fetched at the pipeline
        # boundary only for the first speaker (its own rows); for
        # subsequent speakers we let the assembler fetch their own
        # bundle internally (one extra retrieval per extra speaker is
        # acceptable in Crew mode — Crew is rare).
        try:
            speaker_prompt = await assemble_context(
                character_id=speaker,
                scene_context=user_message_clean,
                scene_state=scene_state,
                session=ctx.session,
                embedding_service=ctx.embedding_service,
                canon=ctx.canon,
                memory_bundle=memory_bundle if speaker == ctx.routing.character_id else None,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "crew_assemble_failed_for_%s", speaker, exc_info=exc
            )
            # Skip this speaker and continue the loop; the turn can
            # still emit other speakers.
            already_spoken.append(speaker)
            continue

        # Attribution marker as its own content chunk. R2-F2 2026-04-15:
        # attribution is SSE frame content, not LLM output — it does NOT
        # increment http_sse_tokens_total. That counter tracks per-delta
        # LLM emissions uniformly across single-speaker and Crew paths.
        attribution = f"**{speaker.title()}:** "
        full_text_parts.append(attribution)
        yield _format_sse(_build_chunk(
            ctx.request_id, ctx.routing.character_id,
            content=attribution, created=created,
        ))

        # R2-F1 2026-04-15: speakers 2+ receive earlier validated text
        # prepended to their user_prompt via _format_crew_prior_block so
        # the LLM can respond to what preceded instead of generating in
        # isolation (the Talk-to-Each-Other Mandate's Step 9 contract).
        speaker_user_prompt = _format_crew_prior_block(
            prior_validated_speakers, user_message_clean
        )

        # Stream the speaker's completion.
        speaker_text_parts: list[str] = []
        async for delta in ctx.llm_client.stream_complete(
            system_prompt=speaker_prompt.prompt,
            user_prompt=speaker_user_prompt,
            max_tokens=ctx.request.max_tokens or 1500,
            temperature=ctx.request.temperature if ctx.request.temperature is not None else 0.7,
        ):
            speaker_text_parts.append(delta)
            full_text_parts.append(delta)
            http_sse_tokens_total.labels(character_id=speaker).inc()
            yield _format_sse(_build_chunk(
                ctx.request_id, ctx.routing.character_id,
                content=delta, created=created,
            ))

        speaker_full = "".join(speaker_text_parts)

        # Per-speaker Whyze-Byte validation. FAIL emits a warning chunk
        # but does not abort the Crew loop — other speakers still land.
        speaker_is_validated = False
        try:
            speaker_validation = validate_response(
                character_id=speaker,
                response_text=speaker_full,
                scene_state=scene_state,
            )
            if speaker_validation.fail_violations:
                codes = sorted({v.code for v in speaker_validation.fail_violations})
                yield _format_error(
                    f"Whyze-Byte FAIL for {speaker}: {codes}",
                    "WHYZE_BYTE_FAIL",
                )
            else:
                speaker_is_validated = speaker_validation.passed
        except Exception as exc:  # noqa: BLE001 — validation must never wedge
            logger.warning("crew_validation_failed_for_%s", speaker, exc_info=exc)

        # Persist only validated text for the next iteration's
        # carry-forward block. Failed or unvalidated output stays visible
        # to the client that already received it, but it is not fed into
        # later speakers as Step 9 context.
        if speaker_is_validated:
            prior_validated_speakers.append((speaker, speaker_full))

        # Separator between speakers.
        if _turn < cap - 1 and len(already_spoken) + 1 < eligible_count:
            separator = "\n\n"
            full_text_parts.append(separator)
            yield _format_sse(_build_chunk(
                ctx.request_id, ctx.routing.character_id,
                content=separator, created=created,
            ))

        already_spoken.append(speaker)
        turn_history.append(
            TurnEntry(
                speaker=speaker,
                addressed_to="whyze",
                turn_index=len(turn_history),
            )
        )


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

    # Step 2a (F2 2026-04-15): Resolve alicia_home from Tier 8 life_states
    # BEFORE scene classification. A missing row defaults to home=True.
    try:
        alicia_home = await retrieve_alicia_home(ctx.session)
    except Exception as exc:  # noqa: BLE001 — degraded retrieval must not wedge flow
        logger.warning("alicia_home_resolution_failed", exc_info=exc)
        alicia_home = True

    # Step 2b: scene classification.
    try:
        scene_state = _build_scene_state(
            ctx, user_message_clean, alicia_home=alicia_home
        )
    except Exception as exc:  # noqa: BLE001 — surface as terminal SSE chunk
        logger.warning("scene_classification_failed", exc_info=exc)
        yield _format_error(f"scene classification failed: {exc}", "SCENE_CLASSIFICATION_FAILED")
        yield _format_done()
        return

    # Step 3 (F2 2026-04-15): retrieve memories once at the pipeline
    # boundary so the bundle is available to both the Scene Director
    # (activity_context in Crew mode) and the assembler. Passing the
    # bundle via ``memory_bundle=`` keyword avoids a duplicate DB round
    # trip inside ``assemble_context``.
    memory_bundle: MemoryBundle | None = None
    try:
        memory_bundle = await retrieve_memories(
            session=ctx.session,
            embedding_service=ctx.embedding_service,
            scene_context=user_message_clean,
            character_id=ctx.routing.character_id,
            present_characters=scene_state.present_characters,
        )
    except Exception as exc:  # noqa: BLE001 — degraded retrieval logs + falls back
        logger.warning("memory_retrieval_failed", exc_info=exc)
        memory_bundle = None

    # Steps 4-5: 7-layer prompt assembly. Pre-fetched bundle is handed in
    # so the assembler skips its internal retrieve_memories call.
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
        yield _format_error(f"context assembly failed: {exc}", "CONTEXT_ASSEMBLY_FAILED")
        yield _format_done()
        return

    # Step 1 of SSE: opening role chunk so OpenAI clients see an
    # assistant message.
    created = int(time.time())
    yield _format_sse(_build_chunk(ctx.request_id, ctx.routing.character_id, role="assistant", created=created))

    # F1 2026-04-15: Crew-mode branching. Single-speaker path is the
    # default; Crew mode fires when _is_crew_mode returns True.
    full_text_parts: list[str] = []
    validation: ValidationResult | None = None

    if _is_crew_mode(ctx):
        # Step 9 (F1 closure): multi-speaker Crew expansion.
        activity_context = _build_activity_context(memory_bundle)
        turn_history = _build_turn_history(ctx)
        try:
            dyad_rows = await _retrieve_dyads_for_scene(
                ctx.session, scene_state.present_characters
            )
        except Exception as exc:  # noqa: BLE001 — degraded dyad read must not wedge
            logger.warning("dyad_retrieval_failed", exc_info=exc)
            dyad_rows = []
        dyad_provider = build_dyad_state_provider(dyad_rows)
        max_speakers = getattr(ctx.settings, "crew_max_speakers", 3) if ctx.settings else 3

        already_spoken: list[str] = []
        try:
            async for chunk in _run_crew_turn(
                ctx=ctx,
                scene_state=scene_state,
                memory_bundle=memory_bundle,
                user_message_clean=user_message_clean,
                turn_history=turn_history,
                activity_context=activity_context,
                dyad_provider=dyad_provider,
                already_spoken=already_spoken,
                full_text_parts=full_text_parts,
                max_speakers=max_speakers,
                created=created,
            ):
                yield chunk
        except DreamsLLMError as exc:
            logger.warning("crew_upstream_stream_failed", exc_info=exc)
            yield _format_error(f"upstream LLM failure: {exc}", "UPSTREAM_LLM_ERROR")
            yield _format_done()
            return
    else:
        # Steps 6-7: single-speaker stream.
        try:
            async for delta in ctx.llm_client.stream_complete(
                system_prompt=prompt.prompt,
                user_prompt=user_message_clean,
                max_tokens=ctx.request.max_tokens or 1500,
                temperature=ctx.request.temperature if ctx.request.temperature is not None else 0.7,
            ):
                full_text_parts.append(delta)
                http_sse_tokens_total.labels(character_id=ctx.routing.character_id).inc()
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
        try:
            validation = validate_response(
                character_id=ctx.routing.character_id,
                response_text=full_text,
                scene_state=scene_state,
            )
        except Exception as exc:  # noqa: BLE001 — validation MUST never wedge stream
            logger.warning("validation_failed_unexpectedly", exc_info=exc)

        # AC-7.12: Tier 1 FAIL violations land as a terminal error chunk so
        # downstream clients can flag the bad response.
        if validation is not None and validation.fail_violations:
            codes = sorted({v.code for v in validation.fail_violations})
            yield _format_error(
                f"Whyze-Byte FAIL: {codes}", "WHYZE_BYTE_FAIL",
            )

    full_text = "".join(full_text_parts)

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
        scene_state=scene_state,
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
