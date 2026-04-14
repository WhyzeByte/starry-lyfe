"""Character routines loader for Phase 6 Dreams content generation.

Dreams reads routines.yaml at generation time to seed tomorrow's schedule
and to anchor off-screen event generation so the LLM does not hallucinate
arbitrary activities.

Follows the pairs_loader.py pattern: single parse at module import,
fail-loud on missing character coverage or schema violations.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from .schemas.enums import CharacterNotFoundError, _assert_complete_character_keys
from .schemas.routines import CanonRoutines, CharacterRoutines

ROUTINES_YAML = Path(__file__).resolve().parent / "routines.yaml"

_routines_cache: dict[str, CharacterRoutines] = {}
_canon_routines: CanonRoutines | None = None
_yaml_loaded: bool = False


def _ensure_loaded() -> None:
    """Parse routines.yaml once and populate the per-character cache."""
    global _yaml_loaded, _canon_routines  # noqa: PLW0603
    if _yaml_loaded:
        return

    if not ROUTINES_YAML.exists():
        msg = f"routines.yaml not found at {ROUTINES_YAML}"
        raise FileNotFoundError(msg)

    data = yaml.safe_load(ROUTINES_YAML.read_text(encoding="utf-8"))
    _canon_routines = CanonRoutines.model_validate(data)

    for char_id, stanza in _canon_routines.routines.items():
        _routines_cache[char_id.value] = stanza

    # R-3.2 pattern: validate complete character coverage at load time.
    _assert_complete_character_keys(_routines_cache, "routines.yaml")

    _yaml_loaded = True


def get_routines(character_id: str) -> CharacterRoutines:
    """Return the routine stanza for a character. Fails loud if missing."""
    _ensure_loaded()

    if character_id not in _routines_cache:
        msg = f"No routine stanza for character '{character_id}'"
        raise CharacterNotFoundError(msg)

    return _routines_cache[character_id]


def get_alicia_communication_distribution() -> dict[str, float]:
    """Return Alicia's away-mode communication_mode sampling distribution.

    Used by Dreams generators when Alicia.is_away=True to pick
    phone/letter/video_call per emitted artifact (Phase A'' retroactive).
    """
    _ensure_loaded()
    assert _canon_routines is not None  # populated by _ensure_loaded
    dist = _canon_routines.alicia_communication_distribution
    return {
        "phone": dist.phone,
        "letter": dist.letter,
        "video_call": dist.video_call,
    }


def clear_routines_cache() -> None:
    """Clear the routines cache (useful for testing)."""
    global _yaml_loaded, _canon_routines  # noqa: PLW0603
    _routines_cache.clear()
    _canon_routines = None
    _yaml_loaded = False


# Eager load at import time so schema / coverage errors surface immediately
# rather than on first Dreams invocation (matches pairs_loader pattern).
_ensure_loaded()
