"""ChatSession CRUD helpers.

The HTTP endpoint upserts a session row on every chat completion
request: creates on first turn for a given session id, increments
``turn_count`` + updates ``last_turn_at`` on subsequent turns. Single
operator deployment so contention is not a concern.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from starry_lyfe.db.models import ChatSession


async def upsert_session(
    session: AsyncSession,
    *,
    session_id: uuid.UUID,
    client_type: str,
    character_id: str,
    scene_characters: list[str] | None = None,
    now: datetime | None = None,
) -> ChatSession:
    """Create or update a chat_sessions row for this turn.

    Returns the (possibly newly-created) ChatSession ORM instance.
    The caller owns the outer transaction; this helper only flushes,
    not commits.
    """
    moment = now or datetime.now(UTC)
    roster: dict[str, Any] = {"members": list(scene_characters or [])}

    existing = await session.execute(
        select(ChatSession).where(ChatSession.id == session_id)
    )
    row = existing.scalars().first()
    if row is None:
        row = ChatSession(
            id=session_id,
            client_type=client_type,
            character_id=character_id,
            scene_characters=roster,
            started_at=moment,
            last_turn_at=moment,
            turn_count=1,
        )
        session.add(row)
    else:
        row.last_turn_at = moment
        row.turn_count += 1
        # If the focal character has changed mid-session (Crew flipping
        # speakers), update the latest character_id; the original
        # character_id is preserved in the started_at / first turn so
        # observability can backtrack.
        row.character_id = character_id
        row.scene_characters = roster
    await session.flush()
    return row
