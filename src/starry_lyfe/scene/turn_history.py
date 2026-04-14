"""TurnEntry dataclass and helpers for reading recent exchanges (Phase 5)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TurnEntry:
    """A single turn in the recent conversation history.

    Used by ``select_next_speaker`` to score the Talk-to-Each-Other
    Mandate: consecutive ``addressed_to == "whyze"`` turns trigger the
    chain-breaking penalty; woman-to-woman exchanges trigger the chain
    reward.

    Attributes:
        speaker: Character name who spoke this turn (lowercase), or
            ``"whyze"`` for Whyze's message.
        addressed_to: Who the speaker was primarily addressing
            (lowercase character name or ``"whyze"``).
        turn_index: Monotonic turn index from the session's beginning.
            Used only for debugging and deterministic ordering; the
            scoring function reads turn order by list position.
    """

    speaker: str
    addressed_to: str
    turn_index: int


def last_non_whyze_speaker(history: list[TurnEntry]) -> str | None:
    """Return the most recent non-Whyze speaker, or None if none found.

    Used for the recency-suppression rule in ``select_next_speaker``
    (avoid picking the same woman who just spoke).
    """
    for turn in reversed(history):
        if turn.speaker != "whyze":
            return turn.speaker
    return None
