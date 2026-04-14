"""Phase 6 Dreams Engine — nightly batch life-simulation.

Public exports are the runner + types callers need to invoke a Dreams
pass or wire up the scheduler. See Docs/_phases/PHASE_6.md for the full
architecture and lifecycle.
"""

from __future__ import annotations

from .config import DreamsSettings
from .errors import (
    DreamsLLMError,
    DreamsRunError,
    DreamsScheduleError,
)
from .llm import BDOne, BDOneCompletion, BDOneSettings, StubBDOne
from .runner import run_dreams_pass
from .types import (
    DreamsCharacterResult,
    DreamsPassResult,
    GenerationContext,
    GenerationOutput,
    LLMClient,
    SessionSnapshot,
)

__all__ = [
    "BDOne",
    "BDOneCompletion",
    "BDOneSettings",
    "DreamsCharacterResult",
    "DreamsLLMError",
    "DreamsPassResult",
    "DreamsRunError",
    "DreamsScheduleError",
    "DreamsSettings",
    "GenerationContext",
    "GenerationOutput",
    "LLMClient",
    "SessionSnapshot",
    "StubBDOne",
    "run_dreams_pass",
]
