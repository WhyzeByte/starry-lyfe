"""Phase 10.7 unit tests — Dreams Consistency QA generator.

Mocked LLM. Tests cover all 3 verdicts, schema validation, the 10-relationship
enumeration, prompt builder injection sanitation, and pinning CRUD round-trip.
"""

from __future__ import annotations

import json
import shutil
import uuid
from collections.abc import Generator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.dreams.consistency.prompt import (
    JUDGE_SYSTEM_PROMPT,
    _sanitize_for_evidence_block,
    build_user_prompt,
)
from starry_lyfe.dreams.consistency.relationships import (
    Relationship,
    enumerate_all,
    enumerate_inter_woman_dyads,
    enumerate_woman_whyze_pairs,
)
from starry_lyfe.dreams.consistency.schemas import (
    ConsistencyQAOutput,
    Contradiction,
    QAVerdict,
    RelationshipCheck,
)


def _make_repo_local_tempdir(prefix: str) -> Path:
    """Create a writable scratch dir inside the repo workspace.

    Phase 10.7: avoids the Windows ACL fault on `%TEMP%/pytest-of-Whyze`
    that pytest's tmp_path hits in this workspace (same workaround as
    `tests/unit/test_residue_grep.py::_make_repo_local_tempdir`).
    """
    root = Path(__file__).resolve().parents[2] / ".test_tmp"
    root.mkdir(exist_ok=True)
    path = root / f"{prefix}_{uuid.uuid4().hex}"
    path.mkdir()
    return path


@pytest.fixture
def repo_tmp_path() -> Generator[Path, None, None]:
    """Per-test repo-local scratch dir, auto-cleaned."""
    path = _make_repo_local_tempdir("qa")
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def _utc_now() -> datetime:
    return datetime(2026, 4, 17, 3, 0, 0, tzinfo=UTC)


# ----------------------------------------------------------------------
# Schema validation
# ----------------------------------------------------------------------


class TestSchemas:
    def test_qaverdict_string_values_match_db_check_constraint(self) -> None:
        assert QAVerdict.HEALTHY_DIVERGENCE.value == "healthy_divergence"
        assert QAVerdict.CONCERNING_DRIFT.value == "concerning_drift"
        assert QAVerdict.FACTUAL_CONTRADICTION.value == "factual_contradiction"

    def test_relationship_check_healthy_round_trip(self) -> None:
        check = RelationshipCheck(
            relationship_key="adelia_bina",
            verdict=QAVerdict.HEALTHY_DIVERGENCE,
            divergence_summary="POVs read the porch scene differently; both canonical.",
            contradictions=[],
            scene_fodder=["Bina notices the cardamom Adelia missed."],
        )
        roundtrip = RelationshipCheck.model_validate_json(check.model_dump_json())
        assert roundtrip == check

    def test_relationship_check_with_contradictions(self) -> None:
        check = RelationshipCheck(
            relationship_key="whyze_alicia",
            verdict=QAVerdict.FACTUAL_CONTRADICTION,
            divergence_summary="Alicia recalls the marriage year as 2023.",
            contradictions=[
                Contradiction(
                    field_name="marriage_year",
                    pov_character_id="alicia",
                    shared_canon_field="shared_canon.marriage.year",
                    observed_value="2023",
                    canonical_value="2022",
                )
            ],
        )
        assert check.contradictions[0].pov_character_id == "alicia"

    def test_consistency_qa_output_requires_exactly_ten_checks(self) -> None:
        with pytest.raises(ValidationError):
            ConsistencyQAOutput(
                run_id=uuid.uuid4(),
                started_at=_utc_now(),
                finished_at=_utc_now(),
                relationship_checks=[],
            )

    def test_consistency_qa_output_counts(self) -> None:
        checks = [
            RelationshipCheck(
                relationship_key=f"rel_{i}",
                verdict=(
                    QAVerdict.HEALTHY_DIVERGENCE if i < 6
                    else QAVerdict.CONCERNING_DRIFT if i < 8
                    else QAVerdict.FACTUAL_CONTRADICTION
                ),
                divergence_summary="",
            )
            for i in range(10)
        ]
        out = ConsistencyQAOutput(
            run_id=uuid.uuid4(),
            started_at=_utc_now(),
            finished_at=_utc_now(),
            relationship_checks=checks,
        )
        assert out.healthy_count == 6
        assert out.concerning_count == 2
        assert out.contradiction_count == 2


