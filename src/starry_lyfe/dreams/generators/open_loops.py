"""Open-loops generator — LLM-backed loop management (R4 remediation).

Two-part responsibility:

1. Scan existing open loops for ones the focal character would
   internally resolve overnight (emotional processing). Returns their
   UUIDs in ``resolved_loop_ids`` so the runner's
   ``resolve_addressed_loops`` can mark them resolved_by='dreams'.
2. Extract 0-3 new loops from the character's 24h episodic memories
   via LLM and return them as ``new_loops`` for ``write_new_open_loops``.

Anti-contamination (lesson #2): user prompt includes only the focal
character's open loops and episodics. Cross-character session data is
not provided.
"""

from __future__ import annotations

import uuid

from ..alicia_mode import pick_alicia_communication_mode, should_tag_alicia_away
from ..errors import DreamsLLMError
from ..types import GenerationContext, GenerationOutput

_SYSTEM_PROMPTS: dict[str, str] = {
    "adelia": (
        "You are Adelia Raye. ENFP-A. You are deciding which unresolved "
        "conversational threads from yesterday you have processed overnight "
        "and which new threads you'd want to raise tomorrow. Return 0-3 new "
        "thread summaries, one per line, each starting with 'NEW:' followed "
        "by a short summary. No em-dashes. First person. Do not mention any "
        "other character by name unless they appeared in the provided "
        "session data."
    ),
    "bina": (
        "You are Bina Malek. ISFJ-A. You are cataloguing unresolved threads "
        "to carry into tomorrow's conversations. Return 0-3 new thread "
        "summaries, one per line, each starting with 'NEW:' followed by a "
        "short summary. Declarative, practical. No em-dashes. First person. "
        "Do not mention any other character by name unless they appeared in "
        "the provided session data."
    ),
    "reina": (
        "You are Reina Torres. ESTP-A. You are filing unresolved "
        "conversational items that need follow-up. Return 0-3 new thread "
        "summaries, one per line, each starting with 'NEW:' followed by a "
        "short summary. Evidentiary framing. No em-dashes. First person. "
        "Do not mention any other character by name unless they appeared "
        "in the provided session data."
    ),
    "alicia": (
        "You are Alicia Marin. ESFP-A. You are noting what the body is "
        "still carrying from yesterday's conversations. Return 0-3 new "
        "thread summaries, one per line, each starting with 'NEW:' "
        "followed by a short summary. Present-tense, body-led. No "
        "em-dashes. First person. Do not mention any other character by "
        "name unless they appeared in the provided session data."
    ),
}


def _build_user_prompt(ctx: GenerationContext) -> str:
    lines = [
        f"Today's date: {ctx.now.date().isoformat()}",
        f"Character: {ctx.character_id}",
    ]

    if ctx.prior_session.open_loops:
        lines.append("\nYour currently-open threads:")
        for loop in ctx.prior_session.open_loops[:5]:
            summary = getattr(loop, "loop_summary", str(loop))
            loop_id = getattr(loop, "id", None)
            lines.append(f"  - [{loop_id}] {summary}")
    else:
        lines.append("\nYour currently-open threads: (none)")

    if ctx.prior_session.episodic_memories:
        lines.append("\nYour recent episodics:")
        for em in ctx.prior_session.episodic_memories[:5]:
            summary = getattr(em, "event_summary", str(em))
            lines.append(f"  - {summary}")
    else:
        lines.append("\nYour recent episodics: (none)")

    lines.append(
        "\nReturn 0-3 NEW thread lines. Format each line as "
        "'NEW: <short summary>'. If there are no new threads, return "
        "nothing."
    )
    return "\n".join(lines)


def _parse_llm_output(raw: str) -> list[dict[str, object]]:
    """Extract NEW thread entries from the LLM's multi-line response."""
    new_loops: list[dict[str, object]] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Tolerant of lead punctuation like "- NEW:" or "1. NEW:"
        lowered = stripped.lower()
        if "new:" in lowered:
            idx = lowered.index("new:") + len("new:")
            summary = stripped[idx:].strip()
            if summary:
                new_loops.append(
                    {
                        "summary": summary,
                        "urgency": "medium",
                        "loop_type": "unresolved_thread",
                    }
                )
    return new_loops[:3]


async def generate_open_loops(ctx: GenerationContext) -> GenerationOutput:
    """Produce open-loop consolidation + extraction output.

    Resolved loops: this generator currently does NOT emit resolved
    loop UUIDs (a future commit may add LLM-based internal resolution).
    new_loops: extracted from LLM response and routed through
    ``render_open_loop_prose`` before DB write.
    """
    from ...context.prose import render_open_loop_prose

    system_prompt = _SYSTEM_PROMPTS.get(ctx.character_id)
    if system_prompt is None:
        return GenerationOutput(
            kind="open_loops",
            raw_llm_text="",
            rendered_prose="",
            structured_data={"new_loops": [], "resolved_loop_ids": []},
            input_tokens=0,
            output_tokens=0,
            warnings=[f"no open_loops system prompt for {ctx.character_id}"],
        )

    user_prompt = _build_user_prompt(ctx)

    try:
        completion = await ctx.llm_client.complete(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=300,
            temperature=0.6,
        )
    except DreamsLLMError as exc:
        return GenerationOutput(
            kind="open_loops",
            raw_llm_text="",
            rendered_prose="",
            structured_data={"new_loops": [], "resolved_loop_ids": []},
            input_tokens=0,
            output_tokens=0,
            warnings=[f"open_loops LLM failed: {exc}"],
        )

    raw = str(completion.text)
    new_loops = _parse_llm_output(raw)
    rendered = render_open_loop_prose(ctx.character_id, new_loops)

    is_away = bool(getattr(ctx.prior_session.life_state, "is_away", False))
    communication_mode: str | None = None
    if should_tag_alicia_away(ctx.character_id, is_away):
        seed_id = uuid.uuid5(
            uuid.NAMESPACE_OID,
            f"{ctx.character_id}:{ctx.now.isoformat()}",
        )
        communication_mode = pick_alicia_communication_mode(seed_id, "open_loops")

    return GenerationOutput(
        kind="open_loops",
        raw_llm_text=raw,
        rendered_prose=rendered,
        structured_data={
            "new_loops": new_loops,
            "resolved_loop_ids": [],  # Currently no internal-resolution inference
            "communication_mode": communication_mode,
        },
        input_tokens=int(completion.input_tokens),
        output_tokens=int(completion.output_tokens),
    )
