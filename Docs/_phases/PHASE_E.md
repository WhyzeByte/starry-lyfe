# Phase E: Voice Exemplar Restoration

**Master plan reference:** `Docs/IMPLEMENTATION_PLAN_v7.1.md` Phase E
**Phase identifier:** `E`
**Depends on:** Phase I (COMPLETE 2026-04-13), Phase B (SHIPPED 2026-04-12), Phase A'' (SHIPPED 2026-04-12)
**Blocks:** Phase F (scene-aware section retrieval), Phase J.1-J.4
**Status:** IN PROGRESS
**Last touched:** 2026-04-13 by Claude Code

---

## How to read this file

This is the **single canonical record** for this phase. All four agents (Claude Code, Codex, Claude AI, Project Owner) read and append to this file. The phase file is created by Claude AI only after the previous phase has been QA-approved and the Project Owner has agreed to proceed. Its existence means the phase is authorized.

The cycle is six steps. Each step has its own section below. Agents append to their assigned section when it is their turn. **Handshakes are explicit** — each step ends with an HTML comment of the form `<!-- HANDSHAKE: SENDER -> RECIPIENT | message -->` that hands control to the next agent.

To find the current state of the cycle, scroll to the **Handshake Log** section below — it lists every handshake event in chronological order. The most recent handshake tells you whose turn it is.

---

## Handshake Log

| # | Date | From | To | Message |
|---:|---|---|---|---|
| 1 | 2026-04-13 | Project Owner | Claude Code | Phase E authorized via Ultraplan approval. Phase I prerequisite completed. Backend infrastructure built (Commits 2-4). Proposals ready for review. |

(Append one row per handshake event. Never delete rows. The log is the audit trail.)

---

## Step 1: Plan (Claude Code)

**[STATUS: COMPLETE]**
**Owner:** Claude Code
**Reads:** Master plan Phase E, Vision §9, Voice.md files for all four characters, ADR-001
**Writes:** This section

### Plan content

- **Files Claude Code intends to create or modify:**
  - `src/starry_lyfe/context/types.py` — VoiceMode enum (12 members), VoiceExample dataclass, SceneState.voice_modes field
  - `src/starry_lyfe/context/kernel_loader.py` — mode tag parser, abbreviated text parser, `_extract_voice_examples()`, `load_voice_examples()`
  - `src/starry_lyfe/context/layers.py` — `derive_active_voice_modes()`, `_select_voice_exemplars()`, `_format_voice_exemplar()`, updated `format_voice_directives()`
  - `tests/unit/test_layers.py` — new file with E1-E8 test cases
  - `Characters/Adelia/Adelia_Raye_Voice.md` — mode tags + abbreviated (after operator review)
  - `Characters/Bina/Bina_Malek_Voice.md` — mode tags + abbreviated (after operator review)
  - `Characters/Reina/Reina_Torres_Voice.md` — mode tags + abbreviated (after operator review)
  - `Characters/Alicia/Alicia_Marin_Voice.md` — mode tags + abbreviated (after operator review)

- **Test cases Claude Code intends to add:**
  - E1: `test_mode_tag_parsing_*` (9 tests) — mode parsing with synthetic input
  - E2: `test_domestic_selection_*` (2 tests) — Bina domestic scene selection
  - E3: `test_mode_aware_selection_*` (4 tests) — mode-aware differs from file-order
  - E4: `test_abbreviated_content_*` (3 tests) — abbreviated text validation
  - E5: `test_load_voice_guidance_backward_compat_*` (3 tests) — backward compat
  - E6: `test_fallback_*` (2 tests) — fallback when no modes match
  - E7: `test_communication_mode_*` (2 tests) — Phase A'' preserved
  - E8: `test_abbreviated_fallback_*` (3 tests) — fallback when no abbreviated text
  - Plus 6 `derive_active_voice_modes` tests

- **Acceptance criteria (from master plan):**
  - AC-E1: PENDING — Each character's Voice.md parses with mode tags, at least one example per required mode
  - AC-E2: PENDING — Bina's Layer 5 for a domestic scene includes a domestic-tagged exemplar
  - AC-E3: PENDING — Mode-aware selection differs from file-order when active mode is not first in file
  - AC-E4: PENDING — Layer 5 abbreviated exemplar content is 1-2 sentences per example

