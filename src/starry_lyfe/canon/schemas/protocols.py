"""Pydantic v2 schema for protocols.yaml."""

from __future__ import annotations

from pydantic import BaseModel, model_validator

from .enums import ProtocolCategory

# The 12 protocols from Vision section 7 (canonical set).
VISION_SECTION_7_PROTOCOLS: frozenset[str] = frozenset({
    "flat_state",
    "post_race_crash",
    "four_phase_return",
    "sun_override",
    "taurus_venus_override",
    "whiteboard_mode",
    "red_team_stabilization",
    "perfection_anchoring",
    "alexithymia_protocol",
    "interoceptive_override",
    "admissibility_protocol",
    "bunker_mode",
})

ALLOWED_PROTOCOL_EXTENSION_SOURCES: frozenset[str] = frozenset({
    "character_kernel",
})


class RecoveryRole(BaseModel):
    """A responder role in a recovery architecture."""

    character: str
    role: str


class RecoveryArchitecture(BaseModel):
    """Multi-responder recovery sequence for a protocol."""

    first_responder: RecoveryRole
    second_responder: RecoveryRole
    third_responder: RecoveryRole


class Protocol(BaseModel):
    """A canonical named protocol."""

    name: str
    primary_character: str
    secondary_characters: list[str] = []
    category: ProtocolCategory
    description: str
    entry_conditions: str
    recovery_architecture: RecoveryArchitecture | None = None
    source: str | None = None


class CanonProtocols(BaseModel):
    """Root schema for protocols.yaml."""

    version: str
    protocols: dict[str, Protocol]

    @model_validator(mode="after")
    def validate_protocol_inventory(self) -> CanonProtocols:
        protocol_keys = set(self.protocols.keys())
        missing = VISION_SECTION_7_PROTOCOLS - protocol_keys
        if missing:
            msg = f"Missing Vision section 7 protocols: {sorted(missing)}"
            raise ValueError(msg)

        extra_protocols = protocol_keys - VISION_SECTION_7_PROTOCOLS
        for protocol_name in sorted(extra_protocols):
            source = self.protocols[protocol_name].source
            if source not in ALLOWED_PROTOCOL_EXTENSION_SOURCES:
                msg = (
                    f"Protocol extension '{protocol_name}' must declare one of "
                    f"{sorted(ALLOWED_PROTOCOL_EXTENSION_SOURCES)} as its source"
                )
                raise ValueError(msg)

        for protocol_name in sorted(VISION_SECTION_7_PROTOCOLS):
            if self.protocols[protocol_name].source is not None:
                msg = f"Vision section 7 protocol '{protocol_name}' must not declare an extension source"
                raise ValueError(msg)

        return self
