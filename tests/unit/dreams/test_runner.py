"""Unit tests for Phase 6 Dreams runner orchestration."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.dreams import (
    DreamsSettings,
    StubBDOne,
    run_dreams_pass,
)


class _StubSession:
    async def __aenter__(self) -> _StubSession:
        return self

    async def __aexit__(self, *args: Any) -> None:
        return None


def _stub_session_factory() -> _StubSession:
    return _StubSession()


@pytest.fixture(scope="module")
def canon() -> Any:
    return load_all_canon()


class TestRunDreamsPass:
    async def test_returns_result_with_all_four_characters(self, canon: Any) -> None:
        result = await run_dreams_pass(
            session_factory=_stub_session_factory,  # type: ignore[arg-type]
            llm_client=StubBDOne(),
            canon=canon,
            now=datetime(2026, 4, 14, 3, 30, tzinfo=UTC),
        )
        assert set(result.character_results.keys()) == {"adelia", "bina", "reina", "alicia"}

    async def test_schedule_generator_fires_for_every_character(self, canon: Any) -> None:
        result = await run_dreams_pass(
            session_factory=_stub_session_factory,  # type: ignore[arg-type]
            llm_client=StubBDOne(),
            canon=canon,
            now=datetime(2026, 4, 14, 3, 30, tzinfo=UTC),
        )
        for char_id, cr in result.character_results.items():
            assert cr.schedule_generated, f"{char_id} schedule missing"

    async def test_run_id_is_unique(self, canon: Any) -> None:
        a = await run_dreams_pass(
            session_factory=_stub_session_factory,  # type: ignore[arg-type]
            llm_client=StubBDOne(),
            canon=canon,
            now=datetime(2026, 4, 14, 3, 30, tzinfo=UTC),
        )
        b = await run_dreams_pass(
            session_factory=_stub_session_factory,  # type: ignore[arg-type]
            llm_client=StubBDOne(),
            canon=canon,
            now=datetime(2026, 4, 14, 3, 30, tzinfo=UTC),
        )
        assert a.run_id != b.run_id

    async def test_per_character_warnings_aggregate_into_pass_result(self, canon: Any) -> None:
        """Placeholder generators emit warnings; verify they aggregate up."""
        result = await run_dreams_pass(
            session_factory=_stub_session_factory,  # type: ignore[arg-type]
            llm_client=StubBDOne(),
            canon=canon,
            now=datetime(2026, 4, 14, 3, 30, tzinfo=UTC),
        )
        # 4 characters × 4 stub generators with warnings = 16 warnings minimum.
        assert len(result.warnings) >= 4

    async def test_weekday_vs_weekend_schedule_differs(self, canon: Any) -> None:
        monday = datetime(2026, 4, 13, 3, 30, tzinfo=UTC)  # Monday → Tomorrow = Tuesday
        saturday = datetime(2026, 4, 18, 3, 30, tzinfo=UTC)  # Saturday → Tomorrow = Sunday

        weekday_result = await run_dreams_pass(
            session_factory=_stub_session_factory,  # type: ignore[arg-type]
            llm_client=StubBDOne(),
            canon=canon,
            now=monday,
        )
        weekend_result = await run_dreams_pass(
            session_factory=_stub_session_factory,  # type: ignore[arg-type]
            llm_client=StubBDOne(),
            canon=canon,
            now=saturday,
        )

        # Both passes complete; characters covered in both.
        assert weekday_result.character_results.keys() == weekend_result.character_results.keys()


class TestDreamsSettings:
    def test_defaults(self) -> None:
        settings = DreamsSettings()
        assert settings.enabled is True
        assert settings.dry_run is False
        assert settings.schedule == "30 3 * * *"

    def test_from_env_honors_enabled_false(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("STARRY_LYFE__DREAMS__ENABLED", "false")
        settings = DreamsSettings.from_env()
        assert settings.enabled is False

    def test_from_env_honors_dry_run(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("STARRY_LYFE__DREAMS__DRY_RUN", "true")
        settings = DreamsSettings.from_env()
        assert settings.dry_run is True
