"""Pydantic v2 schema for voice_parameters.yaml."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from .enums import CharacterID, ThinkingEffort


class TemperatureRange(BaseModel):
    """Temperature range with midpoint."""

    range: tuple[float, float]
    midpoint: float

    @model_validator(mode="after")
    def midpoint_within_range(self) -> TemperatureRange:
        low, high = self.range
        if not (low <= self.midpoint <= high):
            msg = f"Midpoint {self.midpoint} not within range [{low}, {high}]"
            raise ValueError(msg)
        return self


class VoiceParameter(BaseModel):
    """Per-character inference parameters."""

    character: CharacterID
    temperature: TemperatureRange
    top_p: float = Field(ge=0.0, le=1.0)
    thinking_effort: ThinkingEffort
    distinctive_sampling: str | None = None
    presence_penalty: float = Field(ge=0.0, le=2.0)
    frequency_penalty: float = Field(ge=0.0, le=2.0)
    response_length: str
    response_length_range: str
    dominant_function_descriptor: str


class CanonVoiceParameters(BaseModel):
    """Root schema for voice_parameters.yaml."""

    version: str
    voice_parameters: dict[CharacterID, VoiceParameter]

    @model_validator(mode="after")
    def exactly_four_characters(self) -> CanonVoiceParameters:
        if len(self.voice_parameters) != 4:
            msg = f"Expected exactly 4 voice parameter sets, got {len(self.voice_parameters)}"
            raise ValueError(msg)
        return self
