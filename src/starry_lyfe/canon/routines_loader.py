"""Character routines loader for Phase 6 Dreams content generation.

Phase 10.5c rewire (2026-04-16): sources from rich character YAMLs
(``Characters/{name}.yaml::runtime.routines``) instead of the legacy
``routines.yaml`` file. Public API (``get_routines`` and
``get_alicia_communication_distribution``) is preserved so callers
in ``dreams/runner.py`` and ``dreams/alicia_mode.py`` stay green
without modification.

Cache semantics preserved: single hydration on first access,
``clear_routines_cache()`` resets state for tests.
"""

from __future__ import annotations

from .rich_loader import load_all_rich_characters
from .schemas.enums import CharacterNotFoundError, _assert_complete_character_keys
from .schemas.routines import (
    AliciaCommunicationDistribution,
    CharacterRoutines,
)

_routines_cache: dict[str, CharacterRoutines] = {}
_alicia_distribution: AliciaCommunicationDistribution | None = None
_loaded: bool = False


def _ensure_loaded() -> None:
    """Hydrate from rich character YAMLs once and populate the per-character cache."""
    global _loaded, _alicia_distribution  # noqa: PLW0603
    if _loaded:
        return

    rich_chars = load_all_rich_characters()

    for char_id in ("adelia", "bina", "reina", "alicia"):
        rc = rich_chars[char_id]
        if rc.runtime is None or rc.runtime.routines is None:
            msg = f"runtime.routines missing in rich YAML for {char_id}"
            raise FileNotFoundError(msg)
        rt = rc.runtime.routines
        _routines_cache[char_id] = CharacterRoutines.model_validate({
            "character": char_id,
            "weekday": [b.model_dump() for b in rt.weekday],
            "weekend": [b.model_dump() for b in rt.weekend],
            "recurring_events": (
                [re.model_dump() for re in rt.recurring_events]
                if rt.recurring_events else []
            ),
        })

    alicia_runtime = rich_chars["alicia"].runtime
    if alicia_runtime is None or alicia_runtime.alicia_communication_distribution is None:
        msg = "runtime.alicia_communication_distribution missing in alicia rich YAML"
        raise FileNotFoundError(msg)
    acd = alicia_runtime.alicia_communication_distribution
    _alicia_distribution = AliciaCommunicationDistribution(
        phone=acd.phone, letter=acd.letter, video_call=acd.video_call,
    )

    # R-3.2 pattern: validate complete character coverage at load time.
    _assert_complete_character_keys(_routines_cache, "rich runtime.routines coverage")
    _loaded = True


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
    assert _alicia_distribution is not None  # populated by _ensure_loaded
    return {
        "phone": _alicia_distribution.phone,
        "letter": _alicia_distribution.letter,
        "video_call": _alicia_distribution.video_call,
    }


def clear_routines_cache() -> None:
    """Clear the routines cache (useful for testing)."""
    global _loaded, _alicia_distribution  # noqa: PLW0603
    _routines_cache.clear()
    _alicia_distribution = None
    _loaded = False


# Eager load at import time so schema / coverage errors surface immediately
# rather than on first Dreams invocation (matches legacy pairs_loader pattern).
_ensure_loaded()
