"""Context-layer custom exceptions."""

from __future__ import annotations


class KernelCompilationError(Exception):
    """A kernel section cannot fit within its token budget.

    This is an authoring problem (the section's irreducible content
    exceeds the available budget) rather than a runtime problem.
    """
