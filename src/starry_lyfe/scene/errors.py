"""Custom exceptions for the Scene Director (Phase 5)."""

from __future__ import annotations


class AliciaAwayContradictionError(ValueError):
    """Raised when a caller asks the classifier to build a scene that is
    physically impossible: Alicia present and marked home-absent while the
    communication mode is IN_PERSON.

    This fires at the Scene Director (front door) layer. The assembler
    has its own defense-in-depth check (``AliciaAwayError``) that fires
    if an invalid ``SceneState`` reaches it by some other path.
    """


class NoValidSpeakerError(RuntimeError):
    """Raised by ``select_next_speaker`` when every candidate has been
    zeroed out by hard gates (Rule of One + Alicia residence).

    The exception message includes the candidates and their reason traces
    so the caller can debug which combination of inputs produced an
    unsatisfiable state.
    """
