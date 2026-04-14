"""Phase H / Phase J.2 soul regression tests for Adelia Raye.

Verifies that the assembled prompt for Adelia preserves all canonical
architecture markers, soul card content, and voice mode coverage, and
that no cross-character content bleeds in.

J.2 critical audit findings:
- Gravitational center / Entangled Pair as the reason the system exists
- Cognitive handoff contract (DEPENDENCE, not just stylistic behavior)
- Structural safety language (not emotional reassurance)
- Load-bearing quietness: silent mode exemplar is canonical
- Whiteboard Mode and Bunker Mode protocols present
- Valencian-Australian cultural register runtime-strong (cultural soul card)
"""

from __future__ import annotations

import pytest

from starry_lyfe.context.kernel_loader import load_kernel, load_voice_examples
from starry_lyfe.context.soul_cards import find_activated_cards
from starry_lyfe.context.types import SceneState, VoiceMode

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _adelia_kernel(budget: int = 10000) -> str:
    return load_kernel("adelia", budget=budget)


def _adelia_pair_card() -> str:
    cards = find_activated_cards("adelia", SceneState())
    pair = [c for c in cards if c.card_type == "pair"]
    assert pair, "Adelia pair soul card must activate"
    return pair[0].body


def _adelia_knowledge_card(keyword: str, scene_desc: str) -> str:
    """Get a specific knowledge card body by file_path keyword."""
    cards = find_activated_cards(
        "adelia",
        SceneState(scene_description=scene_desc),
    )
    matched = [c for c in cards if keyword in c.file_path.lower()]
    assert matched, f"Adelia '{keyword}' card must activate for scene: {scene_desc}"
    return matched[0].body


# ---------------------------------------------------------------------------
# Pair architecture — kernel level
# ---------------------------------------------------------------------------


def test_adelia_kernel_carries_entangled_pair_name() -> None:
    kernel = _adelia_kernel()
    assert "Entangled Pair" in kernel
    assert "Golden Pair" not in kernel  # old v7.0 name


def test_adelia_kernel_carries_marrickville() -> None:
    """Marrickville is Adelia's canonical childhood geography — must be in kernel."""
    assert "Marrickville" in _adelia_kernel()


def test_adelia_kernel_carries_las_fallas() -> None:
    """Las Fallas is load-bearing — fire as architecture, the origin of the appetite."""
    assert "Las Fallas" in _adelia_kernel()


def test_adelia_kernel_carries_ozone_and_ember() -> None:
    """Ozone and Ember is her canonical business name."""
    assert "Ozone and Ember" in _adelia_kernel() or "Ozone & Ember" in _adelia_kernel()


def test_adelia_kernel_carries_whiteboard_mode() -> None:
    """Whiteboard Mode is a named protocol — must appear in kernel."""
    assert "Whiteboard Mode" in _adelia_kernel()


def test_adelia_kernel_carries_bunker_mode() -> None:
    """Bunker Mode is the canonical failure-state protocol for Adelia."""
    assert "Bunker Mode" in _adelia_kernel()


def test_adelia_kernel_carries_joaquin() -> None:
    """Joaquin (father) is load-bearing — the precision-as-love inheritance."""
    assert "Joaquin" in _adelia_kernel()


def test_adelia_kernel_no_truncation() -> None:
    assert "[Kernel trimmed to token budget.]" not in _adelia_kernel()


# ---------------------------------------------------------------------------
# Pair soul card — J.2 critical concepts
# ---------------------------------------------------------------------------


def test_adelia_pair_card_loads() -> None:
    assert len(_adelia_pair_card()) > 100


def test_adelia_pair_card_structural_safety() -> None:
    """J.2 critical: structural safety, not emotional reassurance."""
    assert "structural safety" in _adelia_pair_card().lower()


def test_adelia_pair_card_one_plus_one_equals_eleven() -> None:
    """1+1=11 is the canonical statement of the cognitive interlock."""
    assert "1+1=11" in _adelia_pair_card()


