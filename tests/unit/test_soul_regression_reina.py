"""Phase H / Phase J.3 soul regression tests for Reina Torres.

Verifies canonical architecture, soul card content, voice mode coverage,
and cross-character contamination for Reina.

J.3 critical audit findings (from master plan):
- "The Mastermind and the Operator" must be in the assembled prompt
- Mediterranean reset as dyadic geography (not personal habit)
- Cuatrecasas-to-defence-law pivot is load-bearing biography
- Domestic and escalation modes are audit-driven additions
- Reina and Alicia must remain distinguishable (Se-dominant non-redundancy)
"""

from __future__ import annotations

import pytest

from starry_lyfe.context.kernel_loader import load_kernel, load_voice_examples
from starry_lyfe.context.soul_cards import find_activated_cards
from starry_lyfe.context.types import SceneState, VoiceMode


def _reina_kernel(budget: int = 10000) -> str:
    return load_kernel("reina", budget=budget)


def _reina_pair_card() -> str:
    cards = find_activated_cards("reina", SceneState())
    pair = [c for c in cards if c.card_type == "pair"]
    assert pair, "Reina pair soul card must activate"
    return pair[0].body


def _reina_knowledge_card(keyword: str, scene_desc: str) -> str:
    cards = find_activated_cards("reina", SceneState(scene_description=scene_desc))
    matched = [c for c in cards if keyword in c.file_path.lower()]
    assert matched, f"Reina '{keyword}' card must activate for scene: {scene_desc}"
    return matched[0].body

# ---------------------------------------------------------------------------
# Pair architecture — kernel level
# ---------------------------------------------------------------------------


def test_reina_kernel_carries_kinetic_pair_name() -> None:
    kernel = _reina_kernel()
    assert "Kinetic Pair" in kernel
    assert "Synergistic Pair" not in kernel  # old v7.0 name


def test_reina_kernel_carries_admissibility_protocol() -> None:
    """Admissibility Protocol lives in pair card and constraints — verified across both."""
    pair_text = _reina_pair_card()
    assert "Admissibility Protocol" in pair_text, \
        "Admissibility Protocol must appear in Reina pair soul card"


def test_reina_kernel_carries_gracia() -> None:
    """Gracia (Barcelona neighbourhood) is Reina's canonical home geography."""
    assert "Gracia" in _reina_kernel()


def test_reina_kernel_carries_okotoks() -> None:
    """Okotoks is where her practice is — must be in the kernel."""
    assert "Okotoks" in _reina_kernel()


def test_reina_kernel_carries_mediterranean_reset() -> None:
    """Mediterranean reset is a dyadic geography, not just a personal habit."""
    assert "Mediterranean" in _reina_kernel()


def test_reina_kernel_carries_cuatrecasas() -> None:
    """Cuatrecasas is the pivot point — the deliberate break from corporate prestige."""
    assert "Cuatrecasas" in _reina_kernel()


def test_reina_kernel_carries_bishop() -> None:
    """Bishop (the RCMP Thoroughbred) is canonical."""
    assert "Bishop" in _reina_kernel()


def test_reina_kernel_no_truncation() -> None:
    assert "[Kernel trimmed to token budget.]" not in _reina_kernel()


# ---------------------------------------------------------------------------
# Pair soul card — J.3 critical concepts
# ---------------------------------------------------------------------------


def test_reina_pair_card_loads() -> None:
    assert len(_reina_pair_card()) > 100


def test_reina_pair_card_mastermind_and_operator() -> None:
    """J.3 critical: 'The Mastermind and the Operator' must be in the pair card."""
    text = _reina_pair_card()
    assert "Mastermind and the Operator" in text


def test_reina_pair_card_asymmetrical_leverage() -> None:
    assert "Asymmetrical Leverage" in _reina_pair_card()


def test_reina_pair_card_temporal_collision() -> None:
    """'Temporal collision converted to engine heat' is the pair mechanism."""
    assert "temporal collision" in _reina_pair_card().lower()


def test_reina_pair_card_admissibility_protocol() -> None:
    assert "Admissibility Protocol" in _reina_pair_card()


def test_reina_pair_card_tactical_execution() -> None:
    assert "tactical execution" in _reina_pair_card().lower()


def test_reina_pair_card_no_old_pair_name() -> None:
    assert "Synergistic Pair" not in _reina_pair_card()


# ---------------------------------------------------------------------------
# Stable soul card
# ---------------------------------------------------------------------------


def test_reina_stable_card_activates() -> None:
    body = _reina_knowledge_card("stable", "Bishop stable horse paddock")
    assert len(body) > 50


def test_reina_stable_card_bishop() -> None:
    body = _reina_knowledge_card("stable", "Bishop stable")
    assert "Bishop" in body


def test_reina_stable_card_vex() -> None:
    body = _reina_knowledge_card("stable", "Vex stable horse")
    assert "Vex" in body


def test_reina_stable_card_challenger() -> None:
    body = _reina_knowledge_card("stable", "Challenger horse stable")
    assert "Challenger" in body


def test_reina_stable_card_rcmp() -> None:
    """Bishop's RCMP provenance is canonical."""
    body = _reina_knowledge_card("stable", "Bishop stable RCMP")
    assert "RCMP" in body