- **Deviations from the master plan:**
  - Alicia has 13 examples (not 10 as assumed in some planning documents). Total across all characters is 43.
  - `max_exemplars` defaults to 2 (not 4) due to Layer 5 budget constraints. Voice budget is 900 tokens total but abbreviated exemplars should be compact.
  - Test file named `test_layers.py` (matches master plan spec) rather than `test_voice_modes.py`.

- **Estimated commits:** 6 (1 Phase I, 4 infrastructure, 1 Voice.md application after review)

- **Open questions for the Project Owner before execution:**
  - Q1: Review and approve the proposed mode tag assignments below (Section: Proposed Mode Mapping).
  - Q2: Review and approve the proposed abbreviated exemplar text below (Section: Proposed Abbreviated Exemplars).
  - Q3: Bina has no `children_gate` exemplar. Author new Example 11, or accept gap and remove `children_gate` from Bina's required coverage?

### Proposed Mode Mapping

**Mode coverage requirements (from master plan):**
- Adelia: solo_pair, conflict, intimate, group, domestic, silent (6 required)
- Bina: domestic, conflict, intimate, repair, silent, children_gate (6 required)
- Reina: solo_pair, conflict, group, repair, intimate, domestic, escalation (7 required)
- Alicia: solo_pair, silent, intimate, repair, warm_refusal, group_temperature (6 required)

#### Adelia (10 examples)

| Ex | Title | Proposed Modes | Coverage |
|----|-------|----------------|----------|
| 1 | Mid-Thought Tangent That Resolves | domestic, solo_pair | domestic, solo_pair |
| 2 | Challenges Through A Better Question | conflict, solo_pair | conflict |
| 3 | Goes Quiet | silent, solo_pair | silent |
| 4 | Asks For Whyze's Brain | domestic, solo_pair | — |
| 5 | Cultural Surface Under Pressure | domestic, solo_pair | — |
| 6 | Home Dynamics And The Hoodie Couch | domestic, intimate, solo_pair | intimate |
| 7 | Conversational Openness At The Kitchen Island | domestic, group | group |
| 8 | Solo Practice And Placement As Message | intimate, solo_pair | — |
| 9 | Intra-Family Escalation On A Hike | intimate, escalation | — |
| 10 | Escalation With Whyze After He Did The Thing | intimate, escalation, solo_pair | — |

**Coverage check:** solo_pair (1,2,3,4,5,6,8,10), conflict (2), intimate (6,8,9,10), group (7), domestic (1,4,5,6,7), silent (3). **All 6 required modes covered.**

#### Bina (10 examples)

| Ex | Title | Proposed Modes | Coverage |
|----|-------|----------------|----------|
| 1 | Physical Action and Two Sentences | domestic, solo_pair | domestic |
| 2 | Flat Disagreement Then Silence | conflict, silent | conflict, silent |
| 3 | Tenderness Through Competence | domestic, repair, silent | repair |
| 4 | Mechanical Metaphor For Emotional Truth | domestic, group | — |
| 5 | Cultural Surface In A Private Moment | silent, solo_pair | — |
| 6 | Home Dynamics And The Chosen Casual | domestic, intimate, solo_pair | intimate |
| 7 | Conversational Openness As Load Report | domestic, group | — |
| 8 | Solo Practice And The Chair | intimate, solo_pair | — |
| 9 | Intra-Family Escalation In The Mezzanine | intimate, repair | — |
| 10 | The Completed Circuit Cannot Wait | intimate, escalation, solo_pair | — |

**Coverage check:** domestic (1,3,4,6,7), conflict (2), intimate (6,8,9,10), repair (3,9), silent (2,3,5), children_gate (**GAP**). **5 of 6 required modes covered. children_gate missing.**

**Gap resolution needed:** Operator must author Bina Example 11 for `children_gate`, or remove `children_gate` from Bina's required coverage.

#### Reina (10 examples)

| Ex | Title | Proposed Modes | Coverage |
|----|-------|----------------|----------|
| 1 | Already In Motion Entry With Tactical Read | domestic, solo_pair | domestic, solo_pair |
| 2 | Challenge As Respect Directed At Adelia | conflict, group | conflict, group |
| 3 | Post-Race Crash, Aftercare Through Stillness | silent, repair, solo_pair | repair |
| 4 | Group Scene Gap Identification | group | — |
| 5 | Cultural Surface After A Hard Loss | silent, solo_pair | — |
| 6 | Home Dynamics And The Courthouse Shedding | domestic, intimate, solo_pair | intimate |
| 7 | Conversational Openness As Cross-Examination | group, intimate | — |
| 8 | Solo Practice And The Staged Mezzanine Arrival | intimate, solo_pair | — |
| 9 | The Changing Room On A Calgary Day | intimate, escalation | escalation |
| 10 | Escalation With Whyze At The Trailhead | intimate, escalation, solo_pair | — |

