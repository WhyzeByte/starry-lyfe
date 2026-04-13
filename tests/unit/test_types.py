"""Phase F type system tests for SceneType, SceneModifiers, and SceneState."""

from __future__ import annotations

from starry_lyfe.context.types import (
    CommunicationMode,
    SceneModifiers,
    SceneState,
    SceneType,
    VoiceMode,
)


class TestSceneType:
    """SceneType enum correctness."""

    def test_member_count(self) -> None:
        assert len(SceneType) == 8

    def test_round_trip(self) -> None:
        assert SceneType("domestic") is SceneType.DOMESTIC
        assert SceneType("intimate") is SceneType.INTIMATE

    def test_all_members_are_strings(self) -> None:
        for member in SceneType:
            assert isinstance(member.value, str)


class TestSceneModifiers:
    """SceneModifiers defaults and construction."""

    def test_defaults_all_falsy(self) -> None:
        mods = SceneModifiers()
        assert mods.work_colleagues_present is False
        assert mods.post_intensity_crash_active is False
        assert mods.pair_escalation_active is False
        assert mods.warm_refusal_required is False
        assert mods.silent_register_active is False
        assert mods.group_temperature_shift is False
        assert len(mods.explicitly_invoked_absent_dyad) == 0

    def test_explicit_construction(self) -> None:
        mods = SceneModifiers(
            work_colleagues_present=True,
            explicitly_invoked_absent_dyad=frozenset({"bina-reina"}),
        )
        assert mods.work_colleagues_present is True
        assert "bina-reina" in mods.explicitly_invoked_absent_dyad


class TestSceneStateBackwardCompat:
    """SceneState with Phase F fields must remain backward compatible."""

    def test_no_args_constructs(self) -> None:
        scene = SceneState()
        assert scene.scene_type is SceneType.DOMESTIC
        assert scene.modifiers.work_colleagues_present is False
        assert scene.present_characters == []
        assert scene.communication_mode is CommunicationMode.IN_PERSON

    def test_pre_phase_f_args_still_work(self) -> None:
        scene = SceneState(
            present_characters=["adelia", "whyze"],
            public_scene=True,
            scene_description="Warehouse.",
            voice_modes=[VoiceMode.DOMESTIC],
        )
        assert scene.public_scene is True
        assert scene.scene_type is SceneType.DOMESTIC
        assert scene.voice_modes == [VoiceMode.DOMESTIC]

    def test_phase_f_args(self) -> None:
        mods = SceneModifiers(pair_escalation_active=True)
        scene = SceneState(
            scene_type=SceneType.INTIMATE,
            modifiers=mods,
            present_characters=["reina", "whyze"],
        )
        assert scene.scene_type is SceneType.INTIMATE
        assert scene.modifiers.pair_escalation_active is True
