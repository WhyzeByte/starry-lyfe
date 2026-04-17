"""Phase 10.7 — Dreams Consistency QA sub-package.

Houses the sixth Dreams generator (the consistency QA judge), its prompt
builder, the per-relationship enumeration, the pin/unpin/check-pinned
interface over ``dyad_state_pins``, the 3-night auto-promotion heuristic,
the weekly digest builder, and the per-relationship episodic memory
lookup helper.

The generator itself lives at ``../generators/consistency_qa.py`` so it
sits alongside the other 5 Dreams generators; this sub-package holds the
infrastructure the generator (and Phase 9 evaluator pin-consult) needs.
"""

from .schemas import (
    ConsistencyQAOutput,
    Contradiction,
    QAVerdict,
    RelationshipCheck,
)

__all__ = [
    "ConsistencyQAOutput",
    "Contradiction",
    "QAVerdict",
    "RelationshipCheck",
]
