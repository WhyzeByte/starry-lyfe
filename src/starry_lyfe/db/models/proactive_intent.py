"""Tier 8 (Dreams): Proactive Intent — forward-looking character goals/plans.

Dreams generates proactive intents overnight (e.g., "Adelia wants to ask
Whyze about the weekend trip"). The runtime scene director may lift
these into activity_context when composing tomorrow's opener.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TZDateTime


class ProactiveIntent(Base):
    """A forward-looking intent/goal for a character."""

    __tablename__ = "proactive_intents"
    __table_args__ = (
        Index("ix_proactive_intents_character_id", "character_id"),
        Index("ix_proactive_intents_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    character_id: Mapped[str] = mapped_column(String(20), nullable=False)

    intent_summary: Mapped[str] = mapped_column(Text, nullable=False)
    target_session_horizon: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")

    created_at: Mapped[datetime] = mapped_column(
        TZDateTime, nullable=False, server_default=func.now()
    )
    resolved_at: Mapped[datetime | None] = mapped_column(TZDateTime, nullable=True)
