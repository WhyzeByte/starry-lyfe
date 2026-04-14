"""Phase F-Fidelity: rubric/score dataclass construction tests."""

from __future__ import annotations

import pytest

from starry_lyfe.validation.fidelity import (
    RUBRIC_DIMENSIONS,
    FidelityRubric,
    FidelityScore,
)


class TestFidelityRubric:
    def test_construct_with_minimum_args(self) -> None:
        rubric = FidelityRubric(
            dimension="voice_authenticity",
            character_id="adelia",
            canonical_markers=("Marrickville", "Ozone & Ember"),
        )
        assert rubric.dimension == "voice_authenticity"
        assert rubric.character_id == "adelia"
        assert rubric.canonical_markers == ("Marrickville", "Ozone & Ember")
        assert rubric.anti_patterns == ()
        assert rubric.required_structural == ()
        assert rubric.min_score == 0.7  # default

    def test_construct_with_all_args(self) -> None:
        rubric = FidelityRubric(
            dimension="pair_authenticity",
            character_id="bina",
            canonical_markers=("Circuit Pair",),
            anti_patterns=("As an AI",),
            required_structural=("PAIR:",),
            min_score=0.85,
        )
        assert rubric.min_score == 0.85
        assert "Circuit Pair" in rubric.canonical_markers
        assert "As an AI" in rubric.anti_patterns

    def test_rejects_unknown_dimension(self) -> None:
        with pytest.raises(ValueError, match="Unknown rubric dimension"):
            FidelityRubric(
                dimension="vibe_check",  # not in RUBRIC_DIMENSIONS
                character_id="adelia",
                canonical_markers=("x",),
            )

    def test_rejects_min_score_out_of_range(self) -> None:
        with pytest.raises(ValueError, match=r"min_score must be in \[0.0, 1.0\]"):
            FidelityRubric(
                dimension="voice_authenticity",
                character_id="adelia",
                canonical_markers=("x",),
                min_score=1.5,
            )
        with pytest.raises(ValueError, match=r"min_score must be in \[0.0, 1.0\]"):
            FidelityRubric(
                dimension="voice_authenticity",
                character_id="adelia",
                canonical_markers=("x",),
                min_score=-0.1,
            )


class TestRubricDimensions:
    def test_taxonomy_has_seven_dimensions(self) -> None:
        assert len(RUBRIC_DIMENSIONS) == 7

    def test_taxonomy_is_frozenset(self) -> None:
        assert isinstance(RUBRIC_DIMENSIONS, frozenset)

    def test_taxonomy_contains_canonical_seven(self) -> None:
        assert {
            "voice_authenticity",
            "pair_authenticity",
            "cognitive_function",
            "body_register",
            "conflict_register",
            "repair_register",
            "autonomy_outside_pair",
        } == RUBRIC_DIMENSIONS


class TestFidelityScore:
    def _rubric(self, min_score: float = 0.7) -> FidelityRubric:
        return FidelityRubric(
            dimension="voice_authenticity",
            character_id="adelia",
            canonical_markers=("x",),
            min_score=min_score,
        )

    def test_passed_at_threshold(self) -> None:
        score = FidelityScore(
            rubric=self._rubric(min_score=0.7),
            marker_score=0.7,
            anti_pattern_score=0.7,
            structural_score=0.7,
            composite=0.7,
        )
        assert score.passed() is True

    def test_failed_below_threshold(self) -> None:
        score = FidelityScore(
            rubric=self._rubric(min_score=0.7),
            marker_score=0.5,
            anti_pattern_score=0.0,
            structural_score=0.5,
            composite=0.4,
        )
        assert score.passed() is False

    def test_summary_contains_verdict_and_components(self) -> None:
        score = FidelityScore(
            rubric=self._rubric(min_score=0.7),
            marker_score=0.8,
            anti_pattern_score=1.0,
            structural_score=0.9,
            composite=0.86,
        )
        summary = score.summary()
        assert "PASS" in summary
        assert "adelia.voice_authenticity" in summary
        assert "0.86" in summary

    def test_reasons_default_empty_list(self) -> None:
        score = FidelityScore(
            rubric=self._rubric(),
            marker_score=1.0,
            anti_pattern_score=1.0,
            structural_score=1.0,
            composite=1.0,
        )
        assert score.reasons == []
