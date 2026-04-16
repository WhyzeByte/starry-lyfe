"""Per-layer formatter functions for the seven-layer context assembly."""

from __future__ import annotations

import logging
import re
from collections.abc import Sequence
from typing import Any

from starry_lyfe.canon.loader import Canon
from starry_lyfe.db.models.canon_facts import CanonFact
from starry_lyfe.db.models.character_baseline import CharacterBaseline
from starry_lyfe.db.models.dyad_state_internal import DyadStateInternal
from starry_lyfe.db.models.dyad_state_whyze import DyadStateWhyze
from starry_lyfe.db.models.open_loop import OpenLoop
from starry_lyfe.db.retrieval import DecayedSomaticState

from .budgets import DEFAULT_BUDGETS, estimate_tokens, trim_text_to_budget, trim_to_budget
from .kernel_loader import load_kernel, load_voice_examples, load_voice_guidance
from .prose import (
    render_canon_prose,
    render_dyad_internal_prose,
    render_dyad_whyze_prose,
    render_protocol_prose,
    render_somatic_prose,
)
from .types import LayerContent, SceneState, SceneType, VoiceExample, VoiceMode

logger = logging.getLogger(__name__)

_VOICE_GUIDANCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_PUBLIC_CONTEXT_MODES: set[VoiceMode] = {
    VoiceMode.PUBLIC,
    VoiceMode.DOMESTIC,
    VoiceMode.GROUP,
    VoiceMode.SOLO_PAIR,
}
_PUBLIC_PRIVATE_MODES: set[VoiceMode] = {
    VoiceMode.INTIMATE,
    VoiceMode.ESCALATION,
    VoiceMode.SOLO_PAIR,
}


def _compact_voice_guidance_item(item: str) -> str:
    """Shrink a guidance item to the smallest useful runtime teaching note."""
    parts = item.split(": ", 2)
    if len(parts) == 3:
        label = f"{parts[0]}: {parts[1]}"
        guidance = parts[2].strip()
    else:
        label = ""
        guidance = item.strip()

    first_sentence = _VOICE_GUIDANCE_SPLIT_RE.split(guidance, maxsplit=1)[0].strip()
    if not first_sentence:
        first_sentence = guidance

    compact = f"{label}: {first_sentence}" if label else first_sentence
    return compact.strip()


_SCENE_TYPE_VOICE_MODES: dict[SceneType, list[VoiceMode]] = {
    SceneType.DOMESTIC: [VoiceMode.DOMESTIC],
    SceneType.INTIMATE: [VoiceMode.INTIMATE, VoiceMode.SOLO_PAIR],
    SceneType.CONFLICT: [VoiceMode.CONFLICT],
    SceneType.REPAIR: [VoiceMode.REPAIR, VoiceMode.SILENT],
    SceneType.PUBLIC: [VoiceMode.PUBLIC],
    SceneType.GROUP: [VoiceMode.GROUP],
    SceneType.SOLO_PAIR: [VoiceMode.SOLO_PAIR, VoiceMode.DOMESTIC],
    SceneType.TRANSITION: [VoiceMode.DOMESTIC],
}


def _add_domestic_context_modes(scene: SceneState, modes: list[VoiceMode]) -> None:
    """Accumulate legacy scene-context cues for domestic scenes."""
    if scene.public_scene and VoiceMode.PUBLIC not in modes:
        modes.append(VoiceMode.PUBLIC)

    char_count = len(scene.present_characters)
    if char_count > 2 and VoiceMode.GROUP not in modes:
        modes.append(VoiceMode.GROUP)
    elif char_count == 2 and VoiceMode.SOLO_PAIR not in modes:
        modes.append(VoiceMode.SOLO_PAIR)


def _has_active_modifiers(scene: SceneState) -> bool:
    """Return True if any modifier boolean is set or absent dyads are invoked."""
    m = scene.modifiers
    return (
        m.work_colleagues_present
        or m.post_intensity_crash_active
        or m.pair_escalation_active
        or m.warm_refusal_required
        or m.silent_register_active
        or m.group_temperature_shift
        or bool(m.explicitly_invoked_absent_dyad)
    )


