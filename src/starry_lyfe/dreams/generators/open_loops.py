"""Open-loops generator — placeholder stub (Phase 6 commit 4)."""

from __future__ import annotations

from ..types import GenerationContext, GenerationOutput


async def generate_open_loops(ctx: GenerationContext) -> GenerationOutput:
    """Return empty open-loops list. TODO(phase_6_continuation): LLM wiring + expiry."""
    return GenerationOutput(
        kind="open_loops",
        raw_llm_text="",
        rendered_prose="",
        structured_data={"new_loops": [], "resolved_loop_ids": []},
        input_tokens=0,
        output_tokens=0,
        warnings=["open_loops generator is a placeholder stub (commit 4)"],
    )
