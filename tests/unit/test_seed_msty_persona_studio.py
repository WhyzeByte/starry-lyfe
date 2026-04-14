"""Tests for scripts/seed_msty_persona_studio.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_seed_module():
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "seed_msty_persona_studio.py"
    spec = importlib.util.spec_from_file_location("seed_msty_persona_studio", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VOICE_SAMPLE = """\
## Example 1: Test

**User:**
Hello.

**Assistant:**
Hi.

**Abbreviated:** Short reply.
"""


def test_build_persona_configs_supports_flat_voice_layout(monkeypatch) -> None:
    module = _load_seed_module()
    project_root = Path("C:/seed-test-root")
    flat_path = project_root / "Characters" / "Adelia_Raye_Voice.md"
    path_cls = type(flat_path)

    monkeypatch.setattr(module, "PROJECT_ROOT", project_root)
    monkeypatch.setattr(
        module,
        "VOICE_PATHS",
        {"adelia": ("Characters/Adelia_Raye_Voice.md", "Characters/Adelia/Adelia_Raye_Voice.md")},
    )
    monkeypatch.setattr(
        path_cls,
        "exists",
        lambda self: self == flat_path,
        raising=False,
    )
    monkeypatch.setattr(
        path_cls,
        "read_text",
        lambda self, encoding="utf-8": VOICE_SAMPLE,
        raising=False,
    )

    configs = module.build_persona_configs()

    assert len(configs) == 1
    assert configs[0]["character_id"] == "adelia"
    assert configs[0]["few_shots"][0]["assistant"] == "Short reply."


def test_build_persona_configs_supports_legacy_nested_voice_layout(monkeypatch) -> None:
    module = _load_seed_module()
    project_root = Path("C:/seed-test-root")
    legacy_path = project_root / "Characters" / "Adelia" / "Adelia_Raye_Voice.md"
    path_cls = type(legacy_path)

    monkeypatch.setattr(module, "PROJECT_ROOT", project_root)
    monkeypatch.setattr(
        module,
        "VOICE_PATHS",
        {"adelia": ("Characters/Adelia_Raye_Voice.md", "Characters/Adelia/Adelia_Raye_Voice.md")},
    )
    monkeypatch.setattr(
        path_cls,
        "exists",
        lambda self: self == legacy_path,
        raising=False,
    )
    monkeypatch.setattr(
        path_cls,
        "read_text",
        lambda self, encoding="utf-8": VOICE_SAMPLE,
        raising=False,
    )

    configs = module.build_persona_configs()

    assert len(configs) == 1
    assert configs[0]["character_id"] == "adelia"
    assert configs[0]["few_shots"][0]["title"] == "Test"
