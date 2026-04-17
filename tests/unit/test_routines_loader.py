"""Unit tests for routines.yaml loader (Phase 6 canon layer)."""

from __future__ import annotations

import pytest

from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.canon.routines_loader import (
    clear_routines_cache,
    get_alicia_communication_distribution,
    get_routines,
)
from starry_lyfe.canon.schemas.enums import CharacterNotFoundError


class TestRoutinesYaml:
    def test_routines_yaml_loads_without_error(self) -> None:
        canon = load_all_canon().routines
        assert canon.version == "7.1"
        assert len(canon.routines) == 4

    def test_all_four_characters_have_stanzas(self) -> None:
        canon = load_all_canon().routines
        keys = {k.value for k in canon.routines}
        assert keys == {"adelia", "bina", "reina", "alicia"}

    def test_each_character_has_weekday_and_weekend_blocks(self) -> None:
        canon = load_all_canon().routines
        for char_id, stanza in canon.routines.items():
            assert len(stanza.weekday) >= 1, f"{char_id} missing weekday blocks"
            assert len(stanza.weekend) >= 1, f"{char_id} missing weekend blocks"

    def test_alicia_communication_distribution_present(self) -> None:
        canon = load_all_canon().routines
        dist = canon.alicia_communication_distribution
        total = dist.phone + dist.letter + dist.video_call
        # Approximately 1.0 (not strictly enforced per schema).
        assert 0.9 <= total <= 1.1


class TestRoutinesRuntimeAPI:
    def test_get_routines_returns_expected_shape(self) -> None:
        clear_routines_cache()
        adelia = get_routines("adelia")
        assert adelia.character.value == "adelia"
        assert any("Ozone & Ember" in block.activity for block in adelia.weekday)

    def test_get_routines_raises_on_unknown_character(self) -> None:
        with pytest.raises(CharacterNotFoundError):
            get_routines("not_a_character")

    def test_get_alicia_communication_distribution_returns_dict(self) -> None:
        dist = get_alicia_communication_distribution()
        assert set(dist.keys()) == {"phone", "letter", "video_call"}
        assert all(0.0 <= v <= 1.0 for v in dist.values())


class TestCanonIntegration:
    def test_load_all_canon_includes_routines(self) -> None:
        canon = load_all_canon()
        assert canon.routines is not None
        assert len(canon.routines.routines) == 4

    def test_routines_stanza_key_matches_character_field(self) -> None:
        """The schema validator enforces this — regress against stanza/key mismatch."""
        canon = load_all_canon().routines
        for char_id, stanza in canon.routines.items():
            assert stanza.character == char_id
