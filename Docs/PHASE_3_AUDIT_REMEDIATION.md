# Phase 3 Audit Remediation

**Phase:** 3 (Context Assembly)  
**Audit type:** Post-implementation audit  
**Date:** 2026-04-10  
**Auditor:** Codex  
**Verdict:** **PHASE 3 NOT CLOSED**

---

## 1. Scope

This audit evaluates the Phase 3 implementation in `src/starry_lyfe/context/` against the stated Phase 3 contract in:

- `Docs/Claude_Code_Handoff_v7.1.md`
- `Docs/IMPLEMENTATION_PLAN_v7.1.md`

It covers:

- seven-layer prompt assembly
- terminal anchoring of Whyze-Byte constraints
- Alicia presence-conditional assembly
- per-layer token budgets and trimming behavior
- scene/current-activity injection
- voice-layer implementation
- Gate 3 test coverage

---

## 2. Findings Summary

| ID | Severity | Finding | Result |
|---|---|---|---|
| P3-01 | HIGH | Terminal anchoring is not actually terminal | The assembled prompt appends another instruction block after Layer 7, violating the final-block contract |
| P3-02 | HIGH | Alicia's presence-conditional assembly is not enforced | Alicia can be assembled for in-person scenes even when away between operations |
| P3-03 | HIGH | Token budget enforcement is largely unimplemented | Most layers are never trimmed, and no end-to-end budget pass exists |
| P3-04 | MEDIUM | Scene/current-activity inputs are dropped from the final prompt | `scene_context` and `scene_description` do not become prompt content |
| P3-05 | MEDIUM | Layer 5 does not implement the specified voice few-shot layer | The assembler summarizes baseline metadata but does not load canonical voice calibration content |
| P3-06 | MEDIUM | Gate 3 tests are too weak to catch the current Phase 3 defects | The test suite never exercises `assemble_context()` or the actual prompt ordering rules |

---

## 3. Detailed Findings

### P3-01: Terminal anchoring is not actually terminal

The Phase 3 contract is explicit that the final block must be the Whyze-Byte constraint section:

- `Docs/Claude_Code_Handoff_v7.1.md:352`
- `Docs/IMPLEMENTATION_PLAN_v7.1.md:25`

But the implementation appends a separate system note after the wrapped constraint block:

- `src/starry_lyfe/context/assembler.py:100-105`

So the prompt currently ends with:

1. wrapped constraints
2. a trailing `[SYSTEM: ...]` note

That means Layer 7 is not actually the final block immediately before the user's latest input. This is a structural violation of the terminal-anchoring requirement, not a stylistic difference.

The self-check also does not verify real prompt order:

- `src/starry_lyfe/context/types.py:40-43`

`AssembledPrompt.is_terminally_anchored` only checks a metadata string, so it can report success even when the prompt body is not terminally anchored.

### P3-02: Alicia's presence-conditional assembly is not enforced

Gate 3 requires:

- `Docs/Claude_Code_Handoff_v7.1.md:354`

The code already models the required inputs:

- `src/starry_lyfe/context/types.py:12-17`

But `assemble_context()` never branches on either:

- `src/starry_lyfe/context/assembler.py:44-117`

And the repo-wide usage confirms those fields are effectively dead:

- `alicia_home` appears only in `SceneState` and one unit test
- `communication_mode` appears only in `SceneState`

The only Alicia-specific behavior currently implemented is textual guidance inside the constraint block:

- `src/starry_lyfe/context/constraints.py:52-59`

That is not a gate. It still assembles an in-person Alicia prompt while she is away, which violates the presence-conditional contract.

### P3-03: Token budget enforcement is largely unimplemented

The Phase 3 contract requires:

- `Docs/Claude_Code_Handoff_v7.1.md:348-349`
- `Docs/Claude_Code_Handoff_v7.1.md:355`

The code defines a full budget model:

- `src/starry_lyfe/context/budgets.py:8-28`

But only two narrow call sites actually trim content:

- episodic memories: `src/starry_lyfe/context/layers.py:47-62`
- open-loop lines inside scene blocks: `src/starry_lyfe/context/layers.py:156-161`

The following remain unbounded:

- kernel: `src/starry_lyfe/context/layers.py:21-29`
- canon facts: `src/starry_lyfe/context/layers.py:32-44`
- sensory grounding: `src/starry_lyfe/context/layers.py:71-100`
- voice directives: `src/starry_lyfe/context/layers.py:103-126`
- Whyze-Byte constraints: `src/starry_lyfe/context/assembler.py:83-90`
- total prompt assembly: `src/starry_lyfe/context/assembler.py:108-109`

