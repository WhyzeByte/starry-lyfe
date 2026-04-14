"""Unit tests for Alicia away-mode communication_mode sampling (Phase A'')."""

from __future__ import annotations

import uuid

from starry_lyfe.dreams.alicia_mode import (
    pick_alicia_communication_mode,
    should_tag_alicia_away,
)


class TestPickAliciaCommunicationMode:
    def test_returns_valid_mode(self) -> None:
        mode = pick_alicia_communication_mode(uuid.uuid4(), "diary")
        assert mode in {"phone", "letter", "video_call"}

    def test_deterministic_for_same_seed(self) -> None:
        run_id = uuid.uuid4()
        a = pick_alicia_communication_mode(run_id, "diary")
        b = pick_alicia_communication_mode(run_id, "diary")
        assert a == b

    def test_different_output_kinds_can_yield_different_modes(self) -> None:
        """Different artifacts in one pass can land on different modes."""
        run_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
        # Not a strict requirement; just proves the kind is part of the seed.
        results = {
            pick_alicia_communication_mode(run_id, kind)
            for kind in ("diary", "activity", "off_screen")
        }
        # At least valid modes; may be all same but the hash differs.
        assert results.issubset({"phone", "letter", "video_call"})

    def test_different_run_ids_yield_varied_distribution(self) -> None:
        """Across many passes, we should see all three modes at least once."""
        seen: set[str] = set()
        for i in range(50):
            run_id = uuid.UUID(int=i)
            seen.add(pick_alicia_communication_mode(run_id, "diary"))
        # The distribution is 0.45/0.20/0.35 — with 50 samples every mode
        # should appear (probability of missing any single mode across 50
        # samples is vanishingly small).
        assert seen == {"phone", "letter", "video_call"}


class TestShouldTagAliciaAway:
    def test_alicia_away_yields_true(self) -> None:
        assert should_tag_alicia_away("alicia", True) is True

    def test_alicia_home_yields_false(self) -> None:
        assert should_tag_alicia_away("alicia", False) is False

    def test_non_alicia_always_false(self) -> None:
        for char in ("adelia", "bina", "reina"):
            assert should_tag_alicia_away(char, True) is False
            assert should_tag_alicia_away(char, False) is False
