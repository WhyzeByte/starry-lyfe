"""v7.0 residue drift detection.

Scans all files under src/ for v7.0 legacy tokens from Handoff section 8.1.
Any match is a canonical drift failure.
"""

from __future__ import annotations

from pathlib import Path

# The 22 v7.0 residue tokens from Handoff section 8.1.
V70_RESIDUE_TOKENS: list[str] = [
    "Aliyeh",
    "Bahadori",
    "Laia",
    "Benítez",
    "Hellín",
    "Castilla-La Mancha",
    "Atlético",
    "MAEUEC",
    "Kingdom of Spain",
    "Spanish consular",
    "Subdirección",
    "Portuguese-Australian",
    "Golden Pair",
    "Citadel Pair",
    "Synergistic Pair",
    "Elemental Pair",
    "Adélia",
    "Marín",
    "sheismo",
    "_v7.0.md",
    "_Golden_Pair.md",
    "_Citadel_Pair.md",
    "_Synergistic_Pair.md",
    "_Elemental_Pair.md",
]

# Allowed exceptions per Handoff section 8.1.
ALLOWED_PATTERNS: list[tuple[str, str]] = [
    # Shawn's operator profile is deliberately v7.0 (Handoff section 3).
    ("_v7.0.md", "Shawn_Kroon_v7.0.md"),
    # Mercè Benítez is Reina's mother's maiden name, not Reina's own surname (Handoff §8.1 line 499).
    ("Benítez", "Mercè Benítez"),
]


def _is_allowed(token: str, line: str) -> bool:
    """Check if a token match is in the allowed exceptions list."""
    for allowed_token, allowed_context in ALLOWED_PATTERNS:
        if token == allowed_token and allowed_context in line:
            return True
    return False


def _scan_src_for_residue(src_dir: Path) -> list[tuple[str, int, str, str]]:
    """Scan all files under src/ for v7.0 residue tokens.

    Returns list of (file_path, line_number, token, line_content) tuples.
    """
    matches: list[tuple[str, int, str, str]] = []
    for filepath in sorted(src_dir.rglob("*")):
        if not filepath.is_file():
            continue
        try:
            text = filepath.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        for line_num, line in enumerate(text.splitlines(), start=1):
            for token in V70_RESIDUE_TOKENS:
                if token in line and not _is_allowed(token, line):
                    rel_path = str(filepath.relative_to(src_dir))
                    matches.append((rel_path, line_num, token, line.strip()))
    return matches


def test_v70_residue_grep_returns_zero_matches(src_dir: Path) -> None:
    """No v7.0 drift tokens in src/."""
    matches = _scan_src_for_residue(src_dir)
    if matches:
        report = "\n".join(
            f"  {path}:{line_num} [{token}]: {content}"
            for path, line_num, token, content in matches
        )
        msg = f"v7.0 residue found in src/:\n{report}"
        raise AssertionError(msg)
