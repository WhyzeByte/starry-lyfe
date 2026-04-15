"""Unit tests for ``api.routing.msty.preprocess_msty_request``.

Lesson #2: the preprocessor is the seam where the wide raw payload gets
narrowed into a focused ``MstyPreprocessed``. Downstream code MUST NOT
read the raw messages list directly.
"""

from __future__ import annotations

from starry_lyfe.api.routing.msty import preprocess_msty_request
from starry_lyfe.api.schemas.chat import ChatMessage


class TestSingleCharacterRequest:
    def test_returns_only_user_message(self) -> None:
        out = preprocess_msty_request([
            ChatMessage(role="user", content="hello adelia"),
        ])
        assert out.user_message == "hello adelia"
        assert out.scene_characters == []
        assert out.prior_responses == []
        assert out.system_prompt_text == ""

    def test_uses_last_user_message_when_multiple(self) -> None:
        out = preprocess_msty_request([
            ChatMessage(role="user", content="first"),
            ChatMessage(role="assistant", content="reply"),
            ChatMessage(role="user", content="second"),
        ])
        assert out.user_message == "second"


class TestCrewConversation:
    def test_crew_roster_extracted_from_system_prompt(self) -> None:
        system_prompt = (
            "You are speaking as one member of a crew that includes "
            "adelia, bina, reina, alicia. Stay in your assigned role."
        )
        out = preprocess_msty_request([
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content="group meeting"),
        ])
        assert set(out.scene_characters) == {"adelia", "bina", "reina", "alicia"}
        assert out.scene_characters == ["adelia", "bina", "reina", "alicia"]
        assert out.system_prompt_text == system_prompt

    def test_prior_persona_responses_extracted_via_name(self) -> None:
        out = preprocess_msty_request([
            ChatMessage(role="user", content="who's around?"),
            ChatMessage(role="assistant", content="The atelier is quiet today.", name="adelia"),
            ChatMessage(role="assistant", content="Inventory's caught up.", name="bina"),
            ChatMessage(role="user", content="what about Reina"),
        ])
        assert len(out.prior_responses) == 2
        assert out.prior_responses[0].character_id == "adelia"
        assert out.prior_responses[0].text == "The atelier is quiet today."
        assert out.prior_responses[1].character_id == "bina"

    def test_prior_persona_responses_extracted_via_prefix_fallback(self) -> None:
        out = preprocess_msty_request([
            ChatMessage(role="user", content="..."),
            ChatMessage(role="assistant", content="adelia: I was thinking about that."),
        ])
        assert len(out.prior_responses) == 1
        assert out.prior_responses[0].character_id == "adelia"
        assert out.prior_responses[0].text == "I was thinking about that."

    def test_roster_includes_speakers_even_if_not_in_system_prompt(self) -> None:
        # Some Msty Crew flows omit the system prompt entirely (ADR-001
        # production state) but speakers are still in the message stream.
        out = preprocess_msty_request([
            ChatMessage(role="assistant", content="...", name="reina"),
            ChatMessage(role="user", content="hi everyone"),
        ])
        assert "reina" in out.scene_characters

    def test_unknown_assistant_name_ignored(self) -> None:
        # Lesson #2: don't let unknown persona names contaminate the roster.
        out = preprocess_msty_request([
            ChatMessage(role="assistant", content="some reply", name="unknown_persona"),
            ChatMessage(role="user", content="..."),
        ])
        assert out.scene_characters == []
        assert out.prior_responses == []


class TestEdgeCases:
    def test_empty_message_list(self) -> None:
        out = preprocess_msty_request([])
        assert out.user_message == ""
        assert out.scene_characters == []
        assert out.prior_responses == []

    def test_no_user_message(self) -> None:
        # Should not crash; returns empty user_message.
        out = preprocess_msty_request([
            ChatMessage(role="system", content="..."),
            ChatMessage(role="assistant", content="...", name="adelia"),
        ])
        assert out.user_message == ""

    def test_canonical_order_preserved(self) -> None:
        # Even if speakers appear in a different order in messages, the
        # roster comes back in canonical order.
        out = preprocess_msty_request([
            ChatMessage(role="assistant", content="r", name="reina"),
            ChatMessage(role="assistant", content="a", name="adelia"),
            ChatMessage(role="user", content="..."),
        ])
        assert out.scene_characters == ["adelia", "reina"]
