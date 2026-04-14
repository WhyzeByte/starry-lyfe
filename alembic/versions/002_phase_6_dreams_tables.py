"""Phase 6 Dreams engine — add Tier 8 tables.

Revision ID: 002
Revises: 001
Create Date: 2026-04-14

Adds the 7 Dreams-populated tables (life_states, activities,
consolidated_memories, consolidation_log, drive_states,
proactive_intents, session_health) and the Phase A'' retroactive
communication_mode columns on activities and episodic_memories.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: str | None = "001"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None

SCHEMA = "starry_lyfe"


def upgrade() -> None:
    """Create the 7 Dreams tables and add communication_mode column."""

    # Tier 8a: Life State
    op.create_table(
        "life_states",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("character_id", sa.String(20), nullable=False, unique=True),
        sa.Column("mood", sa.Float(), nullable=False, server_default=sa.text("0.5")),
        sa.Column("energy", sa.Float(), nullable=False, server_default=sa.text("0.5")),
        sa.Column("focus", sa.Float(), nullable=False, server_default=sa.text("0.5")),
        sa.Column("is_away", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("away_since", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expected_return", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )

    # Tier 8b: Activity (Dreams-generated scene openers)
    op.create_table(
        "activities",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("character_id", sa.String(20), nullable=False),
        sa.Column("scene_description", sa.Text(), nullable=False),
        sa.Column("narrator_script", sa.Text(), nullable=False),
        sa.Column("choice_tree", sa.dialects.postgresql.JSONB(), nullable=False),
        # Phase A'' retroactive: Alicia-away tagging.
        sa.Column("communication_mode", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        schema=SCHEMA,
    )
    op.create_index("ix_activities_character_id", "activities", ["character_id"], schema=SCHEMA)
    op.create_index("ix_activities_expires_at", "activities", ["expires_at"], schema=SCHEMA)

    # Tier 8c: Consolidated Memory
    op.create_table(
        "consolidated_memories",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("character_id", sa.String(20), nullable=False),
        sa.Column("consolidated_from", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("narrative_summary", sa.Text(), nullable=False),
        sa.Column("salience", sa.Float(), nullable=False, server_default=sa.text("0.5")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_index("ix_consolidated_character_id", "consolidated_memories", ["character_id"], schema=SCHEMA)
    op.create_index("ix_consolidated_created_at", "consolidated_memories", ["created_at"], schema=SCHEMA)

    # Tier 8d: Consolidation Log
    op.create_table(
        "consolidation_log",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("character_id", sa.String(20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("outputs_written", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("warnings", sa.dialects.postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_index("ix_consolidation_run_id", "consolidation_log", ["run_id"], schema=SCHEMA)
    op.create_index("ix_consolidation_character_id", "consolidation_log", ["character_id"], schema=SCHEMA)

    # Tier 8e: Drive State
    op.create_table(
        "drive_states",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("character_id", sa.String(20), nullable=False),
        sa.Column("drive_name", sa.String(50), nullable=False),
        sa.Column("intensity", sa.Float(), nullable=False, server_default=sa.text("0.5")),
        sa.Column("last_satisfied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_index("ix_drive_states_character_id", "drive_states", ["character_id"], schema=SCHEMA)

    # Tier 8f: Proactive Intent
    op.create_table(
        "proactive_intents",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("character_id", sa.String(20), nullable=False),
        sa.Column("intent_summary", sa.Text(), nullable=False),
        sa.Column("target_session_horizon", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("priority", sa.String(20), nullable=False, server_default=sa.text("'medium'")),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        schema=SCHEMA,
    )
    op.create_index("ix_proactive_intents_character_id", "proactive_intents", ["character_id"], schema=SCHEMA)
    op.create_index("ix_proactive_intents_status", "proactive_intents", ["status"], schema=SCHEMA)

    # Tier 8g: Session Health
    op.create_table(
        "session_health",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("dreams_last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("somatic_last_refreshed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("warnings", sa.dialects.postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_index("ix_session_health_session_id", "session_health", ["session_id"], schema=SCHEMA)


def downgrade() -> None:
    """Drop the 7 Dreams tables."""
    op.drop_index("ix_session_health_session_id", "session_health", schema=SCHEMA)
    op.drop_table("session_health", schema=SCHEMA)

    op.drop_index("ix_proactive_intents_status", "proactive_intents", schema=SCHEMA)
    op.drop_index("ix_proactive_intents_character_id", "proactive_intents", schema=SCHEMA)
    op.drop_table("proactive_intents", schema=SCHEMA)

    op.drop_index("ix_drive_states_character_id", "drive_states", schema=SCHEMA)
    op.drop_table("drive_states", schema=SCHEMA)

    op.drop_index("ix_consolidation_character_id", "consolidation_log", schema=SCHEMA)
    op.drop_index("ix_consolidation_run_id", "consolidation_log", schema=SCHEMA)
    op.drop_table("consolidation_log", schema=SCHEMA)

    op.drop_index("ix_consolidated_created_at", "consolidated_memories", schema=SCHEMA)
    op.drop_index("ix_consolidated_character_id", "consolidated_memories", schema=SCHEMA)
    op.drop_table("consolidated_memories", schema=SCHEMA)

    op.drop_index("ix_activities_expires_at", "activities", schema=SCHEMA)
    op.drop_index("ix_activities_character_id", "activities", schema=SCHEMA)
    op.drop_table("activities", schema=SCHEMA)

    op.drop_table("life_states", schema=SCHEMA)
