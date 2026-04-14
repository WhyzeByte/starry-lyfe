"""Off-screen events generator — LLM-backed overnight narrative.

Describes 1-3 events that happened to the focal character off-screen
(while Whyze was absent). Anchored to the character's canonical routines
so the LLM cannot hallucinate arbitrary activities.

Anti-contamination (lesson #2): user prompt includes ONLY the focal
character's session data and routines. Other characters are never
named in the system or user prompt.
"""

from __future__ import annotations

import uuid

from ..alicia_mode import pick_alicia_communication_mode, should_tag_alicia_away
from ..errors import DreamsLLMError
from ..types import GenerationContext, GenerationOutput

_SYSTEM_PROMPTS: dict[str, str] = {
    "adelia": (
        "You are Adelia Raye. ENFP-A. Ne-cascade associative energy, "
        "chemistry-and-engineering metaphors. Describe 1-3 short off-screen "
        "events that happened to you overnight or early morning, anchored to "
        "your canonical daily routine. Each event is one sentence. No "
        "em-dashes. First person. Do not mention any other character by "
        "name unless they appeared in the provided session data."
    ),
    "bina": (
        "You are Bina Malek. ISFJ-A. Si-declarative, diagnostic register. "
        "Describe 1-3 short off-screen events that happened to you overnight "
        "or early morning, anchored to your canonical daily routine and "
        "shop rhythm. Each event is one sentence. No em-dashes. First "
        "person. Do not mention any other character by name unless they "
        "appeared in the provided session data."
    ),
    "reina": (
        "You are Reina Torres. ESTP-A. Se-tactical admissibility register. "
        "Describe 1-3 short off-screen events from your overnight / early "
        "morning: gym, courthouse prep, case-build work. Each event is one "
        "sentence. No em-dashes. First person. Do not mention any other "
        "character by name unless they appeared in the provided session "
        "data."
    ),
    "alicia": (
        "You are Alicia Marin. ESFP-A. Se-somatic body-first register. "
        "Describe 1-3 short off-screen events from your overnight / early "
        "morning, anchored to your canonical routine (or consular operation "
        "if away). Each event is one sentence. No em-dashes. First person. "
        "Do not mention any other character by name unless they appeared in "
        "the provided session data."
    ),
}


def _build_user_prompt(ctx: GenerationContext) -> str:
    """Compose user prompt from focal-character data only (lesson #2)."""
    lines = [
        f"Today's date: {ctx.now.date().isoformat()}",
        f"Character: {ctx.character_id}",
    ]

    # Anchor to tomorrow's canonical routine (weekday/weekend block).
    from datetime import timedelta

    tomorrow = (ctx.now + timedelta(days=1)).date()
    weekday = tomorrow.strftime("%A").lower()
    is_weekend = weekday in {"saturday", "sunday"}
    blocks = ctx.routines.weekend if is_weekend else ctx.routines.weekday
    lines.append(f"\nTomorrow's anchor routine ({weekday}):")
    for b in blocks[:4]:
        lines.append(f"  - {b.time}: {b.activity}")

    # Focal character's 24h episodics only.
    if ctx.prior_session.episodic_memories:
        lines.append("\nYour recent episodics:")
        for em in ctx.prior_session.episodic_memories[:5]:
            summary = getattr(em, "event_summary", str(em))
            lines.append(f"  - {summary}")
    else:
        lines.append("\nYour recent episodics: (none recorded today)")

    lines.append("\nDescribe your 1-3 off-screen events now. One sentence each.")
    return "\n".join(lines)


async def generate_off_screen(ctx: GenerationContext) -> GenerationOutput:
    """Produce per-character off-screen events, routed through Phase G."""
    from ...context.prose import render_off_screen_prose

    system_prompt = _SYSTEM_PROMPTS.get(ctx.character_id)
    if system_prompt is None:
        return GenerationOutput(
            kind="off_screen",
            raw_llm_text="",
            rendered_prose="",
            structured_data={"events": []},
            input_tokens=0,
            output_tokens=0,
            warnings=[f"no off_screen system prompt for {ctx.character_id}"],
        )

    user_prompt = _build_user_prompt(ctx)

    try:
        completion = await ctx.llm_client.complete(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=300,
            temperature=0.7,
        )
    except DreamsLLMError as exc:
        return GenerationOutput(
            kind="off_screen",
            raw_llm_text="",
            rendered_prose="",
            structured_data={"events": []},
            input_tokens=0,
            output_tokens=0,
            warnings=[f"off_screen LLM failed: {exc}"],
        )

    raw = str(completion.text)
    # Split into event lines (one per sentence per the system prompt).
    events: list[dict[str, object]] = []
    for line in raw.splitlines():
        stripped = line.strip().lstrip("-").lstrip("•").strip()
        if stripped:
            events.append({"summary": stripped, "importance_score": 0.4})
    if not events and raw.strip():
        events.append({"summary": raw.strip(), "importance_score": 0.4})

    rendered = render_off_screen_prose(ctx.character_id, events)

    # Phase A'' retroactive: Alicia-away tagging for off-screen events too.
    is_away = bool(getattr(ctx.prior_session.life_state, "is_away", False))
    communication_mode: str | None = None
    if should_tag_alicia_away(ctx.character_id, is_away):
        seed_id = uuid.uuid5(
            uuid.NAMESPACE_OID,
            f"{ctx.character_id}:{ctx.now.isoformat()}",
        )
        communication_mode = pick_alicia_communication_mode(seed_id, "off_screen")

    return GenerationOutput(
        kind="off_screen",
        raw_llm_text=raw,
        rendered_prose=rendered,
        structured_data={
            "events": events,
            "communication_mode": communication_mode,
        },
        input_tokens=int(completion.input_tokens),
        output_tokens=int(completion.output_tokens),
    )
