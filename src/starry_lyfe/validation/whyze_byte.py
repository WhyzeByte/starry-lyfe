"""Whyze-Byte validation pipeline.

Server-side response validator that enforces the four constraint pillars
and output-hygiene rules before any response reaches the interface.

Two-tier architecture:
    Tier 1 — Hard FAIL: AI-isms, framework leakage, XML tag bleed-through.
              Any Tier-1 violation triggers immediate FAIL; response must be
              regenerated. No exceptions.
    Tier 2 — Soft WARNING: repetition, cognitive hand-off drift, em-dash
              hygiene, cross-character contamination signals. Tier-2 findings
              are collected and returned; the caller decides whether to log,
              flag for review, or regenerate.

Public API::

    from starry_lyfe.validation.whyze_byte import validate_response

    result = validate_response(
        character_id="bina",
        response_text="...",
        scene_state=scene_state,
    )
    if not result.passed:
        # regenerate or log
        for v in result.violations:
            logger.warning("Whyze-Byte: %s", v)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum

from starry_lyfe.context.types import SceneState


class ViolationTier(StrEnum):
    """Severity tier for a validation finding."""

    FAIL = "FAIL"     # hard stop, must regenerate
    WARN = "WARN"     # soft finding, log and consider regenerating


@dataclass(frozen=True)
class ValidationViolation:
    """A single validation finding."""

    tier: ViolationTier
    code: str          # short machine-readable code
    message: str       # human-readable description
    evidence: str = "" # fragment of text that triggered the finding


@dataclass
class ValidationResult:
    """Complete result of a Whyze-Byte validation pass."""

    character_id: str
    passed: bool
    violations: list[ValidationViolation] = field(default_factory=list)

    @property
    def fail_violations(self) -> list[ValidationViolation]:
        return [v for v in self.violations if v.tier == ViolationTier.FAIL]

    @property
    def warn_violations(self) -> list[ValidationViolation]:
        return [v for v in self.violations if v.tier == ViolationTier.WARN]

# ---------------------------------------------------------------------------
# Tier 1 — AI-ism detection (hard FAIL)
# ---------------------------------------------------------------------------

_AI_ISM_PATTERNS: list[re.Pattern[str]] = [
    # Self-identification as an AI system (the canonical violation)
    re.compile(r"\bas an ai\b", re.IGNORECASE),
    re.compile(r"\bi'?m an ai\b", re.IGNORECASE),
    re.compile(r"\blanguage model\b", re.IGNORECASE),
    re.compile(r"\bchatbot\b", re.IGNORECASE),
    re.compile(r"\bai assistant\b", re.IGNORECASE),
    # AI-training self-reference — scoped to prevent false-positives on
    # "my MMA training" (Reina), "my pyrotechnics training" (Adelia), etc.
    re.compile(r"\bmy (ai |machine |model )?(training|programming) (prevents|limits|stops|means)\b", re.IGNORECASE),
    re.compile(r"\bi (was|am) (programmed|trained|designed) (to|by)\b", re.IGNORECASE),
    re.compile(r"\bi'?m (programmed|trained|designed) (to|by)\b", re.IGNORECASE),
    # Self-naming the model — only fire on self-identification, not the given name "Claude"
    re.compile(r"\bi'?m claude\b", re.IGNORECASE),
    re.compile(r"\bthis is claude\b", re.IGNORECASE),
    re.compile(r"\bclaude (ai|here|assistant|model)\b", re.IGNORECASE),
    # Anthropic — scoped to AI-company-reference context only
    re.compile(r"\b(created|made|built|developed|trained) by anthropic\b", re.IGNORECASE),
    re.compile(r"\banthropic (ai|policy|model|system|guidelines)\b", re.IGNORECASE),
    re.compile(r"\banthropics? (says|requires|prevents|limits)\b", re.IGNORECASE),
]


def _check_ai_isms(text: str) -> list[ValidationViolation]:
    violations: list[ValidationViolation] = []
    for pattern in _AI_ISM_PATTERNS:
        match = pattern.search(text)
        if match:
            violations.append(ValidationViolation(
                tier=ViolationTier.FAIL,
                code="AI_ISM",
                message="Response contains an AI-awareness break.",
                evidence=match.group(0),
            ))
    return violations


# ---------------------------------------------------------------------------
# Tier 1 — Framework / prompt leakage (hard FAIL)
# ---------------------------------------------------------------------------

_FRAMEWORK_LEAK_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"</?PERSONA_KERNEL>", re.IGNORECASE),
    re.compile(r"</?CONSTRAINTS>", re.IGNORECASE),
    re.compile(r"</?VOICE_DIRECTIVES>", re.IGNORECASE),
    re.compile(r"</?CANON_FACTS>", re.IGNORECASE),
    re.compile(r"</?SCENE_CONTEXT>", re.IGNORECASE),
    re.compile(r"\bAXIOM 2\.\d", re.IGNORECASE),
    re.compile(r"\bTier [123] —", re.IGNORECASE),
    re.compile(r"<!-- PRESERVE -->", re.IGNORECASE),
    re.compile(r"WHYZE_BYTE_CONSTRAINTS", re.IGNORECASE),
    re.compile(r"Persona_Tier_Framework", re.IGNORECASE),
]


def _check_framework_leakage(text: str) -> list[ValidationViolation]:
    violations: list[ValidationViolation] = []
    for pattern in _FRAMEWORK_LEAK_PATTERNS:
        match = pattern.search(text)
        if match:
            violations.append(ValidationViolation(
                tier=ViolationTier.FAIL,
                code="FRAMEWORK_LEAK",
                message="Response contains internal framework/prompt content.",
                evidence=match.group(0),
            ))
    return violations

# ---------------------------------------------------------------------------
# Tier 2 — Output hygiene (soft WARN)
# ---------------------------------------------------------------------------

_EM_DASH_RE = re.compile(r"[—–]")  # em dash U+2014, en dash U+2013


def _check_output_hygiene(text: str) -> list[ValidationViolation]:
    violations: list[ValidationViolation] = []
    match = _EM_DASH_RE.search(text)
    if match:
        violations.append(ValidationViolation(
            tier=ViolationTier.WARN,
            code="EM_DASH",
            message="Response contains em-dash or en-dash (output hygiene violation).",
            evidence=text[max(0, match.start() - 20): match.end() + 20],
        ))
    return violations


# ---------------------------------------------------------------------------
# Tier 2 — Repetition detection (soft WARN)
# ---------------------------------------------------------------------------

_PHRASE_MIN_LEN = 5      # minimum word count to consider a phrase
_PHRASE_WINDOW = 6       # word window for phrase extraction
_REPEAT_THRESHOLD = 2    # appearances within the response


def _extract_ngrams(text: str, n: int) -> list[str]:
    words = re.findall(r"\b\w+\b", text.lower())
    return [" ".join(words[i: i + n]) for i in range(len(words) - n + 1)]


def _check_repetition(text: str) -> list[ValidationViolation]:
    violations: list[ValidationViolation] = []
    for n in range(_PHRASE_MIN_LEN, _PHRASE_WINDOW + 1):
        ngrams = _extract_ngrams(text, n)
        seen: dict[str, int] = {}
        for gram in ngrams:
            seen[gram] = seen.get(gram, 0) + 1
        for gram, count in seen.items():
            if count >= _REPEAT_THRESHOLD:
                violations.append(ValidationViolation(
                    tier=ViolationTier.WARN,
                    code="REPETITION",
                    message=f"Phrase repeated {count}x: '{gram}'",
                    evidence=gram,
                ))
                break  # one repetition warning per response
    return violations


# ---------------------------------------------------------------------------
# Tier 2 — Cognitive hand-off integrity (per-character, soft WARN)
# ---------------------------------------------------------------------------

# Patterns that signal a cognitive hand-off violation for each character.
# Each entry: (pattern, violation message)
_HANDOFF_VIOLATIONS: dict[str, list[tuple[re.Pattern[str], str]]] = {
    "adelia": [
        (
            re.compile(r"\bI (resolved|solved|figured out|sequenced) (the|this|my) "
                       r"(logistics|plan|sequence|problem)", re.IGNORECASE),
            "Adelia solved her own logistical problem (Entangled Pair hand-off broken).",
        ),
    ],
    "bina": [
        # Narrow to phrases that specifically abdicate the audit role.
        # Common affirmations like "sounds good" are excluded — they fire on
        # natural speech far too often to be useful signal.
        (
            re.compile(r"\bwhatever you (think|decide|want) (is best|works)\b", re.IGNORECASE),
            "Bina may be deferring judgment she should apply (Circuit Pair audit role).",
        ),
        (
            re.compile(r"\bi'?m (happy|fine|okay) (with|if) you (decide|handle|manage)\b",
                       re.IGNORECASE),
            "Bina may be abdicating the safety-audit function (Circuit Pair structural register).",
        ),
    ],
    "reina": [
        (
            re.compile(r"\bhow does that make you feel\b", re.IGNORECASE),
            "Reina used therapist language (Admissibility Protocol violation).",
        ),
    ],
    # Alicia's physical-contact narration check is mode-conditional.
    # Handled separately in _check_cognitive_handoff — see ALICIA_REMOTE_PATTERNS.
    "alicia": [],
}

# Alicia-specific: physical contact narration is only a violation in remote mode.
# In person, somatic contact is her canonical function and should not be flagged.
_ALICIA_REMOTE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"\bI (reach|lean) (out|across|over|in) and (touch|hold|grab|take)\b",
                   re.IGNORECASE),
        "Alicia narrating physical contact that is impossible in remote mode "
        "(Phase A'' constraint: somatic register adapts to communication mode).",
    ),
    (
        re.compile(r"\bI put my (hand|arm|weight|body)\b", re.IGNORECASE),
        "Alicia narrating physical contact that is impossible in remote mode.",
    ),
]


def _check_cognitive_handoff(
    character_id: str,
    text: str,
    scene_state: SceneState,
) -> list[ValidationViolation]:
    violations: list[ValidationViolation] = []

    # Per-character general patterns
    patterns = _HANDOFF_VIOLATIONS.get(character_id, [])
    for pattern, message in patterns:
        match = pattern.search(text)
        if match:
            violations.append(ValidationViolation(
                tier=ViolationTier.WARN,
                code="HANDOFF_DRIFT",
                message=message,
                evidence=match.group(0),
            ))

    # Alicia: physical-contact narration only violates in remote mode.
    # In-person physical contact is her canonical somatic-regulation function.
    if character_id == "alicia":
        from starry_lyfe.context.types import CommunicationMode
        is_remote = scene_state.communication_mode != CommunicationMode.IN_PERSON
        if is_remote:
            for pattern, message in _ALICIA_REMOTE_PATTERNS:
                match = pattern.search(text)
                if match:
                    violations.append(ValidationViolation(
                        tier=ViolationTier.WARN,
                        code="HANDOFF_DRIFT",
                        message=message,
                        evidence=match.group(0),
                    ))

    return violations

# ---------------------------------------------------------------------------
# Tier 2 — Cross-character contamination (soft WARN)
# ---------------------------------------------------------------------------

# Markers exclusive to each character. Presence in another character's
# response suggests voice drift or cross-character contamination.
_CHAR_EXCLUSIVE_MARKERS: dict[str, list[str]] = {
    "adelia": ["Marrickville", "Las Fallas", "Ozone and Ember", "Ozone & Ember"],
    "bina":   ["samovar", "Urmia", "Circuit Pair", "Loth Wolf"],
    "reina":  ["Cuatrecasas", "Kinetic Pair", "Bishop", "Vex"],
    # Diacritic-agnostic partial forms: "Famaill" matches Famaillá/Famailla,
    # "Canciller" matches Cancillería/Cancilleria across all encodings.
    "alicia": ["Famaill", "Canciller", "Solstice Pair", "Four-Phase Return"],
}


def _check_contamination(
    character_id: str,
    text: str,
) -> list[ValidationViolation]:
    violations: list[ValidationViolation] = []
    for owner, markers in _CHAR_EXCLUSIVE_MARKERS.items():
        if owner == character_id:
            continue
        for marker in markers:
            if marker.lower() in text.lower():
                violations.append(ValidationViolation(
                    tier=ViolationTier.WARN,
                    code="CONTAMINATION",
                    message=f"Response contains '{marker}' — exclusive to {owner}.",
                    evidence=marker,
                ))
    return violations


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def validate_response(
    character_id: str,
    response_text: str,
    scene_state: SceneState | None = None,
) -> ValidationResult:
    """Run the full Whyze-Byte validation pipeline on a generated response.

    Tier 1 violations cause ``passed=False`` regardless of Tier 2 findings.
    Tier 2 violations are collected but do not automatically fail the result —
    callers should log them and consider regeneration based on severity.

    Args:
        character_id: Canonical character identifier (adelia/bina/reina/alicia).
        response_text: The generated response text to validate.
        scene_state: Current scene state, used for context-sensitive checks.

    Returns:
        ValidationResult with ``passed`` flag and list of violations.
    """
    if scene_state is None:
        scene_state = SceneState()

    violations: list[ValidationViolation] = []

    # Tier 1 checks (FAIL)
    violations.extend(_check_ai_isms(response_text))
    violations.extend(_check_framework_leakage(response_text))

    # Tier 2 checks (WARN)
    violations.extend(_check_output_hygiene(response_text))
    violations.extend(_check_repetition(response_text))
    violations.extend(_check_cognitive_handoff(character_id, response_text, scene_state))
    violations.extend(_check_contamination(character_id, response_text))

    has_fail = any(v.tier == ViolationTier.FAIL for v in violations)
    return ValidationResult(
        character_id=character_id,
        passed=not has_fail,
        violations=violations,
    )