There is also no canonical prioritization engine beyond "keep list order until one helper hits a budget." That does not satisfy the deliverable that over-budget layers are trimmed by explicit prioritization rules rather than arbitrary truncation.

The token accounting is also inconsistent: Layer 7 uses raw word count instead of the shared token estimator:

- `src/starry_lyfe/context/assembler.py:88`
- compare with `src/starry_lyfe/context/budgets.py:31-39`

### P3-04: Scene/current-activity inputs are dropped from the final prompt

The handoff requires Layer 6 to include scene blocks and current activity:

- `Docs/Claude_Code_Handoff_v7.1.md:345`

But the assembler currently uses `scene_context` only for memory retrieval embeddings:

- `src/starry_lyfe/context/assembler.py:46`
- `src/starry_lyfe/context/assembler.py:62-68`

It does not include `scene_context` in the final prompt body at all.

Likewise, `SceneState.scene_description` exists:

- `src/starry_lyfe/context/types.py:16`

But it is never read by any formatter or by `assemble_context()`.

Layer 6 currently emits only:

- Whyze dyad metrics
- internal dyad metrics
- open loops

See:

- `src/starry_lyfe/context/layers.py:129-163`

Layer 4 likewise contains only somatic-state summaries, not environmental or activity grounding:

- `src/starry_lyfe/context/layers.py:71-100`

So the current implementation does not actually inject current activity or explicit scene state into the assembled prompt.

### P3-05: Layer 5 does not implement the specified voice few-shot layer

The Phase 3 deliverable defines Layer 5 as voice few-shots:

- `Docs/Claude_Code_Handoff_v7.1.md:345`

The implementation does not load any voice calibration files. The only file loader in the context package is the persona-kernel loader:

- `src/starry_lyfe/context/kernel_loader.py:9-13`

And Layer 5 currently formats a short metadata summary from `CharacterBaseline.voice_params`:

- `src/starry_lyfe/context/layers.py:103-126`

That means the assembler is not consuming the canonical `Characters/*/*_Voice.md` material as a prompt layer. Relative to the handoff contract, Layer 5 is incomplete.

If the project now intends voice few-shots to remain Msty-owned only, then the handoff and verification gate need to be corrected to match that authority split. As written today, the implementation and the contract do not agree.

### P3-06: Gate 3 tests are too weak to catch the current defects

The current Phase 3 tests:

- `tests/unit/test_assembler.py:1-117`

They verify constants, string presence, and helper behavior, but they do not:

- call `assemble_context()`
- assert that the final prompt ends with Layer 7
- test Alicia away-state rejection
- test per-character prompt differences at the assembled-prompt level
- test budget enforcement on over-budget inputs
- test that current activity or scene description appears in the prompt

The existing "terminal anchoring" test is especially weak:

- `tests/unit/test_assembler.py:86-95`

It instantiates `AssembledPrompt` directly with `constraint_block_position="terminal"` and then asserts the property returns `True`. It does not inspect the prompt body, layer order, or real assembler output.

This is why the repository currently reports green tests while the core Gate 3 contract is still violated.

---

## 4. Verification Snapshot

Local verification during this audit:

- `python -m ruff check src tests` -> PASS
- `python -m mypy src tests` -> PASS
- `python -m pytest tests/unit/test_assembler.py -q` -> PASS (`13 passed`)
- `python -m pytest tests -q` -> PASS (`59 passed`)

This is important context: the current test suite is green, but it is not strong enough to prove Phase 3 correctness.

---

## 5. Recommended Remediation Order

1. Fix terminal anchoring so Layer 7 is the actual final block and remove any trailing post-constraint instruction text.
2. Enforce Alicia presence-conditional assembly using `alicia_home` plus explicit remote communication modes.
3. Implement real budget enforcement across all seven layers with deterministic prioritization rules and consistent token accounting.
4. Inject current scene/activity state into Layer 6, and decide what belongs in Layer 4 versus Layer 6.
5. Resolve the Layer 5 contract mismatch: either load canonical voice few-shot material or formally narrow the spec and tests to the thinner metadata-based layer.
6. Rewrite Gate 3 tests so they call `assemble_context()` and verify actual prompt structure, gating, budgets, and character-specific output.

---

## 6. Verdict

**Phase 3 is not closed.**

The codebase now has the beginnings of a context assembly layer, but several of the phase's non-negotiable requirements are still missing or structurally violated:

- terminal constraints are not actually terminal
- Alicia presence-gating is not enforced
- budget handling is mostly unimplemented
- current scene/activity context is not assembled
- the real Gate 3 contract is not being tested

Until those are fixed, the current implementation should be treated as a partial scaffold rather than a completed Phase 3 delivery.
