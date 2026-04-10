"""Pydantic v2 schema for characters.yaml."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from .enums import CharacterID, CognitiveFunction, MBTIType, PairName


class LanguageEntry(BaseModel):
    """A language register with usage context."""

    model_config = {"populate_by_name": True}

    register_name: str = Field(alias="register")
    context: str


class Parent(BaseModel):
    """A character's parent."""

    name: str
    origin: str
    profession: str


class ChildEntry(BaseModel):
    """A child in the household."""

    name: str
    age: int = Field(ge=0)
    relationship: str


class AstrologyPlacements(BaseModel):
    """Big-three astrology placements."""

    sun: str
    moon: str
    venus: str


class Sibling(BaseModel):
    """A character's sibling."""

    name: str
    location: str
    occupation: str


class FamilyMember(BaseModel):
    """A named family member with status."""

    name: str
    status: str


class FamilyNotes(BaseModel):
    """Extended family information."""

    twin_brother: FamilyMember | None = None
    parents_status: str | None = None
    ex_partner: FamilyMember | None = None


class ClinicalProfile(BaseModel):
    """Operator clinical profile."""

    asd_level: int
    twice_exceptional: bool


class Character(BaseModel):
    """A canonical character entry."""

    full_name: str
    role: Literal["character"]
    epithet: str
    age: int = Field(ge=18)
    birthdate: str | None = None
    mbti: MBTIType
    heritage: str
    birthplace: str
    raised_in: str
    current_residence: str
    is_resident: bool
    operational_travel: str | None = None
    pair_name: PairName
    profession: str
    business: str | None = None
    employer: str | None = None
    unit: str | None = None
    languages: list[LanguageEntry]
    parents: dict[str, Parent]
    children: list[ChildEntry] = []
    cognitive_function_stack: list[CognitiveFunction] = Field(min_length=4, max_length=4)
    dominant_function: CognitiveFunction
    spouse: str | None = None
    family_notes: FamilyNotes | None = None
    siblings: list[Sibling] | None = None
    astrology: AstrologyPlacements | None = None


class Operator(BaseModel):
    """The operator (Whyze/Shawn Kroon)."""

    full_name: str
    handle: str
    role: Literal["operator"]
    age: int
    mbti: MBTIType
    cognitive_function_stack: list[CognitiveFunction] = Field(min_length=4, max_length=4)
    dominant_function: CognitiveFunction
    clinical: ClinicalProfile | None = None
    disc: str | None = None
    astrology: AstrologyPlacements | None = None
    children: list[ChildEntry] = []
    profile_file: str
    profile_version: str


class CanonCharacters(BaseModel):
    """Root schema for characters.yaml."""

    version: str
    characters: dict[CharacterID, Character]
    operator: dict[str, Operator]

    @model_validator(mode="after")
    def validate_counts(self) -> CanonCharacters:
        if len(self.characters) != 4:
            msg = f"Expected exactly 4 characters, got {len(self.characters)}"
            raise ValueError(msg)
        if len(self.operator) != 1:
            msg = f"Expected exactly 1 operator, got {len(self.operator)}"
            raise ValueError(msg)
        return self

    def all_character_ids(self) -> set[str]:
        """Return all character IDs plus operator handle."""
        ids: set[str] = {c.value for c in self.characters}
        for op in self.operator.values():
            ids.add(op.handle.lower())
        return ids

