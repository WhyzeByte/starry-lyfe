"""Phase 7 HTTP service — add chat_sessions table.

Revision ID: 004
Revises: 003
Create Date: 2026-04-15

Creates the ``chat_sessions`` table that the Phase 7 HTTP service uses
to track one row per Msty / curl operator session. Per
CLAUDE.md §13. Single-operator deployment so contention is not a
concern.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "004"
down_revision: str | None = "003"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None

SCHEMA = "starry_lyfe"


def upgrade() -> None:
    op.create_table(
        "chat_sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("client_type", sa.String(20), nullable=False),
        sa.Column("character_id", sa.String(20), nullable=False),
        sa.Column("scene_characters", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "last_turn_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("turn_count", sa.Integer, nullable=False, server_default="0"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_chat_sessions_character_id",
        "chat_sessions",
        ["character_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_chat_sessions_last_turn_at",
        "chat_sessions",
        ["last_turn_at"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index("ix_chat_sessions_last_turn_at", table_name="chat_sessions", schema=SCHEMA)
    op.drop_index("ix_chat_sessions_character_id", table_name="chat_sessions", schema=SCHEMA)
    op.drop_table("chat_sessions", schema=SCHEMA)
