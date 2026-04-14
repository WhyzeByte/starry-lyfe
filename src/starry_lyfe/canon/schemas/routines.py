"""Pydantic v2 schema for routines.yaml (Phase 6 Dreams canonical source)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .enums import CharacterID


class DailyBlock(BaseModel):
    """A single slot in a character's daily routine."""

    model_config = ConfigDict(extra="forbid")

    time: str = Field(..., description="Local time, HH:MM 24h.")
    activity: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)


class RecurringEvent(BaseModel):
    """A recurring event in a character's weekly/monthly cadence."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    cadence: str = Field(..., description="e.g. weekly, monthly, quarterly, operation-specific")
    weekday: str | None = Field(default=None, description="Weekday anchor, if applicable.")
    notes: str = Field(..., min_length=1)


class CharacterRoutines(BaseModel):
    """A single character's routine stanza."""

    model_config = ConfigDict(extra="forbid")

    character: CharacterID
    weekday: list[DailyBlock] = Field(..., min_length=1)
    weekend: list[DailyBlock] = Field(..., min_length=1)
    recurring_events: list[RecurringEvent] = Field(default_factory=list)


class AliciaCommunicationDistribution(BaseModel):
    """Weighted distribution over communication_mode for Alicia-away Dreams output.

    Summed weights should approximate 1.0 (not strictly enforced — generators
    normalize before sampling). Phase A'' retroactive: when Alicia is away
    and communication_mode is IN_PERSON would be invalid, Dreams samples
    from this distribution to pick phone/letter/video_call per artifact.
    """

    model_config = ConfigDict(extra="forbid")

    phone: float = Field(..., ge=0.0, le=1.0)
    letter: float = Field(..., ge=0.0, le=1.0)
    video_call: float = Field(..., ge=0.0, le=1.0)


class CanonRoutines(BaseModel):
    """Root schema for routines.yaml."""

    model_config = ConfigDict(extra="forbid")

    version: str
    routines: dict[CharacterID, CharacterRoutines]
    alicia_communication_distribution: AliciaCommunicationDistribution

    @model_validator(mode="after")
    def exactly_four_characters(self) -> CanonRoutines:
        if len(self.routines) != 4:
            msg = f"routines.yaml: expected exactly 4 character stanzas, got {len(self.routines)}"
            raise ValueError(msg)
        for char_id, stanza in self.routines.items():
            if stanza.character != char_id:
                msg = (
                    f"routines.yaml: stanza key '{char_id}' does not match its "
                    f"'character' field '{stanza.character}'"
                )
                raise ValueError(msg)
        return self
