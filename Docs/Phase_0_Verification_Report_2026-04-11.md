# Phase 0 Verification Report

**Date:** 2026-04-11
**Author:** Claude Code
**Phase file:** `Docs/_phases/PHASE_0.md`
**Master plan reference:** `Docs/IMPLEMENTATION_PLAN_v7.1.md` §3
**State:** COMPLETE — all acceptance criteria MET after 10-commit remediation sequence (`dc085d5`–`b322b1d`); ready for Claude AI QA. *Historical sections §1–§10 below reflect the state at the time of initial verification (pre-remediation); §11 reflects the final post-remediation state. When §1–§10 and §11 disagree, §11 is authoritative.*

---

## 1. Executive Verdict

**[HISTORICAL — SUPERSEDED BY §11]** This section records the Phase 0 state at the time of initial verification (2026-04-11, before the Vision rewrite and the 10-commit remediation sequence). For the final post-remediation verdict, see §11. The text and AC status table below are preserved as the historical snapshot of what the verification originally found; they are no longer an accurate description of the repository state.

**Phase 0 AC status (initial verification, pre-remediation): NOT CLEAN.** The pre-flight canon verification surfaced drift in production character files that was subsequently remediated across commits `dc085d5`–`b322b1d`.

| # | Criterion | Status | Blocking? |
|---:|---|---|---|
| AC1 | Zero drift grep hits across the extended token list | **NOT MET** | yes — 9 hits |
| AC2 | Zero Vision-vs-kernel drifts (or all resolved with written decision) | **NOT MET** | yes — BINA F7 |
| AC3 | Zero canon YAML vs kernel mismatches | **MET** | n/a |
| AC4 | Zero stale Alicia framing | **NOT MET** | yes — overlaps AC1 |

**Additional finding from work item 2 (kernel canonical state):** All four character kernels reference `Persona_Tier_Framework_v7.md` instead of the canonical `Persona_Tier_Framework_v7.1.md`. The referenced file does not exist at the stated path. Four single-line fixes are needed. This is not caught by the §8.1 drift grep because the exact token `_v7.md` (without major version) is not in the token list, but it is explicitly required by work item 2.

**Remediation scope:** approximately 14 edits across 7 files, broken out below. This is larger than the "1-3 commits" estimate in the Step 1 Plan because that estimate was conditioned on the residue grep finding mostly clean state. Claude Code is **not** proceeding to remediation edits until the Project Owner confirms scope in chat.

---

## 2. Methodology

### 2.1 Scope

The drift grep was run across four scopes:
- `src/` (production code and canon YAML)
- `Characters/` (all four v7.1 character kernels, voice files, pair files, knowledge stacks)
- `Vision/` (master vision and per-character directive files)
- `Docs/` (master plan, handoff doc, changelog, phase files, archive)

### 2.2 Token list

The grep used the canonical token list from `Claude_Code_Handoff_v7.1.md` §8.1 plus the three true Reina-audit additions from master plan §3 work item 1. The master plan's list of "six Reina additions" partially overlapped with existing §8.1 entries (`Spanish consular`, `Marín`, `_v7.0.md`), so the genuinely new additions are only three.

Full merged token list (27 tokens):

```
Aliyeh, Bahadori, Laia, Benítez, Hellín, Castilla-La Mancha,
Atlético, MAEUEC, Kingdom of Spain, Spanish consular, Subdirección,
Portuguese-Australian, Golden Pair, Citadel Pair, Synergistic Pair,
Elemental Pair, Adélia, Marín, sheismo, _v7.0.md, _Golden_Pair.md,
_Citadel_Pair.md, _Synergistic_Pair.md, _Elemental_Pair.md,
non-resident, twice yearly between operations, based in Madrid
```

**Plan correction (from Step 1 D1):** My Step 1 Plan flagged `Aliyeh` as a deviation that would add the token to the grep list. This was based on a wrong assumption — I had not yet read `Claude_Code_Handoff_v7.1.md` §8.1 directly. In reality, `Aliyeh` is the FIRST entry in the canonical §8.1 token list and has always been in scope. D1 is withdrawn; no deviation was necessary. The grep as run is exactly what the master plan specifies.

**Prior-conversation memory correction:** A memory note recorded "46 occurrences of `Aliyeh` in Alicia's files" from a prior conversation. This memory is stale — the grep returns zero `Aliyeh` hits in `Characters/Alicia/` (and zero in any non-meta file). The rename was evidently completed in an earlier session and the memory record was not updated. The memory should be retired or superseded after Phase 0 ships.

### 2.3 Exclusions applied

Per `Claude_Code_Handoff_v7.1.md` §8.1 and the master plan §3:

| Excluded path | Reason |
|---|---|
| `Characters/Shawn/` (entire directory) | Shawn/Whyze operator transplant deferred until directive lands; Shawn kernel is deliberately at v7.0 |
| `Vision/Adelia Raye.md`, `Vision/Alicia Marin.md`, `Vision/Bina Malek.md`, `Vision/Reina Torres.md` | Per-character Vision directive files; contain deliberate "v7.0 → v7.1 transplant" narratives |
| `Vision/Starry-Lyfe_Vision_v7.1.md` Appendix A (lines 175+) | Version history section; contains deliberate historical references |
| `Characters/Reina/Reina_Torres_Knowledge_Stack.md:332` (Mercè Benítez household) | Canonical exception per §8.1 — Mercè Benítez is Reina's mother's maiden name |
| `src/starry_lyfe/canon/characters.yaml` Mercè Benítez field | Same canonical exception |
| `src/starry_lyfe/canon/characters.yaml` Shawn profile_file `_v7.0.md` | Shawn is the legitimate `_v7.0.md` exception |
| `Docs/_archive/` (all contents) | Historical audits and archived specs, contain deliberate references to the tokens by design |
| `Docs/_phases/PHASE_0.md` | This phase file contains deliberate references (e.g., quoting the token list) |
| `Docs/Claude_Code_Handoff_v7.1.md` §8.1 | Defines the token list, contains the tokens by design |
| `Docs/CHANGELOG.md` historical entries | Changelog entries record prior drift cleanups, contain tokens by design |
| `Docs/IMPLEMENTATION_PLAN_v7.1.md` specification references | Master plan reproduces the token list in §3; references are meta-spec, not drift |
| `tests/unit/test_residue_grep.py` | Test file that asserts the drift tokens are absent; references tokens by design |

