"""Alicia away-mode communication_mode sampling (Phase A'' retroactive).

When Alicia is away on consular operation (``life_state.is_away=True``),
all Dreams-generated content that references her speech or presence is
tagged with a ``communication_mode`` value sampled from her canonical
distribution in ``routines.yaml``.

The sampling is seeded deterministically per (run_id, character_id,
output_kind) so a Dreams pass produces stable tags that can be
reproduced in tests without pinning random state globally.
"""

from __future__ import annotations

import hashlib
import uuid

from ..canon.routines_loader import get_alicia_communication_distribution


def pick_alicia_communication_mode(
    run_id: uuid.UUID, output_kind: str
) -> str:
    """Return a stable communication_mode for Alicia-away Dreams output.

    Sampling is keyed by (run_id, output_kind) so every artifact produced
    for a given Dreams pass gets a consistent tag, and two passes with
    the same inputs produce the same tag.

    Args:
        run_id: the Dreams pass run_id (stable per pass).
        output_kind: the generator kind ("diary", "activity", etc.)
            so different artifacts in one pass can land on different
            modes if the distribution favors that.

    Returns:
        One of "phone", "letter", "video_call".
    """
    dist = get_alicia_communication_distribution()
    # Normalize (defensive; schema allows slight drift away from 1.0).
    total = sum(dist.values())
    if total <= 0:
        return "phone"
    normalized = {k: v / total for k, v in dist.items()}

    # Deterministic [0,1) sample from (run_id, output_kind) hash.
    seed = f"{run_id}:{output_kind}".encode()
    digest = hashlib.sha256(seed).hexdigest()
    u = int(digest[:16], 16) / float(1 << 64)

    cumulative = 0.0
    for mode in ("phone", "letter", "video_call"):
        cumulative += normalized.get(mode, 0.0)
        if u < cumulative:
            return mode
    return "phone"  # defensive fallback


def should_tag_alicia_away(character_id: str, life_state_is_away: bool) -> bool:
    """Return True when Dreams output for ``character_id`` requires a
    communication_mode tag.

    Applies only to Alicia, and only when she is currently away.
    Non-Alicia characters never need the tag (their
    ``life_state.is_away`` is permanently False per schema convention).
    """
    return character_id == "alicia" and life_state_is_away
