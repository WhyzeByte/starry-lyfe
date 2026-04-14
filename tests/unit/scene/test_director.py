"""Phase 5: smoke tests for the Scene Director public API.

Focus is on the facade contract: exports are correct, types line up,
and the two halves (classify_scene + select_next_speaker) can be
composed without intermediate glue.
"""

from __future__ import annotations

from starry_lyfe.scene import (
    DictDyadStateProvider,
    DyadStateProvider,
    NextSpeakerDecision,
    NextSpeakerInput,
    SceneDirectorHints,
    SceneDirectorInput,
    TurnEntry,
    build_dyad_state_provider,
    classify_scene,
    last_non_whyze_speaker,
    select_next_speaker,
)


class TestPublicAPIExports:
    def test_all_public_names_importable(self) -> None:
        # This test exists so adding/removing a public name produces a
        # visible diff. If you edit the import list above, update the
        # __all__ tuple in __init__.py / director.py in lockstep.
        names = {
            "AliciaAwayContradictionError",
            "DictDyadStateProvider",
            "DyadStateProvider",
            "NextSpeakerDecision",
            "NextSpeakerInput",
            "NoValidSpeakerError",
            "SceneDirectorHints",
            "SceneDirectorInput",
            "TurnEntry",
            "build_dyad_state_provider",
            "classify_scene",
            "last_non_whyze_speaker",
            "select_next_speaker",
        }
        from starry_lyfe import scene as scene_pkg

        for name in names:
            assert hasattr(scene_pkg, name), f"scene package missing {name}"


class TestComposition:
    def test_classify_then_select_smoke(self) -> None:
        """Full round-trip: classify → feed SceneState into next-speaker."""
        scene_state = classify_scene(
            SceneDirectorInput(
                user_message="Adelia and Bina and I are in the kitchen",
                present_characters=["adelia", "bina"],
            )
        )
        decision = select_next_speaker(
            NextSpeakerInput(
                scene_state=scene_state,
                turn_history=[],
                dyad_state_provider=DictDyadStateProvider({}),
            )
        )
        assert decision.speaker in {"adelia", "bina"}
        assert isinstance(decision, NextSpeakerDecision)

    def test_classify_then_select_with_absent_dyad(self) -> None:
        """A recalled-dyad scene: Reina absent but mentioned. Classifier
        should surface the recalled_dyad; next-speaker should still pick
        from present_characters only."""
        scene_state = classify_scene(
            SceneDirectorInput(
                user_message="adelia and i are in the kitchen, thinking about reina",
                present_characters=["adelia"],
            )
        )
        assert "reina" in scene_state.recalled_dyads
        decision = select_next_speaker(
            NextSpeakerInput(
                scene_state=scene_state,
                turn_history=[],
                dyad_state_provider=DictDyadStateProvider({}),
            )
        )
        assert decision.speaker == "adelia"  # only present candidate

    def test_hints_forced_scene_type_propagates(self) -> None:
        """Hints set at classifier time flow into the final SceneState."""
        from starry_lyfe.context.types import SceneType

        scene_state = classify_scene(
            SceneDirectorInput(
                user_message="hanging out",
                present_characters=["adelia", "bina"],
                hints=SceneDirectorHints(forced_scene_type=SceneType.CONFLICT),
            )
        )
        assert scene_state.scene_type == SceneType.CONFLICT


class TestTurnHistoryHelper:
    def test_last_non_whyze_speaker_with_whyze_only(self) -> None:
        assert last_non_whyze_speaker([]) is None
        history = [TurnEntry(speaker="whyze", addressed_to="adelia", turn_index=1)]
        assert last_non_whyze_speaker(history) is None

    def test_last_non_whyze_speaker_finds_latest(self) -> None:
        history = [
            TurnEntry(speaker="adelia", addressed_to="whyze", turn_index=1),
            TurnEntry(speaker="bina", addressed_to="whyze", turn_index=2),
            TurnEntry(speaker="whyze", addressed_to="adelia", turn_index=3),
        ]
        assert last_non_whyze_speaker(history) == "bina"


class TestProtocolTyping:
    def test_dyad_state_provider_is_protocol(self) -> None:
        """DictDyadStateProvider should satisfy DyadStateProvider at type-check
        time; at runtime we just confirm it's usable."""
        provider: DyadStateProvider = DictDyadStateProvider({})
        assert provider.get("adelia", "bina") is None

    def test_build_dyad_state_provider_returns_concrete_provider(self) -> None:
        provider = build_dyad_state_provider([])
        assert isinstance(provider, DictDyadStateProvider)
