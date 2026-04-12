"""Gate 3 verification tests for the context assembly layer."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.context import assembler as assembler_module
from starry_lyfe.context.assembler import LAYER_MARKERS, AliciaAwayError, assemble_context
from starry_lyfe.context.budgets import (
    DEFAULT_BUDGETS,
    estimate_tokens,
    trim_text_to_budget,
    trim_to_budget,
)
from starry_lyfe.context.constraints import (
    CHARACTER_CONSTRAINTS,
    TIER_1_AXIOMS,
    build_constraint_block,
)
from starry_lyfe.context.kernel_loader import (
    KERNEL_PATHS,
    VOICE_PATHS,
    clear_kernel_cache,
    load_kernel,
    load_voice_guidance,
)
from starry_lyfe.context.layers import format_scene_blocks, format_voice_directives
from starry_lyfe.context.types import AssembledPrompt, CommunicationMode, SceneState


class _StubEmbeddingService:
    async def embed(self, text: str) -> list[float]:
        return [0.0] * 768

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * 768 for _ in texts]


def _make_bundle(character_id: str) -> Any:
    profile = {
        "adelia": {
            "full_name": "Adelia Raye",
            "epithet": "The Catalyst",
            "mbti": "ENFP-A",
            "dominant_function": "Ne",
            "pair_name": "entangled",
            "pair_classification": "asymmetrical cognitive interlock",
            "pair_mechanism": "Chaos-to-structure handoff",
            "pair_core_metaphor": "The Gravity and the Space",
            "heritage": "Valencian-Australian",
            "profession": "Pyrotechnic artist / ethical hacker",
            "response_length_range": "2-4 paragraphs",
            "dominant_function_descriptor": "energy-first, tangent-resolving ideation",
            "internal_member": "bina",
        },
        "bina": {
            "full_name": "Bina Malek",
            "epithet": "The Sentinel",
            "mbti": "ISFJ-A",
            "dominant_function": "Si",
            "pair_name": "circuit",
            "pair_classification": "structural complement",
            "pair_mechanism": "Total division of operational domains",
            "pair_core_metaphor": "The Architect and the Sentinel",
            "heritage": "Assyrian-Iranian Canadian",
            "profession": "Mechanic",
            "response_length_range": "2-4 sentences",
            "dominant_function_descriptor": "Si-dominant declarative steadiness",
            "internal_member": "reina",
        },
        "reina": {
            "full_name": "Reina Torres",
            "epithet": "The Operator",
            "mbti": "ESTP-A",
            "dominant_function": "Se",
            "pair_name": "kinetic",
            "pair_classification": "asymmetrical leverage",
            "pair_mechanism": "Temporal collision converted to engine heat",
            "pair_core_metaphor": "The Mastermind and the Operator",
            "heritage": "Barcelona Catalan-Castilian",
            "profession": "Criminal defence lawyer",
            "response_length_range": "1-3 paragraphs",
            "dominant_function_descriptor": "Se-dominant tactical presence",
            "internal_member": "bina",
        },
        "alicia": {
            "full_name": "Alicia Marin",
            "epithet": "The Solstice",
            "mbti": "ESFP-A",
            "dominant_function": "Se",
            "pair_name": "solstice",
            "pair_classification": "structural complement",
            "pair_mechanism": "Inferior-function gift exchange",
            "pair_core_metaphor": "The Duality",
            "heritage": "Argentine",
            "profession": "Operative",
            "response_length_range": "Short-to-medium",
            "dominant_function_descriptor": "Se-dominant somatic co-regulation",
            "internal_member": "adelia",
        },
    }[character_id]

    baseline = SimpleNamespace(
        full_name=profile["full_name"],
        epithet=profile["epithet"],
        mbti=profile["mbti"],
        dominant_function=profile["dominant_function"],
        pair_name=profile["pair_name"],
        pair_classification=profile["pair_classification"],
        pair_mechanism=profile["pair_mechanism"],
        pair_core_metaphor=profile["pair_core_metaphor"],
        heritage=profile["heritage"],
        profession=profile["profession"],
        voice_params={
            "response_length_range": profile["response_length_range"],
            "dominant_function_descriptor": profile["dominant_function_descriptor"],
        },
    )
    return SimpleNamespace(
        canon_facts=[
            SimpleNamespace(fact_key=f"fact_{i}", fact_value="value")
            for i in range(24)
        ],
        character_baseline=baseline,
        dyad_states_whyze=[
            SimpleNamespace(
                pair_name=baseline.pair_name,
                trust=0.80,
                intimacy=0.65,
                conflict=0.15,
                unresolved_tension=0.25,
            )
        ],
        dyad_states_internal=[
            SimpleNamespace(
                member_a=character_id,
                member_b=profile["internal_member"],
                interlock="anchor_dynamic",
                trust=0.72,
                intimacy=0.55,
                conflict=0.20,
            )
        ],
        episodic_memories=[
            SimpleNamespace(
                event_summary=f"Memory summary {i} " * 6,
                emotional_temperature=0.30 + (i * 0.05),
            )
            for i in range(8)
        ],
        open_loops=[
            SimpleNamespace(urgency="high", loop_summary="Follow up on the kitchen conversation."),
            SimpleNamespace(urgency="medium", loop_summary="Revisit the unresolved shop scheduling detail."),
        ],
        somatic_state=SimpleNamespace(
            character_id=character_id,
            fatigue=0.42,
            stress_residue=0.18,
            injury_residue=0.00,
            active_protocols=[],
        ),
    )

# --- Constraint block structure tests ---


def test_tier_1_axioms_count() -> None:
    """All 7 Tier 1 axioms are present."""
    assert len(TIER_1_AXIOMS) == 7


def test_all_four_characters_have_constraint_pillars() -> None:
    """Each character has a dedicated constraint pillar."""
    assert set(CHARACTER_CONSTRAINTS.keys()) == {"adelia", "bina", "reina", "alicia"}


def test_all_four_characters_have_kernel_paths() -> None:
    """Each character has a kernel file path defined."""
    assert set(KERNEL_PATHS.keys()) == {"adelia", "bina", "reina", "alicia"}


def test_all_four_characters_have_voice_paths() -> None:
    """Each character has a voice file path defined."""
    assert set(VOICE_PATHS.keys()) == {"adelia", "bina", "reina", "alicia"}


def test_constraint_block_contains_all_tier_1_axioms() -> None:
    """The constraint block includes all 7 Tier 1 axioms."""
    scene = SceneState(present_characters=["adelia"])
    block = build_constraint_block("adelia", scene)
    for axiom in TIER_1_AXIOMS:
        assert axiom in block


def test_adelia_constraints_mention_entangled_pair() -> None:
    """Adelia's constraint block mentions Entangled Pair, not Circuit Pair."""
    scene = SceneState(present_characters=["adelia"])
    block = build_constraint_block("adelia", scene)
    assert "ENTANGLED PAIR" in block
    assert "CIRCUIT PAIR" not in block


