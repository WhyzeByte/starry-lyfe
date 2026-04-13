"""Generate canon-seeded local Phase E sample artifacts.

These artifacts use the real ``assemble_context()`` path with a local
MemoryBundle stub derived from canon YAML plus curated sample episodics
and open loops. PostgreSQL-backed retrieval is not available in local
audit environments, so these files are explicit verification samples,
not live database retrieval outputs.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.canon.schemas.enums import CharacterID
from starry_lyfe.context import assembler as assembler_module
from starry_lyfe.context.assembler import assemble_context
from starry_lyfe.context.kernel_loader import clear_kernel_cache
from starry_lyfe.context.types import CommunicationMode, SceneState, VoiceMode

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "Docs" / "_phases" / "_samples"
TODAY = date.today().isoformat()


class _StubEmbeddingService:
    async def embed(self, text: str) -> list[float]:
        return [0.0] * 768

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * 768 for _ in texts]


@dataclass(frozen=True)
class SampleSpec:
    character_id: str
    scene_context: str
    scene_state: SceneState
    scene_profile: str = "default"


SAMPLE_SPECS: tuple[SampleSpec, ...] = (
    SampleSpec(
        character_id="adelia",
        scene_context="Adelia, Bina, Reina, and Whyze are gathered at the kitchen island after a long day.",
        scene_state=SceneState(
            present_characters=["adelia", "bina", "reina", "whyze"],
            scene_description="Kitchen island; late wine; permit binder pushed aside for dinner.",
            communication_mode=CommunicationMode.IN_PERSON,
            voice_modes=[VoiceMode.GROUP, VoiceMode.DOMESTIC],
        ),
    ),
    SampleSpec(
        character_id="bina",
        scene_context="Bina and Whyze are in the kitchen after the shop closes, the house finally quiet.",
        scene_state=SceneState(
            present_characters=["bina", "whyze"],
            scene_description="Kitchen after the shop closes; coffee still warm; house finally quiet.",
            communication_mode=CommunicationMode.IN_PERSON,
            voice_modes=[VoiceMode.DOMESTIC, VoiceMode.REPAIR, VoiceMode.SOLO_PAIR],
        ),
    ),
    SampleSpec(
        character_id="reina",
        scene_context="Reina catches Whyze alone at the trailhead after he has been thinking too long.",
        scene_state=SceneState(
            present_characters=["reina", "whyze"],
            scene_description="Trailhead at dusk; brushes cooling; truck idling nearby.",
            communication_mode=CommunicationMode.IN_PERSON,
            voice_modes=[VoiceMode.ESCALATION, VoiceMode.INTIMATE, VoiceMode.SOLO_PAIR],
        ),
        scene_profile="pair_intimate",
    ),
    SampleSpec(
        character_id="alicia",
        scene_context="Alicia calls late from an operation because the day was too much to carry alone.",
        scene_state=SceneState(
            present_characters=["alicia", "whyze"],
            scene_description="Remote phone call after midnight; hotel balcony door cracked for air.",
            communication_mode=CommunicationMode.PHONE,
            alicia_home=False,
            voice_modes=[VoiceMode.INTIMATE, VoiceMode.SOLO_PAIR],
        ),
    ),
)


_EPISODIC_SUMMARIES: dict[str, list[tuple[str, float]]] = {
    "adelia": [
        ("She dragged the permit binder to the kitchen and made him sequence the impossible parts out loud.", 0.58),
        (
            "She left the warehouse door unlocked on purpose so he would find the exact "
            "version of her she meant to offer.",
            0.72,
        ),
        ("She and Reina turned a hike into a pressure-release valve before the argument could harden.", 0.64),
        ("She translated a spiraling idea into a build plan only after he gave her the route.", 0.51),
    ],
    "bina": [
        ("She left the hall light on, covered a plate, and waited on the loveseat without announcing any of it.", 0.61),
        ("She killed a bad plan in one sentence and took the hit because safety mattered more than comfort.", 0.67),
        ("She steadied the house with sequence, heat, and locks while grief stayed under the surface.", 0.55),
        ("She read Reina's load state early and gave task before talk.", 0.49),
    ],
    "reina": [
        ("She crossed the room already knowing which sentence would cut cleanest through his loop.", 0.68),
        ("She turned a dinner story into cross-examination and the whole kitchen woke up under it.", 0.57),
        ("She held a long silence after a hard verdict and made that silence feel chosen, not empty.", 0.62),
        ("She redirected trailhead friction into motion before it could become theatre.", 0.71),
    ],
    "alicia": [
        (
            "She called because she trusted him with ordinary detail more than she trusted "
            "herself with the whole day.",
            0.66,
        ),
        ("She refused an operational disclosure without apology and stayed warm the whole time.", 0.54),
        (
            "She returned from travel, put her forehead to his sternum, and let the body "
            "arrive before the words did.",
            0.73,
        ),
        ("She changed the room temperature by choosing where to set the bowl of olives and when to sit down.", 0.47),
    ],
}


_OPEN_LOOPS: dict[str, list[tuple[str, str]]] = {
    "adelia": [
        ("high", "Lock the permit timeline before the Friday fabrication window closes."),
        ("medium", "Decide whether the kitchen-island conversation becomes a full warehouse redesign."),
    ],
    "bina": [
        ("high", "Re-check the lift schedule before the morning bay opens."),
        ("medium", "Finish the conversation about what gets carried and what gets put down tonight."),
    ],
    "reina": [
        ("high", "Choose whether the client call happens tonight or after first coffee."),
        ("medium", "Resolve the argument that almost started at the trailhead."),
    ],
    "alicia": [
        ("high", "Call back after dawn if the room still feels wrong when the city wakes up."),
        ("medium", "Say what she can about the trip without crossing the operational line."),
    ],
}


_SOMATIC_STATES: dict[str, dict[str, float]] = {
    "adelia": {"fatigue": 0.38, "stress_residue": 0.22, "injury_residue": 0.00},
    "bina": {"fatigue": 0.44, "stress_residue": 0.19, "injury_residue": 0.05},
    "reina": {"fatigue": 0.35, "stress_residue": 0.27, "injury_residue": 0.00},
    "alicia": {"fatigue": 0.52, "stress_residue": 0.31, "injury_residue": 0.00},
}


def _canon_character(canon: Any, character_id: str) -> Any:
    return canon.characters.characters[CharacterID(character_id)]


def _build_canon_facts(canon: Any, character_id: str) -> list[Any]:
    char = _canon_character(canon, character_id)
    facts: list[tuple[str, str]] = [
        ("full_name", char.full_name),
        ("epithet", char.epithet),
        ("mbti", char.mbti),
        ("heritage", char.heritage),
        ("birthplace", char.birthplace),
        ("current_residence", char.current_residence),
        ("pair_name", str(char.pair_name)),
        ("profession", char.profession),
        ("dominant_function", str(char.dominant_function)),
    ]
    if getattr(char, "operational_travel", None):
        facts.append(("operational_travel", char.operational_travel))
    if getattr(char, "children", None):
        facts.append(("children", ", ".join(child.name for child in char.children)))
    return [SimpleNamespace(fact_key=key, fact_value=value) for key, value in facts]


def _build_baseline(canon: Any, character_id: str) -> Any:
    char = _canon_character(canon, character_id)
    pair = canon.pairs.pairs[char.pair_name]
    voice = canon.voice_parameters.voice_parameters[CharacterID(character_id)]
    return SimpleNamespace(
        full_name=char.full_name,
        epithet=char.epithet,
        mbti=char.mbti,
        dominant_function=str(char.dominant_function),
        pair_name=str(char.pair_name),
        pair_classification=pair.classification,
        pair_mechanism=pair.mechanism,
        pair_core_metaphor=pair.core_metaphor,
        heritage=char.heritage,
        profession=char.profession,
        voice_params={
            "response_length_range": voice.response_length_range,
            "dominant_function_descriptor": voice.dominant_function_descriptor,
        },
    )


def _build_whyze_dyad(canon: Any, character_id: str) -> list[Any]:
    dyad = canon.dyads.dyads[f"whyze_{character_id}"]
    return [
        SimpleNamespace(
            pair_name=str(dyad.pair),
            trust=dyad.dimensions.trust.baseline,
            intimacy=dyad.dimensions.intimacy.baseline,
            conflict=dyad.dimensions.conflict.baseline,
            unresolved_tension=dyad.dimensions.unresolved_tension.baseline,
        )
    ]


def _build_internal_dyads(canon: Any, character_id: str) -> list[Any]:
    rows: list[Any] = []
    for dyad_key, dyad in canon.dyads.dyads.items():
        members = [member.value if hasattr(member, "value") else str(member) for member in dyad.members]
        if "whyze" in dyad_key or character_id not in members:
            continue
        is_active = True if dyad.is_currently_active is None else bool(dyad.is_currently_active)
        rows.append(
            SimpleNamespace(
                member_a=members[0],
                member_b=members[1],
                interlock=dyad.interlock,
                trust=dyad.dimensions.trust.baseline,
                intimacy=dyad.dimensions.intimacy.baseline,
                conflict=dyad.dimensions.conflict.baseline,
                unresolved_tension=dyad.dimensions.unresolved_tension.baseline,
                is_currently_active=is_active,
            )
        )
    return rows


def _build_episodics(character_id: str) -> list[Any]:
    return [
        SimpleNamespace(event_summary=summary, emotional_temperature=temp)
        for summary, temp in _EPISODIC_SUMMARIES[character_id]
    ]


def _build_open_loops(character_id: str) -> list[Any]:
    return [
        SimpleNamespace(urgency=urgency, loop_summary=summary)
        for urgency, summary in _OPEN_LOOPS[character_id]
    ]


def _build_somatic(character_id: str) -> Any:
    state = _SOMATIC_STATES[character_id]
    return SimpleNamespace(
        character_id=character_id,
        fatigue=state["fatigue"],
        stress_residue=state["stress_residue"],
        injury_residue=state["injury_residue"],
        active_protocols=[],
    )


def _build_bundle(canon: Any, character_id: str) -> Any:
    return SimpleNamespace(
        canon_facts=_build_canon_facts(canon, character_id),
        character_baseline=_build_baseline(canon, character_id),
        dyad_states_whyze=_build_whyze_dyad(canon, character_id),
        dyad_states_internal=_build_internal_dyads(canon, character_id),
        episodic_memories=_build_episodics(character_id),
        open_loops=_build_open_loops(character_id),
        somatic_state=_build_somatic(character_id),
    )


def _header_lines(spec: SampleSpec, total_tokens: int, anchor: str) -> str:
    voice_modes = (
        ", ".join(mode.value for mode in spec.scene_state.voice_modes)
        if spec.scene_state.voice_modes
        else "derived from scene state"
    )
    return "\n".join([
        f"# PHASE E ASSEMBLED PROMPT - {spec.character_id.upper()}",
        f"# Generated: {TODAY} via canon-seeded local sample bundle",
        "# Retrieval provenance: assemble_context() with PostgreSQL retrieval replaced by local canonical sample data.",
        "# Sample class: local verification artifact for QA review while integration retrieval is unavailable.",
        f"# Scene: {spec.scene_context}",
        f"# Communication mode: {spec.scene_state.communication_mode.value}",
        f"# Voice modes: {voice_modes}",
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
        output_path = OUTPUT_DIR / f"PHASE_E_assembled_{spec.character_id}_{TODAY}.txt"
        output_path.write_text(rendered, encoding="utf-8")
        print(output_path)


if __name__ == "__main__":
    asyncio.run(main())
