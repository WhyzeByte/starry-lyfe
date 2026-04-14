"""Phase H / Phase J.1 soul regression tests for Bina Malek.

Verifies that the assembled prompt for Bina preserves all canonical
architecture markers, soul card content, and voice mode coverage, and
that no cross-character content bleeds in.

Test structure follows the Phase H spec in IMPLEMENTATION_PLAN_v7.1.md §12.
"""

from __future__ import annotations

import pytest

from starry_lyfe.context.kernel_loader import load_kernel, load_voice_examples
from starry_lyfe.context.soul_cards import find_activated_cards, format_soul_cards
from starry_lyfe.context.types import SceneState, SceneType, VoiceMode

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _bina_kernel(budget: int = 9000) -> str:
    """Compiled Bina kernel at generous budget."""
    return load_kernel("bina", budget=budget)


def _bina_pair_card_text() -> str:
    """Formatted Bina pair soul card text."""
    cards = find_activated_cards("bina", SceneState())
    pair_cards = [c for c in cards if c.card_type == "pair"]
    assert pair_cards, "Bina pair soul card must activate"
    return format_soul_cards(pair_cards, budget=900)


def _bina_ritual_card_text() -> str:
    """Full body of Bina's ritual knowledge card (unformatted, for content validation)."""
    cards = find_activated_cards(
        "bina",
        SceneState(scene_type=SceneType.DOMESTIC, scene_description="samovar kitchen"),
    )
    # filter by file_path — both knowledge cards share the same source document
    ritual_cards = [c for c in cards if "ritual" in c.file_path.lower()]
    assert ritual_cards, "Bina ritual card must activate for domestic/samovar scene"
    # Return raw body to validate authoring completeness, not runtime-trimmed output
    return ritual_cards[0].body


def _bina_grief_card_text() -> str:
    """Full body of Bina's grief knowledge card (unformatted, for content validation)."""
    cards = find_activated_cards(
        "bina",
        SceneState(scene_description="Arash Gilgamesh grief"),
    )
    # filter by file_path — both knowledge cards share the same source document
    grief_cards = [c for c in cards if "grief" in c.file_path.lower()]
    assert grief_cards, "Bina grief card must activate for Arash/grief scene"
    # Return raw body to validate authoring completeness, not runtime-trimmed output
    return grief_cards[0].body


# ---------------------------------------------------------------------------
# Pair architecture presence — kernel level
# ---------------------------------------------------------------------------


def test_bina_kernel_carries_circuit_pair_name() -> None:
    """The kernel must name the Circuit Pair — not an old v7.0 pair name."""
    kernel = _bina_kernel()
    assert "Circuit Pair" in kernel
    assert "Citadel Pair" not in kernel


def test_bina_kernel_carries_orthogonal_opposition() -> None:
    """Orthogonal Opposition is the classification of the Circuit Pair."""
    kernel = _bina_kernel()
    assert "Orthogonal Opposition" in kernel or "orthogonal opposition" in kernel.lower()


def test_bina_kernel_carries_translation_not_mirroring() -> None:
    """Translation concept is in the kernel; 'mirroring' lives in the pair soul card."""
    kernel = _bina_kernel()
    pair_text = _bina_pair_card_text()
    assert "translation" in kernel.lower(), "'translation' must appear in Bina's kernel"
    assert "mirror" in pair_text.lower(), "'mirroring' must appear in Bina's pair soul card"


def test_bina_kernel_carries_gilgamesh() -> None:
    """The Epic of Gilgamesh is load-bearing — it is the citadel substrate."""
    kernel = _bina_kernel()
    assert "Gilgamesh" in kernel


def test_bina_kernel_carries_urmia() -> None:
    """Urmia is Bina's canonical birthplace — must appear in the kernel."""
    kernel = _bina_kernel()
    assert "Urmia" in kernel


def test_bina_kernel_carries_arash() -> None:
    """Arash (twin) is canonical — must appear in the kernel."""
    kernel = _bina_kernel()
    assert "Arash" in kernel


def test_bina_kernel_carries_samovar() -> None:
    """The samovar is the canonical household register for Bina's culture."""
    kernel = _bina_kernel()
    assert "samovar" in kernel