def derive_active_voice_modes(scene: SceneState) -> list[VoiceMode]:
    """Map a SceneState to a list of active VoiceModes for exemplar selection.

    Priority: (1) explicit ``scene.voice_modes`` override, (2) SceneType
    mapping + modifier accumulation (Phase F), (3) legacy fallback from
    ``present_characters``/``public_scene`` when scene_type is DOMESTIC
    with no modifiers active (backward compat).
    """
    # Priority 1: explicit override
    if scene.voice_modes is not None:
        return scene.voice_modes

    # Priority 2: Phase F SceneType + modifier mapping
    # Fires when scene_type is non-DOMESTIC OR any modifier is active.
    if scene.scene_type != SceneType.DOMESTIC or _has_active_modifiers(scene):
        modes = list(_SCENE_TYPE_VOICE_MODES.get(scene.scene_type, [VoiceMode.DOMESTIC]))
        if scene.scene_type == SceneType.DOMESTIC:
            _add_domestic_context_modes(scene, modes)

        # Modifier accumulation (additive, not replacing)
        m = scene.modifiers
        if m.pair_escalation_active and VoiceMode.ESCALATION not in modes:
            modes.append(VoiceMode.ESCALATION)
        if m.warm_refusal_required and VoiceMode.WARM_REFUSAL not in modes:
            modes.append(VoiceMode.WARM_REFUSAL)
        if m.silent_register_active and VoiceMode.SILENT not in modes:
            modes.append(VoiceMode.SILENT)
        if m.group_temperature_shift and VoiceMode.GROUP_TEMPERATURE not in modes:
            modes.append(VoiceMode.GROUP_TEMPERATURE)
        if m.post_intensity_crash_active and VoiceMode.REPAIR not in modes:
            modes.append(VoiceMode.REPAIR)

        return modes

    # Priority 3: legacy fallback (DOMESTIC + no modifiers = pre-Phase-F behavior)
    modes = [VoiceMode.DOMESTIC]
    _add_domestic_context_modes(scene, modes)
    return modes


def _select_voice_exemplars(
    examples: list[VoiceExample],
    active_modes: list[VoiceMode],
    communication_mode: str | None = None,
    max_exemplars: int = 2,
    character_id: str = "",
) -> list[VoiceExample]:
    """Select voice exemplars by mode overlap, respecting communication mode.

    Algorithm:
    1. Filter by communication_mode (Phase A'' behavior preserved).
    2. Filter to examples tagged with at least one active mode.
    3. Score by mode overlap count, rank by score desc then file order.
    4. Take up to max_exemplars.
    5. Fallback: first 2 by file order if no mode matches.
    """
    # Step 1: communication mode filter
    if communication_mode:
        candidates = [
            ex for ex in examples
            if ex.communication_mode in (communication_mode, "any")
        ]
    else:
        candidates = list(examples)

    # L1: defense-in-depth fallback. In production corpora every example
    # carries communication_mode="any" by default (see
    # kernel_loader._extract_voice_examples), so the comm-mode filter
    # cannot empty the candidate list today. This branch survives in case
    # a future Voice.md author writes ONLY mode-specific exemplars and
    # callers request a mode with no canonical coverage. Returning raw
    # examples[:max_exemplars] preserves the contract that Layer 5 always
    # emits something rather than crashing on the slice.
    if not candidates:
        selected = examples[:max_exemplars]
        logger.debug(
            "voice_exemplar_selection: fallback (no comm-mode candidates)",
            extra={
                "character_id": character_id,
                "active_modes": [m.value for m in active_modes],
                "candidates_count": 0,
                "mode_matched_count": 0,
                "selected_titles": [ex.title for ex in selected],
            },
        )
        return selected

    # Step 2: mode overlap filter
    active_set = set(active_modes)
    mode_matched = [
        ex for ex in candidates
        if set(ex.modes) & active_set
    ]

    def public_penalty(ex: VoiceExample, *, has_explicit_public: bool) -> int:
        """Penalize private-register fallbacks when PUBLIC is active.

        If a scene activates PUBLIC but the corpus has no explicit public-tagged
        exemplar for the current candidate set, prefer examples that do not drag
        Layer 5 toward private one-on-one or intimate registers by accident.

        Examples that match a more specific active mode such as WARM_REFUSAL,
        REPAIR, or GROUP_TEMPERATURE keep priority even if they also carry a
        contextual private tag like SOLO_PAIR.
        """
        if VoiceMode.PUBLIC not in active_set or has_explicit_public:
            return 0
        example_modes = set(ex.modes)
        specific_active = active_set - _PUBLIC_CONTEXT_MODES
        if example_modes & specific_active:
            return 0
        return 1 if example_modes & _PUBLIC_PRIVATE_MODES else 0

    if not mode_matched:
        # Fallback: no mode overlap, return first candidates by file order
        has_explicit_public = any(VoiceMode.PUBLIC in ex.modes for ex in candidates)
        selected = sorted(
            candidates,
            key=lambda ex: (public_penalty(ex, has_explicit_public=has_explicit_public), ex.index),
        )[:max_exemplars]
        logger.debug(
            "voice_exemplar_selection: fallback (no mode overlap)",
            extra={
                "character_id": character_id,
                "active_modes": [m.value for m in active_modes],
                "candidates_count": len(candidates),
                "mode_matched_count": 0,
                "public_safe_fallback": (
                    VoiceMode.PUBLIC in active_set and not has_explicit_public
                ),
                "selected_titles": [ex.title for ex in selected],
            },
        )
        return selected

    # Step 3: score and rank
    priority_set = active_set - {VoiceMode.DOMESTIC}
    has_explicit_public = any(VoiceMode.PUBLIC in ex.modes for ex in mode_matched)

    def score_key(ex: VoiceExample) -> tuple[int, int, int, int]:
        example_modes = set(ex.modes)
        priority_overlap = len(example_modes & priority_set)
        total_overlap = len(example_modes & active_set)
        return (
            public_penalty(ex, has_explicit_public=has_explicit_public),
            -priority_overlap,
            -total_overlap,
            ex.index,
        )

    mode_matched.sort(key=score_key)

    selected = mode_matched[:max_exemplars]
    logger.debug(
        "voice_exemplar_selection",
        extra={
            "character_id": character_id,
            "active_modes": [m.value for m in active_modes],
            "candidates_count": len(candidates),
            "mode_matched_count": len(mode_matched),
            "public_safe_ranking": (
                VoiceMode.PUBLIC in active_set and not has_explicit_public
            ),
            "selected_titles": [ex.title for ex in selected],
        },
    )
    return selected


