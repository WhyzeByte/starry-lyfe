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
from starry_lyfe.context.types import SceneModifiers, SceneState, SceneType, VoiceMode

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

SYNTHETIC_VOICE_MD_PUBLIC_GAP = """\
## Example 1: Intimate Private

<!-- mode: intimate, solo_pair -->

**What it teaches the model:** Private intimate register.

**User:**
Stay.

**Assistant:**
Stay right here.

**Abbreviated:** Private intimate response.

---

## Example 2: Domestic Pair

<!-- mode: domestic, solo_pair -->

**What it teaches the model:** Private domestic pair register.

**User:**
Coffee?

**Assistant:**
Already made.

**Abbreviated:** Private domestic response.

---

## Example 3: Group Observation

<!-- mode: group -->

**What it teaches the model:** Group-room observation.

**User:**
What changed?

**Assistant:**
The room did.

**Abbreviated:** Group-scene observation.

---

## Example 4: Domestic Public-Safe

<!-- mode: domestic -->

**What it teaches the model:** Neutral domestic register.

**User:**
You good?

**Assistant:**
Working on it.

**Abbreviated:** Neutral domestic response.

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

    def test_public_mode_fallback_prefers_non_private_examples(self) -> None:
        examples = _extract_voice_examples(SYNTHETIC_VOICE_MD_PUBLIC_GAP)
        selected = _select_voice_exemplars(
            examples,
            active_modes=[VoiceMode.DOMESTIC, VoiceMode.PUBLIC, VoiceMode.SOLO_PAIR],
        )
        assert selected
        assert selected[0].index == 3
        assert VoiceMode.SOLO_PAIR not in selected[0].modes
        assert VoiceMode.INTIMATE not in selected[0].modes

    def test_public_mode_keeps_specific_nonpublic_match_when_requested(self) -> None:
        public_warm_refusal = """\
## Example 1: Warm Refusal

<!-- mode: warm_refusal, solo_pair -->

**What it teaches the model:** Warm refusal that keeps the bond.

**User:**
Tell me anyway.

**Assistant:**
No.

**Abbreviated:** Warm refusal response.

---

## Example 2: Neutral Domestic

<!-- mode: domestic -->

**What it teaches the model:** Neutral domestic fallback.

**User:**
Okay.

**Assistant:**
Okay.

