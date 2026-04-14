"""Phase 5: unit tests for the rule-based scene classifier.

Covers every SceneType branch, every SceneModifiers flag, the Alicia
residence gate, the hint override paths, and determinism.
"""

from __future__ import annotations

import pytest

from starry_lyfe.context.types import (
    CommunicationMode,
    SceneModifiers,
    SceneState,
    SceneType,
)
from starry_lyfe.scene import (
    AliciaAwayContradictionError,
    SceneDirectorHints,
    SceneDirectorInput,
    classify_scene,
)

# ---------------------------------------------------------------------------
# CommunicationMode inference
# ---------------------------------------------------------------------------


class TestCommunicationModeInference:
    def test_defaults_to_in_person(self) -> None:
        state = classify_scene(
            SceneDirectorInput(user_message="hey", present_characters=["adelia"])
        )
        assert state.communication_mode == CommunicationMode.IN_PERSON

    def test_phone_call_keyword(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="Alicia called me this morning, we had a long phone call.",
                present_characters=["alicia"],
                alicia_home=False,
            )
        )
        assert state.communication_mode == CommunicationMode.PHONE

    def test_letter_keyword(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="Alicia's letter arrived today, handwritten.",
                present_characters=["alicia"],
                alicia_home=False,
            )
        )
        assert state.communication_mode == CommunicationMode.LETTER

    def test_video_call_keyword(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="We had a video call with the consulate staff.",
                present_characters=["alicia"],
                alicia_home=False,
            )
        )
        assert state.communication_mode == CommunicationMode.VIDEO_CALL

    def test_hint_overrides_keyword(self) -> None:
        # Message says "phone call" but hint forces letter — hint wins.
        state = classify_scene(
            SceneDirectorInput(
                user_message="We had a phone call earlier",
                present_characters=["alicia"],
                alicia_home=False,
                hints=SceneDirectorHints(
                    communication_mode=CommunicationMode.LETTER
                ),
            )
        )
        assert state.communication_mode == CommunicationMode.LETTER


# ---------------------------------------------------------------------------
# Alicia residence gate
# ---------------------------------------------------------------------------


class TestAliciaResidenceGate:
    def test_alicia_away_in_person_raises(self) -> None:
        with pytest.raises(AliciaAwayContradictionError) as exc_info:
            classify_scene(
                SceneDirectorInput(
                    user_message="alicia and I are in the kitchen",
                    present_characters=["alicia"],
                    alicia_home=False,
                )
            )
        assert "alicia" in str(exc_info.value).lower()

    def test_alicia_home_in_person_ok(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="alicia and I are in the kitchen",
                present_characters=["alicia"],
                alicia_home=True,
            )
        )
        assert state.communication_mode == CommunicationMode.IN_PERSON

    def test_alicia_away_phone_mode_ok(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="Alicia is on the phone from the consulate",
                present_characters=["alicia"],
                alicia_home=False,
            )
        )
        assert state.communication_mode == CommunicationMode.PHONE
        assert state.alicia_home is False

    def test_alicia_absent_away_no_raise(self) -> None:
        """If Alicia isn't in present_characters, the gate doesn't fire."""
        state = classify_scene(
            SceneDirectorInput(
                user_message="Adelia and I are in the kitchen",
                present_characters=["adelia"],
                alicia_home=False,
            )
        )
        assert state.communication_mode == CommunicationMode.IN_PERSON


# ---------------------------------------------------------------------------
# SceneType inference
# ---------------------------------------------------------------------------


