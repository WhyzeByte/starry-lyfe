"""Diary generator — placeholder stub (Phase 6 commit 4).

Commit 5 replaces this stub with a real LLM-backed implementation that
invokes BDOne per character, routes output through the Phase G
``render_diary_prose`` renderer, and returns both raw and rendered text.
The stub returns a one-line placeholder so the runner pipeline can be
exercised end-to-end.
"""

from __future__ import annotations

from ..types import GenerationContext, GenerationOutput


async def generate_diary(ctx: GenerationContext) -> GenerationOutput:
    """Return a placeholder diary entry. TODO(phase_6_commit_5): LLM + Phase G render."""
    placeholder = f"[{ctx.character_id} diary placeholder — commit 5 replaces this with LLM output.]"
    return GenerationOutput(
        kind="diary",
        raw_llm_text="",
        rendered_prose=placeholder,
        structured_data={
            "mood": "neutral",
            "reflection": placeholder,
            "things_to_revisit": [],
        },
        input_tokens=0,
        output_tokens=0,
        warnings=["diary generator is a placeholder stub (commit 4; real LLM + Phase G in commit 5)"],
    )
