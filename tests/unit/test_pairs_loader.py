"""Phase D tests for pair metadata loading and Layer 5 integration."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from starry_lyfe.canon.pairs_loader import (
    PairMetadata,
    clear_pair_cache,
    format_pair_metadata,
    get_pair_metadata,
)
from starry_lyfe.context.budgets import DEFAULT_BUDGETS

ROOT = Path(__file__).resolve().parents[2]
PAIRS_LOADER_PATH = ROOT / "src" / "starry_lyfe" / "canon" / "pairs_loader.py"


def _load_pairs_loader_module(module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, PAIRS_LOADER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        sys.modules.pop(module_name, None)


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
        # Phase 10.5c: classification + mechanism now source from shared_canon.pairs[]
        # (single-source-of-truth migration, R1 §2.5). Strings updated accordingly.
        clear_pair_cache()
        meta = get_pair_metadata("bina")
        assert meta.full_name == "The Circuit Pair"
        assert meta.classification == "diagnostic love"
        assert meta.mechanism.startswith("Si-Fe loop meets Fe-Ti loop")
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
        # Phase 10.5c: classification strings migrated to shared_canon.pairs[]
        # (single-source-of-truth migration, R1 §2.5). The four objective
        # anchors are the shared_canon-authored values.
        clear_pair_cache()
        expected = {
            "adelia": ("The Entangled Pair", "generator-governor polarity", "The Compass and the Gravity"),
            "bina": ("The Circuit Pair", "diagnostic love", "The Architect and the Sentinel"),
            "reina": ("The Kinetic Pair", "kinetic-vanguard", "The Mastermind and the Operator"),
            "alicia": ("The Solstice Pair", "Complete functional inversion / Socionics duality", "The Duality"),
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
        """F1: Layer 5 must not silently swallow pair loading errors.

        Post-Phase-10.5b RT1 cutover, Layer 5 sources pair metadata from
        ``rich_loader.format_pair_metadata_from_rich`` rather than the
        legacy ``pairs_loader.format_pair_metadata``. The F1 invariant
        — Layer 5 must not swallow errors — is preserved against the
        new runtime path.
        """
        from unittest.mock import patch

        from starry_lyfe.context.layers import format_voice_directives

        with patch(
            "starry_lyfe.canon.rich_loader.format_pair_metadata_from_rich",
            side_effect=FileNotFoundError("rich YAML missing"),
        ):
            import pytest

            with pytest.raises(FileNotFoundError):
                format_voice_directives("bina", None)


class TestSingleParse:
    """F4: pair metadata hydrated once, not per character.

    Phase 10.5c: pairs_loader now sources from shared_canon.pairs[] via
    rich_loader.load_shared_canon. The parse-once invariant is enforced
    by counting load_shared_canon calls instead of yaml.safe_load.
    """

    def test_four_characters_single_load_shared_canon(self) -> None:
        from unittest.mock import patch

        clear_pair_cache()
        with patch(
            "starry_lyfe.canon.pairs_loader.load_shared_canon",
            wraps=__import__("starry_lyfe.canon.rich_loader", fromlist=["load_shared_canon"]).load_shared_canon,
        ) as mock_load:
            for char_id in ["adelia", "bina", "reina", "alicia"]:
                get_pair_metadata(char_id)
            assert mock_load.call_count == 1, (
                f"shared_canon loaded {mock_load.call_count} times instead of 1"
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

    async def test_live_assemble_context_layer_5_has_pair_metadata(
        self, monkeypatch: object,
    ) -> None:
        """R2-F2: Live assemble_context() path carries pair metadata in Layer 5."""
        from types import SimpleNamespace
        from unittest.mock import AsyncMock, patch

        from starry_lyfe.context.assembler import assemble_context
        from starry_lyfe.context.kernel_loader import clear_kernel_cache
        from starry_lyfe.context.types import CommunicationMode, SceneState

        def make_stub(char_id: str) -> SimpleNamespace:
            baseline = SimpleNamespace(
                full_name=char_id.title(),
                epithet="Test",
                mbti="ENFP-A",
                dominant_function="Ne",
                pair_name="test",
                heritage="Test",
                profession="Test",
                voice_params={"response_length_range": "default", "dominant_function_descriptor": "default"},
            )
            return SimpleNamespace(
                canon_facts=[],
                character_baseline=baseline,
                dyad_states_whyze=[],
                dyad_states_internal=[],
                episodic_memories=[],
                open_loops=[],
                somatic_state=SimpleNamespace(
                    character_id=char_id, fatigue=0.1, stress_residue=0.1,
                    injury_residue=0.0, active_protocols=[],
                ),
            )

        clear_kernel_cache()
        clear_pair_cache()

        expected_fields = [
            "PAIR:", "CLASSIFICATION:", "MECHANISM:",
            "CORE METAPHOR:", "WHAT SHE PROVIDES:",
            "HOW SHE BREAKS HIS SPIRAL:",
        ]

        for char_id in ["adelia", "bina", "reina", "alicia"]:
            with patch(
                "starry_lyfe.context.assembler.retrieve_memories",
                new=AsyncMock(return_value=make_stub(char_id)),
            ):
                prompt = await assemble_context(
                    char_id,
                    "Phase D Layer 5 probe",
                    SceneState(
                        present_characters=[char_id, "whyze"],
                        alicia_home=True,
                        scene_description="Pair metadata probe",
                        communication_mode=CommunicationMode.IN_PERSON,
                    ),
                    None,
                    None,
                )
                layer_5 = next(ly for ly in prompt.layers if ly.layer_number == 5)
                for field in expected_fields:
                    assert field in layer_5.text, (
                        f"{char_id}: Layer 5 missing '{field}' in live assembled prompt"
                    )


# --- R-2.1 remediation: pairs loader reports all missing entries at once ---


class TestPairsLoaderMissingEntriesR21:
    """R-2.1: authoring a character without a shared_canon.pairs entry fails loudly.

    Phase 10.5c: pairs_loader now sources from shared_canon.pairs[]. The
    missing-entries fail-loud invariant moves to the load_shared_canon
    surface — if shared_canon.pairs is missing entries, _ensure_loaded
    raises a single ValueError listing every missing character→pair_key.
    """

    def test_pairs_loader_import_reports_all_missing_at_once(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Missing pair entries must fail on module import (re-import), not only on first access."""
        from starry_lyfe.canon import pairs_loader, rich_loader
        from starry_lyfe.canon.shared_schema import SharedCanon

        original_load = rich_loader.load_shared_canon
        full = original_load()
        # Remove two pairs so bina and reina lack mappings.
        retained = [sp for sp in (full.pairs or [])
                    if sp.canonical_name not in ("The Circuit Pair", "The Kinetic Pair")]
        partial_dump = full.model_dump()
        partial_dump["pairs"] = [sp.model_dump() for sp in retained]
        partial = SharedCanon.model_validate(partial_dump)

        monkeypatch.setattr(rich_loader, "load_shared_canon", lambda: partial)
        monkeypatch.setattr(pairs_loader, "load_shared_canon", lambda: partial)

        with pytest.raises(ValueError) as excinfo:
            _load_pairs_loader_module("starry_lyfe.canon.pairs_loader_import_r21")

        msg = str(excinfo.value)
        assert "bina->circuit" in msg
        assert "reina->kinetic" in msg
        assert "shared_canon.pairs is missing entries" in msg

    def test_pairs_loader_reports_all_missing_at_once(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Two missing pair entries must surface in ONE error listing both."""
        from starry_lyfe.canon import pairs_loader as pl
        from starry_lyfe.canon import rich_loader
        from starry_lyfe.canon.shared_schema import SharedCanon

        # Force a fresh load
        clear_pair_cache()

        full = rich_loader.load_shared_canon()
        retained = [sp for sp in (full.pairs or [])
                    if sp.canonical_name not in ("The Circuit Pair", "The Kinetic Pair")]
        partial_dump = full.model_dump()
        partial_dump["pairs"] = [sp.model_dump() for sp in retained]
        partial = SharedCanon.model_validate(partial_dump)

        monkeypatch.setattr(pl, "load_shared_canon", lambda: partial)

        with pytest.raises(ValueError) as excinfo:
            pl._ensure_loaded()

        msg = str(excinfo.value)
        # Both missing entries must be in the single error message
        assert "bina->circuit" in msg
        assert "reina->kinetic" in msg
        assert "shared_canon.pairs is missing entries" in msg

        # Cleanup
        clear_pair_cache()
