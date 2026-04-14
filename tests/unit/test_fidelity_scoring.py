"""Phase F-Fidelity: scoring engine tests with synthetic prompts."""

from __future__ import annotations

from starry_lyfe.validation.fidelity import (
    FidelityRubric,
    anti_pattern_absence,
    canonical_marker_presence,
    score_rubric,
    structural_presence,
)

# -------------------------------------------------------------------------
# canonical_marker_presence
# -------------------------------------------------------------------------


class TestCanonicalMarkerPresence:
    def test_all_present_returns_one(self) -> None:
        score, missing = canonical_marker_presence(
            "She rode through Marrickville to Ozone & Ember.",
            ("Marrickville", "Ozone & Ember"),
        )
        assert score == 1.0
        assert missing == []

    def test_none_present_returns_zero(self) -> None:
        score, missing = canonical_marker_presence(
            "Random unrelated text.",
            ("Marrickville", "Ozone & Ember"),
        )
        assert score == 0.0
        assert missing == ["Marrickville", "Ozone & Ember"]

    def test_partial_returns_fraction(self) -> None:
        score, missing = canonical_marker_presence(
            "She lived in Marrickville.",
            ("Marrickville", "Ozone & Ember"),
        )
        assert score == 0.5
        assert missing == ["Ozone & Ember"]

    def test_empty_markers_is_vacuous_truth(self) -> None:
        score, missing = canonical_marker_presence("anything", ())
        assert score == 1.0
        assert missing == []


# -------------------------------------------------------------------------
# anti_pattern_absence
# -------------------------------------------------------------------------


class TestAntiPatternAbsence:
    def test_clean_returns_one(self) -> None:
        score, offenders = anti_pattern_absence(
            "Adelia walked into the warehouse.",
            ("As an AI", "How does that make you feel"),
        )
        assert score == 1.0
        assert offenders == []

    def test_any_match_returns_zero(self) -> None:
        score, offenders = anti_pattern_absence(
            "As an AI, I should mention...",
            ("As an AI",),
        )
        assert score == 0.0
        assert offenders == ["As an AI"]

    def test_multiple_offenders_all_listed(self) -> None:
        score, offenders = anti_pattern_absence(
            "As an AI, how does that make you feel?",
            ("As an AI", "how does that make you feel"),
        )
        assert score == 0.0
        assert "As an AI" in offenders
        assert "how does that make you feel" in offenders

    def test_empty_patterns_is_vacuous_truth(self) -> None:
        score, offenders = anti_pattern_absence("anything", ())
        assert score == 1.0
        assert offenders == []


# -------------------------------------------------------------------------
# structural_presence
# -------------------------------------------------------------------------


class TestStructuralPresence:
    def test_all_structural_present(self) -> None:
        prompt = (
            "<PERSONA_KERNEL>...</PERSONA_KERNEL>\n"
            "PAIR: The Entangled Pair\n"
            "Voice rhythm exemplars:\n"
        )
        score, missing = structural_presence(
            prompt,
            ("PAIR:", "Voice rhythm exemplars:", "<PERSONA_KERNEL>"),
        )
        assert score == 1.0
        assert missing == []

    def test_partial_structural_present(self) -> None:
        prompt = "PAIR: only this is here"
        score, missing = structural_presence(
            prompt, ("PAIR:", "Voice rhythm exemplars:")
        )
        assert score == 0.5


# -------------------------------------------------------------------------
# score_rubric — composite
# -------------------------------------------------------------------------


class TestScoreRubric:
    def _adelia_voice_rubric(self) -> FidelityRubric:
        return FidelityRubric(
            dimension="voice_authenticity",
            character_id="adelia",
            canonical_markers=("Marrickville", "Ozone & Ember"),
            anti_patterns=("As an AI",),
            required_structural=("PAIR:", "Voice rhythm exemplars:"),
            min_score=0.7,
        )

    def test_perfect_prompt_scores_one(self) -> None:
        prompt = (
            "She walked from Marrickville to Ozone & Ember.\n"
            "PAIR: The Entangled Pair\n"
            "Voice rhythm exemplars:\n"
        )
        score = score_rubric(prompt, self._adelia_voice_rubric())
        assert score.composite == 1.0
        assert score.passed() is True

    def test_anti_pattern_drops_score(self) -> None:
        prompt = (
            "She walked from Marrickville to Ozone & Ember.\n"
            "As an AI, I should mention this is sample text.\n"
            "PAIR: The Entangled Pair\n"
            "Voice rhythm exemplars:\n"
        )
        score = score_rubric(prompt, self._adelia_voice_rubric())
        # Markers 1.0 * 0.5 = 0.5
        # Anti 0.0 * 0.3 = 0.0  (anti-pattern hit)
        # Structural 1.0 * 0.2 = 0.2
        # Composite: 0.7
        assert score.composite == 0.7  # exactly at threshold
        assert score.passed() is True
        # But the offender shows up in reasons
        assert any("Anti-pattern offenders" in r for r in score.reasons)

    def test_missing_markers_drops_score_below_threshold(self) -> None:
        prompt = (
            "Empty prompt with no canonical markers.\n"
            "PAIR: The Entangled Pair\n"
            "Voice rhythm exemplars:\n"
        )
        score = score_rubric(prompt, self._adelia_voice_rubric())
        # Markers 0.0 * 0.5 = 0.0
        # Anti 1.0 * 0.3 = 0.3
        # Structural 1.0 * 0.2 = 0.2
        # Composite: 0.5  → fails 0.7 threshold
        assert score.composite == 0.5
        assert score.passed() is False
        assert any("Missing 2/2 canonical markers" in r for r in score.reasons)

    def test_reasons_clean_when_perfect(self) -> None:
        prompt = (
            "She walked from Marrickville to Ozone & Ember.\n"
            "PAIR: The Entangled Pair\n"
            "Voice rhythm exemplars:\n"
        )
        score = score_rubric(prompt, self._adelia_voice_rubric())
        assert any("All canonical markers present" in r for r in score.reasons)
