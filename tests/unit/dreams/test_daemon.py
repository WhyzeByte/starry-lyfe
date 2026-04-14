"""Unit tests for Phase 6 Dreams daemon + CLI (R7 remediation / F4).

Closes part of F4 Medium. Covers the CLI parser, env-driven settings,
and scheduler-configuration error paths. The actual scheduler loop
blocks forever, so we do NOT start it — we only assert the config
construction and short-circuit paths.
"""

from __future__ import annotations

import pytest

from starry_lyfe.dreams import DreamsScheduleError, DreamsSettings
from starry_lyfe.dreams.daemon import _build_llm_client, _parse_args, start_scheduler


class TestCLIParser:
    def test_once_flag_parses(self) -> None:
        args = _parse_args(["--once"])
        assert args.once is True
        assert args.dry_run is False

    def test_dry_run_flag_parses(self) -> None:
        args = _parse_args(["--dry-run"])
        assert args.once is False
        assert args.dry_run is True

    def test_combined_flags_parse(self) -> None:
        args = _parse_args(["--once", "--dry-run"])
        assert args.once is True
        assert args.dry_run is True

    def test_no_args_defaults(self) -> None:
        args = _parse_args([])
        assert args.once is False
        assert args.dry_run is False


class TestLLMClientSelection:
    def test_stub_client_when_use_stub_true(self) -> None:
        from starry_lyfe.dreams import StubBDOne

        client = _build_llm_client(use_stub=True)
        assert isinstance(client, StubBDOne)

    def test_real_client_when_use_stub_false(self) -> None:
        from starry_lyfe.dreams import BDOne

        client = _build_llm_client(use_stub=False)
        assert isinstance(client, BDOne)


class TestSchedulerConfig:
    async def test_disabled_scheduler_blocks_without_starting(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """STARRY_LYFE__DREAMS__ENABLED=false → scheduler never starts.

        The function then blocks on asyncio.Event().wait() forever in
        production. For tests we call start_scheduler with a settings
        object and immediately cancel the task.
        """
        import asyncio

        settings = DreamsSettings(enabled=False)

        async def _run_briefly() -> None:
            task = asyncio.create_task(start_scheduler(settings))
            # Give the scheduler a moment to reach the wait().
            await asyncio.sleep(0.05)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                return None
            return None

        # Should not raise — the disabled path reaches the Event().wait()
        # quickly and we can cancel cleanly.
        await _run_briefly()

    async def test_invalid_cron_raises_schedule_error(self) -> None:
        """Invalid cron → DreamsScheduleError per daemon contract."""
        settings = DreamsSettings(schedule="not a valid cron at all")
        with pytest.raises(DreamsScheduleError, match="Invalid DREAMS__SCHEDULE"):
            await start_scheduler(settings)


class TestDreamsSettingsFromEnv:
    def test_schedule_override_via_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("STARRY_LYFE__DREAMS__SCHEDULE", "0 4 * * *")
        settings = DreamsSettings.from_env()
        assert settings.schedule == "0 4 * * *"

    def test_max_tokens_override_via_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("STARRY_LYFE__DREAMS__MAX_TOKENS_PER_CHAR", "12000")
        settings = DreamsSettings.from_env()
        assert settings.max_tokens_per_character == 12000

    def test_misfire_grace_override_via_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("STARRY_LYFE__DREAMS__MISFIRE_GRACE_S", "1800")
        settings = DreamsSettings.from_env()
        assert settings.misfire_grace_seconds == 1800