def _format_voice_exemplar(example: VoiceExample) -> str:
    """Format a selected VoiceExample as a runtime Layer 5 entry."""
    modes_str = ", ".join(str(m) for m in example.modes)
    if example.abbreviated_text:
        return f"{example.title} [{modes_str}]: {example.abbreviated_text}"
    # Fallback: compact teaching note
    if example.teaching_prose:
        compact = _compact_voice_guidance_item(
            f"{example.title}: {example.teaching_prose}"
        )
        return compact
    return example.title


def format_kernel(
    character_id: str,
    budget: int = DEFAULT_BUDGETS.kernel,
    promote_sections: list[int] | None = None,
    profile_name: str | None = None,
) -> LayerContent:
    """Layer 1: Section-aware kernel compilation preserving load-bearing sections."""
    text = load_kernel(
        character_id,
        budget=budget,
        promote_sections=promote_sections,
        profile_name=profile_name,
    )
    return LayerContent(
        name="persona_kernel",
        text=text,
        estimated_tokens=estimate_tokens(text),
        layer_number=1,
    )


def format_canon_facts(
    facts: list[CanonFact],
    budget: int = DEFAULT_BUDGETS.canon_facts,
    character_id: str = "",
) -> LayerContent:
    """Layer 2: Format canon facts as a narrative paragraph (Phase G), trimmed to budget."""
    if not facts:
        text = "No canon facts available."
    elif character_id:
        text = render_canon_prose(character_id, facts)
        text = trim_text_to_budget(text, budget, "[Canon facts trimmed to token budget.]")
    else:
        # Fallback: flat list when character_id is unknown
        header = "Canon facts for this character:\n"
        remaining = max(1, budget - estimate_tokens(header))
        lines = [f"- {f.fact_key}: {f.fact_value}" for f in facts]
        trimmed = trim_to_budget(lines, remaining)
        text = header + "\n".join(trimmed)
        text = trim_text_to_budget(text, budget, "[Canon facts trimmed to token budget.]")
    return LayerContent(
        name="canon_facts",
        text=text,
        estimated_tokens=estimate_tokens(text),
        layer_number=2,
    )


