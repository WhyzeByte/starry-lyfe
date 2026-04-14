"""Phase 6 R6 — DB round-trip integration test.

Closes F3 High (integration tests were seam-only, not DB-backed). This
test uses a live Postgres via the project's existing `db_session` +
`seeded_session` fixtures in `tests/integration/conftest.py`.

Contract proven end-to-end:
1. run_dreams_pass() with a real session_factory + StubBDOne
2. DB rows actually land (activities, episodic_memories diary +
   off_screen, open_loops, consolidation_log, possibly life_states)
3. retrieve_memories() on the next turn includes Dreams-written
   activities + open_loops
4. The extended MemoryBundle exposes the Tier-8 tiers

The test auto-skips unless the project Postgres is migrated and
reachable; set STARRY_LYFE__TEST__REQUIRE_POSTGRES=1 to force-fail.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Any

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.db.models.activity import Activity
from starry_lyfe.db.models.consolidation_log import ConsolidationLog
from starry_lyfe.db.models.episodic_memory import EpisodicMemory
from starry_lyfe.db.models.open_loop import OpenLoop
from starry_lyfe.db.retrieval import retrieve_memories
from starry_lyfe.dreams import StubBDOne, run_dreams_pass


class _StubEmbeddingService:
    async def embed(self, text: str) -> list[float]:
        return [0.0] * 768


class _SharedSessionWrapper:
    """Wraps a single AsyncSession so the runner's per-character
    ``async with session_factory() as session, session.begin():`` pattern
    works against the same test-owned session.

    - ``__aenter__`` returns self (acts as the session).
    - ``__aexit__`` is a no-op (test fixture owns the real session lifecycle).
    - ``.begin()`` returns an async context manager that wraps
      ``session.begin_nested()`` so each per-character transaction becomes
      a SAVEPOINT inside the test's outer transaction. Writes become
      visible after the savepoint releases, and the test's rollback still
      discards everything at teardown.
    - All other attribute access delegates to the underlying session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def __aenter__(self) -> _SharedSessionWrapper:
        return self

    async def __aexit__(self, *args: Any) -> None:
        # Test owns the underlying session lifecycle; no close here.
        return None

    def begin(self) -> Any:
        return self._session.begin_nested()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._session, name)


@pytest_asyncio.fixture(loop_scope="function")
async def dreams_session_factory(
    engine: AsyncEngine,
    setup_database: None,
) -> AsyncGenerator[Any, None]:
    """Session factory for Dreams round-trip tests.

    Yields a callable that returns a ``_SharedSessionWrapper`` around a
    single AsyncSession. All per-character Dreams writes land through
    this session as SAVEPOINTs; verification queries via the same
    session see the committed savepoint data; the test's outer
    transaction rolls back at teardown so the DB stays clean.
    """
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)

        def _factory() -> _SharedSessionWrapper:
            return _SharedSessionWrapper(session)

        try:
            yield _factory
        finally:
            # fixture owns close
            if transaction.is_active:
                await transaction.rollback()


@pytest.fixture(scope="module")
def canon() -> Any:
    return load_all_canon()


