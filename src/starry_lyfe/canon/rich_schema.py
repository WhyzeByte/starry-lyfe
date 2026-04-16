"""Pydantic v2 schemas for the 5 rich per-character YAMLs (Phase 10.1).

These models define the typed surface that ``rich_loader.py`` validates
against. The schemas run *alongside* the existing narrow-canon loaders
— zero runtime integration in Phase 10.1. Cutovers happen in 10.2–10.4.

Design: load-bearing fields are typed; remaining fields accepted via
``extra="allow"`` so the rich YAMLs load without rejecting content
that Phase 10.6 will formalize. The ``preserve_markers`` enforcement
contract is enforced at load time by the rich loader, not by the schema.

Authority: ``Docs/_phases/PHASE_10.md`` §Phase 10.1 +
``Docs/_phases/PHASE_10_GAP_AUDIT.md`` §1–§5.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class _Permissive(BaseModel):
    model_config = ConfigDict(extra="allow")


class PreserveMarker(_Permissive):
    id: str
    content_anchor: str
    rule: str


class NormalizationNote(_Permissive):
    id: str | None = None
    issue: str | None = None
    resolved_value: str | None = None


class CanonFact(_Permissive):
    category: str | None = None
    fact_text: str


class SoulBlock(_Permissive):
    label: str
    text: str


class SoulSubstrate(_Permissive):
    identity_blocks: list[SoulBlock]
    pair_blocks: list[SoulBlock] | None = None
    behavioral_blocks: list[SoulBlock] | None = None
    intimacy_blocks: list[SoulBlock] | None = None
    chosen_family_blocks: list[SoulBlock] | None = None
    mission_blocks: list[SoulBlock] | None = None


class FewShotExamples(_Permissive):
    note: str | None = None
    examples: list[dict[str, object]] | None = None


class Voice(_Permissive):
    baseline: str
    register_notes: str | None = None
    few_shots: FewShotExamples | None = None


class InterWomanDyad(_Permissive):
    interlock_name: str | None = None
    description: str | None = None
    tone: str | None = None
    truths: list[str] | str | None = None


class PreserveMarkersBlock(_Permissive):
    """Shawn's preserve_markers shape: ``{note, canonical_anchors}``."""

    note: str | None = None
    canonical_anchors: list[PreserveMarker] | None = None


class KernelSection(_Permissive):
    """A single numbered section from the character's kernel body."""

    section_num: int
    title: str
    body: str
    has_preserve_marker: bool = False


class SoulCardActivation(_Permissive):
    """Activation rules for a soul card."""

    always: bool = False
    communication_mode: list[str] | None = None
    with_character: list[str] | None = None
    scene_keyword: list[str] | None = None


class SoulCardYaml(_Permissive):
    """A single soul card embedded in the rich YAML."""

    card_type: str
    source_file: str
    source: str | None = None
    budget_tokens: int = 500
    activation: SoulCardActivation = SoulCardActivation()
    required_concepts: list[str] | None = None
    body: str


class Meta(_Permissive):
    full_name: str
    preserve_markers: list[PreserveMarker] | PreserveMarkersBlock | None = None


class RichCharacter(_Permissive):
    """Top-level schema for a per-character rich YAML (women + Shawn)."""

    version: str
    character_id: str
    meta: Meta
    identity: dict[str, object]
    soul_substrate: SoulSubstrate
    voice: Voice
    behavioral_framework: dict[str, object]
    canon_facts: list[CanonFact]
    normalization_notes: list[NormalizationNote] | None = None
    kernel_sections: list[KernelSection] | None = None

    # --- Woman-specific (optional for Shawn) ---
    pair_architecture: dict[str, object] | None = None
    scene_engine: dict[str, object] | None = None
    intimacy_architecture: dict[str, object] | None = None
    family_and_other_dyads: dict[str, InterWomanDyad] | None = None
    knowledge_stack: dict[str, object] | None = None

    # --- Soul cards (Phase 10.3b) ---
    soul_cards: list[SoulCardYaml] | None = None

    # --- Shawn-specific (optional for women) ---
    continuity_layers: dict[str, object] | None = None
    value_stack: dict[str, object] | None = None
    life_history: dict[str, object] | None = None
    self_knowledge_architecture: dict[str, object] | None = None
    bonding_architecture: dict[str, object] | None = None
