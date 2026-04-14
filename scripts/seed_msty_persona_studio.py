"""Seed Msty Persona Studio few-shot configuration from canonical Voice.md files.

This script reads the Voice.md files for all four characters, extracts the
abbreviated exemplar text (added during Phase E), and produces a JSON
configuration suitable for loading into Msty Persona Studio.

Authority: ADR-001 (Backend-authoritative voice). This script is the only
canonical way to configure Msty persona studio few-shots. Manual copy-paste
from Voice.md is not authorized.

Protocol droids: None (standalone script, no runtime service dependencies).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import TypedDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent

VOICE_PATHS: dict[str, tuple[str, ...]] = {
    "adelia": (
        "Characters/Adelia_Raye_Voice.md",
        "Characters/Adelia/Adelia_Raye_Voice.md",
    ),
    "bina": (
        "Characters/Bina_Malek_Voice.md",
        "Characters/Bina/Bina_Malek_Voice.md",
    ),
    "reina": (
        "Characters/Reina_Torres_Voice.md",
        "Characters/Reina/Reina_Torres_Voice.md",
    ),
    "alicia": (
        "Characters/Alicia_Marin_Voice.md",
        "Characters/Alicia/Alicia_Marin_Voice.md",
    ),
}

_EXAMPLE_HEADING_RE = re.compile(r"^## Example \d+:\s*(.+)$")
_ABBREVIATED_RE = re.compile(r"^\*\*Abbreviated:\*\*\s*(.*)$")
_USER_RE = re.compile(r"^\*\*User:\*\*\s*(.*)$")
_ASSISTANT_RE = re.compile(r"^\*\*Assistant:\*\*\s*(.*)$")


class FewShotEntry(TypedDict):
    """A single few-shot exemplar for Msty Persona Studio."""

    title: str
    user: str
    assistant: str


class PersonaConfig(TypedDict):
    """Per-character Msty Persona Studio configuration."""

    character_id: str
    few_shots: list[FewShotEntry]


def _resolve_repo_path(rel_paths: tuple[str, ...]) -> Path | None:
    """Return the first existing project-relative path from the candidates."""
    for rel_path in rel_paths:
        full_path = PROJECT_ROOT / rel_path
        if full_path.exists():
            return full_path
    return None


def _extract_few_shots(raw_text: str) -> list[FewShotEntry]:
    """Extract few-shot entries from a Voice.md file.

    Each entry consists of the example title, the User block, and the
    abbreviated Assistant text. Examples without an **Abbreviated:** section
    are skipped (they have not been authored yet).
    """
    entries: list[FewShotEntry] = []
    current_title: str | None = None
    current_user_lines: list[str] = []
    current_abbreviated: str | None = None
    in_user_block = False
    in_abbreviated_block = False

    for line in raw_text.splitlines():
        stripped = line.strip()

        heading_match = _EXAMPLE_HEADING_RE.match(stripped)
        if heading_match:
            # Flush previous example
            if current_title and current_abbreviated and current_user_lines:
                entries.append(FewShotEntry(
                    title=current_title,
                    user="\n".join(current_user_lines).strip(),
                    assistant=current_abbreviated,
                ))
            current_title = heading_match.group(1).strip()
            current_user_lines = []
            current_abbreviated = None
            in_user_block = False
            in_abbreviated_block = False
            continue

        abbreviated_match = _ABBREVIATED_RE.match(stripped)
        if abbreviated_match:
            first_line = abbreviated_match.group(1).strip()
            current_abbreviated = first_line if first_line else None
            in_user_block = False
            in_abbreviated_block = True
            continue

        user_match = _USER_RE.match(stripped)
        if user_match:
            in_user_block = True
            in_abbreviated_block = False
            first_line = user_match.group(1).strip()
            current_user_lines = [first_line] if first_line else []
            continue

        assistant_match = _ASSISTANT_RE.match(stripped)
        if assistant_match:
            in_user_block = False
            in_abbreviated_block = False
            continue

        if stripped == "---":
            in_user_block = False
            in_abbreviated_block = False
            continue

        if in_abbreviated_block and stripped:
            current_abbreviated = (
                current_abbreviated + " " + stripped
                if current_abbreviated is not None
                else stripped
            )
        elif in_user_block and stripped:
            current_user_lines.append(stripped)

    # Flush last example
    if current_title and current_abbreviated and current_user_lines:
        entries.append(FewShotEntry(
            title=current_title,
            user="\n".join(current_user_lines).strip(),
            assistant=current_abbreviated,
        ))

    return entries


def build_persona_configs() -> list[PersonaConfig]:
    """Build Msty Persona Studio configuration for all characters."""
    configs: list[PersonaConfig] = []
    warnings: list[str] = []

    for character_id, rel_paths in VOICE_PATHS.items():
        full_path = _resolve_repo_path(rel_paths)
        if full_path is None:
            warnings.append(
                f"WARNING: Voice file not found for {character_id}: {list(rel_paths)}"
            )
            continue

        raw_text = full_path.read_text(encoding="utf-8")
        few_shots = _extract_few_shots(raw_text)

        try:
            resolved_rel_path = str(full_path.relative_to(PROJECT_ROOT))
        except ValueError:
            resolved_rel_path = str(full_path)

        if not few_shots:
            warnings.append(
                f"WARNING: No abbreviated exemplars found in {resolved_rel_path}. "
                f"Phase E Voice.md authoring may not be complete for {character_id}."
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
        "authority": "ADR-001 (Backend-authoritative voice)",
        "personas": configs,
    }
    json.dump(output, sys.stdout, indent=2, ensure_ascii=False)
    print()  # trailing newline


if __name__ == "__main__":
    main()
