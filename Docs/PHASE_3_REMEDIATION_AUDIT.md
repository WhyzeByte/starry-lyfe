# Phase 3 Remediation Audit

**Phase:** 3 (Context Assembly)  
**Audit type:** Post-remediation verification  
**Date:** 2026-04-10  
**Auditor:** Codex  
**Prior document:** `PHASE_3_AUDIT_REMEDIATION.md`  
**Verdict:** **PHASE 3 NOT CLOSED**

---

## 1. Scope

This audit re-checks the current Phase 3 implementation in `src/starry_lyfe/context/` after remediation work, with focus on:

- terminal anchoring
- Alicia presence gating
- token-budget enforcement
- scene/activity injection
- Layer 5 voice implementation
- Gate 3 test adequacy

Primary authority references:

- `Docs/Claude_Code_Handoff_v7.1.md`
- `Docs/IMPLEMENTATION_PLAN_v7.1.md`

---

## 2. Prior Findings Status

The following previously-audited issues are now materially resolved:

| Prior ID | Prior issue | Current state |
|---|---|---|
| P3-01 | Constraint block was not actually terminal | Resolved. The assembled prompt now ends with `</CONSTRAINTS>` and no trailing post-constraint block. |
| P3-04 | Scene/current-activity inputs were dropped | Largely resolved. `scene_description` is now injected into Layer 4 and Layer 6. |

The following were only partially remediated:

| Prior ID | Prior issue | Current state |
|---|---|---|
| P3-02 | Alicia presence-conditional assembly absent | Partially resolved. Canonical in-person-away assembly now raises, but the gate is still bypassable through arbitrary `communication_mode` values. |
| P3-03 | Budget enforcement absent | Partially resolved. Kernel and canon facts now attempt trimming, but real budget compliance still fails on live assembly. |
| P3-05 | Layer 5 contract mismatch | Shifted, not closed. The backend now loads voice files, but it loads the raw `Voice.md` documents rather than a backend-safe layer. |
| P3-06 | Gate 3 tests too weak | Still open. The test suite still does not exercise `assemble_context()` itself. |

---

## 3. Findings Summary

| ID | Severity | Finding | Result |
|---|---|---|---|
| R3-01 | HIGH | Budget enforcement still fails on real prompt assembly | A normal assembled prompt exceeds both per-layer and total budgets |
| R3-02 | HIGH | Alicia's away-state gate is still bypassable | Any non-`in_person` free-form mode string allows assembly, not just canonical `phone` / `letter` cases |
| R3-03 | MEDIUM | Layer 5 still injects raw Msty few-shot files into the backend prompt | The prompt includes Msty UI instructions plus literal `User`/`Assistant` example blocks |
| R3-04 | MEDIUM | Gate 3 tests still do not verify real assembled output | Remaining behavioral defects pass with green tests because `assemble_context()` is never exercised |

---

## 4. Detailed Findings

### R3-01: Budget enforcement still fails on live prompt assembly

The Phase 3 gate still requires:

- `Docs/Claude_Code_Handoff_v7.1.md:355`

The implementation now includes budget hooks:

- `src/starry_lyfe/context/layers.py:21-39`
- `src/starry_lyfe/context/layers.py:42-58`

But it still does not enforce budget compliance end-to-end:

- `src/starry_lyfe/context/layers.py:125-160` has no budget parameter or trimming path for Layer 5
- `src/starry_lyfe/context/layers.py:85-122` has no budget enforcement for Layer 4
- `src/starry_lyfe/context/assembler.py:120` only sums layer totals; it never performs a final budget pass

The kernel trim path also overshoots its own budget:

- `src/starry_lyfe/context/layers.py:28-33`

It truncates to an estimated budget, then appends a trimming note, which pushes the resulting layer back over budget.

Observed on a live `assemble_context()` run for Bina with a stub embedding service:

- Layer 1 `persona_kernel`: `2006 / 2000`
- Layer 5 `voice_directives`: `2817 / 200`
- Total prompt: `5333 / 5300`

So the remediation added budgeting machinery, but the Gate 3 budget contract is still not satisfied.

### R3-02: Alicia's away-state gate is still bypassable

The written requirement remains:

- `Docs/Claude_Code_Handoff_v7.1.md:354`

