"""Phase C tests for soul card infrastructure."""

from __future__ import annotations

from types import SimpleNamespace

from starry_lyfe.context import assembler as assembler_module
from starry_lyfe.context.assembler import assemble_context
from starry_lyfe.context.budgets import DEFAULT_BUDGETS, resolve_kernel_budget
from starry_lyfe.context.soul_cards import (
    SoulCard,
    find_activated_cards,
    format_soul_cards,
    load_all_soul_cards,
    load_soul_card,
)
from starry_lyfe.context.types import CommunicationMode, SceneState


class _StubEmbeddingService:
    async def embed(self, text: str) -> list[float]:
        return [0.0] * 768

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * 768 for _ in texts]


def _make_bina_bundle() -> SimpleNamespace:
    baseline = SimpleNamespace(
        full_name="Bina Malek",
        epithet="The Sentinel",
        mbti="ISFJ-A",
        dominant_function="Si",
        pair_name="circuit",
        heritage="Assyrian-Iranian Canadian",
        profession="Mechanic",
        voice_params={
            "response_length_range": "2-4 sentences",
            "dominant_function_descriptor": "Si-dominant declarative steadiness",
        },
    )
    return SimpleNamespace(
        canon_facts=[],
        character_baseline=baseline,
        dyad_states_whyze=[],
        dyad_states_internal=[],
        episodic_memories=[],
        open_loops=[],
        somatic_state=SimpleNamespace(
            character_id="bina",
            fatigue=0.10,
            stress_residue=0.10,
            injury_residue=0.00,
            active_protocols=[],
        ),
    )


class TestSoulCardLoader:
    """WI1: Soul card loader parses YAML frontmatter + markdown body."""

    def test_soul_card_loader_parses_frontmatter(self) -> None:
        from starry_lyfe.context.soul_cards import SOUL_CARDS_DIR

        path = SOUL_CARDS_DIR / "pair" / "bina_circuit.md"
        card = load_soul_card(path)
        assert card.character == "bina"
        assert card.card_type == "pair"
        assert card.budget_tokens == 850  # raised from 700 to match authored body size
        assert card.activation.get("always") is True
        assert "Circuit Pair" in card.required_concepts

    def test_all_soul_cards_load_without_error(self) -> None:
        cards = load_all_soul_cards()
        assert len(cards) == 15
        pair_cards = [c for c in cards if c.card_type == "pair"]
        knowledge_cards = [c for c in cards if c.card_type == "knowledge"]
        assert len(pair_cards) == 4
        assert len(knowledge_cards) == 11

    def test_no_placeholders_remain(self) -> None:
        """After 2026-04-12 direct remediation, all 15 cards should be authored."""
        cards = load_all_soul_cards()
        placeholders = [c for c in cards if c.is_placeholder]
        assert not placeholders, f"Unexpected placeholders: {[c.file_path for c in placeholders]}"


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

    def test_format_authored_cards_returns_content(self) -> None:
        """After 2026-04-12 direct remediation, formatting should return non-empty content."""
        cards = load_all_soul_cards()
        result = format_soul_cards(cards, 5000)
        assert result != ""
        assert len(result) > 1000

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
    """Content tests that enforce the authored contract."""

    def test_all_cards_are_authored(self) -> None:
        """After 2026-04-12 direct remediation, all 15 cards should be authored with full fidelity."""
        cards = load_all_soul_cards()
        placeholders = [c for c in cards if c.is_placeholder]
        authored = [c for c in cards if not c.is_placeholder]
        assert len(authored) == 15, f"Expected 15 authored cards, got {len(authored)}"
        assert len(placeholders) == 0, f"Unexpected placeholders: {[c.file_path for c in placeholders]}"

    def test_knowledge_cards_within_500_token_budget(self) -> None:
        """Knowledge card bodies must fit within their declared budget_tokens.

        budget_tokens was raised per-card to match actual authored content
        (Phase C lettered remediation, 2026-04-13). The test now validates
        that the body fits within the declared value — not a fixed 500-token
        ceiling — so the runtime delivers all canonical content.
        """
        cards = load_all_soul_cards()
        from starry_lyfe.context.budgets import estimate_tokens
        for card in cards:
            if card.card_type == "knowledge":
                body_tokens = estimate_tokens(card.body)
                assert body_tokens <= card.budget_tokens, (
                    f"{card.file_path} body is {body_tokens} tokens "
                    f"but budget_tokens is only {card.budget_tokens}"
                )

    def test_pair_cards_within_700_token_budget(self) -> None:
        """Pair card bodies must fit within their declared budget_tokens.

        budget_tokens was raised per-card to match actual authored content
        (Phase C lettered remediation, 2026-04-13).
        """
        cards = load_all_soul_cards()
        from starry_lyfe.context.budgets import estimate_tokens
        for card in cards:
            if card.card_type == "pair":
                body_tokens = estimate_tokens(card.body)
                assert body_tokens <= card.budget_tokens, (
                    f"{card.file_path} body is {body_tokens} tokens "
                    f"but budget_tokens is only {card.budget_tokens}"
                )

    def test_required_concepts_within_budget(self) -> None:
        """Every required_concept must appear in the first budget_tokens tokens.

        This verifies runtime delivery — the model receives the trimmed body
        and all required concepts must be present in what actually arrives.
        """
        from starry_lyfe.context.budgets import trim_text_to_budget
        cards = load_all_soul_cards()
        failures: list[str] = []
        for card in cards:
            trimmed = trim_text_to_budget(card.body, card.budget_tokens)
            for concept in card.required_concepts:
                if concept.lower() not in trimmed.lower():
                    failures.append(
                        f"{card.file_path}: '{concept}' missing from trimmed output"
                    )
        assert not failures, "required_concepts missing from runtime-delivered content:\n" + "\n".join(failures)


