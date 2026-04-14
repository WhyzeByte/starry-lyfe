"""Phase H / Phase J.4 soul regression tests for Alicia Marin.

Verifies canonical architecture, soul card content, voice mode coverage,
and cross-character contamination for Alicia.

J.4 critical audit findings (highest architectural impact):
- 'The Duality' and 'Complete Jungian Duality' must be in assembled prompt
- 'Sun Override' and 'Four-Phase Return' must be in assembled prompt
- warm_refusal and group_temperature modes are audit-driven additions
- Alicia and Reina must remain distinguishable (Se-dominant non-redundancy)
- Communication-mode constraint substitution (Phase A'') must hold
- 'no costume Argentineness' — no performance of Argentine identity
"""

from __future__ import annotations

import pytest

from starry_lyfe.context.kernel_loader import load_kernel, load_voice_examples
from starry_lyfe.context.soul_cards import find_activated_cards
from starry_lyfe.context.types import SceneState, VoiceMode


def _alicia_kernel(budget: int = 9000) -> str:
    return load_kernel("alicia", budget=budget)


def _alicia_pair_card() -> str:
    cards = find_activated_cards("alicia", SceneState())
    pair = [c for c in cards if c.card_type == "pair"]
    assert pair, "Alicia pair soul card must activate"
    return pair[0].body


def _alicia_knowledge_card(keyword: str, scene_desc: str = "",
                           comm_mode: str | None = None) -> str:
    cards = find_activated_cards(
        "alicia",
        SceneState(scene_description=scene_desc),
        communication_mode=comm_mode,
    )
    matched = [c for c in cards if keyword in c.file_path.lower()]
    assert matched, f"Alicia '{keyword}' card must activate (scene='{scene_desc}', comm={comm_mode})"
    return matched[0].body

# ---------------------------------------------------------------------------
# Pair architecture — kernel level
# ---------------------------------------------------------------------------


def test_alicia_kernel_carries_solstice_pair_name() -> None:
    kernel = _alicia_kernel()
    assert "Solstice Pair" in kernel
    assert "Elemental Pair" not in kernel  # old v7.0 name


def test_alicia_kernel_carries_sun_override() -> None:
    """Sun Override is the canonical body-regulation protocol for Alicia."""
    assert "Sun Override" in _alicia_kernel()


def test_alicia_kernel_carries_famailla() -> None:
    """Famaillá is Alicia's canonical birthplace — must be in kernel."""
    kernel = _alicia_kernel()
    assert "Famaill" in kernel  # matches Famaillá with or without encoding


def test_alicia_kernel_carries_tucuman() -> None:
    kernel = _alicia_kernel()
    assert "Tucum" in kernel  # matches Tucumán


def test_alicia_kernel_carries_lucía_vega_case() -> None:
    """The Lucía Vega case is load-bearing motivation — must be in kernel."""
    assert "Vega" in _alicia_kernel()


def test_alicia_kernel_carries_cancilleria() -> None:
    assert "Canciller" in _alicia_kernel()


def test_alicia_kernel_no_truncation() -> None:
    assert "[Kernel trimmed to token budget.]" not in _alicia_kernel()


# ---------------------------------------------------------------------------
# Pair soul card — J.4 critical concepts
# ---------------------------------------------------------------------------


def test_alicia_pair_card_loads() -> None:
    assert len(_alicia_pair_card()) > 100


def test_alicia_pair_card_the_duality() -> None:
    """J.4 critical: 'The Duality' must be in pair card."""
    assert "The Duality" in _alicia_pair_card() or "the Duality" in _alicia_pair_card()


def test_alicia_pair_card_complete_jungian_duality() -> None:
    """J.4 critical: 'Complete Jungian Duality' is the pair classification."""
    assert "Complete Jungian Duality" in _alicia_pair_card()


def test_alicia_pair_card_inferior_function_gift_exchange() -> None:
    """Inferior-function gift exchange is the pair mechanism."""
    assert "inferior-function gift exchange" in _alicia_pair_card().lower()


def test_alicia_pair_card_polyvagal_co_regulation() -> None:
    """Polyvagal co-regulation is the mechanistic description of the Sun Override."""
    assert "polyvagal" in _alicia_pair_card().lower()


def test_alicia_pair_card_sun_override() -> None:
    assert "Sun Override" in _alicia_pair_card()


def test_alicia_pair_card_mercedes_sosa() -> None:
    """Mercedes Sosa is canonical in Alicia's interior life."""
    assert "Mercedes Sosa" in _alicia_pair_card()


def test_alicia_pair_card_no_old_pair_name() -> None:
    assert "Elemental Pair" not in _alicia_pair_card()