All remaining hits are real drift unless explicitly categorized otherwise in §3.

---

## 3. Work Item 1 — Drift Grep Results

### 3.1 src/ results

| File:Line | Matched token | Status |
|---|---|---|
| `src/starry_lyfe/canon/characters.yaml:116` | `Benítez` | **EXEMPT** — Mercè Benítez is Reina's mother's maiden name (canonical exception) |
| `src/starry_lyfe/canon/characters.yaml:190` | `_v7.0.md` | **EXEMPT** — Shawn `profile_file` reference; Shawn is the legitimate `_v7.0.md` exception |

**src/ verdict: CLEAN.** Zero real drift.

### 3.2 Characters/ results

| File:Line | Matched token(s) | Category | Status |
|---|---|---|---|
| `Characters/Shawn/Shawn_Kroon_Knowledge_Stack.md:142` | `Marín` | Shawn/ excluded | EXEMPT |
| `Characters/Shawn/Shawn_Kroon_Knowledge_Stack.md:259` | (omitted long line) | Shawn/ excluded | EXEMPT |
| `Characters/Shawn/Shawn_Kroon_Knowledge_Stack.md:403` | (omitted long line) | Shawn/ excluded | EXEMPT |
| `Characters/Shawn/Shawn_Kroon_v7.0.md:341` | (omitted long line) | Shawn/ excluded | EXEMPT |
| `Characters/Reina/Reina_Torres_Knowledge_Stack.md:332` | `Benítez` | Mercè Benítez exception | EXEMPT |
| **`Characters/Adelia/Adelia_Raye_Entangled_Pair.md:215`** | **`Elemental Pair`** | **real drift** | **DRIFT HIT 1** |
| **`Characters/Reina/Reina_Torres_Knowledge_Stack.md:308`** | **`Marín`, `non-resident`, `twice yearly`, "operational in Madrid"** | **real drift** | **DRIFT HIT 2** |
| **`Characters/Reina/Reina_Torres_Knowledge_Stack.md:310`** | **`twice-yearly visits`** | **real drift** | **DRIFT HIT 3** |
| **`Characters/Reina/Reina_Torres_Knowledge_Stack.md:405`** | **`Marín`** (in heading) | **real drift** | **DRIFT HIT 4** |
| **`Characters/Reina/Reina_Torres_Knowledge_Stack.md:407`** | **`Marín`, `non-resident`, `twice yearly between operations`, "based in Buenos Aires"** | **real drift** | **DRIFT HIT 5** |
| **`Characters/Reina/Reina_Torres_Knowledge_Stack.md:425`** | **`Marín`, `non-resident`, `Spanish consular`, `based in Madrid`, `twice yearly`, "Racing Club Madrid"** | **real drift — major** | **DRIFT HIT 6** |
| **`Characters/Bina/Bina_Malek_Knowledge_Stack.md:137`** | **`non-resident`, `twice-yearly`** | **real drift** | **DRIFT HIT 7** |
| **`Characters/Bina/Bina_Malek_Knowledge_Stack.md:414`** | **`non-resident`, `twice yearly`, "based in Buenos Aires"** | **real drift** | **DRIFT HIT 8** |
| **`Characters/Reina/Reina_Torres_v7.1.md:228`** | **`Spanish consular`** (as "Spanish consular rooms") | **real drift** | **DRIFT HIT 9** |

**Characters/ verdict: NOT CLEAN.** 9 real drift hits across 4 files (Adelia Entangled Pair file, Reina kernel, Reina Knowledge Stack, Bina Knowledge Stack).

### 3.3 Vision/ results

| File:Line | Matched token(s) | Category | Status |
|---|---|---|---|
| `Vision/Adelia Raye.md:7` | `Portuguese-Australian`, `Atlético` | Per-character directive excluded | EXEMPT |
| `Vision/Adelia Raye.md:38` | `Atlético` | Per-character directive excluded | EXEMPT |
| `Vision/Alicia Marin.md:10` | `Hellín` | Per-character directive excluded | EXEMPT |
| `Vision/Alicia Marin.md:14` | `Hellín`, `Castilla-La Mancha` | Per-character directive excluded | EXEMPT |
| `Vision/Alicia Marin.md:34` | `Atlético` | Per-character directive excluded | EXEMPT |
| `Vision/Bina Malek.md:11` | `Citadel Pair` | Per-character directive excluded | EXEMPT |
| `Vision/Bina Malek.md:38` | `Citadel Pair` | Per-character directive excluded | EXEMPT |
| `Vision/Reina Torres.md:43` | `Synergistic Pair` | Per-character directive excluded | EXEMPT (see note) |
| `Vision/Starry-Lyfe_Vision_v7.1.md:177` | (Appendix A version history) | Appendix exclusion | EXEMPT |
| `Vision/Starry-Lyfe_Vision_v7.1.md:179` | (Appendix A version history) | Appendix exclusion | EXEMPT |
| `Vision/Starry-Lyfe_Vision_v7.1.md:183` | `Golden Pair`, `Citadel Pair`, `Synergistic Pair` | Appendix A version history | EXEMPT |