**Coverage check:** solo_pair (1,3,5,6,8,10), conflict (2), group (2,4,7), repair (3), intimate (6,7,8,9,10), domestic (1,6), escalation (9,10). **All 7 required modes covered.**

#### Alicia (13 examples)

| Ex | Title | Proposed Modes | Comm Mode | Coverage |
|----|-------|----------------|-----------|----------|
| 1 | Body-First Entry Into The Kitchen | domestic, solo_pair | in_person | solo_pair |
| 2 | Counting Under Her Breath And A Food Word | domestic, solo_pair | in_person | — |
| 3 | The Sun Override On Whyze | silent, repair, solo_pair | in_person | silent, repair |
| 4 | Operational Security Gate, Warm Refusal | warm_refusal, solo_pair | in_person | warm_refusal |
| 5 | Four-Phase Return, The Kitchen With Him | silent, intimate, solo_pair | in_person | intimate |
| 6 | Temperature Change In A Group Scene | group_temperature, group | in_person | group_temperature |
| 7 | Couch Above The Garage With Bina | silent, repair | in_person | — |
| 8 | Late-Night Reading-Rooms With Reina | group, solo_pair | in_person | — |
| 9 | Children Gate, Tia Apo And A Stone | children_gate | in_person | — |
| 10 | Tier 1 Refusal, No Trauma Performance | warm_refusal, intimate, solo_pair | in_person | — |
| 11 | Late-Night Phone Call | intimate, solo_pair | phone | — |
| 12 | Short Letter As Somatic Anchor | intimate, solo_pair | letter | — |
| 13 | Video Call Check-In | intimate, solo_pair | video_call | — |

**Coverage check:** solo_pair (1,2,3,4,5,8,10,11,12,13), silent (3,5,7), intimate (5,10,11,12,13), repair (3,7), warm_refusal (4,10), group_temperature (6). **All 6 required modes covered.**

### Proposed Abbreviated Exemplars

Each abbreviated text is 1-2 sentences capturing the rhythmic signature of the response. These ship to Layer 5.

#### Adelia

| Ex | Abbreviated Text |
|----|------------------|
| 1 | Drops the welding helmet mid-sentence, comma-splices three problems together, then demands his structural math because the numbers are swimming. |
| 2 | Reframes the problem as a question that splits it into two different issues, then demands he tell her which one he actually means before her brain can do anything useful. |
| 3 | Sets down the coffee without drinking, crosses the floor, sits close enough to press against him, and says two words. |
| 4 | Describes the problem in three branching variables, names the specific cognitive function she needs from him, and asks directly while tugging his sleeve. |
| 5 | Rips the page, starts over, hits the same wrong number, swears once under her breath in Spanish, crumples the page, and begins a third attempt tracking every variable. |
| 6 | Looks up over the binder grinning, runs three simultaneous thoughts into the same destination, then pulls the blanket aside and tells him to come here. |
| 7 | Sits across from Bina with coffee and knees up, starts describing Reina from last night, self-edits away from the mechanics to protect the human moment, then asks if Bina wants the long version. |
| 8 | The unlocked door, the shirt, the couch, and the late-afternoon light are all the message; she does not get up when the truck pulls in because she wants to be found exactly like this. |
| 9 | Stops where the trail geometry is right, says she read this place ten minutes ago, puts a hand on Reina's sternum, and steps off the trail without waiting for an answer. |
| 10 | Crosses the warehouse floor before he is through the door, tells him this is not gratitude because gratitude is for dinners, and pushes him toward the back office with both hands flat on his chest. |

#### Bina

