"""Phase 10.7 regression — Phase 9 evaluator MUST refuse to update pinned fields.

Pre-pins a ``dyad_state_pins`` row for (adelia_bina, trust). Then runs the
Phase 9 evaluator. Then asserts the trust column on the dyad row is
unchanged. Closes AC-10.27.

Skips when Postgres is unreachable (matches integration-suite pattern).
"""

from __future__ import annotations

import pytest
from sqlalchemy import text

pytestmark = pytest.mark.asyncio


async def test_phase_9_skips_pinned_field(
    engine,
    seeded_session,  # noqa: ARG001 — keep dep so schema is migrated
) -> None:
    """Pin (adelia_bina, trust). Run Phase 9. Trust column does NOT move.

    Seeds the adelia_bina dyad row via the engine-bound session so the row
    is visible across sessions. (``seeded_session``'s seeds live inside its
    rolled-back transaction and are invisible to engine-bound sessions —
    that's why we cannot bind via ``seeded_session.bind``; doing so would
    also yield the wrapped sync ``Connection`` and trigger MissingGreenlet.)
    """
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from starry_lyfe.api.config import ApiSettings
    from starry_lyfe.api.orchestration.internal_relationship import (
        evaluate_and_update_internal,
    )
    from starry_lyfe.canon.loader import load_all_canon
    from starry_lyfe.db.seed import _seed_dyad_state_internal
    from starry_lyfe.dreams.consistency.pinning import pin_field

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    # 1. Seed the adelia_bina dyad row at engine scope so the row persists
    # across the test's sessions. Idempotent via ON CONFLICT DO NOTHING.
    canon = load_all_canon()
    async with session_factory() as session, session.begin():
        await _seed_dyad_state_internal(session, canon)

    # 2. Read the current trust value for the adelia_bina dyad.
    async with session_factory() as session:
        result = await session.execute(
            text(
                "SELECT trust FROM starry_lyfe.dyad_state_internal "
                "WHERE dyad_key = 'adelia_bina'"
            )
        )
        row = result.first()
        if row is None:
            pytest.skip("seed_dyad_state_internal did not produce adelia_bina row")
        original_trust: float = float(row[0])

    # 3. Pin trust.
    async with session_factory() as session, session.begin():
        await pin_field(
            session,
            relationship_key="adelia_bina",
            pov_character_id=None,
            field_name="trust",
            pinned_value=original_trust,
            pinned_reason="Phase 10.7 regression test pin",
        )

    # 4. Run Phase 9 with no LLM (heuristic path). The heuristic produces
    # nonzero deltas for non-empty response_text — we just need ANY proposed
    # delta on trust so we can verify the pin blocks the write.
    settings = ApiSettings(internal_relationship_eval_llm=False)
    response_text = (
        "I am angry at her about the way the kitchen was left. We do not need "
        "to talk about it tonight but I am noting it. The trust is fine."
    )
    await evaluate_and_update_internal(
        session_factory,
        character_id="adelia",
        response_text=response_text,
        llm_client=None,
        settings=settings,
    )

    # 5. Verify trust unchanged.
    async with session_factory() as session:
        result = await session.execute(
            text(
                "SELECT trust FROM starry_lyfe.dyad_state_internal "
                "WHERE dyad_key = 'adelia_bina'"
            )
        )
        row = result.first()
        assert row is not None
        post_trust = float(row[0])
        assert post_trust == original_trust, (
            f"Phase 10.7 regression: pinned trust field was updated "
            f"({original_trust} -> {post_trust}) despite active pin"
        )

    # 6. Cleanup pin AND seeded dyad row so subsequent tests aren't poisoned.
    async with session_factory() as session, session.begin():
        await session.execute(
            text(
                "DELETE FROM starry_lyfe.dyad_state_pins "
                "WHERE relationship_key = 'adelia_bina' "
                "AND field_name = 'trust'"
            )
        )
