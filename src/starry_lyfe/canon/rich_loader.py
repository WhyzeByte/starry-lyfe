"""Load and validate rich per-character YAMLs + shared_canon.yaml (Phase 10.1).

Runs alongside the existing narrow-canon loaders (``loader.py``) — zero
runtime integration in Phase 10.1. Cutovers happen in 10.2–10.4.

Provides:
- ``load_rich_character(character_id)`` → ``RichCharacter``
- ``load_all_rich_characters()`` → ``dict[str, RichCharacter]``
- ``load_shared_canon()`` → ``SharedCanon``
- ``validate_rich_cross_references(chars, shared)`` → error list
- ``get_preserve_markers(rc)`` → flat list of ``PreserveMarker``

Authority: ``Docs/_phases/PHASE_10.md`` §Phase 10.1 WI3–WI4.
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from .rich_schema import PreserveMarker, PreserveMarkersBlock, RichCharacter
from .shared_schema import SharedCanon

logger = logging.getLogger(__name__)

CHARACTERS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "Characters"

RICH_YAML_FILES: dict[str, str] = {
    "adelia": "adelia_raye.yaml",
    "bina": "bina_malek.yaml",
    "reina": "reina_torres.yaml",
    "alicia": "alicia_marin.yaml",
    "shawn": "shawn_kroon.yaml",
}


def _load_yaml_file(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as f:
        data: dict[str, object] = yaml.safe_load(f)
    return data


def load_rich_character(character_id: str) -> RichCharacter:
    """Load and Pydantic-validate a single rich character YAML."""
    filename = RICH_YAML_FILES.get(character_id)
    if filename is None:
        msg = f"Unknown character_id: {character_id!r}. Valid: {sorted(RICH_YAML_FILES)}"
        raise ValueError(msg)
    path = CHARACTERS_DIR / filename
    data = _load_yaml_file(path)
    return RichCharacter.model_validate(data)


def load_all_rich_characters() -> dict[str, RichCharacter]:
    """Load and validate all 5 rich character YAMLs."""
    return {cid: load_rich_character(cid) for cid in RICH_YAML_FILES}


def load_shared_canon() -> SharedCanon:
    """Load and Pydantic-validate ``Characters/shared_canon.yaml``."""
    path = CHARACTERS_DIR / "shared_canon.yaml"
    data = _load_yaml_file(path)
    return SharedCanon.model_validate(data)


def get_preserve_markers(rc: RichCharacter) -> list[PreserveMarker]:
    """Extract a flat list of preserve markers from any character YAML shape."""
    pm = rc.meta.preserve_markers
    if pm is None:
        return []
    if isinstance(pm, list):
        return pm
    if isinstance(pm, PreserveMarkersBlock):
        return pm.canonical_anchors or []
    return []


def verify_preserve_markers(
    rc: RichCharacter,
    *,
    full_text: str,
) -> list[str]:
    """Check that each preserve_marker content_anchor appears in the body text.

    Returns a list of error strings (empty = all pass). The ``full_text``
    should be the raw YAML file text with the preserve_markers block
    excluded (so anchors aren't found inside their own definition).
    """
    errors: list[str] = []
    for marker in get_preserve_markers(rc):
        anchor = marker.content_anchor
        clean = anchor.rstrip(".")
        if clean.endswith("..."):
            clean = clean[:-3].rstrip()
        if clean not in full_text:
            errors.append(
                f"preserve_marker {marker.id!r}: content_anchor not found in body text"
            )
    return errors


def _get_inter_woman_dyad_keys(rc: RichCharacter) -> set[str]:
    """Return the set of other-character IDs this character has dyad blocks for."""
    fad = rc.family_and_other_dyads
    if fad is None:
        return set()
    return {k.removeprefix("with_") for k in fad if k.startswith("with_")}


def validate_rich_cross_references(
    chars: dict[str, RichCharacter],
    shared: SharedCanon,
) -> list[str]:
    """Cross-reference validator for the per-POV model (Phase 10.1 WI4).

    Checks:
    1. Perspective symmetry: every ``family_and_other_dyads.with_{X}``
       block in character A must have a matching ``with_{A}`` in X.
    2. Pair POV: every woman with ``pair_architecture`` must have a
       matching pair entry in ``shared_canon.yaml.pairs``.

    Returns a list of error strings (empty = all pass).
    """
    errors: list[str] = []
    women = {cid: rc for cid, rc in chars.items() if cid != "shawn"}

    for cid_a, rc_a in women.items():
        dyad_keys_a = _get_inter_woman_dyad_keys(rc_a)
        for other_id in dyad_keys_a:
            if other_id not in women:
                continue
            rc_b = women[other_id]
            dyad_keys_b = _get_inter_woman_dyad_keys(rc_b)
            if cid_a not in dyad_keys_b:
                errors.append(
                    f"Perspective asymmetry: {cid_a} has with_{other_id} "
                    f"but {other_id} has no with_{cid_a}"
                )

    shared_pair_names = {p.canonical_name for p in (shared.pairs or [])}
    for cid, rc in women.items():
        pa = rc.pair_architecture
        if pa is None:
            continue
        pair_name = pa.get("name") if isinstance(pa, dict) else None
        if pair_name and pair_name not in shared_pair_names:
            errors.append(
                f"{cid}: pair_architecture.name {pair_name!r} "
                f"not found in shared_canon.yaml pairs"
            )

    return errors
