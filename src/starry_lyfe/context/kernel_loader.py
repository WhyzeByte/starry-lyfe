"""Load backend-safe kernel and voice guidance documents from the filesystem."""

from __future__ import annotations

from pathlib import Path

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

_kernel_cache: dict[str, str] = {}
_voice_cache: dict[str, list[str] | None] = {}


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


def load_kernel(character_id: str) -> str:
    """Load a backend-safe character kernel document. Cached after first load."""
    if character_id in _kernel_cache:
        return _kernel_cache[character_id]

    rel_path = KERNEL_PATHS.get(character_id)
    if rel_path is None:
        msg = f"No kernel path defined for character '{character_id}'"
        raise ValueError(msg)

    full_path = PROJECT_ROOT / rel_path
    if not full_path.exists():
        msg = f"Kernel file not found: {full_path}"
        raise FileNotFoundError(msg)

    text = _sanitize_kernel_text(full_path.read_text(encoding="utf-8"))
    _kernel_cache[character_id] = text
    return text


def _extract_voice_guidance(raw_text: str) -> list[str]:
    """Extract backend-safe guidance items from a Voice.md file.

    The backend should only ingest the "What it teaches the model" prose. Raw
    Msty UI instructions and literal User/Assistant few-shot pairs stay out of
    the backend prompt.
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

    Full few-shot prompt pairs remain Msty-owned per the production authority
    split. The backend only consumes the explanatory guidance prose.
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
    _voice_cache[character_id] = guidance_items or None
    return _voice_cache[character_id]


def clear_kernel_cache() -> None:
    """Clear all caches (useful for testing)."""
    _kernel_cache.clear()
    _voice_cache.clear()
