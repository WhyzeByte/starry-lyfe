"""Tier 3: Dyad State (Whyze) — mutable relationship dimensions between each woman and Whyze."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TZDateTime


class DyadStateWhyze(Base):
    """One row per Whyze-to-character dyad (exactly 4). Dimensions updated by episodic extraction."""

    __tablename__ = "dyad_state_whyze"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dyad_key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    character_id: Mapped[str] = mapped_column(String(20), nullable=False)
    pair_name: Mapped[str] = mapped_column(String(50), nullable=False)
    trust: Mapped[float] = mapped_column(Float, nullable=False)
    intimacy: Mapped[float] = mapped_column(Float, nullable=False)
    conflict: Mapped[float] = mapped_column(Float, nullable=False)
    unresolved_tension: Mapped[float] = mapped_column(Float, nullable=False)
    repair_history: Mapped[float] = mapped_column(Float, nullable=False)
    last_updated_at: Mapped[datetime] = mapped_column(TZDateTime, nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(TZDateTime, nullable=False, server_default=func.now())
