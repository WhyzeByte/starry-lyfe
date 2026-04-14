"""Tier 8 (Dreams): Consolidated Memory — aggregated memory chunks post-Dreams.

Dreams consolidates highest-salience episodic memories into narrative summaries
overnight. These become durable memory anchors for subsequent sessions.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Float, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TZDateTime


class ConsolidatedMemory(Base):
    """Aggregated memory from Dreams consolidation pass."""

    __tablename__ = "consolidated_memories"
    __table_args__ = (
        Index("ix_consolidated_character_id", "character_id"),
        Index("ix_consolidated_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    character_id: Mapped[str] = mapped_column(String(20), nullable=False)

    # UUIDs of source episodic memories that fed this consolidation.
    consolidated_from: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    narrative_summary: Mapped[str] = mapped_column(Text, nullable=False)
    salience: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    created_at: Mapped[datetime] = mapped_column(
        TZDateTime, nullable=False, server_default=func.now()
    )