# ---------------------------------------------------------------------------
# Pair soul card — required concepts
# ---------------------------------------------------------------------------


def test_bina_pair_soul_card_loads() -> None:
    """Bina's pair soul card must activate and contain canonical content."""
    text = _bina_pair_card_text()
    assert len(text) > 100


def test_bina_pair_card_contains_architect_and_sentinel() -> None:
    """'The Architect and the Sentinel' is the core metaphor — must be in card."""
    text = _bina_pair_card_text()
    assert "Architect and the Sentinel" in text or "Sentinel" in text


def test_bina_pair_card_contains_diagnostic_love() -> None:
    """Diagnostic love is Bina's canonical love-language descriptor."""
    text = _bina_pair_card_text()
    assert "diagnostic love" in text.lower()


def test_bina_pair_card_contains_total_division() -> None:
    """Total division of operational domains is the pair mechanism."""
    text = _bina_pair_card_text()
    assert "total division" in text.lower()


def test_bina_pair_card_no_old_pair_name() -> None:
    """Old v7.0 pair name 'Citadel' must not appear in the pair card."""
    text = _bina_pair_card_text()
    assert "Citadel Pair" not in text


# ---------------------------------------------------------------------------
# Ritual soul card — required concepts
# ---------------------------------------------------------------------------


def test_bina_ritual_card_contains_samovar() -> None:
    """Ritual card must carry the samovar — the canonical household anchor."""
    text = _bina_ritual_card_text()
    assert "samovar" in text.lower()


def test_bina_ritual_card_contains_norouz() -> None:
    """Norouz is on the canonical ritual calendar."""
    text = _bina_ritual_card_text()
    assert "Norouz" in text or "norouz" in text.lower()


def test_bina_ritual_card_contains_tahdig() -> None:
    """Tahdig is Shirin's signature dish — canonical kitchen register."""
    text = _bina_ritual_card_text()
    assert "tahdig" in text.lower()


def test_bina_ritual_card_contains_kipte() -> None:
    """Kipte is specifically Assyrian — the cultural distinction marker."""
    text = _bina_ritual_card_text()
    assert "kipte" in text.lower()


# ---------------------------------------------------------------------------
# Grief soul card — required concepts
# ---------------------------------------------------------------------------


def test_bina_grief_card_contains_farhad() -> None:
    """Farhad (father) must be named in the grief card."""
    text = _bina_grief_card_text()
    assert "Farhad" in text


def test_bina_grief_card_contains_shirin() -> None:
    """Shirin (mother) must be named in the grief card."""
    text = _bina_grief_card_text()
    assert "Shirin" in text


def test_bina_grief_card_contains_arash() -> None:
    """Arash (twin) must be named in the grief card."""
    text = _bina_grief_card_text()
    assert "Arash" in text


def test_bina_grief_card_contains_urmia_to_edmonton() -> None:
    """The Urmia-to-Edmonton migration is load-bearing context."""
    text = _bina_grief_card_text()
    assert "Urmia" in text and "Edmonton" in text


# ---------------------------------------------------------------------------
# Voice mode coverage — all 5 required modes present
# ---------------------------------------------------------------------------


def test_bina_voice_covers_domestic_mode() -> None:
    examples = load_voice_examples("bina") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.DOMESTIC in modes, "Bina Voice.md must have domestic exemplar"


def test_bina_voice_covers_conflict_mode() -> None:
    examples = load_voice_examples("bina") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.CONFLICT in modes, "Bina Voice.md must have conflict exemplar"


def test_bina_voice_covers_intimate_mode() -> None:
    examples = load_voice_examples("bina") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.INTIMATE in modes, "Bina Voice.md must have intimate exemplar"


def test_bina_voice_covers_repair_mode() -> None:
    examples = load_voice_examples("bina") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.REPAIR in modes, "Bina Voice.md must have repair exemplar"


def test_bina_voice_covers_silent_mode() -> None:
    """Silent mode is audit-driven — Bina's near-silent seismograph response is canonical."""
    examples = load_voice_examples("bina") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.SILENT in modes, "Bina Voice.md must have silent exemplar"


