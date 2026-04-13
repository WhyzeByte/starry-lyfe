"""Phase E voice mode tests: parsing, selection, and Layer 5 integration."""

from __future__ import annotations

import pytest

from starry_lyfe.context.kernel_loader import (
    _extract_voice_examples,
    _extract_voice_guidance,
    clear_kernel_cache,
    load_voice_guidance,
)
from starry_lyfe.context.layers import (
    _compact_voice_guidance_item,
    _select_voice_exemplars,
    derive_active_voice_modes,
)
from starry_lyfe.context.types import SceneState, VoiceMode

# ---------------------------------------------------------------------------
# Synthetic Voice.md content for parser tests
# ---------------------------------------------------------------------------

SYNTHETIC_VOICE_MD = """\
# Character : Few-Shot Voice Calibration

**Purpose:** Test voice file.

---

## Example 1: Domestic Morning

<!-- mode: domestic, solo_pair -->

**What it teaches the model:** A short domestic response.

**User:**
Good morning.

**Assistant:**
*Sets down a coffee mug.* Morning. The truck needs gas before noon.

**Abbreviated:** Morning exchange, sets down a coffee mug, mentions the truck needs gas.

---

## Example 2: Conflict Veto

<!-- mode: conflict -->
<!-- communication_mode: in_person -->

**What it teaches the model:** A flat disagreement with no hedging.

**User:**
Let's skip the inspection.

**Assistant:**
No. The clearance is marginal.

**Abbreviated:** Flat refusal, the clearance is marginal.

---

## Example 3: Silent Response

<!-- mode: silent, solo_pair -->

**What it teaches the model:** Silence as a complete response.

**User:**
I got bad news.

**Assistant:**
*Sits next to you.*

---

## Example 4: No Mode Tags

**What it teaches the model:** An example without mode tags for backward compat.

**User:**
What do you think?

**Assistant:**
I think you already know.

**Abbreviated:** She thinks he already knows.

---
"""

SYNTHETIC_VOICE_MD_NO_MODES = """\
# Character : Few-Shot Voice Calibration

---

## Example 1: Basic Response

**What it teaches the model:** A basic response with no mode tags.

**User:**
Hello.

**Assistant:**
Hi there.

---

## Example 2: Another Response

**What it teaches the model:** Another response with no mode tags at all.

**User:**
What's up?

**Assistant:**
Not much.

---
"""


# ---------------------------------------------------------------------------
# E1: Mode tag parsing
# ---------------------------------------------------------------------------

class TestModeTagParsing:
    """E1: Each character's Voice.md parses successfully with mode tags."""

    def test_extracts_all_modes_from_tagged_examples(self) -> None:
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        assert len(examples) == 4

        ex1 = examples[0]
        assert ex1.title == "Example 1: Domestic Morning"
        assert VoiceMode.DOMESTIC in ex1.modes
        assert VoiceMode.SOLO_PAIR in ex1.modes
        assert len(ex1.modes) == 2

    def test_single_mode_tag(self) -> None:
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        ex2 = examples[1]
        assert ex2.title == "Example 2: Conflict Veto"
        assert ex2.modes == [VoiceMode.CONFLICT]

    def test_communication_mode_preserved(self) -> None:
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        ex2 = examples[1]
        assert ex2.communication_mode == "in_person"
        ex1 = examples[0]
        assert ex1.communication_mode == "any"

    def test_example_without_mode_tags_has_empty_modes(self) -> None:
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        ex4 = examples[3]
        assert ex4.title == "Example 4: No Mode Tags"
        assert ex4.modes == []

    def test_teaching_prose_extracted(self) -> None:
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        ex1 = examples[0]
        assert "short domestic response" in ex1.teaching_prose

    def test_abbreviated_text_extracted(self) -> None:
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        ex1 = examples[0]
        assert ex1.abbreviated_text is not None
        assert "coffee mug" in ex1.abbreviated_text

    def test_abbreviated_text_none_when_missing(self) -> None:
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        ex3 = examples[2]
        assert ex3.title == "Example 3: Silent Response"
        assert ex3.abbreviated_text is None

    def test_file_order_indices(self) -> None:
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        for i, ex in enumerate(examples):
            assert ex.index == i

    def test_invalid_mode_raises_value_error(self) -> None:
        bad_voice = """\
## Example 1: Bad

<!-- mode: nonexistent_mode -->

**What it teaches the model:** Bad mode test.

**User:**
Test.

**Assistant:**
Test.
"""
        with pytest.raises(ValueError):
            _extract_voice_examples(bad_voice)


# ---------------------------------------------------------------------------
# E5: Backward compatibility — load_voice_guidance still works without mode tags
# ---------------------------------------------------------------------------

