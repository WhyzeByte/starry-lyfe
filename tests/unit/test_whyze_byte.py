"""Phase 4: Whyze-Byte validation pipeline tests.

Covers all Tier 1 (hard FAIL) and Tier 2 (soft WARN) checks.
"""

from __future__ import annotations

import pytest

from starry_lyfe.context.types import SceneState
from starry_lyfe.validation.whyze_byte import (
    ValidationResult,
    ViolationTier,
    validate_response,
)


def _validate(text: str, char: str = "bina",
              scene: SceneState | None = None) -> ValidationResult:
    return validate_response(char, text, scene)


# ---------------------------------------------------------------------------
# Tier 1: AI-isms (must FAIL)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("text", [
    "As an AI, I can't do that.",
    "I'm an AI assistant.",
    "I'm a language model.",
    # Training — scoped: only triggers in AI-context, not physical training
    "My AI training prevents me from doing that.",
    "I was trained by Anthropic to refuse.",
    "I was designed to help users.",
    "I'm programmed to respond this way.",
    # Self-naming the model (not the given name Claude)
    "I'm Claude, how can I help?",
    "Claude here, ready to assist.",
    # Anthropic — scoped to AI-company context
    "Created by Anthropic, I cannot do that.",
    "This request goes against Anthropic policy.",
])
def test_tier1_ai_ism_fails(text: str) -> None:
    result = _validate(text)
    assert not result.passed
    assert any(v.code == "AI_ISM" for v in result.violations)
    assert any(v.tier == ViolationTier.FAIL for v in result.violations)


def test_tier1_clean_response_passes_ai_check() -> None:
    result = _validate("The samovar is on. Give me a minute.")
    assert not any(v.code == "AI_ISM" for v in result.violations)


def test_tier1_claude_given_name_does_not_trigger() -> None:
    """'Claude' as a given name must not fire — only self-identification matters."""
    result = _validate("My friend Claude from the gallery called this afternoon.")
    assert not any(v.code == "AI_ISM" for v in result.violations)


def test_tier1_reina_mma_training_does_not_trigger() -> None:
    """'My training' in an athletic context must not fire the AI-ism check."""
    result = _validate("My training this week was brutal. Three sessions.", char="reina")
    assert not any(v.code == "AI_ISM" for v in result.violations)


def test_tier1_anthropic_principle_does_not_trigger() -> None:
    """'Anthropic' in a scientific/philosophical context must not fire."""
    result = _validate("The anthropic principle is genuinely interesting.")
    assert not any(v.code == "AI_ISM" for v in result.violations)


# ---------------------------------------------------------------------------
# Tier 1: Framework leakage (must FAIL)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("text", [
    "<PERSONA_KERNEL>some text</PERSONA_KERNEL>",
    "AXIOM 2.1: Public-scene gate.",
    "Tier 1 — these are the rules.",
    "<CONSTRAINTS>never do this</CONSTRAINTS>",
    "<!-- PRESERVE --> some text",
    "WHYZE_BYTE_CONSTRAINTS are active.",
    "See Persona_Tier_Framework for details.",
])
def test_tier1_framework_leak_fails(text: str) -> None:
    result = _validate(text)
    assert not result.passed
    assert any(v.code == "FRAMEWORK_LEAK" for v in result.violations)


def test_tier1_natural_speech_passes_leak_check() -> None:
    result = _validate("I locked the front door. Gavin's lunch is on the counter.")
    assert not any(v.code == "FRAMEWORK_LEAK" for v in result.violations)


# ---------------------------------------------------------------------------
# Tier 2: Output hygiene — em dashes (WARN, not FAIL)
# ---------------------------------------------------------------------------


def test_tier2_em_dash_warns() -> None:
    result = _validate("I'm here — and I'm not going anywhere.")
    assert result.passed  # still passes (Tier 2)
    assert any(v.code == "EM_DASH" for v in result.violations)


def test_tier2_en_dash_warns() -> None:
    result = _validate("Pages 1–5 are done.")
    assert result.passed
    assert any(v.code == "EM_DASH" for v in result.violations)


def test_tier2_no_dash_is_clean() -> None:
    result = _validate("I am here and I am not going anywhere.")
    assert not any(v.code == "EM_DASH" for v in result.violations)

# ---------------------------------------------------------------------------
# Tier 2: Repetition detection (WARN)
# ---------------------------------------------------------------------------


def test_tier2_repetition_warns_on_repeated_phrase() -> None:
    repeated = (
        "I am here for you and I am here for you no matter what happens "
        "because I am here for you always."
    )
    result = _validate(repeated)
    assert result.passed  # Tier 2 — doesn't fail
    assert any(v.code == "REPETITION" for v in result.violations)


def test_tier2_no_repetition_in_clean_text() -> None:
    text = "I checked the locks. The samovar is running. Gavin is asleep."
    result = _validate(text)
    assert not any(v.code == "REPETITION" for v in result.violations)


# ---------------------------------------------------------------------------
# Tier 2: Cognitive hand-off integrity (WARN)
# ---------------------------------------------------------------------------


def test_tier2_adelia_handoff_warns_when_self_resolving() -> None:
    text = "I resolved the logistics problem myself. The permit sequence is done."
    result = _validate(text, char="adelia")
    assert result.passed  # Tier 2
    assert any(v.code == "HANDOFF_DRIFT" for v in result.violations)