**Vision/ verdict: CLEAN** for AC1 purposes — all hits are in excluded files or the Appendix A version history section.

**Flag (informational, not blocking):** `Vision/Reina Torres.md:43` — "He is his Synergistic Pair" — this line uses the v7.0 pair name without a "renamed to Kinetic" annotation. The §8.1 exemption for per-character directive files applies to "deliberate 'X is replaced by Y' descriptions of the v7.0 → v7.1 transplant." Line 43 is not such a description; it is a plain assertion. The line is still in an excluded path and therefore exempt for AC1 counting, but if the Project Owner wants the per-character directive files brought to the same canonical-tightness bar as the rest of the codebase, this is where to start. Recommending DEFERRAL to a follow-up phase rather than expanding Phase 0 scope.

### 3.4 Docs/ results

| File:Line | Matched token(s) | Category | Status |
|---|---|---|---|
| `Docs/_phases/PHASE_0.md` (multiple) | many | This phase file — meta references | EXEMPT |
| `Docs/_archive/*` (multiple) | many | Archive — historical | EXEMPT |
| `Docs/CHANGELOG.md:33` | `Aliyeh` | Changelog entry recording prior Aliyeh cleanup | EXEMPT (meta) |
| `Docs/Claude_Code_Handoff_v7.1.md` (multiple) | many | Defines the token list — meta | EXEMPT |
| `Docs/IMPLEMENTATION_PLAN_v7.1.md:55` | Alicia residence framing | Master plan specification reference | EXEMPT (meta) |
| `Docs/IMPLEMENTATION_PLAN_v7.1.md:218-222` | Reina-audit drift tokens | Master plan §3 Phase 0 spec | EXEMPT (meta) |
| `Docs/IMPLEMENTATION_PLAN_v7.1.md:238` | Alicia residence framing | Master plan specification | EXEMPT (meta) |
| `Docs/IMPLEMENTATION_PLAN_v7.1.md:1103` | `Bahadori` | Phase status log resolution record | EXEMPT (meta) |
| `Docs/IMPLEMENTATION_PLAN_v7.1.md:1105` | `Citadel Pair` | Phase status log resolution record | EXEMPT (meta) |
| `Docs/IMPLEMENTATION_PLAN_v7.1.md:1294` | `Citadel Pair` | Test assertion specification — meta | EXEMPT (meta) |

**Docs/ verdict: CLEAN.** All Docs/ hits are legitimate meta-references, historical records, or specification content. Zero real drift in Docs/.

---

## 4. Work Item 2 — Kernel Canonical State

| Check | Adelia | Bina | Reina | Alicia |
|---|---|---|---|---|
| Kernel mentions correct pair name | ✅ Entangled | ✅ Circuit | ✅ Kinetic | ✅ Solstice |
| No stray v7.0 pair names in kernel | ✅ | ✅ | ✅ (except §5 PTF reference) | ✅ |
| Kernel surname matches YAML | ✅ Raye | ✅ Malek | ✅ Torres | ✅ Marin |
| Kernel §3 heading matches canonical pair name | ✅ "Whyze And The Entangled Pair" (line 44) | ✅ "Whyze And The Circuit Pair" (line 50) | ✅ "Whyze And The Kinetic Pair" (line 40) | ✅ "Whyze And The Solstice Pair" (line 36) |
| Kernel §5 references `Persona_Tier_Framework_v7.1.md` | ❌ references `_v7.md` (line 70) | ❌ references `_v7.md` (line 74) | ❌ references `_v7.md` (line 64) | ❌ references `_v7.md` (line 64) |

**Work item 2 verdict: NOT CLEAN.** The four §3 headings are canonical and the surname and pair_name checks pass. But the §5 PTF reference is stale in all four kernels — they point to `Persona_Tier_Framework_v7.md` (no `.1`), a file that does not exist at that path. The canonical file exists at `Docs/Persona_Tier_Framework_v7.1.md`.

This is drift but is not caught by the §8.1 drift grep (the exact token `_v7.md` is not in the list; only `_v7.0.md` is). Work item 2 is the layer that catches it.

**Remediation: four single-line fixes** to update the filename from `Persona_Tier_Framework_v7.md` to `Persona_Tier_Framework_v7.1.md`.

---

## 5. Work Item 3 — Vision-vs-Kernel Consistency

Each character's Vision §5 summary paragraph compared against the kernel §2 Core Identity paragraph.

### 5.1 Adelia

**Vision §5 (line 54):**

> **Adelia Raye (ENFP-A).** Valencian-Australian pyrotechnician-engineer, Gemini Sun, Libra Moon, Taurus Venus.

**Kernel §2 (line 18):**

> I am Adelia Raye. I build fire for a living and meaning for a reason. I am thirty-seven. Born on the fifth of June 1988 in Valencia, on the Mediterranean coast of Spain. My family emigrated to Sydney in 1993 when I was five, and I grew up in the Inner West...

**Verdict: PASS.** Vision compresses the kernel's "born in Valencia, emigrated to Sydney" to "Valencian-Australian"; the compression is accurate. Kernel and canon YAML (`heritage: "Valencian-Australian"`, `birthplace: "Valencia, Spain"`) all align.

### 5.2 Bina

