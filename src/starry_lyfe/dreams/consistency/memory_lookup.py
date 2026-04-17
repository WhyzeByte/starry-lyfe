"""Phase 10.7 — per-relationship episodic memory lookup (last 7 days).

Helper kept separate from ``runner.py::default_snapshot_loader`` (which
loads the last 24h of memories per character for the per-character
generators). The QA judge needs a 7-day window AND filtered to the
specific pair of characters in the relationship under review.

Centralizing the query here keeps the hot-path snapshot loader narrow
(no broadening) and keeps the QA-specific filter logic discoverable.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

EPISODIC_TABLE = "starry_lyfe.episodic_memories"


async def load_relationship_memories(
    session: AsyncSession,
    *,
    pov_a: str,
    pov_b: str,
    days: int = 7,
    now: datetime | None = None,
    limit: int = 40,
) -> list[str]:
    """Return episodic memory text excerpts where BOTH POVs appear.

    Inclusive: any episodic memory whose ``character_id`` is one of the
    POVs AND whose ``content`` mentions the other POV (case-insensitive
    substring match) qualifies. Results sorted newest-first, capped at
    ``limit`` to bound prompt size.

    The judge prompt builder runs each result through
    ``prompt._sanitize_for_evidence_block`` — this helper returns raw text.
    """
    ref = now if now is not None else datetime.now(UTC)
    since = ref - timedelta(days=days)

    sql = text(
        f"""
        SELECT character_id, content, created_at
        FROM {EPISODIC_TABLE}
        WHERE character_id IN (:pov_a, :pov_b)
          AND created_at >= :since
          AND created_at < :now
          AND (
            (character_id = :pov_a AND lower(content) LIKE lower(:b_pat))
            OR
            (character_id = :pov_b AND lower(content) LIKE lower(:a_pat))
          )
        ORDER BY created_at DESC
        LIMIT :limit_n
        """
    )
    result = await session.execute(
        sql,
        {
            "pov_a": pov_a,
            "pov_b": pov_b,
            "since": since,
            "now": ref,
            "a_pat": f"%{pov_a}%",
            "b_pat": f"%{pov_b}%",
            "limit_n": limit,
        },
    )
    rows = result.mappings().all()
    excerpts: list[str] = []
    for row in rows:
        ts = row["created_at"].strftime("%Y-%m-%d") if row["created_at"] else "?"
        excerpts.append(f"[{ts} {row['character_id']}] {row['content']}")
    return excerpts


# For woman_whyze pairs: ``pov_b`` is "whyze" but episodic memories are
# stored against the woman's character_id (Whyze doesn't have his own
# memories table). Special-case caller passes pov_a=woman, pov_b="whyze";
# we return memories where character_id=woman AND content mentions "whyze".
async def load_woman_whyze_memories(
    session: AsyncSession,
    *,
    woman_id: str,
    days: int = 7,
    now: datetime | None = None,
    limit: int = 40,
) -> list[str]:
    """Last-7-days memories where the woman mentions Whyze."""
    ref = now if now is not None else datetime.now(UTC)
    since = ref - timedelta(days=days)
    sql = text(
        f"""
        SELECT character_id, content, created_at
        FROM {EPISODIC_TABLE}
        WHERE character_id = :woman
          AND created_at >= :since
          AND created_at < :now
          AND lower(content) LIKE '%whyze%'
        ORDER BY created_at DESC
        LIMIT :limit_n
        """
    )
    result = await session.execute(
        sql,
        {"woman": woman_id, "since": since, "now": ref, "limit_n": limit},
    )
    rows = result.mappings().all()
    excerpts: list[str] = []
    for row in rows:
        ts = row["created_at"].strftime("%Y-%m-%d") if row["created_at"] else "?"
        excerpts.append(f"[{ts} {row['character_id']}] {row['content']}")
    return excerpts


__all__ = ["load_relationship_memories", "load_woman_whyze_memories"]