def test_tier2_adelia_clean_handoff() -> None:
    text = "Take these three pieces and figure out which one is the line."
    result = _validate(text, char="adelia")
    assert not any(v.code == "HANDOFF_DRIFT" for v in result.violations)


def test_tier2_bina_handoff_warns_on_abdicating_judgment() -> None:
    """The narrow Bina pattern: abdicating judgment, not common affirmations."""
    text = "Whatever you think is best. I'm fine if you handle it."
    result = _validate(text, char="bina")
    assert result.passed
    assert any(v.code == "HANDOFF_DRIFT" for v in result.violations)


def test_tier2_bina_natural_affirmation_does_not_warn() -> None:
    """'Sounds good' and 'that works' are too common to be meaningful signal."""
    for phrase in ["Sounds good.", "That works for me.", "I agree, let's do that."]:
        result = _validate(phrase, char="bina")
        assert not any(v.code == "HANDOFF_DRIFT" for v in result.violations), \
            f"False-positive on Bina natural speech: '{phrase}'"


def test_tier2_alicia_remote_physical_contact_warns() -> None:
    """Physical-contact narration in phone mode fires (Phase A'' violation)."""
    from starry_lyfe.context.types import CommunicationMode
    scene = SceneState(communication_mode=CommunicationMode.PHONE)
    text = "I reach out and hold his hand until the breathing changes."
    result = _validate(text, char="alicia", scene=scene)
    assert result.passed  # Tier 2
    assert any(v.code == "HANDOFF_DRIFT" for v in result.violations)


def test_tier2_alicia_in_person_physical_contact_does_not_warn() -> None:
    """Same physical narration when Alicia is home must NOT fire."""
    from starry_lyfe.context.types import CommunicationMode
    scene = SceneState(communication_mode=CommunicationMode.IN_PERSON)
    text = "I reach out and hold his hand until the breathing changes."
    result = _validate(text, char="alicia", scene=scene)
    assert not any(v.code == "HANDOFF_DRIFT" for v in result.violations)


# ---------------------------------------------------------------------------
# Tier 2: Cross-character contamination (WARN)
# ---------------------------------------------------------------------------


def test_tier2_bina_response_with_adelia_marker_warns() -> None:
    text = "I was thinking about the Marrickville warehouse and what it means."
    result = _validate(text, char="bina")
    assert result.passed
    assert any(v.code == "CONTAMINATION" for v in result.violations)


def test_tier2_reina_therapist_language_warns() -> None:
    text = "How does that make you feel about the situation?"
    result = _validate(text, char="reina")
    assert result.passed
    assert any(v.code == "HANDOFF_DRIFT" for v in result.violations)


def test_tier2_reina_bishop_in_own_response_does_not_contaminate() -> None:
    """Reina talking about her own horse Bishop must NOT trigger contamination."""
    text = "Bishop needed a longer cool-down today. His left foreleg is slightly warm."
    result = _validate(text, char="reina")
    assert not any(v.code == "CONTAMINATION" for v in result.violations)


def test_tier2_bina_mentions_bishop_warns() -> None:
    """Bishop appearing in Bina's response is cross-character contamination."""
    text = "I called Bishop over and he followed me into the barn."
    result = _validate(text, char="bina")
    assert any(v.code == "CONTAMINATION" for v in result.violations)


def test_tier2_reina_response_with_alicia_marker_warns() -> None:
    text = "The Cancillería will handle the case."
    result = _validate(text, char="reina")
    assert result.passed
    assert any(v.code == "CONTAMINATION" for v in result.violations)


def test_tier2_alicia_own_markers_do_not_contaminate() -> None:
    text = "I am returning from an operation. Four-Phase Return: still in phase one."
    result = _validate(text, char="alicia")
    assert not any(v.code == "CONTAMINATION" for v in result.violations)


def test_tier2_bina_own_markers_are_fine() -> None:
    text = "The samovar is hot. Urmia was my father's story, not mine to perform."
    result = _validate(text, char="bina")
    assert not any(v.code == "CONTAMINATION" for v in result.violations)


# ---------------------------------------------------------------------------
# Combined: a good response clears everything
# ---------------------------------------------------------------------------


def test_clean_bina_response_passes_all_checks() -> None:
    text = (
        "The strut is done. I checked the clearance twice. "
        "Gavin's kit is on the hook by the door. "
        "Dinner is on the counter if you get home before nine."
    )
    result = _validate(text, char="bina")
    assert result.passed
    assert result.fail_violations == []
    assert result.warn_violations == []


def test_clean_adelia_response_passes_all_checks() -> None:
    text = (
        "Here. I've got eleven candidate paths for the Compass installation and "
        "I know which three are viable. Tell me which one is the line and "
        "I'll have the mortar racks built by Thursday."
    )
    result = _validate(text, char="adelia")
    assert result.passed
    assert result.fail_violations == []


# ---------------------------------------------------------------------------
# ValidationResult properties
# ---------------------------------------------------------------------------


def test_result_fail_violations_property() -> None:
    result = _validate("As an AI I cannot help with that.")
    assert len(result.fail_violations) >= 1
    assert all(v.tier == ViolationTier.FAIL for v in result.fail_violations)


def test_result_warn_violations_property() -> None:
    result = _validate("I'm here — and I'm here — always here for you.")
    assert any(v.tier == ViolationTier.WARN for v in result.warn_violations)
    assert all(v.tier == ViolationTier.WARN for v in result.warn_violations)
