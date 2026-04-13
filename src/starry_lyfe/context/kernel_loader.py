"""Load backend-safe kernel and voice guidance documents from the filesystem."""

from __future__ import annotations

import re
from pathlib import Path

from ..canon.soul_essence import format_soul_essence
from .budgets import estimate_tokens, trim_text_to_budget
from .types import VoiceExample, VoiceMode

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

KERNEL_PATHS: dict[str, str] = {
    "adelia": "Characters/Adelia/Adelia_Raye_v7.1.md",
    "bina": "Characters/Bina/Bina_Malek_v7.1.md",
    "reina": "Characters/Reina/Reina_Torres_v7.1.md",
    "alicia": "Characters/Alicia/Alicia_Marin_v7.1.md",
}

VOICE_PATHS: dict[str, str] = {
    "adelia": "Characters/Adelia/Adelia_Raye_Voice.md",
    "bina": "Characters/Bina/Bina_Malek_Voice.md",
    "reina": "Characters/Reina/Reina_Torres_Voice.md",
    "alicia": "Characters/Alicia/Alicia_Marin_Voice.md",
}

# Kernel section budgets tuned for the 2000-token runtime window.
# The goal is not to include whole documents. It is to ensure each runtime
# kernel still carries identity substrate, pair mechanics, and protocol surface.
SECTION_TOKEN_TARGETS: dict[int, int] = {
    1: 300,   # Runtime Directives
    2: 900,   # Core Identity (soul substrate — PRESERVE-marked paragraphs live here)
    3: 1000,  # Whyze / Pair section
    4: 250,   # Silent Routing
    5: 900,   # Behavioral Tier Framework
    7: 550,   # Emotional / Relational / Operational Frameworks
    6: 300,   # Voice Architecture
}

PRIMARY_SECTION_ORDER: list[int] = [1, 2, 3, 4, 5, 7, 6]
EXPANSION_SECTION_ORDER: list[int] = [2, 3, 5, 7, 6, 8, 9, 10, 11]
FILL_SECTION_ORDER: list[int] = [8, 9, 10, 11]

_kernel_cache: dict[str, str] = {}
_voice_raw_cache: dict[str, list[tuple[str, str]] | None] = {}

_SECTION_RE = re.compile(r"^## (\d+)\.")


def _sanitize_kernel_text(raw_text: str) -> str:
    """Remove frontend-specific kernel scaffolding before backend assembly."""
    filtered_lines: list[str] = []
    for line in raw_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# SYSTEM_ROLE:"):
            continue
        if stripped.startswith("**Version:**"):
            continue
        if stripped.startswith("**Target:**"):
            continue
        filtered_lines.append(line)
    while filtered_lines and not filtered_lines[0].strip():
        filtered_lines.pop(0)
    return "\n".join(filtered_lines).strip()


def _parse_kernel_sections(text: str) -> list[tuple[int, str]]:
    """Parse a sanitized kernel into numbered sections.

    Returns a list of (section_number, section_text) tuples.
    Content before the first ## header is included as section 0.
    """
    sections: list[tuple[int, str]] = []
    current_num = 0
    current_lines: list[str] = []

    for line in text.splitlines():
        match = _SECTION_RE.match(line)
        if match:
            if current_lines:
                sections.append((current_num, "\n".join(current_lines).strip()))
            current_num = int(match.group(1))
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_num, "\n".join(current_lines).strip()))

    return sections


