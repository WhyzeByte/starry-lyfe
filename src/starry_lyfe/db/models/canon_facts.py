"""Tier 1: Canon Facts — immutable truths from YAML source."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TZDateTime


class CanonFact(Base):
    """Immutable canonical facts seeded from YAML. One row per entity-fact pair."""

    __tablename__ = "canon_facts"
    __table_args__ = (
        UniqueConstraint("entity_type", "entity_key", "fact_key", name="uq_canon_fact_entity_fact"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_key: Mapped[str] = mapped_column(String(100), nullable=False)
    fact_key: Mapped[str] = mapped_column(String(200), nullable=False)
    fact_value: Mapped[str] = mapped_column(Text, nullable=False)
    canon_version: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TZDateTime, nullable=False, server_default=func.now())
