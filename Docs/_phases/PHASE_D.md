# Phase D: Live Pair Data in Prompt

**Master plan reference:** `Docs/IMPLEMENTATION_PLAN_v7.1.md` Phase D
**Phase identifier:** `D`
**Depends on:** Phase 0, A, A', A'', B, C (all SHIPPED 2026-04-12)
**Blocks:** Phase E (parallel capable), downstream J.1-J.4
**Status:** IN PROGRESS — Round 2 audit complete, awaiting remediation Round 2
**Last touched:** 2026-04-12 by Codex (Round 2 re-audit recorded)

---

## How to read this file

This is the **single canonical record** for this phase. All four agents (Claude Code, Codex, Claude AI, Project Owner) read and append to this file. The cycle is six steps. Each step has its own section below. Agents append to their assigned section when it is their turn. Handshakes are explicit — each step ends with an HTML comment of the form `<!-- HANDSHAKE: SENDER -> RECIPIENT | message -->` that hands control to the next agent. To find the current state of the cycle, scroll to the Handshake Log below — the most recent handshake tells you whose turn it is.

---

## Handshake Log

| # | Date | From | To | Message |
|---:|---|---|---|---|
| 1 | 2026-04-12 | Claude AI | Project Owner | Phase D created after Phase C shipped and quality audit completed. Small scope, high value, Claude-Code-appropriate. |
| 2 | 2026-04-12 | Project Owner | Claude Code | APPROVED. Proceed with execution. Answer open questions Q1/Q2 per recommendations (exclude shared_functions and cadence from structured block). |
| 3 | 2026-04-12 | Codex | Claude Code | Round 1 audit recorded from the landed Phase D code surface because Step 1 and Step 2 were never canonically filled. Gate recommendation: FAIL. Findings: F1 High (Layer 5 silently drops pair metadata when the loader fails instead of raising a clear error), F2 Medium (the new Phase D tests do not cover the accepted spec or the live `assemble_context()` path), F3 Medium (the canonical Phase D record is still execution-incomplete and there are no `PHASE_D_assembled_*` sample artifacts), F4 Low (the loader does not parse `pairs.yaml` once at module init as specified; it reparses on each character cache miss). |
| 4 | 2026-04-12 | Codex | Claude Code | Round 2 re-audit after remediation commit `e7e0175`. Gate recommendation: PASS WITH MINOR FIXES. Verified fixed: F1 silent Layer 5 fallback is gone, and F4 single-parse caching is live. Remaining findings: R2-F1 Medium (the canonical Phase D record is still not QA-ready: Step 1, Step 2, and Step 4 remain `PENDING`, and there are still no `PHASE_D_assembled_*` sample artifacts), R2-F2 Low (the accepted live `assemble_context()` regression test for Layer 5 pair metadata is still missing). |

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

**[STATUS: COMPLETE - handed to Claude Code for remediation Round 1]**
**Owner:** Codex
**Reads:** Step 1, Step 2, landed code
**Writes:** This section with gate recommendation (PASS / FAIL / FAIL with remediation items)

### Audit content

#### Scope

Reviewed:

- `Docs/IMPLEMENTATION_PLAN_v7.1.md` Phase D
- `Docs/_phases/PHASE_D.md` header, Handshake Log, Step 1, Step 2, and accepted Phase D specification
- landed Phase D commit `fa1eb90`
- `src/starry_lyfe/canon/pairs_loader.py`
- `src/starry_lyfe/context/layers.py`
- `src/starry_lyfe/canon/pairs.yaml`
- `tests/unit/test_pairs_loader.py`
- `tests/unit/test_assembler.py` for existing Layer 5 / live assembly coverage
- `Docs/_phases/_samples/` for `PHASE_D_assembled_*` artifacts

Because Step 1 and Step 2 were never canonically populated, this audit used the landed commit surface and live runtime probes as the execution record.

#### Verification context

Independent checks run during audit:

- `.venv\Scripts\python -m pytest tests/unit/test_pairs_loader.py tests/unit/test_assembler.py -q` -> **PASS** (`61 passed`)
- `.venv\Scripts\python -m pytest tests/unit -q` -> **PASS** (`136 passed`)
- `.venv\Scripts\python -m ruff check src/ tests/` -> **PASS**
- `.venv\Scripts\python -m mypy src/` -> **PASS**
- `.venv\Scripts\python -m pytest -q` -> **ENVIRONMENTAL FAIL** (`136 passed, 14 errors`) because PostgreSQL is unreachable during integration setup at `tests/integration/conftest.py:92`

