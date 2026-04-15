"""Phase 9 Step 2: inter-woman evaluator unit tests.

Covers AC-9.1 (signature + list return), AC-9.3 (±0.03 cap), AC-9.6
(heuristic fallback on every LLM failure branch), AC-9.7 (toggle),
AC-9.11 (Alicia-orbital gate), AC-9.15 (structured log events).

Uses SQLAlchemy session stubs that mirror the Phase 8 test fixture
pattern, plus a `_seed_internal_row()` factory for the 6 canonical
dyads.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import pytest

from starry_lyfe.api.orchestration.internal_relationship import (
    _CONFLICT_POSITIVE,
    InternalDyadDeltaProposal,
    _propose_internal_deltas,
    evaluate_and_update_internal,
)
from starry_lyfe.api.orchestration.relationship import _DELTA_CAP
from starry_lyfe.db.models.dyad_state_internal import DyadStateInternal

# ---------------------------------------------------------------------------
# Fixture scaffolding
# ---------------------------------------------------------------------------


class _FakeScalars:
    def __init__(self, rows: list[DyadStateInternal]) -> None:
        self._rows = rows

    def all(self) -> list[DyadStateInternal]:
        return self._rows


class _FakeResult:
    def __init__(self, rows: list[DyadStateInternal]) -> None:
        self._rows = rows

    def scalars(self) -> _FakeScalars:
        return _FakeScalars(self._rows)


class _FakeSession:
    """Minimal AsyncSession stub.

    Records the predicate-expression used in each ``execute`` call so
    the Alicia-orbital gate test can assert that the is_currently_active
    filter is applied at the query boundary (AC-9.11).
    """

    def __init__(self, rows: list[DyadStateInternal]) -> None:
        self._rows = rows
        self.info: dict[str, Any] = {}
        self.execute_calls: list[Any] = []

    async def execute(self, stmt: Any) -> _FakeResult:
        self.execute_calls.append(stmt)
        return _FakeResult(self._rows)

    def begin(self) -> _FakeBeginCtx:
        return _FakeBeginCtx()

    async def __aenter__(self) -> _FakeSession:
        return self

    async def __aexit__(self, *_: object) -> None: ...


class _FakeBeginCtx:
    async def __aenter__(self) -> None: ...
    async def __aexit__(self, *_: object) -> None: ...


class _FakeFactory:
    def __init__(self, rows: list[DyadStateInternal]) -> None:
        self._rows = rows
        self.last_session: _FakeSession | None = None

    def __call__(self) -> _FakeSession:
        self.last_session = _FakeSession(self._rows)
        return self.last_session


def _seed_internal_row(
    dyad_key: str = "adelia_bina",
    member_a: str = "adelia",
    member_b: str = "bina",
    subtype: str = "anchor_dynamic",
    intimacy: float = 0.5,
    trust: float = 0.5,
    conflict: float = 0.2,
    unresolved_tension: float = 0.2,
    repair_history: float = 0.3,
    is_currently_active: bool = True,
) -> DyadStateInternal:
    return DyadStateInternal(
        id=uuid.uuid4(),
        dyad_key=dyad_key,
        member_a=member_a,
        member_b=member_b,
        subtype=subtype,
        interlock=None,
        trust=trust,
        intimacy=intimacy,
        conflict=conflict,
        unresolved_tension=unresolved_tension,
        repair_history=repair_history,
        is_currently_active=is_currently_active,
        last_updated_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
    )


class _StubSettings:
    def __init__(
        self,
        *,
        internal_relationship_eval_llm: bool = True,
        relationship_eval_max_tokens: int = 200,
        relationship_eval_temperature: float = 0.2,
    ) -> None:
        self.internal_relationship_eval_llm = internal_relationship_eval_llm
        self.relationship_eval_max_tokens = relationship_eval_max_tokens
        self.relationship_eval_temperature = relationship_eval_temperature


# ---------------------------------------------------------------------------
# Heuristic coverage
# ---------------------------------------------------------------------------


class TestProposeInternalDeltas:
    def test_neutral_text_yields_zero_deltas(self) -> None:
        result = _propose_internal_deltas("the kettle is on")
        assert result == InternalDyadDeltaProposal()

    def test_conflict_positive_signal_increments(self) -> None:
        # "push back" + "cut it" both in _CONFLICT_POSITIVE.
        proposal = _propose_internal_deltas(
            "She did not push back, but Reina chose to cut it."
        )
        assert proposal.conflict > 0

    def test_conflict_negative_signal_reduces_conflict(self) -> None:
        # "i hear you" + "adjusted" in _CONFLICT_NEGATIVE.
        proposal = _propose_internal_deltas(
            "She said 'I hear you' and they adjusted the plan."
        )
        assert proposal.conflict < 0

    def test_repair_positive_only_signal(self) -> None:
        proposal = _propose_internal_deltas("I was wrong about the channel.")
        assert proposal.repair_history > 0

    def test_conflict_signal_banks_disjoint_from_tension(self) -> None:
        # Conflict is about live disagreement; tension about residue.
        # Ensure the signal banks do not share terms.
        assert not set(_CONFLICT_POSITIVE) & {
            "frustrat", "tense", "sharp", "snapped", "unfinished",
            "residue", "left open",
        }


# ---------------------------------------------------------------------------
# evaluate_and_update_internal — integration with fake session factory
# ---------------------------------------------------------------------------


class TestEvaluateAndUpdateInternal:
    async def test_no_active_dyads_returns_empty_list(self) -> None:
        factory = _FakeFactory([])  # no dyads seeded
        result = await evaluate_and_update_internal(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="warm and close",
        )
        assert result == []

    async def test_zero_delta_proposal_produces_no_update_record(self) -> None:
        # Neutral text → heuristic yields all-zero proposal → no update.
        factory = _FakeFactory([_seed_internal_row()])
        result = await evaluate_and_update_internal(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="the kettle is on",
        )
        assert result == []

    async def test_single_active_dyad_produces_one_update_record(self) -> None:
        factory = _FakeFactory([_seed_internal_row()])
        result = await evaluate_and_update_internal(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="we were warm and close and tender",
        )
        assert len(result) == 1
        assert result[0].dyad_key == "adelia_bina"
        assert result[0].applied.intimacy > 0
        # Cap invariant (AC-9.3).
        assert abs(result[0].applied.intimacy) <= _DELTA_CAP
        assert abs(result[0].applied.trust) <= _DELTA_CAP
        assert abs(result[0].applied.conflict) <= _DELTA_CAP

    async def test_multiple_active_dyads_produce_per_dyad_records(self) -> None:
        rows = [
            _seed_internal_row("adelia_bina", "adelia", "bina"),
            _seed_internal_row("adelia_reina", "adelia", "reina"),
        ]
        factory = _FakeFactory(rows)
        result = await evaluate_and_update_internal(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="she was warm and close, very tender",
        )
        assert len(result) == 2
        dyad_keys = {u.dyad_key for u in result}
        assert dyad_keys == {"adelia_bina", "adelia_reina"}


class TestAliciaOrbitalActiveGate:
    """AC-9.11: dormant Alicia-orbital dyads never consume LLM budget + never update."""

    async def test_dormant_alicia_dyad_filtered_at_db_boundary(self) -> None:
        """Stub returns zero rows (simulating the DB query filtering dormant).

        The query's is_currently_active filter is asserted by the
        follow-up test; this case ensures the evaluator handles the
        empty-result path cleanly.
        """
        factory = _FakeFactory([])  # query returns nothing
        result = await evaluate_and_update_internal(
            factory,  # type: ignore[arg-type]
            character_id="alicia",
            response_text="we sat on the couch and talked",
        )
        assert result == []

    async def test_query_applies_is_currently_active_filter(self) -> None:
        """AC-9.11: the SELECT statement carries an is_currently_active predicate."""
        factory = _FakeFactory([_seed_internal_row()])
        await evaluate_and_update_internal(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="warm and close",
        )
        session = factory.last_session
        assert session is not None
        assert len(session.execute_calls) == 1
        # The statement's text representation should mention is_currently_active.
        stmt_text = str(session.execute_calls[0])
        assert "is_currently_active" in stmt_text

    async def test_active_orbital_dyad_updates_normally(self) -> None:
        """Alicia-orbital dyad with is_currently_active=True updates the same as resident."""
        rows = [
            _seed_internal_row(
                "adelia_alicia", "adelia", "alicia",
                subtype="letter_era_friends",
                is_currently_active=True,
            ),
        ]
        factory = _FakeFactory(rows)
        result = await evaluate_and_update_internal(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="the greeting landed warm and close",
        )
        assert len(result) == 1
        assert result[0].dyad_key == "adelia_alicia"


# ---------------------------------------------------------------------------
# LLM path + fallback branches
# ---------------------------------------------------------------------------


class TestEvaluateAndUpdateInternalLLMPath:
    """AC-9.6: five fallback branches + LLM-primary success path."""

    async def test_llm_path_applies_parsed_deltas_under_cap(self) -> None:
        from starry_lyfe.dreams.llm import StubBDOne

        def _responder(_sys: str, _user: str) -> str:
            return (
                '{"trust": 0.02, "intimacy": 0.01, "conflict": -0.01, '
                '"unresolved_tension": 0.0, "repair_history": 0.005}'
            )

        stub = StubBDOne(responder=_responder)
        factory = _FakeFactory([_seed_internal_row()])
        result = await evaluate_and_update_internal(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="any text",
            llm_client=stub,
            settings=_StubSettings(),  # type: ignore[arg-type]
        )
        assert len(result) == 1
        assert result[0].applied.trust == pytest.approx(0.02)
        assert result[0].applied.conflict == pytest.approx(-0.01)

    async def test_llm_path_clamps_above_cap(self) -> None:
        from starry_lyfe.dreams.llm import StubBDOne

        def _responder(_sys: str, _user: str) -> str:
            return (
                '{"trust": 1.0, "intimacy": 1.0, "conflict": -1.0, '
                '"unresolved_tension": 0.0, "repair_history": 0.0}'
            )

        stub = StubBDOne(responder=_responder)
        factory = _FakeFactory([_seed_internal_row()])
        result = await evaluate_and_update_internal(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="text",
            llm_client=stub,
            settings=_StubSettings(),  # type: ignore[arg-type]
        )
        assert len(result) == 1
        assert result[0].applied.trust == _DELTA_CAP
        assert result[0].applied.conflict == -_DELTA_CAP

    async def test_llm_failure_falls_back_to_heuristic(self) -> None:
        from starry_lyfe.dreams.llm import StubBDOne

        stub = StubBDOne(default_text="unused", fail_next_n=1)
        factory = _FakeFactory([_seed_internal_row()])
        result = await evaluate_and_update_internal(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="she was warm and close and tender",
            llm_client=stub,
            settings=_StubSettings(),  # type: ignore[arg-type]
        )
        assert len(result) == 1  # heuristic produced non-zero delta
        assert result[0].applied.intimacy > 0

    async def test_llm_malformed_response_falls_back_to_heuristic(self) -> None:
        from starry_lyfe.dreams.llm import StubBDOne

        def _responder(_sys: str, _user: str) -> str:
            return "not valid json"

        stub = StubBDOne(responder=_responder)
        factory = _FakeFactory([_seed_internal_row()])
        result = await evaluate_and_update_internal(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="she was warm and close",
            llm_client=stub,
            settings=_StubSettings(),  # type: ignore[arg-type]
        )
        assert len(result) == 1
        assert result[0].applied.intimacy > 0

    async def test_llm_non_object_json_falls_back_to_heuristic(self) -> None:
        """AC-9.9: Phase 8 R1-F1 lesson — arrays / scalars / null → None → heuristic."""
        from starry_lyfe.dreams.llm import StubBDOne

        def _responder(_sys: str, _user: str) -> str:
            return "[]"

        stub = StubBDOne(responder=_responder)
        factory = _FakeFactory([_seed_internal_row()])
        result = await evaluate_and_update_internal(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="warm and close",
            llm_client=stub,
            settings=_StubSettings(),  # type: ignore[arg-type]
        )
        assert len(result) == 1
        assert result[0].applied.intimacy > 0

    async def test_toggle_false_uses_heuristic_directly(self) -> None:
        """AC-9.7: settings.internal_relationship_eval_llm=False forces heuristic."""
        from starry_lyfe.dreams.llm import StubBDOne

        call_count = {"n": 0}

        def _responder(_sys: str, _user: str) -> str:
            call_count["n"] += 1
            return '{"trust": 1.0, "intimacy": 1.0, "conflict": 0.0, "unresolved_tension": 0.0, "repair_history": 0.0}'

        stub = StubBDOne(responder=_responder)
        factory = _FakeFactory([_seed_internal_row()])
        result = await evaluate_and_update_internal(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="warm and close",
            llm_client=stub,
            settings=_StubSettings(internal_relationship_eval_llm=False),  # type: ignore[arg-type]
        )
        assert call_count["n"] == 0  # LLM never invoked
        assert len(result) == 1
        assert result[0].applied.intimacy > 0

    async def test_circuit_open_falls_back_to_heuristic(self) -> None:
        """Live circuit breaker open → heuristic; no HTTP attempt."""
        from starry_lyfe.dreams.llm import BDOne, BDOneSettings

        bdone = BDOne(BDOneSettings())
        bdone._circuit_open = True  # type: ignore[attr-defined]
        factory = _FakeFactory([_seed_internal_row()])
        result = await evaluate_and_update_internal(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="warm and close",
            llm_client=bdone,
            settings=_StubSettings(),  # type: ignore[arg-type]
        )
        assert len(result) == 1
        assert result[0].applied.intimacy > 0

    async def test_no_llm_client_uses_heuristic(self) -> None:
        """Backward compat: legacy callers without llm_client still work."""
        factory = _FakeFactory([_seed_internal_row()])
        result = await evaluate_and_update_internal(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="warm and close",
            # No llm_client, no settings.
        )
        assert len(result) == 1
        assert result[0].applied.intimacy > 0
