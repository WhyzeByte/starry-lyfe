"""Tier 2: Character Baseline — immutable at runtime personality and voice profiles."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TZDateTime


class CharacterBaseline(Base):
    """One row per character (exactly 4). Immutable at runtime."""

    __tablename__ = "character_baselines"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    character_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    epithet: Mapped[str] = mapped_column(String(100), nullable=False)
    mbti: Mapped[str] = mapped_column(String(10), nullable=False)
    cognitive_stack: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    dominant_function: Mapped[str] = mapped_column(String(5), nullable=False)
    voice_params: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    pair_name: Mapped[str] = mapped_column(String(50), nullable=False)
    pair_classification: Mapped[str] = mapped_column(String(100), nullable=False)
    pair_mechanism: Mapped[str] = mapped_column(Text, nullable=False)
    pair_core_metaphor: Mapped[str] = mapped_column(String(200), nullable=False)
    heritage: Mapped[str] = mapped_column(String(200), nullable=False)
    profession: Mapped[str] = mapped_column(String(200), nullable=False)
    is_resident: Mapped[bool] = mapped_column(Boolean, nullable=False)
    operational_travel: Mapped[str | None] = mapped_column(Text, nullable=True)
    canon_version: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TZDateTime, nullable=False, server_default=func.now())
