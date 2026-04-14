"""Activity-design generator — placeholder stub (Phase 6 commit 4)."""

from __future__ import annotations

from ..types import GenerationContext, GenerationOutput


async def generate_activity_design(ctx: GenerationContext) -> GenerationOutput:
    """Return a placeholder activity. TODO(phase_6_continuation): LLM wiring."""
    placeholder = f"[{ctx.character_id} activity design placeholder]"
    return GenerationOutput(
        kind="activity_design",
        raw_llm_text="",
        rendered_prose=placeholder,
        structured_data={
            "scene_description": placeholder,
            "narrator_script": "",
            "choice_tree": {},
        },
        input_tokens=0,
        output_tokens=0,
        warnings=["activity_design generator is a placeholder stub (commit 4)"],
    )