Runtime probes performed:

- live `assemble_context(...)` probe across Adelia, Bina, Reina, and Alicia using the canonical unit-test stub retrieval path to confirm Layer 5 now carries `PAIR:` before voice guidance
- failure-path probe that patched `starry_lyfe.canon.pairs_loader.format_pair_metadata` to raise `FileNotFoundError`
- loader-cache probe that patched `yaml.safe_load` and counted parse calls while loading all four characters
- sample-artifact existence check for `Docs/_phases/_samples/PHASE_D_assembled_*_2026-04-12.txt`

#### Executive assessment

The happy path is real. Phase D does surface structured pair metadata in Layer 5 for all four characters, and in live prompts the `PAIR:` block appears before `Voice calibration guidance:`. Default-budget Layer 5 token counts are healthy (`adelia 314`, `bina 333`, `reina 342`, `alicia 117`), so the added metadata is not currently stressing the voice budget.

The implementation is still not shippable. The failure path violates the accepted spec: if pair metadata loading fails, `format_voice_directives()` silently drops the pair block and returns a degraded Layer 5 instead of surfacing a clear runtime error. The test suite also overstates coverage: the accepted spec called for all-four canonical phrase checks and live `assemble_context()` assertions, but the new tests mostly stop at helper-level behavior and a single-character content check. The canonical Phase D record is also still untouched past approval, and there are no Phase D sample prompt artifacts for QA to read.

Gate recommendation: **FAIL**.

#### Findings

| # | Severity | Finding | Evidence | Recommended fix |
|---:|---|---|---|---|
| F1 | High | Layer 5 silently drops pair metadata when pair loading fails instead of raising a clear error. | The accepted Phase D spec requires missing pair data to fail clearly, not silently. `src/starry_lyfe/context/layers.py:167-169` prepends the pair block and then swallows both `ValueError` and `FileNotFoundError` with `pass`. In a live failure-path probe, patching `starry_lyfe.canon.pairs_loader.format_pair_metadata` to raise `FileNotFoundError('missing pairs.yaml')` still returned a normal Layer 5 with `pair_present False` and no exception. That means the core Phase D value can disappear at runtime without any signal. | Remove the silent fallback. Let `FileNotFoundError` / pair-resolution errors surface clearly on the live prompt path, or convert them into an explicit hard failure with a Phase D-specific message. Add a regression test that forces loader failure and asserts the error is raised. |
| F2 | Medium | The new Phase D tests do not cover the accepted spec or the live `assemble_context()` path. | `tests/unit/test_pairs_loader.py:41` checks all eight fields only for Bina, not all four pairs. `tests/unit/test_pairs_loader.py:75` checks canonical phrases only for Bina, even though the accepted spec names all four characters. `tests/unit/test_pairs_loader.py:86` and `:97` call `format_voice_directives(..., None)` directly instead of the accepted live `assemble_context()` path, so assembler wiring and wrapped Layer 5 behavior are still unguarded. | Add a live `assemble_context()` test for all four characters that asserts the `PAIR:` block and the five metadata fields appear in Layer 5, and strengthen the canonical phrase coverage so Adelia, Reina, and Alicia are checked explicitly. |
| F3 | Medium | The canonical Phase D record is still execution-incomplete, and there are no Phase D sample prompt artifacts. | `Docs/_phases/PHASE_D.md:112`, `:125`, and `:135` still show Step 1, Step 2, and Step 3 as `PENDING` even though `fa1eb90` landed. The Handshake Log stops at Project Owner approval, and `Get-ChildItem Docs/_phases/_samples/PHASE_D_assembled_*_2026-04-12.txt` returned count `0`. That leaves no canonical execution log or prompt samples for QA. | Fill Step 1 and Step 2 truthfully from the landed work, keep this Round 1 audit in Step 3, and generate four `PHASE_D_assembled_*_2026-04-12.txt` samples from the live runtime. |
| F4 | Low | The loader does not parse `pairs.yaml` once at module init as specified; it reparses on each character cache miss. | The accepted Phase D work item says the loader should parse the YAML once and cache the parsed result. `src/starry_lyfe/canon/pairs_loader.py` instead keeps a per-character cache only and calls `yaml.safe_load(PAIRS_YAML.read_text(...))` inside `get_pair_metadata()`. In a probe that cleared the cache and loaded all four characters, `yaml.safe_load` was invoked `4` times. | Cache the parsed YAML document or a full character-to-metadata map once, then serve all characters from that cache. Add a test that proves repeated multi-character lookup does not reparse the file. |

