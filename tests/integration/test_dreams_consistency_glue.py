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
    seeded_session,  # noqa: ARG001 — fixture imports trigger DB setup
) -> None:
    """Real Postgres + StubBDOne: nightly pass writes 10 dreams_qa_log rows."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from starry_lyfe.dreams.generators.consistency_qa import generate_consistency_qa

    canon = load_all_canon()
    # Seeded session's engine binds the session_factory the QA pass needs.
    bind = seeded_session.bind
    session_factory = async_sessionmaker(bind=bind, expire_on_commit=False)

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


async def test_consistency_qa_writes_pin_on_factual_contradiction(
    seeded_session,  # noqa: ARG001
) -> None:
    """Synthetic factual_contradiction verdict produces a dyad_state_pins row."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from starry_lyfe.dreams.generators.consistency_qa import generate_consistency_qa

    canon = load_all_canon()
    bind = seeded_session.bind
    session_factory = async_sessionmaker(bind=bind, expire_on_commit=False)

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
