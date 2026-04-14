"""Tests for soul essence formatting and validation."""

from __future__ import annotations

import pytest

from starry_lyfe.canon.soul_essence import (
    SOUL_ESSENCES,
    format_soul_essence,
    get_soul_essence,
    soul_essence_token_estimate,
)


class TestFormatSoulEssence:
    """format_soul_essence must fail loud on unknown characters."""

    def test_raises_for_unknown_character(self) -> None:
        """C1 remediation: unknown character must raise, not return empty string."""
        with pytest.raises(ValueError, match="No soul essence registered"):
            format_soul_essence("shawn")

    def test_raises_for_empty_string(self) -> None:
        with pytest.raises(ValueError, match="No soul essence registered"):
            format_soul_essence("")

    def test_returns_nonempty_for_all_registered_characters(self) -> None:
        for character_id in SOUL_ESSENCES:
            text = format_soul_essence(character_id)
            assert text.strip(), f"Soul essence for {character_id} rendered empty"
            assert "## Core Identity (soul substrate)" in text

    def test_case_insensitive_lookup(self) -> None:
        # get_soul_essence lowercases the input
        assert get_soul_essence("ADELIA") is not None
        assert get_soul_essence("Adelia") is not None


class TestSoulEssenceTokenEstimate:
    def test_returns_positive_for_registered_characters(self) -> None:
        for character_id in SOUL_ESSENCES:
            tokens = soul_essence_token_estimate(character_id)
            assert tokens > 0, f"Token estimate for {character_id} was {tokens}"

    def test_propagates_value_error_for_unknown(self) -> None:
        """Token estimate must not swallow the ValueError from format_soul_essence."""
        with pytest.raises(ValueError, match="No soul essence registered"):
            soul_essence_token_estimate("shawn")
