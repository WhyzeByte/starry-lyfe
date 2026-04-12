"""Seven-layer context assembler with terminal constraint anchoring.

This is the core of Phase 3. It takes a character ID and scene context,
retrieves all memory tiers via Phase 2, formats them into seven layers,
and places Whyze-Byte constraints terminally (Layer 7 is ALWAYS the
final block in the prompt, immediately before the user's input).
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from starry_lyfe.canon.loader import Canon, load_all_canon
from starry_lyfe.db.embed import EmbeddingService
from starry_lyfe.db.retrieval import retrieve_memories

from .budgets import DEFAULT_BUDGETS, estimate_tokens, trim_text_to_budget
from .constraints import build_constraint_block
from .layers import (
    format_canon_facts,
    format_kernel,
    format_memory_fragments,
    format_scene_blocks,
    format_sensory_grounding,
    format_voice_directives,
)
from .types import AssembledPrompt, CommunicationMode, LayerContent, SceneState

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
) -> AssembledPrompt:
    """Assemble the seven-layer system prompt for a character.

    Layer 7 (Whyze-Byte constraints) is ALWAYS the final block in the
    prompt. Nothing follows it. This is terminal anchoring.

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
            "Set scene_state.alicia_home=True or communication_mode to 'phone' or 'letter'."
        )
        raise AliciaAwayError(msg)

    # Retrieve all memory tiers from Phase 2
    memories = await retrieve_memories(
        session=session,
        embedding_service=embedding_service,
        scene_context=scene_context,
        character_id=character_id,
        present_characters=scene_state.present_characters,
    )

    # Format layers 1-6
    layer_1 = format_kernel(character_id)
    layer_2 = format_canon_facts(memories.canon_facts)
    layer_3 = format_memory_fragments(memories.episodic_memories)
    layer_4 = format_sensory_grounding(
        memories.somatic_state, canon, scene_state.scene_description
    )
    layer_5 = format_voice_directives(character_id, memories.character_baseline)
    layer_6 = format_scene_blocks(
        character_id,
        memories.dyad_states_whyze,
        memories.dyad_states_internal,
        memories.open_loops,
        scene_state.present_characters,
        scene_state.scene_description,
        recalled_dyads=scene_state.recalled_dyads,
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