class TestBackwardCompatibility:
    """E5: load_voice_guidance() still works with no mode tags present."""

    def test_guidance_extraction_unchanged_for_untagged_file(self) -> None:
        items = _extract_voice_guidance(SYNTHETIC_VOICE_MD_NO_MODES)
        assert len(items) == 2
        assert all(isinstance(item, tuple) and len(item) == 2 for item in items)

    def test_guidance_extraction_works_with_mode_tagged_file(self) -> None:
        items = _extract_voice_guidance(SYNTHETIC_VOICE_MD)
        assert len(items) >= 3  # At least the examples with teaching prose

    def test_load_voice_guidance_returns_for_all_characters(self) -> None:
        clear_kernel_cache()
        for char_id in ("adelia", "bina", "reina", "alicia"):
            result = load_voice_guidance(char_id)
            assert result is not None, f"load_voice_guidance returned None for {char_id}"
            assert len(result) > 0, f"No guidance items for {char_id}"
        clear_kernel_cache()


# ---------------------------------------------------------------------------
# E8: Abbreviated fallback — when abbreviated_text is None, compact teaching note
# ---------------------------------------------------------------------------

class TestAbbreviatedFallback:
    """E8: When abbreviated_text is None, fall back to compacted teaching note."""

    def test_compact_teaching_note_extracts_first_sentence(self) -> None:
        item = "Example 1: Domestic Morning: A short domestic response. More detail here."
        compact = _compact_voice_guidance_item(item)
        assert "A short domestic response." in compact
        assert "More detail" not in compact

    def test_voice_example_with_abbreviated_text_preferred(self) -> None:
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        ex1 = examples[0]
        assert ex1.abbreviated_text is not None
        assert "coffee mug" in ex1.abbreviated_text

    def test_voice_example_without_abbreviated_falls_back(self) -> None:
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        ex3 = examples[2]
        assert ex3.abbreviated_text is None
        # The fallback path uses teaching_prose -> compact first sentence
        assert "Silence as a complete response" in ex3.teaching_prose
        compact = _compact_voice_guidance_item(
            f"{ex3.title}: {ex3.teaching_prose}"
        )
        assert len(compact) > 0


# ---------------------------------------------------------------------------
# E3: Mode-aware selection differs from file-order
# ---------------------------------------------------------------------------

class TestModeAwareSelection:
    """E3: Mode-aware selection produces different results than file-order."""

    def test_conflict_mode_promotes_conflict_example(self) -> None:
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        # File order: domestic(0), conflict(1), silent(2), untagged(3)
        # Mode-aware with conflict active should return conflict example first
        selected = _select_voice_exemplars(
            examples,
            active_modes=[VoiceMode.CONFLICT],
        )
        assert len(selected) >= 1
        assert VoiceMode.CONFLICT in selected[0].modes

    def test_mode_aware_differs_from_file_order(self) -> None:
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        file_order = examples[:2]
        selected = _select_voice_exemplars(
            examples,
            active_modes=[VoiceMode.SILENT],
        )
        # Silent example is at index 2, not in the first 2 by file order
        assert selected[0].index != file_order[0].index

    def test_multi_mode_overlap_scored_higher(self) -> None:
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        selected = _select_voice_exemplars(
            examples,
            active_modes=[VoiceMode.DOMESTIC, VoiceMode.SOLO_PAIR],
        )
        # Example 1 has both domestic + solo_pair (score 2), should be first
        assert selected[0].index == 0
        assert len(set(selected[0].modes) & {VoiceMode.DOMESTIC, VoiceMode.SOLO_PAIR}) == 2

    def test_max_exemplars_respected(self) -> None:
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        selected = _select_voice_exemplars(
            examples,
            active_modes=[VoiceMode.DOMESTIC, VoiceMode.SOLO_PAIR],
            max_exemplars=1,
        )
        assert len(selected) == 1


# ---------------------------------------------------------------------------
# E6: Fallback when no modes match
# ---------------------------------------------------------------------------

class TestSelectionFallback:
    """E6: Fallback returns non-empty when no modes match."""

    def test_fallback_returns_nonempty_for_unmatched_mode(self) -> None:
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        # ESCALATION is not tagged in any synthetic example
        selected = _select_voice_exemplars(
            examples,
            active_modes=[VoiceMode.ESCALATION],
        )
        assert len(selected) > 0

    def test_fallback_returns_file_order(self) -> None:
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        selected = _select_voice_exemplars(
            examples,
            active_modes=[VoiceMode.ESCALATION],
        )
        # Should return the first 2 by file order as fallback
        assert selected[0].index <= selected[-1].index


# ---------------------------------------------------------------------------
# E7: Communication mode filtering preserved
# ---------------------------------------------------------------------------

