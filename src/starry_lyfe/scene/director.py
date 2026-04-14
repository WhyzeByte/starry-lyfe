"""Scene Director public orchestration (Phase 5).

Re-exports the two public entry points:

- ``classify_scene(input)`` — build a ``SceneState`` from caller inputs.
- ``select_next_speaker(input)`` — score present women and pick who
  speaks next in Crew Conversations.

Both functions are pure, synchronous, and deterministic given their
inputs. Dyad state is injected via ``DyadStateProvider`` (see
``next_speaker``) so the scoring function stays free of DB dependencies.

This module is intentionally thin; the actual logic lives in
``classifier.py`` and ``next_speaker.py`` so each file has a single
focus and unit tests can target narrowly.
"""

from __future__ import annotations

from .classifier import (
    SceneDirectorHints,
    SceneDirectorInput,
    classify_scene,
)
from .next_speaker import (
    DictDyadStateProvider,
    DyadStateProvider,
    NextSpeakerDecision,
    NextSpeakerInput,
    select_next_speaker,
)
from .turn_history import TurnEntry, last_non_whyze_speaker

__all__ = [
    "DictDyadStateProvider",
    "DyadStateProvider",
    "NextSpeakerDecision",
    "NextSpeakerInput",
    "SceneDirectorHints",
    "SceneDirectorInput",
    "TurnEntry",
    "classify_scene",
    "last_non_whyze_speaker",
    "select_next_speaker",
]
