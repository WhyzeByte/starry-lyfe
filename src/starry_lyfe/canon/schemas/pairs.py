"""Pydantic v2 schema for pairs.yaml."""

from __future__ import annotations

from pydantic import BaseModel, model_validator

from .enums import CharacterID, PairCadence, PairName


class Pair(BaseModel):
    """A canonical Whyze-to-character pair."""

    character: CharacterID
    full_name: str
    classification: str
    shared_functions: str
    mechanism: str
    what_she_provides: str
    how_she_breaks_spiral: str
    core_metaphor: str
    cadence: PairCadence


class CanonPairs(BaseModel):
    """Root schema for pairs.yaml."""

    version: str
    pairs: dict[PairName, Pair]

    @model_validator(mode="after")
    def exactly_four_pairs(self) -> CanonPairs:
        if len(self.pairs) != 4:
            msg = f"Expected exactly 4 pairs, got {len(self.pairs)}"
            raise ValueError(msg)
        return self
