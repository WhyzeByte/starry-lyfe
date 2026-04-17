"""Phase 10.6 closeout (2026-04-17): terminal 6-file authoring surface invariant.

Phase 10.5c shipped the terminal canonical state of **6 authoring files**
(5 rich per-character YAMLs at ``Characters/`` + 1 ``shared_canon.yaml``).
The 7 narrow YAMLs that previously sat at ``src/starry_lyfe/canon/`` are
archived. This test enforces the post-10.5c invariant so a regression
where someone reintroduces a narrow YAML or adds a stray YAML to
``Characters/`` fails CI immediately.

The Phase 0 verification script (``scripts/phase_0_verification.py``)
runs an equivalent check at hydration time; this pytest version puts
the gate inside the test suite so it cannot be skipped.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
NARROW_CANON_DIR = REPO_ROOT / "src" / "starry_lyfe" / "canon"
CHARACTERS_DIR = REPO_ROOT / "Characters"

# Phase 10.5c terminal-state authoring surface.
EXPECTED_AUTHORING_FILES = frozenset({
    "adelia_raye.yaml",
    "bina_malek.yaml",
    "reina_torres.yaml",
    "alicia_marin.yaml",
    "shawn_kroon.yaml",
    "shared_canon.yaml",
})


def test_no_narrow_yaml_in_src_canon() -> None:
    """Phase 10.5c §C3: src/starry_lyfe/canon/*.yaml must be empty.

    Catches accidental reintroduction of any of the 7 archived narrow
    YAMLs (characters, pairs, dyads, protocols, interlocks,
    voice_parameters, routines) — or any new narrow YAML that would
    bypass the rich YAML authoring surface.
    """
    stray = sorted(p.name for p in NARROW_CANON_DIR.glob("*.yaml"))
    assert not stray, (
        f"Phase 10.5c regression: narrow YAML files reappeared in "
        f"src/starry_lyfe/canon/: {stray}. The terminal authoring surface "
        f"is the 6 files in Characters/. Author there, not here."
    )


def test_characters_dir_has_exactly_terminal_six_yamls() -> None:
    """Phase 10.5c terminal state: Characters/ holds exactly 6 YAML authoring files.

    Catches both directions of drift: a missing canonical file (Pydantic
    load would fail loud, but this test reports the missing name first)
    AND a stray YAML that bypasses the canonical authoring surface.
    """
    actual = {p.name for p in CHARACTERS_DIR.glob("*.yaml")}
    missing = EXPECTED_AUTHORING_FILES - actual
    extra = actual - EXPECTED_AUTHORING_FILES
    assert not missing, (
        f"Terminal authoring surface incomplete — missing canonical YAML(s): "
        f"{sorted(missing)}. Expected exactly {sorted(EXPECTED_AUTHORING_FILES)}."
    )
    assert not extra, (
        f"Terminal authoring surface contaminated — unexpected YAML(s) in Characters/: "
        f"{sorted(extra)}. Author non-canonical YAMLs elsewhere "
        f"(scripts/, .claude/scripts/, or under Archive/)."
    )


def test_terminal_six_files_all_load_via_rich_loader() -> None:
    """End-to-end: the 6 authoring files all hydrate cleanly through rich_loader.

    This is the operational invariant — after Phase 10.5c rewire,
    `load_all_canon()` builds the entire narrow Canon from these 6
    files via rich_loader. If any of them fails to load or
    Pydantic-validate, the whole canonical surface is broken.
    """
    from starry_lyfe.canon.loader import load_all_canon
    from starry_lyfe.canon.rich_loader import (
        load_all_rich_characters,
        load_shared_canon,
    )

    rich_chars = load_all_rich_characters()
    assert set(rich_chars.keys()) == {"adelia", "bina", "reina", "alicia", "shawn"}, (
        f"load_all_rich_characters returned {sorted(rich_chars.keys())}; "
        f"expected 5 character ids (4 women + shawn)."
    )

    shared = load_shared_canon()
    assert shared.pairs is not None and len(shared.pairs) == 4
    assert shared.dyads_baseline is not None and len(shared.dyads_baseline) == 10
    assert shared.memory_tiers is not None and len(shared.memory_tiers) == 7
    assert shared.interlocks is not None and len(shared.interlocks) == 6

    # End-to-end: load_all_canon() must succeed against the 6 files alone.
    canon = load_all_canon(validate_on_load=True)
    assert len(canon.characters.characters) == 4
    assert len(canon.characters.operator) == 1
    assert len(canon.pairs.pairs) == 4
    assert len(canon.dyads.dyads) == 10
    assert len(canon.dyads.memory_tiers) == 7
    assert len(canon.protocols.protocols) >= 12  # Vision section 7 minimum
    assert len(canon.interlocks.interlocks) == 6
    assert len(canon.voice_parameters.voice_parameters) == 4
    assert len(canon.routines.routines) == 4
