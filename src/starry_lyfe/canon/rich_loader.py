"""Load and validate rich per-character YAMLs + shared_canon.yaml (Phase 10.1).

Runs alongside the existing narrow-canon loaders (``loader.py``) — zero
runtime integration in Phase 10.1. Cutovers happen in 10.2–10.4.

Provides:
- ``load_rich_character(character_id)`` → ``RichCharacter``
- ``load_all_rich_characters()`` → ``dict[str, RichCharacter]``
- ``load_shared_canon()`` → ``SharedCanon``
- ``validate_rich_cross_references(chars, shared)`` → error list
- ``get_preserve_markers(rc)`` → flat list of ``PreserveMarker``

Authority: ``Docs/_phases/PHASE_10.md`` §Phase 10.1 WI3–WI4.
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from .rich_schema import PreserveMarker, PreserveMarkersBlock, RichCharacter
from .shared_schema import SharedCanon


class SoulEssenceNotFoundError(ValueError):
    """Raised when soul essence content is missing for a character (Phase 10.5).

    Phase 10.3 C1 rewire and Phase 10.5 archival moved the legacy
    ``soul_essence.py`` module to ``Archive/v7.1_pre_yaml/``. This error
    is re-defined here so the soul essence propagation contract (R-1.1
    strict propagation through the assembly chain) stays intact. Error
    semantics are preserved byte-for-byte from the archived module.
    """

logger = logging.getLogger(__name__)

CHARACTERS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "Characters"

RICH_YAML_FILES: dict[str, str] = {
    "adelia": "adelia_raye.yaml",
    "bina": "bina_malek.yaml",
    "reina": "reina_torres.yaml",
    "alicia": "alicia_marin.yaml",
    "shawn": "shawn_kroon.yaml",
}


def _load_yaml_file(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as f:
        data: dict[str, object] = yaml.safe_load(f)
    return data


def load_rich_character(character_id: str) -> RichCharacter:
    """Load and Pydantic-validate a single rich character YAML."""
    filename = RICH_YAML_FILES.get(character_id)
    if filename is None:
        msg = f"Unknown character_id: {character_id!r}. Valid: {sorted(RICH_YAML_FILES)}"
        raise ValueError(msg)
    path = CHARACTERS_DIR / filename
    data = _load_yaml_file(path)
    return RichCharacter.model_validate(data)


def load_all_rich_characters() -> dict[str, RichCharacter]:
    """Load and validate all 5 rich character YAMLs."""
    return {cid: load_rich_character(cid) for cid in RICH_YAML_FILES}


def load_shared_canon() -> SharedCanon:
    """Load and Pydantic-validate ``Characters/shared_canon.yaml``."""
    path = CHARACTERS_DIR / "shared_canon.yaml"
    data = _load_yaml_file(path)
    return SharedCanon.model_validate(data)


def get_kernel_sections(rc: RichCharacter) -> list[tuple[int, str]]:
    """Extract kernel sections as ``(section_num, section_text)`` tuples.

    Returns the same shape as ``kernel_loader._parse_kernel_sections()``
    so the downstream ``compile_kernel()`` trim pipeline works unchanged.
    Returns an empty list for characters without kernel_sections (Shawn).
    """
    if rc.kernel_sections is None:
        return []
    return [(ks.section_num, ks.body) for ks in rc.kernel_sections]


def format_soul_essence_from_rich(rc: RichCharacter) -> str:
    """Format soul essence from rich YAML soul_substrate blocks.

    Produces the same prompt-ready text as ``soul_essence.py::
    format_soul_essence()`` but sourced from ``RichCharacter.soul_substrate``
    instead of the hardcoded Python module. Section headers are identical
    to preserve assembled-prompt equivalence.

    Raises ``SoulEssenceNotFoundError`` if the soul substrate has no
    content blocks — same error contract as the Python module path.
    """
    ss = rc.soul_substrate
    parts: list[str] = []
    if ss.identity_blocks:
        parts.append("## Core Identity (soul substrate)")
        for block in ss.identity_blocks:
            parts.append(block.text)
    if ss.pair_blocks:
        parts.append("## Pair Architecture (soul substrate)")
        for block in ss.pair_blocks:
            parts.append(block.text)
    if ss.behavioral_blocks:
        parts.append("## Behavioral Substrate (soul substrate)")
        for block in ss.behavioral_blocks:
            parts.append(block.text)
    if ss.intimacy_blocks:
        parts.append("## Intimacy Architecture (soul substrate)")
        for block in ss.intimacy_blocks:
            parts.append(block.text)
    result = "\n\n".join(parts)
    if not result.strip():
        raise SoulEssenceNotFoundError(
            f"No soul essence content in rich YAML for '{rc.character_id}'"
        )
    return result


def format_pair_callbacks_from_rich(rc: RichCharacter) -> str:
    """Format ``pair_architecture.callbacks`` as a Layer 1 canonical block.

    Phase 10.6 remediation: pair-architecture callbacks are load-bearing
    short-form canonical phrases (e.g., "The plate will always be
    covered.", "Neither of us is the load the other carries."). They
    are authored as list items that the main kernel/voice assembly
    does not render as prose. This helper renders them as a dedicated
    Layer 1 block so preserve_marker anchors targeting these phrases
    reach the assembled prompt.

    Returns an empty string when the character has no pair_architecture
    callbacks block (e.g., Shawn).
    """
    pa = rc.pair_architecture
    if not isinstance(pa, dict):
        return ""
    callbacks = pa.get("callbacks")
    if not isinstance(callbacks, list) or not callbacks:
        return ""
    lines = ["## Canonical Callbacks (pair architecture)"]
    for cb in callbacks:
        lines.append(f"- {cb}")
    return "\n".join(lines)


def pair_callbacks_token_estimate_from_rich(character_id: str) -> int:
    """Estimate token count for the pair_architecture.callbacks Layer 1 block.

    Phase 10.6 remediation: the callbacks block prepended to Layer 1 via
    ``compile_kernel_with_soul`` is a guaranteed surcharge (not trimmed).
    The effective Layer 1 ceiling therefore grows by this amount on top
    of ``kernel_budget + soul_essence_token_estimate_from_rich``.
    """
    from starry_lyfe.context.budgets import estimate_tokens

    try:
        rc = load_rich_character(character_id)
    except ValueError:
        return 0
    text = format_pair_callbacks_from_rich(rc)
    return estimate_tokens(text) if text else 0


def soul_essence_token_estimate_from_rich(character_id: str) -> int:
    """Estimate token count for soul essence sourced from rich YAML.

    Raises ``SoulEssenceNotFoundError`` if the character has no soul
    substrate blocks — same error contract as the Python module path.
    """
    from starry_lyfe.context.budgets import estimate_tokens

    try:
        rc = load_rich_character(character_id)
    except ValueError as exc:
        raise SoulEssenceNotFoundError(str(exc)) from exc
    text = format_soul_essence_from_rich(rc)
    if not text.strip():
        raise SoulEssenceNotFoundError(
            f"No soul essence content in rich YAML for '{character_id}'"
        )
    return estimate_tokens(text)


def get_evaluator_whyze_register(rc: RichCharacter) -> str | None:
    """Return the Phase 8 per-character evaluator register prose (or None)."""
    if rc.evaluator_register is None:
        return None
    return rc.evaluator_register.whyze_dyad


def get_internal_dyad_register(rc: RichCharacter, dyad_key: str) -> str | None:
    """Return the Phase 9 per-dyad register prose for a given dyad_key (or None)."""
    if rc.evaluator_register is None or rc.evaluator_register.internal_dyads is None:
        return None
    for entry in rc.evaluator_register.internal_dyads:
        if entry.dyad_key == dyad_key:
            return entry.prose
    return None


def get_constraint_pillars(rc: RichCharacter, mode: str) -> list[str] | None:
    """Return the constraint pillars list for a communication mode.

    Reads ``behavioral_framework.constraint_pillars[mode]`` with fallback
    to ``in_person`` if the requested mode is missing. Returns None if
    the YAML does not carry the block.
    """
    bf = rc.behavioral_framework or {}
    pillars_block = bf.get("constraint_pillars") if isinstance(bf, dict) else None
    if not isinstance(pillars_block, dict):
        return None
    direct = pillars_block.get(mode)
    if isinstance(direct, list):
        return [str(x) for x in direct]
    in_person = pillars_block.get("in_person")
    if isinstance(in_person, list):
        return [str(x) for x in in_person]
    return None


def get_state_protocols(rc: RichCharacter) -> dict[str, object]:
    """Return the behavioral_framework.state_protocols block (or empty dict).

    Initially sourced from ``stress_modes`` when ``state_protocols`` is
    not yet embedded. Phase 10.4 C2 migration may normalize the key.
    """
    bf = rc.behavioral_framework or {}
    if isinstance(bf, dict):
        sp = bf.get("state_protocols")
        if isinstance(sp, dict):
            return sp
        sm = bf.get("stress_modes")
        if isinstance(sm, dict):
            return sm
    return {}


def get_preserve_markers(rc: RichCharacter) -> list[PreserveMarker]:
    """Extract a flat list of preserve markers from any character YAML shape."""
    pm = rc.meta.preserve_markers
    if pm is None:
        return []
    if isinstance(pm, list):
        return pm
    if isinstance(pm, PreserveMarkersBlock):
        return pm.canonical_anchors or []
    return []


def verify_preserve_markers(
    rc: RichCharacter,
    *,
    full_text: str,
) -> list[str]:
    """Check that each preserve_marker content_anchor appears in the body text.

    Returns a list of error strings (empty = all pass). The ``full_text``
    should be the raw YAML file text with the preserve_markers block
    excluded (so anchors aren't found inside their own definition).
    """
    errors: list[str] = []
    for marker in get_preserve_markers(rc):
        anchor = marker.content_anchor
        clean = anchor.rstrip(".")
        if clean.endswith("..."):
            clean = clean[:-3].rstrip()
        if clean not in full_text:
            errors.append(
                f"preserve_marker {marker.id!r}: content_anchor not found in body text"
            )
    return errors


def _get_inter_woman_dyad_keys(rc: RichCharacter) -> set[str]:
    """Return the set of other-character IDs this character has dyad blocks for."""
    fad = rc.family_and_other_dyads
    if fad is None:
        return set()
    return {k.removeprefix("with_") for k in fad if k.startswith("with_")}


def validate_rich_cross_references(
    chars: dict[str, RichCharacter],
    shared: SharedCanon,
) -> list[str]:
    """Cross-reference validator for the per-POV model (Phase 10.1 WI4).

    Checks:
    1. Perspective symmetry: every ``family_and_other_dyads.with_{X}``
       block in character A must have a matching ``with_{A}`` in X.
    2. Pair POV: every woman with ``pair_architecture`` must have a
       matching pair entry in ``shared_canon.yaml.pairs``.

    Returns a list of error strings (empty = all pass).
    """
    errors: list[str] = []
    women = {cid: rc for cid, rc in chars.items() if cid != "shawn"}

    for cid_a, rc_a in women.items():
        dyad_keys_a = _get_inter_woman_dyad_keys(rc_a)
        for other_id in dyad_keys_a:
            if other_id not in women:
                continue
            rc_b = women[other_id]
            dyad_keys_b = _get_inter_woman_dyad_keys(rc_b)
            if cid_a not in dyad_keys_b:
                errors.append(
                    f"Perspective asymmetry: {cid_a} has with_{other_id} "
                    f"but {other_id} has no with_{cid_a}"
                )

    shared_pair_names = {p.canonical_name for p in (shared.pairs or [])}
    for cid, rc in women.items():
        pa = rc.pair_architecture
        if pa is None:
            continue
        pair_name = pa.get("name") if isinstance(pa, dict) else None
        if pair_name and pair_name not in shared_pair_names:
            errors.append(
                f"{cid}: pair_architecture.name {pair_name!r} "
                f"not found in shared_canon.yaml pairs"
            )

    return errors