def test_bina_constraints_mention_circuit_pair() -> None:
    """Bina's constraint block mentions Circuit Pair, not Entangled Pair."""
    scene = SceneState(present_characters=["bina"])
    block = build_constraint_block("bina", scene)
    assert "CIRCUIT PAIR" in block
    assert "ENTANGLED PAIR" not in block


def test_reina_constraints_mention_admissibility() -> None:
    """Reina's constraints include admissibility frame."""
    scene = SceneState(present_characters=["reina"])
    block = build_constraint_block("reina", scene)
    assert "ADMISSIBILITY" in block


def test_alicia_constraints_mention_presence_conditional() -> None:
    """Alicia's constraints include presence-conditional language."""
    scene = SceneState(present_characters=["alicia"])
    block = build_constraint_block("alicia", scene)
    assert "PRESENCE-CONDITIONAL" in block


def test_children_gate_activates() -> None:
    """Children present activates the gate directive."""
    scene = SceneState(present_characters=["adelia"], children_present=True)
    block = build_constraint_block("adelia", scene)
    assert "ACTIVE GATE" in block


def test_children_gate_inactive_by_default() -> None:
    """No children = no gate directive."""
    scene = SceneState(present_characters=["adelia"], children_present=False)
    block = build_constraint_block("adelia", scene)
    assert "ACTIVE GATE" not in block


