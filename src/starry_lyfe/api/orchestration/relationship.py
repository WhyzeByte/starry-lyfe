"""Post-turn relationship evaluator (fire-and-forget).

After the SSE response closes, the chat endpoint schedules
``evaluate_and_update`` as ``asyncio.create_task``. The function
applies bounded deltas to the focal woman's ``DyadStateWhyze`` row
based on coarse heuristics over the turn text. Per CLAUDE.md §16,
deltas are capped ±0.03 per dimension per turn — this is a guardrail,
not a tuning parameter.

The current implementation is intentionally heuristic-based rather
than LLM-driven: a single failed turn cannot drift a relationship
more than 3 percentage points in any dimension. Future versions can
swap in an LLM evaluator without changing the cap.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from starry_lyfe.db.models.dyad_state_whyze import DyadStateWhyze

logger = logging.getLogger(__name__)


# Per-dimension cap per CLAUDE.md §16. Matches the existing Phase 6
# Dreams ``apply_overnight_dyad_deltas`` consolidation cap so daytime
# (per-turn) and nighttime (per-Dreams) updates use the same ceiling.
_DELTA_CAP: float = 0.03


# Coarse signal banks. Lowercase substring match in the response text.
# Tunable; the *cap* is the safety margin, not these tables.
_INTIMACY_POSITIVE = ("close", "warm", "tender", "soft", "intimate", "near")
_INTIMACY_NEGATIVE = ("distant", "cold", "withdrawn", "pulling away")
_TENSION_POSITIVE = ("frustrat", "tense", "sharp", "snapped", "pushback")
_TENSION_NEGATIVE = ("calm", "settled", "resolved", "let it go", "breathe")
_TRUST_POSITIVE = ("trust", "honest", "open", "shared", "told you")
_TRUST_NEGATIVE = ("doubt", "suspicio", "guarded", "withhold")
_REPAIR_POSITIVE = ("apolog", "i was wrong", "make this right", "repair", "i'm sorry")


@dataclass(frozen=True)
class DyadDeltaProposal:
    """Proposed deltas before clamping."""

    intimacy: float = 0.0
    unresolved_tension: float = 0.0
    trust: float = 0.0
    repair_history: float = 0.0


def _clamp_delta(value: float) -> float:
    if value > _DELTA_CAP:
        return _DELTA_CAP
    if value < -_DELTA_CAP:
        return -_DELTA_CAP
    return value


def _propose_deltas(text: str) -> DyadDeltaProposal:
    """Heuristic delta proposal based on response text content.

    Returns deltas BEFORE the cap is applied; ``_clamp_delta`` is the
    final gate. Any single signal is worth 0.01; the cap pins the
    aggregate at ±0.03 per dimension.
    """
    lowered = text.lower()

    def _bias(positives: tuple[str, ...], negatives: tuple[str, ...]) -> float:
        pos = sum(1 for p in positives if p in lowered)
        neg = sum(1 for n in negatives if n in lowered)
        return 0.01 * (pos - neg)

    return DyadDeltaProposal(
        intimacy=_bias(_INTIMACY_POSITIVE, _INTIMACY_NEGATIVE),
        unresolved_tension=_bias(_TENSION_POSITIVE, _TENSION_NEGATIVE),
        trust=_bias(_TRUST_POSITIVE, _TRUST_NEGATIVE),
        repair_history=_bias(_REPAIR_POSITIVE, ()),
    )


@dataclass
class RelationshipUpdate:
    """Audit record returned by ``evaluate_and_update`` for tests + logs."""

    character_id: str
    proposed: DyadDeltaProposal
    applied: DyadDeltaProposal
    pre_intimacy: float
    post_intimacy: float


async def evaluate_and_update(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    character_id: str,
    response_text: str,
) -> RelationshipUpdate | None:
    """Apply capped per-turn deltas to the focal woman's Whyze dyad.

    Returns the update record or None if the dyad row is missing
    (e.g. fresh DB before seed). Commits its own transaction.
    """
    proposal = _propose_deltas(response_text)
    applied = DyadDeltaProposal(
        intimacy=_clamp_delta(proposal.intimacy),
        unresolved_tension=_clamp_delta(proposal.unresolved_tension),
        trust=_clamp_delta(proposal.trust),
        repair_history=_clamp_delta(proposal.repair_history),
    )

    if all(v == 0.0 for v in (
        applied.intimacy,
        applied.unresolved_tension,
        applied.trust,
        applied.repair_history,
    )):
        # Nothing to write — skip the round-trip.
        return None

    async with session_factory() as session, session.begin():
        result = await session.execute(
            select(DyadStateWhyze).where(DyadStateWhyze.character_id == character_id)
        )
        row = result.scalars().first()
        if row is None:
            logger.warning(
                "evaluate_and_update_no_dyad_row",
                extra={"character_id": character_id},
            )
            return None
        pre_intimacy = float(row.intimacy)
        row.intimacy = _bound01(row.intimacy + applied.intimacy)
        row.unresolved_tension = _bound01(row.unresolved_tension + applied.unresolved_tension)
        row.trust = _bound01(row.trust + applied.trust)
        row.repair_history = _bound01(row.repair_history + applied.repair_history)
        row.last_updated_at = datetime.now(UTC)
        return RelationshipUpdate(
            character_id=character_id,
            proposed=proposal,
            applied=applied,
            pre_intimacy=pre_intimacy,
            post_intimacy=float(row.intimacy),
        )


def _bound01(value: float) -> float:
    """Clamp a dyad dimension into [0.0, 1.0]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value
