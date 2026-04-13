"""Phase D tests for pair metadata loading and Layer 5 integration."""

from __future__ import annotations

from starry_lyfe.canon.pairs_loader import (
    PairMetadata,
    clear_pair_cache,
    format_pair_metadata,
    get_pair_metadata,
)
from starry_lyfe.context.budgets import DEFAULT_BUDGETS


class TestPairsLoader:
    """WI1: pairs_loader parses pairs.yaml correctly."""

    def test_loads_all_four_characters(self) -> None:
        clear_pair_cache()
        for char_id in ["adelia", "bina", "reina", "alicia"]:
            meta = get_pair_metadata(char_id)
            assert isinstance(meta, PairMetadata)
            assert meta.full_name != ""

    def test_pair_metadata_is_frozen(self) -> None:
        clear_pair_cache()
        meta = get_pair_metadata("bina")
        try:
            meta.full_name = "changed"  # type: ignore[misc]
            msg = "Should have raised FrozenInstanceError"
            raise AssertionError(msg)
        except AttributeError:
            pass

    def test_canonical_pair_names(self) -> None:
        clear_pair_cache()
        assert get_pair_metadata("adelia").full_name == "The Entangled Pair"
        assert get_pair_metadata("bina").full_name == "The Circuit Pair"
        assert get_pair_metadata("reina").full_name == "The Kinetic Pair"
        assert get_pair_metadata("alicia").full_name == "The Solstice Pair"

    def test_all_eight_fields_present(self) -> None:
        clear_pair_cache()
        meta = get_pair_metadata("bina")
        assert meta.full_name == "The Circuit Pair"
        assert meta.classification == "Orthogonal Opposition"
        assert meta.mechanism == "Total division of operational domains"
        assert meta.core_metaphor == "The Architect and the Sentinel"
        assert meta.what_she_provides != ""
        assert meta.how_she_breaks_spiral != ""
        assert meta.shared_functions != ""
        assert meta.cadence != ""


class TestFormatPairMetadata:
    """WI1: format_pair_metadata returns 6-field structured block."""

    def test_six_fields_for_all_characters(self) -> None:
        clear_pair_cache()
        for char_id in ["adelia", "bina", "reina", "alicia"]:
            block = format_pair_metadata(char_id)
            assert "PAIR:" in block
            assert "CLASSIFICATION:" in block
            assert "MECHANISM:" in block
            assert "CORE METAPHOR:" in block
            assert "WHAT SHE PROVIDES:" in block
            assert "HOW SHE BREAKS HIS SPIRAL:" in block

    def test_excludes_shared_functions_and_cadence(self) -> None:
        clear_pair_cache()
        for char_id in ["adelia", "bina", "reina", "alicia"]:
            block = format_pair_metadata(char_id)
            assert "SHARED FUNCTIONS:" not in block.upper().replace("_", " ")
            assert "CADENCE:" not in block.upper()

    def test_all_four_canonical_phrases(self) -> None:
        clear_pair_cache()
        expected = {
            "adelia": ("The Entangled Pair", "Intuitive Symbiosis", "The Compass and the Gravity"),
            "bina": ("The Circuit Pair", "Orthogonal Opposition", "The Architect and the Sentinel"),
            "reina": ("The Kinetic Pair", "Asymmetrical Leverage", "The Mastermind and the Operator"),
            "alicia": ("The Solstice Pair", "Complete Jungian Duality", "The Duality"),
        }
        for char_id, (pair_name, classification, metaphor) in expected.items():
            block = format_pair_metadata(char_id)
            assert pair_name in block, f"{char_id}: missing {pair_name}"
            assert classification in block, f"{char_id}: missing {classification}"
            assert metaphor in block, f"{char_id}: missing {metaphor}"


class TestErrorHandling:
    """F1 regression: pair loading failures must propagate, not silently disappear."""

    def test_missing_character_raises_value_error(self) -> None:
        clear_pair_cache()
        import pytest

        with pytest.raises(ValueError, match="No pair metadata"):
            get_pair_metadata("nonexistent")

    def test_layer_5_propagates_pair_error(self) -> None:
        """F1: Layer 5 must not silently swallow pair loading errors."""
        from unittest.mock import patch

        from starry_lyfe.context.layers import format_voice_directives

        with patch(
            "starry_lyfe.canon.pairs_loader.format_pair_metadata",
            side_effect=FileNotFoundError("pairs.yaml missing"),
        ):
            import pytest

            with pytest.raises(FileNotFoundError):
                format_voice_directives("bina", None)


class TestSingleParse:
    """F4: YAML parsed once, not per character."""

    def test_four_characters_single_yaml_parse(self) -> None:
        from unittest.mock import patch

        clear_pair_cache()
        with patch("starry_lyfe.canon.pairs_loader.yaml.safe_load", wraps=__import__("yaml").safe_load) as mock_load:
            for char_id in ["adelia", "bina", "reina", "alicia"]:
                get_pair_metadata(char_id)
            assert mock_load.call_count == 1, (
                f"YAML parsed {mock_load.call_count} times instead of 1"
            )


class TestLayer5Integration:
    """WI2: pair metadata reaches Layer 5 voice directives."""

    def test_layer_5_contains_pair_metadata(self) -> None:
        from starry_lyfe.context.kernel_loader import clear_kernel_cache
        from starry_lyfe.context.layers import format_voice_directives

        clear_kernel_cache()
        clear_pair_cache()
        for char_id in ["adelia", "bina", "reina", "alicia"]:
            layer = format_voice_directives(char_id, None)
            assert "PAIR:" in layer.text, f"{char_id}: missing PAIR: in Layer 5"
            assert "CLASSIFICATION:" in layer.text

    def test_layer_5_within_900_token_budget(self) -> None:
        from starry_lyfe.context.kernel_loader import clear_kernel_cache
        from starry_lyfe.context.layers import format_voice_directives

        clear_kernel_cache()
        clear_pair_cache()
        for char_id in ["adelia", "bina", "reina", "alicia"]:
            layer = format_voice_directives(
                char_id, None, budget=DEFAULT_BUDGETS.voice,
            )
            assert layer.estimated_tokens <= DEFAULT_BUDGETS.voice, (
                f"{char_id}: Layer 5 {layer.estimated_tokens} tokens "
                f"exceeds {DEFAULT_BUDGETS.voice} budget"
            )