**Vision §5 (line 56):**

> **Bina Malek (ISFJ-A).** Canadian-born Assyrian, Red Seal mechanic, builder of Loth Wolf Hypersport, survivor of an eight-year coercive control relationship. [...]

**Kernel §2 (line 18):**

> I am Bina Malek. Forty. First-generation Assyrian-Iranian Canadian — Assyrian by heritage, Iranian by the nationality stamped on the passport my parents carried out of Urmia. Raised in Edmonton. Red Seal mechanic. [...]

**Kernel §2 (line 24):**

> My parents were Farhad and Shirin Malek. They left Urmia in the early nineties when I was still small enough to fit inside a coat sleeve. [...]

**Verdict: DRIFT (BINA F7).** The Vision says "Canadian-born Assyrian." The kernel says she was born in Urmia, Iran, and was "still small enough to fit inside a coat sleeve" when her parents brought her out in the early nineties. The canon YAML agrees (`birthplace: "Urmia, Iran"`, `raised_in: "Edmonton, Alberta"`, `heritage: "Assyrian-Iranian Canadian"`). The Vision's "Canadian-born" is factually wrong.

**Master plan's recommended resolution:** master plan §3 work item 3 says "Resolve toward 'Canadian-born Assyrian from Urmia' (both true)." Claude Code flags this phrasing as **logically self-contradictory**: "Canadian-born" and "from Urmia" cannot both be true as birth statements. You cannot be born in Canada AND from Urmia in the birth sense.

**AGENTS.md Settled Canon Reminder** (independent authority, higher than master plan in the source-of-truth hierarchy):

> **Bina Malek** — surname is Malek (NOT Bahadori). Iran-born Assyrian-Canadian, born in Urmia, raised in Canada from the early nineties.

This phrasing ("Iran-born Assyrian-Canadian, born in Urmia, raised in Canada") is internally consistent AND matches the kernel AND matches the canon YAML.

**Claude Code recommendation:** Fix the Vision §5 Bina paragraph toward the AGENTS.md / kernel phrasing, NOT the master plan's recommended phrasing. The master plan's recommendation is a drafting error that contradicts higher-authority sources. After the fix, the master plan itself should be corrected in a Phase A' work item to align with the new Bina paragraph and with AGENTS.md.

**Proposed replacement for Vision §5 Bina first sentence (line 56):**

> **Bina Malek (ISFJ-A).** Iran-born Assyrian-Canadian from Urmia, raised in Edmonton, Red Seal mechanic, builder of Loth Wolf Hypersport, survivor of an eight-year coercive control relationship.

Claude Code **does not commit this edit** until Project Owner confirms in chat which phrasing to use.

### 5.3 Reina

**Vision §5 (line 58):**

> **Reina Torres (ESTP-A).** Barcelona-born criminal defence lawyer, track rider, body reader.

**Kernel §2 (line 18):**

> I am Reina Torres. [...] I was born in Barcelona on the twenty-eighth of March in 1990 and raised in Gràcia, in a small flat above the bar my father ran [...]

**Verdict: PASS.** Kernel and Vision agree. Canon YAML matches.

### 5.4 Alicia

**Vision §5 (line 60):**

> **Alicia Marin (ESFP-A).** Famaillá-born, working consular officer for the Argentine Cancillería (MRECIC), resident at the property but frequently away on consular operations. [...]

**Kernel §2 (line 18):**

> I am Alicia Marin. Thirty-three. Born on the twenty-seventh of April 1992 in Famaillá, a small town in the south of the province of Tucumán [...]

**Verdict: PASS.** Kernel and Vision agree on Famaillá birthplace, MRECIC/Cancillería employer, and resident-but-frequently-away framing. Canon YAML matches.

**Work item 3 verdict: 1 drift — Bina only (BINA F7).** Other three characters are clean.

---

## 6. Work Item 4 — Canon YAML vs Kernel Consistency

Specified fields compared for all four characters:

| Field | Adelia | Bina | Reina | Alicia |
|---|---|---|---|---|
| `surname` | Raye ✅ | Malek ✅ | Torres ✅ | Marin ✅ |
| `parents.father.name` | Joaquin Raye (YAML) / Joaquín (kernel) — see note | Farhad Malek ✅ | Rafael Torres ✅ | Ramon Marin (YAML) / Ramón (kernel) — see note |
| `parents.father.origin` | Valencia, Spain ✅ | Urmia, Iran ✅ | Granada, Andalusia ✅ | Famaillá, Tucumán ✅ |
| `parents.mother.name` | Ines Raye (YAML) / Inés (kernel) — see note | Shirin Malek ✅ | Mercè Benítez ✅ (canonical exception) | Pilar Marin ✅ |
| `birthplace` | Valencia, Spain ✅ | Urmia, Iran ✅ | Barcelona, Spain ✅ | Famaillá, Tucumán province, Argentina ✅ |
| `pair_name` | entangled ✅ | circuit ✅ | kinetic ✅ | solstice ✅ |
| `pair_classification` (from pairs.yaml) | Intuitive Symbiosis ✅ | Orthogonal Opposition ✅ | Asymmetrical Leverage ✅ | Complete Jungian Duality ✅ |
| `pair_mechanism` (from pairs.yaml) | Complementary cognitive interlock ✅ | Total division of operational domains ✅ | Temporal collision converted to engine heat ✅ | Inferior-function gift exchange through dominant mastery ✅ |
| `pair_core_metaphor` (from pairs.yaml) | The Compass and the Gravity ✅ | The Architect and the Sentinel ✅ | The Mastermind and the Operator ✅ | The Duality ✅ |

