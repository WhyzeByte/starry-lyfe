"""Unit tests for PostgreSQL integration-test skip policy."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CONFTST_PATH = ROOT / "tests" / "integration" / "conftest.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("integration_conftest_under_test", CONFTST_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_require_postgres_defaults_false(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.delenv("STARRY_LYFE__TEST__REQUIRE_POSTGRES", raising=False)
    assert module._require_postgres() is False


def test_require_postgres_accepts_truthy_env(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setenv("STARRY_LYFE__TEST__REQUIRE_POSTGRES", "true")
    assert module._require_postgres() is True


def test_skip_or_fail_integration_skips_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    settings = module.DatabaseSettings()
    monkeypatch.delenv("STARRY_LYFE__TEST__REQUIRE_POSTGRES", raising=False)

    with pytest.raises(pytest.skip.Exception) as exc_info:
        module._skip_or_fail_integration("connection refused", settings)

    assert "connection refused" in str(exc_info.value)
    assert "fail instead of skip" in str(exc_info.value)


def test_skip_or_fail_integration_raises_when_required(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    settings = module.DatabaseSettings()
    monkeypatch.setenv("STARRY_LYFE__TEST__REQUIRE_POSTGRES", "1")

    with pytest.raises(RuntimeError) as exc_info:
        module._skip_or_fail_integration("missing tables", settings)

    assert "missing tables" in str(exc_info.value)
    assert "starry_lyfe" in str(exc_info.value)
