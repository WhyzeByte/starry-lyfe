"""Tier 8 (Dreams): Drive State — character motivation/priority state.

Per-character drive tracking. Dreams nightly pass reads these to seed
generator priorities (e.g., if Bina's "shop stability" drive has low
satisfaction, diary weights toward shop-themed reflection).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Float, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TZDateTime


class DriveState(Base):
    """A motivation/priority drive for a given character."""

    __tablename__ = "drive_states"
    __table_args__ = (
        Index("ix_drive_states_character_id", "character_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    character_id: Mapped[str] = mapped_column(String(20), nullable=False)
    drive_name: Mapped[str] = mapped_column(String(50), nullable=False)
    intensity: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    last_satisfied_at: Mapped[datetime | None] = mapped_column(TZDateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        TZDateTime, nullable=False, server_default=func.now()
    )