def test_adelia_pair_card_fragmented_plans_handoff() -> None:
    """The fragmented plans handoff is the cognitive dependence contract."""
    assert "fragmented plans" in _adelia_pair_card().lower()


def test_adelia_pair_card_compass_and_gravity() -> None:
    """The Compass and the Gravity is the core metaphor."""
    assert "Compass and the Gravity" in _adelia_pair_card() or \
           "compass and the gravity" in _adelia_pair_card().lower()


def test_adelia_pair_card_intuitive_symbiosis() -> None:
    """Intuitive Symbiosis is the pair classification."""
    assert "Intuitive Symbiosis" in _adelia_pair_card()


def test_adelia_pair_card_no_old_pair_name() -> None:
    assert "Golden Pair" not in _adelia_pair_card()


# ---------------------------------------------------------------------------
# Cultural soul card — Valencian register (J.2 audit-driven)
# ---------------------------------------------------------------------------


def test_adelia_cultural_card_activates_on_marrickville() -> None:
    body = _adelia_knowledge_card("cultural", "Marrickville workshop Valencia")
    assert len(body) > 50


def test_adelia_cultural_card_valencian_australian() -> None:
    body = _adelia_knowledge_card("cultural", "Valencia Marrickville")
    assert "Valencian-Australian" in body


def test_adelia_cultural_card_kitchen_spanish() -> None:
    body = _adelia_knowledge_card("cultural", "Spanish Marrickville")
    assert "kitchen Spanish" in body or "kitchen spanish" in body.lower()


def test_adelia_cultural_card_joaquin_raye() -> None:
    """Joaquin Raye is the canonical full name of her father."""
    body = _adelia_knowledge_card("cultural", "Joaquin Valencia")
    assert "Joaquin Raye" in body


def test_adelia_cultural_card_virgen_desamparados() -> None:
    """Virgen de los Desamparados is the canonical Valencian icon."""
    body = _adelia_knowledge_card("cultural", "Valencia Marrickville")
    assert "Desamparados" in body


# ---------------------------------------------------------------------------
# Workshop soul card
# ---------------------------------------------------------------------------


def test_adelia_workshop_card_activates() -> None:
    body = _adelia_knowledge_card("workshop", "warehouse fabrication")
    assert len(body) > 50


def test_adelia_workshop_card_manchester_warehouse() -> None:
    body = _adelia_knowledge_card("workshop", "warehouse commission")
    assert "Manchester" in body and "warehouse" in body.lower()


def test_adelia_workshop_card_ozone_and_ember() -> None:
    body = _adelia_knowledge_card("workshop", "warehouse commission")
    assert "Ozone and Ember" in body or "Ozone & Ember" in body


def test_adelia_workshop_card_the_compass() -> None:
    """The Compass is the lifetime installation — load-bearing."""
    body = _adelia_knowledge_card("workshop", "Compass warehouse")
    assert "the Compass" in body or "The Compass" in body


def test_adelia_workshop_card_penetration_testing() -> None:
    body = _adelia_knowledge_card("workshop", "pen test warehouse")
    assert "penetration testing" in body.lower() or "pen test" in body.lower()


# ---------------------------------------------------------------------------
# Pyrotechnics soul card
# ---------------------------------------------------------------------------


def test_adelia_pyrotechnics_card_activates() -> None:
    body = _adelia_knowledge_card("pyrotechnics", "Stampede fire pyro")
    assert len(body) > 50


def test_adelia_pyrotechnics_card_blast_radius() -> None:
    body = _adelia_knowledge_card("pyrotechnics", "Stampede fire")
    assert "blast radius" in body.lower()


def test_adelia_pyrotechnics_card_mortar_rack() -> None:
    body = _adelia_knowledge_card("pyrotechnics", "mortar fire")
    assert "mortar rack" in body.lower() or "mortar" in body.lower()


def test_adelia_pyrotechnics_card_stampede() -> None:
    body = _adelia_knowledge_card("pyrotechnics", "Calgary Stampede")
    assert "Stampede" in body


