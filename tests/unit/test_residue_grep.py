"""v7.0 residue drift detection.

Scans all files under src/ for v7.0 legacy tokens from Handoff section 8.1.
Any match is a canonical drift failure.
"""

from __future__ import annotations

import tempfile
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
    # "Benítez household" also refers to Mercè's family of origin, not to Reina's surname.
    ("Benítez", "Mercè Benítez"),
    ("Benítez", "Benítez household"),
    # sheismo is a real phonological feature of Rioplatense Spanish (Alicia's canon).
    # It was on the drift token list when Alicia was Spanish; in the Argentine reframe
    # it is a legitimate canonical term describing her speech patterns.
    ("sheismo", "Rioplatense"),
    ("sheismo", "voseo"),
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


EXTENDED_TOKENS: list[str] = V70_RESIDUE_TOKENS + [
    "non-resident",
    "twice yearly between operations",
    "based in Madrid",
]

EXCLUDED_PATHS: set[str] = {
    "Characters/Shawn",
    "Characters/shawn_kroon.yaml",
    "Vision/Adelia Raye.md",
    "Vision/Alicia Marin.md",
    "Vision/Bina Malek.md",
    "Vision/Reina Torres.md",
}

VISION_APPENDIX_FILE = "Vision/Starry-Lyfe_Vision_v7.1.md"
VISION_APPENDIX_START_LINE = 175


def _is_excluded_path(filepath: Path, project_root: Path) -> bool:
    """Check if a file is in the excluded paths set."""
    rel = str(filepath.relative_to(project_root)).replace("\\", "/")
    return any(rel == excluded or rel.startswith(excluded + "/") for excluded in EXCLUDED_PATHS)


def _is_vision_appendix(filepath: Path, project_root: Path, line_num: int) -> bool:
    """Check if a line is in the Vision v7.1 Appendix A section."""
    rel = str(filepath.relative_to(project_root)).replace("\\", "/")
    return rel == VISION_APPENDIX_FILE and line_num >= VISION_APPENDIX_START_LINE


def _get_normalization_notes_lines(lines: list[str]) -> set[int]:
    """Return set of 0-based line indices inside normalization_notes: YAML blocks.

    normalization_notes blocks document RESOLVED legacy drift artifacts.
    Their content references v7.0 tokens by design (audit trail of what was
    fixed), so these lines must be excluded from the residue scan.

    Phase 9 QA-1 closure + CLAUDE.md §16 highest-quality-default directive.
    """
    excluded: set[int] = set()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        if stripped.startswith("normalization_notes:"):
            block_indent = len(line) - len(stripped)
            excluded.add(i)
            i += 1
            while i < len(lines):
                if not lines[i].strip():
                    excluded.add(i)
                    i += 1
                    continue
                current_indent = len(lines[i]) - len(lines[i].lstrip())
                if current_indent <= block_indent:
                    break
                excluded.add(i)
                i += 1
        else:
            i += 1
    return excluded


def _scan_repo_for_residue(
    project_root: Path,
    directories: list[str],
) -> list[tuple[str, int, str, str]]:
    """Scan multiple directories for v7.0 residue tokens with exclusions."""
    matches: list[tuple[str, int, str, str]] = []
    for dir_name in directories:
        scan_dir = project_root / dir_name
        if not scan_dir.exists():
            continue
        for filepath in sorted(scan_dir.rglob("*")):
            if not filepath.is_file():
                continue
            if _is_excluded_path(filepath, project_root):
                continue
            try:
                text = filepath.read_text(encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                continue
            all_lines = text.splitlines()
            is_yaml = filepath.suffix in (".yaml", ".yml")
            norm_lines = _get_normalization_notes_lines(all_lines) if is_yaml else set()
            for line_num, line in enumerate(all_lines, start=1):
                if _is_vision_appendix(filepath, project_root, line_num):
                    continue
                if is_yaml and (line_num - 1) in norm_lines:
                    continue
                for token in EXTENDED_TOKENS:
                    if token in line and not _is_allowed(token, line):
                        rel_path = str(filepath.relative_to(project_root))
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


def test_v70_residue_repo_wide() -> None:
    """INH-3: No v7.0 drift tokens across src/ + Characters/ + Vision/.

    This test closes the Phase 0 F1 automation gap by scanning the full
    Phase 0 AC1 scope (not just src/) with the canonical exclusion list
    from Claude_Code_Handoff_v7.1.md §8.1.
    """
    project_root = Path(__file__).resolve().parent.parent.parent
    matches = _scan_repo_for_residue(
        project_root,
        ["src", "Characters", "Vision"],
    )
    if matches:
        report = "\n".join(
            f"  {path}:{line_num} [{token}]: {content[:100]}"
            for path, line_num, token, content in matches
        )
        msg = f"v7.0 residue found in repo-wide scan:\n{report}"
        raise AssertionError(msg)


def test_normalization_notes_token_excluded() -> None:
    """v7.0 tokens inside normalization_notes: blocks are excluded.

    normalization_notes document RESOLVED drift — referencing the legacy
    token is the audit trail, not the drift itself. Phase 9 QA-1 closure.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        yaml_dir = tmp_path / "Characters"
        yaml_dir.mkdir()
        (yaml_dir / "test_char.yaml").write_text(
            "identity:\n"
            "  name: Test\n"
            "normalization_notes:\n"
            "  - id: legacy_name_fix\n"
            '    issue: "Aliyeh was the v7.0 name for Bina"\n'
            '    resolved_value: "Bina Malek"\n'
            "work_and_world:\n"
            "  employer: Ozone\n",
            encoding="utf-8",
        )
        matches = _scan_repo_for_residue(tmp_path, ["Characters"])
        tokens_found = {m[2] for m in matches}
        assert "Aliyeh" not in tokens_found, (
            "Aliyeh inside normalization_notes should be excluded"
        )


def test_token_outside_normalization_notes_still_fails() -> None:
    """v7.0 tokens OUTSIDE normalization_notes: blocks still fail."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        yaml_dir = tmp_path / "Characters"
        yaml_dir.mkdir()
        (yaml_dir / "test_char.yaml").write_text(
            "identity:\n"
            '  old_name: "Aliyeh Bahadori"\n'
            "normalization_notes:\n"
            '  - note: "this is fine"\n',
            encoding="utf-8",
        )
        matches = _scan_repo_for_residue(tmp_path, ["Characters"])
        tokens_found = {m[2] for m in matches}
        assert "Aliyeh" in tokens_found, (
            "Aliyeh outside normalization_notes must still be caught"
        )


def test_normalization_exclusion_does_not_mask_other_blocks() -> None:
    """Exclusion is scoped to normalization_notes only, not adjacent blocks."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        yaml_dir = tmp_path / "Characters"
        yaml_dir.mkdir()
        (yaml_dir / "test_char.yaml").write_text(
            "normalization_notes:\n"
            '  - issue: "Golden Pair was renamed"\n'
            "pair_architecture:\n"
            '  old_label: "Golden Pair"\n',
            encoding="utf-8",
        )
        matches = _scan_repo_for_residue(tmp_path, ["Characters"])
        tokens_found = {m[2] for m in matches}
        assert "Golden Pair" in tokens_found, (
            "Golden Pair in pair_architecture (not normalization_notes) must fail"
        )
