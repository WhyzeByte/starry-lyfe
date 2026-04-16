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


_ONEDRIVE_LOCK_RETRY_BACKOFF_MS: tuple[int, ...] = (50, 100, 200, 400)


def _load_yaml_file(path: Path) -> dict[str, object]:
    """Load a rich YAML file with bounded retry on transient OS locks.

    Phase 10.5b R2-F1: the Characters/ YAMLs live on OneDrive, and the
    cloud-sync daemon occasionally holds a brief lock during incremental
    upload/download which surfaces as ``PermissionError`` (Windows) or
    ``OSError`` (POSIX). Codex Round 2 audit on commit ``005cbff`` hit
    this on ``shawn_kroon.yaml`` and correctly failed the audit because
    every path that calls ``load_all_rich_characters()`` inherited the
    transient failure.

    Retry policy: up to 5 attempts across ~750ms total (50 + 100 + 200 +
    400 + final) — a window long enough to cover typical OneDrive sync
    lock durations (50–500ms) without masking a genuine unreadable-file
    condition. The original exception is re-raised on the final attempt.
    """
    import time

    last_exc: OSError | None = None
    for attempt, backoff_ms in enumerate((*_ONEDRIVE_LOCK_RETRY_BACKOFF_MS, 0)):
        try:
            with path.open(encoding="utf-8") as f:
                data: dict[str, object] = yaml.safe_load(f)
            return data
        except OSError as exc:
            last_exc = exc
            if backoff_ms > 0:
                logger.warning(
                    "rich YAML transient read error (attempt %d/%d) for %s: %s",
                    attempt + 1,
                    len(_ONEDRIVE_LOCK_RETRY_BACKOFF_MS) + 1,
                    path,
                    exc,
                )
                time.sleep(backoff_ms / 1000.0)
    assert last_exc is not None
    raise last_exc


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
    if pa is None:
        return ""
    callbacks = pa.callbacks
    if not callbacks:
        return ""
    lines = ["## Canonical Callbacks (pair architecture)"]
    for cb in callbacks:
        lines.append(f"- {cb}")
    return "\n".join(lines)


def format_pair_metadata_from_rich(character_id: str) -> str:
    """Layer 5 pair metadata block sourced from shared_canon + rich YAML.

    Phase 10.5b RT1 cutover + Phase 10.5b R2-F3 shared-canon-anchoring
    completion: replaces the legacy ``pairs_loader.format_pair_metadata``
    runtime path.

    Source-of-truth split (per the RT1 playbook):

    - **Objective anchors** (immune to per-character drift) come from
      ``shared_canon.yaml.pairs[canonical_name=<name>]``:
      PAIR name, CLASSIFICATION, MECHANISM. A red-team probe patching
      shared_canon to sentinel values MUST see those sentinels in the
      emitted block (enforced by
      ``test_layers.py::TestLayer5PairMetadataFocalPOV``).

    - **Focal-POV experiential content** (AC-10.23) comes from the
      focal character's ``pair_architecture``: CORE METAPHOR (from
      ``core_metaphors[]`` list or ``core_metaphor`` singular string),
      WHAT SHE PROVIDES (from ``what_she_provides[]``).

    - **HOW SHE BREAKS HIS SPIRAL** (her POV on regulation) comes from
      ``floor_defaults.ambiguity_resolution.when_whyze_is_spiraling``,
      the canonical location in every woman's rich YAML.

    When shared_canon does not carry an entry for the authored pair
    name, or when a field is blank in shared_canon, the focal YAML
    value is used as a defensive fallback — but the expected contract
    is that every pair name in a per-character ``pair_architecture.name``
    resolves in ``shared_canon.yaml::pairs[]`` (AC-10.2).

    Raises CharacterNotFoundError if the character has no
    ``pair_architecture`` block (Shawn by design).
    """
    rc = load_rich_character(character_id)
    pa = rc.pair_architecture
    if pa is None:
        from .schemas.enums import CharacterNotFoundError
        msg = f"No pair_architecture for character {character_id!r}"
        raise CharacterNotFoundError(msg)

    shared = load_shared_canon()
    authored_name = pa.name

    shared_entry = None
    if authored_name and shared.pairs:
        for entry in shared.pairs:
            if entry.canonical_name == authored_name:
                shared_entry = entry
                break

    canonical_name = (
        shared_entry.canonical_name if shared_entry is not None else authored_name
    )

    if shared_entry is not None and shared_entry.classification:
        classification = str(shared_entry.classification).strip()
    else:
        classification = str(pa.classification or "").strip()

    if shared_entry is not None and shared_entry.mechanism:
        mechanism = str(shared_entry.mechanism).strip()
    else:
        mechanism = str(pa.mechanism or "").strip()

    metaphors = pa.core_metaphors
    if metaphors:
        metaphor_text = "; ".join(str(m).strip() for m in metaphors if str(m).strip())
    else:
        metaphor_text = str(pa.core_metaphor or "").strip()

    provides = pa.what_she_provides
    if isinstance(provides, list) and provides:
        provides_text = "; ".join(str(p).strip() for p in provides if str(p).strip())
    else:
        provides_text = str(provides or "").strip()

    spiral_text = ""
    extras = getattr(rc, "__pydantic_extra__", None) or {}
    floor_defaults = extras.get("floor_defaults")
    if isinstance(floor_defaults, dict):
        ar = floor_defaults.get("ambiguity_resolution")
        if isinstance(ar, dict):
            candidate = ar.get("when_whyze_is_spiraling")
            if isinstance(candidate, str):
                spiral_text = candidate.strip()
    if not spiral_text:
        bf = rc.behavioral_framework or {}
        if isinstance(bf, dict):
            for parent_key in ("regulation_loop", "anxiety_anchoring"):
                parent = bf.get(parent_key)
                if isinstance(parent, dict):
                    candidate = parent.get("when_whyze_is_spiraling")
                    if isinstance(candidate, str) and candidate.strip():
                        spiral_text = candidate.strip()
                        break
                elif parent_key == "anxiety_anchoring" and isinstance(parent, str):
                    spiral_text = parent.strip()
                    break

    lines = [f"PAIR: {canonical_name or 'Unknown'}"]
    if classification:
        lines.append(f"CLASSIFICATION: {classification}")
    if mechanism:
        lines.append(f"MECHANISM: {mechanism}")
    if metaphor_text:
        lines.append(f"CORE METAPHOR: {metaphor_text}")
    if provides_text:
        lines.append(f"WHAT SHE PROVIDES: {provides_text}")
    if spiral_text:
        lines.append(f"HOW SHE BREAKS HIS SPIRAL: {spiral_text}")
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


