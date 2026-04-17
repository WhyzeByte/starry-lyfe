"""Phase 10.7 unit tests — 3-night auto-promotion heuristic.

Boundary cases:
- Exactly 3 consecutive nights → promote.
- Gap of >36 hours between flags → reset; counter starts fresh.
- Different fields don't accumulate (per-field, not per-relationship).

Tests use an in-memory recorded-call log instead of a real Postgres
session so they stay in tests/unit/ (no DB required).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from starry_lyfe.dreams.consistency.auto_promote import (
    NIGHT_WINDOW_HOURS,
    THRESHOLD_NIGHTS,
    should_promote,
)


class _MockMappings:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows

    def all(self) -> list[dict[str, Any]]:
        return self._rows


class _MockResult:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows

    def mappings(self) -> _MockMappings:
        return _MockMappings(self._rows)


class _MockSession:
    """Minimal AsyncSession stub that returns canned rows for any query."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows
        self.last_params: dict[str, Any] | None = None

    async def execute(self, _sql: Any, params: dict[str, Any] | None = None) -> _MockResult:
        self.last_params = params
        return _MockResult(self._rows)


@pytest.mark.asyncio
async def test_should_promote_returns_false_with_no_history() -> None:
    session = _MockSession(rows=[])
    promoted = await should_promote(
        session,  # type: ignore[arg-type]
        relationship_key="adelia_bina",
        field_name="trust",
    )
    assert promoted is False


@pytest.mark.asyncio
async def test_should_promote_returns_true_at_exactly_threshold_minus_one() -> None:
    """If THRESHOLD_NIGHTS - 1 prior nights all flagged the same field, promote."""
    now = datetime(2026, 4, 17, 3, 0, 0, tzinfo=UTC)
    rows = [
        {
            "created_at": now - timedelta(hours=24),
            "contradictions": [{"field_name": "trust"}],
        },
        {
            "created_at": now - timedelta(hours=48),
            "contradictions": [{"field_name": "trust"}],
        },
    ]
    session = _MockSession(rows=rows)
    promoted = await should_promote(
        session,  # type: ignore[arg-type]
        relationship_key="adelia_bina",
        field_name="trust",
        now=now,
    )
    assert promoted is True


@pytest.mark.asyncio
async def test_should_promote_resets_on_gap_exceeding_window() -> None:
    """A 60-hour gap between qualifying entries breaks the chain."""
    now = datetime(2026, 4, 17, 3, 0, 0, tzinfo=UTC)
    rows = [
        {
            "created_at": now - timedelta(hours=24),
            "contradictions": [{"field_name": "trust"}],
        },
        # 60h gap from the previous one — too far. Chain breaks here.
        {
            "created_at": now - timedelta(hours=60 + 24),
            "contradictions": [{"field_name": "trust"}],
        },
    ]
    session = _MockSession(rows=rows)
    promoted = await should_promote(
        session,  # type: ignore[arg-type]
        relationship_key="adelia_bina",
        field_name="trust",
        now=now,
    )
    # Only 1 contiguous prior night → THRESHOLD_NIGHTS - 1 = 2 not met.
    assert promoted is False


@pytest.mark.asyncio
async def test_should_promote_ignores_unrelated_fields() -> None:
    """Different fields' counters do not accumulate together."""
    now = datetime(2026, 4, 17, 3, 0, 0, tzinfo=UTC)
    rows = [
        {
            "created_at": now - timedelta(hours=24),
            "contradictions": [{"field_name": "intimacy"}],
        },
        {
            "created_at": now - timedelta(hours=48),
            "contradictions": [{"field_name": "intimacy"}],
        },
    ]
    session = _MockSession(rows=rows)
    promoted = await should_promote(
        session,  # type: ignore[arg-type]
        relationship_key="adelia_bina",
        field_name="trust",  # different field — no qualifying rows
        now=now,
    )
    assert promoted is False


def test_threshold_constants_are_sensible() -> None:
    assert THRESHOLD_NIGHTS == 3
    assert NIGHT_WINDOW_HOURS >= 24  # nightly cadence + DST/cron jitter tolerance