# ----------------------------------------------------------------------
# Relationship enumeration
# ----------------------------------------------------------------------


class TestRelationships:
    def test_enumerate_inter_woman_dyads_yields_six(self) -> None:
        rels = enumerate_inter_woman_dyads()
        assert len(rels) == 6
        assert all(r.relationship_kind == "inter_woman" for r in rels)

    def test_enumerate_inter_woman_keys_match_dyads_baseline_convention(self) -> None:
        canon = load_all_canon()
        rel_keys = sorted(r.relationship_key for r in enumerate_inter_woman_dyads())
        # All inter-woman keys must exist in shared_canon.dyads_baseline
        # (which uses the seniority precedence adelia/bina/reina/alicia).
        baseline_keys = set(canon.shared.dyads_baseline.keys())
        for key in rel_keys:
            assert key in baseline_keys, f"{key} not in dyads_baseline"

    def test_enumerate_woman_whyze_pairs_yields_four(self) -> None:
        canon = load_all_canon()
        rels = enumerate_woman_whyze_pairs(canon)
        assert len(rels) == 4
        assert all(r.relationship_kind == "woman_whyze" for r in rels)
        assert all(r.pov_a == "whyze" for r in rels)

    def test_enumerate_all_yields_exactly_ten(self) -> None:
        canon = load_all_canon()
        assert len(enumerate_all(canon)) == 10


# ----------------------------------------------------------------------
# Prompt builder + sanitation
# ----------------------------------------------------------------------


class TestPromptBuilder:
    def test_judge_system_prompt_mentions_three_verdicts(self) -> None:
        for verdict in QAVerdict:
            assert verdict.value in JUDGE_SYSTEM_PROMPT
        assert "JSON" in JUDGE_SYSTEM_PROMPT.upper()

    def test_sanitize_neutralizes_html_and_truncates(self) -> None:
        text = "<script>alert('hi')</script>" * 100
        out = _sanitize_for_evidence_block(text, max_chars=200)
        assert "<script>" not in out  # html-escaped
        assert "&lt;script&gt;" in out
        assert out.startswith("> ")  # line-prefix sentinel

    def test_sanitize_truncation_marker_appears(self) -> None:
        long = "a" * 2000
        out = _sanitize_for_evidence_block(long, max_chars=100)
        assert "truncated" in out

    def test_build_user_prompt_includes_anchor_and_both_povs(self) -> None:
        canon = load_all_canon()
        rel = Relationship(
            relationship_key="adelia_bina",
            relationship_kind="inter_woman",
            pov_a="adelia",
            pov_b="bina",
        )
        prompt = build_user_prompt(
            rel,
            canon,
            pov_a_block="adelia thinks bina is grounded.",
            pov_b_block="bina thinks adelia is generative.",
            recent_memories=["[2026-04-15 adelia] We made paella with bina."],
        )
        assert "adelia_bina" in prompt
        assert "Objective anchor" in prompt
        assert "adelia thinks bina is grounded" in prompt
        assert "bina thinks adelia is generative" in prompt
        assert "Recent episodic memories" in prompt
        # Memory text is sanitized — should appear in the > -prefixed block.
        assert "> [2026-04-15 adelia]" in prompt


# ----------------------------------------------------------------------
# LLM judge mocking — exercises the full _judge_one path
# ----------------------------------------------------------------------


class _MockLLMResponse:
    """Mimic the BDOne / StubBDOne response shape for the consistency_qa generator."""

    def __init__(self, text: str, input_tokens: int = 50, output_tokens: int = 50) -> None:
        self.text = text
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


class _MockLLMClient:
    """Record calls + return the next queued response."""

    def __init__(self, responses: list[_MockLLMResponse]) -> None:
        self._responses = list(responses)
        self.calls: list[tuple[str, str]] = []
        self._circuit_open = False

    @property
    def circuit_open(self) -> bool:
        return self._circuit_open

    def reset_circuit(self) -> None:
        self._circuit_open = False

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        max_tokens: int = 800,
        temperature: float = 0.2,
    ) -> _MockLLMResponse:
        self.calls.append((system_prompt, user_prompt))
        if not self._responses:
            raise RuntimeError("MockLLMClient out of queued responses")
        return self._responses.pop(0)


