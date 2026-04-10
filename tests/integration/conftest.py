"""Integration test fixtures using a real PostgreSQL database.

Requires Docker plus an Alembic-migrated database before running `pytest tests/integration`.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.db.base import SCHEMA
from starry_lyfe.db.config import get_db_settings
from starry_lyfe.db.models import (  # noqa: F401
    CanonFact,
    CharacterBaseline,
    DyadStateInternal,
    DyadStateWhyze,
    EpisodicMemory,
    OpenLoop,
    TransientSomaticState,
)
from starry_lyfe.db.seed import (
    _seed_canon_facts,
    _seed_character_baselines,
    _seed_dyad_state_internal,
    _seed_dyad_state_whyze,
    _seed_transient_somatic,
)

APPLICATION_TABLES = (
    "canon_facts",
    "character_baselines",
    "dyad_state_whyze",
    "dyad_state_internal",
    "episodic_memories",
    "open_loops",
    "transient_somatic_states",
)
REQUIRED_TABLES = frozenset((*APPLICATION_TABLES, "alembic_version"))


async def _fetch_schema_tables(connection: AsyncConnection) -> set[str]:
    result = await connection.execute(
        text(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = :schema
            """
        ),
        {"schema": SCHEMA},
    )
    return {row[0] for row in result}


async def _assert_migrated_schema(connection: AsyncConnection) -> None:
    existing_tables = await _fetch_schema_tables(connection)
    missing_tables = sorted(REQUIRED_TABLES - existing_tables)
    if missing_tables:
        missing = ", ".join(missing_tables)
        raise RuntimeError(
            f"Integration tests require an Alembic-migrated database. Missing tables in "
            f"schema '{SCHEMA}': {missing}. Run `python -m alembic upgrade head` first."
        )


async def _truncate_application_tables(connection: AsyncConnection) -> None:
    qualified_tables = ", ".join(f"{SCHEMA}.{table}" for table in APPLICATION_TABLES)
    await connection.execute(text(f"TRUNCATE TABLE {qualified_tables} RESTART IDENTITY CASCADE"))


@pytest.fixture(scope="session")
def engine() -> AsyncEngine:
    """Create a test engine that never reuses asyncpg connections across loops."""
    settings = get_db_settings()
    return create_async_engine(
        settings.async_dsn,
        echo=False,
        poolclass=NullPool,
    )


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def setup_database(engine: AsyncEngine) -> AsyncGenerator[None]:
    """Require migrated schema, then keep application tables empty across the test session."""
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await _assert_migrated_schema(conn)
        await _truncate_application_tables(conn)
    yield
    async with engine.begin() as conn:
        await _truncate_application_tables(conn)
    await engine.dispose()


@pytest_asyncio.fixture(loop_scope="function")
async def db_session(
    engine: AsyncEngine,
    setup_database: None,
) -> AsyncGenerator[AsyncSession]:
    """Provide a per-test session bound to a dedicated connection transaction."""
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)
        try:
            yield session
        finally:
            await session.close()
            if transaction.is_active:
                await transaction.rollback()


@pytest_asyncio.fixture(loop_scope="function")
async def seeded_session(
    engine: AsyncEngine,
    setup_database: None,
) -> AsyncGenerator[AsyncSession]:
    """Provide a per-test session seeded with canon data and rolled back afterward."""
    canon = load_all_canon()
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)
        await _seed_canon_facts(session, canon)
        await _seed_character_baselines(session, canon)
        await _seed_dyad_state_whyze(session, canon)
        await _seed_dyad_state_internal(session, canon)
        await _seed_transient_somatic(session, canon)
        await session.flush()
        yield session
        await session.close()
        if transaction.is_active:
            await transaction.rollback()