# ---------------------------------------------------------------------------
# Operational soul card — Four-Phase Return (J.4 gap now fixed)
# ---------------------------------------------------------------------------


def test_alicia_operational_card_activates() -> None:
    body = _alicia_knowledge_card("operational", "operation Cancilleria Caracas consular")
    assert len(body) > 50


def test_alicia_operational_card_four_phase_return() -> None:
    """J.4 gap remediation: Four-Phase Return must now be in the operational card."""
    body = _alicia_knowledge_card("operational", "operation Cancilleria consular")
    assert "Four-Phase Return" in body


def test_alicia_operational_card_cancilleria() -> None:
    body = _alicia_knowledge_card("operational", "Cancilleria operation consular")
    assert "Canciller" in body


def test_alicia_operational_card_isen() -> None:
    body = _alicia_knowledge_card("operational", "ISEN operation")
    assert "ISEN" in body


def test_alicia_operational_card_unidad() -> None:
    body = _alicia_knowledge_card("operational", "operation Cancilleria Caracas")
    assert "Unidad de Respuesta Consular" in body


# ---------------------------------------------------------------------------
# Famailla soul card
# ---------------------------------------------------------------------------


def test_alicia_famailla_card_activates() -> None:
    body = _alicia_knowledge_card("famailla", "Famailla Tucuman lemon zafra")
    assert len(body) > 50


def test_alicia_famailla_card_mercedes_sosa() -> None:
    body = _alicia_knowledge_card("famailla", "Famailla Tucuman zafra Ramon")
    assert "Mercedes Sosa" in body


def test_alicia_famailla_card_zafra() -> None:
    body = _alicia_knowledge_card("famailla", "Famailla Tucuman zafra")
    assert "zafra" in body.lower()


def test_alicia_famailla_card_ramon_marin() -> None:
    body = _alicia_knowledge_card("famailla", "Ramon Famailla")
    assert "Ramon" in body


def test_alicia_famailla_card_pilar_marin() -> None:
    body = _alicia_knowledge_card("famailla", "Pilar Famailla lemon")
    assert "Pilar" in body


# ---------------------------------------------------------------------------
# Rioplatense soul card
# ---------------------------------------------------------------------------


def test_alicia_rioplatense_card_activates() -> None:
    body = _alicia_knowledge_card("rioplatense", "Spanish Rioplatense voseo zamba")
    assert len(body) > 50


def test_alicia_rioplatense_card_voseo() -> None:
    body = _alicia_knowledge_card("rioplatense", "voseo Spanish Argentina")
    assert "voseo" in body.lower()


def test_alicia_rioplatense_card_mercedes_sosa() -> None:
    body = _alicia_knowledge_card("rioplatense", "Mercedes Sosa zamba")
    assert "Mercedes Sosa" in body


def test_alicia_rioplatense_card_no_costume() -> None:
    """'No costume Argentineness' is the canonical register discipline rule."""
    body = _alicia_knowledge_card("rioplatense", "Spanish Argentina zamba")
    assert "no costume" in body.lower()


# ---------------------------------------------------------------------------
# Remote soul card (Phase A'' activation)
# ---------------------------------------------------------------------------


def test_alicia_remote_card_activates_on_phone() -> None:
    body = _alicia_knowledge_card("remote", comm_mode="phone")
    assert len(body) > 50


def test_alicia_remote_card_activates_on_letter() -> None:
    body = _alicia_knowledge_card("remote", comm_mode="letter")
    assert len(body) > 50

# ---------------------------------------------------------------------------
# Voice mode coverage — all 6 required modes
# ---------------------------------------------------------------------------


def test_alicia_voice_covers_solo_pair() -> None:
    examples = load_voice_examples("alicia") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.SOLO_PAIR in modes


def test_alicia_voice_covers_silent() -> None:
    examples = load_voice_examples("alicia") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.SILENT in modes


def test_alicia_voice_covers_intimate() -> None:
    examples = load_voice_examples("alicia") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.INTIMATE in modes


def test_alicia_voice_covers_repair() -> None:
    examples = load_voice_examples("alicia") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.REPAIR in modes


def test_alicia_voice_covers_warm_refusal() -> None:
    """Warm refusal is audit-driven — operational security gate is canonical."""
    examples = load_voice_examples("alicia") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.WARM_REFUSAL in modes


def test_alicia_voice_covers_group_temperature() -> None:
    """Group temperature is audit-driven — temperature-change-in-group function."""
    examples = load_voice_examples("alicia") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.GROUP_TEMPERATURE in modes