The gate now exists:

- `src/starry_lyfe/context/assembler.py:69-75`

But `SceneState.communication_mode` is still an unconstrained free-form string:

- `src/starry_lyfe/context/types.py:12-17`

And the gate only blocks the literal value `"in_person"`:

- `src/starry_lyfe/context/assembler.py:70`

That means any unexpected value bypasses the gate. During audit, `communication_mode="sms"` allowed Alicia to assemble while `alicia_home=False`.

This is still a real contract violation because the implementation message itself says the only intended remote exceptions are:

- `phone`
- `letter`

but the code does not enforce that boundary.

### R3-03: Layer 5 still injects raw Msty few-shot files into the backend prompt

The production authority split says:

- `Docs/IMPLEMENTATION_PLAN_v7.1.md:7`
- `Docs/IMPLEMENTATION_PLAN_v7.1.md:47`

The handoff also treats the `Voice.md` files as the canonical few-shot calibration material:

- `Docs/Claude_Code_Handoff_v7.1.md:38`
- `Docs/Claude_Code_Handoff_v7.1.md:276`

The current code comments claim Layer 5 only loads backend-safe "voice calibration notes":

- `src/starry_lyfe/context/layers.py:129-134`
- `src/starry_lyfe/context/kernel_loader.py:48-52`

But the implementation reads and injects the entire raw file:

- `src/starry_lyfe/context/kernel_loader.py:66-68`
- `src/starry_lyfe/context/layers.py:150-153`

Those raw files contain:

- Msty UI copy instructions
- literal `**User:**` / `**Assistant:**` blocks
- full few-shot content

Observed on a live Bina prompt assembly:

- `Msty Persona Studio` appeared in the prompt
- `**User:**` appeared in the prompt
- `**Assistant:**` appeared in the prompt

So this remediation did not produce a clean backend-side voice layer. It imported the full Msty-side artifact into the backend prompt, which also explains the Layer 5 budget blowout in R3-01.

### R3-04: Gate 3 tests still do not verify real assembled output

The current Phase 3 tests are here:

- `tests/unit/test_assembler.py:1-184`

They now cover more helper structure than before, but they still do not:

- call `assemble_context()`
- inspect a real prompt built from canonical kernel + memory + voice content
- assert layer token counts against budgets
- assert Alicia's gate rejects all non-canonical away modes
- assert Layer 5 excludes raw Msty few-shot blocks

During audit:

- `rg -n "assemble_context\\(" tests` returned no matches

That explains why the current repository still reports green verification while R3-01 through R3-03 remain present.

---

## 5. Verification Snapshot

Local verification during this remediation audit:

- `python -m ruff check src tests` -> PASS
- `python -m mypy src tests` -> PASS
- `python -m pytest tests -q` -> PASS (`67 passed`)

Additional live audit probes:

- `assemble_context()` for Bina produced a terminally anchored prompt
- The same prompt still contained `Msty Persona Studio`, `**User:**`, and `**Assistant:**`
- The same prompt exceeded budget (`5333 / 5300`)
- `assemble_context()` for Alicia with `alicia_home=False` and `communication_mode='in_person'` correctly raised `AliciaAwayError`
- `assemble_context()` for Alicia with `alicia_home=False` and `communication_mode='sms'` incorrectly assembled

---

## 6. Recommended Remediation Order

1. Fix Layer 5 first: extract backend-safe voice guidance instead of loading the raw `Voice.md` files.
2. Enforce a validated communication-mode enum or equivalent whitelist so Alicia assembly only permits canonical remote modes.
3. Implement real per-layer and total-budget enforcement after Layer 5 is corrected.
4. Add Gate 3 tests that call `assemble_context()` and assert actual prompt content, budget compliance, and Alicia gating.

---

## 7. Verdict

**Phase 3 is improved but still not closed.**

The highest-risk structural defects from the first audit were partially remediated:

- terminal anchoring is now real
- scene description now reaches the prompt
- Alicia's in-person away-state now has a gate

But the remaining defects are still substantive:

- budget compliance fails in real output
- Alicia's gate is bypassable
- Layer 5 still imports raw Msty few-shot artifacts
- tests remain too weak to catch these failures

Phase 3 should be treated as partially remediated, not signed off.
