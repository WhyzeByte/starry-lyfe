"""Unit tests for Phase 6 Dreams consolidation helpers (Subsystem F).

DB interactions (select/update) are exercised by the commit-8 integration
tests against a live Postgres; the unit tests here focus on the pure
clamping/delta logic and the dataclass contracts.
"""

from __future__ import annotations

import types

import pytest

from starry_lyfe.dreams.consolidation import (
    _DYAD_DELTA_CAP,
    DyadDelta,
    DyadDeltaApplication,
    SomaticRefreshResult,
    _apply_single_delta,
)


class TestDyadDeltaDataclass:
    def test_construct(self) -> None:
        d = DyadDelta(dimension="trust", delta=0.05)
        assert d.dimension == "trust"
        assert d.delta == 0.05

    def test_frozen(self) -> None:
        d = DyadDelta(dimension="trust", delta=0.05)
        with pytest.raises((AttributeError, Exception)):
            d.delta = 0.1  # type: ignore[misc]


class TestSomaticRefreshResult:
    def test_empty_when_no_row(self) -> None:
        r = SomaticRefreshResult(
            character_id="adelia",
            applied=False,
            elapsed_hours=0.0,
            before={},
            after={},
        )
        assert r.applied is False


class TestApplySingleDelta:
    """Covers AC-13: dyad deltas capped at ±_DYAD_DELTA_CAP per dimension."""

    def _make_row(self, **kwargs: float) -> types.SimpleNamespace:
        """SimpleNamespace mimics SQLAlchemy row shape for setattr/getattr."""
        defaults = {
            "trust": 0.5,
            "intimacy": 0.5,
            "conflict": 0.0,
            "unresolved_tension": 0.0,
            "repair_history": 0.5,
        }
        defaults.update(kwargs)
        return types.SimpleNamespace(**defaults)

    def test_delta_within_cap_applied_verbatim(self) -> None:
        row = self._make_row(trust=0.5)
        app = _apply_single_delta(row, "trust", 0.05)
        assert app.applied == 0.05
        assert not app.clamped
        assert row.trust == 0.55

    def test_positive_delta_exceeding_cap_is_clamped(self) -> None:
        row = self._make_row(trust=0.5)
        app = _apply_single_delta(row, "trust", 0.30)  # way over 0.10 cap
        assert app.applied == _DYAD_DELTA_CAP
        assert app.clamped
        assert row.trust == pytest.approx(0.5 + _DYAD_DELTA_CAP)

    def test_negative_delta_exceeding_cap_is_clamped(self) -> None:
        row = self._make_row(intimacy=0.5)
        app = _apply_single_delta(row, "intimacy", -0.25)
        assert app.applied == -_DYAD_DELTA_CAP
        assert app.clamped
        assert row.intimacy == pytest.approx(0.5 - _DYAD_DELTA_CAP)

    def test_result_value_clamped_to_zero_one_range(self) -> None:
        """Applied delta + original value is clamped to [0.0, 1.0]."""
        row = self._make_row(trust=0.95)
        app = _apply_single_delta(row, "trust", 0.5)  # would push above 1.0
        assert row.trust == 1.0
        assert app.after == 1.0

    def test_result_value_clamped_to_zero_floor(self) -> None:
        row = self._make_row(trust=0.05)
        app = _apply_single_delta(row, "trust", -0.5)  # would push below 0.0
        assert row.trust == 0.0
        assert app.after == 0.0

    def test_unknown_dimension_returns_zero_application(self) -> None:
        row = self._make_row()
        app = _apply_single_delta(row, "not_a_real_dim", 0.05)
        assert app.applied == 0.0
        assert app.before == 0.0
        assert app.after == 0.0

    def test_boundary_exactly_at_cap_is_not_clamped(self) -> None:
        """Delta exactly at the cap should not flag clamped=True."""
        row = self._make_row(trust=0.5)
        app = _apply_single_delta(row, "trust", _DYAD_DELTA_CAP)
        assert app.applied == _DYAD_DELTA_CAP
        assert not app.clamped

    def test_application_bookkeeping_fields(self) -> None:
        row = self._make_row(trust=0.60)
        app = _apply_single_delta(row, "trust", 0.15)
        assert app.requested == 0.15
        assert app.applied == _DYAD_DELTA_CAP  # clamped to 0.10
        assert app.before == 0.60
        assert app.after == 0.70
        assert app.clamped


class TestDyadDeltaApplicationShape:
    def test_fields_present(self) -> None:
        app = DyadDeltaApplication(
            dimension="trust",
            requested=0.15,
            applied=0.10,
            clamped=True,
            before=0.5,
            after=0.6,
        )
        assert app.dimension == "trust"
        assert app.clamped is True
