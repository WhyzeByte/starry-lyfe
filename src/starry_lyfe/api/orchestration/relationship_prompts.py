"""Relationship evaluator prompts and response schema.

The LLM evaluator reads the focal character's response text from a
single turn and proposes bounded deltas for the four ``DyadStateWhyze``
dimensions. The heuristic fallback in ``relationship.py::_propose_deltas``
remains the live degraded-mode path; this module is the LLM-primary path.

Per-character register notes are drawn from canonical kernel constraint
pillars (Tier 1 / Tier 2) and the intimacy architectures of each character.
These notes must NOT be auto-generated or paraphrased from code. They are
hand-authored against the source kernels and updated only via direct
authorship. See ``Characters/{Name}/{Name}_v7.1.md`` for authority.

Canonical authority: ``Vision/Starry-Lyfe_Vision_v7.1.md`` §9 (Success
Criteria) + per-character kernels §5 (Behavioral Tier Framework) §8
(Intimacy Architecture). Phase 8 spec: ``Docs/_phases/PHASE_8.md`` AC-8.8.
"""

from __future__ import annotations

import html
import json
import logging
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict, ValidationError

from starry_lyfe.api.orchestration.relationship import DyadDeltaProposal

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompt — preamble + footer hardcoded; per-character register
# sections assembled from YAML at import time (Phase 10.4 C3).
# ---------------------------------------------------------------------------

_PREAMBLE: str = """\
You are a relationship state evaluator for a four-character interactive fiction \
system. Your only job is to read a single response written by one of the four \
focal characters and propose deltas for four relationship dimensions that track \
her ongoing dyad with Whyze (the operator).

## Dimensions

- **intimacy**: Warmth, closeness, somatic or intellectual connection expressed \
in this turn. Positive = closer. Negative = more distant. Range: -1.0 to 1.0.
- **unresolved_tension**: Friction, frustration, or conflict active in this \
turn. Positive = more tension. Negative = tension eased or resolved. Range: \
-1.0 to 1.0.
- **trust**: Demonstrated trust — vulnerability, honesty, clean handoff, \
structural veto honored, or explicit ask for help. Positive = trust expressed. \
Negative = guardedness or withdrawal. Range: -1.0 to 1.0.
- **repair_history**: Evidence of active repair — apology, acknowledged error, \
named wrongness, restored reciprocity. NEVER negative. Repair is positive-only; \
a single turn cannot erase accumulated repair history. Range: 0.0 to 1.0.

## Per-character register notes

The signals for each dimension look different in each character's voice. Read \
the character ID and apply the correct register."""


# Hardcoded headers preserve the per-character section labels that
# appeared in the legacy hardcoded RELATIONSHIP_EVAL_SYSTEM. YAML
# carries the body prose only.
_CHARACTER_HEADERS: dict[str, str] = {
    "adelia": "### ADELIA (Entangled Pair — Ne-dominant ENFP-A)",
    "bina": "### BINA (Circuit Pair — Si-dominant ISFJ-A)",
    "reina": "### REINA (Kinetic Pair — Se-dominant ESTP-A)",
    "alicia": "### ALICIA (Solstice Pair — Se-somatic ESFP-A)",
}

_FOOTER: str = """\
## Output format

Respond with ONLY valid JSON. No preamble, no explanation, no markdown fences.
The JSON must contain exactly four numeric fields. All values are floats.

```
{
  "intimacy": <float in [-1.0, 1.0]>,
  "unresolved_tension": <float in [-1.0, 1.0]>,
  "trust": <float in [-1.0, 1.0]>,
  "repair_history": <float in [0.0, 1.0]>
}
```

If the turn is neutral with respect to a dimension, use 0.0 for that dimension. \
Prefer small values (±0.1 to ±0.3) unless the signal is strong and unambiguous. \
The downstream ±0.03 per-turn cap will gate the final applied delta — your job \
is to indicate direction and rough magnitude, not to apply the cap yourself.
"""


def _build_relationship_eval_system() -> str:
    """Assemble the Phase 8 evaluator system prompt from rich YAML (Phase 10.4 C3).

    Preamble + per-character headers + footer are hardcoded; each character's
    register body prose is read from ``RichCharacter.evaluator_register.whyze_dyad``.
    Byte-equivalent to the legacy hardcoded string.
    """
    from starry_lyfe.canon.rich_loader import (
        get_evaluator_whyze_register,
        load_rich_character,
    )

    sections: list[str] = [_PREAMBLE, ""]
    for cid in ("adelia", "bina", "reina", "alicia"):
        rc = load_rich_character(cid)
        body = get_evaluator_whyze_register(rc)
        if body is None:
            msg = f"No whyze_dyad register prose in YAML for {cid!r}"
            raise ValueError(msg)
        sections.append(_CHARACTER_HEADERS[cid])
        sections.append("")
        sections.append(body)
        sections.append("")
        sections.append("---")
        sections.append("")
    sections.append(_FOOTER)
    return "\n".join(sections)


