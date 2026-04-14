"""Phase 5: unit tests for select_next_speaker scoring.

Tests assert RELATIVE score differentials (not absolute values) so minor
weight tuning in ``next_speaker.py`` does not churn the suite. The one
exception is hard-gate zero-out cases where the score is required to be
exactly 0.0 by contract.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from starry_lyfe.context.types import (
    CommunicationMode,
    SceneState,
)
from starry_lyfe.db.models.dyad_state_internal import DyadStateInternal
from starry_lyfe.scene import (
    DictDyadStateProvider,
    NextSpeakerInput,
    NoValidSpeakerError,
    TurnEntry,
    build_dyad_state_provider,
    select_next_speaker,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_dyad(
    member_a: str,
    member_b: str,
    *,
    intimacy: float = 0.5,
    unresolved_tension: float = 0.2,
    trust: float = 0.7,
    conflict: float = 0.1,
    repair_history: float = 0.5,
    is_active: bool = True,
) -> DyadStateInternal:
    return DyadStateInternal(
        id=uuid.uuid4(),
        dyad_key=f"{member_a}_{member_b}",
        member_a=member_a,
        member_b=member_b,
        subtype="resident_continuous",
        interlock=None,
        trust=trust,
        intimacy=intimacy,
        conflict=conflict,
        unresolved_tension=unresolved_tension,
        repair_history=repair_history,
        is_currently_active=is_active,
        last_updated_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
    )


def _empty_provider() -> DictDyadStateProvider:
    return DictDyadStateProvider({})


def _scene(
    present: list[str],
    *,
    alicia_home: bool = True,
    comm: CommunicationMode = CommunicationMode.IN_PERSON,
) -> SceneState:
    return SceneState(
        present_characters=present,
        alicia_home=alicia_home,
        communication_mode=comm,
    )


# ---------------------------------------------------------------------------
# Basic argmax + tiebreak
# ---------------------------------------------------------------------------


class TestArgmaxAndTiebreak:
    def test_single_candidate_chosen(self) -> None:
        decision = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(["adelia"]),
                turn_history=[],
                dyad_state_provider=_empty_provider(),
            )
        )
        assert decision.speaker == "adelia"

    def test_stable_tiebreak_order(self) -> None:
        """Two candidates, identical scores → canonical order wins."""
        decision = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(["bina", "adelia"]),  # reversed input order
                turn_history=[],
                dyad_state_provider=_empty_provider(),
            )
        )
        # Adelia is first in _STABLE_TIEBREAK_ORDER → wins on tie.
        assert decision.speaker == "adelia"

    def test_whyze_excluded_from_candidates(self) -> None:
        decision = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(["adelia", "whyze"]),
                turn_history=[],
                dyad_state_provider=_empty_provider(),
            )
        )
        assert decision.speaker == "adelia"
        assert "whyze" not in decision.scores

    def test_reasons_trace_populated(self) -> None:
        decision = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(["adelia"]),
                turn_history=[],
                dyad_state_provider=_empty_provider(),
            )
        )
        assert decision.reasons
        assert any("base" in r for r in decision.reasons)


# ---------------------------------------------------------------------------
# Hard gates
# ---------------------------------------------------------------------------


class TestHardGates:
    def test_alicia_away_in_person_scores_zero(self) -> None:
        """AC-5.9: alicia away + IN_PERSON → score 0.0 exactly."""
        decision = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(
                    ["adelia", "alicia"],
                    alicia_home=False,
                    comm=CommunicationMode.IN_PERSON,
                ),
                turn_history=[],
                dyad_state_provider=_empty_provider(),
            )
        )
        assert decision.scores["alicia"] == 0.0
        assert decision.speaker == "adelia"

    def test_alicia_away_phone_mode_not_zeroed(self) -> None:
        decision = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(
                    ["alicia"],
                    alicia_home=False,
                    comm=CommunicationMode.PHONE,
                ),
                turn_history=[],
                dyad_state_provider=_empty_provider(),
            )
        )
        assert decision.scores["alicia"] > 0.0
        assert decision.speaker == "alicia"

    def test_rule_of_one_already_spoken_scores_zero(self) -> None:
        """AC-5.10: candidate in in_turn_already_spoken → score 0.0."""
        decision = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(["adelia", "bina"]),
                turn_history=[],
                dyad_state_provider=_empty_provider(),
                in_turn_already_spoken=["adelia"],
            )
        )
        assert decision.scores["adelia"] == 0.0
        assert decision.speaker == "bina"

    def test_all_zeroed_raises(self) -> None:
        with pytest.raises(NoValidSpeakerError):
            select_next_speaker(
                NextSpeakerInput(
                    scene_state=_scene(["adelia"]),
                    turn_history=[],
                    dyad_state_provider=_empty_provider(),
                    in_turn_already_spoken=["adelia"],  # only candidate zeroed
                )
            )

    def test_no_candidates_raises(self) -> None:
        with pytest.raises(NoValidSpeakerError):
            select_next_speaker(
                NextSpeakerInput(
                    scene_state=_scene(["whyze"]),  # only whyze
                    turn_history=[],
                    dyad_state_provider=_empty_provider(),
                )
            )


# ---------------------------------------------------------------------------
# Talk-to-Each-Other Mandate
# ---------------------------------------------------------------------------


class TestTalkToEachOther:
    def test_two_whyze_chain_rewards_chain_breaker(self) -> None:
        """AC-5.7: last 2 turns addressed Whyze → chain-breaker reward."""
        # Baseline: no history
        base = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(["adelia", "bina"]),
                turn_history=[],
                dyad_state_provider=_empty_provider(),
            )
        )
        # Trigger: last 2 turns addressed whyze
        trigger = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(["adelia", "bina"]),
                turn_history=[
                    TurnEntry(speaker="adelia", addressed_to="whyze", turn_index=1),
                    TurnEntry(speaker="bina", addressed_to="whyze", turn_index=2),
                ],
                dyad_state_provider=_empty_provider(),
            )
        )
        # Differential: the trigger score for ANY candidate should be higher
        # than the baseline score (reward fires because another woman exists).
        assert trigger.scores["adelia"] >= base.scores["adelia"] + 0.20

    def test_solo_woman_cannot_break_chain_is_penalized(self) -> None:
        """Only-woman present → chain penalty, no reward."""
        base = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(["adelia"]),
                turn_history=[],
                dyad_state_provider=_empty_provider(),
            )
        )
        penalty = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(["adelia"]),
                turn_history=[
                    TurnEntry(speaker="adelia", addressed_to="whyze", turn_index=1),
                    TurnEntry(speaker="whyze", addressed_to="adelia", turn_index=2),
                ],
                dyad_state_provider=_empty_provider(),
            )
        )
        assert penalty.scores["adelia"] < base.scores["adelia"]

    def test_woman_to_woman_chain_rewarded(self) -> None:
        """AC-5.8: last turn was w2w → continuation reward."""
        base = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(["adelia", "bina"]),
                turn_history=[],
                dyad_state_provider=_empty_provider(),
            )
        )
        w2w = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(["adelia", "bina"]),
                turn_history=[
                    TurnEntry(speaker="adelia", addressed_to="bina", turn_index=1),
                ],
                dyad_state_provider=_empty_provider(),
            )
        )
        # Bina (continues the w2w) should score higher than baseline.
        assert w2w.scores["bina"] > base.scores["bina"]


# ---------------------------------------------------------------------------
# Dyad-state fitness
# ---------------------------------------------------------------------------


class TestDyadStateFitness:
    def test_high_intimacy_increases_score(self) -> None:
        """AC-5.11: dyad-state fitness influences scores."""
        low = DictDyadStateProvider(
            {frozenset({"adelia", "bina"}): _make_dyad("adelia", "bina", intimacy=0.0, unresolved_tension=0.0)}
        )
        high = DictDyadStateProvider(
            {frozenset({"adelia", "bina"}): _make_dyad("adelia", "bina", intimacy=1.0, unresolved_tension=0.0)}
        )
        low_decision = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(["adelia", "bina"]),
                turn_history=[],
                dyad_state_provider=low,
            )
        )
        high_decision = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(["adelia", "bina"]),
                turn_history=[],
                dyad_state_provider=high,
            )
        )
        assert high_decision.scores["adelia"] > low_decision.scores["adelia"]

    def test_tension_also_boosts_score(self) -> None:
        """Tension is narratively productive — it raises score like intimacy does."""
        calm = DictDyadStateProvider(
            {frozenset({"adelia", "bina"}): _make_dyad("adelia", "bina", intimacy=0.5, unresolved_tension=0.0)}
        )
        tense = DictDyadStateProvider(
            {frozenset({"adelia", "bina"}): _make_dyad("adelia", "bina", intimacy=0.5, unresolved_tension=1.0)}
        )
        calm_decision = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(["adelia", "bina"]),
                turn_history=[],
                dyad_state_provider=calm,
            )
        )
        tense_decision = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(["adelia", "bina"]),
                turn_history=[],
                dyad_state_provider=tense,
            )
        )
        assert tense_decision.scores["adelia"] > calm_decision.scores["adelia"]

    def test_dyad_lookup_is_order_independent(self) -> None:
        """Provider indexed by frozenset → (a,b) and (b,a) both hit."""
        provider = DictDyadStateProvider(
            {frozenset({"adelia", "bina"}): _make_dyad("adelia", "bina", intimacy=0.9)}
        )
        # The scoring loop asks provider.get(candidate, other); flip the
        # candidate order by flipping present_characters.
        a = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(["adelia", "bina"]),
                turn_history=[],
                dyad_state_provider=provider,
            )
        )
        b = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(["bina", "adelia"]),
                turn_history=[],
                dyad_state_provider=provider,
            )
        )
        # Same dyad, same intimacy contribution → same final scores.
        assert a.scores == b.scores

    def test_missing_dyad_returns_none_no_crash(self) -> None:
        """Provider returns None for unknown pair → scoring continues."""
        provider = DictDyadStateProvider({})  # empty
        decision = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(["adelia", "bina"]),
                turn_history=[],
                dyad_state_provider=provider,
            )
        )
        assert decision.speaker in {"adelia", "bina"}


# ---------------------------------------------------------------------------
# Recency suppression
# ---------------------------------------------------------------------------


class TestRecencySuppression:
    def test_last_non_whyze_speaker_penalized(self) -> None:
        """Candidate who just spoke non-whyze gets a small penalty."""
        decision = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(["adelia", "bina"]),
                turn_history=[
                    TurnEntry(speaker="adelia", addressed_to="bina", turn_index=1),
                ],
                dyad_state_provider=_empty_provider(),
            )
        )
        # Adelia just spoke → bina should win (also got w2w continuation
        # reward), so the composite effect is bina ahead of adelia.
        assert decision.speaker == "bina"


# ---------------------------------------------------------------------------
# build_dyad_state_provider adapter
# ---------------------------------------------------------------------------


class TestBuildDyadStateProvider:
    def test_wraps_list_of_rows(self) -> None:
        rows = [
            _make_dyad("adelia", "bina", intimacy=0.8),
            _make_dyad("bina", "reina", intimacy=0.9),
        ]
        provider = build_dyad_state_provider(rows)
        assert provider.get("adelia", "bina") is rows[0]
        assert provider.get("bina", "adelia") is rows[0]  # order-independent
        assert provider.get("bina", "reina") is rows[1]
        assert provider.get("adelia", "reina") is None

    def test_empty_list_produces_empty_provider(self) -> None:
        provider = build_dyad_state_provider([])
        assert provider.get("adelia", "bina") is None


# ---------------------------------------------------------------------------
# Activity-context salience (R3 remediation / F3)
# ---------------------------------------------------------------------------


class TestActivityContext:
    def test_candidate_named_in_scene_description_boosted(self) -> None:
        """R3 (F3): scene_state.scene_description is read as activity context.

        A scene whose description names a candidate should boost that
        candidate's score relative to an otherwise-identical scene with
        a neutral description.
        """
        neutral = SceneState(
            present_characters=["adelia", "bina"],
            scene_description="quiet evening",
            communication_mode=CommunicationMode.IN_PERSON,
        )
        named_adelia = SceneState(
            present_characters=["adelia", "bina"],
            scene_description="Adelia is arranging lanterns",
            communication_mode=CommunicationMode.IN_PERSON,
        )
        neutral_decision = select_next_speaker(
            NextSpeakerInput(
                scene_state=neutral,
                turn_history=[],
                dyad_state_provider=_empty_provider(),
            )
        )
        named_decision = select_next_speaker(
            NextSpeakerInput(
                scene_state=named_adelia,
                turn_history=[],
                dyad_state_provider=_empty_provider(),
            )
        )
        assert named_decision.scores["adelia"] > neutral_decision.scores["adelia"]

    def test_candidate_named_in_activity_context_boosted(self) -> None:
        """R3 (F3): explicit activity_context field is read alongside
        scene_description. Phase 6 Dreams will source longer activity
        narratives here."""
        neutral = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(["adelia", "bina"]),
                turn_history=[],
                dyad_state_provider=_empty_provider(),
                activity_context="evening setup",
            )
        )
        salient = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(["adelia", "bina"]),
                turn_history=[],
                dyad_state_provider=_empty_provider(),
                activity_context="Bina is plating dinner at the island",
            )
        )
        assert salient.scores["bina"] > neutral.scores["bina"]

    def test_salience_differential_matches_weight(self) -> None:
        """The salience boost magnitude is roughly 0.05 — assert a lower
        bound rather than an exact equality so weight tuning does not
        churn the test."""
        base = select_next_speaker(
            NextSpeakerInput(
                scene_state=_scene(["adelia", "bina"]),
                turn_history=[],
                dyad_state_provider=_empty_provider(),
            )
        )
        boosted = select_next_speaker(
            NextSpeakerInput(
                scene_state=SceneState(
                    present_characters=["adelia", "bina"],
                    scene_description="Adelia and Bina discussing the evening",
                    communication_mode=CommunicationMode.IN_PERSON,
                ),
                turn_history=[],
                dyad_state_provider=_empty_provider(),
            )
        )
        # Both named → both boosted. Differential vs base must be positive.
        for c in ("adelia", "bina"):
            assert boosted.scores[c] > base.scores[c]

    def test_candidate_absent_from_context_not_boosted(self) -> None:
        """Candidates not named receive no salience boost."""
        decision = select_next_speaker(
            NextSpeakerInput(
                scene_state=SceneState(
                    present_characters=["adelia", "reina"],
                    scene_description="Adelia is arranging lanterns",
                    communication_mode=CommunicationMode.IN_PERSON,
                ),
                turn_history=[],
                dyad_state_provider=_empty_provider(),
            )
        )
        # Adelia named → boosted; Reina absent from description → not boosted.
        assert decision.scores["adelia"] > decision.scores["reina"]
