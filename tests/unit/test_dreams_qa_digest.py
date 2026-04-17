"""Phase 10.7 unit tests — weekly digest builder.

Synthesizes 7 daily ledger files in a tmp dir, points the digest module
at it, and verifies trajectory labels + counts come out correctly.
"""

from __future__ import annotations

import re
import shutil
import uuid
from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from starry_lyfe.dreams.consistency import digest as digest_mod


def _repo_local_scratch() -> Path:
    root = Path(__file__).resolve().parents[2] / ".test_tmp"
    root.mkdir(exist_ok=True)
    path = root / f"qa_digest_{uuid.uuid4().hex}"
    path.mkdir()
    return path


@pytest.fixture
def repo_tmp_path() -> Generator[Path, None, None]:
    """Repo-local scratch dir, auto-cleaned. Avoids %TEMP% ACL fault."""
    path = _repo_local_scratch()
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def _write_daily(
    tmp_dir,
    *,
    date: datetime,
    healthy: list[str] | None = None,
    drift: list[str] | None = None,
    contradiction: list[str] | None = None,
) -> None:
    """Author one daily ledger file with the given verdict bullets per section."""
    healthy = healthy or []
    drift = drift or []
    contradiction = contradiction or []
    body = (
        f"# Dreams Consistency QA — {date.strftime('%Y-%m-%d')}\n\n"
        "## Healthy\n\n"
        + "".join(f"- **{k}**\n  - synthetic\n" for k in healthy)
        + "\n## Drift watch\n\n"
        + "".join(f"- **{k}**\n  - synthetic\n" for k in drift)
        + "\n## Operator review required\n\n"
        + "".join(f"- **{k}**\n  - synthetic\n" for k in contradiction)
        + "\n"
    )
    (tmp_dir / f"{date.strftime('%Y-%m-%d')}_consistency.md").write_text(
        body, encoding="utf-8"
    )


@pytest.fixture
def patched_dirs(repo_tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    """Redirect the digest module at a repo-local tmp dir for both daily + weekly outputs."""
    daily = repo_tmp_path / "daily"
    weekly = repo_tmp_path / "weekly"
    daily.mkdir()
    weekly.mkdir()
    monkeypatch.setattr(digest_mod, "_DAILY_DIR", daily)
    monkeypatch.setattr(digest_mod, "_WEEKLY_DIR", weekly)
    return daily, weekly


def test_build_weekly_emits_full_relationship_slate(patched_dirs) -> None:
    daily, weekly = patched_dirs
    now = datetime(2026, 4, 17, 3, 0, 0, tzinfo=UTC)
    # No daily files at all — digest still lists all 10 relationships as stable.
    out_path = digest_mod.build_weekly(now=now)
    text = out_path.read_text(encoding="utf-8")
    for key in (
        "adelia_bina",
        "adelia_reina",
        "adelia_alicia",
        "bina_reina",
        "bina_alicia",
        "reina_alicia",
        "whyze_adelia",
        "whyze_bina",
        "whyze_reina",
        "whyze_alicia",
    ):
        assert f"`{key}`" in text


def test_build_weekly_labels_drifting_when_window_worse_than_prior(patched_dirs) -> None:
    daily, weekly = patched_dirs
    now = datetime(2026, 4, 17, 3, 0, 0, tzinfo=UTC)
    # Prior week (days 8-14): 0 drift. This week (days 1-7): 3 drift on adelia_bina.
    for offset in (1, 2, 3):
        _write_daily(daily, date=now - timedelta(days=offset), drift=["adelia_bina"])
    out_path = digest_mod.build_weekly(now=now)
    text = out_path.read_text(encoding="utf-8")
    # Expect adelia_bina row labeled "drifting" with non-zero drift count.
    row_match = re.search(r"\| `adelia_bina` \| (\w+) \| (\d+) / (\d+) / (\d+) \|", text)
    assert row_match is not None
    label, healthy, drift, contradiction = row_match.groups()
    assert label == "drifting"
    assert int(drift) == 3


def test_build_weekly_labels_improving_when_window_better_than_prior(patched_dirs) -> None:
    daily, weekly = patched_dirs
    now = datetime(2026, 4, 17, 3, 0, 0, tzinfo=UTC)
    # Prior week: 3 drift on bina_reina; this week: 0 drift.
    for offset in (8, 9, 10):
        _write_daily(daily, date=now - timedelta(days=offset), drift=["bina_reina"])
    out_path = digest_mod.build_weekly(now=now)
    text = out_path.read_text(encoding="utf-8")
    row_match = re.search(r"\| `bina_reina` \| (\w+) \| (\d+) / (\d+) / (\d+) \|", text)
    assert row_match is not None
    label, _, drift, _ = row_match.groups()
    assert label == "improving"
    assert int(drift) == 0


def test_build_weekly_labels_stable_when_window_equal(patched_dirs) -> None:
    daily, weekly = patched_dirs
    now = datetime(2026, 4, 17, 3, 0, 0, tzinfo=UTC)
    # 1 drift this week + 1 drift prior week → stable.
    _write_daily(daily, date=now - timedelta(days=1), drift=["whyze_alicia"])
    _write_daily(daily, date=now - timedelta(days=8), drift=["whyze_alicia"])
    out_path = digest_mod.build_weekly(now=now)
    text = out_path.read_text(encoding="utf-8")
    row_match = re.search(r"\| `whyze_alicia` \| (\w+) \|", text)
    assert row_match is not None
    assert row_match.group(1) == "stable"


def test_build_weekly_filename_uses_iso_week(patched_dirs) -> None:
    _, weekly = patched_dirs
    now = datetime(2026, 4, 17, 3, 0, 0, tzinfo=UTC)
    out_path = digest_mod.build_weekly(now=now)
    iso_year, iso_week, _ = now.isocalendar()
    assert out_path.name == f"{iso_year}-W{iso_week:02d}.md"
