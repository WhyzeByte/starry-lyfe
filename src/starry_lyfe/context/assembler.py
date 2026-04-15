"""Seven-layer context assembler with terminal constraint anchoring.

This is the core of Phase 3. It takes a character ID and scene context,
retrieves all memory tiers via Phase 2, formats them into seven layers,
and places Whyze-Byte constraints terminally (Layer 7 is ALWAYS the
final block in the prompt, immediately before the user's input).
"""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from starry_lyfe.canon.loader import Canon, load_all_canon
from starry_lyfe.canon.soul_essence import soul_essence_token_estimate
from starry_lyfe.db.embed import EmbeddingService
from starry_lyfe.db.retrieval import MemoryBundle, retrieve_memories

from .budgets import DEFAULT_BUDGETS, estimate_tokens, trim_text_to_budget
from .constraints import build_constraint_block
from .kernel_loader import scene_type_to_promoted_sections
from .layers import (
    format_canon_facts,
    format_kernel,
    format_memory_fragments,
    format_scene_blocks,
    format_sensory_grounding,
    format_voice_directives,
)
from .types import AssembledPrompt, CommunicationMode, LayerContent, SceneState

logger = logging.getLogger(__name__)

LAYER_MARKERS: dict[int, str] = {
    1: "PERSONA_KERNEL",
    2: "CANON_FACTS",
    3: "MEMORY_FRAGMENTS",
    4: "SENSORY_GROUNDING",
    5: "VOICE_DIRECTIVES",
    6: "SCENE_CONTEXT",
    7: "CONSTRAINTS",
}


class AliciaAwayError(Exception):
    """Raised when assembling an in-person Alicia prompt while she is away on operations."""


def _wrap_layer(layer: LayerContent) -> str:
    """Wrap a layer in XML-style markers that the model must never echo."""
    marker = LAYER_MARKERS[layer.layer_number]
    return f"<{marker}>\n{layer.text}\n</{marker}>"


