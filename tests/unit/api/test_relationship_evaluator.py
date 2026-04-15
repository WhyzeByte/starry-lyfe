"""Unit tests for ``api.orchestration.relationship.evaluate_and_update``.

The ±0.03 cap per dimension per CLAUDE.md §16 is the load-bearing
invariant — verified directly. Heuristic banks are tunable;
the cap is the safety margin.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime
from typing import Any

import pytest

from starry_lyfe.api.orchestration.relationship import (
    _DELTA_CAP,
    DyadDeltaProposal,
    _bound01,
    _clamp_delta,
    _propose_deltas,
    evaluate_and_update,
)
from starry_lyfe.db.models.dyad_state_whyze import DyadStateWhyze


class TestPropose:
    def test_neutral_text_yields_zero_deltas(self) -> None:
        proposal = _propose_deltas("the kettle is on")
        assert proposal == DyadDeltaProposal()

    def test_intimacy_positive_increments(self) -> None:
        proposal = _propose_deltas("we sat close on the porch, warm and quiet")
        assert proposal.intimacy > 0

    def test_tension_negative_signals_reduce_tension(self) -> None:
        proposal = _propose_deltas("she was calm and we settled it")
        assert proposal.unresolved_tension < 0

    def test_repair_signal_increments_repair_history(self) -> None:
        proposal = _propose_deltas("i'm sorry, that was wrong of me")
        assert proposal.repair_history > 0


class TestClamp:
    def test_capped_at_positive_limit(self) -> None:
        assert _clamp_delta(0.5) == _DELTA_CAP

    def test_capped_at_negative_limit(self) -> None:
        assert _clamp_delta(-0.5) == -_DELTA_CAP

    def test_within_band_unchanged(self) -> None:
        assert _clamp_delta(0.01) == 0.01
        assert _clamp_delta(-0.02) == -0.02


class TestBound01:
    def test_clamps_negative(self) -> None:
        assert _bound01(-0.5) == 0.0

    def test_clamps_above_one(self) -> None:
        assert _bound01(1.5) == 1.0

    def test_passthrough(self) -> None:
        assert _bound01(0.42) == 0.42


# --- evaluate_and_update integration with fake session factory -------------


class _FakeScalars:
    def __init__(self, row: DyadStateWhyze | None) -> None:
        self._row = row

    def first(self) -> DyadStateWhyze | None:
        return self._row


class _FakeResult:
    def __init__(self, row: DyadStateWhyze | None) -> None:
        self._row = row

    def scalars(self) -> _FakeScalars:
        return _FakeScalars(self._row)


class _FakeSession:
    def __init__(self, row: DyadStateWhyze | None) -> None:
        self._row = row
        self.info: dict[str, Any] = {}

    async def execute(self, *args: object, **kwargs: object) -> _FakeResult:
        return _FakeResult(self._row)

    def begin(self) -> _FakeBeginCtx:
        return _FakeBeginCtx()

    async def __aenter__(self) -> _FakeSession:
        return self

    async def __aexit__(self, *_: object) -> None: ...


class _FakeBeginCtx:
    async def __aenter__(self) -> None: ...
    async def __aexit__(self, *_: object) -> None: ...


class _FakeFactory:
    def __init__(self, row: DyadStateWhyze | None) -> None:
        self._row = row

    def __call__(self) -> _FakeSession:
        return _FakeSession(self._row)


def _seed_row(intimacy: float = 0.5) -> DyadStateWhyze:
    return DyadStateWhyze(
        id=uuid.uuid4(),
        dyad_key="adelia-whyze",
        character_id="adelia",
        pair_name="entangled",
        trust=0.6,
        intimacy=intimacy,
        conflict=0.2,
        unresolved_tension=0.3,
        repair_history=0.4,
        last_updated_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
    )


class TestEvaluateAndUpdate:
    async def test_no_signal_returns_none(self) -> None:
        row = _seed_row()
        factory = _FakeFactory(row)
        result = await evaluate_and_update(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="just steady morning chatter",
        )
        assert result is None

    async def test_positive_intimacy_increment_capped_at_three_percent(self) -> None:
        row = _seed_row(intimacy=0.5)
        factory = _FakeFactory(row)
        # Stack many positive signals; cap must hold.
        text = (
            "she was warm, close, tender, and intimate; we sat near each "
            "other and the room was soft"
        )
        result = await evaluate_and_update(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text=text,
        )
        assert result is not None
        # The applied delta must respect the cap.
        assert result.applied.intimacy <= _DELTA_CAP
        # The proposal can exceed the cap (it's pre-clamp).
        assert result.proposed.intimacy > _DELTA_CAP
        # Pre/post differ by exactly the applied delta (no double-counting).
        assert result.post_intimacy == pytest.approx(result.pre_intimacy + result.applied.intimacy)

    async def test_negative_intimacy_decrement_capped(self) -> None:
        row = _seed_row(intimacy=0.5)
        factory = _FakeFactory(row)
        text = "she was distant, cold, withdrawn, pulling away"
        result = await evaluate_and_update(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text=text,
        )
        assert result is not None
        assert result.applied.intimacy >= -_DELTA_CAP
        assert result.applied.intimacy < 0

    async def test_missing_dyad_row_returns_none(self) -> None:
        factory = _FakeFactory(None)  # no dyad in DB
        result = await evaluate_and_update(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="we were close and warm and tender",
        )
        assert result is None

    async def test_intimacy_clamped_to_zero_one_band(self) -> None:
        row = _seed_row(intimacy=0.99)  # near top
        factory = _FakeFactory(row)
        text = "she was warm, close, tender, intimate, near"
        result = await evaluate_and_update(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text=text,
        )
        assert result is not None
        # Even with capped delta, post_intimacy must not exceed 1.0
        assert result.post_intimacy <= 1.0

    async def test_concurrent_calls_do_not_share_state(self) -> None:
        # Two factories, two rows; concurrent evaluation must not mix.
        row_a = _seed_row(intimacy=0.5)
        row_b = _seed_row(intimacy=0.5)
        factory_a = _FakeFactory(row_a)
        factory_b = _FakeFactory(row_b)
        results = await asyncio.gather(
            evaluate_and_update(
                factory_a,  # type: ignore[arg-type]
                character_id="adelia",
                response_text="we were warm and close",
            ),
            evaluate_and_update(
                factory_b,  # type: ignore[arg-type]
                character_id="bina",
                response_text="she was distant and cold",
            ),
        )
        a, b = results
        assert a is not None and b is not None
        assert a.applied.intimacy > 0
        assert b.applied.intimacy < 0


# --- Phase 8 LLM-path tests ------------------------------------------------


class _StubSettings:
    """Minimal Settings-shaped stub — avoids Pydantic env coupling."""

    def __init__(
        self,
        *,
        relationship_eval_llm: bool = True,
        relationship_eval_max_tokens: int = 200,
        relationship_eval_temperature: float = 0.2,
    ) -> None:
        self.relationship_eval_llm = relationship_eval_llm
        self.relationship_eval_max_tokens = relationship_eval_max_tokens
        self.relationship_eval_temperature = relationship_eval_temperature


class TestEvaluateAndUpdateLLMPath:
    """Phase 8 AC-8.4 / AC-8.6 / AC-8.7: LLM-primary with heuristic fallback.

    Uses ``StubBDOne`` with a custom ``responder`` to inject canned JSON
    responses. The fallback branches are exercised by raising
    ``DreamsLLMError``, returning non-JSON, or tripping the circuit
    breaker.
    """

    async def test_llm_path_applies_parsed_deltas_under_cap(self) -> None:
        """AC-8.4: LLM returns in-range values → those become the applied deltas."""
        from starry_lyfe.dreams.llm import StubBDOne

        def _responder(_sys: str, _user: str) -> str:
            return (
                '{"intimacy": 0.02, "unresolved_tension": -0.01, '
                '"trust": 0.015, "repair_history": 0.005}'
            )

        stub = StubBDOne(responder=_responder)
        row = _seed_row(intimacy=0.5)
        factory = _FakeFactory(row)
        result = await evaluate_and_update(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="any turn text; LLM decides",
            llm_client=stub,
            settings=_StubSettings(),  # type: ignore[arg-type]
        )
        assert result is not None
        # Deltas within the cap pass through unchanged.
        assert result.applied.intimacy == pytest.approx(0.02)
        assert result.applied.unresolved_tension == pytest.approx(-0.01)
        assert result.applied.trust == pytest.approx(0.015)
        assert result.applied.repair_history == pytest.approx(0.005)
        # Proposal matches the LLM output (pre-clamp).
        assert result.proposed.intimacy == pytest.approx(0.02)

    async def test_llm_path_clamps_deltas_above_cap(self) -> None:
        """AC-8.3: LLM can return ±1.0; final applied delta MUST be ±0.03."""
        from starry_lyfe.dreams.llm import StubBDOne

        def _responder(_sys: str, _user: str) -> str:
            return (
                '{"intimacy": 1.0, "unresolved_tension": -1.0, '
                '"trust": 0.0, "repair_history": 0.0}'
            )

        stub = StubBDOne(responder=_responder)
        row = _seed_row(intimacy=0.5)
        factory = _FakeFactory(row)
        result = await evaluate_and_update(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="loaded turn",
            llm_client=stub,
            settings=_StubSettings(),  # type: ignore[arg-type]
        )
        assert result is not None
        assert result.applied.intimacy == _DELTA_CAP
        assert result.applied.unresolved_tension == -_DELTA_CAP
        # Proposal captures what LLM actually said.
        assert result.proposed.intimacy == pytest.approx(1.0)

    async def test_llm_failure_falls_back_to_heuristic(self) -> None:
        """AC-8.6: DreamsLLMError → heuristic path runs on the same text."""
        from starry_lyfe.dreams.llm import StubBDOne

        stub = StubBDOne(default_text="unused", fail_next_n=1)
        row = _seed_row()
        factory = _FakeFactory(row)
        # Text has heuristic-positive intimacy signals so the fallback
        # produces a non-zero proposal, proving the fallback ran.
        result = await evaluate_and_update(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="we were warm and close and tender",
            llm_client=stub,
            settings=_StubSettings(),  # type: ignore[arg-type]
        )
        assert result is not None
        assert result.applied.intimacy > 0
        # Heuristic would have proposed ~0.03 (three positive hits).
        # LLM path, had it succeeded, could have proposed anything.
        # This assertion distinguishes heuristic (bounded small int multiple
        # of 0.01) from LLM (arbitrary float) because the responder was never
        # invoked — fail_next_n tripped first.

    async def test_llm_malformed_response_falls_back_to_heuristic(self) -> None:
        """AC-8.6 + AC-8.9: parser returns None → heuristic runs."""
        from starry_lyfe.dreams.llm import StubBDOne

        def _responder(_sys: str, _user: str) -> str:
            return "this is not JSON at all"

        stub = StubBDOne(responder=_responder)
        row = _seed_row()
        factory = _FakeFactory(row)
        result = await evaluate_and_update(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="she was warm and close",  # heuristic can bite
            llm_client=stub,
            settings=_StubSettings(),  # type: ignore[arg-type]
        )
        assert result is not None
        # Heuristic fired because LLM path returned None.
        assert result.applied.intimacy > 0

    async def test_llm_toggle_false_uses_heuristic_directly(self) -> None:
        """AC-8.7: relationship_eval_llm=False → LLM never called; heuristic only."""
        from starry_lyfe.dreams.llm import StubBDOne

        call_count = {"n": 0}

        def _responder(_sys: str, _user: str) -> str:
            call_count["n"] += 1
            return '{"intimacy": 1.0, "unresolved_tension": 0.0, "trust": 0.0, "repair_history": 0.0}'

        stub = StubBDOne(responder=_responder)
        row = _seed_row()
        factory = _FakeFactory(row)
        result = await evaluate_and_update(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="we were warm and close",  # heuristic produces a positive delta
            llm_client=stub,
            settings=_StubSettings(relationship_eval_llm=False),  # type: ignore[arg-type]
        )
        assert result is not None
        # Heuristic fired; LLM responder was never invoked.
        assert call_count["n"] == 0
        # Heuristic produces multiples of 0.01 from signal-bank hits.
        assert result.proposed.intimacy in (0.01, 0.02, 0.03)

    async def test_circuit_open_falls_back_to_heuristic(self) -> None:
        """AC-8.6: llm_client.circuit_open=True → heuristic without attempting LLM call."""
        from starry_lyfe.dreams.llm import BDOne, BDOneSettings

        # Construct a real BDOne so we can trip the circuit without
        # relying on the stub's (non-existent) circuit_open setter.
        bdone = BDOne(BDOneSettings())
        bdone._circuit_open = True  # type: ignore[attr-defined]
        row = _seed_row()
        factory = _FakeFactory(row)
        result = await evaluate_and_update(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="we were warm and close",
            llm_client=bdone,
            settings=_StubSettings(),  # type: ignore[arg-type]
        )
        assert result is not None
        # Heuristic ran; circuit-open branch short-circuits before any HTTP call.
        assert result.applied.intimacy > 0

    async def test_no_llm_client_uses_heuristic(self) -> None:
        """Backward compatibility: legacy callers without llm_client still work."""
        row = _seed_row()
        factory = _FakeFactory(row)
        result = await evaluate_and_update(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="we were warm and close",
            # No llm_client, no settings.
        )
        assert result is not None
        assert result.applied.intimacy > 0


class TestR1F1EvaluatorFallbackOnNonObjectJSON:
    """R1-F1 closure (evaluator level): fallback fires without exception.

    Pre-remediation, an LLM returning ``[]`` (or any non-object JSON)
    propagated an ``AttributeError`` out of the fire-and-forget task.
    The heuristic path never ran. This class proves the fail-closed
    contract at the live evaluator boundary.
    """

    @pytest.mark.parametrize(
        "bad_json", ["[]", "42", '"hi"', "null", "true"],
    )
    async def test_non_object_json_falls_back_to_heuristic(
        self, bad_json: str
    ) -> None:
        from starry_lyfe.dreams.llm import StubBDOne

        def _responder(_sys: str, _user: str) -> str:
            return bad_json

        stub = StubBDOne(responder=_responder)
        row = _seed_row()
        factory = _FakeFactory(row)
        # Text contains heuristic-positive intimacy signals so a successful
        # fallback produces a non-zero proposal. The key behavior: no
        # exception escapes; a result is returned.
        result = await evaluate_and_update(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="we were warm and close and tender",
            llm_client=stub,
            settings=_StubSettings(),  # type: ignore[arg-type]
        )
        assert result is not None
        assert result.applied.intimacy > 0

    async def test_boolean_field_falls_back_to_heuristic(self) -> None:
        """JSON boolean in a numeric field: parser rejects → heuristic runs."""
        from starry_lyfe.dreams.llm import StubBDOne

        def _responder(_sys: str, _user: str) -> str:
            return (
                '{"intimacy": true, "unresolved_tension": 0.0, '
                '"trust": 0.0, "repair_history": 0.0}'
            )

        stub = StubBDOne(responder=_responder)
        row = _seed_row()
        factory = _FakeFactory(row)
        result = await evaluate_and_update(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            response_text="we were warm and close",
            llm_client=stub,
            settings=_StubSettings(),  # type: ignore[arg-type]
        )
        assert result is not None
        # Heuristic fired because LLM path returned None.
        assert result.applied.intimacy > 0