def test_talk_to_each_other_mandate_multi_character() -> None:
    """Multi-character scenes include the Talk-to-Each-Other mandate."""
    scene = SceneState(present_characters=["adelia", "bina", "reina"])
    block = build_constraint_block("adelia", scene)
    assert "TALK-TO-EACH-OTHER" in block


def test_talk_to_each_other_mandate_absent_solo() -> None:
    """Solo scenes do not include the mandate."""
    scene = SceneState(present_characters=["adelia"])
    block = build_constraint_block("adelia", scene)
    assert "TALK-TO-EACH-OTHER" not in block


def test_non_echo_instruction_in_constraint_block() -> None:
    """The non-echo instruction is embedded within the constraint block."""
    scene = SceneState(present_characters=["adelia"])
    block = build_constraint_block("adelia", scene)
    assert "Never output them" in block


def test_em_dash_ban_in_hygiene_directives() -> None:
    """Output hygiene includes em-dash ban."""
    scene = SceneState(present_characters=["adelia"])
    block = build_constraint_block("adelia", scene)
    assert "em-dash" in block.lower() or "en-dash" in block.lower()


# --- Token budget tests ---


def test_estimate_tokens_basic() -> None:
    """Token estimation produces reasonable results."""
    text = "This is a test sentence with eight words total."
    tokens = estimate_tokens(text)
    assert 8 <= tokens <= 20


def test_trim_to_budget_drops_excess() -> None:
    """Trim drops items that exceed budget."""
    items = ["short", "another short one", "a much longer text that takes more tokens"]
    result = trim_to_budget(items, 5)
    assert len(result) <= len(items)
    assert len(result) >= 1


def test_trim_to_budget_keeps_order() -> None:
    """Trim preserves priority order (first items kept)."""
    items = ["first priority", "second priority", "third priority"]
    result = trim_to_budget(items, 10)
    if len(result) >= 2:
        assert result[0] == "first priority"
        assert result[1] == "second priority"


def test_trim_text_to_budget_never_exceeds_limit() -> None:
    """Single-text trimming produces output that fits within budget."""
    text = "word " * 400
    trimmed = trim_text_to_budget(text, 40, "[Trimmed.]")
    assert estimate_tokens(trimmed) <= 40


# --- AssembledPrompt structural tests ---


def test_assembled_prompt_terminal_anchoring_structural() -> None:
    """AssembledPrompt.is_terminally_anchored checks actual prompt body."""
    good_prompt = AssembledPrompt(
        prompt="<PERSONA_KERNEL>\ntest\n</PERSONA_KERNEL>\n\n<CONSTRAINTS>\ntest\n</CONSTRAINTS>",
        character_id="adelia",
        layers=[],
        total_tokens=100,
        constraint_block_position="terminal",
    )
    assert good_prompt.is_terminally_anchored

    # A prompt with trailing content after CONSTRAINTS should fail
    bad_prompt = AssembledPrompt(
        prompt="<CONSTRAINTS>\ntest\n</CONSTRAINTS>\n\n[SYSTEM: extra stuff]",
        character_id="adelia",
        layers=[],
        total_tokens=100,
        constraint_block_position="terminal",
    )
    assert not bad_prompt.is_terminally_anchored


