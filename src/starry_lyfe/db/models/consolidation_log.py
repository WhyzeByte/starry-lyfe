"""Tier 8 (Dreams): Consolidation Log — audit trail per Dreams run.

One row per (run_id, character_id) pair. Dreams writes a row at the end
of each per-character pass recording outputs produced and warnings.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TZDateTime


class ConsolidationLog(Base):
    """Audit trail of each Dreams per-character consolidation pass."""

    __tablename__ = "consolidation_log"
    __table_args__ = (
        Index("ix_consolidation_run_id", "run_id"),
        Index("ix_consolidation_character_id", "character_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    character_id: Mapped[str] = mapped_column(String(20), nullable=False)

    started_at: Mapped[datetime] = mapped_column(TZDateTime, nullable=False)
    finished_at: Mapped[datetime] = mapped_column(TZDateTime, nullable=False)

    # JSONB payloads: {"schedule": bool, "off_screen": N, "diary_id": "...", ...}
    outputs_written: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    warnings: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        TZDateTime, nullable=False, server_default=func.now()
    )
