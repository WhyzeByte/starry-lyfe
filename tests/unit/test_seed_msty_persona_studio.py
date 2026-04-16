"""Tests for scripts/seed_msty_persona_studio.py (post-10.5 rich-YAML rewire)."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest


def _load_seed_module() -> Any:
    script_path = (
        Path(__file__).resolve().parents[2] / "scripts" / "seed_msty_persona_studio.py"
    )
    spec = importlib.util.spec_from_file_location(
        "seed_msty_persona_studio", script_path,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_persona_configs_reads_all_four_women_from_rich_yaml() -> None:
    """Post-10.5: seed pulls from Characters/{name}.yaml::voice.few_shots.examples."""
    module = _load_seed_module()
    configs = module.build_persona_configs()

    assert len(configs) == 4
    ids = {c["character_id"] for c in configs}
    assert ids == {"adelia", "bina", "reina", "alicia"}

    for cfg in configs:
        assert isinstance(cfg["few_shots"], list), cfg["character_id"]
        assert cfg["few_shots"], (
            f"{cfg['character_id']} has no few_shot entries — "
            f"voice.few_shots.examples missing or malformed"
        )


def test_few_shot_entry_shape_title_user_assistant() -> None:
    """Each entry carries title + user + assistant strings (no empties)."""
    module = _load_seed_module()
    configs = module.build_persona_configs()

    for cfg in configs:
        for entry in cfg["few_shots"]:
            assert entry["title"], cfg["character_id"]
            assert entry["user"], cfg["character_id"]
            assert entry["assistant"], cfg["character_id"]


def test_seed_does_not_read_archived_voice_md(monkeypatch: pytest.MonkeyPatch) -> None:
    """Post-10.5: the seed must not try to read Archive/v7.1_pre_yaml/*.md.

    The archived Voice.md files were the pre-10.5 source. The rewired
    script must source exclusively from rich YAML and never touch the
    archive tree. Fail loud if anything else reaches a filesystem open
    against Voice.md paths.
    """
    module = _load_seed_module()

    opens: list[str] = []
    real_read = Path.read_text

    def tracking_read_text(self: Path, *args: Any, **kwargs: Any) -> str:
        opens.append(str(self))
        return real_read(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", tracking_read_text, raising=False)
    module.build_persona_configs()
    voice_md_opens = [p for p in opens if "Voice.md" in p]
    assert not voice_md_opens, (
        f"seed script read archived Voice.md files: {voice_md_opens}"
    )


def test_main_emits_rich_yaml_authority_marker(capsys: pytest.CaptureFixture[str]) -> None:
    """JSON output must cite rich YAML as source of truth (F3 governance fix)."""
    import json

    module = _load_seed_module()
    module.main()
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert parsed["source_of_truth"] == (
        "Characters/{name}.yaml::voice.few_shots.examples[]"
    )
    assert "Phase 10 rich YAML" in parsed["authority"]
