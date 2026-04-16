"""Seed Msty Persona Studio few-shot configuration from rich character YAMLs.

Reads ``Characters/{name}.yaml::voice.few_shots.examples[]`` for all four
women and produces a JSON configuration suitable for loading into Msty
Persona Studio. Each rich YAML entry maps one-to-one to a Msty few-shot
exemplar: ``id`` -> ``title``, ``user`` (or ``user_setup`` when only a
scene setup is authored) -> ``user``, ``assistant`` (the in-character
block scalar) -> ``assistant``.

Authority: Phase 10 rich YAML is the sole canonical source for character
content (per ``CLAUDE.md §19`` + ``Archive/v7.1_pre_yaml/MANIFEST.md``).
Voice.md markdown files are archived; this script does not read them.
Manual copy-paste from any character source is not authorized — this
script is the only canonical way to configure Msty Persona Studio
few-shots.

Protocol droids: None (standalone script, no runtime service dependencies).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TypedDict

from starry_lyfe.canon.rich_loader import load_all_rich_characters

PROJECT_ROOT = Path(__file__).resolve().parent.parent

WOMAN_IDS: tuple[str, ...] = ("adelia", "bina", "reina", "alicia")


class FewShotEntry(TypedDict):
    """A single few-shot exemplar for Msty Persona Studio."""

    title: str
    user: str
    assistant: str


class PersonaConfig(TypedDict):
    """Per-character Msty Persona Studio configuration."""

    character_id: str
    few_shots: list[FewShotEntry]


def _extract_few_shots_from_rich(character_id: str) -> list[FewShotEntry]:
    """Extract few-shot entries from a rich character YAML.

    Reads ``voice.few_shots.examples[]``. Each entry must carry an
    ``id``, an ``assistant`` block, and either a ``user`` line or a
    ``user_setup`` description. Entries missing either end are skipped
    (authoring-in-progress cases).
    """
    chars = load_all_rich_characters()
    rc = chars.get(character_id)
    if rc is None:
        return []

    fs = rc.voice.few_shots
    if fs is None or not fs.examples:
        return []

    entries: list[FewShotEntry] = []
    for raw in fs.examples:
        if not isinstance(raw, dict):
            continue
        title = str(raw.get("id") or "").strip()
        user_line = str(raw.get("user") or raw.get("user_setup") or "").strip()
        assistant = str(raw.get("assistant") or "").strip()
        if not (title and user_line and assistant):
            continue
        entries.append(FewShotEntry(
            title=title,
            user=user_line,
            assistant=assistant,
        ))
    return entries


def build_persona_configs() -> list[PersonaConfig]:
    """Build Msty Persona Studio configuration for all four women."""
    configs: list[PersonaConfig] = []
    warnings: list[str] = []

    for character_id in WOMAN_IDS:
        few_shots = _extract_few_shots_from_rich(character_id)
        if not few_shots:
            warnings.append(
                f"WARNING: No few_shots.examples authored for {character_id} "
                f"in Characters/{character_id}_*.yaml::voice.few_shots.examples"
            )
        configs.append(PersonaConfig(
            character_id=character_id,
            few_shots=few_shots,
        ))

    for warning in warnings:
        print(warning, file=sys.stderr)

    return configs


def main() -> None:
    """Generate Msty Persona Studio JSON configuration to stdout."""
    configs = build_persona_configs()
    output = {
        "generated_by": "seed_msty_persona_studio.py",
        "source_of_truth": "Characters/{name}.yaml::voice.few_shots.examples[]",
        "authority": "Phase 10 rich YAML (sole canonical source)",
        "personas": configs,
    }
    json.dump(output, sys.stdout, indent=2, ensure_ascii=False)
    print()  # trailing newline


if __name__ == "__main__":
    main()
