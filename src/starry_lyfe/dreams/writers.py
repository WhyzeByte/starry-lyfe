"""Phase 6 Dreams writers — persist generator outputs into the DB.

Five writer functions, one per Dreams output type. Each is async,
idempotent where possible, and takes an ``AsyncSession`` that the
runner's per-character transaction owns. Writers do NOT call
``session.commit()`` themselves — the runner's ``session.begin()``
block handles the transaction.

Per F1 remediation: these replace the previous "no writer path" state
where `run_dreams_pass` returned success-shaped results without any DB
state change.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from ..db.models.activity import Activity
from ..db.models.consolidation_log import ConsolidationLog
from ..db.models.episodic_memory import EMBEDDING_DIMENSION, EpisodicMemory
from ..db.models.open_loop import OpenLoop
from .types import GenerationOutput

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

# Activity rows live for 24h by default — next Dreams run overwrites.
_ACTIVITY_TTL_HOURS: int = 24

# New open loops default to a 7-day TTL matching OpenLoop.ttl_hours default.
_NEW_LOOP_DEFAULT_TTL_HOURS: int = 168

# Dreams-generated episodic memories need an embedding per schema contract.
# We write a zero vector by default; real embedding could be wired via
# EmbeddingService in a follow-up commit. The zero vector is inert for
# similarity search (cosine distance will rank lower than real embeddings).
_ZERO_EMBEDDING: list[float] = [0.0] * EMBEDDING_DIMENSION


async def write_diary_entry(
    session: AsyncSession,
    character_id: str,
    output: GenerationOutput,
    *,
    session_id: uuid.UUID | None = None,
) -> uuid.UUID:
    """Insert a diary EpisodicMemory row. Returns the new row's UUID.

    Diary entries carry memory_type='diary', participant_ids=[character_id],
    and event_summary=output.rendered_prose (Phase G wrapped). Alicia-away
    entries carry the communication_mode from structured_data.
    """
    comm_mode = output.structured_data.get("communication_mode") if isinstance(
        output.structured_data, dict
    ) else None
    row = EpisodicMemory(
        session_id=session_id,
        character_id=character_id,
        participant_ids={"ids": [character_id]},
        event_summary=output.rendered_prose,
        emotional_temperature=None,
        memory_type="diary",
        importance_score=0.6,
        embedding=_ZERO_EMBEDDING,
        metadata_={
            "source": "dreams",
            "kind": "diary",
            "raw_llm_text": output.raw_llm_text,
        },
        communication_mode=comm_mode,
    )
    session.add(row)
    await session.flush()
    return row.id


async def write_activity(
    session: AsyncSession,
    character_id: str,
    output: GenerationOutput,
    *,
    now: datetime,
) -> uuid.UUID:
    """Insert an Activity row for tomorrow's scene opener.

    expires_at defaults to now + 24h (next Dreams run invalidates).
    Alicia-away activities carry the communication_mode tag.
    """
    structured = output.structured_data if isinstance(output.structured_data, dict) else {}
    comm_mode = structured.get("communication_mode")
    choice_tree = structured.get("choice_tree") or {}
    narrator_script = structured.get("narrator_script") or output.rendered_prose
    scene_description = structured.get("scene_description") or output.rendered_prose

    row = Activity(
        character_id=character_id,
        scene_description=scene_description,
        narrator_script=narrator_script,
        choice_tree=choice_tree,
        communication_mode=comm_mode,
        expires_at=now + timedelta(hours=_ACTIVITY_TTL_HOURS),
    )
    session.add(row)
    await session.flush()
    return row.id


async def write_new_open_loops(
    session: AsyncSession,
    character_id: str,
    output: GenerationOutput,
    *,
    now: datetime,
    source_session_id: uuid.UUID | None = None,
) -> list[uuid.UUID]:
    """Insert OpenLoop rows for each new loop extracted by the generator.

    Expects output.structured_data["new_loops"] to be a list of dicts with
    keys {summary, urgency, loop_type?, best_next_speaker?, suggested_scene?}.
    Returns the UUIDs of the newly-inserted rows.
    """
    structured = output.structured_data if isinstance(output.structured_data, dict) else {}
    new_loops = structured.get("new_loops") or []
    written: list[uuid.UUID] = []

    for loop in new_loops:
        if not isinstance(loop, dict):
            continue
        summary = loop.get("summary")
        if not summary:
            continue
        ttl = int(loop.get("ttl_hours", _NEW_LOOP_DEFAULT_TTL_HOURS))
        row = OpenLoop(
            character_id=character_id,
            loop_summary=str(summary),
            loop_type=str(loop.get("loop_type") or "unresolved_thread"),
            urgency=str(loop.get("urgency") or "medium"),
            best_next_speaker=loop.get("best_next_speaker"),
            suggested_scene=loop.get("suggested_scene"),
            source_session_id=source_session_id,
            status="open",
            ttl_hours=ttl,
            expires_at=now + timedelta(hours=ttl),
        )
        session.add(row)
        written.append(row.id)

    if written:
        await session.flush()
    return written


async def write_off_screen_events(
    session: AsyncSession,
    character_id: str,
    output: GenerationOutput,
    *,
    session_id: uuid.UUID | None = None,
) -> list[uuid.UUID]:
    """Insert EpisodicMemory rows (memory_type='off_screen') for each event.

    Off-screen events are the overnight narrative the character accrues while
    Whyze is absent. Expects output.structured_data["events"] to be a list
    of dicts with at least a ``summary`` key.
    """
    structured = output.structured_data if isinstance(output.structured_data, dict) else {}
    events = structured.get("events") or []
    comm_mode = structured.get("communication_mode")
    written: list[uuid.UUID] = []

    for event in events:
        if not isinstance(event, dict):
            continue
        summary = event.get("summary")
        if not summary:
            continue
        importance = float(event.get("importance_score") or 0.4)
        row = EpisodicMemory(
            session_id=session_id,
            character_id=character_id,
            participant_ids={"ids": [character_id]},
            event_summary=str(summary),
            emotional_temperature=None,
            memory_type="off_screen",
            importance_score=importance,
            embedding=_ZERO_EMBEDDING,
            metadata_={
                "source": "dreams",
                "kind": "off_screen",
                "when": event.get("when"),
                "mood": event.get("mood"),
            },
            communication_mode=comm_mode,
        )
        session.add(row)
        written.append(row.id)

    if written:
        await session.flush()
    return written


async def write_consolidation_log(
    session: AsyncSession,
    *,
    run_id: uuid.UUID,
    character_id: str,
    started_at: datetime,
    finished_at: datetime,
    outputs_written: dict[str, Any],
    warnings: list[str],
) -> uuid.UUID:
    """Insert a ConsolidationLog row at the end of each per-character pass.

    outputs_written is a JSONB dict summarizing what was written; warnings
    is the flat list aggregated by the runner.
    """
    row = ConsolidationLog(
        run_id=run_id,
        character_id=character_id,
        started_at=started_at,
        finished_at=finished_at,
        outputs_written=outputs_written,
        warnings={"list": list(warnings)},
    )
    session.add(row)
    await session.flush()
    return row.id