def compile_kernel(character_id: str, budget: int) -> str:
    """Section-aware kernel compilation.

    The runtime kernel must carry more than pair mechanics alone. This
    compiler gives the live prompt bounded excerpts from core identity,
    pair dynamics, routing, behavior rails, and protocol surface so the
    character still feels like herself inside a tight token window.
    """
    raw = _load_raw_kernel(character_id)
    sanitized = _sanitize_kernel_text(raw)
    sections = _parse_kernel_sections(sanitized)
    section_map = {
        num: text
        for num, text in sections
        if num > 0
    }

    # Allocate the baseline runtime slice for each primary section first.
    allocated_budgets: dict[int, int] = {}
    allocated_total = 0
    for num in PRIMARY_SECTION_ORDER:
        text = section_map.get(num)
        if not text:
            continue
        full_tokens = estimate_tokens(text)
        target_tokens = min(SECTION_TOKEN_TARGETS[num], full_tokens)
        allocated_budgets[num] = target_tokens
        allocated_total += target_tokens

    remaining = max(0, budget - allocated_total)

    # If the caller asked for a larger kernel window, spend the extra budget
    # by expanding identity and protocol sections before low-priority lore.
    for num in EXPANSION_SECTION_ORDER:
        if remaining <= 0:
            break
        text = section_map.get(num)
        if not text:
            continue
        full_tokens = estimate_tokens(text)
        current_tokens = allocated_budgets.get(num, 0)
        if full_tokens <= current_tokens:
            continue
        extra_tokens = min(full_tokens - current_tokens, remaining)
        allocated_budgets[num] = current_tokens + extra_tokens
        remaining -= extra_tokens

    assembled: list[str] = []

    for num in PRIMARY_SECTION_ORDER:
        text = section_map.get(num)
        if not text:
            continue
        section_budget = allocated_budgets.get(num, 0)
        trimmed = trim_text_to_budget(text, section_budget, strict=True)
        if trimmed and estimate_tokens(trimmed) > 10:
            assembled.append(trimmed)

    for num in FILL_SECTION_ORDER:
        text = section_map.get(num)
        if not text:
            continue
        section_budget = allocated_budgets.get(num, 0)
        if section_budget <= 0:
            continue
        trimmed = trim_text_to_budget(text, section_budget)
        if trimmed and estimate_tokens(trimmed) > 10:
            assembled.append(trimmed)

    result = "\n\n".join(assembled)
    if estimate_tokens(result) > budget:
        result = trim_text_to_budget(result, budget, strict=True)
    return result


def compile_kernel_with_soul(character_id: str, budget: int) -> str:
    """Return compiled kernel prepended with guaranteed soul essence.

    Soul essence is load-bearing canonical prose that must reach every
    prompt for the focal character regardless of trim pressure. It rides
    alongside the compiled kernel and is NEVER subject to the kernel
    trim budget - the budget governs only the trimmable kernel body.

    Use this function at the assembler layer (Layer 1) when building
    the final prompt. Use compile_kernel() directly when you want only
    the budget-bounded kernel body (e.g., for budget regression tests).
    """
    kernel_body = compile_kernel(character_id, budget)
    soul = format_soul_essence(character_id)
    if not soul:
        return kernel_body
    return soul + "\n\n" + kernel_body


def _load_raw_kernel(character_id: str) -> str:
    """Load raw kernel text from filesystem."""
    rel_path = KERNEL_PATHS.get(character_id)
    if rel_path is None:
        msg = f"No kernel path defined for character '{character_id}'"
        raise ValueError(msg)
    full_path = PROJECT_ROOT / rel_path
    if not full_path.exists():
        msg = f"Kernel file not found: {full_path}"
        raise FileNotFoundError(msg)
    return full_path.read_text(encoding="utf-8")


def load_kernel(character_id: str, budget: int = 2000) -> str:
    """Load a section-compiled character kernel with guaranteed soul essence.

    Returns the compiled kernel body (budget-bounded) with the character's
    canonical soul essence prepended. Soul essence is load-bearing
    substrate that rides alongside the kernel and is not subject to the
    trim budget. The budget parameter governs only the trimmable kernel
    body. Cached after first load.
    """
    cache_key = f"{character_id}:{budget}"
    if cache_key in _kernel_cache:
        return _kernel_cache[cache_key]
    text = compile_kernel_with_soul(character_id, budget)
    _kernel_cache[cache_key] = text
    return text


def load_kernel_body_only(character_id: str, budget: int = 2000) -> str:
    """Load only the trimmable kernel body, without soul essence.

    Use this when you need to verify budget compliance of the trimmable
    kernel content in isolation (e.g., budget regression tests).
    """
    return compile_kernel(character_id, budget)


_COMM_MODE_TAG_RE = re.compile(r"^<!--\s*communication_mode:\s*(\w+)\s*-->$")
_MODE_TAG_RE = re.compile(r"^<!--\s*mode:\s*(.+?)\s*-->$")
_ABBREVIATED_RE = re.compile(r"^\*\*Abbreviated:\*\*\s*(.*)$")