def format_memory_fragments(
    episodic_memories: Sequence[Any],
    budget: int = DEFAULT_BUDGETS.episodic,
) -> LayerContent:
    """Layer 3: Format episodic memories, trimmed to budget by relevance rank."""
    if not episodic_memories:
        text = "No relevant episodic memories for this scene."
    else:
        header = "Relevant memories from past interactions:\n"
        remaining = max(1, budget - estimate_tokens(header))
        summaries = []
        for mem in episodic_memories:
            summary = getattr(mem, "event_summary", str(mem))
            temp = getattr(mem, "emotional_temperature", None)
            temp_str = f" [emotional temperature: {temp:.1f}]" if temp is not None else ""
            summaries.append(f"- {summary}{temp_str}")
        trimmed = trim_to_budget(summaries, remaining)
        text = header + "\n".join(trimmed)
        text = trim_text_to_budget(text, budget, "[Memory fragments trimmed to token budget.]")
    return LayerContent(
        name="memory_fragments",
        text=text,
        estimated_tokens=estimate_tokens(text),
        layer_number=3,
    )


def format_sensory_grounding(
    somatic_state: DecayedSomaticState | None,
    canon: Canon,
    scene_description: str = "",
    budget: int = DEFAULT_BUDGETS.somatic,
) -> LayerContent:
    """Layer 4: Format somatic state and environment in per-character prose (Phase G)."""
    lines: list[str] = []

    if scene_description:
        lines.append(f"Current scene: {scene_description}")

    if somatic_state is None:
        lines.append("No somatic state data available.")
    else:
        # Phase G: character-voiced prose + numeric block
        lines.append(render_somatic_prose(somatic_state.character_id, somatic_state))

        if somatic_state.active_protocols:
            for proto_key in somatic_state.active_protocols:
                proto_prose = render_protocol_prose(somatic_state.character_id, proto_key)
                if proto_prose:
                    lines.append(proto_prose)
                else:
                    proto = canon.protocols.protocols.get(proto_key)
                    name = proto.name if proto else proto_key
                    lines.append(f"Active protocol: {name}.")

    text = "\n".join(lines)
    text = trim_text_to_budget(text, budget, "[Sensory grounding trimmed to token budget.]")
    return LayerContent(
        name="sensory_grounding",
        text=text,
        estimated_tokens=estimate_tokens(text),
        layer_number=4,
    )


def format_voice_directives(
    character_id: str,
    baseline: CharacterBaseline | None,
    budget: int = DEFAULT_BUDGETS.voice,
    communication_mode: str | None = None,
    scene_state: SceneState | None = None,
) -> LayerContent:
    """Layer 5: Format voice directives and calibration material.

    Includes metadata from CharacterBaseline plus voice exemplars or
    calibration notes from the canonical Voice.md files.

    When Voice.md files contain mode tags (Phase E), uses mode-aware
    exemplar selection. Otherwise falls back to the existing compact
    teaching note path for backward compatibility.
    """
    sections: list[str] = []
    remaining = budget

    from starry_lyfe.canon.rich_loader import format_pair_metadata_from_rich

    pair_block = format_pair_metadata_from_rich(character_id)
    pair_tokens = estimate_tokens(pair_block)
    sections.append(pair_block)
    remaining = max(0, remaining - pair_tokens - 3)

    if baseline is not None:
        voice = baseline.voice_params
        metadata_text = (
            f"Voice directives for {baseline.full_name} ({baseline.epithet}). "
            f"{baseline.mbti}, {baseline.dominant_function}-dominant. "
            f"Pair: {baseline.pair_name}. "
            f"Response length: {voice.get('response_length_range', 'default')}. "
            f"Register: {voice.get('dominant_function_descriptor', '')}. "
            f"Background: {baseline.heritage}; {baseline.profession}."
        )
        metadata_text = trim_text_to_budget(
            metadata_text,
            remaining,
            "[Voice directives trimmed to token budget.]",
        )
        sections.append(metadata_text)
        remaining = max(0, remaining - estimate_tokens(metadata_text) - 3)

    # Phase E: try mode-aware exemplar selection first
    voice_section_added = False
    if remaining > 0:
        voice_examples = load_voice_examples(character_id)
        has_mode_tags = voice_examples and any(ex.modes for ex in voice_examples)

        if has_mode_tags and voice_examples:
            active_modes = (
                derive_active_voice_modes(scene_state)
                if scene_state is not None
                else [VoiceMode.DOMESTIC]
            )
            selected = _select_voice_exemplars(
                voice_examples,
                active_modes=active_modes,
                communication_mode=communication_mode,
                character_id=character_id,
            )
            if selected:
                formatted = [_format_voice_exemplar(ex) for ex in selected]
                header = "Voice rhythm exemplars:\n"
                header_tokens = estimate_tokens(header)
                if remaining > header_tokens:
                    item_format_overhead = min(len(formatted), 4) * 2
                    remaining_for_items = remaining - header_tokens - item_format_overhead
                    chosen_items = trim_to_budget(formatted, remaining_for_items)
                    if chosen_items:
                        sections.append(
                            header + "\n".join(f"- {item}" for item in chosen_items)
                        )
                        voice_section_added = True

    # Fallback: existing compact teaching note path (pre-Phase E)
    if not voice_section_added and remaining > 0:
        guidance_items = load_voice_guidance(
            character_id, communication_mode=communication_mode
        )
        if guidance_items:
            compact_items = [_compact_voice_guidance_item(item) for item in guidance_items]
            header = "Voice calibration guidance:\n"
            header_tokens = estimate_tokens(header)
            if remaining > header_tokens:
                item_format_overhead = min(len(compact_items), 10) * 2
                remaining_for_items = remaining - header_tokens - item_format_overhead
                chosen_items = trim_to_budget(compact_items, remaining_for_items)
                if not chosen_items:
                    chosen_items = [
                        trim_text_to_budget(
                            compact_items[0],
                            remaining_for_items,
                            "[Voice guidance trimmed to token budget.]",
                        )
                    ]
                sections.append(
                    header + "\n".join(f"- {item}" for item in chosen_items)
                )

    text = "\n\n".join(sections) if sections else "No voice directive data available."
    text = trim_text_to_budget(text, budget, "[Voice layer trimmed to token budget.]")
    return LayerContent(
        name="voice_directives",
        text=text,
        estimated_tokens=estimate_tokens(text),
        layer_number=5,
    )


