# Phase D: Live Pair Data in Prompt

**Master plan reference:** `Docs/IMPLEMENTATION_PLAN_v7.1.md` Phase D
**Phase identifier:** `D`
**Depends on:** Phase 0, A, A', A'', B, C (all SHIPPED 2026-04-12)
**Blocks:** Phase E (parallel capable), downstream J.1-J.4
**Status:** APPROVED — READY FOR CLAUDE CODE EXECUTION
**Last touched:** 2026-04-12 by Project Owner (approval)

---

## How to read this file

This is the **single canonical record** for this phase. All four agents (Claude Code, Codex, Claude AI, Project Owner) read and append to this file. The cycle is six steps. Each step has its own section below. Agents append to their assigned section when it is their turn. Handshakes are explicit — each step ends with an HTML comment of the form `<!-- HANDSHAKE: SENDER -> RECIPIENT | message -->` that hands control to the next agent. To find the current state of the cycle, scroll to the Handshake Log below — the most recent handshake tells you whose turn it is.

---

## Handshake Log

| # | Date | From | To | Message |
|---:|---|---|---|---|
| 1 | 2026-04-12 | Claude AI | Project Owner | Phase D created after Phase C shipped and quality audit completed. Small scope, high value, Claude-Code-appropriate. |
| 2 | 2026-04-12 | Project Owner | Claude Code | APPROVED. Proceed with execution. Answer open questions Q1/Q2 per recommendations (exclude shared_functions and cadence from structured block). |

(Append one row per handshake event. Never delete rows. The log is the audit trail.)

---

## Phase D Specification

### Vision authority
Vision §5 Chosen Family comparison table. Five canonical fields per pair are exposed: `classification`, `mechanism`, `what_she_provides`, `how_she_breaks_spiral`, `core_metaphor`. These fields name the architectural distinctness of each pair.

### Priority
Medium. Small fix, high value. The pair fields exist canonically in `src/starry_lyfe/canon/pairs.yaml` and are currently unused at runtime.

### Source of truth
- `src/starry_lyfe/canon/pairs.yaml` — canonical, verified 2026-04-12. All 4 pairs have full field coverage.
- Vision §5 comparison table — canonical authority for field definitions.

### Decision
Surface `full_name`, `classification`, `mechanism`, `what_she_provides`, `how_she_breaks_spiral`, and `core_metaphor` in **Layer 5** (Voice Directives) as a structured metadata block at the top of the layer. Any prior decision to hide these fields is superseded.

### Additive redundancy note
Phase A direct remediation added `*_pair_name` blocks to `soul_essence.py` that carry the pair name in prose within Layer 1. Phase C added pair soul cards that carry the pair architecture in narrative voice within Layer 1. Phase D adds the same pair identity as **structured metadata** in Layer 5.

This is three registers, three layers, **intentionally redundant**. Claude Code MUST NOT deduplicate by stripping Layer 1 prose coverage. The three registers serve different purposes: prose (soul essence) anchors the voice, narrative (soul card) carries the lived experience, structured metadata (Phase D) gives the model fast typed access to pair mechanics for scene-level reasoning.

### Work items

1. **Load `pairs.yaml` at module init.** Add a loader in `src/starry_lyfe/canon/pairs_loader.py` (new file) that parses the YAML and exposes `get_pair_metadata(character_id)` returning a typed dataclass. Cache the parsed result. The module must handle missing files with a clear error, not silent fallback.

2. **Typed dataclass for pair metadata.** Add `PairMetadata` dataclass with fields: `full_name`, `classification`, `mechanism`, `what_she_provides`, `how_she_breaks_spiral`, `core_metaphor`, `shared_functions`, `cadence`. All fields required. Frozen dataclass.

3. **Format pair metadata block.** Add `format_pair_metadata(character_id)` function returning a prompt-ready structured text block:
   ```
   PAIR: {full_name}
   CLASSIFICATION: {classification}
   MECHANISM: {mechanism}
   CORE METAPHOR: {core_metaphor}
   WHAT SHE PROVIDES: {what_she_provides}
   HOW SHE BREAKS HIS SPIRAL: {how_she_breaks_spiral}
   ```

4. **Inject into Layer 5.** Modify `format_voice_directives()` in `src/starry_lyfe/context/layers.py` to prepend the pair metadata block to the voice directives output. The metadata block counts against the Layer 5 budget but is guaranteed — voice directives trim to accommodate it, not the other way around.

5. **Budget accounting.** Estimate pair metadata block at ~100-150 tokens. Layer 5 default budget is `DEFAULT_BUDGETS.voice` (300 tokens). Verify all 4 characters' metadata fit within budget with room for voice directives. If not, escalate to Project Owner before trimming.

6. **Tests.**
   - `test_pairs_yaml_loads_without_error` — loader parses all 4 pairs cleanly
   - `test_all_four_pairs_have_required_fields` — every pair has non-empty values for all 6 surfaced fields
   - `test_format_pair_metadata_contains_canonical_phrases` — per-character assertions on classification and core_metaphor:
     - Adelia: `Intuitive Symbiosis` + `The Compass and the Gravity`
     - Bina: `Orthogonal Opposition` + `The Architect and the Sentinel`
     - Reina: `Asymmetrical Leverage` + `The Mastermind and the Operator`
     - Alicia: `Complete Jungian Duality` + `The Duality`
   - `test_layer_5_contains_pair_metadata_block` — live `assemble_context()` call verifies Layer 5 contains `PAIR:` line for all 4 characters
   - `test_layer_5_within_budget_with_pair_metadata` — Layer 5 tokens ≤ `DEFAULT_BUDGETS.voice` after metadata injection

