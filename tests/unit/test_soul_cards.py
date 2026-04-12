"""Phase C tests for soul card infrastructure.

Infrastructure tests (loader, activation, formatting) pass on placeholder
content. Content validation tests (required_concepts, budget compliance)
are marked xfail until the Project Owner authors real card prose.
"""

from __future__ import annotations

import pytest

from starry_lyfe.context.soul_cards import (
    SoulCard,
    find_activated_cards,
    format_soul_cards,
    load_all_soul_cards,
    load_soul_card,
)


class TestSoulCardLoader:
    """WI1: Soul card loader parses YAML frontmatter + markdown body."""

    def test_soul_card_loader_parses_frontmatter(self) -> None:
        from starry_lyfe.context.soul_cards import SOUL_CARDS_DIR

        path = SOUL_CARDS_DIR / "pair" / "bina_circuit.md"
        card = load_soul_card(path)
        assert card.character == "bina"
        assert card.card_type == "pair"
        assert card.budget_tokens == 700
        assert card.activation.get("always") is True
        assert "Circuit Pair" in card.required_concepts

    def test_all_soul_cards_load_without_error(self) -> None:
        cards = load_all_soul_cards()
        assert len(cards) == 15
        pair_cards = [c for c in cards if c.card_type == "pair"]
        knowledge_cards = [c for c in cards if c.card_type == "knowledge"]
        assert len(pair_cards) == 4
        assert len(knowledge_cards) == 11

    def test_placeholder_detection(self) -> None:
        cards = load_all_soul_cards()
        assert all(c.is_placeholder for c in cards)


class TestActivation:
    """WI1: Activation logic matches scene state."""

    def test_pair_card_always_activated_for_focal_character(self) -> None:
        cards = find_activated_cards("bina")
        pair_cards = [c for c in cards if c.card_type == "pair"]
        assert len(pair_cards) == 1
        assert pair_cards[0].character == "bina"

    def test_pair_card_not_activated_for_wrong_character(self) -> None:
        cards = find_activated_cards("bina")
        assert all(c.character == "bina" for c in cards)

    def test_knowledge_card_scene_activation(self) -> None:
        from starry_lyfe.context.types import SceneState

        scene = SceneState(
            present_characters=["reina", "whyze"],
            scene_description="Evening at the stable, Bishop in the paddock.",
        )
        cards = find_activated_cards("reina", scene_state=scene)
        knowledge_cards = [c for c in cards if c.card_type == "knowledge"]
        activated_names = [c.file_path for c in knowledge_cards]
        assert any("reina_stable" in p for p in activated_names)

    def test_alicia_remote_card_activates_on_communication_mode_phone(self) -> None:
        cards = find_activated_cards("alicia", communication_mode="phone")
        knowledge_cards = [c for c in cards if c.card_type == "knowledge"]
        activated_names = [c.file_path for c in knowledge_cards]
        assert any("alicia_remote" in p for p in activated_names)

    def test_alicia_remote_card_does_not_activate_in_person(self) -> None:
        cards = find_activated_cards("alicia", communication_mode="in_person")
        knowledge_cards = [c for c in cards if c.card_type == "knowledge"]
        activated_names = [c.file_path for c in knowledge_cards]
        assert not any("alicia_remote" in p for p in activated_names)


class TestFormatting:
    """WI1: format_soul_cards assembles within budget."""

    def test_format_empty_cards_returns_empty(self) -> None:
        assert format_soul_cards([], 700) == ""

    def test_format_placeholder_cards_returns_empty(self) -> None:
        cards = load_all_soul_cards()
        result = format_soul_cards(cards, 5000)
        assert result == ""

    def test_format_real_card_within_budget(self) -> None:
        card = SoulCard(
            character="bina",
            card_type="pair",
            source="test",
            budget_tokens=700,
            body="Bina and Whyze run the Circuit Pair on total division of operational domains.",
        )
        result = format_soul_cards([card], 700)
        assert "Circuit Pair" in result
        from starry_lyfe.context.budgets import estimate_tokens
        assert estimate_tokens(result) <= 700


class TestContentValidation:
    """Content tests that will fail on placeholders — expected by design."""

    @pytest.mark.xfail(reason="Placeholder content — awaiting Project Owner authoring")
    def test_pair_cards_within_700_token_budget(self) -> None:
        cards = load_all_soul_cards()
        for card in cards:
            if card.card_type == "pair" and not card.is_placeholder:
                from starry_lyfe.context.budgets import estimate_tokens
                assert estimate_tokens(card.body) <= 700, f"{card.file_path} exceeds 700 tokens"

    @pytest.mark.xfail(reason="Placeholder content — awaiting Project Owner authoring")
    def test_required_concepts_present_in_each_card(self) -> None:
        cards = load_all_soul_cards()
        for card in cards:
            if card.required_concepts and not card.is_placeholder:
                for concept in card.required_concepts:
                    assert concept in card.body, (
                        f"{card.file_path} missing required concept: {concept}"
                    )