def format_scene_blocks(
    character_id: str,
    dyads_whyze: list[DyadStateWhyze],
    dyads_internal: list[DyadStateInternal],
    open_loops: list[OpenLoop],
    present_characters: list[str],
    scene_description: str = "",
    budget: int = DEFAULT_BUDGETS.scene,
    recalled_dyads: set[str] | None = None,
    explicitly_invoked_absent_dyad: frozenset[str] | None = None,
    dreams_activities: list[Any] | None = None,
) -> LayerContent:
    """Layer 6: Format relationship state and scene context in per-character prose (Phase G).

    Phase 6 R3-F2: when ``dreams_activities`` contains Dreams-written
    Activity rows, the most recent row's narrator_script is prepended
    to the layer as "Today's Dreams scene opener:". This closes the
    Dreams -> assembler consumer path: retrieval surfaces the Tier 8
    data, and Layer 6 renders it so the model sees Dreams output on
    the next turn.
    """
    sections: list[str] = []

    if scene_description:
        sections.append(f"Current activity: {scene_description}")

    # Phase 6 R3-F2: inject Dreams-generated activity narrator script
    # when present. The retrieval layer supplies dreams_activities
    # sorted most-recent-first; we render only the top entry.
    if dreams_activities:
        top = dreams_activities[0]
        narrator = getattr(top, "narrator_script", None)
        if narrator:
            sections.append(f"Today's Dreams scene opener:\n{narrator}")

    # Phase G: character-voiced dyad prose + numeric block
    for wd in dyads_whyze:
        sections.append(render_dyad_whyze_prose(character_id, wd))

    recalled = recalled_dyads or set()
    invoked = explicitly_invoked_absent_dyad or frozenset()
    for iwd in dyads_internal:
        other = iwd.member_b if iwd.member_a == character_id else iwd.member_a
        dyad_key = f"{iwd.member_a}-{iwd.member_b}"
        dyad_key_rev = f"{iwd.member_b}-{iwd.member_a}"
        if (
            other in present_characters
            or dyad_key in recalled
            or dyad_key_rev in recalled
            or dyad_key in invoked
            or dyad_key_rev in invoked
        ):
            sections.append(render_dyad_internal_prose(character_id, iwd))

    if open_loops:
        loop_lines = [f"- [{loop.urgency}] {loop.loop_summary}" for loop in open_loops]
        trimmed = trim_to_budget(loop_lines, budget // 2)
        if trimmed:
            sections.append("Open threads to address:\n" + "\n".join(trimmed))

    text = "\n".join(sections) if sections else "No scene context data available."
    text = trim_text_to_budget(text, budget, "[Scene context trimmed to token budget.]")
    return LayerContent(
        name="scene_blocks",
        text=text,
        estimated_tokens=estimate_tokens(text),
        layer_number=6,
    )
