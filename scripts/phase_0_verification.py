"""Phase 0 pre-flight verification — rewritten for Phase 10.6 spec §8.

Consumes ``normalization_notes`` blocks directly from rich YAMLs and
verifies the resolved authoring against actual rich YAML content.
Replaces the legacy markdown drift grep with a YAML drift gate that
runs against the terminal 6-file authoring surface (5 rich
per-character YAMLs + ``Characters/shared_canon.yaml``).

Run as a Phase 0 hydration gate before any code change:

    python scripts/phase_0_verification.py

Exits 0 on clean canon; exits 1 with a structured drift report on any
failure. Designed to be fast (no LLM calls, no DB hits) so the operator
can run it as a habitual pre-work check.

Per ``Docs/_phases/PHASE_10.md`` §Phase 10.6 spec §8 + §9 + Phase 10.6
closeout audit (2026-04-17).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure src/ is importable when run from repo root.
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from starry_lyfe.canon.rich_loader import (  # noqa: E402
    get_preserve_markers,
    load_all_rich_characters,
    load_shared_canon,
    verify_preserve_markers,
)


def _yaml_body_text(rc_yaml_path: Path) -> str:
    """Return the full YAML file text — the `full_text` surface for preserve_markers."""
    return rc_yaml_path.read_text(encoding="utf-8")


def _check_normalization_notes(rich_chars: dict[str, object]) -> list[str]:
    """Phase 10.6 §9: every per-character YAML must carry a normalization_notes block.

    Returns the list of character_ids missing the block (empty = clean).
    """
    missing: list[str] = []
    for char_id, rc in rich_chars.items():
        notes = getattr(rc, "normalization_notes", None)
        if not notes:
            missing.append(char_id)
    return missing


def _check_preserve_markers(rich_chars: dict[str, object]) -> dict[str, list[str]]:
    """Phase 10.6 §1: every preserve_marker.content_anchor must appear verbatim in YAML body.

    Returns dict of character_id → list of missing-anchor error messages
    (empty dict = clean).
    """
    char_dir = REPO_ROOT / "Characters"
    yaml_paths = {
        "adelia": char_dir / "adelia_raye.yaml",
        "bina": char_dir / "bina_malek.yaml",
        "reina": char_dir / "reina_torres.yaml",
        "alicia": char_dir / "alicia_marin.yaml",
        "shawn": char_dir / "shawn_kroon.yaml",
    }
    issues: dict[str, list[str]] = {}
    for char_id, rc in rich_chars.items():
        anchors = get_preserve_markers(rc)
        if not anchors:
            continue
        path = yaml_paths.get(char_id)
        if path is None or not path.exists():
            issues[char_id] = [f"YAML path missing for {char_id}"]
            continue
        full_text = _yaml_body_text(path)
        errors = verify_preserve_markers(rc, full_text=full_text)
        if errors:
            issues[char_id] = errors
    return issues


def _check_terminal_authoring_surface() -> list[str]:
    """Phase 10.5c: src/starry_lyfe/canon/*.yaml must be empty (no narrow-YAML reintroduction)."""
    canon_dir = REPO_ROOT / "src" / "starry_lyfe" / "canon"
    stray = sorted(canon_dir.glob("*.yaml"))
    return [str(p.relative_to(REPO_ROOT)) for p in stray]


def _check_shared_canon_blocks() -> list[str]:
    """Phase 10.5c: shared_canon.yaml must carry the 4 cross-character taxonomies expected by load_all_canon."""
    shared = load_shared_canon()
    missing: list[str] = []
    if not shared.pairs:
        missing.append("shared_canon.pairs (required by _build_pairs)")
    if not shared.dyads_baseline:
        missing.append("shared_canon.dyads_baseline (required by _build_dyads)")
    if not shared.memory_tiers:
        missing.append("shared_canon.memory_tiers (required by _build_dyads)")
    if not shared.interlocks:
        missing.append("shared_canon.interlocks (required by _build_interlocks)")
    return missing


def main() -> int:
    """Run all Phase 0 pre-flight checks. Return 0 clean / 1 drift."""
    rich_chars = load_all_rich_characters()
    drift: list[str] = []

    # §1 — preserve_marker enforcement against YAML body
    pm_issues = _check_preserve_markers(rich_chars)
    if pm_issues:
        drift.append("preserve_marker drift:")
        for char_id, errors in pm_issues.items():
            drift.append(f"  {char_id}:")
            drift.extend(f"    - {e}" for e in errors)

    # §9 — normalization_notes ledger across per-character YAMLs
    missing_notes = _check_normalization_notes(rich_chars)
    if missing_notes:
        drift.append(
            f"normalization_notes missing in: {missing_notes} "
            f"(Phase 10.6 §9 requires the ledger across all per-character YAMLs)"
        )

    # Phase 10.5c terminal authoring surface
    stray_narrow = _check_terminal_authoring_surface()
    if stray_narrow:
        drift.append(
            "narrow YAML reintroduction detected (Phase 10.5c terminal-6-file invariant violated):"
        )
        drift.extend(f"  - {p}" for p in stray_narrow)

    # Phase 10.5c shared_canon completeness for load_all_canon hydration
    missing_blocks = _check_shared_canon_blocks()
    if missing_blocks:
        drift.append("shared_canon.yaml missing required blocks:")
        drift.extend(f"  - {b}" for b in missing_blocks)

    if drift:
        sys.stderr.write("\nPhase 0 verification FAILED:\n")
        for line in drift:
            sys.stderr.write(f"  {line}\n")
        return 1

    sys.stdout.write(
        "Phase 0 verification PASSED — terminal 6-file authoring surface clean, "
        "preserve_markers verified, normalization_notes ledger complete, "
        "shared_canon hydration blocks present.\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
