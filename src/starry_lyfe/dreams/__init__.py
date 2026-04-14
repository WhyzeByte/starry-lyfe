"""Phase 6 Dreams Engine — nightly batch life-simulation.

Public exports are the runner + types callers need to invoke a Dreams
pass or wire up the scheduler. See Docs/_phases/PHASE_6.md for the full
architecture and lifecycle.
"""

from __future__ import annotations

from .errors import (
    DreamsLLMError,
    DreamsRunError,
    DreamsScheduleError,
)
from .llm import BDOne, BDOneCompletion, BDOneSettings, StubBDOne

__all__ = [
    "BDOne",
    "BDOneCompletion",
    "BDOneSettings",
    "DreamsLLMError",
    "DreamsRunError",
    "DreamsScheduleError",
    "StubBDOne",
]
