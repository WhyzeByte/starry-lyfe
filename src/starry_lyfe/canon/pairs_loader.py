"""Pair metadata loader for runtime Layer 5 structured data.

Surfaces canonical pair fields from pairs.yaml as typed metadata
that rides in Layer 5 (Voice Directives) alongside voice guidance.
This is intentional redundancy with Layer 1 soul essence prose —
different register (structured data vs narrative) for scene-level
reasoning without modifying the soul essence content.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from .schemas.enums import CharacterNotFoundError, _assert_complete_character_keys

PAIRS_YAML = Path(__file__).resolve().parent / "pairs.yaml"


@dataclass(frozen=True)
class PairMetadata:
    """Typed pair metadata from pairs.yaml. All fields required."""

    full_name: str
    classification: str
    mechanism: str
    what_she_provides: str
    how_she_breaks_spiral: str
    core_metaphor: str
    shared_functions: str
    cadence: str


_CHARACTER_TO_PAIR: dict[str, str] = {
    "adelia": "entangled",
    "bina": "circuit",
    "reina": "kinetic",
    "alicia": "solstice",
}
_assert_complete_character_keys(_CHARACTER_TO_PAIR, "_CHARACTER_TO_PAIR")

_pair_cache: dict[str, PairMetadata] = {}
_yaml_loaded: bool = False


def _ensure_loaded() -> None:
    """Parse pairs.yaml once and populate the full character cache."""
    global _yaml_loaded  # noqa: PLW0603
    if _yaml_loaded:
        return

    if not PAIRS_YAML.exists():
        msg = f"pairs.yaml not found at {PAIRS_YAML}"
        raise FileNotFoundError(msg)

    data = yaml.safe_load(PAIRS_YAML.read_text(encoding="utf-8"))
    pairs = data.get("pairs", {})

    missing: list[str] = []
    for char_id, pair_key in _CHARACTER_TO_PAIR.items():
        pair_data = pairs.get(pair_key)
        if pair_data is None:
            missing.append(f"{char_id}->{pair_key}")
            continue
        _pair_cache[char_id] = PairMetadata(
            full_name=pair_data["full_name"],
            classification=pair_data["classification"],
            mechanism=pair_data["mechanism"],
            what_she_provides=pair_data["what_she_provides"],
            how_she_breaks_spiral=pair_data["how_she_breaks_spiral"],
            core_metaphor=pair_data["core_metaphor"],
            shared_functions=pair_data["shared_functions"],
            cadence=pair_data["cadence"],
        )

    if missing:
        # R-2.1 remediation: collect all missing entries and raise a single
        # error listing them, rather than deferring to per-access ValueError.
        expected_keys = sorted(set(_CHARACTER_TO_PAIR.values()))
        msg = (
            f"pairs.yaml is missing entries for: {missing}. "
            f"Expected pair_keys: {expected_keys}"
        )
        raise ValueError(msg)

    _yaml_loaded = True


def get_pair_metadata(character_id: str) -> PairMetadata:
    """Load pair metadata for a character from pairs.yaml (cached, single parse)."""
    _ensure_loaded()

    if character_id not in _pair_cache:
        msg = f"No pair metadata for character '{character_id}'"
        raise CharacterNotFoundError(msg)

    return _pair_cache[character_id]


def format_pair_metadata(character_id: str) -> str:
    """Format 6-field structured pair metadata block for Layer 5.

    Excludes shared_functions and cadence per Phase D Q1/Q2 decisions.
    """
    meta = get_pair_metadata(character_id)
    return (
        f"PAIR: {meta.full_name}\n"
        f"CLASSIFICATION: {meta.classification}\n"
        f"MECHANISM: {meta.mechanism}\n"
        f"CORE METAPHOR: {meta.core_metaphor}\n"
        f"WHAT SHE PROVIDES: {meta.what_she_provides}\n"
        f"HOW SHE BREAKS HIS SPIRAL: {meta.how_she_breaks_spiral}"
    )


def clear_pair_cache() -> None:
    """Clear the pair metadata cache (useful for testing)."""
    global _yaml_loaded  # noqa: PLW0603
    _pair_cache.clear()
    _yaml_loaded = False


# R-2.1: missing pair manifest entries must fail at module import rather than
# silently surviving until first runtime access.
_ensure_loaded()