def _extract_voice_guidance(raw_text: str) -> list[tuple[str, str]]:
    """Extract backend-safe guidance items from a Voice.md file.

    Returns list of (guidance_text, communication_mode_tag) tuples.
    The communication_mode_tag is parsed from <!-- communication_mode: X -->
    lines within each example block. Defaults to "any" if no tag is present.
    """
    guidance_items: list[tuple[str, str]] = []
    current_title: str | None = None
    current_parts: list[str] | None = None
    current_comm_mode: str = "any"

    for line in raw_text.splitlines():
        stripped = line.strip()

        if stripped.startswith("## Example "):
            if current_title and current_parts:
                guidance = " ".join(part for part in current_parts if part).strip()
                if guidance:
                    guidance_items.append((f"{current_title}: {guidance}", current_comm_mode))
            current_title = stripped.removeprefix("## ").strip()
            current_parts = None
            current_comm_mode = "any"
            continue

        comm_match = _COMM_MODE_TAG_RE.match(stripped)
        if comm_match:
            current_comm_mode = comm_match.group(1)
            continue

        if stripped.startswith("**What it teaches the model:**"):
            teaching_text = stripped.removeprefix("**What it teaches the model:**").strip()
            current_parts = [teaching_text] if teaching_text else []
            continue

        if current_parts is None:
            continue

        if stripped.startswith("**User:**") or stripped.startswith("**Assistant:**") or stripped == "---":
            guidance = " ".join(part for part in current_parts if part).strip()
            if current_title and guidance:
                guidance_items.append((f"{current_title}: {guidance}", current_comm_mode))
            current_parts = None
            continue

        if stripped:
            current_parts.append(stripped)

    if current_title and current_parts:
        guidance = " ".join(part for part in current_parts if part).strip()
        if guidance:
            guidance_items.append((f"{current_title}: {guidance}", current_comm_mode))

    return guidance_items


def load_voice_guidance(
    character_id: str,
    communication_mode: str | None = None,
) -> list[str] | None:
    """Load backend-safe voice guidance derived from a Voice.md file.

    When communication_mode is provided, filters to exemplars tagged with
    that mode or "any". Items without a communication_mode tag default to "any".
    """
    if character_id not in _voice_raw_cache:
        rel_path = VOICE_PATHS.get(character_id)
        if rel_path is None:
            _voice_raw_cache[character_id] = None
        else:
            full_path = PROJECT_ROOT / rel_path
            if not full_path.exists():
                _voice_raw_cache[character_id] = None
            else:
                text = full_path.read_text(encoding="utf-8")
                _voice_raw_cache[character_id] = _extract_voice_guidance(text)

    raw = _voice_raw_cache[character_id]
    if raw is None:
        return None

    if communication_mode:
        filtered = [
            text for text, mode in raw
            if mode in (communication_mode, "any")
        ]
    else:
        filtered = [text for text, _ in raw]

    if not filtered:
        return None

    guidance_items = filtered

    if character_id == "adelia":
        priority_prefixes = [
            "Example 1:",
            "Example 4:",
            "Example 5:",
            "Example 3:",
            "Example 2:",
        ]
        ordered: list[str] = []
        remaining_items = guidance_items[:]
        for prefix in priority_prefixes:
            matches = [item for item in remaining_items if item.startswith(prefix)]
            ordered.extend(matches)
            remaining_items = [item for item in remaining_items if not item.startswith(prefix)]
        guidance_items = ordered + remaining_items
    elif len(guidance_items) > 4:
        even_items = guidance_items[::2]
        odd_items = guidance_items[1::2]
        guidance_items = even_items + odd_items

    return guidance_items or None


_voice_examples_cache: dict[str, list[VoiceExample] | None] = {}