### Files touched
- `src/starry_lyfe/canon/pairs_loader.py` (new)
- `src/starry_lyfe/context/layers.py` (modify `format_voice_directives`)
- `tests/unit/test_pairs_loader.py` (new)
- `tests/unit/test_layers.py` (extend, if exists, else skip)
- `Docs/_phases/PHASE_D.md` (this file)
- `Docs/_phases/_samples/PHASE_D_assembled_*_2026-04-12.txt` (4 regenerated samples)

### Acceptance criteria
- **AC-1** `pairs_loader.py` exists and loads `pairs.yaml` successfully
- **AC-2** `PairMetadata` dataclass is frozen, typed, with all 8 fields
- **AC-3** `format_pair_metadata(character_id)` returns the 6-field structured block for all 4 characters
- **AC-4** Layer 5 output in `assemble_context()` contains `PAIR:` line and all 5 metadata fields for all 4 characters
- **AC-5** Layer 5 total tokens remain within `DEFAULT_BUDGETS.voice` for all 4 characters (no overrun)
- **AC-6** 4 Phase D sample files at `Docs/_phases/_samples/PHASE_D_assembled_{adelia,bina,reina,alicia}_2026-04-12.txt` show pair metadata in Layer 5
- **AC-7** All existing tests still pass (127 + new tests)
- **AC-8** Soul essence pair labels in Layer 1 are NOT removed or deduplicated (Phase A redundancy preserved)

### Estimated commits
2-3 commits:
1. Loader + dataclass + tests
2. Layer 5 integration + integration test + sample regen
3. (Optional) Documentation touchups

### Open questions for Project Owner
- **Q1:** Should `shared_functions` (e.g., "Fi-Te axis (direct bridge)") be surfaced in the structured block? Currently excluded to keep the block tight, but it is canonical per Vision §5. **Recommendation: exclude** unless Project Owner indicates voice directives need this typological anchor for scene routing.
- **Q2:** Should `cadence` (`continuous` vs `intermittent`) be surfaced? This is Alicia-specific signal (Phase A'' already handles communication mode gating via `alicia_remote` card and the assembler gate). **Recommendation: exclude from structured block** — `cadence` belongs to assembly-time routing decisions, not prompt content.

---

## Step 1: Plan (Claude Code)

**[STATUS: PENDING]**
**Owner:** Claude Code
**Reads:** Master plan Phase D, Phase D spec above, AGENTS.md Phase D customization, `pairs.yaml`
**Writes:** This section

_Claude Code: fill this section during execution, not after. Path C reconstruction is explicitly disallowed per Phase C INH-8 restrictive amendment._

<!-- HANDSHAKE: Claude AI -> Project Owner | Phase D spec drafted. Awaiting approval to hand to Claude Code. -->

---

## Step 2: Execute (Claude Code)

**[STATUS: PENDING]**
**Owner:** Claude Code
**Writes:** This section + the code changes listed in work items

_Claude Code: fill this section during execution. Record each commit hash as it lands._

---

## Step 3: Audit (Codex)

**[STATUS: PENDING]**
**Owner:** Codex
**Reads:** Step 1, Step 2, landed code
**Writes:** This section with gate recommendation (PASS / FAIL / FAIL with remediation items)

---

## Step 4: Remediate (Claude Code, if audit FAIL)

**[STATUS: PENDING]**
**Owner:** Claude Code (only if Step 3 returns FAIL)

---

## Step 5: QA (Claude AI)

**[STATUS: PENDING]**
**Owner:** Claude AI
**Reads:** All prior steps, landed code, sample artifacts
**Writes:** This section with ship recommendation

---

## Step 6: Ship (Project Owner)

**[STATUS: PENDING]**
**Owner:** Project Owner
**Writes:** This section with final decision and Phase D SHIPPED marker

---

## Phase D Notes and Context

### Why this phase exists
The `pairs.yaml` canonical file has been in the repository since v7.0. Its contents have never reached runtime. The model has been generating responses without fast-access structured knowledge of the pair mechanics it is supposed to embody. Phase D closes that gap with a 2-3 commit fix.

### Why this phase is Claude-Code-appropriate (not direct remediation)
Phases A/B/C required direct remediation because they touched soul-bearing prose content where word choice carries canonical weight. Phase D touches:
- A YAML file with fixed-schema data (no prose authoring)
- A loader module (pure infrastructure)
- A formatter function (deterministic string formatting)
- A Layer 5 injection point (small surgical edit)
- Tests (mechanical assertions)

No soul content is authored or interpreted. The canonical fields already exist in `pairs.yaml` and Vision §5. Phase D just plumbs them through to Layer 5.

### Post-Phase-C foundation
All Phase D work operates on a foundation of:
- 41 soul essence blocks in `soul_essence.py` (Phase A remediation)
- 15 authored soul cards (Phase C)
- 3-layer soul architecture wired into assembler (Phase B remediation)
- Terminal anchoring on all 4 characters (Phase B)
- Per-character budget scaling (Phase B)
- Communication-mode routing (Phase A'')
- 127 passing tests

Phase D adds Layer 5 metadata on top of this foundation without touching any of it.
