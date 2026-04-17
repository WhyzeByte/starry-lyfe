"""Phase 6 + 10.7 Dreams content generators.

Each per-character generator is an async function
``generate_<kind>(ctx) -> GenerationOutput``. The Phase 6 set:

- ``schedule``: deterministic from ``routines.yaml``
- ``diary``: LLM-backed, wrapped through Phase G prose rendering
- ``off_screen``: LLM-backed overnight events
- ``open_loops``: LLM-backed loop extraction / resolution candidates
- ``activity_design``: LLM-backed next-session opener design

Every per-character generator is a pure function: it reads ``ctx``
(GenerationContext) and returns a ``GenerationOutput``. They never touch the DB.

Phase 10.7 adds the sixth generator — ``generate_consistency_qa`` — which
runs AFTER all five per-character generators complete (relationship-scoped,
not character-scoped). It DOES touch the DB (writes ``dreams_qa_log`` and
``dyad_state_pins`` rows) and is not a pure function — that's the
deliberate distinction between the per-character pre-pass generators and
the cross-character consistency judge.
"""

from __future__ import annotations

from .activity_design import generate_activity_design
from .consistency_qa import generate_consistency_qa
from .diary import generate_diary
from .off_screen import generate_off_screen
from .open_loops import generate_open_loops
from .schedule import generate_schedule

__all__ = [
    "generate_activity_design",
    "generate_consistency_qa",
    "generate_diary",
    "generate_off_screen",
    "generate_open_loops",
    "generate_schedule",
]
