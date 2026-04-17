"""Phase 10.7 — weekly Dreams Consistency QA digest.

Reads the last 7 daily ``Docs/_dreams_qa/YYYY-MM-DD_consistency.md``
files and emits a single weekly summary at
``Docs/_dreams_qa/_weekly/YYYY-WW.md`` (ISO week numbering) listing
each of the 10 relationships with a trajectory label:

- ``improving`` — fewer concerning/contradiction verdicts than the
  prior 7-day window
- ``stable`` — verdict mix unchanged
- ``drifting`` — more concerning/contradiction verdicts than the prior
  7-day window

The digest is the operator's weekly canon-coherence dashboard.
"""

from __future__ import annotations

import logging
import re
from collections import Counter
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .relationships import enumerate_inter_woman_dyads

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
_DAILY_DIR = _REPO_ROOT / "Docs" / "_dreams_qa"
_WEEKLY_DIR = _DAILY_DIR / "_weekly"

# Relationship keys appear in daily files as ``- **<key>**`` bullets.
_KEY_BULLET_RE = re.compile(r"^- \*\*([a-z_]+)\*\*", re.MULTILINE)
# Section headers per notifications._VERDICT_SECTION_HEADER.
_SECTION_HEADERS: dict[str, str] = {
    "healthy_divergence": "## Healthy",
    "concerning_drift": "## Drift watch",
    "factual_contradiction": "## Operator review required",
}
_DRIFT_VERDICTS = ("concerning_drift", "factual_contradiction")


def _classify_section(text: str, section_header: str) -> set[str]:
    """Extract the set of relationship_keys appearing under ``section_header``."""
    if section_header not in text:
        return set()
    after = text.split(section_header, 1)[1]
    # Stop at the next ``## `` or end-of-file.
    end = after.find("\n## ")
    body = after[:end] if end != -1 else after
    return set(_KEY_BULLET_RE.findall(body))


def _aggregate_window(daily_files: list[Path]) -> dict[str, Counter[str]]:
    """For each daily file, classify each relationship's verdict.

    Returns ``{relationship_key: Counter({verdict: count, ...}), ...}``.
    Counts are per-day, so a relationship flagged 3 days running with
    concerning_drift gives Counter({'concerning_drift': 3}).
    """
    out: dict[str, Counter[str]] = {}
    for path in daily_files:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for verdict, header in _SECTION_HEADERS.items():
            keys_here = _classify_section(text, header)
            for key in keys_here:
                out.setdefault(key, Counter())[verdict] += 1
    return out


def _drift_score(counts: Counter[str]) -> int:
    """Sum of concerning + contradiction verdicts in the window."""
    return sum(counts.get(v, 0) for v in _DRIFT_VERDICTS)


def _trajectory_label(this_score: int, prior_score: int) -> str:
    """Compare drift scores between current and prior 7-day windows."""
    if this_score > prior_score:
        return "drifting"
    if this_score < prior_score:
        return "improving"
    return "stable"


def _daily_files_in_range(start: datetime, end: datetime) -> list[Path]:
    """Return existing daily ledger files in [start, end) sorted by date."""
    if not _DAILY_DIR.exists():
        return []
    out: list[Path] = []
    cur = start
    while cur < end:
        candidate = _DAILY_DIR / f"{cur.strftime('%Y-%m-%d')}_consistency.md"
        if candidate.exists():
            out.append(candidate)
        cur += timedelta(days=1)
    return out


def build_weekly(now: datetime | None = None) -> Path:
    """Build the weekly digest for the ISO week containing ``now``.

    Reads the last 7 days of daily ledgers + the prior 7 days for the
    trajectory comparison. Emits the markdown digest and returns its path.
    Idempotent: re-running the same week overwrites the digest.
    """
    ref = now if now is not None else datetime.now(UTC)
    iso_year, iso_week, _ = ref.isocalendar()

    this_end = ref
    this_start = ref - timedelta(days=7)
    prior_end = this_start
    prior_start = this_start - timedelta(days=7)

    this_files = _daily_files_in_range(this_start, this_end)
    prior_files = _daily_files_in_range(prior_start, prior_end)

    this_counts = _aggregate_window(this_files)
    prior_counts = _aggregate_window(prior_files)

    # All 10 relationship keys (so the digest always shows the full slate).
    inter_woman_keys = [r.relationship_key for r in enumerate_inter_woman_dyads()]
    woman_whyze_keys = [f"whyze_{c}" for c in ("adelia", "bina", "reina", "alicia")]
    all_keys = inter_woman_keys + woman_whyze_keys

    rows: list[str] = []
    for key in all_keys:
        this_c = this_counts.get(key, Counter())
        prior_c = prior_counts.get(key, Counter())
        traj = _trajectory_label(_drift_score(this_c), _drift_score(prior_c))
        rows.append(
            f"| `{key}` | {traj} | "
            f"{this_c.get('healthy_divergence', 0)} / "
            f"{this_c.get('concerning_drift', 0)} / "
            f"{this_c.get('factual_contradiction', 0)} |"
        )

    digest_text = (
        f"# Dreams Consistency QA — Weekly Digest {iso_year}-W{iso_week:02d}\n"
        f"\n"
        f"Window: {this_start.strftime('%Y-%m-%d')} → {this_end.strftime('%Y-%m-%d')} "
        f"(7 days; comparing against prior 7 days {prior_start.strftime('%Y-%m-%d')} → "
        f"{prior_end.strftime('%Y-%m-%d')})\n"
        f"\n"
        f"Verdict counts in the window are healthy / drift / contradiction.\n"
        f"\n"
        f"| Relationship | Trajectory | Counts (healthy / drift / contradiction) |\n"
        f"|---|---|---|\n"
        + "\n".join(rows)
        + "\n"
    )

    _WEEKLY_DIR.mkdir(parents=True, exist_ok=True)
    out_path = _WEEKLY_DIR / f"{iso_year}-W{iso_week:02d}.md"
    out_path.write_text(digest_text, encoding="utf-8")
    logger.info(
        "dreams_qa_weekly_digest_written",
        extra={
            "path": str(out_path),
            "iso_year": iso_year,
            "iso_week": iso_week,
            "daily_files_in_window": len(this_files),
        },
    )
    return out_path


__all__ = ["build_weekly"]
