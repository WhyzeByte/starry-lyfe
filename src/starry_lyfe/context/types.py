"""Data types for the context assembly layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class CommunicationMode(StrEnum):
    """Canonical communication modes that affect assembly rules."""

    IN_PERSON = "in_person"
    PHONE = "phone"
    LETTER = "letter"
    VIDEO_CALL = "video_call"


@dataclass
class SceneState:
    """Current scene state for context assembly decisions."""

    present_characters: list[str] = field(default_factory=list)
    children_present: bool = False
    public_scene: bool = False
    alicia_home: bool = False
    scene_description: str = ""
    communication_mode: CommunicationMode = CommunicationMode.IN_PERSON
    recalled_dyads: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if not isinstance(self.communication_mode, CommunicationMode):
            self.communication_mode = CommunicationMode(self.communication_mode)


@dataclass
class LayerContent:
    """A single assembled layer with its text and token estimate."""

    name: str
    text: str
    estimated_tokens: int
    layer_number: int


@dataclass
class AssembledPrompt:
    """The fully assembled seven-layer prompt with metadata."""

    prompt: str
    character_id: str
    layers: list[LayerContent]
    total_tokens: int
    constraint_block_position: str

    @property
    def is_terminally_anchored(self) -> bool:
        """Verify Layer 7 constraints are the final block in the actual prompt body."""
        if self.constraint_block_position != "terminal":
            return False
        # Structural check: prompt must end with the CONSTRAINTS closing tag
        return self.prompt.rstrip().endswith("</CONSTRAINTS>")
