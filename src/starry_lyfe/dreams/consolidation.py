"""Phase 6 Dreams consolidation helpers (Subsystem F).

These functions are called by the runner after generator outputs are
collected. They operate on the DB: refresh somatic decay, apply
overnight dyad deltas (capped), expire stale open loops, and mark
loops as resolved by the Dreams run.

Each helper is async, takes an AsyncSession, and is idempotent: calling
twice with the same ``now`` and no interleaved writes produces the same
end state.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import select, update

from ..db.decay import apply_decay
from ..db.models.dyad_state_internal import DyadStateInternal
from ..db.models.dyad_state_whyze import DyadStateWhyze
from ..db.models.open_loop import OpenLoop
from ..db.models.transient_somatic import TransientSomaticState

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Tunable: dyad-delta ceiling per Dreams pass. Runtime per-turn is ±0.03
# (see CLAUDE.md §16 "Relationship evaluator fires every turn"); Dreams
# gets a higher ceiling because it represents overnight reflection,
# which is architecturally allowed to be a larger step than a single
# turn. But not unlimited — the cap enforces the AC-13 invariant.
_DYAD_DELTA_CAP: float = 0.10

# Somatic decay default half-lives when a row's decay_config is missing
# a key. These match the defaults in db/retrieval.py::REQUIRED_DECAY_KEYS.
_DEFAULT_HALF_LIFE_HOURS: dict[str, float] = {
    "fatigue": 8.0,
    "stress_residue": 24.0,
    "injury_residue": 72.0,
}


# ---------------------------------------------------------------------------
# Somatic decay refresh
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SomaticRefreshResult:
    """Outcome of one ``refresh_somatic_decay`` call."""

    character_id: str
    applied: bool
    elapsed_hours: float
    before: dict[str, float]
    after: dict[str, float]


async def refresh_somatic_decay(
    session: AsyncSession, character_id: str, now: datetime
) -> SomaticRefreshResult:
    """Apply exponential decay to a character's Transient Somatic State.

    Reads the character's current row, computes elapsed hours since
    ``last_decayed_at``, applies ``apply_decay`` per field using
    ``decay_config`` half-lives, writes back, and updates
    ``last_decayed_at`` to ``now``.

    No-op (returns ``applied=False``) if no row exists for the character
    yet — Dreams does not create rows, only refreshes existing ones.
    """
    stmt = select(TransientSomaticState).where(
        TransientSomaticState.character_id == character_id
    )
    result = await session.execute(stmt)
    row = result.scalar_one_or_none()

    if row is None:
        return SomaticRefreshResult(
            character_id=character_id,
            applied=False,
            elapsed_hours=0.0,
            before={},
            after={},
        )

    before = {
        "fatigue": float(row.fatigue),
        "stress_residue": float(row.stress_residue),
        "injury_residue": float(row.injury_residue),
    }

    elapsed_hours = max(
        0.0, (now - row.last_decayed_at).total_seconds() / 3600.0
    )

    config = row.decay_config or {}
    new_fatigue = apply_decay(
        before["fatigue"],
        float(config.get("fatigue", _DEFAULT_HALF_LIFE_HOURS["fatigue"])),
        elapsed_hours,
    )
    new_stress = apply_decay(
        before["stress_residue"],
        float(config.get("stress_residue", _DEFAULT_HALF_LIFE_HOURS["stress_residue"])),
        elapsed_hours,
    )
    new_injury = apply_decay(
        before["injury_residue"],
        float(config.get("injury_residue", _DEFAULT_HALF_LIFE_HOURS["injury_residue"])),
        elapsed_hours,
    )

    row.fatigue = new_fatigue
    row.stress_residue = new_stress
    row.injury_residue = new_injury
    row.last_decayed_at = now

    after = {
        "fatigue": new_fatigue,
        "stress_residue": new_stress,
        "injury_residue": new_injury,
    }

    logger.info(
        "dreams_somatic_refreshed",
        extra={
            "character_id": character_id,
            "elapsed_hours": elapsed_hours,
            "before": before,
            "after": after,
        },
    )

    return SomaticRefreshResult(
        character_id=character_id,
        applied=True,
        elapsed_hours=elapsed_hours,
        before=before,
        after=after,
    )


# ---------------------------------------------------------------------------
# Dyad deltas
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DyadDelta:
    """A single dimension delta request for a dyad."""

    dimension: str  # e.g. "trust", "intimacy", "conflict", "unresolved_tension", "repair_history"
    delta: float


@dataclass(frozen=True)
class DyadDeltaApplication:
    """Outcome of applying one DyadDelta."""

    dimension: str
    requested: float
    applied: float  # clamped to [-_DYAD_DELTA_CAP, _DYAD_DELTA_CAP]
    clamped: bool
    before: float
    after: float


async def apply_overnight_dyad_deltas(
    session: AsyncSession,
    *,
    character_id: str,
    whyze_deltas: list[DyadDelta] | None = None,
    internal_deltas: dict[str, list[DyadDelta]] | None = None,
) -> list[DyadDeltaApplication]:
    """Apply per-dimension deltas to dyad rows, capped at ±_DYAD_DELTA_CAP.

    ``whyze_deltas`` apply to the character's DyadStateWhyze row.
    ``internal_deltas`` is keyed by the *other* member of the internal
    dyad (e.g. ``{"bina": [DyadDelta(...)]}`` applies to the adelia-bina
    row when ``character_id`` is adelia).

    Returns a flat list of per-dimension application records with
    before/after values + a clamped flag. AC-13 invariant: the applied
    delta is always ≤ _DYAD_DELTA_CAP in magnitude regardless of the
    requested magnitude.
    """
    applications: list[DyadDeltaApplication] = []

    # Whyze dyad
    if whyze_deltas:
        wd_stmt = select(DyadStateWhyze).where(
            DyadStateWhyze.character_id == character_id
        )
        wd_result = await session.execute(wd_stmt)
        whyze_row = wd_result.scalar_one_or_none()
        if whyze_row is not None:
            for d in whyze_deltas:
                applications.append(
                    _apply_single_delta(whyze_row, d.dimension, d.delta)
                )
            whyze_row.last_updated_at = datetime.now(whyze_row.last_updated_at.tzinfo)

    # Internal (woman-to-woman) dyads
    if internal_deltas:
        for other, deltas in internal_deltas.items():
            id_stmt = select(DyadStateInternal).where(
                (
                    (DyadStateInternal.member_a == character_id)
                    & (DyadStateInternal.member_b == other)
                )
                | (
                    (DyadStateInternal.member_a == other)
                    & (DyadStateInternal.member_b == character_id)
                )
            )
            id_result = await session.execute(id_stmt)
            internal_row = id_result.scalar_one_or_none()
            if internal_row is None:
                continue
            for d in deltas:
                applications.append(
                    _apply_single_delta(internal_row, d.dimension, d.delta)
                )
            internal_row.last_updated_at = datetime.now(
                internal_row.last_updated_at.tzinfo
            )

    return applications


def _apply_single_delta(
    row: DyadStateWhyze | DyadStateInternal, dimension: str, delta: float
) -> DyadDeltaApplication:
    """Clamp, apply, and return the bookkeeping record."""
    if not hasattr(row, dimension):
        logger.warning(
            "dreams_unknown_dyad_dimension",
            extra={"dimension": dimension, "row_type": type(row).__name__},
        )
        return DyadDeltaApplication(
            dimension=dimension,
            requested=delta,
            applied=0.0,
            clamped=False,
            before=0.0,
            after=0.0,
        )

    clamped = abs(delta) > _DYAD_DELTA_CAP
    applied = max(-_DYAD_DELTA_CAP, min(_DYAD_DELTA_CAP, delta))

    before = float(getattr(row, dimension))
    after = max(0.0, min(1.0, before + applied))
    setattr(row, dimension, after)

    if clamped:
        logger.warning(
            "dreams_dyad_delta_clamped",
            extra={
                "dimension": dimension,
                "requested": delta,
                "applied": applied,
                "cap": _DYAD_DELTA_CAP,
            },
        )

    return DyadDeltaApplication(
        dimension=dimension,
        requested=delta,
        applied=applied,
        clamped=clamped,
        before=before,
        after=after,
    )


# ---------------------------------------------------------------------------
# Open loop expiry + resolution
# ---------------------------------------------------------------------------


async def expire_stale_loops(session: AsyncSession, now: datetime) -> int:
    """Bulk-update open loops whose expires_at is past ``now`` to status='expired'.

    Returns the number of rows transitioned. Only operates on rows whose
    current status is 'open' — already-resolved/expired rows are not
    touched so the state machine stays one-way per loop.
    """
    stmt = (
        update(OpenLoop)
        .where((OpenLoop.expires_at < now) & (OpenLoop.status == "open"))
        .values(status="expired", resolved_at=now)
    )
    result = await session.execute(stmt)
    count = int(getattr(result, "rowcount", 0) or 0)
    if count:
        logger.info(
            "dreams_open_loops_expired",
            extra={"count": count, "as_of": now.isoformat()},
        )
    return count


async def resolve_addressed_loops(
    session: AsyncSession,
    character_id: str,
    loop_ids: list[uuid.UUID],
    *,
    now: datetime,
) -> int:
    """Mark the named open loops as resolved by this Dreams run.

    Only resolves rows that belong to ``character_id`` and whose current
    status is 'open' — defensive against passing stale loop IDs that
    might already be expired or resolved by another run.
    """
    if not loop_ids:
        return 0
    stmt = (
        update(OpenLoop)
        .where(
            (OpenLoop.id.in_(loop_ids))
            & (OpenLoop.character_id == character_id)
            & (OpenLoop.status == "open")
        )
        .values(status="resolved", resolved_by="dreams", resolved_at=now)
    )
    result = await session.execute(stmt)
    count = int(getattr(result, "rowcount", 0) or 0)
    if count:
        logger.info(
            "dreams_open_loops_resolved",
            extra={"character_id": character_id, "count": count},
        )
    return count