**Abbreviated:** Domestic fallback.
"""
        examples = _extract_voice_examples(public_warm_refusal)
        selected = _select_voice_exemplars(
            examples,
            active_modes=[VoiceMode.PUBLIC, VoiceMode.WARM_REFUSAL],
        )
        assert selected
        assert VoiceMode.WARM_REFUSAL in selected[0].modes


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

    # --- Phase F: SceneType → VoiceMode mapping tests ---

    def test_intimate_scene_activates_intimate_and_solo_pair(self) -> None:
        """F10 derive: INTIMATE scene → INTIMATE + SOLO_PAIR."""
        scene = SceneState(scene_type=SceneType.INTIMATE, present_characters=["bina", "whyze"])
        modes = derive_active_voice_modes(scene)
        assert VoiceMode.INTIMATE in modes
        assert VoiceMode.SOLO_PAIR in modes

    def test_conflict_scene_activates_conflict(self) -> None:
        """F11 derive: CONFLICT scene → CONFLICT."""
        scene = SceneState(scene_type=SceneType.CONFLICT, present_characters=["adelia", "whyze"])
        modes = derive_active_voice_modes(scene)
        assert VoiceMode.CONFLICT in modes

    def test_repair_scene_activates_repair_and_silent(self) -> None:
        """F6 derive: REPAIR scene → REPAIR + SILENT."""
        scene = SceneState(scene_type=SceneType.REPAIR, present_characters=["alicia", "whyze"])
        modes = derive_active_voice_modes(scene)
        assert VoiceMode.REPAIR in modes
        assert VoiceMode.SILENT in modes

    def test_modifier_accumulates_escalation(self) -> None:
        """F7 derive: pair_escalation_active → +ESCALATION on top of scene modes."""
        scene = SceneState(
            scene_type=SceneType.INTIMATE,
            present_characters=["reina", "whyze"],
            modifiers=SceneModifiers(pair_escalation_active=True),
        )
        modes = derive_active_voice_modes(scene)
        assert VoiceMode.ESCALATION in modes
        assert VoiceMode.INTIMATE in modes

    def test_modifier_warm_refusal(self) -> None:
        """F8 derive: warm_refusal_required → +WARM_REFUSAL."""
        scene = SceneState(
            present_characters=["alicia", "whyze"],
            modifiers=SceneModifiers(warm_refusal_required=True),
        )
        modes = derive_active_voice_modes(scene)
        assert VoiceMode.WARM_REFUSAL in modes

    def test_modifier_group_temperature(self) -> None:
        """F9 derive: group_temperature_shift → +GROUP_TEMPERATURE."""
        scene = SceneState(
            present_characters=["alicia", "bina", "whyze"],
            modifiers=SceneModifiers(group_temperature_shift=True),
        )
        modes = derive_active_voice_modes(scene)
        assert VoiceMode.GROUP_TEMPERATURE in modes

    def test_legacy_default_unchanged(self) -> None:
        """Legacy compat: SceneState() default → [DOMESTIC] only."""
        modes = derive_active_voice_modes(SceneState())
        assert modes == [VoiceMode.DOMESTIC]

    def test_f12_all_11_modes_reachable(self) -> None:
        """F12: Every VoiceMode is reachable via at least one (scene_type, modifiers) combo."""
        reachable: set[VoiceMode] = set()

        # Walk scene types
        for st in SceneType:
            scene = SceneState(scene_type=st, present_characters=["bina", "whyze"])
            modes = derive_active_voice_modes(scene)
            reachable.update(modes)

        # Walk modifier-driven modes
        modifier_combos = [
            SceneModifiers(pair_escalation_active=True),
            SceneModifiers(warm_refusal_required=True),
            SceneModifiers(silent_register_active=True),
            SceneModifiers(group_temperature_shift=True),
            SceneModifiers(post_intensity_crash_active=True),
        ]
        for mods in modifier_combos:
            scene = SceneState(present_characters=["alicia", "whyze"], modifiers=mods)
            modes = derive_active_voice_modes(scene)
            reachable.update(modes)

        # Legacy path for PUBLIC (via public_scene flag)
        scene = SceneState(public_scene=True)
        reachable.update(derive_active_voice_modes(scene))

        # Legacy path for GROUP (via 3+ characters)
        scene = SceneState(present_characters=["adelia", "bina", "reina", "whyze"])
        reachable.update(derive_active_voice_modes(scene))

        all_modes = set(VoiceMode)
        missing = all_modes - reachable
        assert not missing, (
            f"Dormant modes still unreachable: {[m.value for m in missing]}. "
            f"Only {len(reachable)}/11 reachable."
        )


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
                assert 1 <= len(sentences) <= 2, (
                    f"{ex.title}: expected 1-2 sentences, got {len(sentences)}: "
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


# ---------------------------------------------------------------------------
# Real-file tests: E1 and E4 against actual Voice.md corpus
# ---------------------------------------------------------------------------

REQUIRED_MODES: dict[str, set[str]] = {
    "adelia": {"solo_pair", "conflict", "intimate", "group", "domestic", "silent"},
    "bina": {"domestic", "conflict", "intimate", "repair", "silent"},
    "reina": {"solo_pair", "conflict", "group", "repair", "intimate", "domestic", "escalation"},
    "alicia": {"solo_pair", "silent", "intimate", "repair", "warm_refusal", "group_temperature"},
}


class TestRealFileParsing:
    """Real-file tests against the actual Voice.md corpus."""

    def test_all_characters_parse_with_mode_tags(self) -> None:
        """E1 real: each character's Voice.md parses with mode tags."""
        from starry_lyfe.context.kernel_loader import load_voice_examples
        clear_kernel_cache()
        for char_id in ("adelia", "bina", "reina", "alicia"):
            examples = load_voice_examples(char_id)
            assert examples is not None, f"No examples for {char_id}"
            tagged = [ex for ex in examples if ex.modes]
            assert len(tagged) == len(examples), (
                f"{char_id}: {len(tagged)}/{len(examples)} examples have mode tags"
            )
        clear_kernel_cache()

    def test_required_mode_coverage(self) -> None:
        """E1 real: each character covers all required modes."""
        from starry_lyfe.context.kernel_loader import load_voice_examples
        clear_kernel_cache()
        for char_id, required in REQUIRED_MODES.items():
            examples = load_voice_examples(char_id)
            assert examples is not None
            covered_modes: set[str] = set()
            for ex in examples:
                for mode in ex.modes:
                    covered_modes.add(str(mode))
            missing = required - covered_modes
            assert not missing, (
                f"{char_id}: missing required modes {missing}"
            )
        clear_kernel_cache()

    def test_all_examples_have_abbreviated_text(self) -> None:
        """E4 real: all examples have abbreviated text."""
        from starry_lyfe.context.kernel_loader import load_voice_examples
        clear_kernel_cache()
        for char_id in ("adelia", "bina", "reina", "alicia"):
            examples = load_voice_examples(char_id)
            assert examples is not None
            for ex in examples:
                assert ex.abbreviated_text is not None, (
                    f"{char_id} {ex.title}: missing abbreviated text"
                )
                assert len(ex.abbreviated_text) > 20, (
                    f"{char_id} {ex.title}: abbreviated text too short"
                )
        clear_kernel_cache()

    def test_abbreviated_text_sentence_count_real(self) -> None:
        """E4 real: abbreviated text is 1-2 sentences."""
        import re as re_mod

        from starry_lyfe.context.kernel_loader import load_voice_examples
        clear_kernel_cache()
        sentence_split = re_mod.compile(r"(?<=[.!?])\s+")
        for char_id in ("adelia", "bina", "reina", "alicia"):
            examples = load_voice_examples(char_id)
            assert examples is not None
            for ex in examples:
                if ex.abbreviated_text:
                    sentences = sentence_split.split(ex.abbreviated_text)
                    sentences = [s for s in sentences if s.strip()]
                    assert 1 <= len(sentences) <= 2, (
                        f"{char_id} {ex.title}: expected 1-2 sentences, "
                        f"got {len(sentences)}: {ex.abbreviated_text}"
                    )
        clear_kernel_cache()