def test_layer_markers_cover_all_seven_layers() -> None:
    """All 7 layer markers are defined."""
    assert set(LAYER_MARKERS.keys()) == {1, 2, 3, 4, 5, 6, 7}


def test_constraint_block_differs_per_character() -> None:
    """Each character's constraint block has unique content."""
    scene = SceneState(present_characters=["adelia", "bina"])
    adelia_block = build_constraint_block("adelia", scene)
    bina_block = build_constraint_block("bina", scene)
    # Tier 1 axioms are shared, but character pillars differ
    assert "ENTANGLED PAIR" in adelia_block
    assert "CIRCUIT PAIR" in bina_block
    assert "ENTANGLED PAIR" not in bina_block
    assert "CIRCUIT PAIR" not in adelia_block


def test_scene_state_rejects_unknown_communication_mode() -> None:
    """Communication mode must be one of the canonical allowed values."""
    with pytest.raises(ValueError):
        SceneState(communication_mode=cast(Any, "sms"))


def test_load_voice_guidance_strips_raw_msty_artifacts() -> None:
    """Backend voice guidance must exclude Msty instructions and raw few-shot blocks."""
    clear_kernel_cache()
    guidance = load_voice_guidance("bina")
    assert guidance is not None
    joined = "\n".join(guidance)
    assert "Msty Persona Studio" not in joined
    assert "**User:**" not in joined
    assert "**Assistant:**" not in joined


def test_bina_kernel_uses_malek_and_circuit_pair() -> None:
    """Bina's runtime kernel should carry the corrected family and pair names."""
    clear_kernel_cache()
    kernel = load_kernel("bina", budget=4000)
    assert "Bahadori" not in kernel
    assert "Citadel Pair" not in kernel
    assert "Circuit Pair" in kernel
    assert "Farhad and Shirin Malek" in kernel


async def test_assemble_context_real_output_is_budgeted_and_backend_safe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """assemble_context should produce a terminally anchored, budgeted, backend-safe prompt."""

    async def stub_retrieve_memories(*args: Any, **kwargs: Any) -> Any:
        return _make_bundle("bina")

    monkeypatch.setattr(assembler_module, "retrieve_memories", stub_retrieve_memories)
    clear_kernel_cache()

    prompt = await assemble_context(
        character_id="bina",
        scene_context="Bina is in the kitchen after the shop closes.",
        scene_state=SceneState(
            present_characters=["bina", "whyze"],
            scene_description="Kitchen after the shop closes; quiet house, evening cleanup.",
            communication_mode=CommunicationMode.IN_PERSON,
        ),
        session=cast(AsyncSession, None),
        embedding_service=_StubEmbeddingService(),
    )

    assert prompt.is_terminally_anchored
    assert prompt.prompt.rstrip().endswith("</CONSTRAINTS>")
    assert "Current scene: Kitchen after the shop closes; quiet house, evening cleanup." in prompt.prompt
    assert "Current activity: Kitchen after the shop closes; quiet house, evening cleanup." in prompt.prompt
    assert "Msty Persona Studio" not in prompt.prompt
    assert "**User:**" not in prompt.prompt
    assert "**Assistant:**" not in prompt.prompt

    from starry_lyfe.context.budgets import resolve_kernel_budget

    layer_budgets = {
        1: resolve_kernel_budget("bina"),
        2: DEFAULT_BUDGETS.canon_facts,
        3: DEFAULT_BUDGETS.episodic,
        4: DEFAULT_BUDGETS.somatic,
        5: DEFAULT_BUDGETS.voice,
        6: DEFAULT_BUDGETS.scene,
        7: DEFAULT_BUDGETS.constraints,
    }
    for layer in prompt.layers:
        assert layer.estimated_tokens <= layer_budgets[layer.layer_number]


