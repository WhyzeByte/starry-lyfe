"""Unit tests for ``api.routing.character.resolve_character_id``.

Lesson-#2 anti-contamination: the resolver is a single narrow pure
function that returns one immutable decision. The header > inline >
model > default priority must hold even when multiple inputs disagree.
"""

from __future__ import annotations

import pytest

from starry_lyfe.api.config import ApiSettings
from starry_lyfe.api.routing.character import (
    CharacterRoutingDecision,
    resolve_character_id,
    strip_inline_override,
)
from starry_lyfe.canon.schemas.enums import CharacterNotFoundError


def _settings(default: str = "adelia") -> ApiSettings:
    return ApiSettings(api_key="dev", default_character=default)


class TestResolveCharacterIdHeaderPath:
    def test_canonical_header_wins(self) -> None:
        decision = resolve_character_id(
            header="bina",
            model_field="reina",
            user_message="/alicia hello",
            settings=_settings(),
        )
        assert decision.character_id == "bina"
        assert decision.source == "header"
        assert decision.raw_value == "bina"

    def test_header_case_insensitive(self) -> None:
        decision = resolve_character_id(
            header="BINA",
            model_field=None,
            user_message=None,
            settings=_settings(),
        )
        assert decision.character_id == "bina"
        assert decision.raw_value == "BINA"

    def test_legacy_alias_routes_to_default(self) -> None:
        decision = resolve_character_id(
            header="starry-lyfe",
            model_field=None,
            user_message=None,
            settings=_settings(default="reina"),
        )
        assert decision.character_id == "reina"
        assert decision.source == "header"
        assert decision.raw_value == "starry-lyfe"

    def test_unknown_header_raises(self) -> None:
        with pytest.raises(CharacterNotFoundError):
            resolve_character_id(
                header="shawn",
                model_field=None,
                user_message=None,
                settings=_settings(),
            )


class TestResolveCharacterIdInlinePath:
    def test_inline_override_at_message_start(self) -> None:
        decision = resolve_character_id(
            header=None,
            model_field="reina",
            user_message="/bina what's the inventory like",
            settings=_settings(),
        )
        assert decision.character_id == "bina"
        assert decision.source == "inline_override"

    def test_all_marker_returns_default_with_flag(self) -> None:
        decision = resolve_character_id(
            header=None,
            model_field=None,
            user_message="/all ok everyone, group meeting",
            settings=_settings(default="adelia"),
        )
        assert decision.character_id == "adelia"
        assert decision.all_override is True
        assert decision.source == "inline_override"

    def test_inline_marker_only_at_start(self) -> None:
        decision = resolve_character_id(
            header=None,
            model_field=None,
            user_message="hey, /bina would not be a marker here",
            settings=_settings(default="adelia"),
        )
        # Falls through to default since no marker at start.
        assert decision.character_id == "adelia"
        assert decision.source == "default"


class TestResolveCharacterIdModelFieldPath:
    def test_model_field_routes(self) -> None:
        decision = resolve_character_id(
            header=None,
            model_field="alicia",
            user_message="hi",
            settings=_settings(),
        )
        assert decision.character_id == "alicia"
        assert decision.source == "model_field"

    def test_unknown_model_field_raises(self) -> None:
        with pytest.raises(CharacterNotFoundError):
            resolve_character_id(
                header=None,
                model_field="nonexistent-model",
                user_message=None,
                settings=_settings(),
            )

    def test_model_legacy_alias(self) -> None:
        decision = resolve_character_id(
            header=None,
            model_field="starry-lyfe",
            user_message=None,
            settings=_settings(default="bina"),
        )
        assert decision.character_id == "bina"
        assert decision.source == "model_field"


class TestResolveCharacterIdDefault:
    def test_no_inputs_returns_default(self) -> None:
        decision = resolve_character_id(
            header=None,
            model_field=None,
            user_message=None,
            settings=_settings(default="reina"),
        )
        assert decision.character_id == "reina"
        assert decision.source == "default"

    def test_empty_inputs_treated_as_missing(self) -> None:
        decision = resolve_character_id(
            header="",
            model_field="   ",
            user_message="",
            settings=_settings(default="adelia"),
        )
        assert decision.character_id == "adelia"
        assert decision.source == "default"


class TestAntiContamination:
    """AC-7.17: lesson-#2 — header MUST win over model field even when
    they disagree, and the losing source MUST not appear anywhere in
    the returned decision."""

    def test_adelia_header_beats_bina_model(self) -> None:
        decision = resolve_character_id(
            header="adelia",
            model_field="bina",
            user_message=None,
            settings=_settings(),
        )
        assert decision.character_id == "adelia"
        assert decision.source == "header"
        # The losing source MUST NOT leak.
        assert "bina" not in decision.raw_value
        assert decision.raw_value == "adelia"

    def test_decision_is_frozen(self) -> None:
        from dataclasses import FrozenInstanceError

        decision = resolve_character_id(
            header="adelia",
            model_field=None,
            user_message=None,
            settings=_settings(),
        )
        with pytest.raises(FrozenInstanceError):
            decision.character_id = "bina"  # type: ignore[misc]

    def test_decision_is_dataclass_instance(self) -> None:
        decision = resolve_character_id(
            header="adelia",
            model_field=None,
            user_message=None,
            settings=_settings(),
        )
        assert isinstance(decision, CharacterRoutingDecision)


class TestStripInlineOverride:
    def test_strips_leading_marker(self) -> None:
        assert strip_inline_override("/bina what's up") == "what's up"

    def test_no_marker_unchanged(self) -> None:
        assert strip_inline_override("just a regular message") == "just a regular message"

    def test_strips_all_marker(self) -> None:
        assert strip_inline_override("/all group meeting") == "group meeting"

    def test_only_strips_first_marker(self) -> None:
        # Subsequent slashes are content.
        assert strip_inline_override("/adelia /bina also") == "/bina also"