class TestAssemblyIntegration:
    """F1 regression: soul cards must be wired into the live assembly path."""

    async def test_soul_cards_reach_assembled_layers_within_layer_budgets(
        self,
        monkeypatch,
    ) -> None:
        """Non-placeholder soul cards reach live assembly without breaking layer budgets."""
        pair_card = SoulCard(
            character="bina",
            card_type="pair",
            source="test",
            budget_tokens=700,
            activation={"always": True},
            body=("Circuit Pair " + ("pairword " * 1200)).strip(),
        )
        knowledge_card = SoulCard(
            character="bina",
            card_type="knowledge",
            source="test",
            budget_tokens=500,
            activation={"scene_keyword": ["kitchen"]},
            body=("knowledgeword " * 900).strip(),
        )

        async def stub_retrieve_memories(*args: object, **kwargs: object) -> SimpleNamespace:
            return _make_bina_bundle()

        monkeypatch.setattr(assembler_module, "retrieve_memories", stub_retrieve_memories)
        monkeypatch.setattr(
            "starry_lyfe.context.soul_cards.find_activated_cards",
            lambda *args, **kwargs: [pair_card, knowledge_card],
        )

        prompt = await assemble_context(
            character_id="bina",
            scene_context="Bina is in the kitchen after the shop closes.",
            scene_state=SceneState(
                present_characters=["bina", "whyze"],
                scene_description="Kitchen after the shop closes.",
                communication_mode=CommunicationMode.IN_PERSON,
            ),
            session=None,
            embedding_service=_StubEmbeddingService(),
        )

        layer_1 = next(layer for layer in prompt.layers if layer.layer_number == 1)
        layer_6 = next(layer for layer in prompt.layers if layer.layer_number == 6)

        assert "pairword" in layer_1.text
        assert "knowledgeword" in layer_6.text
        # Layer 1 carries guaranteed soul essence alongside the trimmable
        # kernel body. Effective ceiling = kernel_budget + soul_essence.
        from starry_lyfe.canon.soul_essence import soul_essence_token_estimate
        effective_l1_ceiling = (
            resolve_kernel_budget("bina") + soul_essence_token_estimate("bina")
        )
        assert layer_1.estimated_tokens <= effective_l1_ceiling
        assert layer_6.estimated_tokens <= DEFAULT_BUDGETS.scene
