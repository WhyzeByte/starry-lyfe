"""Phase 8 Step 2.8: prompt builder + response parser unit tests.

Covers AC-8.8 (per-character register notes in the system prompt),
AC-8.9 (parser returns None on malformed / missing / non-numeric),
and AC-8.10 (repair_history negative values clamp to 0.0).

Pure unit tests: no async, no DB, no BDOne.
"""

from __future__ import annotations

import pytest

from starry_lyfe.api.orchestration import (
    RELATIONSHIP_EVAL_SYSTEM,
    build_eval_prompt,
    parse_eval_response,
)
from starry_lyfe.api.orchestration.relationship import DyadDeltaProposal


class TestBuildEvalPrompt:
    def test_contains_character_id_and_response(self) -> None:
        """AC-8.8: user prompt surfaces the character id + response text."""
        prompt = build_eval_prompt("adelia", "She set the kiln to cool.")
        assert "Character: adelia" in prompt
        assert "She set the kiln to cool." in prompt
        # Delimited section lets the LLM locate response text unambiguously.
        assert "<response_text>" in prompt
        assert "</response_text>" in prompt

    def test_lowercases_character_id(self) -> None:
        """build_eval_prompt normalises the character id to lowercase."""
        prompt = build_eval_prompt("ADELIA", "morning")
        assert "Character: adelia" in prompt
        # Upper-case form should not also surface.
        assert "Character: ADELIA" not in prompt

    def test_system_prompt_names_all_four_characters(self) -> None:
        """AC-8.8: each of the four women has a register section."""
        for name in ("ADELIA", "BINA", "REINA", "ALICIA"):
            assert name in RELATIONSHIP_EVAL_SYSTEM, (
                f"{name} register section missing from system prompt"
            )

    def test_system_prompt_declares_repair_as_positive_only(self) -> None:
        """AC-8.10: the canonical contract for repair_history is positive-only."""
        assert "repair_history" in RELATIONSHIP_EVAL_SYSTEM
        # Look for explicit positive-only language.
        lowered = RELATIONSHIP_EVAL_SYSTEM.lower()
        assert "positive-only" in lowered or "never negative" in lowered


class TestParseEvalResponse:
    def test_valid_json_returns_proposal(self) -> None:
        """AC-8.9: well-formed JSON parses to a DyadDeltaProposal."""
        raw = (
            '{"intimacy": 0.12, "unresolved_tension": -0.05, '
            '"trust": 0.08, "repair_history": 0.0}'
        )
        result = parse_eval_response(raw)
        assert isinstance(result, DyadDeltaProposal)
        assert result.intimacy == 0.12
        assert result.unresolved_tension == -0.05
        assert result.trust == 0.08
        assert result.repair_history == 0.0

    def test_strips_markdown_fences(self) -> None:
        """Some LLMs emit ```json ... ``` fences despite instructions."""
        raw = (
            "```json\n"
            '{"intimacy": 0.2, "unresolved_tension": 0.0, '
            '"trust": 0.0, "repair_history": 0.0}\n'
            "```"
        )
        result = parse_eval_response(raw)
        assert result is not None
        assert result.intimacy == 0.2

    def test_malformed_json_returns_none(self) -> None:
        """AC-8.9: malformed JSON → None → caller falls back."""
        assert parse_eval_response("not json at all") is None
        assert parse_eval_response("{intimacy: 0.1}") is None  # unquoted key
        assert parse_eval_response("") is None

    def test_missing_field_returns_none(self) -> None:
        """AC-8.9: missing any of the 4 required fields → None."""
        raw = '{"intimacy": 0.1, "unresolved_tension": 0.0, "trust": 0.0}'
        # Missing repair_history.
        assert parse_eval_response(raw) is None

    def test_non_numeric_value_returns_none(self) -> None:
        """AC-8.9: string or null in a numeric field → None."""
        raw = (
            '{"intimacy": "warm", "unresolved_tension": 0.0, '
            '"trust": 0.0, "repair_history": 0.0}'
        )
        assert parse_eval_response(raw) is None

    def test_out_of_range_value_clamps_at_boundary(self) -> None:
        """AC-8.5: slightly-out-of-bounds values clamp instead of failing.

        The ±0.03 downstream cap is the real safety margin, so graceful
        degradation on minor overshoot is safer than hard-failing.
        """
        raw = (
            '{"intimacy": 1.5, "unresolved_tension": -1.2, '
            '"trust": 0.5, "repair_history": 0.0}'
        )
        result = parse_eval_response(raw)
        assert result is not None
        assert result.intimacy == 1.0
        assert result.unresolved_tension == -1.0
        assert result.trust == 0.5

    def test_negative_repair_history_clamps_to_zero(self) -> None:
        """AC-8.10: repair is positive-only; a single turn can never erase it."""
        raw = (
            '{"intimacy": 0.0, "unresolved_tension": 0.0, '
            '"trust": 0.0, "repair_history": -0.4}'
        )
        result = parse_eval_response(raw)
        assert result is not None
        assert result.repair_history == 0.0

    def test_integer_values_accepted(self) -> None:
        """Integer literals are valid numerics per JSON; parser should accept."""
        raw = (
            '{"intimacy": 0, "unresolved_tension": 0, '
            '"trust": 0, "repair_history": 0}'
        )
        result = parse_eval_response(raw)
        assert result is not None
        assert result.intimacy == 0.0

    def test_parse_survives_extra_fields(self) -> None:
        """LLM may include a 'reason' or 'explanation' key — ignore it."""
        raw = (
            '{"intimacy": 0.1, "unresolved_tension": 0.0, '
            '"trust": 0.0, "repair_history": 0.0, '
            '"reason": "warm but reserved"}'
        )
        result = parse_eval_response(raw)
        assert result is not None
        assert result.intimacy == 0.1


