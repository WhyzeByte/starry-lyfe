"""R5 protocol: async database engine, session factory, and lifecycle management."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from .config import DatabaseSettings, get_db_settings


def build_engine(settings: DatabaseSettings | None = None, echo: bool = False) -> AsyncEngine:
    """Create the async engine with connection pool."""
    if settings is None:
        settings = get_db_settings()
    return create_async_engine(
        settings.async_dsn,
        echo=echo,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )


def build_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create the async session factory."""
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db(engine: AsyncEngine) -> None:
    """Startup: verify connectivity and ensure pgvector extension exists."""
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))


async def close_db(engine: AsyncEngine) -> None:
    """Shutdown: dispose of the connection pool."""
    await engine.dispose()