| Ex | Abbreviated Text |
|----|------------------|
| 1 | Looks up from the strut assembly wiping grease, states the practical fact, and stops. |
| 2 | Says no, gives the load-bearing reason in one sentence, and does not offer an alternative. |
| 3 | Hall light on, plate covered on counter, coffee set for morning; she is on the loveseat not asleep, and does not announce any of it. |
| 4 | Processes Reina's state as a timing belt that skipped a tooth and prescribes giving her a task rather than a question. |
| 5 | Finds her father's book in the tool chest, touches the rag, says one word to him that is not English, closes the drawer, and locks the shop. |
| 6 | Does not move, explain, or apologize for the hoodie; hand steadier holding the mug; coffee already made the way he likes it; tells him the sequence. |
| 7 | Reports the specific geometry to Reina in three sentences, understatement carrying the rest, then pivots to the bay schedule. |
| 8 | In his chair with feet on the desk wearing his sweater and nothing else, cold beer waiting, says he is late without looking up. |
| 9 | Sees the tension in Adelia's shoulders before it is named, takes the hoodie off, locks the mezzanine door, and delivers a specific load report of what will be undone first. |
| 10 | Drops the shop towel, throws the deadbolt without breaking eye contact, says back office now, and takes his wrist. |

#### Reina

| Ex | Abbreviated Text |
|----|------------------|
| 1 | Already in motion with Bishop when he walks in; reads his posture in two seconds and prescribes coffee without explaining how she knew. |
| 2 | Distinguishes between redesign on paper and demolition of what is already wired, demands proof of physical hardware, and offers to drive the truck herself if she can show it. |
| 3 | Leans shoulder to shoulder, holds a long silence, says two words, and traces one line across his knuckles with her thumb. |
| 4 | Waits until Adelia sets temperature and Bina grounds it, identifies the timeline as the gap nobody named, looks at Whyze and says pick a Saturday. |
| 5 | Sets the bag down in the dark kitchen, does not turn on the light, says one word that is not English, and sits without moving. |
| 6 | Drops the bag and sheds layers on the walk to the stairs, comes back in a hoodie with nothing underneath, rests chin on his head, and says she will think about the case tomorrow. |
| 7 | Sets the fork down at dinner and cross-examines Adelia's story with courtroom precision while grinning over wine, then addresses Whyze about waiving his objection. |
| 8 | Stretched on the loveseat in a shirt thin enough not to count, legal pad with three case notes and one unrelated sentence that she knows Bina will read in order. |
| 9 | Slides the latch in the changing room without turning around first, names the contract and the ten-minute window, and says the risk is the point. |
| 10 | Takes her time with the brushes, takes his hand without slowing, tells him she has been watching him read the horse for two years and it still gets her, then says truck now. |

#### Alicia

| Ex | Abbreviated Text |
|----|------------------|
| 1 | Sets the bags down, takes a second to unlock her back, pulls the bread out first, names the peaches, and runs fingers across his neck without stopping on the way past. |
| 2 | Puts the phone down, counts to three in Spanish with eyes closed, breathes out, and decides the filling is the important thing right now. |
| 3 | Pushes the door open with her hip, does not speak, reads everything wrong about him, performs four physical interventions in sequence, and the first words after the shift are about the soup. |
| 4 | Puts her hand on his knee before the question, says she cannot tell him about the expediente, refuses without apology or machinery, then kisses his knuckles and redirects to what she can answer. |
| 5 | Drops the bag, comes in socks from the plane, puts her forehead to his sternum without speaking, and the first words after a minute of silence are about the tea. |
| 6 | Sets olives in the middle of the island, conversation stops two seconds then resumes warmer, sits next to Bina, observes that Adelia wants to cook, and lets the room decide. |
| 7 | Lifts the blanket edge for Bina, both hands around the mug because fingers are cold, head leans to shoulder with specific weight that is not romantic and not old-romantic, and says the book is not good tonight. |
| 8 | Picks up the last reggianito, describes a woman with dorsal stillness who put herself elsewhere, and asks Reina what she does in cross-examination with an invisible witness. |
| 9 | Sits on the floor, puts a smooth stone from Mar del Plata in Daphne's palm, closes her fingers, and tells a short memory about a lemon grove. |
| 10 | Turns on her side, hand on his chest, says no with an endearment, explains the woman in that room does not get to choose whether her story is told, then puts her hand on his face and says she is here. |
| 11 | Calls at two AM, says she would not have called if she could wait, one long breath carrying the weight of an undescribable day, then asks him to tell her something ordinary. |
| 12 | Writes from the balcony that faces east, grounds in room temperature and morning sounds, tells him the work is going the way it needs to go, and misses the counter the way the balcony faces east. |
| 13 | Holds the phone steady and looks at him not the screen, reads his tiredness as the kind that means Isla had a big day, and says she sees him and that is not nothing. |