#### Runtime probe summary

- Live happy-path probe confirmed Phase D's intended prompt behavior:
  - `adelia`: `pair=True`, `guidance=True`, `pair_before_guidance=True`, `layer5_tokens=314`
  - `bina`: `pair=True`, `guidance=True`, `pair_before_guidance=True`, `layer5_tokens=333`
  - `reina`: `pair=True`, `guidance=True`, `pair_before_guidance=True`, `layer5_tokens=342`
  - `alicia`: `pair=True`, `guidance=True`, `pair_before_guidance=True`, `layer5_tokens=117`
- Live failure-path probe exposed the silent-drop bug directly:
  - patched `format_pair_metadata()` to raise `FileNotFoundError('missing pairs.yaml')`
  - `format_voice_directives('bina', ...)` still returned successfully
  - probe output: `pair_present False`, `layer_tokens 280`
- Loader-cache probe showed spec drift:
  - clear cache
  - load all four characters
  - `yaml.safe_load` call count = `4`
- No `PHASE_D_assembled_*_2026-04-12.txt` sample artifacts are present under `Docs/_phases/_samples/`

#### Drift against specification

- The happy path for Work Items 2-4 is implemented: typed metadata exists, the formatted block exists, and live Layer 5 prepends it before voice guidance.
- Work Item 1 is only partially met. The loader exists, but it does not parse once at module init and the live formatting path hides missing-file errors instead of surfacing them.
- Work Item 6 is only partially met. The named coverage for all four canonical phrase checks and live `assemble_context()` assertions is missing.
- Acceptance criterion `AC-6` is unmet because no Phase D sample files exist.
- The canonical Step 1 / Step 2 execution record is missing, so the phase file is not QA-ready.

#### Verified resolved

- `src/starry_lyfe/canon/pairs_loader.py` exists and returns a frozen typed dataclass with all eight canonical fields.
- `format_pair_metadata(character_id)` returns the expected six-line structured block and excludes `shared_functions` / `cadence`.
- In live prompts, Layer 5 now carries the `PAIR:` block before voice guidance for all four characters.
- Default-budget Layer 5 output remains within the current `DEFAULT_BUDGETS.voice` budget for all four characters on the happy path.
- The unit suite, lint, and type-check gates remain clean after Phase D (`136` unit tests passing, `ruff` pass, `mypy` pass).

#### Adversarial scenarios constructed

1. **Missing-loader failure-path probe:** patched `format_pair_metadata()` to raise `FileNotFoundError` and confirmed the live formatter silently dropped the pair block instead of surfacing an error.
2. **Coverage reality check:** compared the accepted spec's all-four canonical phrase assertions and live `assemble_context()` requirement to the shipped tests; the suite stops at helper-level checks plus a single-character content assertion.
3. **Cache-discipline probe:** patched `yaml.safe_load` and loaded all four characters after clearing cache; the loader reparsed the file four times instead of once.
4. **Artifact trail check:** scanned `Docs/_phases/_samples/` for `PHASE_D_assembled_*` files and found none.

#### Recommended remediation order

1. Fix `F1` first. Silent degradation of the Phase D metadata block is the main runtime defect.
2. Fix `F2` next. Tighten the tests around the live prompt path and all-four canonical phrases so the defect surface is actually defended.
3. Fix `F3` after the code/test corrections. The canonical record and prompt samples need to exist before QA.
4. Fix `F4` last. It is implementation drift and a small performance hit, not a demonstrated user-visible break on the current happy path.

#### Gate recommendation

**FAIL**

Phase D should not proceed to QA yet. The happy path is working, but the failure path is wrong, the tests do not fully cover the accepted contract, and the canonical phase record plus sample artifacts are still missing.

