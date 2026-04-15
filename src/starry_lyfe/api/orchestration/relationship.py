"""Post-turn relationship evaluator (fire-and-forget).

After the SSE response closes, the chat endpoint schedules
``evaluate_and_update`` as ``asyncio.create_task``. The function
applies bounded deltas to the focal woman's ``DyadStateWhyze`` row.
Per CLAUDE.md §16, deltas are capped ±0.03 per dimension per turn —
this is a guardrail, not a tuning parameter.

Phase 8 (2026-04-15): the evaluator is now LLM-primary by default via
``BDOne.complete()`` + ``relationship_prompts.parse_eval_response``.
The heuristic path remains in this file as a named fallback for:

1. ``settings.relationship_eval_llm=False`` (operator opt-out)
2. ``llm_client`` not supplied (legacy/test callers)
3. BD-1 circuit breaker open
4. LLM call raises ``DreamsLLMError``
5. Parser returns ``None`` (malformed / missing / non-numeric)

Either path feeds the same ``_clamp_delta`` gate — the ±0.03 cap is
the final safety margin regardless of which proposal source fired.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from starry_lyfe.db.models.dyad_state_whyze import DyadStateWhyze
from starry_lyfe.dreams.errors import DreamsLLMError
from starry_lyfe.dreams.llm import BDOne, StubBDOne

if TYPE_CHECKING:
    from starry_lyfe.api.config import ApiSettings

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


async def _llm_propose_deltas(
    llm_client: BDOne | StubBDOne,
    *,
    character_id: str,
    response_text: str,
    max_tokens: int,
    temperature: float,
) -> DyadDeltaProposal | None:
    """Phase 8: LLM-driven delta proposal. Returns None on any failure.

    Failures (``DreamsLLMError``, parser returning None, empty
    completion text) are logged as structured events so the fallback
    path is observable. Returns None so the caller can route to
    ``_propose_deltas`` without additional branching.
    """
    # Import here to avoid a top-level circular import (relationship_prompts
    # imports DyadDeltaProposal from this module).
    from .relationship_prompts import (
        RELATIONSHIP_EVAL_SYSTEM,
        build_eval_prompt,
        parse_eval_response,
    )

    if llm_client.circuit_open:
        logger.info(
            "llm_eval_fallback_to_heuristic",
            extra={"character_id": character_id, "reason": "circuit_open"},
        )
        return None

    user_prompt = build_eval_prompt(character_id, response_text)
    try:
        completion = await llm_client.complete(
            system_prompt=RELATIONSHIP_EVAL_SYSTEM,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )
    except DreamsLLMError as exc:
        logger.info(
            "llm_eval_fallback_to_heuristic",
            extra={"character_id": character_id, "reason": f"DreamsLLMError: {exc}"},
        )
        return None

    parsed = parse_eval_response(completion.text)
    if parsed is None:
        logger.info(
            "llm_eval_fallback_to_heuristic",
            extra={"character_id": character_id, "reason": "parse_returned_none"},
        )
        return None

    logger.info(
        "llm_eval_parsed_proposal",
        extra={
            "character_id": character_id,
            "intimacy": parsed.intimacy,
            "unresolved_tension": parsed.unresolved_tension,
            "trust": parsed.trust,
            "repair_history": parsed.repair_history,
        },
    )
    return parsed


async def evaluate_and_update(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    character_id: str,
    response_text: str,
    llm_client: BDOne | StubBDOne | None = None,
    settings: ApiSettings | None = None,
) -> RelationshipUpdate | None:
    """Apply capped per-turn deltas to the focal woman's Whyze dyad.

    Phase 8 (2026-04-15): LLM-primary with heuristic fallback. Falls
    back to ``_propose_deltas`` when:

    - ``settings.relationship_eval_llm`` is False (operator opt-out)
    - ``llm_client`` is None (legacy caller / test without LLM stub)
    - LLM circuit breaker open
    - LLM raises ``DreamsLLMError``
    - Parser returns ``None``

    Either proposal source feeds the same ±0.03 ``_clamp_delta`` gate.

    Returns the update record or None if the dyad row is missing
    (e.g. fresh DB before seed). Commits its own transaction.
    """
    use_llm = (
        llm_client is not None
        and (settings is None or settings.relationship_eval_llm)
    )
    proposal: DyadDeltaProposal | None = None
    if use_llm:
        assert llm_client is not None  # narrowed by use_llm guard
        max_tokens = settings.relationship_eval_max_tokens if settings else 200
        temperature = settings.relationship_eval_temperature if settings else 0.2
        proposal = await _llm_propose_deltas(
            llm_client,
            character_id=character_id,
            response_text=response_text,
            max_tokens=max_tokens,
            temperature=temperature,
        )
    if proposal is None:
        if not use_llm:
            logger.info(
                "llm_eval_fallback_to_heuristic",
                extra={
                    "character_id": character_id,
                    "reason": "llm_disabled_or_missing",
                },
            )
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
