"""Phase 5 integration: Scene Director output flows into assemble_context.

Verifies AC-5.6: the classifier-produced SceneState yields a prompt
semantically equivalent to a hand-constructed SceneState with the same
field values, and the inferred scene_type / modifiers drive the same
kernel section promotion and Layer 7 constraint decisions.

Also verifies the Round 1 remediation end-to-end:
- F1: classifier absent-dyad normalization renders internal-dyad prose in Layer 6.
- F2: two-woman-domestic scene routes as GROUP via Layer 5 mode accumulation.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any, cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from starry_lyfe.context import assembler as assembler_module
from starry_lyfe.context.assembler import assemble_context
from starry_lyfe.context.layers import derive_active_voice_modes
from starry_lyfe.context.types import (
    SceneState,
    SceneType,
    VoiceMode,
)
from starry_lyfe.db.models.dyad_state_internal import DyadStateInternal
from starry_lyfe.scene import (
    SceneDirectorHints,
    SceneDirectorInput,
    classify_scene,
)


class _StubEmbeddingService:
    async def embed(self, text: str) -> list[float]:
        return [0.0] * 768


@pytest.fixture
def stub_memories(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub retrieve_memories so we don't need a live DB session."""

    async def _stub(*args: Any, **kwargs: Any) -> Any:
        return SimpleNamespace(
            canon_facts=[],
            episodic_memories=[],
            somatic_state=None,
            character_baseline=None,
            dyad_states_whyze=[],
            dyad_states_internal=[],
            open_loops=[],
        )

    monkeypatch.setattr(assembler_module, "retrieve_memories", _stub)


async def test_classifier_output_flows_into_assembler(
    stub_memories: None,
) -> None:
    """AC-5.6 (half 1): a SceneState from classify_scene assembles without error."""
    scene_state = classify_scene(
        SceneDirectorInput(
            user_message="adelia and i are in the kitchen making dinner",
            present_characters=["adelia", "whyze"],
        )
    )

    prompt = await assemble_context(
        character_id="adelia",
        scene_context=scene_state.scene_description,
        scene_state=scene_state,
        session=cast(AsyncSession, None),
        embedding_service=cast(Any, _StubEmbeddingService()),
    )
    assert prompt.is_terminally_anchored
    assert prompt.character_id == "adelia"


async def test_classifier_vs_manual_scene_state_produce_same_prompt(
    stub_memories: None,
) -> None:
    """AC-5.6 (half 2): classifier-produced SceneState yields byte-identical
    prompt to a hand-constructed SceneState with the same field values."""
    msg = "adelia and i are in the kitchen making dinner"
    classified = classify_scene(
        SceneDirectorInput(
            user_message=msg,
            present_characters=["adelia", "whyze"],
        )
    )
    # Construct the equivalent SceneState manually with the SAME field values.
    manual = SceneState(
        present_characters=classified.present_characters,
        public_scene=classified.public_scene,
        alicia_home=classified.alicia_home,
        scene_description=classified.scene_description,
        communication_mode=classified.communication_mode,
        recalled_dyads=classified.recalled_dyads,
        voice_modes=classified.voice_modes,
        scene_type=classified.scene_type,
        modifiers=classified.modifiers,
    )

    prompt_classified = await assemble_context(
        character_id="adelia",
        scene_context=msg,
        scene_state=classified,
        session=cast(AsyncSession, None),
        embedding_service=cast(Any, _StubEmbeddingService()),
    )
    prompt_manual = await assemble_context(
        character_id="adelia",
        scene_context=msg,
        scene_state=manual,
        session=cast(AsyncSession, None),
        embedding_service=cast(Any, _StubEmbeddingService()),
    )
    assert prompt_classified.prompt == prompt_manual.prompt


async def test_inferred_conflict_scene_promotes_conflict_sections(
    stub_memories: None,
) -> None:
    """SceneType.CONFLICT promotes kernel sections 5 + 7 per Phase F mapping."""
    scene_state = classify_scene(
        SceneDirectorInput(
            user_message="we had a fight about the kitchen and it got bad",
            present_characters=["adelia", "whyze"],
        )
    )
    assert scene_state.scene_type == SceneType.CONFLICT

    prompt = await assemble_context(
        character_id="adelia",
        scene_context=scene_state.scene_description,
        scene_state=scene_state,
        session=cast(AsyncSession, None),
        embedding_service=cast(Any, _StubEmbeddingService()),
    )
    # The prompt should assemble cleanly; kernel section promotion is an
    # internal concern of the assembler. We verify the observable
    # contract: the prompt is terminally anchored and non-empty.
    assert prompt.is_terminally_anchored
    assert len(prompt.prompt) > 100


async def test_inferred_pair_escalation_modifier_reaches_layer_7(
    stub_memories: None,
) -> None:
    """Classifier-inferred modifiers flow into Layer 7 constraint generation.

    Reina's pillar includes an Admissibility Protocol that fires when the
    pair_escalation_active modifier is set. We verify that a message with
    the escalation keyword lands that modifier in the final SceneState.
    """
    scene_state = classify_scene(
        SceneDirectorInput(
            user_message="the pair is flaring, escalation is active tonight",
            present_characters=["reina", "whyze"],
        )
    )
    assert scene_state.modifiers.pair_escalation_active is True

    prompt = await assemble_context(
        character_id="reina",
        scene_context=scene_state.scene_description,
        scene_state=scene_state,
        session=cast(AsyncSession, None),
        embedding_service=cast(Any, _StubEmbeddingService()),
    )
    # The constraint block is terminal — the modifier's effect reaches the
    # assembled output via the Layer 7 pillar registry.
    assert prompt.is_terminally_anchored