RELATIONSHIP_EVAL_SYSTEM: str = _build_relationship_eval_system()



# ---------------------------------------------------------------------------
# Response schema
# ---------------------------------------------------------------------------


def _reject_bool(v: Any) -> Any:
    """R1-F2 before-validator: reject JSON booleans in numeric fields.

    ``bool`` is a subclass of ``int`` in Python, so Pydantic's default
    ``float`` validator would coerce True/False to 1.0/0.0. AC-8.9
    requires non-numeric inputs (including booleans) to fail closed.
    """
    if isinstance(v, bool):
        raise ValueError("boolean values are not accepted in numeric fields")
    return v


_NumericValue = Annotated[float, BeforeValidator(_reject_bool)]


class RelationshipEvalResponse(BaseModel):
    """Parsed LLM response for a single relationship evaluation turn.

    R1-F2 closure (2026-04-15): this schema is now the authoritative
    validator used by ``parse_eval_response`` via ``model_validate``.
    All four numeric fields reject booleans via the ``_reject_bool``
    before-validator. Range clamping happens AFTER validation in the
    parser — AC-8.5 specifies clamping-with-warn rather than raising
    on out-of-range values, so the schema stays permissive on range
    and the parser applies the clamp.

    ``repair_history`` is positive-only per architecture (AC-8.10);
    the parser clamps negative values to 0.0 after this schema has
    validated the shape and types.
    """

    model_config = ConfigDict(extra="ignore")

    intimacy: _NumericValue
    unresolved_tension: _NumericValue
    trust: _NumericValue
    repair_history: _NumericValue


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

_UNKNOWN_CHARACTER = "unknown"

_CHARACTER_IDS = frozenset({"adelia", "bina", "reina", "alicia"})


def build_eval_prompt(character_id: str, response_text: str) -> str:
    """Build the user-turn message for a relationship evaluation call.

    The system prompt (``RELATIONSHIP_EVAL_SYSTEM``) carries all per-character
    register notes. This user turn supplies only the runtime values the
    evaluator needs: which character spoke, and what she said.

    ``response_text`` is injected between XML-style delimiters after HTML
    escaping so the LLM can locate it unambiguously regardless of its
    content without allowing delimiter injection from the text itself.

    Intentional narrowing (Phase 8 R2a, 2026-04-15): the prompt does NOT
    include the current ``DyadStateWhyze`` row. The Step 1 plan speculated
    a three-arg form that would surface running intimacy / tension / trust
    / repair values so the evaluator could calibrate magnitude relative to
    the existing state. That surface was dropped in Step 2 after review:
    the evaluator's job is to read signal DIRECTION and rough MAGNITUDE
    from the text, and the downstream ±0.03 per-turn cap (``_clamp_delta``
    in ``relationship.py``) is the real safety margin regardless of what
    the current state is. Adding running state would expand the prompt
    without tightening output semantics, and would couple prompt assembly
    to a DB read that ``evaluate_and_update`` already owns. The text-alone
    form ships as the canonical shape.

    Delimiter injection defense (Phase 8 R1-F3, 2026-04-15): the response
    text is ``html.escape``'d before interpolation so a payload containing
    ``</response_text>`` cannot break out of the wrapper block and inject
    instructions into the evaluator prompt. ``<`` and ``>`` become ``&lt;``
    and ``&gt;`` respectively; the LLM reads the escaped content correctly
    (HTML entities are transparent to capable models) but can no longer
    see a verbatim closing delimiter inside the user text. The ``quote=False``
    flag leaves quotation marks alone so the response reads naturally.

    Args:
        character_id: Canonical lowercase character ID (adelia / bina /
            reina / alicia). Unrecognised IDs are passed through; the
            system prompt will apply best-effort matching.
        response_text: The focal character's full response text from this
            turn, exactly as it was returned by the LLM and validated by
            the Whyze-Byte pipeline.

    Returns:
        A single string ready to send as the ``user`` role message in the
        evaluation API call.
    """
    cid = character_id.lower().strip() if character_id else _UNKNOWN_CHARACTER
    # R1-F3 closure: escape < and > so the closing </response_text>
    # delimiter cannot appear verbatim inside the user-supplied content.
    safe_text = html.escape(response_text, quote=False)
    return (
        f"Character: {cid}\n\n"
        f"<response_text>\n{safe_text}\n</response_text>\n\n"
        "Evaluate the four relationship dimensions for this turn and respond "
        "with only the JSON object described in the system prompt."
    )


