"""Pydantic v2 schema for dyads.yaml."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from .enums import DyadSubtype, DyadType, PairName


class DimensionBaseline(BaseModel):
    """A single dyad dimension with baseline and range."""

    baseline: float = Field(ge=0.0, le=1.0)
    min: float = Field(ge=0.0, le=1.0)
    max: float = Field(ge=0.0, le=1.0)


class DyadDimensions(BaseModel):
    """The five canonical dyad dimensions."""

    trust: DimensionBaseline
    intimacy: DimensionBaseline
    conflict: DimensionBaseline
    unresolved_tension: DimensionBaseline
    repair_history: DimensionBaseline


class Dyad(BaseModel):
    """A canonical dyad entry."""

    members: list[str] = Field(min_length=2, max_length=2)
    type: DyadType
    subtype: DyadSubtype | None = None
    interlock: str | None = None
    pair: PairName | None = None
    is_currently_active: bool | None = None
    dimensions: DyadDimensions

    @model_validator(mode="after")
    def members_must_be_distinct(self) -> Dyad:
        if self.members[0] == self.members[1]:
            msg = f"Dyad members must be distinct, got duplicate: '{self.members[0]}'"
            raise ValueError(msg)
        return self


class MemoryTier(BaseModel):
    """A canonical memory tier definition."""

    name: str
    tier: int = Field(ge=1, le=7)
    mutable: bool
    description: str


class CanonDyads(BaseModel):
    """Root schema for dyads.yaml."""

    version: str
    dyads: dict[str, Dyad]
    memory_tiers: list[MemoryTier]

    @model_validator(mode="after")
    def validate_counts(self) -> CanonDyads:
        if len(self.memory_tiers) != 7:
            msg = f"Expected exactly 7 memory tiers, got {len(self.memory_tiers)}"
            raise ValueError(msg)
        return self
