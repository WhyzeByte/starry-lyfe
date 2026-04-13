"""Per-layer formatter functions for the seven-layer context assembly."""

from __future__ import annotations

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
from .types import LayerContent, SceneState, VoiceExample, VoiceMode

_VOICE_GUIDANCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


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


def derive_active_voice_modes(scene: SceneState) -> list[VoiceMode]:
    """Map a SceneState to a list of active VoiceModes for exemplar selection.

    When ``scene.voice_modes`` is explicitly set, those modes are used
    directly (future Phase F integration). Otherwise, modes are derived
    from the existing scene state fields.
    """
    if scene.voice_modes is not None:
        return scene.voice_modes

    modes: list[VoiceMode] = [VoiceMode.DOMESTIC]

    if scene.public_scene:
        modes.append(VoiceMode.PUBLIC)

    char_count = len(scene.present_characters)
    if char_count > 2:
        modes.append(VoiceMode.GROUP)
    elif char_count == 2:
        modes.append(VoiceMode.SOLO_PAIR)

    return modes


def _select_voice_exemplars(
    examples: list[VoiceExample],
    active_modes: list[VoiceMode],
    communication_mode: str | None = None,
    max_exemplars: int = 2,
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

    if not candidates:
        return examples[:max_exemplars]

    # Step 2: mode overlap filter
    active_set = set(active_modes)
    mode_matched = [
        ex for ex in candidates
        if set(ex.modes) & active_set
    ]

    if not mode_matched:
        # Fallback: no mode overlap, return first candidates by file order
        return sorted(candidates, key=lambda ex: ex.index)[:max_exemplars]

    # Step 3: score and rank
    def score_key(ex: VoiceExample) -> tuple[int, int]:
        overlap = len(set(ex.modes) & active_set)
        return (-overlap, ex.index)

    mode_matched.sort(key=score_key)

    return mode_matched[:max_exemplars]


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
) -> LayerContent:
    """Layer 1: Section-aware kernel compilation preserving load-bearing sections."""
    text = load_kernel(character_id, budget=budget)
    return LayerContent(
        name="persona_kernel",
        text=text,
        estimated_tokens=estimate_tokens(text),
        layer_number=1,
    )


def format_canon_facts(
    facts: list[CanonFact],
    budget: int = DEFAULT_BUDGETS.canon_facts,
) -> LayerContent:
    """Layer 2: Format canon facts into a readable block, trimmed to budget."""
    if not facts:
        text = "No canon facts available."
    else:
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
    """Layer 4: Format biological/psychological state, active protocols, and environment."""
    lines: list[str] = []

    # P3-04: Include scene/environment description
    if scene_description:
        lines.append(f"Current scene: {scene_description}")

    if somatic_state is None:
        lines.append("No somatic state data available.")
    else:
        lines.extend([
            f"Current state for {somatic_state.character_id}:",
            f"  Fatigue: {somatic_state.fatigue:.2f}",
            f"  Stress residue: {somatic_state.stress_residue:.2f}",
            f"  Injury residue: {somatic_state.injury_residue:.2f}",
        ])
        if somatic_state.active_protocols:
            proto_names = []
            for proto_key in somatic_state.active_protocols:
                proto = canon.protocols.protocols.get(proto_key)
                name = proto.name if proto else proto_key
                proto_names.append(name)
            lines.append(f"  Active protocols: {', '.join(proto_names)}")
        else:
            lines.append("  No active protocols.")

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

    from starry_lyfe.canon.pairs_loader import format_pair_metadata

    pair_block = format_pair_metadata(character_id)
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
) -> LayerContent:
    """Layer 6: Format relationship state, open loops, and current scene activity."""
    sections: list[str] = []

    # Include scene/activity description
    if scene_description:
        sections.append(f"Current activity: {scene_description}")

    # Dyad state with Whyze
    for wd in dyads_whyze:
        sections.append(
            f"Relationship with Whyze ({wd.pair_name}): "
            f"trust={wd.trust:.2f}, intimacy={wd.intimacy:.2f}, "
            f"conflict={wd.conflict:.2f}, tension={wd.unresolved_tension:.2f}"
        )

    recalled = recalled_dyads or set()
    for iwd in dyads_internal:
        other = iwd.member_b if iwd.member_a == character_id else iwd.member_a
        dyad_key = f"{iwd.member_a}-{iwd.member_b}"
        dyad_key_rev = f"{iwd.member_b}-{iwd.member_a}"
        if other in present_characters or dyad_key in recalled or dyad_key_rev in recalled:
            sections.append(
                f"Relationship {iwd.member_a}-{iwd.member_b} ({iwd.interlock or 'n/a'}): "
                f"trust={iwd.trust:.2f}, intimacy={iwd.intimacy:.2f}, "
                f"conflict={iwd.conflict:.2f}"
            )

    # Open loops (already ranked by urgency from retrieval)
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
