"""Inter-woman (internal) dyad evaluator prompts and response schema (Phase 9).

Extends the Phase 8 Whyze-dyad evaluator pattern to the 6 inter-woman
dyads tracked in ``DyadStateInternal``. Same ±0.03 per-turn cap, same
LLM-primary-with-heuristic-fallback flow, same Pydantic schema shape
with a 5th dimension (``conflict``). The hand-authored per-pair
register notes below are copied **verbatim** from the canonical
source: ``Docs/_phases/PHASE_9.md`` §Pre-execution. They must not be
regenerated, paraphrased, or summarized — per AC-9.8.

Authority: `Docs/_phases/PHASE_9.md` §Pre-execution +
`Characters/{name}.yaml::kernel_sections` §5/§7/§8/§9 (Phase 10.5
rich-YAML cutover — legacy markdown kernels archived under
`Archive/v7.1_pre_yaml/`) +
`Characters/shared_canon.yaml::dyads_baseline` (Phase 10.5c —
narrow canon archived; dyad baselines now hydrate from shared_canon).
"""

from __future__ import annotations

import html
import json
import logging
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, ValidationError

from starry_lyfe.api.orchestration.relationship_prompts import _NumericValue

if TYPE_CHECKING:
    from starry_lyfe.api.orchestration.internal_relationship import (
        InternalDyadDeltaProposal,
    )

logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------
# System prompt — preamble + footer hardcoded; per-pair register sections
# assembled from YAML at import time (Phase 10.4 C3).
# ---------------------------------------------------------------------------

_PREAMBLE: str = """\
You are an inter-woman relationship state evaluator for a four-character \
interactive fiction system. Your only job is to read a single response \
written by one of the four focal women and propose deltas for five \
relationship dimensions that track an ongoing dyad *between two of the \
women* (not between the woman and Whyze — that dyad is handled by a \
separate evaluator).

## Dimensions

- **trust**: Demonstrated mutual trust between the two women. Positive = \
trust expressed or enacted. Negative = guardedness, procedural distancing, \
old-wiring activation between them. Range: -1.0 to 1.0.
- **intimacy**: Warmth, closeness, somatic or intellectual connection \
between the two women in this turn. Positive = closer. Negative = more \
distant. Range: -1.0 to 1.0.
- **conflict**: Active disagreement, friction, or tension *between the two \
women specifically*. Positive = conflict active. Negative = conflict \
resolved or absent. Distinguished from ``unresolved_tension`` (which \
tracks residue) by being about live disagreement in the turn. Range: \
-1.0 to 1.0.
- **unresolved_tension**: Emotional residue or unfinished business between \
them. Positive = more residue. Negative = residue cleared. Range: -1.0 \
to 1.0.
- **repair_history**: Evidence of active repair between the two women. \
NEVER negative. Repair is positive-only; a single turn cannot erase \
accumulated repair history. Range: 0.0 to 1.0.

## Per-pair register notes

The signals for each dimension look different in each pair. Read the \
``dyad_key`` and the two member names, then apply the correct pair's \
register."""


# Hardcoded pair-section headers; YAML carries the body prose only. The
# tuple ordering matches the canonical sequence of the legacy prompt.
_DYAD_HEADERS: list[tuple[str, str]] = [
    ("adelia_bina", "### ADELIA × BINA (anchor_dynamic — resident_continuous)"),
    ("bina_reina", "### BINA × REINA (shield_wall — resident_continuous)"),
    ("adelia_reina", "### ADELIA × REINA (kinetic_vanguard — resident_continuous)"),
    ("adelia_alicia", "### ADELIA × ALICIA (letter_era_friends — alicia_orbital)"),
    ("bina_alicia", "### BINA × ALICIA (couch_above_the_garage — alicia_orbital)"),
    ("reina_alicia", "### REINA × ALICIA (lateral_friends — alicia_orbital)"),
]


_FOOTER: str = """\
## Output format

Respond with ONLY valid JSON. No preamble, no explanation, no markdown fences.
The JSON must contain exactly five numeric fields. All values are floats.

```
{
  "trust": <float in [-1.0, 1.0]>,
  "intimacy": <float in [-1.0, 1.0]>,
  "conflict": <float in [-1.0, 1.0]>,
  "unresolved_tension": <float in [-1.0, 1.0]>,
  "repair_history": <float in [0.0, 1.0]>
}
```

If the turn is neutral with respect to a dimension, use 0.0 for that dimension. \
Prefer small values (±0.1 to ±0.3) unless the signal is strong and unambiguous. \
The downstream ±0.03 per-turn cap will gate the final applied delta — your job \
is to indicate direction and rough magnitude, not to apply the cap yourself.
"""


# Dyad → (member_a, member_b) for looking up either member's YAML copy.
_DYAD_MEMBERS: dict[str, tuple[str, str]] = {
    "adelia_bina": ("adelia", "bina"),
    "bina_reina": ("bina", "reina"),
    "adelia_reina": ("adelia", "reina"),
    "adelia_alicia": ("adelia", "alicia"),
    "bina_alicia": ("bina", "alicia"),
    "reina_alicia": ("reina", "alicia"),
}