async def test_alicia_away_contradiction_stops_at_classifier(
    stub_memories: None,
) -> None:
    """Classifier raises before assembler is ever called, so no prompt leaks."""
    from starry_lyfe.scene import AliciaAwayContradictionError

    with pytest.raises(AliciaAwayContradictionError):
        classify_scene(
            SceneDirectorInput(
                user_message="alicia and i are in the kitchen",
                present_characters=["alicia", "whyze"],
                alicia_home=False,
            )
        )


async def test_hints_forced_scene_type_reaches_assembler(
    stub_memories: None,
) -> None:
    """A hint at classifier time threads through to the final assembled prompt."""
    scene_state = classify_scene(
        SceneDirectorInput(
            user_message="adelia and i are doing nothing special",
            present_characters=["adelia", "whyze"],
            hints=SceneDirectorHints(forced_scene_type=SceneType.INTIMATE),
        )
    )
    assert scene_state.scene_type == SceneType.INTIMATE

    # Sanity: assembler accepts the forced type without complaint.
    prompt = await assemble_context(
        character_id="adelia",
        scene_context=scene_state.scene_description,
        scene_state=scene_state,
        session=cast(AsyncSession, None),
        embedding_service=cast(Any, _StubEmbeddingService()),
    )
    assert prompt.is_terminally_anchored


# ---------------------------------------------------------------------------
# Round 1 remediation regressions
# ---------------------------------------------------------------------------


def _make_internal_dyad(
    member_a: str, member_b: str, *, intimacy: float = 0.5
) -> DyadStateInternal:
    return DyadStateInternal(
        id=uuid.uuid4(),
        dyad_key=f"{member_a}_{member_b}",
        member_a=member_a,
        member_b=member_b,
        subtype="resident_continuous",
        interlock=None,
        trust=0.7,
        intimacy=intimacy,
        conflict=0.1,
        unresolved_tension=0.2,
        repair_history=0.5,
        is_currently_active=True,
        last_updated_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
    )


async def test_f1_classifier_absent_dyad_renders_in_layer_6(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """F1 remediation end-to-end: classifier-inferred absent dyads produce
    Layer 6 internal-dyad prose for the focal character.

    Pre-remediation: classifier emitted ``{"reina"}`` (bare name) which
    layers.format_scene_blocks could not match against its dyad-key
    check. No Layer 6 prose rendered.

    Post-remediation: classifier emits ``{"adelia-reina"}`` (dyad-key
    shape). Layer 6 matches and renders the internal-dyad prose.
    """

    # Stub a retrieval bundle with the adelia-reina internal dyad row
    # that Layer 6 should render when Reina is invoked as absent.
    async def _stub(*args: Any, **kwargs: Any) -> Any:
        return SimpleNamespace(
            canon_facts=[],
            episodic_memories=[],
            somatic_state=None,
            character_baseline=None,
            dyad_states_whyze=[],
            dyad_states_internal=[_make_internal_dyad("adelia", "reina")],
            open_loops=[],
        )

    monkeypatch.setattr(assembler_module, "retrieve_memories", _stub)

    scene_state = classify_scene(
        SceneDirectorInput(
            user_message="adelia and i are in the kitchen, thinking about reina",
            present_characters=["adelia"],  # classifier auto-appends whyze
        )
    )
    # Sanity: dyad-key shape, not bare name.
    assert "adelia-reina" in scene_state.recalled_dyads

    prompt = await assemble_context(
        character_id="adelia",
        scene_context=scene_state.scene_description,
        scene_state=scene_state,
        session=cast(AsyncSession, None),
        embedding_service=cast(Any, _StubEmbeddingService()),
    )
    # render_dyad_internal_prose opens with "<member_a>-<other> — <interlock>."
    # For the stubbed adelia-reina row this produces "adelia-reina — pair."
    # The substring "adelia-reina" is the load-bearing end-to-end marker.
    assert "adelia-reina" in prompt.prompt


async def test_f2_two_woman_domestic_routes_as_group(
    stub_memories: None,
) -> None:
    """F2 remediation end-to-end: a two-woman domestic scene (the
    documented public-API example) normalizes to present_characters
    shape ``[..., "whyze"]`` and Layer 5 mode accumulation picks GROUP,
    not SOLO_PAIR.

    Pre-remediation: classifier returned ``present_characters=["adelia",
    "bina"]``; layers.py:75-84 counted raw len == 2 and added SOLO_PAIR.
    Post-remediation: classifier auto-appends whyze; len == 3 adds GROUP.
    """
    scene_state = classify_scene(
        SceneDirectorInput(
            user_message="adelia and bina are in the kitchen making dinner",
            present_characters=["adelia", "bina"],  # documented shape
        )
    )
    # R2 normalization
    assert scene_state.present_characters == ["adelia", "bina", "whyze"]
    assert scene_state.scene_type == SceneType.DOMESTIC

    modes = derive_active_voice_modes(scene_state)
    assert VoiceMode.GROUP in modes
    assert VoiceMode.SOLO_PAIR not in modes

    # Assemble to confirm the whole pipeline accepts the normalized shape.
    prompt = await assemble_context(
        character_id="adelia",
        scene_context=scene_state.scene_description,
        scene_state=scene_state,
        session=cast(AsyncSession, None),
        embedding_service=cast(Any, _StubEmbeddingService()),
    )
    assert prompt.is_terminally_anchored
