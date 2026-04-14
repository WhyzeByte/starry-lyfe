"""Tier 8 (Dreams): Session Health — per-session system health metrics.

Records Dreams-run timing and health indicators per session. Helps detect
drift (e.g., Dreams hasn't run for > 36h indicates scheduler failure).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TZDateTime


class SessionHealth(Base):
    """Per-session aggregate health metrics."""

    __tablename__ = "session_health"
    __table_args__ = (
        Index("ix_session_health_session_id", "session_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(nullable=False)

    dreams_last_run_at: Mapped[datetime | None] = mapped_column(TZDateTime, nullable=True)
    somatic_last_refreshed_at: Mapped[datetime | None] = mapped_column(TZDateTime, nullable=True)

    # JSONB list of warning strings raised during the session.
    warnings: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        TZDateTime, nullable=False, server_default=func.now()
    )