_INTER_WOMAN_DYADS: tuple[tuple[str, str], ...] = (
    ("adelia", "bina"),
    ("adelia", "reina"),
    ("adelia", "alicia"),
    ("bina", "reina"),
    ("bina", "alicia"),
    ("reina", "alicia"),
)


def _dyad_pov_prose_signature(rc: RichCharacter, other_id: str) -> tuple[str, ...] | None:
    """Return a normalized prose tuple for comparing two POVs on one dyad.

    Returns ``None`` if the POV block is absent. The tuple packs the
    load-bearing prose fields (``interlock_name``, ``description``,
    ``tone``, joined ``truths``) in a stable order so two POVs can be
    compared component-wise.
    """
    fad = rc.family_and_other_dyads
    if fad is None:
        return None
    block = fad.get(f"with_{other_id}")
    if block is None:
        return None
    truths = block.truths
    if isinstance(truths, list):
        truths_text = "\n".join(str(t) for t in truths)
    elif isinstance(truths, str):
        truths_text = truths
    else:
        truths_text = ""
    return (
        str(block.interlock_name or ""),
        str(block.description or ""),
        str(block.tone or ""),
        truths_text,
    )


def validate_rich_cross_references(
    chars: dict[str, RichCharacter],
    shared: SharedCanon,
) -> list[str]:
    """Cross-reference validator for the per-POV model.

    Checks:
    1. Perspective symmetry: every ``family_and_other_dyads.with_{X}``
       block in character A must have a matching ``with_{A}`` in X.
    2. Pair POV: every woman with ``pair_architecture`` must have a
       matching pair entry in ``shared_canon.yaml.pairs``.
    3. All-six-dyads divergence (AC-10.21, Phase 10.5b RT2): for every
       one of the 6 inter-woman dyads, the two POV blocks must differ
       in at least one prose field. Byte-identical POVs indicate drift
       toward agreeable mush and FAIL the validator.

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
        pair_name = pa.name
        if pair_name and pair_name not in shared_pair_names:
            errors.append(
                f"{cid}: pair_architecture.name {pair_name!r} "
                f"not found in shared_canon.yaml pairs"
            )

    for dyad_a, dyad_b in _INTER_WOMAN_DYADS:
        rc_x = women.get(dyad_a)
        rc_y = women.get(dyad_b)
        if rc_x is None or rc_y is None:
            continue
        sig_a = _dyad_pov_prose_signature(rc_x, dyad_b)
        sig_b = _dyad_pov_prose_signature(rc_y, dyad_a)
        if sig_a is None or sig_b is None:
            continue
        diverges = any(
            a and b and a != b
            for a, b in zip(sig_a, sig_b, strict=False)
        )
        asymmetric = any(
            bool(a) != bool(b)
            for a, b in zip(sig_a, sig_b, strict=False)
        )
        if not (diverges or asymmetric):
            errors.append(
                f"Dyad {dyad_a}x{dyad_b}: POV prose blocks are byte-identical "
                f"across interlock_name/description/tone/truths. "
                f"AC-10.21 requires per-POV divergence on at least one "
                f"lived-mechanic prose field."
            )

    return errors
