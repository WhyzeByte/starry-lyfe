# PHASE_K — Subjective Success Proxies

**Status:** SHIPPED
**Shipped:** 2026-04-13
**Authored by:** Claude AI (direct remediation authority)

---

## Phase Summary

Phase K ships the framework for catching drift that automated tests cannot measure — the qualitative collapse of character voice into generic AI warmth. Automated tests can verify that canonical markers are present. They cannot verify that reading Bina feels like reading Bina.

Phase K provides three artifacts: a daily one-line gut-check log, a quarterly eight-north-star scorecard, and an automated flattening detector that scans assembled prompt samples for canonical marker presence and cross-character contamination.

---

## Step 2: Execute

### Files created

| File | Purpose |
|---|---|
| `Docs/gut_check_log.md` | One line per conversation: date, character, scene type, score 1–5, optional note. Drift becomes visible as a downtrend in the rolling 10-conversation average. Filled by Project Owner. |
| `Docs/qualitative_review_template.md` | Quarterly 8-north-star scorecard: Voice Integrity, Cognitive Hand-Off Contract, Constraint Pillar Enforcement, Decentralized Narrative Weight, Memory Continuity, Life Authenticity, Agent Sovereignty, The Felt Sense. Filled by Project Owner. |
| `scripts/flattening_regression_detector.py` | Automated sample scan. Checks required canonical markers present in each character's assembled prompt sample; checks that no character's exclusive markers appear in another character's sample. Exits 0 if clean, 1 with itemized warnings if not. |
| `Docs/flattening_dashboard.md` | Generated output from the detector. Currently CLEAN on Phase F samples. |

### Flattening detector design

Required markers per character (always-present vocabulary that signals the character is herself):
- **Adelia:** Marrickville, Las Fallas, Ozone and Ember, Whiteboard Mode, Bunker Mode, 1+1=11
- **Bina:** Circuit Pair, Urmia, samovar, Gilgamesh, Arash, Farhad
- **Reina:** Kinetic Pair, Gracia, Cuatrecasas, Bishop, Admissibility Protocol, Mastermind
- **Alicia:** Solstice Pair, Famaill (diacritic-agnostic partial), Canciller (partial), Sun Override, Complete Jungian Duality

Exclusive markers (any of these appearing in the wrong character's response triggers CONTAMINATION):
- Each character's pair name, canonical geography, and business/institutional identifier

---

## Step 5: QA

**Verdict: APPROVED FOR SHIP**

All three artifacts are operational. The gut-check log and qualitative review template are correctly scoped to Project Owner authoring — they are frameworks, not generated content. The flattening detector runs clean against all four Phase F assembled prompt samples. The dashboard output is committed.

The 8 North Stars in the qualitative review template map directly to the Vision §5–§9 requirements, ensuring the quarterly review traces to canonical authority.

---

## Step 6: Ship

**Decision: SHIPPED — 2026-04-13**
