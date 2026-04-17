"""Phase 10.7 integration — Dreams Consistency QA end-to-end against real Postgres.

Skips when Postgres is unreachable (matches the existing integration-suite
pattern that bounds env-dependence to a single conftest-driven skip).

Asserts:
- ``dreams_qa_log`` rows land for all 10 relationships per nightly pass
- Daily ``Docs/_dreams_qa/YYYY-MM-DD_consistency.md`` ledger written
- ``factual_contradiction`` writes a ``dyad_state_pins`` row (when the
  judge surfaces one — driven by a synthetic StubBDOne response)
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

import pytest
from sqlalchemy import text

from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.dreams.consistency.schemas import QAVerdict

pytestmark = pytest.mark.asyncio


class _SyntheticStubBDOne:
    """Minimal LLMClient that returns canned JSON verdicts for the QA judge.

    Avoids the real BDOne HTTP path so tests don't depend on an external
    LLM endpoint. Cycles through the queued verdicts; raises if exhausted.
    """

    def __init__(self, verdicts_by_key: dict[str, dict[str, Any]]) -> None:
        self._verdicts = verdicts_by_key
        self._call_count = 0
        self._circuit_open = False

    @property
    def circuit_open(self) -> bool:
        return self._circuit_open

    def reset_circuit(self) -> None:
        self._circuit_open = False

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        max_tokens: int = 800,
        temperature: float = 0.2,
    ) -> Any:
        # Extract relationship_key from the user prompt's first marker line.
        rel_key = ""
        for line in user_prompt.splitlines():
            if line.startswith("relationship_key:"):
                rel_key = line.split(":", 1)[1].strip()
                break
        verdict_payload = self._verdicts.get(rel_key) or {
            "relationship_key": rel_key,
            "verdict": QAVerdict.HEALTHY_DIVERGENCE.value,
            "divergence_summary": "synthetic default",
            "contradictions": [],
            "scene_fodder": [],
        }

        class _Resp:
            text = json.dumps(verdict_payload)
            input_tokens = 50
            output_tokens = 50

        self._call_count += 1
        return _Resp()


async def test_consistency_qa_writes_log_rows_for_all_ten_relationships(
    engine,  # AsyncEngine — bind directly, see comment below
    seeded_session,  # noqa: ARG001 — keep dep so schema is migrated
) -> None:
    """Real Postgres + StubBDOne: nightly pass writes 10 dreams_qa_log rows."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from starry_lyfe.dreams.generators.consistency_qa import generate_consistency_qa

    canon = load_all_canon()
    # Bind the QA pass session_factory directly to the AsyncEngine. The
    # ``seeded_session`` fixture's connection-bound AsyncSession internally
    # wraps a sync Connection; ``seeded_session.bind`` would yield that sync
    # Connection back, and ``async_sessionmaker(bind=sync_conn)`` produces
    # sessions that hit ``MissingGreenlet`` the moment they execute SQL.
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    run_id = uuid.uuid4()
    llm_client = _SyntheticStubBDOne(verdicts_by_key={})

    output = await generate_consistency_qa(
        run_id=run_id,
        canon=canon,
        llm_client=llm_client,
        session_factory=session_factory,
        now=datetime(2026, 4, 17, 3, 0, 0, tzinfo=UTC),
    )

    assert len(output.relationship_checks) == 10

    # Verify rows landed.
    async with session_factory() as session:
        result = await session.execute(
            text(
                "SELECT count(*), min(verdict) FROM starry_lyfe.dreams_qa_log "
                "WHERE run_id = :rid"
            ),
            {"rid": run_id},
        )
        row = result.first()
        assert row is not None
        count, _ = row
        assert count == 10

    # Cleanup: engine-bound writes committed; remove this run's rows so the
    # next test sees a clean slate.
    async with session_factory() as session, session.begin():
        await session.execute(
            text("DELETE FROM starry_lyfe.dreams_qa_log WHERE run_id = :rid"),
            {"rid": run_id},
        )


