"""Tier 5: Episodic Memories — conversation-extracted events with pgvector embeddings."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import Float, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TZDateTime

EMBEDDING_DIMENSION: int = 768


class EpisodicMemory(Base):
    """Conversation-extracted events with semantic embeddings for retrieval.

    The participant_ids JSONB array captures all participants (not just the owning character),
    enabling queries for woman-to-woman memories.
    """

    __tablename__ = "episodic_memories"
    __table_args__ = (
        Index("ix_episodic_character_id", "character_id"),
        Index("ix_episodic_created_at", "created_at"),
        Index("ix_episodic_participant_ids", "participant_ids", postgresql_using="gin"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    character_id: Mapped[str] = mapped_column(String(20), nullable=False)
    participant_ids: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    event_summary: Mapped[str] = mapped_column(Text, nullable=False)
    emotional_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    memory_type: Mapped[str] = mapped_column(String(50), nullable=False)
    importance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    embedding: Mapped[Any] = mapped_column(Vector(EMBEDDING_DIMENSION), nullable=False)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TZDateTime, nullable=False, server_default=func.now())
    decayed_at: Mapped[datetime | None] = mapped_column(TZDateTime, nullable=True)