def test_adelia_pyrotechnics_card_certified_supervisor() -> None:
    body = _adelia_knowledge_card("pyrotechnics", "Stampede firing")
    assert "certified supervisor" in body.lower()


# ---------------------------------------------------------------------------
# Voice mode coverage — all 6 required modes
# ---------------------------------------------------------------------------


def test_adelia_voice_covers_domestic_mode() -> None:
    examples = load_voice_examples("adelia") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.DOMESTIC in modes


def test_adelia_voice_covers_conflict_mode() -> None:
    examples = load_voice_examples("adelia") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.CONFLICT in modes


def test_adelia_voice_covers_intimate_mode() -> None:
    examples = load_voice_examples("adelia") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.INTIMATE in modes


def test_adelia_voice_covers_group_mode() -> None:
    examples = load_voice_examples("adelia") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.GROUP in modes


def test_adelia_voice_covers_solo_pair_mode() -> None:
    examples = load_voice_examples("adelia") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.SOLO_PAIR in modes


def test_adelia_voice_covers_silent_mode() -> None:
    """Silent mode is J.2-critical — near-silent seismograph response is canonical."""
    examples = load_voice_examples("adelia") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.SILENT in modes, "Adelia Voice.md must have a silent mode exemplar"


# ---------------------------------------------------------------------------
# Cross-character contamination negatives
# ---------------------------------------------------------------------------


def test_adelia_kernel_no_bina_markers() -> None:
    kernel = _adelia_kernel()
    assert "samovar" not in kernel
    assert "Circuit Pair" not in kernel
    assert "Urmia" not in kernel


def test_adelia_kernel_no_reina_markers() -> None:
    kernel = _adelia_kernel()
    assert "Cuatrecasas" not in kernel
    assert "Bishop" not in kernel


def test_adelia_kernel_no_alicia_markers() -> None:
    kernel = _adelia_kernel()
    assert "Famaill" not in kernel
    assert "Mercedes Sosa" not in kernel
    assert "Canciller" not in kernel


# ---------------------------------------------------------------------------
# Parametrized required-concept sweeps
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("concept", [
    "Entangled Pair",
    "Intuitive Symbiosis",
    "complementary cognitive interlock",
    "fragmented plans handoff",
    "the Compass and the Gravity",
    "structural safety",
])
def test_adelia_pair_card_required_concept(concept: str) -> None:
    card = _adelia_pair_card()
    assert concept.lower() in card.lower(), \
        f"Required concept missing from Adelia pair card: '{concept}'"


@pytest.mark.parametrize("concept", [
    "Valencian-Australian",
    "Marrickville",
    "kitchen Spanish",
    "Virgen de los Desamparados",
    "Joaquin Raye",
])
def test_adelia_cultural_card_required_concept(concept: str) -> None:
    body = _adelia_knowledge_card("cultural", "Valencia Marrickville Spanish Joaquin")
    assert concept.lower() in body.lower(), \
        f"Required concept missing from Adelia cultural card: '{concept}'"


@pytest.mark.parametrize("concept", [
    "Manchester warehouse",
    "Ozone and Ember",
    "custom fabrication",
    "penetration testing",
    "the Compass",
])
def test_adelia_workshop_card_required_concept(concept: str) -> None:
    body = _adelia_knowledge_card("workshop", "warehouse commission Compass pen test")
    assert concept.lower() in body.lower(), \
        f"Required concept missing from Adelia workshop card: '{concept}'"


@pytest.mark.parametrize("concept", [
    "Ozone and Ember",
    "mortar rack",
    "blast radius",
    "Calgary Stampede",
    "certified supervisor",
])
def test_adelia_pyrotechnics_card_required_concept(concept: str) -> None:
    body = _adelia_knowledge_card(
        "pyrotechnics", "Stampede fire pyro mortar blast"
    )
    assert concept.lower() in body.lower(), \
        f"Required concept missing from Adelia pyrotechnics card: '{concept}'"
