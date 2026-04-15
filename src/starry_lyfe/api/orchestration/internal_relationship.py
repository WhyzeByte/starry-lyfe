"""Post-turn inter-woman dyad evaluator (Phase 9, fire-and-forget).

Extends the Phase 8 Whyze-dyad evaluator pattern to the 6 inter-woman
dyads tracked in ``DyadStateInternal``. Same ±0.03 per-turn cap, same
LLM-primary-with-heuristic-fallback flow, same BDOne wiring. The
structural differences vs Phase 8:

1. **Five dimensions** (not four): ``trust``, ``intimacy``, ``conflict``,
   ``unresolved_tension``, ``repair_history``. ``conflict`` is the new
   dimension — tracks live disagreement *between the two women* (not
   residue, not Whyze-facing tension).
2. **Per-active-dyad fan-out**: the focal character is a member of
   multiple inter-woman dyads. ``evaluate_and_update_internal`` returns
   a list of ``InternalRelationshipUpdate`` records, one per active
   dyad that actually had a non-zero proposal.
3. **Alicia-orbital gate** (AC-9.11): dyads where
   ``is_currently_active=False`` are skipped. The gate lives in this
   evaluator, not the post_turn scheduler, so dormant dyads never
   consume LLM budget.

The ±0.03 ``_clamp_delta`` gate is shared with Phase 8 (imported from
``relationship.py``). The _NumericValue + _reject_bool Pydantic
primitives are shared via ``relationship_prompts.py`` re-use in
``internal_relationship_prompts.py``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from starry_lyfe.api.orchestration.relationship import _bound01, _clamp_delta
from starry_lyfe.db.models.dyad_state_internal import DyadStateInternal
from starry_lyfe.dreams.errors import DreamsLLMError
from starry_lyfe.dreams.llm import BDOne, StubBDOne

if TYPE_CHECKING:
    from starry_lyfe.api.config import ApiSettings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Heuristic signal banks — per-dimension substring cues. Drafted from the
# 18 per-pair conflict+/- bullets + standard trust/intimacy/repair cues
# from the Phase 9 register notes. Heuristic is the degraded-mode path;
# the cap is the safety margin, not these tables.
# ---------------------------------------------------------------------------

_INTIMACY_POSITIVE = (
    "warm", "tender", "close", "soft", "intimate",
    "saved my life", "covered plate", "hall light",
    "forehead", "greeting", "banter",
)
_INTIMACY_NEGATIVE = (
    "distant", "cold", "withdrawn", "pulling away",
    "operational face", "transit register", "flat state",
)

_TRUST_POSITIVE = (
    "trust", "open", "shared", "handed", "handing",
    "structural veto", "witnessed", "held",
)
_TRUST_NEGATIVE = (
    "doubt", "suspicio", "guarded", "withhold",
    "old wiring", "procedural distanc",
)

_CONFLICT_POSITIVE = (
    "push back", "pushback", "the sharpness", "cutting",
    "cut it", "Ti cuts", "urgency ladder", "go protocol",
    "veto blocked", "did not yield",
)
_CONFLICT_NEGATIVE = (
    "conceded", "pivot", "i hear you", "received cleanly",
    "the idea, not the person", "veto received", "adjusted",
)

_TENSION_POSITIVE = (
    "frustrat", "tense", "sharp", "snapped", "unfinished",
    "residue", "left open",
)
_TENSION_NEGATIVE = (
    "calm", "settled", "resolved", "let it go", "breathe",
    "closed it", "cleared",
)

_REPAIR_POSITIVE = (
    "apolog", "i was wrong", "make this right", "repair",
    "i'm sorry", "closed something", "rebuilt",
)


# ---------------------------------------------------------------------------
# Public dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class InternalDyadDeltaProposal:
    """Proposed deltas for a single inter-woman dyad before clamping.

    Five dimensions matching ``DyadStateInternal`` columns. ``conflict``
    is the Phase 9 addition vs Phase 8's four-dimension Whyze proposal.
    """

    trust: float = 0.0
    intimacy: float = 0.0
    conflict: float = 0.0
    unresolved_tension: float = 0.0
    repair_history: float = 0.0


@dataclass
class InternalRelationshipUpdate:
    """Audit record returned by ``evaluate_and_update_internal`` per active dyad.

    Production code doesn't read this; tests + MSE-6 logs consume it.
    One record per dyad whose row was actually updated — dormant
    Alicia-orbital dyads and zero-delta proposals produce no record.
    """

    dyad_key: str
    member_a: str
    member_b: str
    proposed: InternalDyadDeltaProposal
    applied: InternalDyadDeltaProposal


# ---------------------------------------------------------------------------
# Heuristic proposal
# ---------------------------------------------------------------------------


def _propose_internal_deltas(text: str) -> InternalDyadDeltaProposal:
    """Heuristic delta proposal based on response text content.

    Returns deltas BEFORE the cap is applied; ``_clamp_delta`` is the
    final gate. Each signal is worth 0.01; the cap pins aggregates at
    ±0.03 per dimension. Structure mirrors Phase 8's ``_propose_deltas``
    with a 5th dimension for ``conflict``.

    Not pair-aware. The LLM path carries the register notes; this
    heuristic is the degraded-mode path for when the LLM is unavailable,
    and intentionally dim by comparison.
    """
    lowered = text.lower()

    def _bias(positives: tuple[str, ...], negatives: tuple[str, ...]) -> float:
        pos = sum(1 for p in positives if p in lowered)
        neg = sum(1 for n in negatives if n in lowered)
        return 0.01 * (pos - neg)

    return InternalDyadDeltaProposal(
        trust=_bias(_TRUST_POSITIVE, _TRUST_NEGATIVE),
        intimacy=_bias(_INTIMACY_POSITIVE, _INTIMACY_NEGATIVE),
        conflict=_bias(_CONFLICT_POSITIVE, _CONFLICT_NEGATIVE),
        unresolved_tension=_bias(_TENSION_POSITIVE, _TENSION_NEGATIVE),
        repair_history=_bias(_REPAIR_POSITIVE, ()),
    )


# ---------------------------------------------------------------------------
# LLM proposal
# ---------------------------------------------------------------------------


async def _llm_propose_internal_deltas(
    llm_client: BDOne | StubBDOne,
    *,
    dyad_key: str,
    member_a: str,
    member_b: str,
    speaker_id: str,
    response_text: str,
    max_tokens: int,
    temperature: float,
) -> InternalDyadDeltaProposal | None:
    """LLM-driven delta proposal. Returns None on any failure.

    Fail-closed branches mirror Phase 8's ``_llm_propose_deltas``:
    circuit open, ``DreamsLLMError``, parser returning None. Each logs
    a structured ``internal_llm_eval_fallback_to_heuristic`` event with
    the ``dyad_key`` and ``reason``.

    R1-F1 closure (2026-04-15): ``speaker_id`` is threaded through so
    the LLM can disambiguate directional pair signals.
    """
    # Import here to avoid top-level circular import (prompts module
    # imports InternalDyadDeltaProposal from this module).
    from .internal_relationship_prompts import (
        INTERNAL_RELATIONSHIP_EVAL_SYSTEM,
        build_internal_eval_prompt,
        parse_internal_eval_response,
    )

    if llm_client.circuit_open:
        logger.info(
            "internal_llm_eval_fallback_to_heuristic",
            extra={"dyad_key": dyad_key, "reason": "circuit_open"},
        )
        return None

    user_prompt = build_internal_eval_prompt(
        dyad_key, member_a, member_b, response_text, speaker_id=speaker_id
    )
    try:
        completion = await llm_client.complete(
            system_prompt=INTERNAL_RELATIONSHIP_EVAL_SYSTEM,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )
    except DreamsLLMError as exc:
        logger.info(
            "internal_llm_eval_fallback_to_heuristic",
            extra={"dyad_key": dyad_key, "reason": f"DreamsLLMError: {exc}"},
        )
        return None

    parsed = parse_internal_eval_response(completion.text)
    if parsed is None:
        logger.info(
            "internal_llm_eval_fallback_to_heuristic",
            extra={"dyad_key": dyad_key, "reason": "parse_returned_none"},
        )
        return None

    logger.info(
        "internal_llm_eval_parsed_proposal",
        extra={
            "dyad_key": dyad_key,
            "trust": parsed.trust,
            "intimacy": parsed.intimacy,
            "conflict": parsed.conflict,
            "unresolved_tension": parsed.unresolved_tension,
            "repair_history": parsed.repair_history,
        },
    )
    return parsed


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _apply_and_zero_check(proposal: InternalDyadDeltaProposal) -> InternalDyadDeltaProposal:
    """Clamp each field to ±0.03. Returns the applied proposal."""
    return InternalDyadDeltaProposal(
        trust=_clamp_delta(proposal.trust),
        intimacy=_clamp_delta(proposal.intimacy),
        conflict=_clamp_delta(proposal.conflict),
        unresolved_tension=_clamp_delta(proposal.unresolved_tension),
        # repair_history is positive-only but may still need capping if
        # LLM proposed, say, +0.6. _clamp_delta handles the positive cap.
        repair_history=_clamp_delta(max(0.0, proposal.repair_history)),
    )


def _is_zero(proposal: InternalDyadDeltaProposal) -> bool:
    return (
        proposal.trust == 0.0
        and proposal.intimacy == 0.0
        and proposal.conflict == 0.0
        and proposal.unresolved_tension == 0.0
        and proposal.repair_history == 0.0
    )


async def evaluate_and_update_internal(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    character_id: str,
    response_text: str,
    llm_client: BDOne | StubBDOne | None = None,
    settings: ApiSettings | None = None,
) -> list[InternalRelationshipUpdate]:
    """Apply capped per-turn deltas to the focal character's active inter-woman dyads.

    AC-9.1: signature preserved; returns a list (empty if no dyads
    updated — e.g., all orbital dyads dormant, or no signal to apply).

    AC-9.11 Alicia-orbital gate: dyads with ``is_currently_active=False``
    are filtered out BEFORE the LLM call, so dormant dyads never
    consume LLM budget and never produce an update record.

    For each active dyad:

    1. If ``settings.internal_relationship_eval_llm`` is False OR
       ``llm_client`` is None OR ``llm_client.circuit_open`` → heuristic.
    2. Else: build prompt, call ``BDOne.complete``, parse JSON.
    3. On any LLM failure → heuristic fallback.
    4. Clamp each dimension at ±0.03 via ``_clamp_delta``.
    5. Skip write if the applied proposal is all-zero (no DB churn).

    Commits its own transaction.
    """
    use_llm = (
        llm_client is not None
        and (settings is None or settings.internal_relationship_eval_llm)
    )
    max_tokens = settings.relationship_eval_max_tokens if settings else 200
    temperature = settings.relationship_eval_temperature if settings else 0.2

    updates: list[InternalRelationshipUpdate] = []

    async with session_factory() as session, session.begin():
        # AC-9.11: retrieve only ACTIVE dyads the character is a member of.
        # Alicia-orbital dormant dyads are filtered at the query boundary.
        result = await session.execute(
            select(DyadStateInternal).where(
                (DyadStateInternal.member_a == character_id)
                | (DyadStateInternal.member_b == character_id),
                DyadStateInternal.is_currently_active.is_(True),
            )
        )
        active_rows = list(result.scalars().all())

        if not active_rows:
            # No active dyads — common case when focal = Alicia and she's
            # away, or when the character has no seeded dyads yet.
            return []

        for row in active_rows:
            # Determine the "other" member for this dyad from the focal
            # character's perspective. Used only for prompt labeling
            # (member_a / member_b stays canonical order in the row).
            proposal: InternalDyadDeltaProposal | None = None
            if use_llm:
                assert llm_client is not None  # narrowed by use_llm
                proposal = await _llm_propose_internal_deltas(
                    llm_client,
                    dyad_key=row.dyad_key,
                    member_a=row.member_a,
                    member_b=row.member_b,
                    speaker_id=character_id,
                    response_text=response_text,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
            if proposal is None:
                if not use_llm:
                    logger.info(
                        "internal_llm_eval_fallback_to_heuristic",
                        extra={
                            "dyad_key": row.dyad_key,
                            "reason": "llm_disabled_or_missing",
                        },
                    )
                proposal = _propose_internal_deltas(response_text)

            applied = _apply_and_zero_check(proposal)
            if _is_zero(applied):
                # No churn — nothing to write; no update record.
                continue

            # Apply deltas to the row. Each dimension is [0, 1]-bounded
            # via _bound01. Matches Phase 8's ``evaluate_and_update``.
            row.trust = _bound01(row.trust + applied.trust)
            row.intimacy = _bound01(row.intimacy + applied.intimacy)
            row.conflict = _bound01(row.conflict + applied.conflict)
            row.unresolved_tension = _bound01(
                row.unresolved_tension + applied.unresolved_tension
            )
            row.repair_history = _bound01(
                row.repair_history + applied.repair_history
            )
            row.last_updated_at = datetime.now(UTC)
            updates.append(
                InternalRelationshipUpdate(
                    dyad_key=row.dyad_key,
                    member_a=row.member_a,
                    member_b=row.member_b,
                    proposed=proposal,
                    applied=applied,
                )
            )

    return updates
