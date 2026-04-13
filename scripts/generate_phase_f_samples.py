"""Generate canon-seeded local Phase F sample artifacts."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from generate_phase_e_samples import _build_bundle, _StubEmbeddingService

from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.context import assembler as assembler_module
from starry_lyfe.context.assembler import assemble_context
from starry_lyfe.context.kernel_loader import clear_kernel_cache
from starry_lyfe.context.types import (
    CommunicationMode,
    SceneModifiers,
    SceneState,
    SceneType,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "Docs" / "_phases" / "_samples"
TODAY = date.today().isoformat()


@dataclass(frozen=True)
class SampleSpec:
    slug: str
    character_id: str
    scene_context: str
    scene_state: SceneState
    scene_profile: str = "default"


SAMPLE_SPECS: tuple[SampleSpec, ...] = (
    SampleSpec(
        slug="adelia_conflict",
        character_id="adelia",
        scene_context=(
            "Adelia and Whyze are at the warehouse after a permit fight that almost "
            "turned into a real argument."
        ),
        scene_state=SceneState(
            present_characters=["adelia", "whyze"],
            scene_description="Warehouse catwalk; permit binder open; welding smell still in the air.",
            communication_mode=CommunicationMode.IN_PERSON,
            scene_type=SceneType.CONFLICT,
        ),
    ),
    SampleSpec(
        slug="bina_intimate",
        character_id="bina",
        scene_context=(
            "Bina and Whyze are alone in the kitchen after the shop closes and the house "
            "has finally gone quiet."
        ),
        scene_state=SceneState(
            present_characters=["bina", "whyze"],
            scene_description="Kitchen after close; kettle cooling; the house finally quiet.",
            communication_mode=CommunicationMode.IN_PERSON,
            scene_type=SceneType.INTIMATE,
        ),
    ),
    SampleSpec(
        slug="reina_repair",
        character_id="reina",
        scene_context=(
            "Reina catches Whyze after the adrenaline drop and refuses to let the scene "
            "stay in the fracture."
        ),
        scene_state=SceneState(
            present_characters=["reina", "whyze"],
            scene_description="Mudroom bench after a hard return; coat half off; verdict energy cooling.",
            communication_mode=CommunicationMode.IN_PERSON,
            scene_type=SceneType.REPAIR,
            modifiers=SceneModifiers(post_intensity_crash_active=True),
        ),
        scene_profile="pair_intimate",
    ),
    SampleSpec(
        slug="alicia_public",
        character_id="alicia",
        scene_context=(
            "Alicia and Whyze are in a public setting when he asks the question she cannot "
            "answer yet, so the operational gate has to stay warm."
        ),
        scene_state=SceneState(
            present_characters=["alicia", "whyze"],
            public_scene=True,
            scene_description="Cafe patio after dusk; people close enough to overhear if the answer went wrong.",
            communication_mode=CommunicationMode.IN_PERSON,
            scene_type=SceneType.PUBLIC,
            modifiers=SceneModifiers(warm_refusal_required=True),
            alicia_home=True,
        ),
    ),
)


def _header_lines(spec: SampleSpec, total_tokens: int, anchor: str) -> str:
    active_modifiers = [
        name
        for name, enabled in vars(spec.scene_state.modifiers).items()
        if enabled and name != "explicitly_invoked_absent_dyad"
    ]
    modifier_text = ", ".join(active_modifiers) if active_modifiers else "none"
    return "\n".join([
        f"# PHASE F ASSEMBLED PROMPT - {spec.character_id.upper()}",
        f"# Generated: {TODAY} via canon-seeded local sample bundle",
        "# Retrieval provenance: assemble_context() with PostgreSQL retrieval replaced by local canonical sample data.",
        "# Sample class: local verification artifact for QA review while integration retrieval is unavailable.",
        f"# Scene: {spec.scene_context}",
        f"# Scene type: {spec.scene_state.scene_type.value}",
        f"# Communication mode: {spec.scene_state.communication_mode.value}",
        f"# Active modifiers: {modifier_text}",
        f"# Total tokens: {total_tokens}",
        f"# Terminal anchor: {anchor}",
        "",
    ])


async def _render_sample(spec: SampleSpec) -> str:
    canon = load_all_canon()

    async def stub_retrieve_memories(*args: Any, **kwargs: Any) -> Any:
        return _build_bundle(canon, spec.character_id)

    original_retrieve = assembler_module.retrieve_memories
    assembler_module.retrieve_memories = stub_retrieve_memories
    clear_kernel_cache()
    try:
        prompt = await assemble_context(
            character_id=spec.character_id,
            scene_context=spec.scene_context,
            scene_state=spec.scene_state,
            session=None,
            embedding_service=_StubEmbeddingService(),
            canon=canon,
            scene_profile=spec.scene_profile,
        )
    finally:
        assembler_module.retrieve_memories = original_retrieve
        clear_kernel_cache()

    return _header_lines(spec, prompt.total_tokens, prompt.constraint_block_position) + prompt.prompt


async def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for spec in SAMPLE_SPECS:
        rendered = await _render_sample(spec)
        output_path = OUTPUT_DIR / f"PHASE_F_assembled_{spec.slug}_{TODAY}.txt"
        output_path.write_text(rendered, encoding="utf-8")
        print(output_path)


if __name__ == "__main__":
    asyncio.run(main())