<!-- HANDSHAKE: Codex -> Claude Code | Audit Round 1 complete. FAIL gate. F1 High: Layer 5 silently drops pair metadata when the loader fails instead of raising a clear error. F2 Medium: Phase D tests do not cover the accepted spec or the live assemble_context path. F3 Medium: the canonical Phase D record and PHASE_D sample artifacts are still missing. F4 Low: pairs_loader reparses pairs.yaml on each character cache miss instead of loading once. Ready for remediation Round 1. -->

---

## Step 4: Remediate (Claude Code, if audit FAIL)

**[STATUS: PENDING]**
**Owner:** Claude Code (only if Step 3 returns FAIL)

---

## Step 3': Audit (Codex) — Round 2

**[STATUS: COMPLETE - handed to Claude Code for remediation Round 2]**
**Owner:** Codex
**Reads:** Remediation commit `e7e0175`, current code/tests, and the current phase file
**Writes:** This section with re-audit findings and updated gate recommendation

### Round 2 audit content

#### Scope

Reviewed:

- remediation commit `e7e0175`
- current `src/starry_lyfe/canon/pairs_loader.py`
- current `src/starry_lyfe/context/layers.py`
- current `tests/unit/test_pairs_loader.py`
- current `tests/unit/test_assembler.py`
- current `Docs/_phases/PHASE_D.md`
- `Docs/_phases/_samples/` for `PHASE_D_assembled_*` artifacts

Because Step 4 is still not canonically filled, this re-audit used the landed remediation commit plus live runtime probes as the remediation record.

#### Verification context

Independent checks run during re-audit:

- `.venv\Scripts\python -m pytest tests/unit/test_pairs_loader.py tests/unit/test_assembler.py -q` -> **PASS** (`64 passed`)
- `.venv\Scripts\python -m pytest tests/unit -q` -> **PASS** (`139 passed`)
- `.venv\Scripts\python -m ruff check src/ tests/` -> **PASS**
- `.venv\Scripts\python -m mypy src/` -> **PASS**
- `.venv\Scripts\python -m pytest -q` -> **ENVIRONMENTAL FAIL** (`139 passed, 14 errors`) because PostgreSQL remains unreachable during integration setup at `tests/integration/conftest.py:92`

Runtime probes performed:

- live `assemble_context(...)` probe across Adelia, Bina, Reina, and Alicia using the canonical unit-test stub retrieval path to confirm Layer 5 still carries `PAIR:`, `CLASSIFICATION:`, and `CORE METAPHOR:`
- failure-path probe that patched `starry_lyfe.canon.pairs_loader.format_pair_metadata` to raise `FileNotFoundError`
- single-parse probe that patched `yaml.safe_load` and counted parse calls while loading all four characters
- sample-artifact existence check for `Docs/_phases/_samples/PHASE_D_assembled_*_2026-04-12.txt`

#### Executive assessment

The substantive runtime remediation is good. The silent Layer 5 fallback is gone, the loader now parses `pairs.yaml` once per cache lifetime instead of once per character, and the test suite meaningfully improved with all-four canonical phrase coverage plus explicit regression tests for error propagation and single-parse behavior. Live prompts for all four characters still carry the pair metadata block before voice guidance.

The phase is still not fully converged as a canonical artifact. The remediation never filled Step 1, Step 2, or Step 4 in `PHASE_D.md`, and the required `PHASE_D_assembled_*` sample prompt artifacts still do not exist. The strengthened tests also still stop short of the accepted live `assemble_context()` regression named in the Phase D spec; the current Layer 5 assertions remain helper-level. Because the remaining issues are documentation / artifact completeness plus one residual coverage gap rather than a live runtime defect, the gate recommendation improves to **PASS WITH MINOR FIXES**.

#### Findings

