"""Phase 6 Dreams content generators.

Each generator is an async function ``generate_<kind>(ctx) -> GenerationOutput``.
The shipped set is:
- ``schedule``: deterministic from ``routines.yaml``
- ``diary``: LLM-backed, wrapped through Phase G prose rendering
- ``off_screen``: LLM-backed overnight events
- ``open_loops``: LLM-backed loop extraction / resolution candidates
- ``activity_design``: LLM-backed next-session opener design

Every generator is a pure function: it reads ``ctx`` (GenerationContext)
and returns a ``GenerationOutput``. Generators never touch the DB.
"""

from __future__ import annotations

from .activity_design import generate_activity_design
from .diary import generate_diary
from .off_screen import generate_off_screen
from .open_loops import generate_open_loops
from .schedule import generate_schedule

__all__ = [
    "generate_activity_design",
    "generate_diary",
    "generate_off_screen",
    "generate_open_loops",
    "generate_schedule",
]