async def test_assemble_context_blocks_away_alicia_in_person(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Alicia cannot assemble for in-person scenes while away on operations."""

    async def unreachable_retrieve_memories(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("retrieve_memories should not run when Alicia is gated off")

    monkeypatch.setattr(assembler_module, "retrieve_memories", unreachable_retrieve_memories)

    with pytest.raises(AliciaAwayError):
        await assemble_context(
            character_id="alicia",
            scene_context="Alicia arrives in the kitchen.",
            scene_state=SceneState(
                present_characters=["alicia", "whyze"],
                scene_description="Main kitchen, late evening.",
                alicia_home=False,
                communication_mode=CommunicationMode.IN_PERSON,
            ),
            session=cast(AsyncSession, None),
            embedding_service=_StubEmbeddingService(),
            canon=load_all_canon(),
        )


async def test_assemble_context_allows_away_alicia_phone(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Alicia may assemble remotely while away through canonical remote modes only."""

    async def stub_retrieve_memories(*args: Any, **kwargs: Any) -> Any:
        return _make_bundle("alicia")

    monkeypatch.setattr(assembler_module, "retrieve_memories", stub_retrieve_memories)
    clear_kernel_cache()

    prompt = await assemble_context(
        character_id="alicia",
        scene_context="Alicia calls from an operation.",
        scene_state=SceneState(
            present_characters=["alicia", "whyze"],
            scene_description="A remote phone call late at night.",
            alicia_home=False,
            communication_mode=CommunicationMode.PHONE,
        ),
        session=cast(AsyncSession, None),
        embedding_service=_StubEmbeddingService(),
        canon=load_all_canon(),
    )

    assert prompt.character_id == "alicia"
    assert prompt.is_terminally_anchored


# --- Adelia conversion audit regression tests ---


def test_adelia_kernel_preserves_entangled_pair() -> None:
    """Finding 1: Adelia's compiled kernel must contain Entangled Pair section."""
    from starry_lyfe.context.kernel_loader import load_kernel

    clear_kernel_cache()
    kernel = load_kernel("adelia", budget=DEFAULT_BUDGETS.kernel)
    assert "Entangled Pair" in kernel or "entangled" in kernel.lower()
    # The pair section (§3) is Tier A priority and must survive compilation
    assert "Whyze" in kernel


def test_adelia_kernel_preserves_behavioral_tier() -> None:
    """Finding 1: Adelia's compiled kernel must contain Behavioral Tier Framework."""
    from starry_lyfe.context.kernel_loader import load_kernel

    clear_kernel_cache()
    kernel = load_kernel("adelia", budget=DEFAULT_BUDGETS.kernel)
    # §5 Behavioral Tier Framework is Tier A priority
    assert "Tier" in kernel or "behavioral" in kernel.lower()


def test_adelia_kernel_preserves_identity_surface() -> None:
    """Adelia's runtime kernel should retain biographical anchors, not only pair mechanics."""
    clear_kernel_cache()
    kernel = load_kernel("adelia", budget=DEFAULT_BUDGETS.kernel)
    assert "Valencia" in kernel
    assert "I am Adelia Raye" in kernel
    assert "## 2. Core Identity" in kernel


def test_adelia_whyze_scene_no_talk_to_each_other() -> None:
    """Finding 3: An Adelia-Whyze scene must NOT get the Talk-to-Each-Other mandate."""
    scene = SceneState(present_characters=["adelia", "whyze"])
    block = build_constraint_block("adelia", scene)
    assert "TALK-TO-EACH-OTHER" not in block


def test_talk_to_each_other_requires_two_women() -> None:
    """Finding 3: Mandate fires only when 2+ women (not counting Whyze) are present."""
    # Two women + Whyze: mandate should fire
    scene_multi = SceneState(present_characters=["adelia", "bina", "whyze"])
    block_multi = build_constraint_block("adelia", scene_multi)
    assert "TALK-TO-EACH-OTHER" in block_multi

    # One woman + Whyze: mandate should NOT fire
    scene_pair = SceneState(present_characters=["adelia", "whyze"])
    block_pair = build_constraint_block("adelia", scene_pair)
    assert "TALK-TO-EACH-OTHER" not in block_pair


def test_one_woman_plus_child_no_talk_mandate() -> None:
    """F1 regression: Gavin is a child, not a woman — no Talk-to-Each-Other mandate."""
    scene = SceneState(present_characters=["adelia", "gavin", "whyze"])
    block = build_constraint_block("adelia", scene)
    assert "TALK-TO-EACH-OTHER" not in block


async def test_recalled_dyad_included_when_other_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """F2 regression: explicit absent-member dyad recall renders in Layer 6."""
    bundle = _make_bundle("bina")

    without_recall = format_scene_blocks(
        "bina",
        bundle.dyad_states_whyze,
        bundle.dyad_states_internal,
        bundle.open_loops,
        ["bina", "whyze"],
        "Shop closed; Reina still at court.",
    )
    assert "Relationship bina-reina" not in without_recall.text

    async def stub_retrieve_memories(*args: Any, **kwargs: Any) -> Any:
        return bundle

    monkeypatch.setattr(assembler_module, "retrieve_memories", stub_retrieve_memories)
    clear_kernel_cache()

    prompt = await assemble_context(
        character_id="bina",
        scene_context="Bina thinking about Reina while Reina is still at court.",
        scene_state=SceneState(
            present_characters=["bina", "whyze"],
            scene_description="Shop closed; Reina still at court.",
            recalled_dyads={"bina-reina"},
        ),
        session=cast(AsyncSession, None),
        embedding_service=_StubEmbeddingService(),
    )
    assert "Relationship bina-reina" in prompt.prompt


# --- Phase A'' tests: communication-mode-aware pruning ---


def test_a_double_prime_1_alicia_phone_no_somatic_pillar() -> None:
    """A''1: Alicia phone-mode prompt does NOT contain somatic-first language."""
    scene = SceneState(
        present_characters=["alicia", "whyze"],
        alicia_home=True,
        communication_mode=CommunicationMode.PHONE,
    )
    block = build_constraint_block("alicia", scene)
    assert "Somatic contact first" not in block
    assert "close the distance" not in block


def test_a_double_prime_2_alicia_phone_has_substituted_pillar() -> None:
    """A''2: Alicia phone-mode prompt DOES contain the phone pillar."""
    scene = SceneState(
        present_characters=["alicia", "whyze"],
        alicia_home=True,
        communication_mode=CommunicationMode.PHONE,
    )
    block = build_constraint_block("alicia", scene)
    assert "voice carries the regulation" in block.lower()


def test_a_double_prime_3_phone_filters_in_person_exemplars() -> None:
    """A''3: In-person examples do NOT appear in phone-mode voice guidance."""
    clear_kernel_cache()
    phone_items = load_voice_guidance("alicia", communication_mode="phone")
    in_person_items = load_voice_guidance("alicia", communication_mode="in_person")
    assert phone_items is not None
    assert in_person_items is not None
    assert len(phone_items) < len(in_person_items)
    phone_text = " ".join(phone_items)
    assert "Example 3" not in phone_text
    assert "Example 5" not in phone_text


def test_a_double_prime_4_phone_tagged_exemplar_appears() -> None:
    """A''4: Phone-tagged exemplar appears in phone mode, NOT in in-person mode."""
    clear_kernel_cache()
    phone_items = load_voice_guidance("alicia", communication_mode="phone")
    in_person_items = load_voice_guidance("alicia", communication_mode="in_person")
    assert phone_items is not None
    assert in_person_items is not None
    phone_text = " ".join(phone_items)
    in_person_text = " ".join(in_person_items)
    assert "Example 11" in phone_text or "Phone Call" in phone_text
    assert "Example 11" not in in_person_text


def test_a_double_prime_5_bina_phone_mode_is_noop() -> None:
    """A''5: Bina phone-mode constraints are identical to in-person."""
    scene_in_person = SceneState(
        present_characters=["bina", "whyze"],
        communication_mode=CommunicationMode.IN_PERSON,
    )
    scene_phone = SceneState(
        present_characters=["bina", "whyze"],
        communication_mode=CommunicationMode.PHONE,
    )
    block_ip = build_constraint_block("bina", scene_in_person)
    block_phone = build_constraint_block("bina", scene_phone)
    assert block_ip == block_phone


def test_a_double_prime_6_letter_and_video_have_own_pillars() -> None:
    """A''6: Letter-mode and video-mode prompts each get their own pillar text."""
    scene_letter = SceneState(
        present_characters=["alicia", "whyze"],
        alicia_home=True,
        communication_mode=CommunicationMode.LETTER,
    )
    scene_video = SceneState(
        present_characters=["alicia", "whyze"],
        alicia_home=True,
        communication_mode=CommunicationMode.VIDEO_CALL,
    )
    block_letter = build_constraint_block("alicia", scene_letter)
    block_video = build_constraint_block("alicia", scene_video)
    assert "Letters are weight" in block_letter
    assert "Eye contact and posture" in block_video
    assert block_letter != block_video


def test_adelia_phone_mode_is_noop() -> None:
    """Cross-character regression: Adelia's constraints don't change with phone mode."""
    scene_ip = SceneState(
        present_characters=["adelia", "whyze"],
        communication_mode=CommunicationMode.IN_PERSON,
    )
    scene_phone = SceneState(
        present_characters=["adelia", "whyze"],
        communication_mode=CommunicationMode.PHONE,
    )
    assert build_constraint_block("adelia", scene_ip) == build_constraint_block("adelia", scene_phone)


def test_reina_phone_mode_is_noop() -> None:
    """Cross-character regression: Reina's constraints don't change with phone mode."""
    scene_ip = SceneState(
        present_characters=["reina", "whyze"],
        communication_mode=CommunicationMode.IN_PERSON,
    )
    scene_phone = SceneState(
        present_characters=["reina", "whyze"],
        communication_mode=CommunicationMode.PHONE,
    )
    assert build_constraint_block("reina", scene_ip) == build_constraint_block("reina", scene_phone)


def test_adelia_voice_guidance_multiple_modes() -> None:
    """Finding 2: Voice guidance should cover more than just the first 2 examples."""
    clear_kernel_cache()
    guidance = load_voice_guidance("adelia")
    assert guidance is not None
    # Should have more than 2 items to cover diverse voice modes
    assert len(guidance) >= 3


def test_adelia_voice_layer_prioritizes_handoff_and_cultural_surface() -> None:
    """The live Adelia voice layer carries metadata and at least some guidance."""
    layer = format_voice_directives("adelia", _make_bundle("adelia").character_baseline)
    assert "Adelia Raye" in layer.text
    assert "ENFP-A" in layer.text
    assert "Voice calibration guidance:" in layer.text


async def test_assemble_context_adelia_retains_identity_and_protocol_surface(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Adelia's live prompt should carry identity, protocol, and voice-surface cues."""

    async def stub_retrieve_memories(*args: Any, **kwargs: Any) -> Any:
        return _make_bundle("adelia")

    monkeypatch.setattr(assembler_module, "retrieve_memories", stub_retrieve_memories)
    clear_kernel_cache()

    prompt = await assemble_context(
        character_id="adelia",
        scene_context="Adelia and Whyze are in the warehouse after a permit fight.",
        scene_state=SceneState(
            present_characters=["adelia", "whyze"],
            scene_description="Warehouse after hours; permit binder open; welding bench still warm.",
            communication_mode=CommunicationMode.IN_PERSON,
        ),
        session=cast(AsyncSession, None),
        embedding_service=_StubEmbeddingService(),
    )

    assert "I am Adelia Raye" in prompt.prompt
    assert "## 2. Core Identity" in prompt.prompt
    assert "TALK-TO-EACH-OTHER" not in prompt.prompt
    assert "Relationship adelia-bina" not in prompt.prompt


# --- Phase A' WI5: Adelia + Reina solo pair smoke tests ---


async def test_assemble_context_adelia_solo_pair(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Adelia solo pair assembly: succeeds, terminally anchored, no Msty artifacts."""

    async def stub_retrieve_memories(*args: Any, **kwargs: Any) -> Any:
        return _make_bundle("adelia")

    monkeypatch.setattr(assembler_module, "retrieve_memories", stub_retrieve_memories)
    clear_kernel_cache()

    prompt = await assemble_context(
        character_id="adelia",
        scene_context="Adelia is working on a commission in the warehouse.",
        scene_state=SceneState(
            present_characters=["adelia", "whyze"],
            scene_description="Manchester warehouse; sparks from the bench; late afternoon.",
            communication_mode=CommunicationMode.IN_PERSON,
        ),
        session=cast(AsyncSession, None),
        embedding_service=_StubEmbeddingService(),
    )

    assert prompt.is_terminally_anchored
    assert prompt.prompt.rstrip().endswith("</CONSTRAINTS>")
    assert "## 2. Core Identity" in prompt.prompt
    assert "I am Adelia Raye" in prompt.prompt
    assert "Msty Persona Studio" not in prompt.prompt
    assert "**User:**" not in prompt.prompt


async def test_assemble_context_reina_solo_pair(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reina solo pair assembly: succeeds, terminally anchored, no Msty artifacts."""

    async def stub_retrieve_memories(*args: Any, **kwargs: Any) -> Any:
        return _make_bundle("reina")

    monkeypatch.setattr(assembler_module, "retrieve_memories", stub_retrieve_memories)
    clear_kernel_cache()

    prompt = await assemble_context(
        character_id="reina",
        scene_context="Reina reviewing case files in the home office.",
        scene_state=SceneState(
            present_characters=["reina", "whyze"],
            scene_description="Home office; case binder open; evening quiet.",
            communication_mode=CommunicationMode.IN_PERSON,
        ),
        session=cast(AsyncSession, None),
        embedding_service=_StubEmbeddingService(),
    )

    assert prompt.is_terminally_anchored
    assert prompt.prompt.rstrip().endswith("</CONSTRAINTS>")
    assert "## 2. Core Identity" in prompt.prompt
    assert "I am Reina Torres" in prompt.prompt
    assert "Msty Persona Studio" not in prompt.prompt
    assert "**User:**" not in prompt.prompt


# --- Bina conversion audit regression tests ---


def test_bina_kernel_preserves_circuit_pair_section() -> None:
    """Bina's compiled kernel must contain Circuit Pair architecture."""
    clear_kernel_cache()
    kernel = load_kernel("bina", budget=DEFAULT_BUDGETS.kernel)
    assert "Circuit" in kernel
    assert "Whyze" in kernel


def test_bina_kernel_preserves_behavioral_tier() -> None:
    """Bina's compiled kernel must contain Behavioral Tier Framework."""
    clear_kernel_cache()
    kernel = load_kernel("bina", budget=DEFAULT_BUDGETS.kernel)
    assert "Tier" in kernel or "behavioral" in kernel.lower()


def test_bina_voice_guidance_multiple_modes() -> None:
    """Bina's voice guidance should cover diverse modes, not just compression and veto."""
    clear_kernel_cache()
    guidance = load_voice_guidance("bina")
    assert guidance is not None
    assert len(guidance) >= 3


def test_bina_whyze_scene_no_talk_mandate() -> None:
    """A Bina-Whyze scene must NOT get the Talk-to-Each-Other mandate."""
    scene = SceneState(present_characters=["bina", "whyze"])
    block = build_constraint_block("bina", scene)
    assert "TALK-TO-EACH-OTHER" not in block