| # | Severity | Finding | Evidence | Recommended fix |
|---:|---|---|---|---|
| R2-F1 | Medium | The canonical Phase D record is still not QA-ready: Step 1, Step 2, and Step 4 remain `PENDING`, and the required Phase D sample artifacts still do not exist. | `Docs/_phases/PHASE_D.md:113`, `:126`, and `:252` still show Step 1, Step 2, and Step 4 as `PENDING` despite remediation commit `e7e0175` landing. `Get-ChildItem Docs/_phases/_samples/PHASE_D_assembled_*_2026-04-12.txt` still returns count `0`. That leaves no canonical execution log, remediation table, or sample prompt evidence for QA. | Fill Step 1, Step 2, and Step 4 truthfully from the landed execution/remediation history and generate the four `PHASE_D_assembled_*_2026-04-12.txt` prompt artifacts from the live runtime. |
| R2-F2 | Low | The accepted live `assemble_context()` regression test for Layer 5 pair metadata is still missing. | `tests/unit/test_pairs_loader.py:126-140` still checks `format_voice_directives(..., None)` directly rather than asserting the wrapped Layer 5 content through live `assemble_context()`. The original broad test gap is improved, but the specific accepted test case `test_layer_5_contains_pair_metadata_block` as a live `assemble_context()` call is still not present. | Add one live `assemble_context()` regression that asserts Layer 5 contains `PAIR:`, `CLASSIFICATION:`, `MECHANISM:`, `CORE METAPHOR:`, `WHAT SHE PROVIDES:`, and `HOW SHE BREAKS HIS SPIRAL:` for all four characters. |

#### Runtime probe summary

- Live happy-path prompt probes remain correct after remediation:
  - `adelia`: `PAIR:=True`, `CLASSIFICATION:=True`, `CORE METAPHOR:=True`, `layer5_tokens=314`
  - `bina`: `PAIR:=True`, `CLASSIFICATION:=True`, `CORE METAPHOR:=True`, `layer5_tokens=333`
  - `reina`: `PAIR:=True`, `CLASSIFICATION:=True`, `CORE METAPHOR:=True`, `layer5_tokens=342`
  - `alicia`: `PAIR:=True`, `CLASSIFICATION:=True`, `CORE METAPHOR:=True`, `layer5_tokens=117`
- Live failure-path probe now behaves correctly:
  - patched `format_pair_metadata()` to raise `FileNotFoundError('pairs.yaml missing')`
  - `format_voice_directives('bina', ...)` now raises `FileNotFoundError` instead of silently dropping the block
- Single-parse probe now behaves correctly:
  - clear cache
  - load all four characters
  - `yaml.safe_load` call count = `1`
- No `PHASE_D_assembled_*_2026-04-12.txt` sample artifacts are present under `Docs/_phases/_samples/`

#### Drift against specification

- Original `F1` is fixed: missing pair metadata no longer fails silently.
- Original `F4` is fixed in substance: the loader now parses once per cache lifetime for all four characters together.
- Original `F2` is partially fixed: all-four canonical phrase coverage landed, but the accepted live `assemble_context()` regression is still missing.
- Original `F3` remains open: the canonical phase record and sample prompt artifacts are still absent.

#### Verified resolved

- `src/starry_lyfe/context/layers.py` no longer swallows pair-loading errors; the failure path is now explicit.
- `src/starry_lyfe/canon/pairs_loader.py` now populates the full character cache from a single YAML parse.
- `tests/unit/test_pairs_loader.py` now checks all four characters' canonical pair phrases and includes targeted regressions for the original F1/F4 failures.
- The unit suite, lint, and type-check gates remain clean after remediation (`139` unit tests passing, `ruff` pass, `mypy` pass).

#### Adversarial scenarios constructed

1. **Failure-path re-probe:** patched `format_pair_metadata()` to raise and confirmed the error now propagates instead of producing a degraded Layer 5.
2. **Single-parse re-probe:** patched `yaml.safe_load` and confirmed all four-character lookup now parses once, not four times.
3. **Coverage reality check:** re-read the strengthened tests and confirmed they still stop at `format_voice_directives()` rather than the accepted live `assemble_context()` path.
4. **Artifact trail re-check:** scanned `Docs/_phases/_samples/` again and confirmed no `PHASE_D_assembled_*` files exist.

#### Recommended remediation order

1. Fix `R2-F1` first. The phase cannot go to QA without a canonical execution/remediation record and sample artifacts.
2. Fix `R2-F2` last. It is a residual regression-gap, not a demonstrated live defect.

#### Gate recommendation

**PASS WITH MINOR FIXES**

Phase D's runtime defects are closed. The remaining work is to complete the canonical phase record, generate the missing sample artifacts, and add the last accepted live-path regression test before QA.

<!-- HANDSHAKE: Codex -> Claude Code | Audit Round 2 complete. PASS WITH MINOR FIXES. Original F1 and F4 verified fixed. Remaining: R2-F1 Medium (canonical phase record + PHASE_D samples still missing), R2-F2 Low (live assemble_context regression still missing). Ready for remediation Round 2. -->

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