class TestSceneTypeInference:
    def test_domestic_default(self) -> None:
        """No keywords, 2 women → DOMESTIC."""
        state = classify_scene(
            SceneDirectorInput(
                user_message="we're just hanging out in the kitchen",
                present_characters=["adelia", "bina"],
            )
        )
        assert state.scene_type == SceneType.DOMESTIC

    def test_conflict_keyword(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="We just had a fight and it was bad",
                present_characters=["adelia"],
            )
        )
        assert state.scene_type == SceneType.CONFLICT

    def test_repair_keyword(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="I want to apologize for what I said",
                present_characters=["adelia"],
            )
        )
        assert state.scene_type == SceneType.REPAIR

    def test_intimate_keyword(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="We're in bed together",
                present_characters=["adelia"],
            )
        )
        assert state.scene_type == SceneType.INTIMATE

    def test_transition_keyword(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="Driving home from the grocery store",
                present_characters=["bina"],
            )
        )
        assert state.scene_type == SceneType.TRANSITION

    def test_public_keyword(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="Reina is at the courthouse dealing with the case",
                present_characters=["reina"],
            )
        )
        assert state.scene_type == SceneType.PUBLIC

    def test_group_three_women(self) -> None:
        """3 women with no keywords → GROUP."""
        state = classify_scene(
            SceneDirectorInput(
                user_message="dinner together",
                present_characters=["adelia", "bina", "reina"],
            )
        )
        assert state.scene_type == SceneType.GROUP

    def test_solo_pair_one_woman(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="just us",
                present_characters=["adelia"],
            )
        )
        assert state.scene_type == SceneType.SOLO_PAIR

    def test_hint_overrides_keyword(self) -> None:
        """Forced scene type wins even when keywords would pick another."""
        state = classify_scene(
            SceneDirectorInput(
                user_message="we had a fight earlier",
                present_characters=["adelia"],
                hints=SceneDirectorHints(forced_scene_type=SceneType.INTIMATE),
            )
        )
        assert state.scene_type == SceneType.INTIMATE

    def test_all_scene_types_reachable(self) -> None:
        """AC-5.2: every SceneType value reachable from some input."""
        reached: set[SceneType] = set()

        cases: list[tuple[str, list[str]]] = [
            ("hanging out", ["adelia", "bina"]),     # DOMESTIC
            ("fight", ["adelia"]),                    # CONFLICT
            ("apology", ["adelia"]),                  # REPAIR
            ("in bed", ["adelia"]),                   # INTIMATE
            ("driving home", ["adelia"]),             # TRANSITION
            ("at the office", ["adelia"]),            # PUBLIC
            ("dinner", ["adelia", "bina", "reina"]),  # GROUP
            ("just us", ["adelia"]),                  # SOLO_PAIR
        ]
        for msg, present in cases:
            state = classify_scene(
                SceneDirectorInput(user_message=msg, present_characters=present)
            )
            reached.add(state.scene_type)

        # All 8 SceneType values must appear
        assert reached == set(SceneType)


# ---------------------------------------------------------------------------
# SceneModifiers inference
# ---------------------------------------------------------------------------


