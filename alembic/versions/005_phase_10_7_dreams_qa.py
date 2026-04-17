"""Phase 10.7 — Dreams Consistency QA tables.

Revision ID: 005
Revises: 004
Create Date: 2026-04-17

Creates two tables that back the nightly Dreams Consistency QA pass:

- ``dreams_qa_log`` — append-only verdict history. One row per
  (run, relationship) per nightly pass. Feeds the 3-night
  auto-promotion heuristic and the weekly digest.
- ``dyad_state_pins`` — last-coherent snapshots of fields the QA
  judge flagged as ``factual_contradiction``. Phase 9 evaluator
  consults this before each ``DyadStateInternal`` write and refuses
  to update pinned fields until the operator resolves.

Per ``Docs/_phases/PHASE_10.md`` §Phase 10.7 + AC-10.24..AC-10.28
(spec) + plan-phase-10-5c-zany-cherny.md (executed plan, retains
prior slug per plan-mode rule).
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "005"
down_revision: str | None = "004"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None

SCHEMA = "starry_lyfe"


def upgrade() -> None:
    # --- dreams_qa_log ------------------------------------------------------
    op.create_table(
        "dreams_qa_log",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("run_id", UUID(as_uuid=True), nullable=False),
        sa.Column("relationship_key", sa.String(64), nullable=False),
        sa.Column("verdict", sa.String(32), nullable=False),
        sa.Column("divergence_summary", sa.Text, nullable=False, server_default=""),
        sa.Column(
            "contradictions",
            JSONB,
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "scene_fodder",
            JSONB,
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "verdict IN ('healthy_divergence', 'concerning_drift', 'factual_contradiction')",
            name="ck_dreams_qa_log_verdict",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_dreams_qa_log_run_id",
        "dreams_qa_log",
        ["run_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_dreams_qa_log_relationship_created",
        "dreams_qa_log",
        ["relationship_key", "created_at"],
        schema=SCHEMA,
    )

    # --- dyad_state_pins ----------------------------------------------------
    op.create_table(
        "dyad_state_pins",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("relationship_key", sa.String(64), nullable=False),
        sa.Column(
            "pov_character_id",
            sa.String(20),
            nullable=True,
            comment="NULL = symmetric pin; set = asymmetric per-POV pin",
        ),
        sa.Column("field_name", sa.String(64), nullable=False),
        sa.Column("pinned_value", JSONB, nullable=False),
        sa.Column(
            "pinned_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("pinned_reason", sa.Text, nullable=False, server_default=""),
        sa.Column(
            "operator_resolved_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("operator_resolution_note", sa.Text, nullable=True),
        schema=SCHEMA,
    )
    # Unique partial index: one ACTIVE pin per (relationship, pov, field).
    # Resolved pins (operator_resolved_at IS NOT NULL) don't block new pins.
    op.create_index(
        "uq_dyad_state_pins_active",
        "dyad_state_pins",
        ["relationship_key", "pov_character_id", "field_name"],
        unique=True,
        postgresql_where=sa.text("operator_resolved_at IS NULL"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_dyad_state_pins_relationship",
        "dyad_state_pins",
        ["relationship_key"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_dyad_state_pins_relationship",
        table_name="dyad_state_pins",
        schema=SCHEMA,
    )
    op.drop_index(
        "uq_dyad_state_pins_active",
        table_name="dyad_state_pins",
        schema=SCHEMA,
    )
    op.drop_table("dyad_state_pins", schema=SCHEMA)

    op.drop_index(
        "ix_dreams_qa_log_relationship_created",
        table_name="dreams_qa_log",
        schema=SCHEMA,
    )
    op.drop_index("ix_dreams_qa_log_run_id", table_name="dreams_qa_log", schema=SCHEMA)
    op.drop_table("dreams_qa_log", schema=SCHEMA)
