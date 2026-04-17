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
import os
import sys
from collections.abc import Callable, Iterator
from contextlib import contextmanager, suppress
from datetime import UTC, datetime
from pathlib import Path
from typing import IO

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


@contextmanager
def _file_lock(handle: IO[str]) -> Iterator[None]:
    """Cross-platform exclusive file lock for the duration of the block.

    Phase 10.7 F2 remediation: defends ``_emit_markdown`` against the
    read-modify-write race that could clobber a verdict when two Dreams
    runs collide on the same UTC date (cron jitter, manual replay,
    systemd retry). Uses ``msvcrt.locking`` on Windows and ``fcntl.flock``
    on POSIX. Falls back to a no-op if neither module is importable
    (very old or stripped-down Python builds) — a warning is logged but
    no exception is raised, preserving the best-effort dispatcher
    contract.
    """
    if sys.platform == "win32":
        try:
            import msvcrt

            # LK_LOCK blocks until the lock is acquired. Lock 1 byte at the
            # current position; on Windows the byte range is enough to
            # serialize concurrent writers.
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                # Re-position to the byte we locked before unlocking.
                handle.seek(0)
                with suppress(OSError):
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            return
        except (ImportError, OSError) as exc:
            logger.warning(
                "dreams_qa_markdown_lock_unavailable",
                extra={"platform": sys.platform, "error": str(exc)},
            )
            yield
            return
    try:
        import fcntl

        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    except (ImportError, OSError) as exc:
        logger.warning(
            "dreams_qa_markdown_lock_unavailable",
            extra={"platform": sys.platform, "error": str(exc)},
        )
        yield


def _render_entry(
    relationship_key: str,
    divergence_summary: str,
    contradictions: list[Contradiction],
) -> str:
    """Render the markdown bullet for a single verdict entry."""
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
    return "\n".join(line for line in entry_lines if line) + "\n"


def _emit_markdown(
    verdict: QAVerdict,
    relationship_key: str,
    divergence_summary: str,
    contradictions: list[Contradiction],
    *,
    now: datetime | None = None,
) -> None:
    """Append a verdict entry to the daily markdown ledger.

    Phase 10.7 F2: the read-modify-write critical section is wrapped in
    ``_file_lock`` so two concurrent Dreams runs on the same UTC date
    serialize cleanly instead of clobbering each other.
    """
    path = _daily_file_path(now)
    _ensure_daily_file(path)
    section_header = _VERDICT_SECTION_HEADER[verdict]
    entry = _render_entry(relationship_key, divergence_summary, contradictions)
    insertion_marker = section_header + "\n\n"

    # Open r+ so we can lock the file handle while doing read-modify-write.
    # New file is guaranteed to exist (created by _ensure_daily_file).
    with path.open("r+", encoding="utf-8") as handle, _file_lock(handle):
        # Re-read inside the lock — another writer may have appended
        # between _ensure_daily_file and this point.
        handle.seek(0)
        text = handle.read()
        if section_header not in text:
            text += f"\n{section_header}\n\n"
        if insertion_marker in text:
            text = text.replace(insertion_marker, insertion_marker + entry, 1)
        else:
            text = text.rstrip() + f"\n\n{section_header}\n\n{entry}"
        handle.seek(0)
        handle.truncate()
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())


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
