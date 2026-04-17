"""Shared dataclasses for the Dreams pipeline.

Kept in a dedicated module so ``runner``, ``generators/*``, and
``writers`` can import without circular-dep headaches.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol

from ..canon.loader import Canon
from ..canon.schemas.routines import CharacterRoutines
from .consistency.schemas import ConsistencyQAOutput


# BDOne and StubBDOne both conform to this shape; generators accept either.
class LLMClient(Protocol):
    """Duck-typed interface covering BDOne and StubBDOne for generators."""

    @property
    def circuit_open(self) -> bool: ...

    def reset_circuit(self) -> None: ...

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        max_tokens: int = ...,
        temperature: float = ...,
    ) -> Any: ...


# BDOne + StubBDOne structurally satisfy LLMClient; mypy validates this at
# every generator call site that declares ``llm_client: LLMClient``.


@dataclass(frozen=True)
class SessionSnapshot:
    """24-hour read-only snapshot of a single character's pre-pass state.

    All fields are lists of domain-level dataclasses or ORM objects. Dreams
    generators consume this as their primary session-data input. Constructed
    by runner.py before invoking the generators; generators never touch the
    DB directly.
    """

    character_id: str
    episodic_memories: list[Any] = field(default_factory=list)
    open_loops: list[Any] = field(default_factory=list)
    somatic_state: Any | None = None
    dyad_states_whyze: list[Any] = field(default_factory=list)
    dyad_states_internal: list[Any] = field(default_factory=list)
    life_state: Any | None = None


@dataclass(frozen=True)
class GenerationContext:
    """Inputs passed to every Dreams generator."""

    character_id: str
    canon: Canon
    routines: CharacterRoutines
    prior_session: SessionSnapshot
    llm_client: LLMClient
    now: datetime


@dataclass(frozen=True)
class GenerationOutput:
    """Result of a single Dreams generator.

    ``rendered_prose`` is the Phase G per-character prose-rendered text
    that will reach the DB. ``raw_llm_text`` is retained for debugging
    but is never persisted directly (Phase G retroactive).
    """

    kind: str  # "schedule" | "off_screen" | "diary" | "open_loops" | "activity_design"
    raw_llm_text: str
    rendered_prose: str
    structured_data: dict[str, Any]
    input_tokens: int
    output_tokens: int
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DreamsCharacterResult:
    """Outcome of Dreams processing a single character."""

    character_id: str
    schedule_generated: bool
    off_screen_events_count: int
    diary_entry_id: uuid.UUID | None
    open_loops_resolved: int
    open_loops_added: int
    activities_designed: int
    dyad_deltas_applied: int
    somatic_refreshed: bool
    input_tokens: int
    output_tokens: int
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DreamsPassResult:
    """Aggregate result of one Dreams pass across all 4 characters.

    Phase 10.7: ``consistency_qa`` carries the sixth Dreams generator's
    aggregate verdict across all 10 relationships. None when the QA pass
    is disabled or skipped (e.g., dry-run mode); otherwise present.
    """

    run_id: uuid.UUID
    character_results: dict[str, DreamsCharacterResult]
    started_at: datetime
    finished_at: datetime
    total_input_tokens: int
    total_output_tokens: int
    warnings: list[str] = field(default_factory=list)
    consistency_qa: ConsistencyQAOutput | None = None