class TestR1F1ParserFailClosed:
    """R1-F1 closure: parser fails closed on non-object JSON + booleans.

    Pre-remediation: `parse_eval_response('[]')` raised AttributeError
    on `raw.keys()`, and the same exception propagated through
    ``evaluate_and_update`` instead of falling back to the heuristic.
    JSON booleans were silently coerced to 1.0/0.0 because ``bool`` is
    a subclass of ``int`` in Python.
    """

    @pytest.mark.parametrize(
        "raw",
        ["[]", "[1, 2, 3]", "42", "3.14", '"hi"', "null", "true", "false"],
        ids=[
            "empty_array", "number_array", "integer", "float",
            "string", "null", "bool_true", "bool_false",
        ],
    )
    def test_parse_non_object_json_returns_none(self, raw: str) -> None:
        """Any valid JSON that is NOT an object must return None, not raise."""
        assert parse_eval_response(raw) is None

    def test_parse_boolean_field_value_returns_none(self) -> None:
        """AC-8.9: JSON booleans are non-numeric per spec; reject explicitly."""
        raw = (
            '{"intimacy": true, "unresolved_tension": 0.0, '
            '"trust": 0.0, "repair_history": 0.0}'
        )
        assert parse_eval_response(raw) is None

    def test_parse_boolean_false_field_returns_none(self) -> None:
        raw = (
            '{"intimacy": 0.1, "unresolved_tension": 0.0, '
            '"trust": 0.0, "repair_history": false}'
        )
        assert parse_eval_response(raw) is None


class TestR1F2PydanticSchemaActive:
    """R1-F2 closure: `RelationshipEvalResponse` is no longer dead code.

    The parser now routes validation through ``model_validate``. These
    tests prove the schema fires by importing it directly and asserting
    the same contract the parser relies on.
    """

    def test_schema_rejects_booleans_via_before_validator(self) -> None:
        """Direct schema test: boolean in any field raises ValidationError."""
        from pydantic import ValidationError

        from starry_lyfe.api.orchestration import RelationshipEvalResponse

        with pytest.raises(ValidationError):
            RelationshipEvalResponse.model_validate(
                {"intimacy": True, "unresolved_tension": 0.0, "trust": 0.0, "repair_history": 0.0}
            )

    def test_schema_accepts_valid_floats(self) -> None:
        from starry_lyfe.api.orchestration import RelationshipEvalResponse

        model = RelationshipEvalResponse.model_validate(
            {"intimacy": 0.12, "unresolved_tension": -0.05, "trust": 0.08, "repair_history": 0.0}
        )
        assert model.intimacy == 0.12
        assert model.unresolved_tension == -0.05

    def test_schema_ignores_extra_fields(self) -> None:
        """`extra='ignore'` config lets LLMs add `reason` etc. without breaking parse."""
        from starry_lyfe.api.orchestration import RelationshipEvalResponse

        model = RelationshipEvalResponse.model_validate(
            {
                "intimacy": 0.1, "unresolved_tension": 0.0,
                "trust": 0.0, "repair_history": 0.0,
                "reason": "Warm and reserved",
                "confidence": 0.85,
            }
        )
        assert model.intimacy == 0.1

    def test_schema_accepts_integer_coerced_to_float(self) -> None:
        from starry_lyfe.api.orchestration import RelationshipEvalResponse

        model = RelationshipEvalResponse.model_validate(
            {"intimacy": 0, "unresolved_tension": 0, "trust": 0, "repair_history": 0}
        )
        assert isinstance(model.intimacy, float)
        assert model.intimacy == 0.0
