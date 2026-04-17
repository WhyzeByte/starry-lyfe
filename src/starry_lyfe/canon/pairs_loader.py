"""Pair metadata loader for runtime Layer 5 structured data.

Phase 10.5c rewire (2026-04-16): sources from ``Characters/shared_canon.yaml``
``pairs[]`` (the single authoritative source per §2.5 of
PHASE_10_5c_MAPPING.md) instead of the legacy ``pairs.yaml`` file.
Public API (``PairMetadata`` dataclass, ``get_pair_metadata``,
``format_pair_metadata``) is preserved so callers in tests + Layer 5
prompt assembly stay green without modification.

Cache semantics preserved: single hydration on first access,
``clear_pair_cache()`` resets state for tests.
"""

from __future__ import annotations

from dataclasses import dataclass

from .rich_loader import load_shared_canon
from .schemas.enums import CharacterNotFoundError, _assert_complete_character_keys


@dataclass(frozen=True)
class PairMetadata:
    """Typed pair metadata sourced from shared_canon.pairs[]. All fields required."""

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

_PAIR_NAME_TO_KEY: dict[str, str] = {
    "The Entangled Pair": "entangled",
    "The Circuit Pair": "circuit",
    "The Kinetic Pair": "kinetic",
    "The Solstice Pair": "solstice",
}

_pair_cache: dict[str, PairMetadata] = {}
_loaded: bool = False


def _ensure_loaded() -> None:
    """Hydrate from shared_canon.pairs[] once and populate the per-character cache."""
    global _loaded  # noqa: PLW0603
    if _loaded:
        return

    shared = load_shared_canon()
    if shared.pairs is None:
        msg = "shared_canon.pairs is missing — required for pair metadata hydration"
        raise FileNotFoundError(msg)

    by_pair_key: dict[str, PairMetadata] = {}
    for sp in shared.pairs:
        pair_key = _PAIR_NAME_TO_KEY.get(sp.canonical_name)
        if pair_key is None:
            msg = f"Unknown shared_canon pair canonical_name: {sp.canonical_name!r}"
            raise ValueError(msg)
        by_pair_key[pair_key] = PairMetadata(
            full_name=sp.canonical_name,
            classification=sp.classification or "",
            mechanism=sp.mechanism or "",
            what_she_provides=sp.what_she_provides or "",
            how_she_breaks_spiral=sp.how_she_breaks_spiral or "",
            core_metaphor=sp.core_metaphor or "",
            shared_functions=sp.shared_functions or "",
            cadence=sp.cadence or "continuous",
        )

    missing: list[str] = []
    for char_id, pair_key in _CHARACTER_TO_PAIR.items():
        if pair_key not in by_pair_key:
            missing.append(f"{char_id}->{pair_key}")
            continue
        _pair_cache[char_id] = by_pair_key[pair_key]

    if missing:
        # R-2.1 remediation: collect all missing entries and raise a single
        # error listing them, rather than deferring to per-access ValueError.
        expected_keys = sorted(set(_CHARACTER_TO_PAIR.values()))
        msg = (
            f"shared_canon.pairs is missing entries for: {missing}. "
            f"Expected pair_keys: {expected_keys}"
        )
        raise ValueError(msg)

    _loaded = True


def get_pair_metadata(character_id: str) -> PairMetadata:
    """Load pair metadata for a character (cached, single hydration)."""
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
    global _loaded  # noqa: PLW0603
    _pair_cache.clear()
    _loaded = False


# R-2.1: missing pair manifest entries must fail at module import rather than
# silently surviving until first runtime access.
_ensure_loaded()
