"""Phase 6 Dreams Engine — per-character orchestration runner.

``run_dreams_pass`` iterates every canonical character, loads a
24-hour session snapshot for each, invokes the 5 content generators
(in parallel per character via ``asyncio.gather``), and writes outputs
back through ``writers``. This is the public API that the apscheduler
daemon (and the ``--once`` CLI) calls.

Round 1 remediation (F1 + F6):
- ``_empty_snapshot_loader`` retained as a test-only helper; the
  default runner now uses ``default_snapshot_loader`` which reads 24h
  of real session data.
- Writers (``dreams.writers``) are invoked inside a per-character
  ``session.begin()`` transaction so DreamsCharacterResult fields
  reflect real DB write outcomes.
- Consolidation helpers are invoked on the same session:
  ``refresh_somatic_decay``, ``expire_stale_loops``,
  ``resolve_addressed_loops``. (``apply_overnight_dyad_deltas`` is
  defined in ``consolidation.py`` but not yet invoked from the
  runner — no Dreams-computed delta source exists yet. See R3-F4 in
  PHASE_6.md.)
- Generators run in parallel per character via
  ``asyncio.gather(..., return_exceptions=True)`` with per-generator
  graceful failure semantics.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..canon.loader import Canon
from ..canon.routines_loader import get_routines
from ..canon.schemas.enums import CharacterID, _assert_complete_character_keys
from ..db.models.dyad_state_internal import DyadStateInternal
from ..db.models.dyad_state_whyze import DyadStateWhyze
from ..db.models.episodic_memory import EpisodicMemory
from ..db.models.life_state import LifeState
from ..db.models.open_loop import OpenLoop
from .config import DreamsSettings
from .consolidation import (
    expire_stale_loops,
    refresh_somatic_decay,
    resolve_addressed_loops,
)
from .errors import DreamsLLMError
from .generators import (
    generate_activity_design,
    generate_diary,
    generate_off_screen,
    generate_open_loops,
    generate_schedule,
)
from .types import (
    DreamsCharacterResult,
    DreamsPassResult,
    GenerationContext,
    GenerationOutput,
    LLMClient,
    SessionSnapshot,
)
from .writers import (
    write_activity,
    write_consolidation_log,
    write_diary_entry,
    write_new_open_loops,
    write_off_screen_events,
)

logger = logging.getLogger(__name__)


SessionFactory = Callable[[], Any]
SnapshotLoader = Callable[[AsyncSession, str, datetime], Awaitable[SessionSnapshot]]


# ---------------------------------------------------------------------------
# Snapshot loaders
# ---------------------------------------------------------------------------


async def _empty_snapshot_loader(
    session: AsyncSession, character_id: str, now: datetime
) -> SessionSnapshot:
    """Test-only loader: returns an empty snapshot.

    Retained for unit tests that want to exercise the runner without
    a populated DB. Production path uses ``default_snapshot_loader``.
    """
    return SessionSnapshot(character_id=character_id)


async def default_snapshot_loader(
    session: AsyncSession, character_id: str, now: datetime
) -> SessionSnapshot:
    """Production loader: reads 24h of session data for a character.

    Pulls:
    - episodic_memories from the last 24h owned by this character
    - currently-open open_loops for this character
    - dyad_state_whyze row for this character
    - dyad_state_internal rows where the character is a member
    - life_states row for this character (None if missing)

    Somatic state is intentionally NOT loaded here because the runner
    calls ``refresh_somatic_decay`` on the same session, which reads +
    writes the row atomically inside the transaction.
    """
    cutoff = now - timedelta(hours=24)

    epis_result = await session.execute(
        select(EpisodicMemory)
        .where(
            EpisodicMemory.character_id == character_id,
            EpisodicMemory.created_at >= cutoff,
        )
        .order_by(EpisodicMemory.created_at.desc())
        .limit(20)
    )
    episodic_memories = list(epis_result.scalars().all())

    loops_result = await session.execute(
        select(OpenLoop).where(
            OpenLoop.character_id == character_id,
            OpenLoop.status == "open",
        )
    )
    open_loops = list(loops_result.scalars().all())

    whyze_result = await session.execute(
        select(DyadStateWhyze).where(DyadStateWhyze.character_id == character_id)
    )
    dyad_states_whyze = list(whyze_result.scalars().all())

    internal_result = await session.execute(
        select(DyadStateInternal).where(
            (DyadStateInternal.member_a == character_id)
            | (DyadStateInternal.member_b == character_id)
        )
    )
    dyad_states_internal = list(internal_result.scalars().all())

    life_result = await session.execute(
        select(LifeState).where(LifeState.character_id == character_id)
    )
    life_state = life_result.scalars().first()

    return SessionSnapshot(
        character_id=character_id,
        episodic_memories=episodic_memories,
        open_loops=open_loops,
        somatic_state=None,  # refreshed inside the runner transaction
        dyad_states_whyze=dyad_states_whyze,
        dyad_states_internal=dyad_states_internal,
        life_state=life_state,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def run_dreams_pass(
    session_factory: SessionFactory,
    llm_client: LLMClient,
    canon: Canon,
    *,
    settings: DreamsSettings | None = None,
    now: datetime | None = None,
    snapshot_loader: SnapshotLoader | None = None,
) -> DreamsPassResult:
    """Run one Dreams pass across every canonical character.

    Args:
        session_factory: callable returning an ``AsyncSession`` (or an
            async-context-manager yielding one)
        llm_client: BDOne, StubBDOne, or anything satisfying the
            ``LLMClient`` protocol
        canon: loaded canon (must include routines — Phase 6 added this)
        settings: optional DreamsSettings; defaults to ``DreamsSettings()``
        now: dependency-injected clock for test determinism; defaults
            to ``datetime.now(UTC)``
        snapshot_loader: optional override; defaults to
            ``default_snapshot_loader``

    Returns:
        DreamsPassResult with per-character outcomes reflecting real
        DB write operations, aggregate token totals, and any warnings
        from partial failures.
    """
    if settings is None:
        settings = DreamsSettings()
    use_internal_clock = now is None
    if now is None:
        now = datetime.now(UTC)
    if snapshot_loader is None:
        snapshot_loader = default_snapshot_loader

    run_id = uuid.uuid4()
    started_at = now

    logger.info(
        "dreams_run_started",
        extra={"run_id": str(run_id), "started_at": started_at.isoformat()},
    )

    character_results: dict[str, DreamsCharacterResult] = {}
    warnings: list[str] = []
    total_input = 0
    total_output = 0

    for character_id in CharacterID.all_strings():
        try:
            result = await _process_character(
                run_id=run_id,
                character_id=character_id,
                canon=canon,
                llm_client=llm_client,
                session_factory=session_factory,
                settings=settings,
                now=now,
                snapshot_loader=snapshot_loader,
            )
            character_results[character_id] = result
            total_input += result.input_tokens
            total_output += result.output_tokens
            if result.warnings:
                warnings.extend(f"{character_id}: {w}" for w in result.warnings)
        except Exception as exc:  # noqa: BLE001 — orchestration must log + continue
            logger.exception(
                "dreams_character_failed",
                extra={"character_id": character_id, "run_id": str(run_id)},
            )
            warnings.append(f"{character_id}: {type(exc).__name__}: {exc}")
            character_results[character_id] = _empty_character_result(character_id, exc)

    _assert_complete_character_keys(character_results, "dreams.run_dreams_pass results")

    finished_at = datetime.now(UTC) if use_internal_clock else now
    logger.info(
        "dreams_run_complete",
        extra={
            "run_id": str(run_id),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "warnings_count": len(warnings),
        },
    )

    return DreamsPassResult(
        run_id=run_id,
        character_results=character_results,
        started_at=started_at,
        finished_at=finished_at,
        total_input_tokens=total_input,
        total_output_tokens=total_output,
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# Per-character pipeline
# ---------------------------------------------------------------------------


async def _run_one_generator(
    kind: str,
    generator: Callable[[GenerationContext], Awaitable[GenerationOutput]],
    ctx: GenerationContext,
) -> GenerationOutput:
    """Wrap a single generator call so asyncio.gather(return_exceptions=True)
    can surface ``DreamsLLMError`` and unexpected errors uniformly.

    If the generator raises, we re-raise (asyncio.gather captures it).
    Successful returns include their own ``warnings`` list which the
    runner propagates per generator.
    """
    return await generator(ctx)


async def _process_character(
    *,
    run_id: uuid.UUID,
    character_id: str,
    canon: Canon,
    llm_client: LLMClient,
    session_factory: SessionFactory,
    settings: DreamsSettings,
    now: datetime,
    snapshot_loader: SnapshotLoader,
) -> DreamsCharacterResult:
    """Per-character pipeline: snapshot → parallel generators → writers +
    consolidation inside a single transaction.

    F1 remediation: this now performs the full §9 read/write lifecycle,
    not just a shape-result.
    F6 remediation: generators run in parallel via asyncio.gather with
    per-generator graceful failure semantics.
    """
    logger.info("dreams_character_started", extra={"character_id": character_id})

    routines = get_routines(character_id)
    started_at = now

    async with session_factory() as session, session.begin():
        snapshot = await snapshot_loader(session, character_id, now)

        ctx = GenerationContext(
            character_id=character_id,
            canon=canon,
            routines=routines,
            prior_session=snapshot,
            llm_client=llm_client,
            now=now,
        )

        # F6: parallel generator fan-out with return_exceptions so one
        # generator's failure doesn't torpedo the others.
        gens: tuple[tuple[str, Callable[[GenerationContext], Awaitable[GenerationOutput]]], ...] = (
            ("schedule", generate_schedule),
            ("off_screen", generate_off_screen),
            ("diary", generate_diary),
            ("open_loops", generate_open_loops),
            ("activity_design", generate_activity_design),
        )
        gather_results = await asyncio.gather(
            *(_run_one_generator(kind, gen, ctx) for kind, gen in gens),
            return_exceptions=True,
        )

        outputs: dict[str, GenerationOutput] = {}
        warnings: list[str] = []
        for (kind, _), result in zip(gens, gather_results, strict=True):
            if isinstance(result, DreamsLLMError):
                warnings.append(f"{kind} generator LLM failure: {result}")
            elif isinstance(result, BaseException):
                warnings.append(
                    f"{kind} generator unexpected error: {type(result).__name__}: {result}"
                )
            else:
                outputs[kind] = result
                for w in result.warnings:
                    warnings.append(f"{kind}: {w}")

        # F1: invoke writers + consolidation inside the transaction.
        diary_entry_id: uuid.UUID | None = None
        off_screen_ids: list[uuid.UUID] = []
        new_loop_ids: list[uuid.UUID] = []
        activity_ids: list[uuid.UUID] = []

        if "diary" in outputs:
            try:
                diary_entry_id = await write_diary_entry(
                    session, character_id, outputs["diary"]
                )
            except Exception as exc:  # noqa: BLE001 — log + continue
                warnings.append(f"diary write failed: {type(exc).__name__}: {exc}")

        if "off_screen" in outputs:
            try:
                off_screen_ids = await write_off_screen_events(
                    session, character_id, outputs["off_screen"]
                )
            except Exception as exc:  # noqa: BLE001
                warnings.append(f"off_screen write failed: {type(exc).__name__}: {exc}")

        if "open_loops" in outputs:
            try:
                new_loop_ids = await write_new_open_loops(
                    session, character_id, outputs["open_loops"], now=now
                )
            except Exception as exc:  # noqa: BLE001
                warnings.append(f"open_loops write failed: {type(exc).__name__}: {exc}")

        if "activity_design" in outputs:
            try:
                activity_id = await write_activity(
                    session, character_id, outputs["activity_design"], now=now
                )
                activity_ids.append(activity_id)
            except Exception as exc:  # noqa: BLE001
                warnings.append(f"activity write failed: {type(exc).__name__}: {exc}")

        # Consolidation helpers on the same session.
        somatic_refreshed = False
        try:
            somatic_result = await refresh_somatic_decay(session, character_id, now)
            somatic_refreshed = somatic_result.applied
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"somatic refresh failed: {type(exc).__name__}: {exc}")

        open_loops_resolved = 0
        if "open_loops" in outputs:
            structured = outputs["open_loops"].structured_data
            if isinstance(structured, dict):
                resolved_ids_raw = structured.get("resolved_loop_ids") or []
                resolved_ids: list[uuid.UUID] = []
                for rid in resolved_ids_raw:
                    try:
                        resolved_ids.append(
                            rid if isinstance(rid, uuid.UUID) else uuid.UUID(str(rid))
                        )
                    except (ValueError, TypeError):
                        continue
                if resolved_ids:
                    try:
                        open_loops_resolved = await resolve_addressed_loops(
                            session, character_id, resolved_ids, now=now
                        )
                    except Exception as exc:  # noqa: BLE001
                        warnings.append(
                            f"resolve_addressed_loops failed: {type(exc).__name__}: {exc}"
                        )

        # Expire stale loops (character-agnostic bulk update is cheap).
        try:
            await expire_stale_loops(session, now)
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"expire_stale_loops failed: {type(exc).__name__}: {exc}")

        # Dyad deltas: currently no Dreams-computed deltas; Phase 6.1 / future
        # work will seed these from session analysis. Count remains 0 honestly.
        dyad_deltas_applied = 0

        # Write the consolidation log row last so its outputs_written mirrors
        # the actual state above.
        outputs_written: dict[str, Any] = {
            "diary_entry_id": str(diary_entry_id) if diary_entry_id else None,
            "off_screen_count": len(off_screen_ids),
            "new_open_loops_count": len(new_loop_ids),
            "activities_count": len(activity_ids),
            "open_loops_resolved": open_loops_resolved,
            "dyad_deltas_applied": dyad_deltas_applied,
            "somatic_refreshed": somatic_refreshed,
        }
        finished_at = datetime.now(UTC)
        try:
            await write_consolidation_log(
                session,
                run_id=run_id,
                character_id=character_id,
                started_at=started_at,
                finished_at=finished_at,
                outputs_written=outputs_written,
                warnings=warnings,
            )
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"consolidation_log write failed: {type(exc).__name__}: {exc}")

    input_tokens = sum(o.input_tokens for o in outputs.values())
    output_tokens = sum(o.output_tokens for o in outputs.values())

    logger.info(
        "dreams_character_complete",
        extra={
            "character_id": character_id,
            "diary_entry_id": str(diary_entry_id) if diary_entry_id else None,
            "off_screen_count": len(off_screen_ids),
            "new_open_loops_count": len(new_loop_ids),
            "activities_count": len(activity_ids),
            "somatic_refreshed": somatic_refreshed,
            "warnings_count": len(warnings),
        },
    )

    return DreamsCharacterResult(
        character_id=character_id,
        schedule_generated="schedule" in outputs,
        off_screen_events_count=len(off_screen_ids),
        diary_entry_id=diary_entry_id,
        open_loops_resolved=open_loops_resolved,
        open_loops_added=len(new_loop_ids),
        activities_designed=len(activity_ids),
        dyad_deltas_applied=dyad_deltas_applied,
        somatic_refreshed=somatic_refreshed,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        warnings=warnings,
    )


def _empty_character_result(character_id: str, exc: Exception) -> DreamsCharacterResult:
    """Placeholder result when a character's pass failed outright."""
    return DreamsCharacterResult(
        character_id=character_id,
        schedule_generated=False,
        off_screen_events_count=0,
        diary_entry_id=None,
        open_loops_resolved=0,
        open_loops_added=0,
        activities_designed=0,
        dyad_deltas_applied=0,
        somatic_refreshed=False,
        input_tokens=0,
        output_tokens=0,
        warnings=[f"character-level failure: {type(exc).__name__}: {exc}"],
    )
