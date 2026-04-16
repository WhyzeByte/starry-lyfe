"""Soul card loader and activation engine.

Soul cards are compact runtime-loadable distillations of pair files and
knowledge stacks. They carry the deepest character differentiation into
the assembled prompt without loading the full 15-80K source documents.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

from .budgets import estimate_tokens, trim_text_to_budget

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SOUL_CARDS_DIR = PROJECT_ROOT / "src" / "starry_lyfe" / "canon" / "soul_cards"

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


class SoulCardActivation(BaseModel):
    """Typed activation rules for soul cards (R-2.3).

    Validated at load time via Pydantic. Invalid frontmatter fails
    immediately rather than silently mis-activating at scene build time.

    Fields mirror the four canonical activation patterns:
    - always: unconditional activation
    - communication_mode: activate when scene.communication_mode matches
    - with_character: activate when any listed character is present
    - scene_keyword: activate when any keyword substring matches scene_description
    """

    model_config = ConfigDict(extra="forbid")  # reject unknown activation fields

    always: bool = False
    communication_mode: list[str] = Field(default_factory=list)
    with_character: list[str] = Field(default_factory=list)
    scene_keyword: list[str] = Field(default_factory=list)


@dataclass
class SoulCard:
    """A single soul card with metadata and body text."""

    character: str
    card_type: str
    source: str
    budget_tokens: int
    activation: SoulCardActivation = field(default_factory=SoulCardActivation)
    required_concepts: list[str] = field(default_factory=list)
    body: str = ""
    file_path: str = ""

    @property
    def is_placeholder(self) -> bool:
        return "[PLACEHOLDER" in self.body


def load_soul_card(path: Path | str) -> SoulCard:
    """Parse a soul card file (YAML frontmatter + markdown body)."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(text)
    if not match:
        msg = f"No YAML frontmatter found in {path}"
        raise ValueError(msg)

    frontmatter = yaml.safe_load(match.group(1))
    body = text[match.end():].strip()

    activation_data = frontmatter.get("activation", {}) or {}
    activation = SoulCardActivation.model_validate(activation_data)

    return SoulCard(
        character=frontmatter.get("character", ""),
        card_type=frontmatter.get("card_type", ""),
        source=frontmatter.get("source", ""),
        budget_tokens=frontmatter.get("budget_tokens", 500),
        activation=activation,
        required_concepts=frontmatter.get("required_concepts", []),
        body=body,
        file_path=str(path),
    )


def load_all_soul_cards() -> list[SoulCard]:
    """Load all soul cards from the rich per-character YAMLs (Phase 10.3b).

    Previously read from ``src/starry_lyfe/canon/soul_cards/*.md``. Phase
    10.3b embedded each card's frontmatter + body into the per-character
    YAML under the ``soul_cards`` block. This function now iterates
    ``RichCharacter.soul_cards`` and converts each entry to the same
    ``SoulCard`` dataclass shape the rest of the system consumes.
    """
    from starry_lyfe.canon.rich_loader import load_all_rich_characters

    cards: list[SoulCard] = []
    for cid, rc in load_all_rich_characters().items():
        if not rc.soul_cards:
            continue
        for yc in rc.soul_cards:
            act_data = {
                "always": yc.activation.always,
                "communication_mode": yc.activation.communication_mode or [],
                "with_character": yc.activation.with_character or [],
                "scene_keyword": yc.activation.scene_keyword or [],
            }
            cards.append(SoulCard(
                character=cid,
                card_type=yc.card_type,
                source=yc.source or "",
                budget_tokens=yc.budget_tokens,
                activation=SoulCardActivation.model_validate(act_data),
                required_concepts=list(yc.required_concepts or []),
                body=yc.body,
                file_path=yc.source_file,
            ))
    return cards


def find_activated_cards(
    character_id: str,
    scene_state: Any | None = None,
    communication_mode: str | None = None,
) -> list[SoulCard]:
    """Return soul cards whose activation rules match the current scene."""
    all_cards = load_all_soul_cards()
    activated: list[SoulCard] = []

    for card in all_cards:
        if card.character != character_id:
            continue

        act = card.activation

        if act.always:
            activated.append(card)
            continue

        if (
            communication_mode
            and act.communication_mode
            and communication_mode in act.communication_mode
        ):
            activated.append(card)
            continue

        if scene_state and act.with_character:
            present = getattr(scene_state, "present_characters", [])
            if any(c in present for c in act.with_character):
                activated.append(card)
                continue

        if scene_state and act.scene_keyword:
            desc = getattr(scene_state, "scene_description", "")
            if any(kw.lower() in desc.lower() for kw in act.scene_keyword):
                activated.append(card)
                continue

    return activated


def format_soul_cards(cards: list[SoulCard], budget: int) -> str:
    """Assemble activated soul cards into a formatted text block within budget."""
    if not cards:
        return ""

    sections: list[str] = []
    remaining = budget

    for card in cards:
        if card.is_placeholder:
            continue
        trimmed = trim_text_to_budget(card.body, min(card.budget_tokens, remaining))
        if trimmed and estimate_tokens(trimmed) > 5:
            sections.append(trimmed)
            remaining -= estimate_tokens(trimmed)
            if remaining <= 0:
                break

    return "\n\n".join(sections)
