"""GNK protocol: HTTP service settings loaded from STARRY_LYFE__API__* env vars."""

from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings


class ApiSettings(BaseSettings):
    """Configuration for the Phase 7 HTTP service.

    Loaded from environment with prefix ``STARRY_LYFE__API__``. Defaults
    are tuned for the single-operator local deployment described in
    CLAUDE.md §11; production (if it ever exists) overrides via env.
    """

    host: str = "0.0.0.0"
    port: int = 8001
    api_key: str = ""
    cors_origins: list[str] = []
    default_character: str = "adelia"
    # F3 closure: when True, /health/ready issues a live HEAD probe against
    # the BD-1 provider URL. Tests that don't want network I/O set this
    # False; production keeps it True for truthful readiness.
    health_bd1_probe: bool = True
    # F1 closure: Crew-mode multi-speaker cap. Project axiom (CLAUDE.md §16):
    # "Max 3 choices per decision point. Fun, not overwhelming."
    crew_max_speakers: int = 3

    model_config = {
        "env_prefix": "STARRY_LYFE__API__",
        "env_parse_none_str": "",
    }

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: object) -> object:
        """Allow comma-separated env value (e.g. ``a.com,b.com``)."""
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            return [entry.strip() for entry in stripped.split(",") if entry.strip()]
        return value

    @field_validator("default_character")
    @classmethod
    def _validate_default_character(cls, value: str) -> str:
        # Lazy import to avoid pulling canon at module import time.
        from starry_lyfe.canon.schemas.enums import CharacterID

        valid = set(CharacterID.all_strings())
        if value not in valid:
            raise ValueError(
                f"default_character must be one of {sorted(valid)}, got {value!r}"
            )
        return value


def get_api_settings() -> ApiSettings:
    """Load API settings from environment. Cached at FastAPI startup."""
    return ApiSettings()
