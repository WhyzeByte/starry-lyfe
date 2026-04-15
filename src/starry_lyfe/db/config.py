"""GNK protocol: database configuration from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database connection settings loaded from STARRY_LYFE__DB__* env vars."""

    host: str = "localhost"
    port: int = 5432
    name: str = "starry_lyfe"
    user: str = "starry_lyfe"
    password: str = "changeme"

    model_config = {"env_prefix": "STARRY_LYFE__DB__"}

    @property
    def async_dsn(self) -> str:
        """Build the asyncpg connection string."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def sync_dsn(self) -> str:
        """Build the synchronous connection string (for Alembic)."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class EmbeddingSettings(BaseSettings):
    """Embedding model configuration.

    Defaults target LM Studio's OpenAI-compatible server on port 1234
    with ``text-embedding-nomic-embed-text-v1.5`` (768-dim), which matches
    the ``Vector(768)`` column on ``episodic_memories``.
    """

    model: str = "text-embedding-nomic-embed-text-v1.5@q5_k_m"
    dimension: int = 768
    base_url: str = "http://localhost:1234/v1"

    model_config = {"env_prefix": "STARRY_LYFE__EXT__EMBEDDING_"}


def get_db_settings() -> DatabaseSettings:
    """Load database settings from environment."""
    return DatabaseSettings()


def get_embedding_settings() -> EmbeddingSettings:
    """Load embedding settings from environment."""
    return EmbeddingSettings()