# ---------------------------------------------------------------------------
# Response parser
# ---------------------------------------------------------------------------

def parse_eval_response(text: str) -> DyadDeltaProposal | None:
    """Parse an LLM relationship evaluation response into a delta proposal.

    Strips markdown fences, parses JSON, validates via Pydantic, and
    returns a ``DyadDeltaProposal``. Returns ``None`` on any failure so
    the caller can fall back to ``_propose_deltas``.

    AC-8.9: Returns None on malformed JSON, missing fields, non-numeric
    values.
    AC-8.10: ``repair_history`` is clamped to 0.0 if the LLM returns a
    negative value. Repair is positive-only by architecture; a single turn
    cannot erase accumulated repair history.
    AC-8.5: Out-of-range values are clamped at the boundary [-1.0, 1.0]
    with a warning log.

    Args:
        text: Raw string returned by the LLM (may contain markdown fences).

    Returns:
        A ``DyadDeltaProposal`` with values clamped and validated, or
        ``None`` if parsing fails for any reason.
    """
    # Strip markdown fences that some models emit despite instructions.
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        # Drop opening fence line and any closing fence.
        inner = [
            ln for ln in lines[1:]
            if not ln.strip().startswith("```")
        ]
        cleaned = "\n".join(inner).strip()

    try:
        raw = json.loads(cleaned)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning(
            "llm_eval_parse_json_failed",
            extra={"error": str(exc), "raw_prefix": cleaned[:120]},
        )
        return None

    # R1-F1 fail-closed guard (2026-04-15): JSON can decode to any of the
    # seven shapes (object / array / string / number / bool / null). Only
    # the object shape has ``.keys()``; everything else raised
    # AttributeError pre-remediation and propagated out of
    # ``evaluate_and_update`` instead of falling back to the heuristic.
    # Pydantic would also reject these with a ValidationError, but the
    # explicit guard logs a cleaner reason.
    if not isinstance(raw, dict):
        logger.warning(
            "llm_eval_parse_non_object",
            extra={"type": type(raw).__name__, "raw_prefix": cleaned[:120]},
        )
        return None

    # R1-F2 closure (2026-04-15): route field-shape + type validation
    # through the RelationshipEvalResponse Pydantic schema. The before-
    # validator on ``_NumericValue`` rejects booleans; missing fields
    # and non-numeric values raise ValidationError → None. Extra fields
    # are ignored per model_config.
    try:
        model = RelationshipEvalResponse.model_validate(raw)
    except ValidationError as exc:
        logger.warning(
            "llm_eval_parse_schema_validation_failed",
            extra={"error": str(exc), "raw_keys": sorted(raw.keys())},
        )
        return None

    # Clamp out-of-range values and warn. The schema stays permissive on
    # range so we can clamp-with-warn here rather than failing closed on
    # a slightly-out-of-bounds LLM response (AC-8.5). This degrades
    # gracefully: the ±0.03 downstream cap is the real safety margin.
    def _clamp_range(value: float, lo: float, hi: float, field: str) -> float:
        if value < lo or value > hi:
            logger.warning(
                "llm_eval_parse_out_of_range",
                extra={"field": field, "value": value, "clamped_to": max(lo, min(hi, value))},
            )
            return max(lo, min(hi, value))
        return value

    intimacy = _clamp_range(model.intimacy, -1.0, 1.0, "intimacy")
    tension = _clamp_range(model.unresolved_tension, -1.0, 1.0, "unresolved_tension")
    trust = _clamp_range(model.trust, -1.0, 1.0, "trust")
    repair_raw = model.repair_history

    # AC-8.10: repair_history is positive-only. Clamp negative to 0.0.
    if repair_raw < 0.0:
        logger.warning(
            "llm_eval_parse_negative_repair_history",
            extra={"value": repair_raw, "clamped_to": 0.0},
        )
        repair_raw = 0.0
    repair = _clamp_range(repair_raw, 0.0, 1.0, "repair_history")

    return DyadDeltaProposal(
        intimacy=intimacy,
        unresolved_tension=tension,
        trust=trust,
        repair_history=repair,
    )
