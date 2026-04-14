"""Positive fidelity test harness (Phase F-Fidelity).

Complements ``whyze_byte.py`` (negative filter) with rubric-scored positive
checks. Whyze-Byte answers "this is not obviously broken." Fidelity rubrics
answer "this genuinely sounds like her."

Spec: ``Docs/_phases/PHASE_F_FIDELITY.md``.

Scoring engine has three methods over an assembled prompt string:
- ``canonical_marker_presence``: fraction of required phrases present
- ``anti_pattern_absence``: 1.0 if zero forbidden phrases, 0.0 otherwise
- ``structural_presence``: fraction of required structural markers present

``score_rubric`` combines the three into a weighted composite:
``composite = 0.5 * markers + 0.3 * anti_pattern + 0.2 * structural``.

A rubric passes when ``composite >= rubric.min_score``. Static scoring
only — no LLM calls, no embedding calls. Tests run <10s.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Valid rubric dimension names. Constrained set — keep in sync with
# PHASE_F_FIDELITY.md §2 "Rubric taxonomy".
RUBRIC_DIMENSIONS: frozenset[str] = frozenset({
    "voice_authenticity",
    "pair_authenticity",
    "cognitive_function",
    "body_register",
    "conflict_register",
    "repair_register",
    "autonomy_outside_pair",
})


@dataclass(frozen=True)
class FidelityRubric:
    """A single scoring rubric for one (character, dimension) pair.

    Canonical markers are positive signals that MUST appear for the
    dimension to score well. Anti-patterns are forbidden substrings; any
    match drives anti_pattern_score to 0.0. Required structural markers
    are substrings that the assembled prompt must contain for the
    structural_score to climb.

    min_score gates pass/fail on the composite score.
    """

    dimension: str
    character_id: str
    canonical_markers: tuple[str, ...]
    anti_patterns: tuple[str, ...] = ()
    required_structural: tuple[str, ...] = ()
    min_score: float = 0.7

    def __post_init__(self) -> None:
        if self.dimension not in RUBRIC_DIMENSIONS:
            msg = (
                f"Unknown rubric dimension {self.dimension!r}. "
                f"Valid: {sorted(RUBRIC_DIMENSIONS)}"
            )
            raise ValueError(msg)
        if not 0.0 <= self.min_score <= 1.0:
            msg = f"min_score must be in [0.0, 1.0], got {self.min_score}"
            raise ValueError(msg)


@dataclass
class FidelityScore:
    """Result of scoring a single rubric against one assembled prompt."""

    rubric: FidelityRubric
    marker_score: float
    anti_pattern_score: float
    structural_score: float
    composite: float
    reasons: list[str] = field(default_factory=list)

    def passed(self) -> bool:
        """True if composite meets or exceeds the rubric's min_score."""
        return self.composite >= self.rubric.min_score

    def summary(self) -> str:
        """Human-readable one-line summary."""
        verdict = "PASS" if self.passed() else "FAIL"
        return (
            f"[{verdict}] {self.rubric.character_id}.{self.rubric.dimension}: "
            f"composite={self.composite:.2f} "
            f"(markers={self.marker_score:.2f}, "
            f"anti={self.anti_pattern_score:.2f}, "
            f"structural={self.structural_score:.2f}) "
            f"threshold={self.rubric.min_score:.2f}"
        )


# Composite weights. Markers carry the most signal because the goal is
# "sounds like her," not "has the right XML tags." Anti-patterns are a
# binary safety net. Structural presence is a final check that the
# assembler emitted the right scaffolding.
_MARKER_WEIGHT: float = 0.5
_ANTI_PATTERN_WEIGHT: float = 0.3
_STRUCTURAL_WEIGHT: float = 0.2


def canonical_marker_presence(
    prompt_text: str,
    markers: tuple[str, ...] | list[str],
) -> tuple[float, list[str]]:
    """Fraction of canonical markers found as substrings in the prompt.

    Returns ``(score, missing)`` where ``score`` is in [0.0, 1.0] and
    ``missing`` lists every marker that was NOT found. Empty markers
    list returns 1.0 (vacuous truth — nothing required, nothing missed).
    """
    if not markers:
        return 1.0, []
    missing = [m for m in markers if m not in prompt_text]
    found_count = len(markers) - len(missing)
    return found_count / len(markers), missing


def anti_pattern_absence(
    prompt_text: str,
    patterns: tuple[str, ...] | list[str],
) -> tuple[float, list[str]]:
    """Binary safety check: 1.0 if no pattern present, 0.0 if any present.

    Returns ``(score, offenders)`` where ``offenders`` lists every
    anti-pattern that DID appear in the prompt. Empty patterns list
    returns 1.0 (nothing forbidden, nothing violated).
    """
    if not patterns:
        return 1.0, []
    offenders = [p for p in patterns if p in prompt_text]
    return (0.0 if offenders else 1.0), offenders


def structural_presence(
    prompt_text: str,
    required: tuple[str, ...] | list[str],
) -> tuple[float, list[str]]:
    """Fraction of required structural substrings present in the prompt.

    Same shape as ``canonical_marker_presence`` but semantically reserved
    for assembler-emitted scaffolding (XML markers, layer headers like
    ``"Voice rhythm exemplars:"``, pair metadata field labels).
    """
    if not required:
        return 1.0, []
    missing = [r for r in required if r not in prompt_text]
    found_count = len(required) - len(missing)
    return found_count / len(required), missing


def score_rubric(prompt_text: str, rubric: FidelityRubric) -> FidelityScore:
    """Score a prompt against a rubric. Returns a FidelityScore with reasons."""
    marker_score, missing_markers = canonical_marker_presence(
        prompt_text, rubric.canonical_markers
    )
    anti_score, anti_offenders = anti_pattern_absence(
        prompt_text, rubric.anti_patterns
    )
    structural_score, missing_structural = structural_presence(
        prompt_text, rubric.required_structural
    )

    composite = (
        _MARKER_WEIGHT * marker_score
        + _ANTI_PATTERN_WEIGHT * anti_score
        + _STRUCTURAL_WEIGHT * structural_score
    )

    reasons: list[str] = []
    if missing_markers:
        reasons.append(
            f"Missing {len(missing_markers)}/{len(rubric.canonical_markers)} "
            f"canonical markers: {missing_markers}"
        )
    if anti_offenders:
        reasons.append(f"Anti-pattern offenders detected: {anti_offenders}")
    if missing_structural:
        reasons.append(
            f"Missing {len(missing_structural)}/{len(rubric.required_structural)} "
            f"structural markers: {missing_structural}"
        )
    if not reasons:
        reasons.append("All canonical markers present, no anti-patterns, full structure.")

    return FidelityScore(
        rubric=rubric,
        marker_score=marker_score,
        anti_pattern_score=anti_score,
        structural_score=structural_score,
        composite=composite,
        reasons=reasons,
    )
