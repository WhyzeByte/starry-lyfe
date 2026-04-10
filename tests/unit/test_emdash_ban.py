"""Em-dash and en-dash ban for character-output surfaces.

Scans all YAML files in the canon directory for U+2014 and U+2013.
These characters must never appear in canon YAML (which seeds character output).
"""

from __future__ import annotations

from pathlib import Path

EM_DASH = "\u2014"
EN_DASH = "\u2013"


def test_emdash_ban_in_canon_yaml(canon_dir: Path) -> None:
    """No em-dashes or en-dashes in canon YAML files."""
    matches: list[tuple[str, int, str]] = []
    for filepath in sorted(canon_dir.glob("*.yaml")):
        text = filepath.read_text(encoding="utf-8")
        for line_num, line in enumerate(text.splitlines(), start=1):
            if EM_DASH in line or EN_DASH in line:
                matches.append((filepath.name, line_num, line.strip()))

    if matches:
        report = "\n".join(
            f"  {name}:{line_num}: {content}"
            for name, line_num, content in matches
        )
        msg = f"Em-dash/en-dash found in canon YAML:\n{report}"
        raise AssertionError(msg)
