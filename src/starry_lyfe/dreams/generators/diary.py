"""Diary generator — LLM-backed 1-paragraph diary entry per character.

Invokes BDOne with a per-character system prompt derived from the
character's voice parameters and pair architecture. Raw LLM output is
routed through the Phase G ``render_diary_prose`` renderer before being
returned so Dreams never emits raw JSON-shaped content into Layer 2 /
episodic memory.

Anti-contamination (lesson #2 from Phase 5): the system prompt includes
ONLY the focal character's canonical material. Cross-character session
data is subtracted from the candidate pool before the LLM call.
"""

from __future__ import annotations

from ..errors import DreamsLLMError
from ..types import GenerationContext, GenerationOutput

# Per-character system prompts. Each block is intentionally minimal and
# leans on the character's canonical voice register (established in the
# existing Phase G prose helpers). The LLM is asked for a 1-paragraph
# reflection, not a long journal; Dreams is the consolidation pass.
_SYSTEM_PROMPTS: dict[str, str] = {
    "adelia": (
        "You are Adelia Raye. ENFP-A. Ne-cascade associative energy. "
        "Chemistry and engineering metaphors. You are writing a short "
        "diary reflection before sleep about yesterday's conversation "
        "with Whyze. Keep it to one paragraph. No em-dashes. First "
        "person. Do not mention any other character by name unless "
        "they appeared in the provided session data."
    ),
    "bina": (
        "You are Bina Malek. ISFJ-A. Si-declarative precision, "
        "diagnostic register. You are logging a one-paragraph end-of-day "
        "entry about yesterday's conversation with Whyze. Declarative, "
        "factual, warm. No em-dashes. First person. Do not mention "
        "any other character by name unless they appeared in the "
        "provided session data."
    ),
    "reina": (
        "You are Reina Torres. ESTP-A. Se-tactical admissibility register. "
        "You are writing one paragraph of end-of-day case notes on "
        "yesterday's conversation with Whyze. Evidentiary framing, body-read "
        "present. No em-dashes. First person. Do not mention any other "
        "character by name unless they appeared in the provided session "
        "data."
    ),
    "alicia": (
        "You are Alicia Marin. ESFP-A. Se-somatic body-first register. "
        "You are writing one short paragraph of diary reflection before "
        "sleep about yesterday's conversation with Whyze. Present-tense, "
        "body-led, specific. No em-dashes. First person. Do not mention "
        "any other character by name unless they appeared in the "
        "provided session data."
    ),
}


def _build_user_prompt(ctx: GenerationContext) -> str:
    """Assemble the user-side prompt from focal-character session data only.

    Cross-character session data is NOT included here — that is the
    lesson-#2 anti-contamination filter applied at generation time.
    Only the focal character's own episodics, open loops, and life state
    reach the LLM.
    """
    snap = ctx.prior_session
    lines = [
        f"Today's date: {ctx.now.date().isoformat()}",
        f"Character: {ctx.character_id}",
    ]

    if snap.episodic_memories:
        lines.append("\nRecent episodic memories (yours):")
        for em in snap.episodic_memories[:5]:
            summary = getattr(em, "event_summary", str(em))
            lines.append(f"  - {summary}")
    else:
        lines.append("\nRecent episodic memories: (none recorded today)")

    if snap.open_loops:
        lines.append("\nYour open threads:")
        for loop in snap.open_loops[:5]:
            summary = getattr(loop, "loop_summary", str(loop))
            lines.append(f"  - {summary}")

    lines.append("\nWrite your one-paragraph diary reflection now.")
    return "\n".join(lines)


async def generate_diary(ctx: GenerationContext) -> GenerationOutput:
    """Produce a per-character diary entry, routed through Phase G prose."""
    # Lazy import so the generator module does not pull the context layer
    # into its import graph at Dreams import time.
    from ...context.prose import render_diary_prose

    system_prompt = _SYSTEM_PROMPTS.get(ctx.character_id)
    if system_prompt is None:
        return GenerationOutput(
            kind="diary",
            raw_llm_text="",
            rendered_prose="",
            structured_data={"mood": "unknown", "reflection": "", "things_to_revisit": []},
            input_tokens=0,
            output_tokens=0,
            warnings=[f"no diary system prompt for {ctx.character_id}"],
        )

    user_prompt = _build_user_prompt(ctx)

    try:
        completion = await ctx.llm_client.complete(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=400,
            temperature=0.75,
        )
    except DreamsLLMError as exc:
        return GenerationOutput(
            kind="diary",
            raw_llm_text="",
            rendered_prose="",
            structured_data={"mood": "unknown", "reflection": "", "things_to_revisit": []},
            input_tokens=0,
            output_tokens=0,
            warnings=[f"diary LLM failed: {exc}"],
        )

    raw = str(completion.text)
    rendered = render_diary_prose(ctx.character_id, raw)

    return GenerationOutput(
        kind="diary",
        raw_llm_text=raw,
        rendered_prose=rendered,
        structured_data={
            "mood": "reflective",  # TODO(phase_6_continuation): infer from text
            "reflection": raw,
            "things_to_revisit": [],
        },
        input_tokens=int(completion.input_tokens),
        output_tokens=int(completion.output_tokens),
    )