# ---------------------------------------------------------------------------
# Cross-character contamination — kernel must NOT contain other characters' markers
# ---------------------------------------------------------------------------


def test_bina_kernel_no_adelia_workshop_markers() -> None:
    """Adelia's Marrickville and Ozone & Ember must not appear in Bina's kernel."""
    kernel = _bina_kernel()
    assert "Marrickville" not in kernel
    assert "Ozone" not in kernel


def test_bina_kernel_no_adelia_father() -> None:
    """Adelia's father Joaquin must not appear in Bina's kernel."""
    kernel = _bina_kernel()
    # Bina's father is Farhad; Adelia's is Joaquin/Joaquín
    assert "Joaquin" not in kernel
    assert "Joaquín" not in kernel


def test_bina_kernel_no_reina_court_markers() -> None:
    """Reina's canonical markers must not appear in Bina's kernel."""
    kernel = _bina_kernel()
    assert "Cuatrecasas" not in kernel
    assert "Bishop" not in kernel  # Reina's horse


def test_bina_kernel_no_alicia_rioplatense_markers() -> None:
    """Alicia's Argentine markers must not appear in Bina's kernel."""
    kernel = _bina_kernel()
    assert "Famaill" not in kernel   # Famaillá
    assert "Mercedes Sosa" not in kernel
    assert "Canciller" not in kernel


# ---------------------------------------------------------------------------
# Structural integrity — kernel must not be truncated
# ---------------------------------------------------------------------------


def test_bina_kernel_no_truncation_marker() -> None:
    """A properly budgeted Bina kernel must not hit the truncation fallback."""
    kernel = _bina_kernel(budget=9000)
    assert "[Kernel trimmed to token budget.]" not in kernel
    assert "[Section trimmed" not in kernel


def test_bina_kernel_contains_farhad_not_as_stale_data() -> None:
    """Bina's father Farhad must appear (not Adelia's father Joaquin)."""
    kernel = _bina_kernel()
    assert "Farhad" in kernel


def test_bina_kernel_circuit_pair_is_v71_name() -> None:
    """The kernel uses the canonical v7.1 pair name (Circuit), not the v7.0 name (Citadel)."""
    kernel = _bina_kernel()
    assert "Circuit Pair" in kernel
    assert "Citadel" not in kernel


# ---------------------------------------------------------------------------
# Soul card required-concept invariant — machine-verifiable
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("concept", [
    "Circuit Pair",
    "Orthogonal Opposition",
    "total division of operational domains",
    "diagnostic love",
    "translation not mirroring",
])
def test_bina_pair_card_required_concept_present(concept: str) -> None:
    """All required_concepts from the pair card frontmatter must appear in the body."""
    text = _bina_pair_card_text()
    # Canonical form uses comma — accept both "translation, not mirroring" and "translation not mirroring"
    search = concept.lower().replace(",", "")
    card_lower = text.lower().replace(",", "")
    assert search in card_lower, f"Required concept missing from Bina pair card: '{concept}'"


@pytest.mark.parametrize("concept", [
    "Norouz",
    "Kha b-Nisan",
    "tahdig",
    "kipte",
    "samovar",
    "haft-sin",
])
def test_bina_ritual_card_required_concept_present(concept: str) -> None:
    """All required_concepts from the ritual card frontmatter must appear in the body."""
    text = _bina_ritual_card_text()
    assert concept.lower() in text.lower(), f"Required concept missing from Bina ritual card: '{concept}'"


@pytest.mark.parametrize("concept", [
    "Epic of Gilgamesh",
    "Farhad",       # card says "Farhad and Shirin Malek" — Farhad is present
    "Shirin",       # card says "Farhad and Shirin Malek" — Shirin is present
    "Arash",
    "Urmia to Edmonton",
])
def test_bina_grief_card_required_concept_present(concept: str) -> None:
    """All required_concepts from the grief card frontmatter must appear in the body."""
    text = _bina_grief_card_text()
    assert concept.lower() in text.lower(), f"Required concept missing from Bina grief card: '{concept}'"