**Note on `pairs.yaml`:** The specified fields `pair_classification`, `pair_mechanism`, and `pair_core_metaphor` live in `src/starry_lyfe/canon/pairs.yaml`, not `characters.yaml`. The Plan assumed `characters.yaml` only; `pairs.yaml` was also checked and is clean. All four pair entries in `pairs.yaml` have `version: "7.1"` and canonical names/classifications/mechanisms/metaphors.

**Note on diacritic inconsistencies (parents' given names):**

- Adelia kernel uses `Joaquín` / `Inés` (with acute accents); canon YAML uses `Joaquin` / `Ines` (unaccented).
- Alicia kernel uses `Ramón` (with acute accent); canon YAML uses `Ramon` (unaccented). Alicia kernel's `Pilar` and the YAML's `Pilar` both match without an accent issue.

Per the AGENTS.md diacritic convention:

> **Diacritic convention:** character names are **unaccented** (`Adelia`, `Marin`); Argentine geography is **accented** (`Famaillá`, `Tucumán`, `Cancillería`); Spanish loanwords are **accented** (`café`, `sheísmo`, `voseo`); `Mercè Benítez` is the canonical exception.

The convention says "character names are unaccented." Parent names are character names in the narrative sense (they appear in the kernel prose), so by strict reading the canon YAML's unaccented form (`Joaquin`, `Ines`, `Ramon`) is the canonical form and the kernels' accented forms (`Joaquín`, `Inés`, `Ramón`) are drift-adjacent stylistic inconsistency.

However, this is below the threshold of AC3 work item 4 — the field-level value check ("do the kernel and YAML refer to the same person?") passes trivially because `Joaquín` and `Joaquin` are the same name differently spelled.

**Claude Code recommendation:** mark as **Medium-severity observation**, not AC3 blocker. Leave for a follow-up Phase A' work item to decide whether to (a) normalize the kernels toward the YAML's unaccented form, or (b) expand the AGENTS.md diacritic convention to explicitly carve out parent-given-names as a Spanish-loanword class.

**Work item 4 verdict: CLEAN** for the specified fields. Medium observation recorded on the diacritic inconsistency.

---

## 7. Work Item 5 — Alicia Residence Framing

The drift grep catches every "non-resident" + "twice yearly" + "based in Madrid" + "Spanish consular" + "Marín" hit. All Alicia residence framing drift in this verification is already counted under AC1 drift hits.

Specifically, the stale Alicia framings are in:

| File | Hits |
|---|---|
| `Characters/Bina/Bina_Malek_Knowledge_Stack.md` | lines 137, 414 |
| `Characters/Reina/Reina_Torres_Knowledge_Stack.md` | lines 308, 310, 405, 407, 425 |
| `Characters/Reina/Reina_Torres_v7.1.md` | line 228 (stale `Spanish consular` token, not strictly a residence framing but a stale-officer framing) |

The canonical statement (master plan §3 work item 5): "Alicia is a **resident** at the property who is **frequently away on consular operations**."

The stale framings use one or more of: "non-resident," "visiting twice yearly," "twice yearly between operations," "Spanish consular officer," "based in Madrid," "Racing Club Madrid" (a v7.0 factual error collapsing Argentine Racing Club de Avellaneda with Madrid-based Real Madrid).

Most severe single block: `Reina_Torres_Knowledge_Stack.md:425` is a Knowledge Stack context block at the top of a section that contains a fully v7.0 Alicia description plus the "Racing Club Madrid" factual error. This block needs a full rewrite, not a token-by-token substitution, because the semantic content is wrong in multiple directions.

**Work item 5 verdict: NOT CLEAN** — overlaps AC1 / AC4. Remediation list is the same as AC1 drift hits in `Characters/Bina/` and `Characters/Reina/`.

---

## 8. Remediation List

Proposed edits, ordered by severity and file locality. Each row is a single commit candidate or a grouped commit where edits are tightly related. **None of these are applied yet** — Claude Code is awaiting Project Owner scope confirmation before proceeding.

| # | File | Line(s) | Change | Severity |
|---:|---|---|---|---|
| R1 | `Vision/Starry-Lyfe_Vision_v7.1.md` | 56 | Replace "Canadian-born Assyrian" with "Iran-born Assyrian-Canadian from Urmia, raised in Edmonton" (proposed; PO decision needed on phrasing vs master plan recommendation) | **Critical** (AC2) |
| R2 | `Characters/Adelia/Adelia_Raye_v7.1.md` | 70 | `Persona_Tier_Framework_v7.md` → `Persona_Tier_Framework_v7.1.md` | High (work item 2) |
| R3 | `Characters/Bina/Bina_Malek_v7.1.md` | 74 | `Persona_Tier_Framework_v7.md` → `Persona_Tier_Framework_v7.1.md` | High (work item 2) |
| R4 | `Characters/Reina/Reina_Torres_v7.1.md` | 64 | `Persona_Tier_Framework_v7.md` → `Persona_Tier_Framework_v7.1.md` | High (work item 2) |
| R5 | `Characters/Alicia/Alicia_Marin_v7.1.md` | 64 | `Persona_Tier_Framework_v7.md` → `Persona_Tier_Framework_v7.1.md` | High (work item 2) |
| R6 | `Characters/Adelia/Adelia_Raye_Entangled_Pair.md` | 215 | "Elemental Pair" → "Solstice Pair" | High (AC1) |
| R7 | `Characters/Reina/Reina_Torres_v7.1.md` | 228 | "Spanish consular rooms" → "Argentine consular rooms" (or similar — see note below) | High (AC1) |
| R8 | `Characters/Bina/Bina_Malek_Knowledge_Stack.md` | 137 | Rewrite sentence about Alicia's pit-wall appearance: remove "non-resident," remove "twice-yearly residence windows," reframe as "resident but frequently away on consular operations; she watches from the pit wall when the race schedule aligns with her being home, and when she is operational elsewhere Adelia or Reina calls her from the paddock after the session" | High (AC1 + AC4) |
| R9 | `Characters/Bina/Bina_Malek_Knowledge_Stack.md` | 414 | Rewrite context block: remove "non-resident," remove "based in Buenos Aires" (ambiguous), remove "visits twice yearly," reframe as "resident but frequently away on consular operations, with whom Bina had a year-long romance in 2023-2024" | Critical (AC1 + AC4, preserves 2023-2024 Bina-Alicia romance history) |
| R10 | `Characters/Reina/Reina_Torres_Knowledge_Stack.md` | 308 | Rewrite paragraph: `Marín` → `Marin`, remove "non-resident," remove "twice yearly," remove "operational in Madrid" (Madrid is factually wrong), reframe as "frequently away on consular operations; when she is at the property during a Rossi escalation..." | High (AC1 + AC4) |
| R11 | `Characters/Reina/Reina_Torres_Knowledge_Stack.md` | 310 | "twice-yearly visits" → "when she is home between operations" | High (AC1 + AC4) |
| R12 | `Characters/Reina/Reina_Torres_Knowledge_Stack.md` | 405 | Heading: `Alicia Marín` → `Alicia Marin` (diacritic fix) | Medium (AC1) |
| R13 | `Characters/Reina/Reina_Torres_Knowledge_Stack.md` | 407 | Rewrite paragraph: `Marín` → `Marin`, remove "non-resident," replace "based in Buenos Aires who visits twice yearly between operations" with "resident at the property but frequently away on consular operations" | Critical (AC1 + AC4, very long paragraph) |
| R14 | `Characters/Reina/Reina_Torres_Knowledge_Stack.md` | 425 | **Full context block rewrite.** Replace entirely stale Alicia description plus the "Racing Club Madrid" factual error. This block never got updated after the v7.1 Argentine reframe. | **Critical** (AC1 + AC4 + factual drift) |

**Line 228 note (R7):** The sentence currently reads "Alicia learned it in Spanish consular rooms in cities her Cancillería has sent her to." The phrase "Spanish consular rooms" is ambiguous — it could parse as "Spanish-language consular rooms" (acceptable) or "Spanish (government) consular rooms" (drift, Alicia works for the Argentine Cancillería not the Spanish one). Given the reader-facing ambiguity, Claude Code recommends rewriting to "Argentine consular rooms" or restructuring to "consular rooms in cities where she speaks Spanish," whichever the Project Owner prefers.

**Line 425 note (R14):** The relevant text is:

> **Knowledge Stack context for Reina's specific relationship architecture with Whyze. [...] Alicia Marín is the non-resident fourth woman in the chosen family, a Spanish consular officer based in Madrid who visits twice yearly; Reina and Alicia have never been romantic but are instant lateral friends bonded by an ongoing Racing Club Madrid (Alicia) versus Real Madrid (Reina) football argument conducted in Castilian with a specific vocabulary neither uses with anyone else in the household. [...]**

This is a v7.0 block that somehow survived the Alicia Argentine reframe integration, sitting directly below a section (lines 405-419) that is fully v7.1-compliant and correctly describes the Racing Club de Avellaneda football argument. The remediation is:

- `Alicia Marín` → `Alicia Marin`
- `non-resident fourth woman` → `fourth woman in the chosen family, resident at the property but frequently away on consular operations`
- `Spanish consular officer based in Madrid who visits twice yearly` → `Argentine consular officer with the Cancillería (MRECIC)`
- `Racing Club Madrid (Alicia) versus Real Madrid (Reina) football argument conducted in Castilian` → `Racing Club de Avellaneda (Alicia) versus Real Madrid (Reina) transatlantic football argument conducted in Spanish across Reina's Barcelona Catalan-Castilian and Alicia's Argentine Rioplatense registers`

Claude Code will draft the exact replacement text and surface it to Project Owner for review before committing.

**Commit plan proposal (pending Project Owner approval):**

| Commit | Scope | Includes |
|---|---|---|
| 1 | `feat(canon): Phase 0 PTF reference normalization` | R2 + R3 + R4 + R5 (four one-line kernel edits) |
| 2 | `fix(vision): Phase 0 BINA F7 — Bina §5 Iran-born correction` | R1 (after PO phrasing confirmation) |
| 3 | `fix(characters): Phase 0 AC1 — Adelia Entangled Pair Elemental→Solstice` | R6 |
| 4 | `fix(characters): Phase 0 AC1+AC4 — Reina kernel Spanish consular rooms` | R7 |
| 5 | `fix(characters): Phase 0 AC1+AC4 — Bina Knowledge Stack Alicia framing` | R8 + R9 |
| 6 | `fix(characters): Phase 0 AC1+AC4 — Reina Knowledge Stack Alicia framing` | R10 + R11 + R12 + R13 + R14 (five related edits in one file) |
| 7 | `docs(phase_0): verification report + PHASE_0.md Step 2 execution log` | This report, final PHASE_0.md update |

Seven commits total, up from the Plan estimate of 1-3. The scope grew because the drift is more pervasive than the Plan assumed.

---

## 9. Open Sub-Questions for Project Owner Before Remediation

### Q5 — Bina Vision §5 phrasing

The master plan §3 work item 3 recommends "Canadian-born Assyrian from Urmia" but this is logically self-contradictory. AGENTS.md Settled Canon Reminder says "Iran-born Assyrian-Canadian, born in Urmia, raised in Canada from the early nineties" — internally consistent and matches the kernel.

**Claude Code recommendation:** use the AGENTS.md / kernel phrasing. Proposed sentence:

> **Bina Malek (ISFJ-A).** Iran-born Assyrian-Canadian from Urmia, raised in Edmonton, Red Seal mechanic, builder of Loth Wolf Hypersport, survivor of an eight-year coercive control relationship. [...]

**Decision needed:** approve the proposed phrasing, or specify an alternative. If approved, Claude Code will also queue a Phase A' work item to update the master plan's §3 work item 3 recommendation from "Canadian-born Assyrian from Urmia" to "Iran-born Assyrian-Canadian from Urmia" so the master plan matches the fix.

### Q6 — Scope expansion approval

The Step 1 Plan estimated 1-3 commits. The verification now surfaces ~14 edits across 7 files, planned as 7 commits. This is a scope expansion relative to the Plan.

**Claude Code recommendation:** proceed with all 14 edits in this Phase 0 (not defer to Phase A'). Rationale: (a) the work is all pre-flight cleanup that is explicitly in-scope for Phase 0 work items 1, 2, 3, 5; (b) deferring would leave Phase A starting from a known-dirty state, which defeats Phase 0's purpose; (c) the PTF reference fix (R2-R5) is mechanical and low-risk; (d) the Alicia framing rewrites are tedious but not architectural.

**Decision needed:** approve expanded scope, or specify which edits to defer.

### Q7 — Per-character Vision directive file scope

`Vision/Reina Torres.md:43` contains "She is his Synergistic Pair" as a plain assertion without a "renamed to Kinetic" annotation. This line is in an excluded file and therefore exempt from AC1 counting, but it appears to be stale content rather than a deliberate transplant narrative.

**Claude Code recommendation:** DEFER to a Phase A' follow-up work item that audits the four per-character Vision directive files and tightens any non-transplant-narrative drift. Not expanding Phase 0 scope to include these files.

**Decision needed:** approve deferral, or expand Phase 0 to include a sweep of the per-character Vision directive files.

### Q8 — Parent-name diacritic convention

Adelia kernel uses `Joaquín`/`Inés` (accented); Alicia kernel uses `Ramón` (accented). Canon YAML uses unaccented forms in both cases. Per AGENTS.md "character names are unaccented."

**Claude Code recommendation:** DEFER to Phase A' as a Medium observation. Not AC3 blocker because the field-level value match passes. The fix is either (a) normalize kernels to unaccented form, or (b) update AGENTS.md to explicitly carve out parent-given-names. This decision is not urgent and doesn't block Phase 0 shipping.

**Decision needed:** approve deferral, or expand Phase 0 scope to include the normalization.

---

## 10. Summary

- **Phase 0 verification is complete.**
- **Remediation is not yet started.** Claude Code is awaiting Project Owner confirmation of Q5, Q6, Q7, Q8 before making any edits.
- **Scope expansion:** 1-3 commits (Plan estimate) → 7 commits (verification finding). All within Phase 0 work items.
- **Critical items blocking ship:** BINA F7 (R1), the 9 AC1 drift hits, the 4 PTF reference fixes.
- **Deferred items:** `Vision/Reina Torres.md:43` (Q7), parent-name diacritic normalization (Q8).
- **Plan corrections recorded:** D1 `Aliyeh` deviation was based on a wrong assumption and is withdrawn (`Aliyeh` is already in §8.1); the prior-conversation memory about "46 occurrences of Aliyeh in Alicia's files" is stale and should be retired after Phase 0 ships.

Once Project Owner confirms scope, Claude Code will proceed with the commit plan in §8, then run `make check` as a sanity pass, then update `PHASE_0.md` Step 2 Execute section, then hand off to Codex for Step 3 audit.

---

## 11. Post-Vision-Rewrite Re-Verification (Addendum)

This section was added after the original verification report was written. Between Step 2 read-only verification and remediation execution, the Project Owner delivered a substantial Vision rewrite plus additional pre-session canonical normalization work across the kernels and character support files. Claude Code re-verified, re-planned, re-approved with Project Owner via plan file `C:\Users\Whyze\.claude\plans\wiggly-kindling-floyd.md`, and executed the adjusted remediation plan across 10 commits.

### 11.1 What the rewrite changed

**Vision file (`Vision/Starry-Lyfe_Vision_v7.1.md`, committed as `c0edc0e`):**
- §5 Bina paragraph: heritage line removed entirely. New text is architectural-function-only, no biographical lock-ins. **BINA F7 (the "Canadian-born Assyrian" drift that §5.2 of this report flagged) is resolved by removal, not patch.**
- §5 other three paragraphs: compressed to architectural function; biographical detail deferred to kernel §2.
- §6 Spanish register rule and intermittent-presence architecture: de-specified to remove proper-noun lock-ins; canonical content now lives in the respective kernels.
- Pair table at §5 lines 66-74: unchanged, remains canonical (Entangled / Circuit / Kinetic / Solstice).

**Alicia kernel (`Characters/Alicia/Alicia_Marin_v7.1.md`, committed as part of `c0edc0e`):**
- §2 new paragraph at line 36: "My home is the Foothills County property where Whyze and the chosen family live. [...] **I am a resident, not a visitor. My absences are real absences, not visits to somewhere else.**" This paragraph did not exist when the original verification report was written and is the new canonical source for AC4.

**Additional Project Owner pre-session canonical cleanup** (committed across `dc085d5` and `0713331`):
- Bina kernel §2: `Shirin Bahadori` → `Shirin Malek` (surname)
- Bina kernel §3 heading: `Citadel Pair` → `Circuit Pair`
- Reina kernel line 223: `Bina Bahadori` → `Bina Malek` (reference)
- Alicia Knowledge Stack: pair-name cross-references normalized
- Alicia Solstice Pair intro: Citadel/Golden cross-references normalized
- Reina Kinetic Pair Part VIII: Alicia residence framing fully rewritten from "non-resident Madrid Spanish consular" to "resident Argentine Cancillería"
- Bina Knowledge Stack: five Circuit Pair heading/reference normalizations (surname + pair name; the Alicia framing on line 414 was partially fixed and required Claude Code R9 to complete)

### 11.2 Status of findings after the rewrite

| Original finding | Prior status | Status after rewrite + remediation | Commit |
|---|---|---|---|
| AC1 drift (9 hits in Characters/) | NOT MET | **MET** | commits 6-9 (`35ce037`, `9a6d4f9`, `b6ed33f`, `3bd8597`) + commit 1 (`dc085d5`) + commit 5 (`9cce59f`) |
| AC2 BINA F7 Vision §5 drift | NOT MET | **MET** (resolved by rewrite, not patch) | `c0edc0e` |
| AC3 canon YAML vs kernel | MET | **MET (strengthened)** — parent-name diacritics now strict-compliant | `dc085d5` (R15-R17) |
| AC4 stale Alicia framing | NOT MET (8 hits) | **MET** | commits `c0edc0e` (Alicia kernel §2 paragraph) + `0713331` (Reina Kinetic Pair Part VIII) + `b6ed33f` (Bina KS) + `3bd8597` (Reina KS) |
| Work item 2 kernel canonical state (4 PTF refs) | NOT MET | **MET** | `dc085d5` (R2-R5) |

### 11.3 Project Owner decisions after the rewrite (Q5-Q10)

| # | Question | Decision | Rationale |
|---|---|---|---|
| Q5 | Bina Vision §5 phrasing | **Resolved/moot** | Vision rewrite removed the line entirely; neither the master plan's "Canadian-born Assyrian from Urmia" phrasing nor Claude Code's "Iran-born Assyrian-Canadian from Urmia" counter-phrasing is in the Vision now. The dispute collapsed. |
| Q6 | Scope expansion to 13 (then 21 with Q7/Q8) edits | **Approved** | All Phase 0 remediation edits execute in Phase 0. |
| Q7 | `Vision/Reina Torres.md:43` Synergistic→Kinetic | **Fix in Phase 0** | Committed as `9cce59f`. Single-word substitution in an excluded-path directive file, but aligned with the "pair names match pair file markdown filenames" directive. |
| Q8 | Kernel parent-name diacritic normalization | **Fix in Phase 0 (kernels only)** | Committed as part of `dc085d5`. ~7 line-edits across 3 kernels (Adelia, Alicia, Reina). Broader normalization across Knowledge Stacks / Pair / Voice files (~20 line-hits) deferred to Phase A' per narrow reading of "kernels." |
| Q9 | Master plan §3 work item 3 staleness | **Defer to Phase A'** | Master plan text recommending "Canadian-born Assyrian from Urmia" is now stale since the rewrite took a different approach. Phase A' maintenance task queued. |
| Q10 | Alicia kernel §2 new paragraph (informational) | **No decision needed** | The new paragraph strengthens the canonical source for AC4 and makes the Bina/Reina KS remediation more obviously justified. |

### 11.4 Project Owner directive (recorded 2026-04-11)

During the commit execution phase, the Project Owner restated three canonical rules that governed the remediation text:

1. **Alicia lives with her chosen family. There is no resident vs non-resident status anywhere.** All remediation text uses "fourth woman in the chosen family, resident at the property but frequently away on consular operations" or similar phrasing that treats her residence as fact and her absences as operational travel, not "visits."
2. **Minor changes like surname normalization are fine to bundle.** This authorized Claude Code to bundle the Project Owner's pre-session `Bahadori → Malek` and similar surname/pair-name fixes into Phase 0 commits.
3. **Pair names must match the pair file markdown filename.** This gave Claude Code the precedent to fix `Vision/Reina Torres.md:43` in Phase 0 (Synergistic → Kinetic, matching `Reina_Torres_Kinetic_Pair.md`) and to justify R6 (Elemental → Solstice, matching `Alicia_Marin_Solstice_Pair.md`).

### 11.5 Final Phase 0 verdict

Phase 0 is **READY FOR CODEX AUDIT ROUND 1**. All four acceptance criteria are MET. The automated `test_v70_residue_grep_returns_zero_matches` test passes. All stale Alicia framings have been purged from non-excluded paths. All pair names in production character files match their respective pair file markdown filenames. Deferred items (master plan staleness, broader diacritic normalization, per-character Vision directive file audit) are tracked as Phase A' follow-ups.

Remaining uncommitted working-tree work (Project Owner's substantive in-progress changes to `src/starry_lyfe/context/*.py`, `tests/unit/test_assembler.py`, `Docs/IMPLEMENTATION_PLAN_v7.1.md`, and two `Docs/PHASE_3_*.md` deletions) is outside Phase 0 scope and was deliberately not committed. The Project Owner should review and commit these separately; they do not block Phase 0 shipping.

---

*End of verification report (updated 2026-04-11 with §11 post-rewrite addendum).*