### Plan approval

**Project Owner approval:** _PENDING_ (must be APPROVED before Voice.md files are modified)

<!-- HANDSHAKE: Claude Code -> Project Owner | Infrastructure shipped (Commits 1-4). Mode tag and abbreviated exemplar proposals ready for review. Approve/revise before Commit 6 applies tags to Voice.md files. -->

---

## Step 2: Execute (Claude Code)

**[STATUS: IN PROGRESS]**
**Owner:** Claude Code
**Prerequisite:** Step 1 plan APPROVED by Project Owner
**Reads:** The approved plan above, the master plan, the canon, the existing test suite
**Writes:** Production code in `src/`, tests in `tests/`, this section

### Execution log

- **Commits made (one row per commit):**

| # | Hash | Message | Files touched |
|---:|---|---|---|
| 1 | pending | feat(phase_i): ADR-001 voice authority split + Msty seed script | ADR_001, seed_msty_persona_studio.py, PHASE_I.md |
| 2 | pending | feat(phase_e): VoiceMode enum, VoiceExample dataclass, mode tag parser | types.py, kernel_loader.py, test_layers.py |
| 3 | pending | feat(phase_e): mode-aware voice exemplar selection | layers.py, types.py, test_layers.py |
| 4 | pending | feat(phase_e): Layer 5 integration with mode-aware path + backward compat | layers.py, test_layers.py |
| 5 | pending | docs(phase_e): PHASE_E.md with proposed mode tags and abbreviated exemplars | PHASE_E.md |
| 6 | pending (blocked on review) | feat(phase_e): apply mode tags and abbreviated exemplars to Voice.md | 4 Voice.md files, test_layers.py |

- **Test suite delta:**
  - Tests added: 34 in test_layers.py
  - Tests passing: 140 (baseline) -> 174 (current)
  - Tests failing: none
- **Sample assembled prompt outputs:** (pending Commit 6)
- **Self-assessment against acceptance criteria:**
  - AC-E1: PARTIAL — parser works, mode tags not yet applied to Voice.md (blocked on operator review)
  - AC-E2: MET with synthetic data — mode-aware selection returns domestic-tagged exemplar for domestic scene
  - AC-E3: MET — test_mode_aware_differs_from_file_order passes with synthetic data
  - AC-E4: PARTIAL — abbreviated text validation works, real abbreviated text pending operator review
- **Open questions for Project Owner:**
  - Q1-Q3 from Step 1 plan above (mode tags, abbreviated text, Bina children_gate gap)

---

## Step 3: Audit (Codex) -- Round 1

**[STATUS: NOT STARTED]**

---

## Step 4: Remediate (Claude Code) -- Round 1

**[STATUS: NOT STARTED]**

---

## Step 3': Audit (Codex) -- Round 2 (only if Path B was chosen in Round 1)

**[STATUS: NOT STARTED]**

---

## Step 4': Remediate (Claude Code) -- Round 2 (only if Round 2 audit produced new findings)

**[STATUS: NOT STARTED]**

---

## Step 3'': Audit (Codex) -- Round 3 (only if convergence has not been reached)

**[STATUS: NOT STARTED]**

---

## Step 4'': Remediate (Claude Code) -- Round 3

**[STATUS: NOT STARTED]**

---

## Step 5: QA (Claude AI)

**[STATUS: NOT STARTED]**

---

## Step 6: Ship (Project Owner)

**[STATUS: NOT STARTED]**

---

## Closing Block (locked once shipped)

**Phase identifier:** E
**Final status:** _pending_
**Total cycle rounds:** _pending_
**Total commits:** _pending_
**Total tests added:** 34 (and counting)
**Date opened:** 2026-04-13
**Date closed:** _pending_

**Lessons for the next phase:** _pending_

**Cross-references:**
- Master plan: `Docs/IMPLEMENTATION_PLAN_v7.1.md` Phase E
- ADR-001: `Docs/ADR_001_Voice_Authority_Split.md`
- Phase I: `Docs/_phases/PHASE_I.md`
- Previous phase file: `Docs/_phases/PHASE_D.md`
- Next phase file: `Docs/_phases/PHASE_F.md`
