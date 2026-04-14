"""Phase H: Reina + Alicia Non-Redundancy Invariant.

The highest-stakes single test in the Starry-Lyfe regression suite.

Both Reina and Alicia are Se-dominant. Without active enforcement they risk
collapsing into 'two warm body-readers' — generic assertive physical presence
without the distinct cognitive signatures, geographic substrates, professional
registers, and pair architectures that make them non-substitutable.

This file is the dedicated regression guard for Vision §5 non-redundancy:
    'No woman is substitutable for another.'

Test strategy: kernel + pair soul card level (no PostgreSQL required).
At the runtime layer, J.3 and J.4 inline tests also verify non-redundancy.
This file is the formal stand-alone record mandated by Phase H spec §12.
"""

from __future__ import annotations

from starry_lyfe.context.kernel_loader import load_kernel
from starry_lyfe.context.soul_cards import find_activated_cards
from starry_lyfe.context.types import SceneState


def _kernel(char: str) -> str:
    return load_kernel(char, budget=10000)


def _pair_card(char: str) -> str:
    cards = find_activated_cards(char, SceneState())
    pair = [c for c in cards if c.card_type == "pair"]
    assert pair
    return pair[0].body

# ---------------------------------------------------------------------------
# Kernel-level non-redundancy
# ---------------------------------------------------------------------------


def test_reina_kernel_has_kinetic_pair() -> None:
    assert "Kinetic Pair" in _kernel("reina")


def test_alicia_kernel_has_no_kinetic_pair() -> None:
    assert "Kinetic Pair" not in _kernel("alicia")


def test_alicia_kernel_has_solstice_pair() -> None:
    assert "Solstice Pair" in _kernel("alicia")


def test_reina_kernel_has_no_solstice_pair() -> None:
    assert "Solstice Pair" not in _kernel("reina")


def test_reina_kernel_has_cuatrecasas() -> None:
    assert "Cuatrecasas" in _kernel("reina")


def test_alicia_kernel_has_no_cuatrecasas() -> None:
    assert "Cuatrecasas" not in _kernel("alicia")


def test_alicia_kernel_has_famailla() -> None:
    assert "Famaill" in _kernel("alicia")


def test_reina_kernel_has_no_famailla() -> None:
    assert "Famaill" not in _kernel("reina")


def test_reina_kernel_has_mediterranean_reset() -> None:
    """Mediterranean reset is Reina's specific dyadic geography — not a generic term."""
    assert "Mediterranean" in _kernel("reina")


def test_alicia_kernel_has_no_mediterranean_reset() -> None:
    """Alicia's kernel may use 'Mediterranean' as a negation; 'Mediterranean reset' must not appear."""
    assert "Mediterranean reset" not in _kernel("alicia")


def test_alicia_kernel_has_cancilleria() -> None:
    assert "Canciller" in _kernel("alicia")


def test_reina_kernel_has_no_cancilleria() -> None:
    assert "Canciller" not in _kernel("reina")


def test_reina_kernel_has_gracia() -> None:
    assert "Gracia" in _kernel("reina")


def test_alicia_kernel_has_no_gracia() -> None:
    assert "Gracia" not in _kernel("alicia")


def test_alicia_kernel_has_tucuman() -> None:
    assert "Tucum" in _kernel("alicia")


def test_reina_kernel_has_no_tucuman() -> None:
    assert "Tucum" not in _kernel("reina")

# ---------------------------------------------------------------------------
# Pair card-level non-redundancy — cognitive mechanism distinctness
# ---------------------------------------------------------------------------


def test_reina_pair_card_has_asymmetrical_leverage() -> None:
    assert "Asymmetrical Leverage" in _pair_card("reina")


def test_alicia_pair_card_has_no_asymmetrical_leverage() -> None:
    assert "Asymmetrical Leverage" not in _pair_card("alicia")


def test_alicia_pair_card_has_complete_jungian_duality() -> None:
    assert "Complete Jungian Duality" in _pair_card("alicia")


def test_reina_pair_card_has_no_jungian_duality() -> None:
    assert "Complete Jungian Duality" not in _pair_card("reina")


def test_reina_pair_card_has_admissibility_protocol() -> None:
    assert "Admissibility Protocol" in _pair_card("reina")


def test_alicia_pair_card_has_no_admissibility_protocol() -> None:
    assert "Admissibility Protocol" not in _pair_card("alicia")


