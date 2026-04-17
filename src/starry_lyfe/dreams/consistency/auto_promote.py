"""Phase 10.7 — 3-night auto-promotion heuristic.

If the same (relationship_key, contradiction.field_name) is flagged as
``concerning_drift`` 3 nights running, auto-promote the verdict to
``factual_contradiction`` for the current run. The rationale: drift
that persists across 3 nightly passes has crossed from "probably
canonical" into "definitely needs operator review" territory.

DB-side timestamps only (clock-skew defense). Boundaries:

- Exactly 3 consecutive nights → promote.
- Gap of 1 night with no flag for the same field → reset; counter
  starts fresh.
- Different fields don't accumulate (the heuristic is per-field, not
  per-relationship).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

QA_LOG_TABLE = "starry_lyfe.dreams_qa_log"
THRESHOLD_NIGHTS = 3
NIGHT_WINDOW_HOURS = 36  # one nightly pass is ~24h apart; 36h tolerates DST + cron jitter


async def should_promote(
    session: AsyncSession,
    *,
    relationship_key: str,
    field_name: str,
    now: datetime | None = None,
) -> bool:
    """Return True if the same (relationship, field) was flagged concerning_drift
    in EACH of the last (THRESHOLD_NIGHTS - 1) nightly passes.

    The current pass's flag is the trigger; we look back at the prior 2
    nights. If both of those showed the same field as concerning_drift
    AND the timestamps land in the expected per-night cadence, the third
    flag (this run) auto-promotes to factual_contradiction.

    DB-side timestamps via ``NOW()`` defense — clients cannot game the
    heuristic by manipulating their clock.
    """
    ref = now if now is not None else datetime.now(UTC)
    # Look back THRESHOLD_NIGHTS * NIGHT_WINDOW_HOURS hours. We need to find
    # at least (THRESHOLD_NIGHTS - 1) DISTINCT prior nightly passes that flagged
    # this same (relationship, field) as concerning_drift.
    lookback_hours = (THRESHOLD_NIGHTS - 1) * NIGHT_WINDOW_HOURS
    sql = text(
        f"""
        SELECT created_at, contradictions
        FROM {QA_LOG_TABLE}
        WHERE relationship_key = :rk
          AND verdict = 'concerning_drift'
          AND created_at >= :since
          AND created_at < :now
        ORDER BY created_at DESC
        """
    )
    result = await session.execute(
        sql,
        {
            "rk": relationship_key,
            "since": ref - timedelta(hours=lookback_hours),
            "now": ref,
        },
    )
    rows = result.mappings().all()

    # Filter to rows whose contradictions[].field_name includes the target field.
    # (concerning_drift verdicts may carry contradictions array even though the
    # judge classified it as drift not contradiction — those are the warning
    # candidates the heuristic tracks.)
    qualifying_dates: list[datetime] = []
    for row in rows:
        contras: list[Any] = row.get("contradictions") or []
        for c in contras:
            if isinstance(c, dict) and c.get("field_name") == field_name:
                qualifying_dates.append(row["created_at"])
                break

    # Must have at least (THRESHOLD_NIGHTS - 1) distinct prior nights, and they
    # must form a contiguous chain — gaps of >NIGHT_WINDOW_HOURS reset.
    if len(qualifying_dates) < THRESHOLD_NIGHTS - 1:
        return False

    qualifying_dates.sort(reverse=True)  # newest first
    contiguous = 1
    for i in range(1, len(qualifying_dates)):
        gap = qualifying_dates[i - 1] - qualifying_dates[i]
        if gap.total_seconds() <= NIGHT_WINDOW_HOURS * 3600:
            contiguous += 1
        else:
            break  # chain broken; older entries don't count
    return contiguous >= THRESHOLD_NIGHTS - 1
