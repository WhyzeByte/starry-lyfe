"""Pydantic v2 schema for interlocks.yaml."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from .enums import InterlockType


class Interlock(BaseModel):
    """A canonical cross-partner interlock."""

    name: str
    members: list[str] = Field(min_length=2, max_length=2)
    description: str
    tone: str
    type: InterlockType
    origin: str | None = None
    canonical_disagreement: str | None = None

    @model_validator(mode="after")
    def members_must_be_distinct(self) -> Interlock:
        if self.members[0] == self.members[1]:
            msg = f"Interlock members must be distinct, got duplicate: '{self.members[0]}'"
            raise ValueError(msg)
        return self


class CanonInterlocks(BaseModel):
    """Root schema for interlocks.yaml."""

    version: str
    interlocks: dict[str, Interlock]

    @model_validator(mode="after")
    def exactly_six_interlocks(self) -> CanonInterlocks:
        if len(self.interlocks) != 6:
            msg = f"Expected exactly 6 interlocks, got {len(self.interlocks)}"
            raise ValueError(msg)
        return self
