"""Phase 6 Dreams Engine configuration (GNK pattern).

Settings resolved from environment via ``STARRY_LYFE__DREAMS__*`` vars.
Production boot loads ``DreamsSettings.from_env()``; tests pass
``DreamsSettings(...)`` directly.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    return default


@dataclass(frozen=True)
class DreamsSettings:
    """Configuration for the Dreams engine."""

    # Cron expression evaluated by apscheduler CronTrigger.from_crontab.
    # Default: 03:30 local every day.
    schedule: str = "30 3 * * *"

    # When False, the daemon loads but does not schedule runs. Ops safety
    # switch; defaults to True.
    enabled: bool = True

    # When True, run_dreams_pass logs writes but does not commit them.
    # Used for smoke tests and canary validation.
    dry_run: bool = False

    # Per-character LLM token budget per pass. Aggregate across all 5
    # generators for one character.
    max_tokens_per_character: int = 8000

    # Misfire grace window for apscheduler (seconds). If the scheduled
    # fire time is missed by less than this amount, catch up once.
    misfire_grace_seconds: int = 3600

    @classmethod
    def from_env(cls) -> DreamsSettings:
        return cls(
            schedule=os.getenv("STARRY_LYFE__DREAMS__SCHEDULE", "30 3 * * *"),
            enabled=_env_bool("STARRY_LYFE__DREAMS__ENABLED", default=True),
            dry_run=_env_bool("STARRY_LYFE__DREAMS__DRY_RUN", default=False),
            max_tokens_per_character=int(
                os.getenv("STARRY_LYFE__DREAMS__MAX_TOKENS_PER_CHAR", "8000")
            ),
            misfire_grace_seconds=int(
                os.getenv("STARRY_LYFE__DREAMS__MISFIRE_GRACE_S", "3600")
            ),
        )