def _build_internal_relationship_eval_system() -> str:
    """Assemble the Phase 9 evaluator system prompt from rich YAML (Phase 10.4 C3).

    Preamble + pair headers + footer are hardcoded; each dyad's register
    body prose is read from the first available member's
    ``RichCharacter.evaluator_register.internal_dyads[dyad_key]``.
    Byte-equivalent to the legacy hardcoded string.
    """
    from starry_lyfe.canon.rich_loader import (
        get_internal_dyad_register,
        load_rich_character,
    )

    sections: list[str] = [_PREAMBLE, ""]
    for dyad_key, header in _DYAD_HEADERS:
        body: str | None = None
        for member_id in _DYAD_MEMBERS[dyad_key]:
            rc = load_rich_character(member_id)
            body = get_internal_dyad_register(rc, dyad_key)
            if body:
                break
        if body is None:
            msg = f"No internal_dyads register prose in YAML for {dyad_key!r}"
            raise ValueError(msg)
        sections.append(header)
        sections.append("")
        sections.append(body)
        sections.append("")
        sections.append("---")
        sections.append("")
    sections.append(_FOOTER)
    return "\n".join(sections)


INTERNAL_RELATIONSHIP_EVAL_SYSTEM: str = _build_internal_relationship_eval_system()



# ---------------------------------------------------------------------------
# Response schema
# ---------------------------------------------------------------------------


class InternalRelationshipEvalResponse(BaseModel):
    """Parsed LLM response for a single inter-woman dyad evaluation.

    Reuses Phase 8's ``_NumericValue`` so JSON booleans in numeric fields
    are rejected by the same ``_reject_bool`` before-validator. Extra
    fields (e.g., an LLM-emitted ``reason``) are ignored per
    ``model_config = ConfigDict(extra="ignore")`` — matches Phase 8
    semantics and keeps the parser resilient to LLM verbosity.

    The five fields mirror ``DyadStateInternal`` with ``conflict`` as
    the new fifth dimension vs Phase 8's ``DyadStateWhyze`` schema.
    Range clamping happens post-validation in ``parse_internal_eval_response``
    (AC-8.5 parallel — permissive schema + post-clamp lets a slightly-
    out-of-bounds LLM response degrade gracefully rather than fully
    falling back).
    """

    model_config = ConfigDict(extra="ignore")

    trust: _NumericValue
    intimacy: _NumericValue
    conflict: _NumericValue
    unresolved_tension: _NumericValue
    repair_history: _NumericValue


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------


_CANONICAL_CHARACTERS = frozenset({"adelia", "bina", "reina", "alicia"})
_UNKNOWN = "unknown"


def build_internal_eval_prompt(
    dyad_key: str,
    member_a: str,
    member_b: str,
    response_text: str,
    *,
    speaker_id: str,
) -> str:
    """Build the user-turn message for an inter-woman dyad evaluation call.

    The system prompt (``INTERNAL_RELATIONSHIP_EVAL_SYSTEM``) carries all
    per-pair register notes. This user turn supplies the runtime values
    the evaluator needs: which dyad is being evaluated, which two women
    are members, who actually spoke this turn, and what was said.

    R1-F1 closure (2026-04-15): ``speaker_id`` is required so the LLM can
    resolve directional pair signals (who left the hall light on, who
    delivered the structural veto, who called the other "the witness").
    Without it the same text against ``bina_reina`` produced identical
    prompts whether the focal speaker was Bina or Reina.

    Delimiter injection defense (R1-F3 lesson from Phase 8, proactively
    applied per AC-9.9): the response text is ``html.escape``'d before
    interpolation so a payload containing ``</response_text>`` cannot
    break out of the wrapper block.

    Args:
        dyad_key: Canonical lowercase dyad identifier (e.g., "bina_reina").
        member_a: First woman in the dyad (canonical lowercase ID).
        member_b: Second woman in the dyad (canonical lowercase ID).
        response_text: The speaker's full response text from this turn.
        speaker_id: Canonical lowercase ID of the woman who spoke this
            turn. Should be one of ``member_a`` or ``member_b``; the
            evaluator's SQL filter already enforces membership, so this
            layer accepts the value without re-validation.

    Returns:
        A single string ready to send as the ``user`` role message.
    """
    dkey = dyad_key.lower().strip() if dyad_key else _UNKNOWN
    a = member_a.lower().strip() if member_a else _UNKNOWN
    b = member_b.lower().strip() if member_b else _UNKNOWN
    speaker = speaker_id.lower().strip() if speaker_id else _UNKNOWN
    # R1-F3 lesson: escape < and > so the closing </response_text>
    # delimiter cannot appear verbatim inside user-supplied content.
    safe_text = html.escape(response_text, quote=False)
    return (
        f"Speaker: {speaker}\n"
        f"Dyad: {dkey}\n"
        f"Members: {a}, {b}\n\n"
        f"<response_text>\n{safe_text}\n</response_text>\n\n"
        "Evaluate the five relationship dimensions for this dyad in this turn "
        "and respond with only the JSON object described in the system prompt."
    )


