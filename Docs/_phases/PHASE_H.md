# PHASE_H — Soul Regression Tests (Cross-Character Non-Redundancy)

**Status:** SHIPPED
**Shipped:** 2026-04-13
**Authored by:** Claude AI (direct remediation authority — canonical regression suite)

---

## Phase Summary

Phase H is the machine-verifiable form of Vision §5's non-redundancy guarantee:
*"No woman is substitutable for another."*

Both Reina Torres and Alicia Marin are Se-dominant. Without active enforcement they risk collapsing into "two warm body-readers." Phase H creates the dedicated regression guard that catches drift at the kernel level, the pair soul card level, and the prose renderer level.

---

## Step 2: Execute

### Files created

- `tests/unit/test_reina_alicia_nonduplicate.py` — 31 tests, the dedicated non-redundancy invariant file
- `tests/unit/test_soul_regression_bina.py` — 48 tests, Bina J.1 regression bundle
- `tests/unit/test_soul_regression_adelia.py` — 60 tests, Adelia J.2 regression bundle
- `tests/unit/test_soul_regression_reina.py` — 52 tests, Reina J.3 regression bundle
- `tests/unit/test_soul_regression_alicia.py` — 67 tests, Alicia J.4 regression bundle

### Test structure: `test_reina_alicia_nonduplicate.py`

| Layer | Tests | What it guards |
|---|---|---|
| Kernel | 16 | Geography, pair name, biography disjoint between Reina and Alicia |
| Pair card | 13 | Cognitive mechanism distinctness (Kinetic vs Solstice) |
| Prose renderer | 2 | Trust and fatigue prose produce different language per character |

### Crown test

`test_se_dominant_pair_cards_are_not_interchangeable` — sweeps 5 Reina-only concepts and 5 Alicia-only concepts, asserts each is present in the right card and absent from the wrong one. The most load-bearing single test in the suite.

### Authoring remediations during J.1–J.4 execution

| Phase | Card | Gap | Fix |
|---|---|---|---|
| J.2 | `adelia_entangled.md` | "structural safety" absent from both kernel and soul card | Added sentence + required_concept |
| J.3 | `reina_kinetic.md` | "temporal collision" not in body | Added "temporal collision converted to engine heat" |
| J.4 | `alicia_operational.md` | "Four-Phase Return" not in any card | Authored Four-Phase Return protocol section |

---

## Step 5: QA

**Verdict: APPROVED FOR SHIP**

All 31 non-redundancy tests pass. All 227 J.1–J.4 character regression tests pass. The Se-dominant pair card swap test verifies 10 concept-presence assertions in both directions simultaneously. The prose renderer tests confirm Reina and Alicia produce detectably different language at the same numeric trust/fatigue values.

Kernel-level contamination checks cover all four cross-character directions. No false positives observed. ruff clean, mypy clean.

---

## Step 6: Ship

**Decision: SHIPPED — 2026-04-13**
