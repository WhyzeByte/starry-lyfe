"""Phase 7 ChatSession ORM model.

Per CLAUDE.md §13: chat_sessions tracks one row per HTTP client
session. The HTTP service upserts on first turn (creates) and on
each subsequent turn (updates ``last_turn_at`` + bumps ``turn_count``).

The session is keyed by an opaque ``id`` chosen by the HTTP layer
(typically the OWUI/Msty session token if exposed, otherwise a
random UUID). Single-operator deployment means contention is
out-of-scope; the table is small and read-light.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TZDateTime


class ChatSession(Base):
    """One row per chat session opened by Msty / OWUI / a curl operator."""

    __tablename__ = "chat_sessions"
    __table_args__ = (
        Index("ix_chat_sessions_character_id", "character_id"),
        Index("ix_chat_sessions_last_turn_at", "last_turn_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_type: Mapped[str] = mapped_column(String(20), nullable=False)
    character_id: Mapped[str] = mapped_column(String(20), nullable=False)
    # Crew roster captured at session start. Empty dict for non-Crew sessions.
    scene_characters: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    started_at: Mapped[datetime] = mapped_column(
        TZDateTime, nullable=False, server_default=func.now()
    )
    last_turn_at: Mapped[datetime] = mapped_column(
        TZDateTime, nullable=False, server_default=func.now()
    )
    turn_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
