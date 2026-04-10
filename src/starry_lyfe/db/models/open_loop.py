"""Tier 6: Open Loops — unresolved threads from previous conversations."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TZDateTime


class OpenLoop(Base):
    """Unresolved threads with TTL-based expiry. Resolved by Dreams engine or conversation."""

    __tablename__ = "open_loops"
    __table_args__ = (
        Index("ix_open_loops_character_status", "character_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    character_id: Mapped[str] = mapped_column(String(20), nullable=False)
    loop_summary: Mapped[str] = mapped_column(Text, nullable=False)
    loop_type: Mapped[str] = mapped_column(String(50), nullable=False)
    urgency: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    best_next_speaker: Mapped[str | None] = mapped_column(String(20), nullable=True)
    suggested_scene: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_session_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")
    resolved_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ttl_hours: Mapped[int] = mapped_column(Integer, nullable=False, default=168)
    created_at: Mapped[datetime] = mapped_column(TZDateTime, nullable=False, server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(TZDateTime, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(TZDateTime, nullable=True)
