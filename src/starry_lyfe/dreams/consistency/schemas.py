"""Pydantic v2 schemas for the Dreams Consistency QA pass.

The QA judge LLM returns a JSON object that parses through
``RelationshipCheck`` per relationship. The runner aggregates one
``RelationshipCheck`` per relationship into a single
``ConsistencyQAOutput`` per nightly pass.

Three verdicts (per Phase 10.7 spec + AC-10.24..AC-10.28):

- ``healthy_divergence`` — POVs differ but the gap is canonical and
  dramaturgically correct. Surfaced as scene fodder.
- ``concerning_drift`` — POVs are wandering away from the shared anchor
  but not yet contradictory. Logged; auto-promoted to
  ``factual_contradiction`` if the same (relationship, field) is flagged
  3 nights running.
- ``factual_contradiction`` — POVs contradict a ``shared_canon.yaml``
  fact. Pinned to last-coherent value; operator notified; Phase 9
  evaluator refuses to update pinned fields until operator resolves.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class QAVerdict(StrEnum):
    """Three terminal verdicts a relationship check can resolve to."""

    HEALTHY_DIVERGENCE = "healthy_divergence"
    CONCERNING_DRIFT = "concerning_drift"
    FACTUAL_CONTRADICTION = "factual_contradiction"


class Contradiction(BaseModel):
    """One contradicted field surfaced by the judge.

    ``shared_canon_field`` is the dotted path the contradiction violates
    (e.g., ``shared_canon.marriage.year``, ``shared_canon.pairs[0].canonical_name``).
    The Phase 9 evaluator pin lookup keys on (relationship_key, pov_character_id,
    field_name) — ``field_name`` here is the per-character field that drifted,
    not the shared_canon path.
    """

    model_config = ConfigDict(extra="forbid")

    field_name: str = Field(..., min_length=1, description="The per-character field that drifted")
    pov_character_id: str | None = Field(
        default=None,
        description="NULL = symmetric contradiction; set = asymmetric (only this POV is wrong)",
    )
    shared_canon_field: str = Field(..., min_length=1, description="The shared_canon dotted path violated")
    observed_value: str = Field(..., description="What the per-character POV says")
    canonical_value: str = Field(..., description="What shared_canon says (the anchor)")
    severity_note: str = Field(default="", description="Optional judge commentary")


class RelationshipCheck(BaseModel):
    """One relationship's QA verdict for one nightly pass."""

    model_config = ConfigDict(extra="forbid")

    relationship_key: str = Field(..., min_length=1, description="e.g. adelia_bina, whyze_alicia")
    verdict: QAVerdict
    divergence_summary: str = Field(
        default="",
        description="Neutral-observer summary of the gap between POVs (1-3 sentences)",
    )
    contradictions: list[Contradiction] = Field(
        default_factory=list,
        description="Empty for healthy_divergence; non-empty for factual_contradiction",
    )
    scene_fodder: list[str] = Field(
        default_factory=list,
        description="Healthy-divergence scene seeds. Each item lands as one open_loops row with source='dreams_qa'.",
    )


class ConsistencyQAOutput(BaseModel):
    """Aggregate output of one nightly consistency QA pass.

    Carries one ``RelationshipCheck`` per of the 10 relationships
    (6 inter-woman + 4 woman-Whyze pair).
    """

    model_config = ConfigDict(extra="forbid")

    run_id: uuid.UUID
    started_at: datetime
    finished_at: datetime
    relationship_checks: list[RelationshipCheck] = Field(
        ...,
        min_length=10,
        max_length=10,
        description="Exactly 10 entries: 6 inter-woman dyads + 4 woman-Whyze pairs",
    )
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    warnings: list[str] = Field(default_factory=list)

    @property
    def healthy_count(self) -> int:
        return sum(
            1 for r in self.relationship_checks
            if r.verdict is QAVerdict.HEALTHY_DIVERGENCE
        )

    @property
    def concerning_count(self) -> int:
        return sum(
            1 for r in self.relationship_checks
            if r.verdict is QAVerdict.CONCERNING_DRIFT
        )

    @property
    def contradiction_count(self) -> int:
        return sum(
            1 for r in self.relationship_checks
            if r.verdict is QAVerdict.FACTUAL_CONTRADICTION
        )