def test_alicia_voice_has_phone_exemplar() -> None:
    """Phase A'': at least one phone-tagged exemplar must exist."""
    examples = load_voice_examples("alicia") or []
    phone = [ex for ex in examples if ex.communication_mode == "phone"]
    assert len(phone) >= 2, f"Need ≥2 phone exemplars, found {len(phone)}"


def test_alicia_voice_has_letter_exemplar() -> None:
    """Phase A'': at least two letter-tagged exemplars must exist."""
    examples = load_voice_examples("alicia") or []
    letters = [ex for ex in examples if ex.communication_mode == "letter"]
    assert len(letters) >= 2, f"Need ≥2 letter exemplars, found {len(letters)}"


def test_alicia_voice_has_video_exemplar() -> None:
    """Phase A'': at least one video-call-tagged exemplar must exist."""
    examples = load_voice_examples("alicia") or []
    video = [ex for ex in examples if ex.communication_mode == "video_call"]
    assert len(video) >= 1, f"Need ≥1 video_call exemplar, found {len(video)}"


# ---------------------------------------------------------------------------
# Cross-character contamination negatives
# ---------------------------------------------------------------------------


def test_alicia_kernel_no_bina_markers() -> None:
    kernel = _alicia_kernel()
    assert "samovar" not in kernel
    assert "Circuit Pair" not in kernel
    assert "Urmia" not in kernel


def test_alicia_kernel_no_adelia_markers() -> None:
    kernel = _alicia_kernel()
    assert "Marrickville" not in kernel
    assert "Ozone and Ember" not in kernel


def test_alicia_kernel_no_reina_markers() -> None:
    kernel = _alicia_kernel()
    assert "Cuatrecasas" not in kernel
    assert "Bishop" not in kernel


# ---------------------------------------------------------------------------
# Reina + Alicia non-redundancy (the highest-stakes check in the suite)
# ---------------------------------------------------------------------------


def test_reina_and_alicia_kernel_distinguishable() -> None:
    """Two Se-dominants must have disjoint canonical concept sets."""
    alicia_k = _alicia_kernel()
    from starry_lyfe.context.kernel_loader import load_kernel as lk
    reina_k = lk("reina", budget=10000)

    # Alicia-specific concepts absent from Reina
    assert "Famaill" in alicia_k
    assert "Famaill" not in reina_k
    assert "Canciller" in alicia_k
    assert "Canciller" not in reina_k
    assert "Solstice" in alicia_k
    assert "Solstice" not in reina_k

    # Reina-specific concepts absent from Alicia
    assert "Gracia" in reina_k
    assert "Gracia" not in alicia_k
    assert "Cuatrecasas" in reina_k
    assert "Cuatrecasas" not in alicia_k


# ---------------------------------------------------------------------------
# Parametrized required-concept sweeps
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("concept", [
    "Solstice Pair",
    "Complete Jungian Duality",
    "inferior-function gift exchange",
    "polyvagal co-regulation",
    "the Duality",
])
def test_alicia_pair_card_required_concept(concept: str) -> None:
    card = _alicia_pair_card()
    assert concept.lower() in card.lower(), \
        f"Required concept missing from Alicia pair card: '{concept}'"


@pytest.mark.parametrize("concept", [
    "Cancillería",
    "Consejera de Embajada",
    "ISEN",
    "Unidad de Respuesta Consular",
    "Palacio San Martín",
    "Four-Phase Return",
])
def test_alicia_operational_card_required_concept(concept: str) -> None:
    body = _alicia_knowledge_card(
        "operational", "operation Cancilleria Caracas consular ISEN"
    )
    assert concept.lower() in body.lower(), \
        f"Required concept missing from Alicia operational card: '{concept}'"


@pytest.mark.parametrize("concept", [
    "Famaillá", "Tucumán", "lemon-packing plant", "zafra",
    "Ramon Marin", "Pilar Marin",
])
def test_alicia_famailla_card_required_concept(concept: str) -> None:
    body = _alicia_knowledge_card(
        "famailla", "Famailla Tucuman lemon zafra Ramon Pilar"
    )
    assert concept.lower() in body.lower(), \
        f"Required concept missing from Alicia famailla card: '{concept}'"


@pytest.mark.parametrize("concept", [
    "Rioplatense", "voseo", "che", "Mercedes Sosa",
    "zamba", "no costume Argentineness",
])
def test_alicia_rioplatense_card_required_concept(concept: str) -> None:
    body = _alicia_knowledge_card(
        "rioplatense", "Spanish Rioplatense voseo Mercedes Sosa zamba Argentina"
    )
    assert concept.lower() in body.lower(), \
        f"Required concept missing from Alicia rioplatense card: '{concept}'"