class TestCommunicationModeFiltering:
    """E7: Mode-aware selection respects communication_mode from Phase A''."""

    def test_in_person_filter_includes_matching_example(self) -> None:
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        selected = _select_voice_exemplars(
            examples,
            active_modes=[VoiceMode.CONFLICT],
            communication_mode="in_person",
        )
        assert len(selected) >= 1
        # Example 2 (conflict) is tagged in_person, should be included
        assert any(ex.communication_mode == "in_person" for ex in selected)

    def test_phone_filter_excludes_in_person_only(self) -> None:
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        selected = _select_voice_exemplars(
            examples,
            active_modes=[VoiceMode.CONFLICT],
            communication_mode="phone",
        )
        # Example 2 (conflict) is tagged in_person, should be excluded
        # No phone-tagged examples exist, so fallback to "any" tagged ones
        for ex in selected:
            assert ex.communication_mode in ("phone", "any")


# ---------------------------------------------------------------------------
# derive_active_voice_modes tests
# ---------------------------------------------------------------------------

class TestDeriveActiveVoiceModes:
    """Verify SceneState-to-VoiceMode mapping."""

    def test_default_includes_domestic(self) -> None:
        scene = SceneState(present_characters=["whyze"])
        modes = derive_active_voice_modes(scene)
        assert VoiceMode.DOMESTIC in modes

    def test_children_present_adds_children_gate(self) -> None:
        scene = SceneState(children_present=True)
        modes = derive_active_voice_modes(scene)
        assert VoiceMode.CHILDREN_GATE in modes

    def test_public_scene_adds_public(self) -> None:
        scene = SceneState(public_scene=True)
        modes = derive_active_voice_modes(scene)
        assert VoiceMode.PUBLIC in modes

    def test_two_characters_adds_solo_pair(self) -> None:
        scene = SceneState(present_characters=["adelia", "whyze"])
        modes = derive_active_voice_modes(scene)
        assert VoiceMode.SOLO_PAIR in modes

    def test_three_characters_adds_group(self) -> None:
        scene = SceneState(present_characters=["adelia", "bina", "whyze"])
        modes = derive_active_voice_modes(scene)
        assert VoiceMode.GROUP in modes

    def test_explicit_voice_modes_override(self) -> None:
        scene = SceneState(
            present_characters=["adelia", "whyze"],
            voice_modes=[VoiceMode.INTIMATE, VoiceMode.ESCALATION],
        )
        modes = derive_active_voice_modes(scene)
        assert modes == [VoiceMode.INTIMATE, VoiceMode.ESCALATION]
        assert VoiceMode.DOMESTIC not in modes


# ---------------------------------------------------------------------------
# E2: Bina domestic scene includes domestic-tagged exemplar
# ---------------------------------------------------------------------------

class TestBinaDomesticSelection:
    """E2: Bina's Layer 5 for a domestic scene includes a domestic exemplar."""

    def test_domestic_selection_from_synthetic(self) -> None:
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        selected = _select_voice_exemplars(
            examples,
            active_modes=[VoiceMode.DOMESTIC],
        )
        assert any(VoiceMode.DOMESTIC in ex.modes for ex in selected)

    def test_domestic_selection_returns_domestic_first(self) -> None:
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        selected = _select_voice_exemplars(
            examples,
            active_modes=[VoiceMode.DOMESTIC, VoiceMode.SOLO_PAIR],
        )
        # Example 1 (domestic + solo_pair, score 2) should be first
        assert selected[0].index == 0
        assert VoiceMode.DOMESTIC in selected[0].modes


# ---------------------------------------------------------------------------
# E4: Abbreviated content length validation
# ---------------------------------------------------------------------------

class TestAbbreviatedContentLength:
    """E4: Abbreviated exemplar content is 1-2 sentences per example."""

    def test_abbreviated_text_sentence_count(self) -> None:
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        import re
        sentence_split = re.compile(r"(?<=[.!?])\s+")
        for ex in examples:
            if ex.abbreviated_text:
                sentences = sentence_split.split(ex.abbreviated_text)
                sentences = [s for s in sentences if s.strip()]
                assert 1 <= len(sentences) <= 3, (
                    f"{ex.title}: expected 1-3 sentences, got {len(sentences)}: "
                    f"{ex.abbreviated_text}"
                )

    def test_format_voice_exemplar_uses_abbreviated(self) -> None:
        from starry_lyfe.context.layers import _format_voice_exemplar
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        ex1 = examples[0]
        formatted = _format_voice_exemplar(ex1)
        assert ex1.abbreviated_text is not None
        assert ex1.abbreviated_text in formatted
        assert "domestic" in formatted  # Mode tag appears in output

    def test_format_voice_exemplar_fallback_without_abbreviated(self) -> None:
        from starry_lyfe.context.layers import _format_voice_exemplar
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD)
        ex3 = examples[2]  # Silent response, no abbreviated text
        assert ex3.abbreviated_text is None
        formatted = _format_voice_exemplar(ex3)
        # Should use compacted teaching prose as fallback
        assert "Silence" in formatted
