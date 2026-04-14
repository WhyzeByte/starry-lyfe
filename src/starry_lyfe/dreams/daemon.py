"""Phase 6 Dreams daemon + CLI entry point.

Production deployment runs ``python -m starry_lyfe.dreams``; this starts
an AsyncIOScheduler (apscheduler) configured per ``DreamsSettings`` and
blocks forever until SIGTERM/SIGINT.

Ad-hoc runs use ``python -m starry_lyfe.dreams --once`` which invokes a
single ``run_dreams_pass`` and exits. ``--dry-run`` flag short-circuits
writes for smoke validation.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
from dataclasses import replace
from datetime import UTC, datetime

from ..canon.loader import load_all_canon
from .config import DreamsSettings
from .errors import DreamsScheduleError
from .llm import BDOne, BDOneSettings, StubBDOne
from .runner import run_dreams_pass
from .types import LLMClient

logger = logging.getLogger(__name__)


def _build_llm_client(use_stub: bool) -> LLMClient:
    """Return a real BDOne for production, StubBDOne for dry-run / tests."""
    if use_stub:
        return StubBDOne(default_text="[dreams dry-run stub]")
    return BDOne(BDOneSettings.from_env())


async def _invoke_once(
    settings: DreamsSettings, *, use_stub: bool, now: datetime | None = None
) -> None:
    """Run one Dreams pass end-to-end and log the aggregate result."""
    canon = load_all_canon()
    llm_client = _build_llm_client(use_stub=use_stub)

    # Session factory: lazy import so the daemon can start without a live DB
    # available (the factory only executes when a generator needs a snapshot).
    from ..db.config import get_db_settings
    from ..db.engine import build_engine, build_session_factory

    engine = build_engine(get_db_settings())
    session_factory = build_session_factory(engine)

    try:
        result = await run_dreams_pass(
            session_factory=session_factory,
            llm_client=llm_client,
            canon=canon,
            settings=settings,
            now=now,
        )
        logger.info(
            "dreams_cli_pass_complete",
            extra={
                "run_id": str(result.run_id),
                "warnings": result.warnings,
                "input_tokens": result.total_input_tokens,
                "output_tokens": result.total_output_tokens,
            },
        )
    finally:
        await engine.dispose()


async def start_scheduler(settings: DreamsSettings | None = None) -> None:
    """Start the Dreams apscheduler and block forever.

    Raises:
        DreamsScheduleError: if the cron expression fails to parse.
    """
    settings = settings or DreamsSettings.from_env()

    if not settings.enabled:
        logger.warning(
            "dreams_scheduler_disabled",
            extra={"reason": "STARRY_LYFE__DREAMS__ENABLED=false"},
        )
        await asyncio.Event().wait()
        return

    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore[import-untyped]
        from apscheduler.triggers.cron import CronTrigger  # type: ignore[import-untyped]
    except ImportError as exc:  # pragma: no cover — apscheduler always present in prod
        msg = (
            "apscheduler is required for Dreams scheduler. "
            "Install via `pip install apscheduler>=3.10`."
        )
        raise DreamsScheduleError(msg) from exc

    try:
        trigger = CronTrigger.from_crontab(settings.schedule)
    except ValueError as exc:
        msg = f"Invalid DREAMS__SCHEDULE cron expression: {settings.schedule!r}"
        raise DreamsScheduleError(msg) from exc

    scheduler = AsyncIOScheduler()

    async def _job() -> None:
        await _invoke_once(settings, use_stub=False)

    scheduler.add_job(
        _job,
        trigger,
        id="dreams_nightly",
        max_instances=1,
        misfire_grace_time=settings.misfire_grace_seconds,
        coalesce=True,
    )
    scheduler.start()
    logger.info(
        "dreams_scheduler_started",
        extra={
            "schedule": settings.schedule,
            "misfire_grace_s": settings.misfire_grace_seconds,
        },
    )
    try:
        await asyncio.Event().wait()
    finally:
        scheduler.shutdown(wait=False)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="starry_lyfe.dreams",
        description="Starry-Lyfe Dreams Engine (Phase 6) — nightly batch + CLI.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run one Dreams pass and exit (skip the scheduler loop).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Short-circuit DB writes; use StubBDOne instead of live LLM.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """CLI entry point: ``python -m starry_lyfe.dreams [--once] [--dry-run]``."""
    logging.basicConfig(level=logging.INFO)
    args = _parse_args(argv)

    settings = DreamsSettings.from_env()
    if args.dry_run:
        settings = replace(settings, dry_run=True)

    if args.once:
        asyncio.run(_invoke_once(settings, use_stub=args.dry_run, now=datetime.now(UTC)))
    else:
        asyncio.run(start_scheduler(settings))


if __name__ == "__main__":  # pragma: no cover
    main()
