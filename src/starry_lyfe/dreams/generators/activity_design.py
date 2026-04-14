"""Activity-design generator — LLM-backed scene opener (R5 remediation).

Designs tomorrow's session opener for the focal character: setting,
narrator script, and 2-3 choice branches. The narrator script reaches
Phase G via ``render_activity_prose`` before DB write.

Anti-contamination (lesson #2): the system prompt is per-character and
names no other canonical women; the user prompt includes only the focal
character's routines + episodics.
"""

from __future__ import annotations

import uuid

from ..alicia_mode import pick_alicia_communication_mode, should_tag_alicia_away
from ..errors import DreamsLLMError
from ..types import GenerationContext, GenerationOutput

_SYSTEM_PROMPTS: dict[str, str] = {
    "adelia": (
        "You are designing tomorrow's opening scene for Adelia Raye "
        "(ENFP-A, Ne-cascade chemistry metaphors). Return a short "
        "narrator script (2-3 sentences) describing the setting, and "
        "then 2-3 choice branches labelled 'Branch: <option>'. No "
        "em-dashes. Narrator voice is observational third person. "
        "Do not mention any other character by name unless they "
        "appeared in the provided session data."
    ),
    "bina": (
        "You are designing tomorrow's opening scene for Bina Malek "
        "(ISFJ-A, Si-declarative diagnostic register). Return a short "
        "narrator script (2-3 sentences) describing the shop / kitchen "
        "setting, and 2-3 choice branches labelled 'Branch: <option>'. "
        "No em-dashes. Narrator voice is observational. Do not mention "
        "any other character by name unless they appeared in the "
        "provided session data."
    ),
    "reina": (
        "You are designing tomorrow's opening scene for Reina Torres "
        "(ESTP-A, Se-tactical admissibility register). Return a short "
        "narrator script (2-3 sentences) describing the courthouse / "
        "gym / home setting, and 2-3 choice branches labelled 'Branch: "
        "<option>'. No em-dashes. Narrator voice is observational. "
        "Do not mention any other character by name unless they "
        "appeared in the provided session data."
    ),
    "alicia": (
        "You are designing tomorrow's opening scene for Alicia Marin "
        "(ESFP-A, Se-somatic body-first register). Return a short "
        "narrator script (2-3 sentences) describing the home / "
        "consulate / operation setting depending on her current "
        "is_away state, and 2-3 choice branches labelled 'Branch: "
        "<option>'. No em-dashes. Narrator voice is observational. "
        "Do not mention any other character by name unless they "
        "appeared in the provided session data."
    ),
}


def _build_user_prompt(ctx: GenerationContext) -> str:
    from datetime import timedelta

    tomorrow = (ctx.now + timedelta(days=1)).date()
    weekday = tomorrow.strftime("%A").lower()
    is_weekend = weekday in {"saturday", "sunday"}
    blocks = ctx.routines.weekend if is_weekend else ctx.routines.weekday

    is_away = bool(getattr(ctx.prior_session.life_state, "is_away", False))

    lines = [
        f"Tomorrow's date: {tomorrow.isoformat()} ({weekday})",
        f"Character: {ctx.character_id}",
        f"is_away: {is_away}",
    ]
    lines.append("\nTomorrow's anchor routine:")
    for b in blocks[:4]:
        lines.append(f"  - {b.time}: {b.activity}")

    if ctx.prior_session.episodic_memories:
        lines.append("\nYour recent episodics:")
        for em in ctx.prior_session.episodic_memories[:4]:
            summary = getattr(em, "event_summary", str(em))
            lines.append(f"  - {summary}")

    lines.append(
        "\nDesign the opening now. Narrator script first (2-3 sentences). "
        "Then 2-3 'Branch: <option>' lines."
    )
    return "\n".join(lines)


def _parse_llm_output(raw: str) -> tuple[str, dict[str, object]]:
    """Split LLM output into narrator_script + choice_tree.

    Everything before the first 'Branch:' line is the narrator script.
    Each 'Branch:' line becomes a branch entry in the choice_tree.
    """
    narrator_lines: list[str] = []
    branches: list[dict[str, str]] = []
    for line in raw.splitlines():
        stripped = line.strip().lstrip("-").lstrip("•").lstrip("*").strip()
        if not stripped:
            continue
        lowered = stripped.lower()
        if "branch:" in lowered:
            idx = lowered.index("branch:") + len("branch:")
            option = stripped[idx:].strip()
            if option:
                branches.append({"option": option})
        elif not branches:
            # Only collect narrator lines until the first Branch appears.
            narrator_lines.append(stripped)
    narrator = " ".join(narrator_lines).strip() or raw.strip()
    return narrator, {"branches": branches[:3]}


async def generate_activity_design(ctx: GenerationContext) -> GenerationOutput:
    """Produce tomorrow's scene opener, routed through Phase G."""
    from ...context.prose import render_activity_prose

    system_prompt = _SYSTEM_PROMPTS.get(ctx.character_id)
    if system_prompt is None:
        return GenerationOutput(
            kind="activity_design",
            raw_llm_text="",
            rendered_prose="",
            structured_data={
                "scene_description": "",
                "narrator_script": "",
                "choice_tree": {},
            },
            input_tokens=0,
            output_tokens=0,
            warnings=[f"no activity_design system prompt for {ctx.character_id}"],
        )

    user_prompt = _build_user_prompt(ctx)

    try:
        completion = await ctx.llm_client.complete(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=350,
            temperature=0.7,
        )
    except DreamsLLMError as exc:
        return GenerationOutput(
            kind="activity_design",
            raw_llm_text="",
            rendered_prose="",
            structured_data={
                "scene_description": "",
                "narrator_script": "",
                "choice_tree": {},
            },
            input_tokens=0,
            output_tokens=0,
            warnings=[f"activity_design LLM failed: {exc}"],
        )

    raw = str(completion.text)
    narrator_script, choice_tree = _parse_llm_output(raw)
    rendered = render_activity_prose(ctx.character_id, narrator_script)

    is_away = bool(getattr(ctx.prior_session.life_state, "is_away", False))
    communication_mode: str | None = None
    if should_tag_alicia_away(ctx.character_id, is_away):
        seed_id = uuid.uuid5(
            uuid.NAMESPACE_OID,
            f"{ctx.character_id}:{ctx.now.isoformat()}",
        )
        communication_mode = pick_alicia_communication_mode(seed_id, "activity_design")

    scene_description = narrator_script[:200] if narrator_script else raw[:200]

    return GenerationOutput(
        kind="activity_design",
        raw_llm_text=raw,
        rendered_prose=rendered,
        structured_data={
            "scene_description": scene_description,
            "narrator_script": narrator_script,
            "choice_tree": choice_tree,
            "communication_mode": communication_mode,
        },
        input_tokens=int(completion.input_tokens),
        output_tokens=int(completion.output_tokens),
    )
