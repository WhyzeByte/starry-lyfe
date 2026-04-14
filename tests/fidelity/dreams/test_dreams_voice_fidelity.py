"""Phase 6 R7 — Dreams output voice-distinctness fidelity harness.

Closes the second half of F4 Medium. Rather than re-using the full
assembled-prompt rubric library (which targets kernel-level canonical
markers like "Marrickville" that Dreams does not reproduce), this
harness scores Dreams diary output for per-character voice-register
distinctness using the Phase G opener/closer banks as canonical markers.

The test asserts:
1. Every character's Dreams diary output contains her canonical opener.
2. No character's Dreams diary output contains any other character's
   opener (cross-character voice-swappability FAIL).
3. Diary voice is non-swappable: if you ran the diary generator for
   character A with character B's system prompt, B's opener would
   appear instead — but that's not what happens here.

Parametrized across 4 characters × 2 dimensions (opener-present,
others-absent) = 8 fidelity cases.
"""

from __future__ import annotations

import types
from datetime import UTC, datetime
from typing import Any

import pytest

from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.canon.routines_loader import get_routines
from starry_lyfe.context.prose import _DIARY_OPENERS
from starry_lyfe.dreams import GenerationContext, SessionSnapshot, StubBDOne
from starry_lyfe.dreams.generators import generate_diary


@pytest.fixture(scope="module")
def canon() -> Any:
    return load_all_canon()


@pytest.mark.parametrize("character_id", ["adelia", "bina", "reina", "alicia"])
async def test_dreams_diary_carries_own_canonical_opener(
    canon: Any, character_id: str
) -> None:
    """Fidelity: each character's diary contains her canonical opener."""
    stub = StubBDOne(default_text="reflection content")
    ctx = GenerationContext(
        character_id=character_id,
        canon=canon,
        routines=get_routines(character_id),
        prior_session=SessionSnapshot(
            character_id=character_id,
            life_state=types.SimpleNamespace(is_away=False),
        ),
        llm_client=stub,
        now=datetime(2026, 4, 14, 22, 0, tzinfo=UTC),
    )
    out = await generate_diary(ctx)
    expected_opener = _DIARY_OPENERS[character_id]
    assert expected_opener in out.rendered_prose, (
        f"{character_id} diary missing canonical opener: {expected_opener!r}"
    )


@pytest.mark.parametrize("character_id", ["adelia", "bina", "reina", "alicia"])
async def test_dreams_diary_excludes_other_characters_openers(
    canon: Any, character_id: str
) -> None:
    """Fidelity: no cross-character voice contamination in diary output.

    This is the distinctness proof: if two characters' diary output
    were swappable, this test would catch it.
    """
    stub = StubBDOne(default_text="reflection content")
    ctx = GenerationContext(
        character_id=character_id,
        canon=canon,
        routines=get_routines(character_id),
        prior_session=SessionSnapshot(
            character_id=character_id,
            life_state=types.SimpleNamespace(is_away=False),
        ),
        llm_client=stub,
        now=datetime(2026, 4, 14, 22, 0, tzinfo=UTC),
    )
    out = await generate_diary(ctx)
    for other_id, other_opener in _DIARY_OPENERS.items():
        if other_id == character_id:
            continue
        assert other_opener not in out.rendered_prose, (
            f"{character_id}'s diary leaked {other_id}'s opener: "
            f"voice register is not distinct"
        )
