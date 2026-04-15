"""Post-turn episodic memory extraction (fire-and-forget).

After the SSE response closes, the chat endpoint schedules
``extract_episodic`` as ``asyncio.create_task``. The task makes a
small per-character LLM call summarizing the turn, then writes the
result as an EpisodicMemory row (memory_type='episodic') via the
existing Phase 6 ``write_diary_entry`` writer pattern.

Failure isolation: any exception inside the task is caught by the
``add_done_callback`` logger so the next request is unaffected.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from starry_lyfe.canon.schemas.enums import CharacterID
from starry_lyfe.db.models.episodic_memory import (
    EMBEDDING_DIMENSION,
    EpisodicMemory,
)
from starry_lyfe.dreams.errors import DreamsLLMError
from starry_lyfe.dreams.llm import BDOne, StubBDOne

logger = logging.getLogger(__name__)

_ZERO_EMBEDDING: list[float] = [0.0] * EMBEDDING_DIMENSION


# Per-character extraction system prompts. Each prompt asks the LLM to
# distill the turn into 1-3 sentences that another model could read
# tomorrow as the focal character's recollection of the exchange.
_EXTRACT_SYSTEM_PROMPTS: dict[str, str] = {
    "adelia": (
        "You are summarizing a conversation between Adelia Raye (ENFP-A) and Whyze for "
        "Adelia's own memory. Write 1-3 sentences in Adelia's voice (chemistry / spark "
        "/ catalyst register, present tense, first person). No em-dashes. Do not name "
        "any other character unless they appeared in the conversation."
    ),
    "bina": (
        "You are summarizing a conversation between Bina Malek (ISFJ-A) and Whyze for "
        "Bina's own memory. Write 1-3 sentences in Bina's voice (Si-declarative, "
        "log-recorded register, first person). No em-dashes. Do not name any other "
        "character unless they appeared in the conversation."
    ),
    "reina": (
        "You are summarizing a conversation between Reina Torres (ESTP-A) and Whyze for "
        "Reina's own memory. Write 1-3 sentences in Reina's voice (Se-tactical, "
        "evidence-filed register, first person). No em-dashes. Do not name any other "
        "character unless they appeared in the conversation."
    ),
    "alicia": (
        "You are summarizing a conversation between Alicia Marin (ESFP-A) and Whyze for "
        "Alicia's own memory. Write 1-3 sentences in Alicia's voice (Se-somatic, body-"
        "first present-tense register, first person). No em-dashes. Do not name any "
        "other character unless they appeared in the conversation."
    ),
}

# Sanity at module load: the four canonical characters all have a prompt.
_assert_keys_set: set[str] = set(_EXTRACT_SYSTEM_PROMPTS.keys())
if _assert_keys_set != set(CharacterID.all_strings()):
    raise RuntimeError(
        f"_EXTRACT_SYSTEM_PROMPTS character coverage mismatch: "
        f"{_assert_keys_set} vs {set(CharacterID.all_strings())}"
    )


async def extract_episodic(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    character_id: str,
    user_message: str,
    full_response_text: str,
    chat_session_id: uuid.UUID | None,
    llm_client: BDOne | StubBDOne,
) -> uuid.UUID | None:
    """Extract a single episodic memory from this turn and write it.

    Returns the new EpisodicMemory row id, or None if extraction was
    skipped (empty response, unknown character, LLM failure). The
    function commits its own transaction so the caller can fire it
    without holding the request session open.
    """
    if character_id not in _EXTRACT_SYSTEM_PROMPTS:
        logger.warning("extract_episodic_unknown_character", extra={"character_id": character_id})
        return None
    if not full_response_text.strip():
        return None

    user_prompt = (
        f"Whyze said: {user_message!r}\n"
        f"You replied: {full_response_text!r}\n\n"
        "Write your 1-3 sentence memory of this exchange now."
    )

    try:
        completion = await llm_client.complete(
            system_prompt=_EXTRACT_SYSTEM_PROMPTS[character_id],
            user_prompt=user_prompt,
            max_tokens=200,
            temperature=0.6,
        )
    except DreamsLLMError as exc:
        logger.warning(
            "extract_episodic_llm_failed",
            extra={"character_id": character_id, "error": str(exc)},
        )
        return None

    summary = str(completion.text).strip()
    if not summary:
        return None

    metadata: dict[str, Any] = {
        "source": "post_turn_extraction",
        "kind": "episodic",
        "chat_session_id": str(chat_session_id) if chat_session_id else None,
    }
    new_id = uuid.uuid4()
    row = EpisodicMemory(
        id=new_id,
        session_id=chat_session_id,
        character_id=character_id,
        participant_ids={"ids": [character_id, "whyze"]},
        event_summary=summary,
        emotional_temperature=None,
        memory_type="episodic",
        importance_score=0.5,
        embedding=_ZERO_EMBEDDING,
        metadata_=metadata,
        communication_mode=None,
        created_at=datetime.now(UTC),
    )
    async with session_factory() as session, session.begin():
        session.add(row)
    return new_id