def test_alicia_pair_card_has_sun_override() -> None:
    assert "Sun Override" in _pair_card("alicia")


def test_reina_pair_card_has_no_sun_override() -> None:
    assert "Sun Override" not in _pair_card("reina")


def test_reina_pair_card_has_mastermind_and_operator() -> None:
    assert "Mastermind and the Operator" in _pair_card("reina")


def test_alicia_pair_card_has_no_mastermind_and_operator() -> None:
    assert "Mastermind and the Operator" not in _pair_card("alicia")


def test_alicia_pair_card_has_polyvagal() -> None:
    assert "polyvagal" in _pair_card("alicia").lower()


def test_reina_pair_card_has_no_polyvagal() -> None:
    assert "polyvagal" not in _pair_card("reina").lower()


# ---------------------------------------------------------------------------
# The Mastermind test — the single most important non-redundancy assertion
# ---------------------------------------------------------------------------


def test_se_dominant_pair_cards_are_not_interchangeable() -> None:
    """The core Vision §5 non-redundancy guarantee at the pair architecture level.

    If you swapped Reina and Alicia's pair cards, the assembled prompts
    would produce detectably wrong characters. This test verifies the
    content gap is large enough that no swap could go undetected.
    """
    reina_card = _pair_card("reina")
    alicia_card = _pair_card("alicia")

    # Reina concepts absent from Alicia
    reina_only = [
        "Asymmetrical Leverage",
        "Admissibility Protocol",
        "Mastermind and the Operator",
        "temporal collision",
        "tactical execution",
    ]
    for concept in reina_only:
        assert concept.lower() in reina_card.lower(), \
            f"Reina-only concept missing from Reina card: '{concept}'"
        assert concept.lower() not in alicia_card.lower(), \
            f"Reina-only concept leaked into Alicia card: '{concept}'"

    # Alicia concepts absent from Reina
    alicia_only = [
        "Complete Jungian Duality",
        "Sun Override",
        "polyvagal",
        "inferior-function gift exchange",
        "the Duality",
    ]
    for concept in alicia_only:
        assert concept.lower() in alicia_card.lower(), \
            f"Alicia-only concept missing from Alicia card: '{concept}'"
        assert concept.lower() not in reina_card.lower(), \
            f"Alicia-only concept leaked into Reina card: '{concept}'"


# ---------------------------------------------------------------------------
# Prose renderer non-redundancy (Phase G)
# ---------------------------------------------------------------------------


def test_reina_and_alicia_trust_prose_are_distinct() -> None:
    """Trust at the same numeric value renders as different language for each character."""
    from unittest.mock import MagicMock

    from starry_lyfe.context.prose import render_dyad_whyze_prose

    dyad = MagicMock()
    dyad.pair_name = "test"
    dyad.trust = 0.85
    dyad.intimacy = 0.80
    dyad.conflict = 0.05
    dyad.unresolved_tension = 0.08

    reina_prose = render_dyad_whyze_prose("reina", dyad)
    alicia_prose = render_dyad_whyze_prose("alicia", dyad)

    assert reina_prose != alicia_prose
    # Reina: admissibility register
    assert "admissible" in reina_prose.lower()
    # Alicia: body register
    assert "body" in alicia_prose.lower()


def test_reina_and_alicia_fatigue_prose_are_distinct() -> None:
    """High fatigue renders as different language — courthouse vs Ni-grip."""
    from unittest.mock import MagicMock

    from starry_lyfe.context.prose import render_somatic_prose

    state = MagicMock()
    state.fatigue = 0.80
    state.stress_residue = 0.25
    state.injury_residue = 0.00
    state.active_protocols = []

    reina_state = MagicMock(**vars(state))
    reina_state.character_id = "reina"
    reina_state.fatigue = 0.80
    reina_state.stress_residue = 0.25
    reina_state.injury_residue = 0.00
    reina_state.active_protocols = []

    alicia_state = MagicMock()
    alicia_state.character_id = "alicia"
    alicia_state.fatigue = 0.80
    alicia_state.stress_residue = 0.25
    alicia_state.injury_residue = 0.00
    alicia_state.active_protocols = []

    reina_prose = render_somatic_prose("reina", reina_state)
    alicia_prose = render_somatic_prose("alicia", alicia_state)

    assert reina_prose != alicia_prose
    assert "admissibility" in reina_prose.lower() or "spent" in reina_prose.lower()
    assert "ni-grip" in alicia_prose.lower() or "words" in alicia_prose.lower()
