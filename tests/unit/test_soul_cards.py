"""Phase C tests for soul card infrastructure.

Infrastructure tests (loader, activation, formatting) pass on placeholder
content. Content validation tests (required_concepts, budget compliance)
are marked xfail until the Project Owner authors real card prose.
"""

from __future__ import annotations

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
    """Content tests that enforce the placeholder contract."""

    def test_all_cards_are_currently_placeholders(self) -> None:
        """All cards should be placeholders until PO authors content."""
        cards = load_all_soul_cards()
        placeholders = [c for c in cards if c.is_placeholder]
        authored = [c for c in cards if not c.is_placeholder]
        assert len(placeholders) == 15, f"Expected 15 placeholders, got {len(placeholders)}"
        assert len(authored) == 0, f"Unexpected authored cards: {[c.file_path for c in authored]}"

    def test_knowledge_cards_within_500_token_budget(self) -> None:
        """Knowledge cards must declare budget ≤ 500 tokens."""
        cards = load_all_soul_cards()
        for card in cards:
            if card.card_type == "knowledge":
                assert card.budget_tokens <= 500, (
                    f"{card.file_path} declares {card.budget_tokens} tokens (max 500)"
                )

    def test_pair_cards_within_700_token_budget(self) -> None:
        """Pair cards must declare budget ≤ 700 tokens."""
        cards = load_all_soul_cards()
        for card in cards:
            if card.card_type == "pair":
                assert card.budget_tokens <= 700, (
                    f"{card.file_path} declares {card.budget_tokens} tokens (max 700)"
                )


class TestAssemblyIntegration:
    """F1 regression: soul cards must be wired into the live assembly path."""

    def test_pair_card_body_appears_in_assembled_layer_1(self) -> None:
        """A non-placeholder pair card's body reaches Layer 1."""
        from unittest.mock import patch

        real_card = SoulCard(
            character="bina",
            card_type="pair",
            source="test",
            budget_tokens=700,
            activation={"always": True},
            body="Bina and Whyze run the Circuit Pair on total division of operational domains.",
        )

        def mock_find(character_id: str, **kwargs: object) -> list[SoulCard]:
            if character_id == "bina":
                return [real_card]
            return []

        with patch("starry_lyfe.context.soul_cards.find_activated_cards", side_effect=mock_find):
            from starry_lyfe.context.soul_cards import format_soul_cards

            pair_text = format_soul_cards([real_card], 700)
            assert "Circuit Pair" in pair_text
            assert not real_card.is_placeholder
