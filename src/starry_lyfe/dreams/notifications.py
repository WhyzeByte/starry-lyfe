"""Phase 10.7 — structured QA event emitter.

One entry point — ``emit_qa_event()`` — dispatches each consistency QA
verdict to two destinations:

1. **MSE-6 structlog**: INFO for healthy_divergence, WARNING for
   concerning_drift, ERROR for factual_contradiction. Carries
   relationship_key + verdict + summary as structured fields so the
   ops dashboard / log aggregator can filter by severity.

2. **Daily markdown ledger**: appends to
   ``Docs/_dreams_qa/YYYY-MM-DD_consistency.md`` with three sections —
   Healthy / Drift watch / Operator review required. The operator reads
   the daily file as their morning canon-coherence summary.

The module is extensible — future webhook/email destinations slot into
``_DISPATCHERS`` as additional callables without changing the public API.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from .consistency.schemas import Contradiction, QAVerdict

logger = logging.getLogger(__name__)

# Repo root is 3 levels up from this file (src/starry_lyfe/dreams/notifications.py).
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_DAILY_DIR = _REPO_ROOT / "Docs" / "_dreams_qa"


_VERDICT_LOG_LEVEL: dict[QAVerdict, int] = {
    QAVerdict.HEALTHY_DIVERGENCE: logging.INFO,
    QAVerdict.CONCERNING_DRIFT: logging.WARNING,
    QAVerdict.FACTUAL_CONTRADICTION: logging.ERROR,
}

_VERDICT_SECTION_HEADER: dict[QAVerdict, str] = {
    QAVerdict.HEALTHY_DIVERGENCE: "## Healthy",
    QAVerdict.CONCERNING_DRIFT: "## Drift watch",
    QAVerdict.FACTUAL_CONTRADICTION: "## Operator review required",
}


def _emit_structlog(
    verdict: QAVerdict,
    relationship_key: str,
    divergence_summary: str,
    contradictions: list[Contradiction],
) -> None:
    """Dispatch to MSE-6 structlog at the verdict-appropriate level."""
    level = _VERDICT_LOG_LEVEL[verdict]
    logger.log(
        level,
        "dreams_qa_verdict",
        extra={
            "verdict": verdict.value,
            "relationship_key": relationship_key,
            "divergence_summary": divergence_summary,
            "contradiction_count": len(contradictions),
            "contradicted_fields": [c.field_name for c in contradictions],
        },
    )


def _daily_file_path(now: datetime | None = None) -> Path:
    """Return the markdown ledger path for the given date (UTC)."""
    ref = now if now is not None else datetime.now(UTC)
    return _DAILY_DIR / f"{ref.strftime('%Y-%m-%d')}_consistency.md"


def _ensure_daily_file(path: Path) -> None:
    """Create the daily ledger with a stable section skeleton if missing."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    skeleton = (
        f"# Dreams Consistency QA — {path.stem.replace('_consistency', '')}\n\n"
        "Sections are populated as relationships are judged through the night. Each\n"
        "entry is a single-relationship verdict with the neutral-observer summary\n"
        "and any contradictions surfaced. Operator review required = action needed.\n\n"
        "## Healthy\n\n"
        "## Drift watch\n\n"
        "## Operator review required\n\n"
    )
    path.write_text(skeleton, encoding="utf-8")


def _emit_markdown(
    verdict: QAVerdict,
    relationship_key: str,
    divergence_summary: str,
    contradictions: list[Contradiction],
    *,
    now: datetime | None = None,
) -> None:
    """Append a verdict entry to the daily markdown ledger."""
    path = _daily_file_path(now)
    _ensure_daily_file(path)
    text = path.read_text(encoding="utf-8")
    section_header = _VERDICT_SECTION_HEADER[verdict]
    if section_header not in text:
        # Schema drift; append to end as fallback rather than crash.
        text += f"\n{section_header}\n\n"
    entry_lines: list[str] = [
        f"- **{relationship_key}**",
        f"  - {divergence_summary}" if divergence_summary else "",
    ]
    if contradictions:
        entry_lines.append("  - Contradictions:")
        for c in contradictions:
            pov_str = f" ({c.pov_character_id})" if c.pov_character_id else ""
            entry_lines.append(
                f"    - `{c.field_name}`{pov_str}: observed {c.observed_value!r} "
                f"vs canonical {c.canonical_value!r} ({c.shared_canon_field})"
            )
    entry = "\n".join(line for line in entry_lines if line) + "\n"

    # Insert the entry RIGHT AFTER the section header, preserving the rest.
    insertion_marker = section_header + "\n\n"
    if insertion_marker in text:
        text = text.replace(insertion_marker, insertion_marker + entry, 1)
    else:
        # Fallback: append to end.
        text = text.rstrip() + f"\n\n{section_header}\n\n{entry}"
    path.write_text(text, encoding="utf-8")


# Public dispatcher table — extensible. Add (callable, name) tuples here for
# future webhook/email destinations; each callable takes the same kwargs as
# ``emit_qa_event``.
_DISPATCHERS: list[Callable[..., None]] = [_emit_structlog, _emit_markdown]


def emit_qa_event(
    *,
    verdict: QAVerdict,
    relationship_key: str,
    divergence_summary: str,
    contradictions: list[Contradiction],
    now: datetime | None = None,
) -> None:
    """Dispatch a single relationship's QA verdict to all configured destinations.

    Called once per relationship by the consistency_qa generator. Best-effort
    dispatch — a failure in one destination does not block the others.
    """
    for dispatcher in _DISPATCHERS:
        try:
            # Each dispatcher signature accepts the same kwargs; markdown also
            # accepts ``now`` for deterministic test fixtures.
            dispatcher(
                verdict,
                relationship_key,
                divergence_summary,
                contradictions,
                now=now,
            ) if dispatcher is _emit_markdown else dispatcher(
                verdict, relationship_key, divergence_summary, contradictions
            )
        except Exception as exc:  # noqa: BLE001 — dispatch must not fail-loud
            logger.warning(
                "dreams_qa_dispatch_failed",
                extra={
                    "dispatcher": dispatcher.__name__,
                    "relationship_key": relationship_key,
                    "verdict": verdict.value,
                    "error": str(exc),
                },
            )


__all__ = ["emit_qa_event"]