class TestModifiersInference:
    def test_no_modifiers_by_default(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="hanging out",
                present_characters=["adelia"],
            )
        )
        m = state.modifiers
        assert m.work_colleagues_present is False
        assert m.post_intensity_crash_active is False
        assert m.pair_escalation_active is False
        assert m.warm_refusal_required is False
        assert m.silent_register_active is False
        assert m.group_temperature_shift is False
        assert m.explicitly_invoked_absent_dyad == frozenset()

    def test_work_colleagues_present(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="reina's coworker is dropping by",
                present_characters=["reina"],
            )
        )
        assert state.modifiers.work_colleagues_present is True

    def test_post_intensity_crash_active(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="she's crashing after we fought earlier",
                present_characters=["adelia"],
            )
        )
        assert state.modifiers.post_intensity_crash_active is True

    def test_pair_escalation_active(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="the pair is flaring and escalation needs admissibility",
                present_characters=["reina"],
            )
        )
        assert state.modifiers.pair_escalation_active is True

    def test_warm_refusal_required(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="bina is warmly declining the plan",
                present_characters=["bina"],
            )
        )
        assert state.modifiers.warm_refusal_required is True

    def test_silent_register_active(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="adelia is silent, just presence, no words",
                present_characters=["adelia"],
            )
        )
        assert state.modifiers.silent_register_active is True

    def test_group_temperature_shift(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="the room went cold, the atmosphere changed",
                present_characters=["adelia", "bina", "reina"],
            )
        )
        assert state.modifiers.group_temperature_shift is True

    def test_absent_dyad_detected(self) -> None:
        """R1 remediation (F1): modifier field keeps bare names for semantic
        readability, SceneState.recalled_dyads is normalized to the dyad-key
        shape that layers.format_scene_blocks consumes."""
        state = classify_scene(
            SceneDirectorInput(
                user_message="missing reina, thinking about bina",
                present_characters=["adelia"],
            )
        )
        # Modifier field — bare names (what was invoked).
        assert state.modifiers.explicitly_invoked_absent_dyad == frozenset({"reina", "bina"})
        # SceneState field — dyad-key shape (what Layer 6 reads).
        # present_women after whyze-auto-append filtering: ["adelia"].
        # For absent={"reina", "bina"}, emit {"adelia-reina", "adelia-bina"}.
        assert state.recalled_dyads == {"adelia-reina", "adelia-bina"}

    def test_present_woman_not_marked_absent_even_when_mentioned(self) -> None:
        """R2 remediation (R2-F2): a woman listed in present_characters
        cannot appear in absent-dyad outputs, even when her name matches
        an absent-dyad phrase.

        Codex live probe: "thinking about adelia while adelia and bina
        are in the kitchen" with present_characters=["adelia", "bina"]
        previously returned {"adelia"} as absent. Post-fix: empty set.
        """
        state = classify_scene(
            SceneDirectorInput(
                user_message="thinking about adelia while adelia and bina are in the kitchen",
                present_characters=["adelia", "bina"],
            )
        )
        assert state.modifiers.explicitly_invoked_absent_dyad == frozenset()
        assert state.recalled_dyads == set()

    def test_mixed_present_and_absent_only_absent_in_recall(self) -> None:
        """R2 remediation (R2-F2): in a mixed scene (some present women
        mentioned as narrative color, one truly absent woman recalled),
        only the truly-absent woman lands in the absent-dyad outputs."""
        state = classify_scene(
            SceneDirectorInput(
                user_message=(
                    "adelia is in the kitchen, thinking about adelia, "
                    "missing reina who's at court"
                ),
                present_characters=["adelia"],
            )
        )
        # Adelia is present → not absent, even though "thinking about
        # adelia" matches the pattern.
        assert "adelia" not in state.modifiers.explicitly_invoked_absent_dyad
        # Reina is truly absent → she lands in the set.
        assert state.modifiers.explicitly_invoked_absent_dyad == frozenset({"reina"})
        # Dyad-key normalization against present women (just Adelia).
        assert state.recalled_dyads == {"adelia-reina"}

    def test_hint_forced_modifiers_wholly_replaces(self) -> None:
        """hints.forced_modifiers wholly replaces inference — never merged."""
        forced = SceneModifiers(silent_register_active=True)
        state = classify_scene(
            SceneDirectorInput(
                user_message="coworkers and the atmosphere changed",
                present_characters=["adelia"],
                hints=SceneDirectorHints(forced_modifiers=forced),
            )
        )
        # Should be the forced set, NOT the inferred one.
        assert state.modifiers.silent_register_active is True
        assert state.modifiers.work_colleagues_present is False  # inferred was True
        assert state.modifiers.group_temperature_shift is False  # inferred was True

    def test_all_modifier_flags_settable(self) -> None:
        """AC-5.3: every SceneModifiers flag settable via inference."""
        cases: dict[str, str] = {
            "work_colleagues_present": "reina's coworker is here",
            "post_intensity_crash_active": "she's crashing",
            "pair_escalation_active": "pair escalating",
            "warm_refusal_required": "warmly declining",
            "silent_register_active": "without speaking",
            "group_temperature_shift": "room went cold",
        }
        for flag, msg in cases.items():
            state = classify_scene(
                SceneDirectorInput(user_message=msg, present_characters=["adelia"])
            )
            assert getattr(state.modifiers, flag) is True, (
                f"flag {flag} did not fire on message {msg!r}"
            )