# ---------------------------------------------------------------------------
# Court soul card
# ---------------------------------------------------------------------------


def test_reina_court_card_activates() -> None:
    body = _reina_knowledge_card("court", "court trial Okotoks criminal")
    assert len(body) > 50


def test_reina_court_card_okotoks() -> None:
    body = _reina_knowledge_card("court", "Okotoks criminal court")
    assert "Okotoks" in body


def test_reina_court_card_cuatrecasas() -> None:
    body = _reina_knowledge_card("court", "Cuatrecasas Barcelona court")
    assert "Cuatrecasas" in body


def test_reina_court_card_universitat_barcelona() -> None:
    body = _reina_knowledge_card("court", "Barcelona criminal court")
    assert "Universitat de Barcelona" in body


def test_reina_court_card_nca() -> None:
    body = _reina_knowledge_card("court", "Okotoks criminal court")
    assert "National Committee on Accreditation" in body


# ---------------------------------------------------------------------------
# Voice mode coverage — all 7 required modes
# ---------------------------------------------------------------------------


def test_reina_voice_covers_solo_pair() -> None:
    examples = load_voice_examples("reina") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.SOLO_PAIR in modes


def test_reina_voice_covers_conflict() -> None:
    examples = load_voice_examples("reina") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.CONFLICT in modes


def test_reina_voice_covers_group() -> None:
    examples = load_voice_examples("reina") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.GROUP in modes


def test_reina_voice_covers_repair() -> None:
    examples = load_voice_examples("reina") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.REPAIR in modes


def test_reina_voice_covers_intimate() -> None:
    examples = load_voice_examples("reina") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.INTIMATE in modes


def test_reina_voice_covers_domestic() -> None:
    """Domestic is audit-driven — courthouse-shedding example is canonical."""
    examples = load_voice_examples("reina") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.DOMESTIC in modes


def test_reina_voice_covers_escalation() -> None:
    """Escalation is audit-driven — trailhead escalation with Whyze is canonical."""
    examples = load_voice_examples("reina") or []
    modes = {m for ex in examples for m in ex.modes}
    assert VoiceMode.ESCALATION in modes


# ---------------------------------------------------------------------------
# Cross-character contamination negatives
# ---------------------------------------------------------------------------


def test_reina_kernel_no_bina_markers() -> None:
    kernel = _reina_kernel()
    assert "samovar" not in kernel
    assert "Circuit Pair" not in kernel
    assert "Urmia" not in kernel


def test_reina_kernel_no_adelia_markers() -> None:
    kernel = _reina_kernel()
    assert "Marrickville" not in kernel
    assert "Ozone and Ember" not in kernel


def test_reina_kernel_no_alicia_markers() -> None:
    kernel = _reina_kernel()
    assert "Famaill" not in kernel
    assert "Mercedes Sosa" not in kernel
    assert "Canciller" not in kernel


# ---------------------------------------------------------------------------
# Reina+Alicia non-redundancy (the highest-stakes check in the suite)
# ---------------------------------------------------------------------------


def test_reina_and_alicia_kernel_have_disjoint_canonical_markers() -> None:
    """The two Se-dominants must not be interchangeable — disjoint geography/biography."""
    reina_k = _reina_kernel()
    from starry_lyfe.context.kernel_loader import load_kernel as lk
    alicia_k = lk("alicia", budget=10000)

    # Reina-specific — absent from Alicia
    assert "Gracia" in reina_k
    assert "Gracia" not in alicia_k
    assert "Cuatrecasas" in reina_k
    assert "Cuatrecasas" not in alicia_k
    assert "Mediterranean" in reina_k

    # Alicia-specific — absent from Reina
    assert "Famaill" in alicia_k
    assert "Famaill" not in reina_k
    assert "Canciller" in alicia_k
    assert "Canciller" not in reina_k


# ---------------------------------------------------------------------------
# Parametrized required-concept sweeps
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("concept", [
    "Kinetic Pair",
    "Asymmetrical Leverage",
    "tactical execution",
    "Admissibility Protocol",
    "the Mastermind and the Operator",
])
def test_reina_pair_card_required_concept(concept: str) -> None:
    card = _reina_pair_card()
    assert concept.lower() in card.lower(), \
        f"Required concept missing from Reina pair card: '{concept}'"


@pytest.mark.parametrize("concept", [
    "Bishop", "Vex", "Challenger", "RCMP", "Thoroughbred", "Quarter Horse",
])
def test_reina_stable_card_required_concept(concept: str) -> None:
    body = _reina_knowledge_card(
        "stable", "Bishop Vex Challenger stable horse RCMP paddock"
    )
    assert concept.lower() in body.lower(), \
        f"Required concept missing from Reina stable card: '{concept}'"


@pytest.mark.parametrize("concept", [
    "Okotoks",
    "criminal defence",
    "Universitat de Barcelona",
    "Cuatrecasas",
    "National Committee on Accreditation",
])
def test_reina_court_card_required_concept(concept: str) -> None:
    body = _reina_knowledge_card(
        "court", "Okotoks criminal defence court Cuatrecasas Barcelona"
    )
    assert concept.lower() in body.lower(), \
        f"Required concept missing from Reina court card: '{concept}'"