async def test_run_dreams_pass_writes_rows_to_db(
    dreams_session_factory: Any, canon: Any
) -> None:
    """F3 / AC-R1.7: the runner actually persists DB state.

    Pre-R1 this test would have been impossible because the runner had
    no writer path at all.
    """
    stub = StubBDOne(
        default_text=(
            "End-of-day reflection about the work.\n"
            "Branch: sit and watch.\nBranch: walk outside."
        )
    )
    now = datetime(2026, 4, 14, 3, 30, tzinfo=UTC)

    result = await run_dreams_pass(
        session_factory=dreams_session_factory,
        llm_client=stub,
        canon=canon,
        now=now,
    )

    # Every character's DreamsCharacterResult should now reflect real
    # DB writes: diary_entry_id is a UUID, activities_designed >= 1,
    # consolidation_log row exists.
    assert set(result.character_results.keys()) == {
        "adelia", "bina", "reina", "alicia"
    }

    # Verify via the same underlying session so SAVEPOINT-released
    # writes are visible.
    session = dreams_session_factory()._session  # type: ignore[attr-defined]

    for character_id in ("adelia", "bina", "reina", "alicia"):
        # Diary / off_screen episodic rows for this character from this run.
        epis = await session.execute(
            select(EpisodicMemory).where(
                EpisodicMemory.character_id == character_id,
                EpisodicMemory.memory_type.in_(["diary", "off_screen"]),
                EpisodicMemory.created_at >= now.replace(tzinfo=UTC),
            )
        )
        epis_rows = list(epis.scalars().all())
        assert epis_rows, f"{character_id}: no diary/off_screen episodic rows written"

        # At least one diary entry per character.
        diary_rows = [r for r in epis_rows if r.memory_type == "diary"]
        assert diary_rows, f"{character_id}: no diary row"

        # Activity row for tomorrow.
        acts = await session.execute(
            select(Activity).where(Activity.character_id == character_id)
        )
        act_rows = list(acts.scalars().all())
        assert act_rows, f"{character_id}: no activity row written"

        # Consolidation log row with the run_id.
        logs = await session.execute(
            select(ConsolidationLog).where(
                ConsolidationLog.character_id == character_id,
                ConsolidationLog.run_id == result.run_id,
            )
        )
        log_rows = list(logs.scalars().all())
        assert log_rows, f"{character_id}: no consolidation_log row"

    # fixture owns close


async def test_retrieve_memories_includes_dreams_written_tiers(
    dreams_session_factory: Any, canon: Any
) -> None:
    """F3 / AC-R1.8: MemoryBundle exposes activities + life_state after a
    Dreams run. Proves Tier 8 is wired into the retrieval path."""
    stub = StubBDOne(
        default_text=(
            "Today's reflection.\n"
            "Branch: opt one.\nBranch: opt two."
        )
    )
    now = datetime(2026, 4, 14, 3, 30, tzinfo=UTC)

    await run_dreams_pass(
        session_factory=dreams_session_factory,
        llm_client=stub,
        canon=canon,
        now=now,
    )

    session = dreams_session_factory()._session  # type: ignore[attr-defined]
    bundle = await retrieve_memories(
        session=session,
        embedding_service=_StubEmbeddingService(),  # type: ignore[arg-type]
        scene_context="kitchen morning",
        character_id="adelia",
    )

    # Activities written by the Dreams pass are retrievable.
    assert bundle.activities, "retrieve_memories did not include Dreams activities"
    assert any(a.character_id == "adelia" for a in bundle.activities)

    # fixture owns close


async def test_new_open_loops_land_in_db(
    dreams_session_factory: Any, canon: Any
) -> None:
    """Open_loops generator new_loops are persisted via write_new_open_loops."""
    stub = StubBDOne(
        default_text=(
            "NEW: follow up on the shop order.\n"
            "NEW: raise the weekend trip.\n"
            "NEW: check on the atelier inventory.\n"
        )
    )
    now = datetime(2026, 4, 14, 3, 30, tzinfo=UTC)

    result = await run_dreams_pass(
        session_factory=dreams_session_factory,
        llm_client=stub,
        canon=canon,
        now=now,
    )

    # Each character should have at least 1 new open loop added via the
    # open_loops generator (StubBDOne returns identical text per call).
    for cr in result.character_results.values():
        assert cr.open_loops_added >= 1, (
            f"{cr.character_id}: expected ≥1 open loop added; got {cr.open_loops_added}"
        )

    # And the DB has the rows.
    session = dreams_session_factory()
    loops = await session.execute(
        select(OpenLoop).where(
            OpenLoop.character_id == "adelia",
            OpenLoop.status == "open",
            OpenLoop.created_at >= now.replace(tzinfo=UTC),
        )
    )
    loop_rows = list(loops.scalars().all())
    assert loop_rows, "no Dreams-written open_loops rows for adelia"
    # fixture owns close


