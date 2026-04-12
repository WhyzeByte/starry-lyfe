"""Load backend-safe kernel and voice guidance documents from the filesystem."""

from __future__ import annotations

import re
from pathlib import Path

from .budgets import estimate_tokens, trim_text_to_budget

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
    1: 240,   # Runtime Directives
    2: 480,   # Core Identity (raised from 400 — the identity paragraphs are the soul substrate)
    3: 420,   # Whyze / Pair section
    4: 120,   # Silent Routing (lowered from 180 — routing rules are terse)
    5: 360,   # Behavioral Tier Framework (lowered from 380)
    7: 220,   # Emotional / Relational / Operational Frameworks
    6: 100,   # Voice Architecture (lowered from 120 — compressed at compile time)
}

PRIMARY_SECTION_ORDER: list[int] = [1, 2, 3, 4, 5, 7, 6]
EXPANSION_SECTION_ORDER: list[int] = [2, 3, 5, 7, 6, 8, 9, 10, 11]
FILL_SECTION_ORDER: list[int] = [8, 9, 10, 11]

_kernel_cache: dict[str, str] = {}
_voice_cache: dict[str, list[str] | None] = {}

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
        trimmed = trim_text_to_budget(text, section_budget, strict=True)
        if trimmed and estimate_tokens(trimmed) > 10:
            assembled.append(trimmed)

    result = "\n\n".join(assembled)
    # Final hard ceiling: ensure we never exceed budget even with join overhead
    if estimate_tokens(result) > budget:
        result = trim_text_to_budget(result, budget, None) or result
    return result


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
    """Load a section-compiled character kernel. Cached after first load."""
    cache_key = f"{character_id}:{budget}"
    if cache_key in _kernel_cache:
        return _kernel_cache[cache_key]
    text = compile_kernel(character_id, budget)
    _kernel_cache[cache_key] = text
    return text


def _extract_voice_guidance(raw_text: str) -> list[str]:
    """Extract backend-safe guidance items from a Voice.md file.

    The backend only ingests the "What it teaches the model" prose. Raw
    Msty UI instructions and literal User/Assistant few-shot pairs stay out.
    """
    guidance_items: list[str] = []
    current_title: str | None = None
    current_parts: list[str] | None = None

    for line in raw_text.splitlines():
        stripped = line.strip()

        if stripped.startswith("## Example "):
            if current_title and current_parts:
                guidance = " ".join(part for part in current_parts if part).strip()
                if guidance:
                    guidance_items.append(f"{current_title}: {guidance}")
            current_title = stripped.removeprefix("## ").strip()
            current_parts = None
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
                guidance_items.append(f"{current_title}: {guidance}")
            current_parts = None
            continue

        if stripped:
            current_parts.append(stripped)

    if current_title and current_parts:
        guidance = " ".join(part for part in current_parts if part).strip()
        if guidance:
            guidance_items.append(f"{current_title}: {guidance}")

    return guidance_items


def load_voice_guidance(character_id: str) -> list[str] | None:
    """Load backend-safe voice guidance derived from a Voice.md file.

    Returns guidance items spread across voice modes (not just first N by file order).
    """
    if character_id in _voice_cache:
        return _voice_cache[character_id]

    rel_path = VOICE_PATHS.get(character_id)
    if rel_path is None:
        _voice_cache[character_id] = None
        return None

    full_path = PROJECT_ROOT / rel_path
    if not full_path.exists():
        _voice_cache[character_id] = None
        return None

    text = full_path.read_text(encoding="utf-8")
    guidance_items = _extract_voice_guidance(text)

    # Adelia needs her handoff and Spanish-register examples early in the
    # runtime prompt. Other characters can keep the spread-order heuristic.
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
        # Distribute items for mode coverage rather than clustering at the start.
        even_items = guidance_items[::2]
        odd_items = guidance_items[1::2]
        guidance_items = even_items + odd_items

    _voice_cache[character_id] = guidance_items or None
    return _voice_cache[character_id]


def clear_kernel_cache() -> None:
    """Clear all caches (useful for testing)."""
    _kernel_cache.clear()
    _voice_cache.clear()
