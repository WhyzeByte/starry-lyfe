"""Schedule generator — composes tomorrow's daily block from routines.yaml.

Placeholder implementation (Phase 6 commit 4). A future commit will
add "surprise event" LLM calls for routine deviations. For now this
generator is fully deterministic: it pulls tomorrow's weekday/weekend
block from the character's canonical routine.
"""

from __future__ import annotations

from ..types import GenerationContext, GenerationOutput


async def generate_schedule(ctx: GenerationContext) -> GenerationOutput:
    """Return tomorrow's schedule derived from canonical routines.

    Deterministic: no LLM call. Output format:
    ``structured_data = {"day_of_week": str, "blocks": [...]}``
    where each block is a dict matching the routines.yaml DailyBlock shape.
    """
    # Tomorrow's day relative to ctx.now.
    from datetime import timedelta

    tomorrow = (ctx.now + timedelta(days=1)).date()
    weekday_name = tomorrow.strftime("%A").lower()
    is_weekend = weekday_name in {"saturday", "sunday"}

    blocks = ctx.routines.weekend if is_weekend else ctx.routines.weekday

    block_dicts = [
        {"time": b.time, "activity": b.activity, "location": b.location}
        for b in blocks
    ]

    prose_lines = [
        f"  {b.time}: {b.activity} ({b.location})"
        for b in blocks
    ]
    rendered = f"Tomorrow's schedule ({weekday_name}):\n" + "\n".join(prose_lines)

    return GenerationOutput(
        kind="schedule",
        raw_llm_text="",  # deterministic; no LLM invocation
        rendered_prose=rendered,
        structured_data={
            "day_of_week": weekday_name,
            "is_weekend": is_weekend,
            "blocks": block_dicts,
        },
        input_tokens=0,
        output_tokens=0,
    )
