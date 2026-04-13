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

_pair_cache: dict[str, PairMetadata] = {}


def get_pair_metadata(character_id: str) -> PairMetadata:
    """Load pair metadata for a character from pairs.yaml (cached)."""
    if character_id in _pair_cache:
        return _pair_cache[character_id]

    pair_key = _CHARACTER_TO_PAIR.get(character_id)
    if pair_key is None:
        msg = f"No pair mapping for character '{character_id}'"
        raise ValueError(msg)

    if not PAIRS_YAML.exists():
        msg = f"pairs.yaml not found at {PAIRS_YAML}"
        raise FileNotFoundError(msg)

    data = yaml.safe_load(PAIRS_YAML.read_text(encoding="utf-8"))
    pair_data = data.get("pairs", {}).get(pair_key)
    if pair_data is None:
        msg = f"Pair '{pair_key}' not found in pairs.yaml"
        raise ValueError(msg)

    metadata = PairMetadata(
        full_name=pair_data["full_name"],
        classification=pair_data["classification"],
        mechanism=pair_data["mechanism"],
        what_she_provides=pair_data["what_she_provides"],
        how_she_breaks_spiral=pair_data["how_she_breaks_spiral"],
        core_metaphor=pair_data["core_metaphor"],
        shared_functions=pair_data["shared_functions"],
        cadence=pair_data["cadence"],
    )
    _pair_cache[character_id] = metadata
    return metadata


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
    _pair_cache.clear()
