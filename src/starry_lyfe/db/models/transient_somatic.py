"""Tier 7: Transient Somatic State — per-character biological/psychological state with decay."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Float, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TZDateTime

DEFAULT_DECAY_CONFIG: dict[str, float] = {
    "fatigue": 8.0,
    "stress_residue": 24.0,
    "injury_residue": 72.0,
}


class TransientSomaticState(Base):
    """One row per character (exactly 4). Multi-dimensional state that decays between sessions.

    Decay is exponential: new_value = current_value * 0.5^(elapsed_hours / half_life_hours).
    Per-field half-lives are stored in decay_config JSONB for per-character tuning.
    """

    __tablename__ = "transient_somatic_states"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    character_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    fatigue: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    stress_residue: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    injury_residue: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    active_protocols: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    protocol_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    custom_fields: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    decay_config: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    last_decayed_at: Mapped[datetime] = mapped_column(TZDateTime, nullable=False, server_default=func.now())
    last_updated_at: Mapped[datetime] = mapped_column(TZDateTime, nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(TZDateTime, nullable=False, server_default=func.now())