# ---------------------------------------------------------------------------
# Live Layer 5 test: format_voice_directives uses mode-aware path
# ---------------------------------------------------------------------------

class TestLiveLayer5:
    """Verify format_voice_directives activates mode-aware path on real files."""

    def test_voice_rhythm_exemplars_header_on_real_files(self) -> None:
        """Layer 5 uses 'Voice rhythm exemplars:' when mode tags present."""
        from starry_lyfe.context.layers import format_voice_directives
        clear_kernel_cache()
        layer = format_voice_directives("adelia", baseline=None)
        assert "Voice rhythm exemplars:" in layer.text
        clear_kernel_cache()

    def test_abbreviated_text_appears_in_layer5(self) -> None:
        """Layer 5 carries abbreviated text from real Voice.md files."""
        from starry_lyfe.context.layers import format_voice_directives
        clear_kernel_cache()
        layer = format_voice_directives("bina", baseline=None)
        # Should contain at least one abbreviated exemplar
        assert "domestic" in layer.text.lower() or "solo_pair" in layer.text.lower()
        clear_kernel_cache()

    def test_scene_state_affects_exemplar_selection(self) -> None:
        """Non-domestic scene changes the exemplar set in Layer 5."""
        from starry_lyfe.context.layers import format_voice_directives
        clear_kernel_cache()
        domestic_scene = SceneState(present_characters=["adelia", "whyze"])
        group_scene = SceneState(
            present_characters=["adelia", "bina", "whyze"],
        )
        format_voice_directives(
            "adelia", baseline=None, scene_state=domestic_scene,
        )
        clear_kernel_cache()
        layer_group = format_voice_directives(
            "adelia", baseline=None, scene_state=group_scene,
        )
        clear_kernel_cache()
        # Group scene should include a group-tagged exemplar
        assert "group" in layer_group.text.lower()

    def test_public_scene_avoids_private_register_fallbacks(self) -> None:
        """PUBLIC scenes should not fall back to intimate/escalation pair exemplars."""
        from starry_lyfe.context.layers import format_voice_directives

        clear_kernel_cache()
        scene = SceneState(
            scene_type=SceneType.PUBLIC,
            present_characters=["alicia", "whyze"],
            public_scene=True,
        )
        layer = format_voice_directives("alicia", baseline=None, scene_state=scene)
        clear_kernel_cache()

        assert "intimate" not in layer.text.lower()
        assert "escalation" not in layer.text.lower()
        assert "solo_pair" not in layer.text.lower()