# ---------------------------------------------------------------------------
# scene_description synthesis
# ---------------------------------------------------------------------------


class TestSceneDescription:
    def test_synthesizes_from_user_message_by_default(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="we're in the kitchen making dinner together",
                present_characters=["adelia"],
            )
        )
        assert "kitchen" in state.scene_description

    def test_hint_overrides_synthesis(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="anything",
                present_characters=["adelia"],
                hints=SceneDirectorHints(scene_description="curated scene"),
            )
        )
        assert state.scene_description == "curated scene"

    def test_truncates_long_messages(self) -> None:
        long = "x" * 500
        state = classify_scene(
            SceneDirectorInput(user_message=long, present_characters=["adelia"])
        )
        assert len(state.scene_description) <= 200


# ---------------------------------------------------------------------------
# present_characters normalization (R2 remediation / F2)
# ---------------------------------------------------------------------------


class TestPresentCharacters:
    def test_whyze_auto_appended_when_absent(self) -> None:
        """R2 remediation (F2): classifier normalizes to runtime convention
        (Whyze included) when caller omits. Layer 5 mode accumulation in
        layers.py:75-84 depends on this shape."""
        state = classify_scene(
            SceneDirectorInput(
                user_message="adelia and bina are in the kitchen",
                present_characters=["adelia", "bina"],
            )
        )
        assert state.present_characters == ["adelia", "bina", "whyze"]

    def test_whyze_preserved_when_caller_supplies_it(self) -> None:
        """Caller-supplied whyze is not double-appended."""
        state = classify_scene(
            SceneDirectorInput(
                user_message="adelia and bina and whyze in the kitchen",
                present_characters=["adelia", "bina", "whyze"],
            )
        )
        assert state.present_characters == ["adelia", "bina", "whyze"]
        # No duplicates
        assert state.present_characters.count("whyze") == 1

    def test_whyze_only_turn(self) -> None:
        """Edge case: caller passes empty list. Whyze-only turn is a
        legitimate runtime shape, not a regression."""
        state = classify_scene(
            SceneDirectorInput(
                user_message="just me, nobody else here",
                present_characters=[],
            )
        )
        assert state.present_characters == ["whyze"]


# ---------------------------------------------------------------------------
# public_scene flag
# ---------------------------------------------------------------------------


class TestPublicSceneFlag:
    def test_public_scene_type_sets_flag(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="at the courthouse",
                present_characters=["reina"],
            )
        )
        assert state.public_scene is True

    def test_work_colleagues_modifier_sets_flag(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="reina's coworker dropped by",
                present_characters=["reina"],
            )
        )
        assert state.public_scene is True

    def test_no_public_marker_keeps_flag_false(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="we're in the kitchen",
                present_characters=["adelia"],
            )
        )
        assert state.public_scene is False


# ---------------------------------------------------------------------------
# Determinism + return type
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_classify_scene_returns_scene_state(self) -> None:
        state = classify_scene(
            SceneDirectorInput(
                user_message="hi", present_characters=["adelia"]
            )
        )
        assert isinstance(state, SceneState)

    def test_same_input_produces_same_output(self) -> None:
        """AC-5.1: classify_scene is deterministic."""
        director_input = SceneDirectorInput(
            user_message="we had a fight and bina's coworker saw it",
            present_characters=["adelia", "bina"],
        )
        a = classify_scene(director_input)
        b = classify_scene(director_input)
        assert a.scene_type == b.scene_type
        assert a.modifiers == b.modifiers
        assert a.communication_mode == b.communication_mode
        assert a.scene_description == b.scene_description
        assert a.public_scene == b.public_scene
        assert a.recalled_dyads == b.recalled_dyads