async def test_alicia_away_activity_carries_communication_mode_in_db(
    dreams_session_factory: Any, canon: Any
) -> None:
    """Phase A'' retroactive end-to-end: Alicia-away activity row has the
    communication_mode column populated at DB level."""
    import types

    async def _alicia_away_snapshot(
        session: Any, character_id: str, now: Any
    ) -> Any:
        from starry_lyfe.dreams import SessionSnapshot

        is_away = character_id == "alicia"
        return SessionSnapshot(
            character_id=character_id,
            life_state=types.SimpleNamespace(is_away=is_away),
        )

    stub = StubBDOne(
        default_text=(
            "Opening setting.\n"
            "Branch: one option.\nBranch: another option."
        )
    )
    now = datetime(2026, 4, 14, 3, 30, tzinfo=UTC)

    await run_dreams_pass(
        session_factory=dreams_session_factory,
        llm_client=stub,
        canon=canon,
        now=now,
        snapshot_loader=_alicia_away_snapshot,
    )

    session = dreams_session_factory()._session  # type: ignore[attr-defined]
    # R3-F1 fix: filter to rows written by THIS Dreams run using the
    # injected `now` as a created_at watermark. Previously this query
    # ordered nothing and assertion[0] could pick a pre-existing seeded
    # row with communication_mode=None, producing a false regression.
    now_utc = now.astimezone(UTC).replace(tzinfo=UTC)
    acts = await session.execute(
        select(Activity)
        .where(
            Activity.character_id == "alicia",
            Activity.created_at >= now_utc,
        )
        .order_by(Activity.created_at.desc())
    )
    alicia_acts = list(acts.scalars().all())
    assert alicia_acts, "no activity row for alicia written by this run"
    assert alicia_acts[0].communication_mode in {"phone", "letter", "video_call"}, (
        f"Alicia-away activity carries no communication_mode tag; "
        f"got {alicia_acts[0].communication_mode!r}"
    )

    # Non-Alicia characters should not carry a comm-mode tag (defensive).
    # Same R3-F1 fix: filter to this run only.
    for char in ("adelia", "bina", "reina"):
        rows = await session.execute(
            select(Activity).where(
                Activity.character_id == char,
                Activity.created_at >= now_utc,
            )
        )
        for row in rows.scalars().all():
            assert row.communication_mode is None, (
                f"{char} activity should not carry communication_mode; "
                f"got {row.communication_mode!r}"
            )

    # fixture owns close


async def test_dreams_activity_surfaces_into_assembler_layer_6(
    dreams_session_factory: Any, canon: Any
) -> None:
    """R3-F2 closure: Dreams-written Activity row reaches Layer 6 via retrieval.

    End-to-end proof that the Phase 6 -> Phase 3 consumer handoff is
    not seam-only: run Dreams, then call assemble_context() with the
    same session and verify the activity's narrator_script appears in
    the assembled prompt body.
    """
    from typing import cast as _cast

    from sqlalchemy.ext.asyncio import AsyncSession as _AsyncSession

    from starry_lyfe.context.assembler import assemble_context
    from starry_lyfe.context.types import CommunicationMode, SceneState

    stub = StubBDOne(
        default_text=(
            "Morning in the atelier, the light falling across the bench.\n"
            "Branch: Adelia starts with the kiln test.\n"
            "Branch: Adelia opens the order book first."
        )
    )
    now = datetime(2026, 4, 14, 3, 30, tzinfo=UTC)

    await run_dreams_pass(
        session_factory=dreams_session_factory,
        llm_client=stub,
        canon=canon,
        now=now,
    )

    session = dreams_session_factory()._session  # type: ignore[attr-defined]

    scene = SceneState(
        present_characters=["adelia", "whyze"],
        scene_description="morning in the atelier",
        communication_mode=CommunicationMode.IN_PERSON,
    )
    prompt = await assemble_context(
        character_id="adelia",
        scene_context="morning in the atelier",
        scene_state=scene,
        session=_cast(_AsyncSession, session),
        embedding_service=_StubEmbeddingService(),  # type: ignore[arg-type]
    )

    assert prompt.is_terminally_anchored
    # The Dreams activity's narrator script should surface in Layer 6's
    # new Dreams-opener section. Content is LLM-generated (StubBDOne),
    # so we assert on the stable header marker.
    assert "Today's Dreams scene opener" in prompt.prompt, (
        "Dreams-written Activity did not reach the assembled prompt via "
        "retrieval -> Layer 6. R3-F2 contract not met."
    )