# ---------------------------------------------------------------------------
# Response parser
# ---------------------------------------------------------------------------


def parse_internal_eval_response(text: str) -> InternalDyadDeltaProposal | None:
    """Parse an LLM inter-woman evaluation response into a delta proposal.

    Fail-closed contract (R1-F1 lesson from Phase 8, proactively applied
    per AC-9.9): returns ``None`` on any of malformed JSON, non-object
    JSON, missing fields, boolean or non-numeric field values. Returns
    None so the caller can fall back to ``_propose_internal_deltas``.

    Clamping (AC-9.10 parallel): out-of-range values clamp at the
    boundary with a warn log; negative ``repair_history`` clamps to 0.0
    since repair is positive-only by architecture.

    Args:
        text: Raw string returned by the LLM (may contain markdown fences).

    Returns:
        An ``InternalDyadDeltaProposal`` with values clamped + validated,
        or ``None`` on any parse failure.
    """
    # Import here to avoid top-level circular import — internal_relationship.py
    # imports this module for the schema + helpers.
    from starry_lyfe.api.orchestration.internal_relationship import (
        InternalDyadDeltaProposal,
    )

    # Strip markdown fences that some models emit despite instructions.
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        inner = [ln for ln in lines[1:] if not ln.strip().startswith("```")]
        cleaned = "\n".join(inner).strip()

    try:
        raw: Any = json.loads(cleaned)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning(
            "internal_llm_eval_parse_json_failed",
            extra={"error": str(exc), "raw_prefix": cleaned[:120]},
        )
        return None

    # R1-F1 fail-closed guard: non-object JSON → None.
    if not isinstance(raw, dict):
        logger.warning(
            "internal_llm_eval_parse_non_object",
            extra={"type": type(raw).__name__, "raw_prefix": cleaned[:120]},
        )
        return None

    # Route field-shape + type validation through the Pydantic schema. The
    # _NumericValue before-validator rejects booleans; missing fields and
    # non-numeric values raise ValidationError → None. Extra fields
    # are ignored per model_config.
    try:
        model = InternalRelationshipEvalResponse.model_validate(raw)
    except ValidationError as exc:
        logger.warning(
            "internal_llm_eval_parse_schema_validation_failed",
            extra={"error": str(exc), "raw_keys": sorted(raw.keys())},
        )
        return None

    # Clamp out-of-range values with warn log. Lets a slightly-oob LLM
    # response degrade gracefully rather than falling back entirely.
    def _clamp_range(value: float, lo: float, hi: float, field: str) -> float:
        if value < lo or value > hi:
            logger.warning(
                "internal_llm_eval_parse_out_of_range",
                extra={
                    "field": field,
                    "value": value,
                    "clamped_to": max(lo, min(hi, value)),
                },
            )
            return max(lo, min(hi, value))
        return value

    trust = _clamp_range(model.trust, -1.0, 1.0, "trust")
    intimacy = _clamp_range(model.intimacy, -1.0, 1.0, "intimacy")
    conflict = _clamp_range(model.conflict, -1.0, 1.0, "conflict")
    tension = _clamp_range(model.unresolved_tension, -1.0, 1.0, "unresolved_tension")
    repair_raw = model.repair_history

    # AC-9.10: repair_history is positive-only. Clamp negative to 0.0.
    if repair_raw < 0.0:
        logger.warning(
            "internal_llm_eval_parse_negative_repair_history",
            extra={"value": repair_raw, "clamped_to": 0.0},
        )
        repair_raw = 0.0
    repair = _clamp_range(repair_raw, 0.0, 1.0, "repair_history")

    return InternalDyadDeltaProposal(
        trust=trust,
        intimacy=intimacy,
        conflict=conflict,
        unresolved_tension=tension,
        repair_history=repair,
    )


# ---------------------------------------------------------------------------
# Canonical dyad metadata — used by the evaluator's dyad-key resolution.
# ---------------------------------------------------------------------------


# Canonical dyad keys matching ``DyadStateInternal.dyad_key`` seed values
# and the section headers above. Keys are (member_a, member_b) sorted by
# the stable canonical character order in ``CharacterID.all_strings()``.
CANONICAL_DYAD_KEYS: frozenset[str] = frozenset(
    {
        "adelia_bina",
        "adelia_reina",
        "adelia_alicia",
        "bina_reina",
        "bina_alicia",
        "reina_alicia",
    }
)

# Alicia-orbital dyad keys — these are dormant when Alicia is away per
# ``is_currently_active=False``. Evaluator skips writes for these when
# the dyad is dormant (AC-9.11).
ALICIA_ORBITAL_DYAD_KEYS: frozenset[str] = frozenset(
    {"adelia_alicia", "bina_alicia", "reina_alicia"}
)
