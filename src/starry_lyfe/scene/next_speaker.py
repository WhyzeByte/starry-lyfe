"""Next-speaker scoring for multi-character scenes (Phase 5).

Implements the Talk-to-Each-Other Mandate (Vision §6, §7) and Rule of One
algorithmically. Penalizes consecutive Whyze-addressed turns, rewards
woman-to-woman exchanges, reads dyad state (memory tier 4) as a fitness
input, and zeroes out Alicia when she is away and the scene is in-person.

Pure synchronous function. Dyad state is injected via a
``DyadStateProvider`` callable so unit tests can stub deterministic
values and the production HTTP endpoint (Phase 7) can wrap the real
``dyad_state_internal`` DB read without this module taking a session
dependency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from ..context.types import CommunicationMode, SceneState
from ..db.models.dyad_state_internal import DyadStateInternal
from .errors import NoValidSpeakerError
from .turn_history import TurnEntry, last_non_whyze_speaker

# ---------------------------------------------------------------------------
# Scoring weights — TUNABLE module-level constants. Unit tests assert
# RELATIVE score differentials so minor tuning does not churn the suite.
# ---------------------------------------------------------------------------

_BASE_SCORE = 0.50

# Talk-to-Each-Other chain-breaking
_WHYZE_CHAIN_BREAKER_REWARD = 0.25  # Bonus for candidates who'd talk to a woman
_WHYZE_CHAIN_PENALTY = 0.10         # Penalty otherwise

# Woman-to-woman continuation
_W2W_CHAIN_REWARD = 0.15

# Dyad-state fitness
_INTIMACY_WEIGHT = 0.10
_TENSION_WEIGHT = 0.05

# Recency suppression
_RECENCY_PENALTY = 0.05

# Narrative salience (R3 remediation / F3 — IMPLEMENTATION_PLAN §8
# "current activity context" as a scoring input). Small boost when the
# candidate's name appears in the current scene description or in an
# optional caller-provided activity_context (Phase 6 Dreams will source
# longer-form activity narratives here).
_ACTIVITY_SALIENCE_BOOST = 0.05

# Stable tiebreak order — must match canonical character enumeration in
# canon/schemas/enums.py (CharacterID). Used only when scores tie exactly.
_STABLE_TIEBREAK_ORDER: tuple[str, ...] = ("adelia", "bina", "reina", "alicia")


# ---------------------------------------------------------------------------
# Protocol + dataclasses
# ---------------------------------------------------------------------------


class DyadStateProvider(Protocol):
    """Protocol for reading dyad state (tier-4 memory) in the scoring loop.

    Implementations typically wrap a pre-fetched dict or, in production,
    a synchronous view over the ``dyad_state_internal`` table. The
    scoring function is synchronous on purpose; the caller is expected
    to load whatever dyad rows are needed before invoking it.

    Returns ``None`` when the pair has no recorded dyad state (e.g.
    Alicia-orbital while she is away and the row is inactive).
    """

    def get(self, char_a: str, char_b: str) -> DyadStateInternal | None: ...


@dataclass(frozen=True)
class NextSpeakerInput:
    """All state needed to score next-speaker candidates.

    Attributes:
        scene_state: The classifier's output. Drives residence zero-out
            and residence-aware communication-mode gating. Also the
            short-form activity context source (``scene_description``)
            read by Rule 7 narrative salience.
        turn_history: Recent turns, caller-trimmed (the scoring function
            inspects at most the last 2 entries). Newer turns last.
        in_turn_already_spoken: For Crew-mode multi-speaker response
            bundles. Each character who already spoke in THIS turn is
            zeroed out (Rule of One).
        dyad_state_provider: Injected accessor for tier-4 dyad state.
        activity_context: Optional longer-form activity narrative
            (e.g., a Dreams-generated activity summary in Phase 6).
            Read alongside ``scene_state.scene_description`` by Rule 7
            (narrative salience). Default ``None`` keeps Phase 5
            callers backwards-compatible.
    """

    scene_state: SceneState
    turn_history: list[TurnEntry]
    dyad_state_provider: DyadStateProvider
    in_turn_already_spoken: list[str] = field(default_factory=list)
    activity_context: str | None = None


@dataclass(frozen=True)
class NextSpeakerDecision:
    """Result of ``select_next_speaker``.

    Attributes:
        speaker: The chosen character name (lowercase).
        scores: Map of candidate -> composite score. Hard-gated
            candidates score exactly 0.0.
        reasons: Human-readable trace listing every rule that fired and
            every candidate's score contributions. Enables debugging
            without a debugger — dump and read.
    """

    speaker: str
    scores: dict[str, float]
    reasons: list[str]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def select_next_speaker(speaker_input: NextSpeakerInput) -> NextSpeakerDecision:
    """Score each present woman and return the highest-scoring speaker.

    Rules (applied in order):
    1. Residence zero-out: Alicia away + in-person → score 0.
    2. Rule of One: already spoke this turn → score 0.
    3. Talk-to-Each-Other: last 2 turns both addressed Whyze → reward
       candidates who'd address a woman, penalize those who wouldn't.
    4. Woman-to-woman continuation: last turn was w2w → reward.
    5. Dyad-state fitness: intimacy and tension with other present women.
    6. Recency suppression: just spoke non-whyze → small penalty.
    7. Narrative salience (R3): candidate named in scene_description or
       activity_context → small boost. Implements the "current activity
       context" scoring input from IMPLEMENTATION_PLAN §8.

    Returns the ``argmax``; ties broken by stable canonical ordering.

    Raises:
        NoValidSpeakerError: Every candidate was zeroed out by hard gates.
    """
    candidates = [c for c in speaker_input.scene_state.present_characters if c != "whyze"]
    if not candidates:
        raise NoValidSpeakerError(
            "select_next_speaker: no candidates. scene_state.present_characters "
            f"was {speaker_input.scene_state.present_characters!r}."
        )

    scores: dict[str, float] = {}
    reasons: list[str] = []
    last_non_whyze = last_non_whyze_speaker(speaker_input.turn_history)
    last_turn = speaker_input.turn_history[-1] if speaker_input.turn_history else None
    last_two = speaker_input.turn_history[-2:]
    two_whyze_chain = (
        len(last_two) == 2 and all(t.addressed_to == "whyze" for t in last_two)
    )
    w2w_chain = (
        last_turn is not None
        and last_turn.speaker != "whyze"
        and last_turn.addressed_to != "whyze"
    )

    for candidate in candidates:
        # (1) Residence zero-out
        if (
            candidate == "alicia"
            and not speaker_input.scene_state.alicia_home
            and speaker_input.scene_state.communication_mode == CommunicationMode.IN_PERSON
        ):
            scores[candidate] = 0.0
            reasons.append(f"{candidate}: zero-out (alicia away, in-person mode)")
            continue

        # (2) Rule of One
        if candidate in speaker_input.in_turn_already_spoken:
            scores[candidate] = 0.0
            reasons.append(f"{candidate}: zero-out (already spoke this turn)")
            continue

        score = _BASE_SCORE
        reasons.append(f"{candidate}: base={_BASE_SCORE:.2f}")

        # (3) Talk-to-Each-Other: chain-breaking
        if two_whyze_chain:
            # Candidate is assumed to address a woman if there's another
            # woman present to address. This is a heuristic — actual
            # addressing is decided by the LLM generation step; we just
            # score the OPPORTUNITY.
            other_women = [
                c for c in candidates if c != candidate and c in {"adelia", "bina", "reina", "alicia"}
            ]
            if other_women:
                score += _WHYZE_CHAIN_BREAKER_REWARD
                reasons.append(
                    f"{candidate}: +{_WHYZE_CHAIN_BREAKER_REWARD:.2f} "
                    f"(Talk-to-Each-Other: break 2-turn Whyze chain)"
                )
            else:
                score -= _WHYZE_CHAIN_PENALTY
                reasons.append(
                    f"{candidate}: -{_WHYZE_CHAIN_PENALTY:.2f} "
                    f"(only woman present, cannot break Whyze chain)"
                )

        # (4) Woman-to-woman continuation
        if w2w_chain:
            score += _W2W_CHAIN_REWARD
            reasons.append(
                f"{candidate}: +{_W2W_CHAIN_REWARD:.2f} (continue w2w chain)"
            )

        # (5) Dyad-state fitness
        for other in candidates:
            if other == candidate:
                continue
            dyad = speaker_input.dyad_state_provider.get(candidate, other)
            if dyad is None:
                continue
            intimacy_delta = dyad.intimacy * _INTIMACY_WEIGHT
            tension_delta = dyad.unresolved_tension * _TENSION_WEIGHT
            score += intimacy_delta + tension_delta
            reasons.append(
                f"{candidate}: +{intimacy_delta:.3f}+{tension_delta:.3f} "
                f"(dyad with {other}: intimacy={dyad.intimacy:.2f}, "
                f"tension={dyad.unresolved_tension:.2f})"
            )

        # (6) Recency suppression
        if candidate == last_non_whyze:
            score -= _RECENCY_PENALTY
            reasons.append(
                f"{candidate}: -{_RECENCY_PENALTY:.2f} (recency: just spoke)"
            )

        # (7) Narrative salience — implements IMPLEMENTATION_PLAN §8
        # "current activity context" scoring input. Reads the short-form
        # scene description AND the optional long-form activity_context
        # (Phase 6 Dreams-sourced).
        activity_blob = (
            speaker_input.scene_state.scene_description
            + " "
            + (speaker_input.activity_context or "")
        ).lower()
        if candidate.lower() in activity_blob:
            score += _ACTIVITY_SALIENCE_BOOST
            reasons.append(
                f"{candidate}: +{_ACTIVITY_SALIENCE_BOOST:.2f} "
                f"(narrative salience: named in activity context)"
            )

        scores[candidate] = score

    # Pick argmax with stable tiebreak
    max_score = max(scores.values())
    if max_score == 0.0:
        raise NoValidSpeakerError(
            "select_next_speaker: every candidate zeroed out by hard gates. "
            f"scores={scores!r}, reasons={reasons!r}"
        )

    # Tiebreak: candidates at max_score, pick earliest in canonical order.
    tied = [c for c, s in scores.items() if s == max_score]
    if len(tied) > 1:
        reasons.append(f"tiebreak: {tied} at score {max_score:.3f}")
        for name in _STABLE_TIEBREAK_ORDER:
            if name in tied:
                chosen = name
                break
        else:  # pragma: no cover — defensive, tied names are always canonical
            chosen = tied[0]
    else:
        chosen = tied[0]

    return NextSpeakerDecision(speaker=chosen, scores=scores, reasons=reasons)


# ---------------------------------------------------------------------------
# Production DyadStateProvider adapter
# ---------------------------------------------------------------------------


class DictDyadStateProvider:
    """Simple dict-backed DyadStateProvider for tests and pre-fetched callers.

    Wraps a mapping of ``frozenset({char_a, char_b}) -> DyadStateInternal``.
    Lookup is order-independent: ``get("adelia", "bina")`` and
    ``get("bina", "adelia")`` return the same row.
    """

    def __init__(self, rows: dict[frozenset[str], DyadStateInternal]) -> None:
        self._rows = rows

    def get(self, char_a: str, char_b: str) -> DyadStateInternal | None:
        return self._rows.get(frozenset({char_a, char_b}))


def build_dyad_state_provider(
    rows: list[DyadStateInternal],
) -> DictDyadStateProvider:
    """Turn a list of dyad rows (as returned by ``_retrieve_internal_dyads``)
    into a synchronous ``DyadStateProvider``.

    The production path (Phase 7 HTTP endpoint) is:

    1. ``await _retrieve_internal_dyads(session, character_id)`` → list
    2. ``build_dyad_state_provider(rows)`` → provider
    3. ``select_next_speaker(NextSpeakerInput(dyad_state_provider=provider, ...))``

    Keeping step 2 synchronous means the scoring function stays pure
    and testable without an async context.
    """
    return DictDyadStateProvider(
        {frozenset({row.member_a, row.member_b}): row for row in rows}
    )
