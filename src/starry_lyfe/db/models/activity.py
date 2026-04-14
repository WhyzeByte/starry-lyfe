"""Tier 8 (Dreams): Activity — Dreams-generated activity design for next session.

Consumed at runtime by Phase 5 SceneDirector via activity_context and by
Phase 3 assemble_context Layer 6. Alicia-away activities carry
communication_mode per Phase A'' retroactive contract.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TZDateTime


class Activity(Base):
    """Dreams-generated scene opener for tomorrow's session.

    communication_mode is nullable; populated for Alicia-away scenes so
    Phase A'' layer-5 filtering honors the constraint on read.
    """

    __tablename__ = "activities"
    __table_args__ = (
        Index("ix_activities_character_id", "character_id"),
        Index("ix_activities_expires_at", "expires_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    character_id: Mapped[str] = mapped_column(String(20), nullable=False)

    scene_description: Mapped[str] = mapped_column(Text, nullable=False)
    narrator_script: Mapped[str] = mapped_column(Text, nullable=False)
    choice_tree: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    # Phase A'' retroactive: Alicia-away content carries phone/letter/video_call tag.
    communication_mode: Mapped[str | None] = mapped_column(String(20), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        TZDateTime, nullable=False, server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(TZDateTime, nullable=False)
