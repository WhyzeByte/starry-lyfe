"""Regression: SoulEssenceNotFoundError must never be silently caught.

Spec: Docs/_phases/REMEDIATION_2026-04-13.md §1.R-1.1 acceptance criterion:
  "grep the codebase for `except SoulEssenceNotFoundError` and assert
  every match is annotated with a rationale comment."

Per D-1 strict propagation: SoulEssenceNotFoundError MUST propagate
from the point of raise through the full assembly chain to the caller
boundary. Any intermediate try/except in src/ is a future attenuation
point. This test fails loudly if one is introduced without a rationale.

Acceptable rationale pattern: a Python comment on the line immediately
above the except clause that begins with "# SoulEssenceNotFound-catch-rationale:"
explaining why this catch is safe at this boundary.
"""

from __future__ import annotations

from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[3] / "src" / "starry_lyfe"

SENTINEL = "except SoulEssenceNotFoundError"
RATIONALE_PREFIX = "# SoulEssenceNotFound-catch-rationale:"


def test_no_silent_soul_essence_catches_in_src() -> None:
    """Every `except SoulEssenceNotFoundError` in src/ must have a rationale comment above it."""
    offenders: list[tuple[Path, int, str]] = []
    for py_file in SRC_ROOT.rglob("*.py"):
        lines = py_file.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(lines):
            if SENTINEL in line:
                # Find the previous non-blank line
                prev_idx = idx - 1
                while prev_idx >= 0 and not lines[prev_idx].strip():
                    prev_idx -= 1
                prev_line = lines[prev_idx].strip() if prev_idx >= 0 else ""
                if not prev_line.startswith(RATIONALE_PREFIX):
                    offenders.append((py_file, idx + 1, line.strip()))

    assert not offenders, (
        f"Found {len(offenders)} `{SENTINEL}` without rationale comments:\n"
        + "\n".join(f"  {p}:{ln} -- {src}" for p, ln, src in offenders)
        + f"\n\nEach catch must have a `{RATIONALE_PREFIX} ...` comment on the "
        f"line immediately above explaining why this boundary catch is safe. "
        f"Per REMEDIATION_2026-04-13.md D-1 strict propagation."
    )
