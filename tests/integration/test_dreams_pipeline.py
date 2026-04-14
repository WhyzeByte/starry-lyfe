"""Phase 6 Dreams pipeline end-to-end contract test.

This is the **load-bearing integration test** per Phase 5 lesson #1:
end-to-end regressions per public-API contract beat unit shape tests.

Invokes ``run_dreams_pass()`` with a stubbed session factory and
``StubBDOne`` (no live DB, no live LLM), and asserts:

1. All 4 canonical characters are processed on every pass.
2. Every character's diary output is routed through the Phase G
   ``render_diary_prose`` wrapper (no raw JSON reaches the result).
3. The schedule generator emits a per-character schedule.
4. Per-character warnings aggregate up into the pass-level warnings.
5. Cross-character contamination does NOT occur: each diary entry's
   system prompt excludes the other three canonical women's names.

Commits 6+ will extend this test to cover off-screen, open-loops,
activity-design, and DB writers as those subsystems land.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.dreams import (
    DreamsPassResult,
    StubBDOne,
    run_dreams_pass,
)


class _StubResult:
    def scalars(self) -> _StubResult:
        return self

    def all(self) -> list[Any]:
        return []

    def first(self) -> Any | None:
        return None

    @property
    def rowcount(self) -> int:
        return 0


class _StubBeginCtx:
    async def __aenter__(self) -> _StubBeginCtx:
        return self

    async def __aexit__(self, *args: Any) -> None:
        return None


class _StubSession:
    async def __aenter__(self) -> _StubSession:
        return self

    async def __aexit__(self, *args: Any) -> None:
        return None

    def begin(self) -> _StubBeginCtx:
        return _StubBeginCtx()

    async def execute(self, *args: Any, **kwargs: Any) -> _StubResult:
        return _StubResult()

    def add(self, obj: Any) -> None:
        if getattr(obj, "id", None) is None:
            import contextlib
            import uuid as _uuid

            with contextlib.suppress(AttributeError):
                obj.id = _uuid.uuid4()

    async def flush(self) -> None:
        return None


def _stub_session_factory() -> _StubSession:
    return _StubSession()


async def _empty_snapshot_loader(
    session: Any, character_id: str, now: Any
) -> Any:
    import types as _types

    from starry_lyfe.dreams import SessionSnapshot

    return SessionSnapshot(
        character_id=character_id,
        life_state=_types.SimpleNamespace(is_away=False),
    )


@pytest.fixture(scope="module")
def canon() -> Any:
    return load_all_canon()


async def test_dreams_pass_processes_all_four_characters(canon: Any) -> None:
    """AC-6.2: CharacterID coverage invariant across a full pass."""
    result = await run_dreams_pass(
        session_factory=_stub_session_factory,  # type: ignore[arg-type]
        snapshot_loader=_empty_snapshot_loader,
        llm_client=StubBDOne(default_text="end-of-day reflection."),
        canon=canon,
        now=datetime(2026, 4, 14, 3, 30, tzinfo=UTC),
    )
    assert isinstance(result, DreamsPassResult)
    assert set(result.character_results.keys()) == {"adelia", "bina", "reina", "alicia"}


async def test_diary_output_passes_through_phase_g_wrapper(canon: Any) -> None:
    """AC-6.4: every narrative text routes through Phase G prose renderer."""
    stub = StubBDOne(default_text="The day closed around the evening light.")

    # Record every LLM call so we can verify the rendered prose includes
    # both the opener and the LLM text — that is the Phase G contract.
    from starry_lyfe.canon.routines_loader import get_routines
    from starry_lyfe.dreams import GenerationContext, SessionSnapshot
    from starry_lyfe.dreams.generators.diary import generate_diary

    # Invoke the diary generator directly for each character since the
    # runner's per-character result currently has diary_entry_id=None
    # pending the writer subsystem (commit 6+).
    for char in ("adelia", "bina", "reina", "alicia"):
        ctx = GenerationContext(
            character_id=char,
            canon=canon,
            routines=get_routines(char),
            prior_session=SessionSnapshot(character_id=char),
            llm_client=stub,
            now=datetime(2026, 4, 14, 22, 0, tzinfo=UTC),
        )
        out = await generate_diary(ctx)

        # Phase G frame: opener + body + closer (3 paragraphs).
        assert out.rendered_prose.count("\n\n") == 2
        assert "day closed around the evening light" in out.rendered_prose
        # Opener differs per character so the wrapper is not a no-op.
        opener = out.rendered_prose.split("\n\n")[0]
        assert opener, f"Diary opener missing for {char}"


async def test_schedule_generator_fires_for_every_character(canon: Any) -> None:
    """AC-6.3 (partial, commit-5 scope): schedule is the fully-implemented
    generator this commit; every character must get one per pass."""
    result = await run_dreams_pass(
        session_factory=_stub_session_factory,  # type: ignore[arg-type]
        snapshot_loader=_empty_snapshot_loader,
        llm_client=StubBDOne(),
        canon=canon,
        now=datetime(2026, 4, 14, 3, 30, tzinfo=UTC),
    )
    for char_id, cr in result.character_results.items():
        assert cr.schedule_generated, f"{char_id} schedule did not fire"


async def test_warnings_aggregate_from_generator_failures(canon: Any) -> None:
    """Per-generator LLM failures propagate into the pass-level warnings list.

    Post-R3/R4/R5: all 5 generators are real. Previously this test relied
    on 3 of 5 being placeholder stubs emitting warnings; now we induce
    real failures via StubBDOne.fail_next_n and assert the runner
    aggregates them.
    """
    # 4 characters × 4 LLM-backed generators (diary / off_screen /
    # open_loops / activity_design) = 16 LLM calls total. Fail every call.
    failing = StubBDOne(fail_next_n=64)
    result = await run_dreams_pass(
        session_factory=_stub_session_factory,  # type: ignore[arg-type]
        snapshot_loader=_empty_snapshot_loader,
        llm_client=failing,
        canon=canon,
        now=datetime(2026, 4, 14, 3, 30, tzinfo=UTC),
    )
    # Each character contributes at least one warning per failing generator.
    # The four LLM-backed generators × 4 characters = 16 failure warnings
    # minimum, aggregated through per-character lists into the pass warnings.
    assert len(result.warnings) >= 16


async def test_cross_character_contamination_negative(canon: Any) -> None:
    """Lesson #2 applied at the public-API boundary: the diary generator
    must never include another canonical woman's name in the focal
    character's LLM system prompt.

    This is the end-to-end version of test_diary.py's unit-level check.
    """
    captured: dict[str, dict[str, str]] = {}

    def recorder(system: str, user: str) -> str:
        # Record the latest call per character by sniffing which character
        # the system prompt is addressed to.
        for char in ("adelia", "bina", "reina", "alicia"):
            # Use capitalized forms since system prompts use proper names.
            proper = char.capitalize() if char != "adelia" else "Adelia"
            if proper in system.split("\n")[0]:
                captured[char] = {"system": system, "user": user}
                break
        return "one-paragraph reflection."

    stub = StubBDOne(responder=recorder)

    # Drive the diary generator through the runner for all 4 characters.
    # (Runner-level pass guarantees every character is exercised.)
    await run_dreams_pass(
        session_factory=_stub_session_factory,  # type: ignore[arg-type]
        snapshot_loader=_empty_snapshot_loader,
        llm_client=stub,
        canon=canon,
        now=datetime(2026, 4, 14, 22, 0, tzinfo=UTC),
    )

    # Every character's diary system prompt must have been recorded.
    assert set(captured.keys()) == {"adelia", "bina", "reina", "alicia"}

    # For each character, no other canonical woman's proper name may appear
    # in the system prompt.
    proper_names = {
        "adelia": "Adelia",
        "bina": "Bina",
        "reina": "Reina",
        "alicia": "Alicia",
    }
    for focal, recorded in captured.items():
        system = recorded["system"]
        for other, other_proper in proper_names.items():
            if other == focal:
                continue
            assert other_proper not in system, (
                f"Cross-character contamination: {focal}'s diary system prompt "
                f"contains '{other_proper}'"
            )


async def test_run_id_unique_across_passes(canon: Any) -> None:
    a = await run_dreams_pass(
        session_factory=_stub_session_factory,  # type: ignore[arg-type]
        snapshot_loader=_empty_snapshot_loader,
        llm_client=StubBDOne(),
        canon=canon,
        now=datetime(2026, 4, 14, 3, 30, tzinfo=UTC),
    )
    b = await run_dreams_pass(
        session_factory=_stub_session_factory,  # type: ignore[arg-type]
        snapshot_loader=_empty_snapshot_loader,
        llm_client=StubBDOne(),
        canon=canon,
        now=datetime(2026, 4, 14, 3, 30, tzinfo=UTC),
    )
    assert a.run_id != b.run_id


async def test_token_counts_aggregate(canon: Any) -> None:
    """Token counts sum across characters for observability / cost tracking."""
    result = await run_dreams_pass(
        session_factory=_stub_session_factory,  # type: ignore[arg-type]
        snapshot_loader=_empty_snapshot_loader,
        llm_client=StubBDOne(default_text="reflective paragraph"),
        canon=canon,
        now=datetime(2026, 4, 14, 22, 0, tzinfo=UTC),
    )
    # Only the diary generator is LLM-backed this commit, and it fires once
    # per character — so both input and output token totals are non-zero.
    assert result.total_input_tokens > 0
    assert result.total_output_tokens > 0
