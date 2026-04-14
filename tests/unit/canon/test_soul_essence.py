"""Tests for soul essence formatting and validation (R-1.1 remediation).

Spec: Docs/REMEDIATION_2026-04-13.md §1.R-1.1.
Canonical location per spec acceptance criteria.
"""

from __future__ import annotations

import pytest

from starry_lyfe.canon.soul_essence import (
    SOUL_ESSENCES,
    SoulEssenceNotFoundError,
    format_soul_essence,
    get_soul_essence,
    soul_essence_token_estimate,
)


class TestFormatSoulEssence:
    """format_soul_essence must fail loud on unknown characters."""

    def test_soul_essence_raises_on_missing_character(self) -> None:
        """R-1.1 AC: unknown character must raise SoulEssenceNotFoundError."""
        with pytest.raises(SoulEssenceNotFoundError):
            format_soul_essence("shawn")

    def test_soul_essence_error_message_lists_registered_characters(self) -> None:
        """R-1.1 AC: error message includes character_id and sorted registered list."""
        with pytest.raises(SoulEssenceNotFoundError) as excinfo:
            format_soul_essence("ghost")

        message = str(excinfo.value)
        assert "ghost" in message
        # Sorted registered list in the message
        assert "adelia" in message
        assert "alicia" in message
        assert "bina" in message
        assert "reina" in message
        # Verify sorted order is alphabetical
        adelia_pos = message.index("adelia")
        alicia_pos = message.index("alicia")
        bina_pos = message.index("bina")
        reina_pos = message.index("reina")
        assert adelia_pos < alicia_pos < bina_pos < reina_pos

    def test_soul_essence_raises_for_empty_string(self) -> None:
        with pytest.raises(SoulEssenceNotFoundError):
            format_soul_essence("")

    def test_soul_essence_not_found_error_is_value_error(self) -> None:
        """SoulEssenceNotFoundError subclasses ValueError for backward compat."""
        assert issubclass(SoulEssenceNotFoundError, ValueError)

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

    def test_propagates_error_for_unknown(self) -> None:
        """Token estimate must not swallow SoulEssenceNotFoundError from format_soul_essence."""
        with pytest.raises(SoulEssenceNotFoundError):
            soul_essence_token_estimate("shawn")