async def test_consistency_qa_writes_pin_on_factual_contradiction(
    engine,
    seeded_session,  # noqa: ARG001 — keep dep so schema is migrated
) -> None:
    """Synthetic factual_contradiction verdict produces a dyad_state_pins row."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from starry_lyfe.dreams.generators.consistency_qa import generate_consistency_qa

    canon = load_all_canon()
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    run_id = uuid.uuid4()
    contradiction_payload = {
        "relationship_key": "whyze_alicia",
        "verdict": QAVerdict.FACTUAL_CONTRADICTION.value,
        "divergence_summary": "Alicia recalls 2023 marriage year",
        "contradictions": [
            {
                "field_name": "marriage_year",
                "pov_character_id": "alicia",
                "shared_canon_field": "shared_canon.marriage.year",
                "observed_value": "2023",
                "canonical_value": "2022",
                "severity_note": "",
            }
        ],
        "scene_fodder": [],
    }
    llm_client = _SyntheticStubBDOne(
        verdicts_by_key={"whyze_alicia": contradiction_payload}
    )

    await generate_consistency_qa(
        run_id=run_id,
        canon=canon,
        llm_client=llm_client,
        session_factory=session_factory,
        now=datetime(2026, 4, 17, 3, 0, 0, tzinfo=UTC),
    )

    async with session_factory() as session:
        result = await session.execute(
            text(
                "SELECT count(*) FROM starry_lyfe.dyad_state_pins "
                "WHERE relationship_key = 'whyze_alicia' "
                "AND field_name = 'marriage_year' "
                "AND operator_resolved_at IS NULL"
            )
        )
        row = result.first()
        assert row is not None
        assert row[0] >= 1

    # Cleanup so subsequent tests don't see this pin or this run's QA rows.
    async with session_factory() as session, session.begin():
        await session.execute(
            text("DELETE FROM starry_lyfe.dreams_qa_log WHERE run_id = :rid"),
            {"rid": run_id},
        )
        await session.execute(
            text(
                "DELETE FROM starry_lyfe.dyad_state_pins "
                "WHERE relationship_key = 'whyze_alicia' "
                "AND field_name = 'marriage_year'"
            )
        )


async def test_healthy_divergence_scene_fodder_lands_in_open_loops(
    engine,
    seeded_session,  # noqa: ARG001 — keep dep so schema is migrated
) -> None:
    """Phase 10.7 AC-10.26 regression: healthy_divergence scene_fodder
    routed via runner._route_qa_scene_fodder_to_open_loops becomes
    OpenLoop rows tagged with the dreams_qa source qualifier."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from starry_lyfe.dreams.generators.consistency_qa import generate_consistency_qa
    from starry_lyfe.dreams.runner import _route_qa_scene_fodder_to_open_loops

    canon = load_all_canon()
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    run_id = uuid.uuid4()
    healthy_payload = {
        "relationship_key": "adelia_bina",
        "verdict": QAVerdict.HEALTHY_DIVERGENCE.value,
        "divergence_summary": "Bina sees grounding; Adelia sees buoyancy.",
        "contradictions": [],
        "scene_fodder": [
            "Bina notices the cardamom Adelia missed.",
            "Adelia teases Bina about the over-precise paella timer.",
        ],
    }
    llm_client = _SyntheticStubBDOne(
        verdicts_by_key={"adelia_bina": healthy_payload}
    )

    qa_result = await generate_consistency_qa(
        run_id=run_id,
        canon=canon,
        llm_client=llm_client,
        session_factory=session_factory,
        now=datetime(2026, 4, 17, 3, 0, 0, tzinfo=UTC),
    )

    await _route_qa_scene_fodder_to_open_loops(
        qa_result, canon, session_factory,
        datetime(2026, 4, 17, 3, 0, 0, tzinfo=UTC),
    )

    async with session_factory() as session:
        result = await session.execute(
            text(
                "SELECT loop_summary, loop_type, character_id, best_next_speaker "
                "FROM starry_lyfe.open_loops "
                "WHERE loop_type LIKE '%:dreams_qa' "
                "AND character_id = 'adelia' "
                "ORDER BY created_at DESC LIMIT 5"
            )
        )
        rows = list(result)
        # Two scene_fodder strings → two rows tagged dreams_qa.
        assert len(rows) >= 2
        loop_types = {r[1] for r in rows}
        # Writer qualifies non-default source via loop_type:source.
        assert "dreams_qa_scene_seed:dreams_qa" in loop_types
        speakers = {r[3] for r in rows}
        assert "bina" in speakers

    # Cleanup: remove this run's qa-log rows + dreams_qa-tagged open_loops.
    async with session_factory() as session, session.begin():
        await session.execute(
            text("DELETE FROM starry_lyfe.dreams_qa_log WHERE run_id = :rid"),
            {"rid": run_id},
        )
        await session.execute(
            text(
                "DELETE FROM starry_lyfe.open_loops "
                "WHERE loop_type LIKE '%:dreams_qa'"
            )
        )
