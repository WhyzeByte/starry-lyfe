"""Phase 6 Dreams Engine — per-character orchestration runner.

``run_dreams_pass`` iterates every canonical character, loads a
24-hour session snapshot for each, invokes the 5 content generators in
parallel, and writes outputs back through ``writers``. This is the
public API that the apscheduler daemon (and the ``--once`` CLI) calls.

Generators are imported from ``dreams.generators``; commit 4 ships
placeholder stubs, commit 5 replaces the diary stub with the real
LLM-backed implementation, and commit 5+ replaces the remaining four.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from ..canon.loader import Canon
from ..canon.routines_loader import get_routines
from ..canon.schemas.enums import CharacterID, _assert_complete_character_keys
from .config import DreamsSettings
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

logger = logging.getLogger(__name__)


SessionFactory = Callable[[], AsyncSession]
SnapshotLoader = Callable[[AsyncSession, str, datetime], Awaitable[SessionSnapshot]]


async def _empty_snapshot_loader(
    session: AsyncSession, character_id: str, now: datetime
) -> SessionSnapshot:
    """Commit-4 placeholder loader: returns an empty snapshot.

    Replaced in commit 8 (J6 integration test wiring) by a real loader
    that reads yesterday's episodic memories, open loops, somatic state,
    dyad state, and life state. Keeping the signature stable now so
    ``run_dreams_pass`` does not need to change when the loader swaps.
    """
    return SessionSnapshot(character_id=character_id)


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
        session_factory: callable returning a fresh ``AsyncSession``
        llm_client: BDOne, StubBDOne, or anything satisfying the
            ``LLMClient`` protocol
        canon: loaded canon (must include routines — Phase 6 added this)
        settings: optional DreamsSettings; defaults to ``DreamsSettings()``
        now: dependency-injected clock for test determinism; defaults
            to ``datetime.now(UTC)``
        snapshot_loader: optional override for the session-snapshot
            loader; default is the empty-snapshot stub (commit 4)

    Returns:
        DreamsPassResult with per-character outcomes, aggregate token
        totals, and any warnings from partial failures.
    """
    if settings is None:
        settings = DreamsSettings()
    if now is None:
        now = datetime.now(UTC)
    if snapshot_loader is None:
        snapshot_loader = _empty_snapshot_loader

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

    finished_at = datetime.now(UTC) if now is None else now
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


async def _process_character(
    *,
    character_id: str,
    canon: Canon,
    llm_client: LLMClient,
    session_factory: SessionFactory,
    settings: DreamsSettings,
    now: datetime,
    snapshot_loader: SnapshotLoader,
) -> DreamsCharacterResult:
    """Run the per-character pipeline: snapshot → generators → writers."""
    logger.info(
        "dreams_character_started",
        extra={"character_id": character_id},
    )

    routines = get_routines(character_id)

    async with session_factory() as session:
        snapshot = await snapshot_loader(session, character_id, now)

    ctx = GenerationContext(
        character_id=character_id,
        canon=canon,
        routines=routines,
        prior_session=snapshot,
        llm_client=llm_client,
        now=now,
    )

    outputs: dict[str, GenerationOutput] = {}
    warnings: list[str] = []
    for kind, generator in (
        ("schedule", generate_schedule),
        ("off_screen", generate_off_screen),
        ("diary", generate_diary),
        ("open_loops", generate_open_loops),
        ("activity_design", generate_activity_design),
    ):
        try:
            output = await generator(ctx)
            outputs[kind] = output
            # Propagate generator-level warnings into the per-character aggregate
            # so the caller can see them via DreamsCharacterResult.warnings.
            for w in output.warnings:
                warnings.append(f"{kind}: {w}")
        except DreamsLLMError as exc:
            warnings.append(f"{kind} generator LLM failure: {exc}")
        except Exception as exc:  # noqa: BLE001 — per-generator graceful degradation
            warnings.append(f"{kind} generator unexpected error: {type(exc).__name__}: {exc}")

    # Dry-run short-circuits writers; production path would persist outputs here.
    # Writer wiring lands in a subsequent commit alongside the real diary generator.
    input_tokens = sum(o.input_tokens for o in outputs.values())
    output_tokens = sum(o.output_tokens for o in outputs.values())

    schedule_output = outputs.get("schedule")
    activity_output = outputs.get("activity_design")
    off_screen_output = outputs.get("off_screen")
    open_loops_output = outputs.get("open_loops")

    off_screen_count = (
        len(off_screen_output.structured_data.get("events", []))
        if off_screen_output is not None
        else 0
    )
    open_loops_added = (
        len(open_loops_output.structured_data.get("new_loops", []))
        if open_loops_output is not None
        else 0
    )

    logger.info(
        "dreams_character_complete",
        extra={
            "character_id": character_id,
            "outputs_produced": list(outputs.keys()),
            "warnings_count": len(warnings),
        },
    )

    return DreamsCharacterResult(
        character_id=character_id,
        schedule_generated=schedule_output is not None,
        off_screen_events_count=off_screen_count,
        diary_entry_id=None,  # Populated once writers land.
        open_loops_resolved=0,
        open_loops_added=open_loops_added,
        activities_designed=1 if activity_output is not None else 0,
        dyad_deltas_applied=0,
        somatic_refreshed=False,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        warnings=warnings,
    )


def _empty_character_result(character_id: str, exc: Exception) -> DreamsCharacterResult:
    """Placeholder result when a character's pass failed outright.

    Keeps the per-character coverage invariant (_assert_complete_character_keys)
    satisfied even when orchestration failed for one character.
    """
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
