"""Msty Crew Conversation preprocessor.

Msty Studio's Crew mode replays prior persona responses as
``role="assistant"`` messages with a ``name`` field set to the persona
id, and prefixes Crew turns with a system prompt that names the entire
roster. Per ADR-001 the production Msty system prompts are blank, but
the Crew header still leaks roster + addressing context that we have
to extract before the chat pipeline runs.

This module narrows the wide raw payload into ``MstyPreprocessed``
before any downstream module touches it (lesson #2 — narrow at the seam).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from starry_lyfe.canon.schemas.enums import CharacterID

from ..schemas.chat import ChatMessage

_CANONICAL_IDS: frozenset[str] = frozenset(CharacterID.all_strings())

# Crew header pattern: "You are speaking as a member of a crew..." style
# system prompts usually list ``adelia, bina, reina, alicia`` somewhere
# in the body. We scan for any name mention and intersect with the
# canonical set rather than trying to parse Msty's exact phrasing —
# that phrasing is a moving target across versions.
_CREW_NAME_RE = re.compile(
    r"\b(" + "|".join(sorted(_CANONICAL_IDS)) + r")\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class PriorResponse:
    """A previously-emitted persona response captured from request history."""

    character_id: str
    text: str


@dataclass(frozen=True)
class MstyPreprocessed:
    """Narrowed view of a raw Msty chat-completion request body.

    Attributes:
        user_message: The latest user-role message (Msty strips inline
            override markers itself in some versions; the chat endpoint
            runs ``strip_inline_override`` again to be safe).
        scene_characters: Crew roster intersected with canonical IDs.
            Empty for single-character (non-Crew) requests.
        prior_responses: Past persona turns extracted from the messages
            list. Used to reconstruct ``turn_history`` for
            ``select_next_speaker``.
        system_prompt_text: The concatenated system-role messages, in
            order. Empty in production per ADR-001 but may carry Crew
            roster hints; preserved here so observability can flag any
            non-empty system prompt as a Msty regression.
    """

    user_message: str
    scene_characters: list[str]
    prior_responses: list[PriorResponse]
    system_prompt_text: str


def _last_user_message(messages: list[ChatMessage]) -> str:
    for message in reversed(messages):
        if message.role == "user":
            return message.content
    return ""


def _extract_prior_responses(messages: list[ChatMessage]) -> list[PriorResponse]:
    out: list[PriorResponse] = []
    for message in messages:
        if message.role != "assistant":
            continue
        # Msty Crew turns carry the persona id in the ``name`` field;
        # Some Crew flows prefix the content with
        # ``"<character>:" `` as a fallback.
        if message.name and message.name.lower() in _CANONICAL_IDS:
            out.append(PriorResponse(character_id=message.name.lower(), text=message.content))
            continue
        # Fallback: leading "<name>:" prefix.
        match = re.match(r"\s*(\w+)\s*:\s*", message.content)
        if match is not None:
            candidate = match.group(1).lower()
            if candidate in _CANONICAL_IDS:
                stripped = message.content[match.end():]
                out.append(PriorResponse(character_id=candidate, text=stripped))
    return out


def _detect_crew_roster(system_text: str, prior_responses: list[PriorResponse]) -> list[str]:
    # Names mentioned in any system prompt — heuristic Crew detection.
    found: set[str] = {m.lower() for m in _CREW_NAME_RE.findall(system_text)}
    # Anyone who already spoke must be in the scene roster.
    for prior in prior_responses:
        found.add(prior.character_id)
    # Stable canonical order so downstream logic is deterministic.
    return [c for c in CharacterID.all_strings() if c in found]


def preprocess_msty_request(messages: list[ChatMessage]) -> MstyPreprocessed:
    """Distill an OpenAI-compatible message list into Msty Crew context.

    Pure function. Returns an empty roster + empty prior_responses for
    requests that are not Crew Conversations (single-character chat).
    """
    user_message = _last_user_message(messages)
    system_text = "\n".join(m.content for m in messages if m.role == "system")
    prior_responses = _extract_prior_responses(messages)
    scene_characters = _detect_crew_roster(system_text, prior_responses)
    return MstyPreprocessed(
        user_message=user_message,
        scene_characters=scene_characters,
        prior_responses=prior_responses,
        system_prompt_text=system_text,
    )
