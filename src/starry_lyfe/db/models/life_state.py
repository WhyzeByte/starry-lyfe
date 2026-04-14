"""Tier 8 (Dreams): Life State — per-character current emotional/psychological state.

Updated by Dreams engine overnight and by runtime session events. Drives
Alicia's away/home toggle, which in turn gates communication_mode on
Dreams-generated content (Phase A'' retroactive).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TZDateTime


class LifeState(Base):
    """One row per character. Tracks current mood/energy/focus + Alicia residency."""

    __tablename__ = "life_states"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    character_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    # Emotional state
    mood: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    energy: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    focus: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    # Alicia-specific residency (applied to all characters for schema uniformity;
    # non-Alicia characters keep is_away=False permanently).
    is_away: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    away_since: Mapped[datetime | None] = mapped_column(TZDateTime, nullable=True)
    expected_return: Mapped[datetime | None] = mapped_column(TZDateTime, nullable=True)

    last_updated_at: Mapped[datetime] = mapped_column(
        TZDateTime, nullable=False, server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        TZDateTime, nullable=False, server_default=func.now()
    )