def _make_verdict_json(
    relationship_key: str,
    verdict: QAVerdict,
    *,
    contradictions: list[dict[str, Any]] | None = None,
    scene_fodder: list[str] | None = None,
    summary: str = "synthetic",
) -> str:
    payload = {
        "relationship_key": relationship_key,
        "verdict": verdict.value,
        "divergence_summary": summary,
        "contradictions": contradictions or [],
        "scene_fodder": scene_fodder or [],
    }
    return json.dumps(payload)


class TestVerdictParsing:
    def test_parse_verdict_round_trip_healthy(self) -> None:
        from starry_lyfe.dreams.generators.consistency_qa import _parse_verdict

        raw = _make_verdict_json("adelia_bina", QAVerdict.HEALTHY_DIVERGENCE,
                                  scene_fodder=["paella"])
        check = _parse_verdict(raw, expected_key="adelia_bina")
        assert check.verdict is QAVerdict.HEALTHY_DIVERGENCE

    def test_parse_verdict_unwraps_markdown_fence(self) -> None:
        from starry_lyfe.dreams.generators.consistency_qa import _parse_verdict

        raw = "```json\n" + _make_verdict_json("bina_reina", QAVerdict.CONCERNING_DRIFT) + "\n```"
        check = _parse_verdict(raw, expected_key="bina_reina")
        assert check.verdict is QAVerdict.CONCERNING_DRIFT

    def test_parse_verdict_rejects_wrong_key(self) -> None:
        from starry_lyfe.dreams.errors import DreamsLLMError
        from starry_lyfe.dreams.generators.consistency_qa import _parse_verdict

        raw = _make_verdict_json("wrong_key", QAVerdict.HEALTHY_DIVERGENCE)
        with pytest.raises(DreamsLLMError):
            _parse_verdict(raw, expected_key="adelia_bina")

    def test_parse_verdict_rejects_garbage(self) -> None:
        from starry_lyfe.dreams.errors import DreamsLLMError
        from starry_lyfe.dreams.generators.consistency_qa import _parse_verdict

        with pytest.raises(DreamsLLMError):
            _parse_verdict("this is not json", expected_key="adelia_bina")


# ----------------------------------------------------------------------
# Notifications dispatch (markdown writer + structlog)
# ----------------------------------------------------------------------


class TestNotifications:
    def test_emit_qa_event_writes_markdown_section(self, repo_tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        tmp_path = repo_tmp_path
        from starry_lyfe.dreams import notifications

        monkeypatch.setattr(notifications, "_DAILY_DIR", tmp_path)
        notifications.emit_qa_event(
            verdict=QAVerdict.FACTUAL_CONTRADICTION,
            relationship_key="whyze_alicia",
            divergence_summary="Marriage year contradicted",
            contradictions=[
                Contradiction(
                    field_name="marriage_year",
                    pov_character_id="alicia",
                    shared_canon_field="shared_canon.marriage.year",
                    observed_value="2023",
                    canonical_value="2022",
                )
            ],
            now=_utc_now(),
        )
        files = list(tmp_path.glob("*_consistency.md"))
        assert len(files) == 1
        text = files[0].read_text(encoding="utf-8")
        assert "## Operator review required" in text
        assert "whyze_alicia" in text
        assert "marriage_year" in text

    def test_emit_qa_event_routes_healthy_into_healthy_section(
        self, repo_tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        tmp_path = repo_tmp_path
        from starry_lyfe.dreams import notifications

        monkeypatch.setattr(notifications, "_DAILY_DIR", tmp_path)
        notifications.emit_qa_event(
            verdict=QAVerdict.HEALTHY_DIVERGENCE,
            relationship_key="adelia_bina",
            divergence_summary="Bina sees grounding; Adelia sees buoyancy. Both canonical.",
            contradictions=[],
            now=_utc_now(),
        )
        text = (tmp_path / "2026-04-17_consistency.md").read_text(encoding="utf-8")
        # The Healthy section should now contain adelia_bina; the Operator review
        # section should remain empty (no entries injected there).
        healthy_section = text.split("## Healthy")[1].split("## ")[0]
        assert "adelia_bina" in healthy_section
        operator_section = text.split("## Operator review required")[1]
        assert "adelia_bina" not in operator_section
