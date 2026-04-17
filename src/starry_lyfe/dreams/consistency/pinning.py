"""Phase 10.7 — pin/unpin/check-pinned over the ``dyad_state_pins`` table.

Phase 9 evaluator (``api/orchestration/internal_relationship.py::
evaluate_and_update_internal``) consults ``is_pinned()`` before each
``DyadStateInternal`` field write and skips the update if the field
is currently pinned. Pins are created by the Dreams Consistency QA
generator on ``factual_contradiction`` verdicts and resolved by the
operator (CLI or future UI).

The unique partial index on ``(relationship_key, pov_character_id,
field_name) WHERE operator_resolved_at IS NULL`` (created by
``alembic/versions/005_*.py``) guarantees at most one ACTIVE pin per
(relationship, pov, field) triple at any time. Resolved pins remain in
the table as audit history but do not block new writes.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

PINS_TABLE = "starry_lyfe.dyad_state_pins"


async def is_pinned(
    session: AsyncSession,
    *,
    relationship_key: str,
    pov_character_id: str | None,
    field_name: str,
) -> bool:
    """Return True if an ACTIVE pin exists for this (relationship, pov, field).

    NULL ``pov_character_id`` means symmetric pin — match any POV. A
    symmetric pin AND an asymmetric pin for the same field both block.
    """
    # Match symmetric (pov_character_id IS NULL) OR asymmetric (matching POV).
    if pov_character_id is None:
        sql = text(
            f"""
            SELECT 1 FROM {PINS_TABLE}
            WHERE relationship_key = :rk
              AND field_name = :fn
              AND operator_resolved_at IS NULL
            LIMIT 1
            """
        )
        result = await session.execute(sql, {"rk": relationship_key, "fn": field_name})
    else:
        sql = text(
            f"""
            SELECT 1 FROM {PINS_TABLE}
            WHERE relationship_key = :rk
              AND field_name = :fn
              AND (pov_character_id IS NULL OR pov_character_id = :pov)
              AND operator_resolved_at IS NULL
            LIMIT 1
            """
        )
        result = await session.execute(
            sql,
            {"rk": relationship_key, "fn": field_name, "pov": pov_character_id},
        )
    return result.first() is not None


async def pin_field(
    session: AsyncSession,
    *,
    relationship_key: str,
    pov_character_id: str | None,
    field_name: str,
    pinned_value: Any,
    pinned_reason: str,
) -> uuid.UUID:
    """Insert a new ACTIVE pin. ON CONFLICT against the partial unique index → no-op.

    Returns the pin id (or the existing-active-pin's id on conflict).
    The Phase 9 evaluator then sees the pin on its next write attempt.
    """
    new_id = uuid.uuid4()
    sql = text(
        f"""
        INSERT INTO {PINS_TABLE}
            (id, relationship_key, pov_character_id, field_name,
             pinned_value, pinned_reason)
        VALUES (:id, :rk, :pov, :fn, :pv, :pr)
        ON CONFLICT (relationship_key, pov_character_id, field_name)
          WHERE operator_resolved_at IS NULL
          DO NOTHING
        RETURNING id
        """
    )
    import json as _json
    result = await session.execute(
        sql,
        {
            "id": new_id,
            "rk": relationship_key,
            "pov": pov_character_id,
            "fn": field_name,
            "pv": _json.dumps(pinned_value, default=str),
            "pr": pinned_reason,
        },
    )
    row = result.first()
    if row is not None:
        logger.info(
            "dreams_qa_pin_created",
            extra={
                "pin_id": str(row[0]),
                "relationship_key": relationship_key,
                "pov_character_id": pov_character_id,
                "field_name": field_name,
            },
        )
        return row[0]  # type: ignore[no-any-return]
    # Conflict: an active pin already exists. Fetch it.
    fetch = text(
        f"""
        SELECT id FROM {PINS_TABLE}
        WHERE relationship_key = :rk
          AND (pov_character_id IS NOT DISTINCT FROM :pov)
          AND field_name = :fn
          AND operator_resolved_at IS NULL
        """
    )
    existing = await session.execute(
        fetch, {"rk": relationship_key, "pov": pov_character_id, "fn": field_name}
    )
    found = existing.first()
    if found is None:
        msg = (
            f"pin_field upsert race: ON CONFLICT skipped insert but no active pin "
            f"found for ({relationship_key}, {pov_character_id}, {field_name})"
        )
        raise RuntimeError(msg)
    return found[0]  # type: ignore[no-any-return]


async def unpin_field(
    session: AsyncSession,
    *,
    pin_id: uuid.UUID,
    operator_resolution_note: str,
) -> bool:
    """Operator resolution path: stamp ``operator_resolved_at`` on the pin row.

    Returns True if a row was updated, False if the pin was already resolved
    or did not exist.
    """
    sql = text(
        f"""
        UPDATE {PINS_TABLE}
        SET operator_resolved_at = NOW(),
            operator_resolution_note = :note
        WHERE id = :pid
          AND operator_resolved_at IS NULL
        """
    )
    result = await session.execute(sql, {"pid": pin_id, "note": operator_resolution_note})
    rowcount: int = getattr(result, "rowcount", 0) or 0
    return rowcount > 0


async def list_active_pins(session: AsyncSession) -> list[dict[str, Any]]:
    """Return all ACTIVE pins as a list of dicts. Operator CLI / digest input."""
    sql = text(
        f"""
        SELECT id, relationship_key, pov_character_id, field_name,
               pinned_value, pinned_at, pinned_reason
        FROM {PINS_TABLE}
        WHERE operator_resolved_at IS NULL
        ORDER BY pinned_at DESC
        """
    )
    result = await session.execute(sql)
    rows = result.mappings().all()
    return [dict(r) for r in rows]


# Re-export for the Phase 9 evaluator + writers.py.
__all__ = ["is_pinned", "pin_field", "unpin_field", "list_active_pins"]
