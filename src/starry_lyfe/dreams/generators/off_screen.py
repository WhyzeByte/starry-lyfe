"""Off-screen events generator — placeholder stub (Phase 6 commit 4).

Real LLM implementation follows in a later commit. This stub returns an
empty events list so the runner orchestration exercises correctly.
"""

from __future__ import annotations

from ..types import GenerationContext, GenerationOutput


async def generate_off_screen(ctx: GenerationContext) -> GenerationOutput:
    """Return empty off-screen events. TODO(phase_6_continuation): LLM wiring."""
    return GenerationOutput(
        kind="off_screen",
        raw_llm_text="",
        rendered_prose="",
        structured_data={"events": []},
        input_tokens=0,
        output_tokens=0,
        warnings=["off_screen generator is a placeholder stub (commit 4)"],
    )