def _extract_voice_examples(raw_text: str) -> list[VoiceExample]:
    """Extract structured VoiceExample entries from a Voice.md file.

    Parses mode tags (``<!-- mode: X, Y -->``), communication mode tags,
    teaching prose, and abbreviated text from each example block. Returns
    a list ordered by file position.
    """
    examples: list[VoiceExample] = []
    current_title: str | None = None
    current_teaching_parts: list[str] | None = None
    current_teaching_text: str = ""
    current_comm_mode: str = "any"
    current_modes: list[VoiceMode] = []
    current_abbreviated: str | None = None
    example_index = 0
    in_abbreviated = False

    for line in raw_text.splitlines():
        stripped = line.strip()

        if stripped.startswith("## Example "):
            # Flush previous example
            if current_title is not None:
                examples.append(VoiceExample(
                    title=current_title,
                    modes=current_modes,
                    teaching_prose=current_teaching_text,
                    abbreviated_text=current_abbreviated,
                    communication_mode=current_comm_mode,
                    index=example_index,
                ))
                example_index += 1
            current_title = stripped.removeprefix("## ").strip()
            current_teaching_parts = None
            current_teaching_text = ""
            current_comm_mode = "any"
            current_modes = []
            current_abbreviated = None
            in_abbreviated = False
            continue

        mode_match = _MODE_TAG_RE.match(stripped)
        if mode_match:
            raw_modes = mode_match.group(1)
            for raw_mode in raw_modes.split(","):
                mode_str = raw_mode.strip()
                if mode_str:
                    current_modes.append(VoiceMode(mode_str))
            continue

        comm_match = _COMM_MODE_TAG_RE.match(stripped)
        if comm_match:
            current_comm_mode = comm_match.group(1)
            continue

        abbreviated_match = _ABBREVIATED_RE.match(stripped)
        if abbreviated_match:
            current_abbreviated = abbreviated_match.group(1).strip()
            in_abbreviated = bool(current_abbreviated)
            if not current_abbreviated:
                current_abbreviated = None
                in_abbreviated = True
            continue

        if stripped.startswith("**What it teaches the model:**"):
            in_abbreviated = False
            teaching_text = stripped.removeprefix("**What it teaches the model:**").strip()
            current_teaching_parts = [teaching_text] if teaching_text else []
            continue

        if stripped.startswith("**User:**") or stripped.startswith("**Assistant:**") or stripped == "---":
            in_abbreviated = False
            # Finalize teaching prose before clearing the accumulator
            if current_teaching_parts is not None:
                current_teaching_text = " ".join(
                    p for p in current_teaching_parts if p
                ).strip()
            current_teaching_parts = None
            continue

        if in_abbreviated and stripped and current_abbreviated is not None:
            current_abbreviated = current_abbreviated + " " + stripped
        elif in_abbreviated and stripped and current_abbreviated is None:
            current_abbreviated = stripped
        elif current_teaching_parts is not None and stripped:
            current_teaching_parts.append(stripped)

    # Flush last example
    if current_title is not None:
        if current_teaching_parts is not None:
            current_teaching_text = " ".join(
                p for p in current_teaching_parts if p
            ).strip()
        examples.append(VoiceExample(
            title=current_title,
            modes=current_modes,
            teaching_prose=current_teaching_text,
            abbreviated_text=current_abbreviated,
            communication_mode=current_comm_mode,
            index=example_index,
        ))

    return examples


def load_voice_examples(character_id: str) -> list[VoiceExample] | None:
    """Load structured VoiceExample entries from a Voice.md file.

    Returns a list of VoiceExample dataclasses with mode tags, teaching
    prose, and abbreviated text parsed from the canonical Voice.md. Returns
    None if no Voice.md file exists for the character.
    """
    if character_id not in _voice_examples_cache:
        rel_path = VOICE_PATHS.get(character_id)
        if rel_path is None:
            _voice_examples_cache[character_id] = None
        else:
            full_path = PROJECT_ROOT / rel_path
            if not full_path.exists():
                _voice_examples_cache[character_id] = None
            else:
                text = full_path.read_text(encoding="utf-8")
                _voice_examples_cache[character_id] = _extract_voice_examples(text)

    return _voice_examples_cache[character_id]


def clear_kernel_cache() -> None:
    """Clear all caches (useful for testing)."""
    _kernel_cache.clear()
    _voice_raw_cache.clear()
    _voice_examples_cache.clear()
