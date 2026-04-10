"""Create the seven-tier memory schema.

Revision ID: 001
Revises:
Create Date: 2026-04-10
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "001"
down_revision: str | None = None
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None

SCHEMA = "starry_lyfe"


def upgrade() -> None:
    """Create all memory tier tables."""
    # Extensions and schema
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")

    # Tier 1: Canon Facts
    op.create_table(
        "canon_facts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_key", sa.String(100), nullable=False),
        sa.Column("fact_key", sa.String(200), nullable=False),
        sa.Column("fact_value", sa.Text(), nullable=False),
        sa.Column("canon_version", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("entity_type", "entity_key", "fact_key", name="uq_canon_fact_entity_fact"),
        schema=SCHEMA,
    )

    # Tier 2: Character Baselines
    op.create_table(
        "character_baselines",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("character_id", sa.String(20), nullable=False, unique=True),
        sa.Column("full_name", sa.String(100), nullable=False),
        sa.Column("epithet", sa.String(100), nullable=False),
        sa.Column("mbti", sa.String(10), nullable=False),
        sa.Column("cognitive_stack", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("dominant_function", sa.String(5), nullable=False),
        sa.Column("voice_params", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("pair_name", sa.String(50), nullable=False),
        sa.Column("pair_classification", sa.String(100), nullable=False),
        sa.Column("pair_mechanism", sa.Text(), nullable=False),
        sa.Column("pair_core_metaphor", sa.String(200), nullable=False),
        sa.Column("heritage", sa.String(200), nullable=False),
        sa.Column("profession", sa.String(200), nullable=False),
        sa.Column("is_resident", sa.Boolean(), nullable=False),
        sa.Column("operational_travel", sa.Text(), nullable=True),
        sa.Column("canon_version", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )

    # Tier 3: Dyad State (Whyze)
    op.create_table(
        "dyad_state_whyze",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("dyad_key", sa.String(50), nullable=False, unique=True),
        sa.Column("character_id", sa.String(20), nullable=False),
        sa.Column("pair_name", sa.String(50), nullable=False),
        sa.Column("trust", sa.Float(), nullable=False),
        sa.Column("intimacy", sa.Float(), nullable=False),
        sa.Column("conflict", sa.Float(), nullable=False),
        sa.Column("unresolved_tension", sa.Float(), nullable=False),
        sa.Column("repair_history", sa.Float(), nullable=False),
        sa.Column("last_updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )

    # Tier 4: Dyad State (Internal)
    op.create_table(
        "dyad_state_internal",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("dyad_key", sa.String(50), nullable=False, unique=True),
        sa.Column("member_a", sa.String(20), nullable=False),
        sa.Column("member_b", sa.String(20), nullable=False),
        sa.Column("subtype", sa.String(30), nullable=False),
        sa.Column("interlock", sa.String(50), nullable=True),
        sa.Column("trust", sa.Float(), nullable=False),
        sa.Column("intimacy", sa.Float(), nullable=False),
        sa.Column("conflict", sa.Float(), nullable=False),
        sa.Column("unresolved_tension", sa.Float(), nullable=False),
        sa.Column("repair_history", sa.Float(), nullable=False),
        sa.Column("is_currently_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )

    # Tier 5: Episodic Memories
    op.create_table(
        "episodic_memories",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("session_id", sa.Uuid(), nullable=True),
        sa.Column("character_id", sa.String(20), nullable=False),
        sa.Column("participant_ids", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("event_summary", sa.Text(), nullable=False),
        sa.Column("emotional_temperature", sa.Float(), nullable=True),
        sa.Column("memory_type", sa.String(50), nullable=False),
        sa.Column("importance_score", sa.Float(), nullable=False, server_default=sa.text("0.5")),
        sa.Column("embedding", Vector(768), nullable=False),
        sa.Column("metadata", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("decayed_at", sa.DateTime(timezone=True), nullable=True),
        schema=SCHEMA,
    )

    # Episodic memory indexes
    op.create_index("ix_episodic_character_id", "episodic_memories", ["character_id"], schema=SCHEMA)
    op.create_index("ix_episodic_created_at", "episodic_memories", ["created_at"], schema=SCHEMA)
    op.create_index(
        "ix_episodic_participant_ids",
        "episodic_memories",
        ["participant_ids"],
        schema=SCHEMA,
        postgresql_using="gin",
    )
    op.execute(
        f"CREATE INDEX ix_episodic_embedding ON {SCHEMA}.episodic_memories "
        "USING hnsw (embedding vector_cosine_ops)"
    )

    # Tier 6: Open Loops
    op.create_table(
        "open_loops",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("character_id", sa.String(20), nullable=False),
        sa.Column("loop_summary", sa.Text(), nullable=False),
        sa.Column("loop_type", sa.String(50), nullable=False),
        sa.Column("urgency", sa.String(20), nullable=False, server_default=sa.text("'medium'")),
        sa.Column("best_next_speaker", sa.String(20), nullable=True),
        sa.Column("suggested_scene", sa.Text(), nullable=True),
        sa.Column("source_session_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'open'")),
        sa.Column("resolved_by", sa.String(50), nullable=True),
        sa.Column("ttl_hours", sa.Integer(), nullable=False, server_default=sa.text("168")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        schema=SCHEMA,
    )
    op.create_index("ix_open_loops_character_status", "open_loops", ["character_id", "status"], schema=SCHEMA)

    # Tier 7: Transient Somatic States
    op.create_table(
        "transient_somatic_states",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("character_id", sa.String(20), nullable=False, unique=True),
        sa.Column("fatigue", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("stress_residue", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("injury_residue", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("active_protocols", sa.dialects.postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("protocol_metadata", sa.dialects.postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("custom_fields", sa.dialects.postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("decay_config", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("last_decayed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )


def downgrade() -> None:
    """Drop all memory tier tables."""
    op.drop_table("transient_somatic_states", schema=SCHEMA)
    op.drop_table("open_loops", schema=SCHEMA)
    op.execute(f"DROP INDEX IF EXISTS {SCHEMA}.ix_episodic_embedding")
    op.drop_table("episodic_memories", schema=SCHEMA)
    op.drop_table("dyad_state_internal", schema=SCHEMA)
    op.drop_table("dyad_state_whyze", schema=SCHEMA)
    op.drop_table("character_baselines", schema=SCHEMA)
    op.drop_table("canon_facts", schema=SCHEMA)
    op.execute(f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE")
