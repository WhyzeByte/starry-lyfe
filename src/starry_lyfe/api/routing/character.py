"""Narrow character router.

``resolve_character_id`` is the single canonical entry point for turning
a request's three character-routing surfaces (``X-SC-Force-Character``
header, inline ``/<char>`` override in the user message, ``model`` field)
plus a per-deployment default into a single ``CharacterRoutingDecision``.

Lesson #2 (subtract narrow context from wide pattern space) is enforced
structurally: the decision flows downstream as an immutable frozen
dataclass parameter rather than a mutable context object. Once
resolved, no other code is allowed to override the focal character —
the type system makes contamination impossible.

Per CLAUDE.md §14, the priority order is:

1. ``X-SC-Force-Character`` header (optional force-character override for any client)
2. Inline ``/<char>`` or ``/all`` override at start of user message
3. ``model`` field matching a canonical character name (Msty path)
4. Settings ``default_character`` fallback

Unknown character IDs raise ``CharacterNotFoundError``; the FastAPI
exception handler in ``api.errors`` converts that to a 400 with a
``valid_character_ids`` list in the body.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from starry_lyfe.canon.schemas.enums import CharacterID, CharacterNotFoundError

from ..config import ApiSettings

# Set of canonical character IDs (lowercased). ``starry-lyfe`` is a
# legacy alias accepted on the model field and X-SC-Force-Character
# header — it routes to the deployment default.
_CANONICAL_IDS: frozenset[str] = frozenset(CharacterID.all_strings())
_LEGACY_DEFAULT_ALIAS: str = "starry-lyfe"

# Inline override marker: a leading slash followed by a known short id.
# ``/all`` is the multi-character (Crew) marker — mapped to the focal
# default at character-resolution time; the Crew expansion is done in
# ``preprocess_msty_request`` since it requires roster context.
_INLINE_OVERRIDE_NAMES: frozenset[str] = _CANONICAL_IDS | {"all"}
_INLINE_OVERRIDE_RE = re.compile(
    r"^\s*/(" + "|".join(sorted(_INLINE_OVERRIDE_NAMES)) + r")\b\s*",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CharacterRoutingDecision:
    """Resolved character with full audit trail.

    Attributes:
        character_id: Canonical lowercase id (``adelia|bina|reina|alicia``).
        source: Which input surface won. One of ``"header"``,
            ``"inline_override"``, ``"model_field"``, ``"default"``.
        raw_value: Exactly what the request sent for the winning source
            (e.g. ``"Adelia"`` even though the resolved id is ``"adelia"``).
            Useful for observability + structured logs.
        all_override: True when the inline ``/all`` Crew marker fired;
            the character_id holds the focal default and the Msty
            preprocessor expands the roster from the request body.
    """

    character_id: str
    source: str
    raw_value: str
    all_override: bool = False


def resolve_character_id(
    header: str | None,
    model_field: str | None,
    user_message: str | None,
    settings: ApiSettings,
) -> CharacterRoutingDecision:
    """Resolve the focal character from request inputs (priority-ordered).

    Pure function, no side effects. All four inputs are inspected in
    priority order; the first one that yields a known canonical id (or
    the ``starry-lyfe`` default alias) wins. Unknown IDs at any priority
    layer raise ``CharacterNotFoundError`` rather than silently falling
    through — that would be a lesson-#2 contamination violation
    (silent fallback hides routing bugs).
    """
    # (1) X-SC-Force-Character header
    if header is not None and header.strip():
        raw = header.strip()
        normalized = raw.lower()
        if normalized == _LEGACY_DEFAULT_ALIAS:
            return CharacterRoutingDecision(
                character_id=settings.default_character,
                source="header",
                raw_value=raw,
            )
        if normalized in _CANONICAL_IDS:
            return CharacterRoutingDecision(
                character_id=normalized,
                source="header",
                raw_value=raw,
            )
        raise CharacterNotFoundError(
            f"X-SC-Force-Character header value '{raw}' is not a canonical character. "
            f"Valid values: {sorted(_CANONICAL_IDS)} or '{_LEGACY_DEFAULT_ALIAS}'."
        )

    # (2) Inline override in user message
    if user_message is not None and user_message:
        match = _INLINE_OVERRIDE_RE.match(user_message)
        if match is not None:
            raw = match.group(0).strip()
            inline_name = match.group(1).lower()
            if inline_name == "all":
                return CharacterRoutingDecision(
                    character_id=settings.default_character,
                    source="inline_override",
                    raw_value=raw,
                    all_override=True,
                )
            return CharacterRoutingDecision(
                character_id=inline_name,
                source="inline_override",
                raw_value=raw,
            )

    # (3) model field
    if model_field is not None and model_field.strip():
        raw = model_field.strip()
        normalized = raw.lower()
        if normalized == _LEGACY_DEFAULT_ALIAS:
            return CharacterRoutingDecision(
                character_id=settings.default_character,
                source="model_field",
                raw_value=raw,
            )
        if normalized in _CANONICAL_IDS:
            return CharacterRoutingDecision(
                character_id=normalized,
                source="model_field",
                raw_value=raw,
            )
        raise CharacterNotFoundError(
            f"model field '{raw}' is not a canonical character. "
            f"Valid values: {sorted(_CANONICAL_IDS)} or '{_LEGACY_DEFAULT_ALIAS}'."
        )

    # (4) Default fallback
    return CharacterRoutingDecision(
        character_id=settings.default_character,
        source="default",
        raw_value=settings.default_character,
    )


def strip_inline_override(user_message: str) -> str:
    """Remove a leading ``/<char>`` or ``/all`` marker from the message.

    Called after ``resolve_character_id`` so the LLM never sees the
    routing marker in the user prompt body.
    """
    return _INLINE_OVERRIDE_RE.sub("", user_message, count=1)
