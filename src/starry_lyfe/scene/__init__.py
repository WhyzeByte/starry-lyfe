"""Scene Director (Phase 5).

The Scene Director is the pre-assembly module that turns caller inputs
into a ``SceneState`` ready for ``assemble_context`` to consume, and
scores which woman speaks next in multi-character Crew Conversations.

See ``director.py`` for the public API and ``Docs/_phases/PHASE_5.md``
for the full design rationale.
"""

from __future__ import annotations

from .classifier import (
    SceneDirectorHints,
    SceneDirectorInput,
    classify_scene,
)
from .errors import AliciaAwayContradictionError, NoValidSpeakerError
from .next_speaker import (
    DictDyadStateProvider,
    DyadStateProvider,
    NextSpeakerDecision,
    NextSpeakerInput,
    build_dyad_state_provider,
    select_next_speaker,
)
from .turn_history import TurnEntry, last_non_whyze_speaker

__all__ = [
    "AliciaAwayContradictionError",
    "DictDyadStateProvider",
    "DyadStateProvider",
    "NextSpeakerDecision",
    "NextSpeakerInput",
    "NoValidSpeakerError",
    "SceneDirectorHints",
    "SceneDirectorInput",
    "TurnEntry",
    "build_dyad_state_provider",
    "classify_scene",
    "last_non_whyze_speaker",
    "select_next_speaker",
]
