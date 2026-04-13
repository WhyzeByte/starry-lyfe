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


class VoiceMode(StrEnum):
    """Closed enum of voice modes for mode-aware exemplar selection (Phase E).

    Each Voice.md example is tagged with one or more modes via
    ``<!-- mode: X, Y -->`` comments. The mode-aware selector uses
    these tags to filter and rank exemplars based on the active scene.
    """

    DOMESTIC = "domestic"
    CONFLICT = "conflict"
    INTIMATE = "intimate"
    PUBLIC = "public"
    GROUP = "group"
    REPAIR = "repair"
    SILENT = "silent"
    SOLO_PAIR = "solo_pair"
    ESCALATION = "escalation"
    WARM_REFUSAL = "warm_refusal"
    GROUP_TEMPERATURE = "group_temperature"


@dataclass
class VoiceExample:
    """A parsed voice exemplar from a Voice.md file (Phase E).

    Carries the structured data needed for mode-aware selection: mode
    tags, teaching prose, and the abbreviated text that ships to Layer 5.
    """

    title: str
    modes: list[VoiceMode]
    teaching_prose: str
    abbreviated_text: str | None
    communication_mode: str  # "any" | CommunicationMode value
    index: int  # Original file order position for stable sorting


@dataclass
class SceneState:
    """Current scene state for context assembly decisions."""

    present_characters: list[str] = field(default_factory=list)
    public_scene: bool = False
    alicia_home: bool = False
    scene_description: str = ""
    communication_mode: CommunicationMode = CommunicationMode.IN_PERSON
    recalled_dyads: set[str] = field(default_factory=set)
    voice_modes: list[VoiceMode] | None = None

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
