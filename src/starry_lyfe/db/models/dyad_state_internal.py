"""Tier 4: Dyad State (Internal) — mutable relationship dimensions between the women."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TZDateTime


class DyadStateInternal(Base):
    """One row per inter-woman dyad (exactly 6: 3 resident + 3 Alicia-orbital).

    Alicia-orbital dyads have is_currently_active=false when she is away on operations.
    Dimension values persist through absence and are NOT reset on departure or return.
    Updates to dimensions are only applied when is_currently_active is true.
    """

    __tablename__ = "dyad_state_internal"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dyad_key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    member_a: Mapped[str] = mapped_column(String(20), nullable=False)
    member_b: Mapped[str] = mapped_column(String(20), nullable=False)
    subtype: Mapped[str] = mapped_column(String(30), nullable=False)
    interlock: Mapped[str | None] = mapped_column(String(50), nullable=True)
    trust: Mapped[float] = mapped_column(Float, nullable=False)
    intimacy: Mapped[float] = mapped_column(Float, nullable=False)
    conflict: Mapped[float] = mapped_column(Float, nullable=False)
    unresolved_tension: Mapped[float] = mapped_column(Float, nullable=False)
    repair_history: Mapped[float] = mapped_column(Float, nullable=False)
    is_currently_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_updated_at: Mapped[datetime] = mapped_column(TZDateTime, nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(TZDateTime, nullable=False, server_default=func.now())