async def assemble_context(
    character_id: str,
    scene_context: str,
    scene_state: SceneState,
    session: AsyncSession,
    embedding_service: EmbeddingService,
    canon: Canon | None = None,
    scene_profile: str = "default",
    memory_bundle: MemoryBundle | None = None,
) -> AssembledPrompt:
    """Assemble the seven-layer system prompt for a character.

    Layer 7 (Whyze-Byte constraints) is ALWAYS the final block in the
    prompt. Nothing follows it. This is terminal anchoring.

    F2 (2026-04-15): Callers that have already retrieved the
    ``MemoryBundle`` for ``character_id`` may pass it via
    ``memory_bundle`` to avoid a duplicate DB round-trip. When omitted,
    ``retrieve_memories`` is called internally — the Phase 3 public
    contract is preserved.

    Raises:
        AliciaAwayError: If assembling Alicia for an in-person scene while she is away.
    """
    if canon is None:
        canon = load_all_canon()

    # P3-02: Enforce Alicia presence-conditional assembly
    if (
        character_id == "alicia"
        and not scene_state.alicia_home
        and scene_state.communication_mode == CommunicationMode.IN_PERSON
    ):
        msg = (
            "Cannot assemble in-person Alicia prompt while she is away on operations. "
            "Set scene_state.alicia_home=True or communication_mode to 'phone', 'letter', or 'video_call'."
        )
        raise AliciaAwayError(msg)

    # Retrieve all memory tiers from Phase 2 — skip when caller provided a
    # pre-fetched bundle (F2 plumbing from the HTTP pipeline).
    if memory_bundle is not None:
        memories = memory_bundle
    else:
        memories = await retrieve_memories(
            session=session,
            embedding_service=embedding_service,
            scene_context=scene_context,
            character_id=character_id,
            present_characters=scene_state.present_characters,
        )

    from .budgets import get_scene_profile, resolve_kernel_budget

    profile = get_scene_profile(scene_profile)
    kernel_budget = resolve_kernel_budget(character_id, base_budget=profile.kernel)

    from .soul_cards import find_activated_cards, format_soul_cards

    activated = find_activated_cards(
        character_id,
        scene_state=scene_state,
        communication_mode=str(scene_state.communication_mode),
    )
    pair_cards = [c for c in activated if c.card_type == "pair"]
    knowledge_cards = [c for c in activated if c.card_type == "knowledge"]

    pair_text = format_soul_cards(pair_cards, min(700, kernel_budget)) if pair_cards else ""
    knowledge_text = (
        format_soul_cards(knowledge_cards, min(500, profile.scene))
        if knowledge_cards
        else ""
    )

    reserved_kernel_tokens = estimate_tokens(pair_text) if pair_text else 0
    reserved_scene_tokens = estimate_tokens(knowledge_text) if knowledge_text else 0

    promote = scene_type_to_promoted_sections(scene_state.scene_type)
    layer_1 = format_kernel(
        character_id,
        budget=max(1, kernel_budget - reserved_kernel_tokens),
        promote_sections=promote or None,
        profile_name=scene_profile,
    )
    layer_2 = format_canon_facts(memories.canon_facts, character_id=character_id)
    layer_3 = format_memory_fragments(memories.episodic_memories)
    layer_4 = format_sensory_grounding(
        memories.somatic_state, canon, scene_state.scene_description
    )
    layer_5 = format_voice_directives(
        character_id,
        memories.character_baseline,
        budget=profile.voice,
        communication_mode=scene_state.communication_mode,
        scene_state=scene_state,
    )
    # Phase 6 R3-F2: surface Dreams-written activities into Layer 6.
    # MemoryBundle.activities is Tier 8 (Dreams-populated) and may be
    # empty on fresh DBs. format_scene_blocks renders only the most
    # recent entry's narrator_script when present.
    layer_6 = format_scene_blocks(
        character_id,
        memories.dyad_states_whyze,
        memories.dyad_states_internal,
        memories.open_loops,
        scene_state.present_characters,
        scene_state.scene_description,
        budget=max(1, profile.scene - reserved_scene_tokens),
        recalled_dyads=scene_state.recalled_dyads,
        explicitly_invoked_absent_dyad=scene_state.modifiers.explicitly_invoked_absent_dyad or None,
        dreams_activities=getattr(memories, "activities", None),
    )

    if pair_text:
        combined_layer_1 = f"{layer_1.text}\n\n{pair_text}"
        layer_1 = LayerContent(
            name="persona_kernel",
            text=combined_layer_1,
            estimated_tokens=estimate_tokens(combined_layer_1),
            layer_number=1,
        )

    if knowledge_text:
        combined_layer_6 = f"{layer_6.text}\n\n{knowledge_text}"
        layer_6 = LayerContent(
            name="scene_blocks",
            text=combined_layer_6,
            estimated_tokens=estimate_tokens(combined_layer_6),
            layer_number=6,
        )

    # R-2.4: post-assembly budget reconciliation. Layer 1 and Layer 6 get
    # soul-card tokens merged in after their formatters have already
    # applied trim. Compare actual against the effective ceiling so
    # budget overruns surface in logs rather than silently degrading
    # downstream layers.
    layer_1_actual = estimate_tokens(layer_1.text)
    layer_1_ceiling = kernel_budget + soul_essence_token_estimate(character_id)
    if layer_1_actual > layer_1_ceiling:
        logger.warning(
            "layer_1_budget_overrun",
            extra={
                "character_id": character_id,
                "actual_tokens": layer_1_actual,
                "ceiling_tokens": layer_1_ceiling,
                "kernel_budget": kernel_budget,
            },
        )
    layer_6_actual = estimate_tokens(layer_6.text)
    if layer_6_actual > profile.scene:
        logger.warning(
            "layer_6_budget_overrun",
            extra={
                "character_id": character_id,
                "actual_tokens": layer_6_actual,
                "ceiling_tokens": profile.scene,
            },
        )

    # Build Layer 7: terminal constraints (character-specific)
    # The non-echo instruction is embedded WITHIN the constraint block
    # so nothing follows Layer 7 in the final prompt.
    constraint_text = build_constraint_block(character_id, scene_state)
    constraint_text = trim_text_to_budget(
        constraint_text,
        DEFAULT_BUDGETS.constraints,
        "[Constraints trimmed to token budget.]",
    )
    layer_7 = LayerContent(
        name="whyze_byte_constraints",
        text=constraint_text,
        estimated_tokens=estimate_tokens(constraint_text),
        layer_number=7,
    )

    # Assemble: layers 1-6 first, then Layer 7 LAST (terminal anchoring)
    all_layers = [layer_1, layer_2, layer_3, layer_4, layer_5, layer_6, layer_7]
    wrapped_parts = [_wrap_layer(layer) for layer in all_layers]

    # P3-01: The prompt ends with Layer 7. Nothing follows.
    prompt = "\n\n".join(wrapped_parts)

    total = sum(layer.estimated_tokens for layer in all_layers)

    # Verify terminal anchoring structurally
    final_marker = f"</{LAYER_MARKERS[7]}>"
    position = "terminal" if prompt.rstrip().endswith(final_marker) else "violated"

    return AssembledPrompt(
        prompt=prompt,
        character_id=character_id,
        layers=all_layers,
        total_tokens=total,
        constraint_block_position=position,
    )
