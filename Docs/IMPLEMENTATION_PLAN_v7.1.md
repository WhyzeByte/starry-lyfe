# Starry-Lyfe v7.1 Backend Architecture and Implementation Plan

**Version:** 7.1 (Master Integration)
**Date:** 2026-04-10
**Supersedes:** Original `IMPLEMENTATION_PLAN_v7.1.md` (architecture only) + `Soul_Preservation_Plan_Elevated.md` (execution only) — both consolidated into this single document
**Authority:** This document is the canonical implementation plan for the v7.1 backend. The two source documents remain in the project tree as historical reference, but execution should follow this integrated plan.

---

## Document Origin and Authority

This master plan integrates two prior documents:

1. **`IMPLEMENTATION_PLAN_v7.1.md`** (the architectural plan) — defined what the backend is, the production authority split, the seven memory tiers, the seven-layer prompt assembly with terminal anchoring, the per-character inference parameters, the Whyze-Byte validation pipeline, the Scene Director, the Dreams engine, and the twelve-step end-to-end request flow. Authored before Phase 3 was running. Architectural commitments only.

2. **`Soul_Preservation_Plan_Elevated.md`** (the execution plan) — defined thirteen phases (0, A, A', A'', B, I, C, D, E, F, G, J, H, K) for moving the Phase 3 backend from "preserves constraint integrity" to "preserves the full nervous system." Authored after Phase 3 was running and after four character conversion audits surfaced specific runtime fidelity defects. Execution work only.

The relationship is that the Implementation Plan defined the system to build; the Soul Preservation Plan defined how to make Phase 3 of that system actually preserve the characters' souls. Holding them as separate documents created cross-reference burden and made it hard to read execution work in the context of the architectural commitments it serves. This master plan resolves that by embedding the execution phases as subsections under the architectural sections they implement.

The Implementation Plan section numbering (§1 through §10) is preserved unchanged because it is referenced from `Claude_Code_Handoff_v7.1.md`, `Persona_Tier_Framework_v7.1.md`, `CHARACTER_CONVERSION_PIPELINE.md`, `ARCHITECTURE.md`, and the four character conversion audit documents. The Soul Preservation Plan phase identifiers (A, A', A'', B, C, D, E, F, G, H, I, J, K, plus the new Phase 0) are also preserved because they are referenced from the same audit documents.

The closing nine-word statement of the Soul Preservation Plan is preserved verbatim at the end of this document because it is the right epigraph for the entire body of work:

> *The edges are necessary. The soul is the point.*

---

## Current Project State (Baseline)

As of 2026-04-10, the backend is partially implemented:

- **Phase 1 (Canon YAML) — COMPLETE.** Six canon files (`characters.yaml`, `pairs.yaml`, `dyads.yaml`, `protocols.yaml`, `interlocks.yaml`, `voice_parameters.yaml`) with Pydantic schemas in `src/starry_lyfe/canon/`. See `Docs/ARCHITECTURE.md` for the module registry.
- **Phase 2 (Memory Service) — COMPLETE.** Seven memory tiers in PostgreSQL schema `starry_lyfe`, pgvector HNSW for episodic memories, exponential decay for Tier 7, Alicia-orbital dyad persistence logic.
- **Phase 3 (Context Assembly) — IN PROGRESS.** `kernel_loader.py`, `layers.py`, `assembler.py`, `budgets.py`, `constraints.py` exist and function. Test suite at 86 passing as of the ALICIA audit (2026-04-10). The execution phases A through G in this document operate on this existing code, not on a greenfield build.
- **Phase 4 (Whyze-Byte Validation Pipeline) — PLANNED.** Architecture defined in §7. Not yet implemented.
- **Phase 5 (Scene Director) — PLANNED.** Architecture defined in §8. Phase F adds scene type infrastructure that the Scene Director will consume.
- **Phase 6 (Dreams Engine) — PLANNED.** Architecture defined in §9.
- **Phase 7 (HTTP service on port 8001) — PLANNED.** Service surface defined in §2.

**Two pipeline-level fixes have already landed in code between audits.** The REINA conversion audit (2026-04-10) and the ALICIA conversion audit (also 2026-04-10) both verify in their "Verified Resolved" sections that:
- The Talk-to-Each-Other mandate trigger now correctly fires only for multi-woman scenes (`constraints.py:104`)
- Offstage internal dyads no longer leak into focal-character prompts (`layers.py:232-240`)

These fixes were originally specified in Phase A' work items 1 and 2 below. They remain in the document as historical record but are marked **VERIFIED RESOLVED**.

**Character kernel canonical state:**

- `Characters/Adelia/Adelia_Raye_v7.1.md` — v7.1 canonical, verified clean
- `Characters/Bina/Bina_Malek_v7.1.md` — v7.1 canonical, parents corrected to Malek
- `Characters/Reina/Reina_Torres_v7.1.md` — v7.1 canonical
- `Characters/Reina/Reina_Torres_Kinetic_Pair.md` — v7.1 cleaned 2026-04-10 (was carrying `_v7.0.md` cross-reference and stale Alicia framing)
- `Characters/Alicia/Alicia_Marin_v7.1.md` — v7.1 canonical
- `Characters/Shawn/Shawn_Kroon_v7.0.md` — deliberately excluded per operator instruction; Shawn = Whyze (legal name vs system handle for the same person)

**Alicia residence framing (settled canon, repeated here because it kept resurfacing):** Alicia is a **resident** at the property who is **frequently away on consular operations**. Her dyads activate when she is home. Any prose that calls her "non-resident" or "visiting twice yearly" is stale and should be updated if encountered.

---

## Vision Alignment Matrix

Every architectural section and every execution phase in this plan must be traceable to a specific section of `Vision/Starry-Lyfe_Vision_v7.1.md`. The matrix below makes the alignment explicit.

| Architectural section | Execution phases | Primary Vision authority |
|---|---|---|
| §1 Production Authority Split | Phase I | §8 System Architecture |
| §2 The Backend Service | (architectural commitment) | §8 System Architecture |
| §3 Canon: Single Source of Truth | Phase 0, Phase C | §5 Chosen Family, §6 Relationship Architecture |
| §4 Context Assembly: Seven-Layer Prompt | Phase A, A', A'', B, D, E, F, G | §7 Behavioral Thesis, §9 Success Criteria |
| §5 Memory Service | (Phase 1+2 complete) | §6 Relationship Architecture, §7 Behavioral Thesis |
| §6 Inference Layer | (resolved) | §8 System Architecture |
| §7 Whyze-Byte Pipeline | (Phase 4 planned) | §7 Behavioral Thesis (cognitive hand-off contract) |
| §8 Scene Director | (Phase 5 planned; Phase F adds scene type infrastructure) | §6 Relationship Architecture (Rule of One, Talk-to-Each-Other) |
| §9 Dreams Engine | (Phase 6 planned) | §6 Relationship Architecture (decentralized narrative weight) |
| §10 End-to-End Request Flow | (synthesis of all subsystems) | §8 System Architecture |
| §11 Per-Character Remediation | Phase J (J.1, J.2, J.3, J.4) | §5 Chosen Family (non-redundancy guarantee) |
| §12 Verification and Quality Assurance | Phase H, Phase K | §9 Success Criteria (Ultimate Test) |

---

## Phase Dependency Graph

The execution phases run in this order. Phases nested under the same parent can run in parallel; phases listed sequentially must run in order.

```
Phase 0: Pre-flight Canon Verification
    |
Phase A: Structure-Preserving Compilation
    |
Phase A': Runtime Correctness Fixes
    |     (work items 1+2 VERIFIED RESOLVED in code)
Phase A'': Communication-Mode-Aware Pruning  (Alicia-specific from ALICIA audit)
    |
Phase B: Budget Elevation (with terminal anchoring preserved)
    |
Phase I: Authority Split Resolution  (PREREQUISITE to Phase E)
    |
    +---- Phase C: Soul Cards from Pair and Knowledge Stack
    |
    +---- Phase D: Live Pair Data in Prompt
    |
    +---- Phase E: Voice Exemplar Restoration
    |
Phase F: Scene-Aware Section Retrieval + Cross-Cutting Modifiers
    |
Phase G: Dramaturgical Prose Rendering with Per-Character Templates
    |
Phase J: Per-Character Remediation Passes
    |     J.1 (Bina) → J.2 (Adelia) → J.3 (Reina) → J.4 (Alicia)
    |
Phase H: Soul Regression Tests with Hybrid Methodology
    |
Phase K: Subjective Success Proxies
```

**Parallelism opportunities:**

- Phase A and Phase A' can run in parallel — they touch different files
- Phase A'' is Alicia-specific and can run in parallel with Phase A/A'/B for other characters
- Phase D, Phase C, and Phase E can run in parallel after Phase I resolves
- Phase F and Phase G touch different files and can run in parallel
- The Phase J sub-phases must run sequentially (J.1 first, then J.2, then J.3, then J.4)

**Critical path:** Phase 0 → A → B → I → C/E → F → G → J.1 → J.2 → J.3 → J.4 → H → K. Roughly 13 sequential steps. With reasonable parallelism, the total work fits in 8-10 working sessions for an attentive implementer.

---

## 1. Operating Model: The Production Authority Split

### Architecture

The most important architectural decision in Starry-Lyfe is the division of labor between Msty (the conversational frontend) and the Starry-Lyfe backend (the orchestration brain). In production, the backend owns all prompt authority. The backend owns canonical YAML, kernel assembly, model parameters, memory retrieval, life-state injection, Dreams, and Whyze-Byte. Msty is the conversational platform that provides Crew orchestration, quality monitoring through Shadow Persona, scene sequencing through Turnstiles, few-shot calibration, Knowledge Stacks, project-based scene governance, environmental grounding through Live Contexts, and workspace security.

Critically, Msty persona system prompts are blank or near-blank in production so the backend remains the sole source of character authority. Any incoming Msty system prompt is stripped server-side when model-name routing is active. This is a hard boundary — there is exactly one place where character voice is authored, and it is not Msty.

### Phase I: Authority Split Resolution

**Priority:** Prerequisite to Phase E (Voice Exemplar Restoration). Must resolve before Phase E starts.
**Vision authority:** §8 System Architecture; this section §1
**Original Soul Preservation Plan v1.0 mapping:** Recommendation 9

#### Why this is prerequisite

Phase E's central work item is restoring abbreviated voice exemplars to the backend. Whether the backend is **canonically permitted** to carry voice exemplars is exactly what the authority split resolves. Two options were considered:

**Option 1 — Backend-authoritative voice.** The backend carries abbreviated rhythm-calibration exemplars (2-3 sentence responses sliced from `Voice.md`) as part of Layer 5. Msty's persona studio few-shots are either empty or canonically generated derivatives of the backend's exemplar set. Voice authority lives in one place: the backend, sourced from `Voice.md`.

**Option 2 — Msty-authoritative voice.** The backend carries only meta-voice notes ("what this example teaches") in Layer 5. Msty's persona studio few-shots carry the full `**User:** / **Assistant:**` pairs and are the canonical rhythm source.

**Decision: Option 1 (backend-authoritative voice).** Rationale:

- §1 of this plan is explicit that *"Msty persona system prompts are blank or near-blank in production so the backend remains the sole source of character authority"*
- Option 1 keeps the canonical voice source in one place (`Voice.md` → compiled into backend Layer 5) with no drift surface
- Option 2 creates two voice surfaces and requires a separate drift-prevention mechanism to keep them synchronized

#### Work items

1. **Write `Docs/ADR_001_Voice_Authority_Split.md`** containing the decision, rationale, status (ACCEPTED), and consequences
2. **Update `Docs/CHARACTER_CONVERSION_PIPELINE.md`** to reflect the decision: Voice.md flows into both backend compilation and (via seed script) Msty persona studio
3. **Update `Docs/Claude_Code_Handoff_v7.1.md` §5.6** to note the authority decision and its implications for Phase E
4. **Create `scripts/seed_msty_persona_studio.py`** that compiles abbreviated exemplars from Voice.md and produces the Msty persona studio configuration. This script is the only canonical way Msty persona studio should be configured.

#### Exit criteria

- ADR_001 committed and ACCEPTED
- `CHARACTER_CONVERSION_PIPELINE.md` updated
- Seed script exists and produces a valid Msty persona studio configuration
- Phase E can begin

#### Files touched

- `Docs/ADR_001_Voice_Authority_Split.md` — new file
- `Docs/CHARACTER_CONVERSION_PIPELINE.md` — update
- `Docs/Claude_Code_Handoff_v7.1.md` — update §5.6
- `scripts/seed_msty_persona_studio.py` — new file

---

## 2. The Backend Service

### Architecture

The backend runs as a service on Port 8001 and exposes the following responsibilities: Context Assembly (memories, life state, activity context, sensory grounding), Model Routing (Claude via OpenRouter for all character content), Whyze-Byte Pipeline (two-tier validation gate), Speaker-by-speaker sequential validation, Scene Director (next-speaker selection engine). Three sibling services round out the backend tier: Memory Service (PostgreSQL + pgvector) — Seven-tier memory architecture, Semantic search retrieval, and Life Simulation ("Dreams" Scheduled Tasks) — Nightly REM-sleep processing for all characters, Daily schedule generation, Activity design (narrator, choices, environment), Off-screen events, diary entries, open loops.

### Implementation Status

- **Service surface (port 8001):** PLANNED. Phase 7 of the overall backend build. The service exists in design only at the time of this writing.
- **Context Assembly:** IN PROGRESS as Phase 3. The execution phases under §4 below describe the Soul Preservation work that elevates the assembly path.
- **Model Routing:** Architecture defined. Per-character inference parameters resolved at §6.
- **Whyze-Byte Pipeline:** PLANNED as Phase 4. Architecture defined at §7.
- **Scene Director:** PLANNED as Phase 5. Architecture defined at §8. Phase F adds the scene type infrastructure that the Scene Director will consume.
- **Memory Service:** COMPLETE (Phases 1+2). Architecture defined at §5.
- **Dreams Engine:** PLANNED as Phase 6. Architecture defined at §9.

There is no soul-preservation execution phase under §2 directly. Phase I (Authority Split Resolution) is the closest because it establishes who owns voice content, which is architectural rather than execution work. The actual context assembly execution phases live under §4.

---

## 3. Canon: The Single Source of Truth

### Architecture

All character data, world facts, and constraints originate from versioned YAML. The canonical YAML source is the single source of truth. Character data, world facts, relationship rules, protocols, and constraints are defined in `src/starry_lyfe/canon/` as YAML files. Generator scripts produce backend seeds and Whyze-Byte rules from this source. No character data is manually maintained in multiple locations.

This is what enables the deduplication rule between backend-injected operator context and Msty's User Persona — there cannot be two sources of truth without drift, so YAML wins everywhere.

### Phase 0: Pre-flight Canon Verification

**Priority:** Prerequisite. Run before touching any code.
**Vision authority:** §5 Chosen Family, §6 Relationship Architecture, §7 Behavioral Thesis

This phase is a lightweight verification pass that catches canon drift between the source-of-truth files and what subsequent phases will assume. It does not modify code or canon; it produces a "clean" or "not clean" verdict and a list of items to fix before Phase A starts.

#### Work items

1. **Run the v7.0 drift grep** from `Claude_Code_Handoff_v7.1.md` §8.1 across `src/`, `Docs/`, `Characters/`, `Vision/` (excluding `Characters/Shawn/`, per-character Vision directive files, and the Vision changelog appendix). Any match is a failure that must be resolved before proceeding.

   **Additional drift terms (added during REINA audit integration 2026-04-10):** the following stale Alicia framing phrases must also be grepped, because they were found in `Reina_Torres_Kinetic_Pair.md` L256 during the REINA audit and were not in the original drift token list:
   - `non-resident` (when applied to Alicia)
   - `twice yearly between operations`
   - `Spanish consular officer`
   - `based in Madrid`
   - `Alicia Marín` (with the diacritic; canonical form is `Alicia Marin` unaccented)
   - `_v7.0.md` cross-references in Pair/Knowledge files (canonical form is `_v7.1.md` for all four characters; Shawn is the only legitimate `_v7.0.md` exception)

   These terms slipped through the earlier multi-session cleanup because they were buried inside long sentences in pair file ecosystem-description sections. Phase 0 must catch them before any further work begins.

2. **Verify character kernel canonical state** by running this specific check for each of the four v7.1 characters:
   - Kernel mentions the correct canonical pair name (Entangled, Circuit, Kinetic, Solstice)
   - Kernel mentions no v7.0 pair names (Golden, Citadel, Synergistic, Elemental) except as deliberate historical references with rename annotations
   - Kernel surname and parents' surname match `characters.yaml`
   - Kernel §3 heading matches the canonical pair name
   - Kernel §5 behavioral tier framework references `Persona_Tier_Framework_v7.1.md` (not `_v7.md`)

3. **Verify Vision-kernel consistency** across the four characters. For each character, compare the Vision §5 one-paragraph summary against the character kernel §2 Core Identity. Flag drifts where the Vision summary is stale or the kernel is ahead. **Specific known drift (from `BINA_CONVERSION_AUDIT.md` Finding 7):** ~~Vision says Bina is "Canadian-born Assyrian"~~ **RESOLVED in Phase 0 (commit `c0edc0e`).** The Phase 0 Vision rewrite removed the heritage line from Vision §5 entirely — the new §5 Bina paragraph is essence-only ("The unshakeable anchor under pressure...") with biographical detail deferred to the kernel §2 where it is correctly stated as "First-generation Assyrian-Iranian Canadian... carried out of Urmia... Raised in Edmonton." The master plan's recommended phrasing "Canadian-born Assyrian from Urmia" was not adopted because the Vision rewrite chose a cleaner architectural approach: the Vision names function, the kernels carry life.

4. **Verify canon YAML consistency** with character kernels. `characters.yaml` field values for each character must match the kernel's canonical statement of the same field. Specific fields to check: `surname`, `parents`, `birthplace`, `pair_name`, `pair_classification`, `pair_mechanism`, `pair_core_metaphor`.

5. **Verify Alicia residence framing** is consistent across all files. Canonical statement: Alicia is a **resident** at the property who is **frequently away on consular operations**. Any file describing her as "non-resident" or "visiting twice yearly" is stale and must be updated.

#### Exit criteria

- Zero drift grep hits
- Zero Vision-kernel drifts (or all drifts explicitly resolved with a written decision)
- Zero canon YAML vs kernel mismatches
- Zero stale Alicia framing

#### Files touched

No code changes. Output is a verification report, optionally committed to `Docs/Phase_0_Verification_Report_{date}.md`.

### Phase C: Soul Cards from Pair and Knowledge Stack

**Priority:** High. The Pair files (15-17K tokens each) and Knowledge Stacks (10-80K tokens) contain the deepest character differentiation. Currently excluded from runtime entirely.
**Vision authority:** §5 Chosen Family (non-redundancy), §6 Relationship Architecture (interlocks as first-class elements)
**Original Soul Preservation Plan v1.0 mapping:** Recommendation 3

#### Source of truth relationship

- `pairs.yaml` remains the source of truth for structured pair fields (classification, mechanism, core metaphor, what she provides, how she breaks his spiral, cadence, shared functions)
- `Characters/{Name}/{Name}_{Pair}_Pair.md` remains the canonical authored reference for the pair architecture — cognitive interlock theory, synastry, intimate mechanics, scene-read instructions
- **Soul cards are a new artifact** that distill the narrative prose of the pair file and knowledge stack into compact, typed, runtime-loadable blocks
- Soul cards are **stored as markdown files** in `src/starry_lyfe/canon/soul_cards/` and loaded at context assembly time
- Soul cards are **human-authored** and then validated by a test that asserts they mention specific canonical concepts from their source file

The decision against automated distillation is deliberate. The earlier multi-session cleanup spent significant effort removing drift that an LLM had introduced; auto-generating soul cards would reintroduce that exact failure mode. Soul cards are short enough (500-700 tokens for pair cards, 300-500 for knowledge cards) that human authoring is bounded.

#### Soul card directory structure

```
src/starry_lyfe/canon/soul_cards/
├── pair/
│   ├── adelia_entangled.md
│   ├── bina_circuit.md
│   ├── reina_kinetic.md
│   └── alicia_solstice.md
└── knowledge/
    ├── adelia_cultural.md       (audit-driven addition from ADELIA F6)
    ├── adelia_workshop.md
    ├── adelia_pyrotechnics.md
    ├── bina_ritual.md
    ├── bina_grief.md
    ├── reina_stable.md
    ├── reina_court.md
    ├── alicia_rioplatense.md
    ├── alicia_famailla.md
    ├── alicia_operational.md
    └── alicia_remote.md         (audit-driven addition from ALICIA F1 / Phase A'')
```

#### Soul card schema

Each soul card is a markdown file with YAML frontmatter:

```markdown
---
character: bina
card_type: pair
source: Characters/Bina/Bina_Malek_Circuit_Pair.md
budget_tokens: 700
activation:
  always: true
required_concepts:
  - "Circuit Pair"
  - "Orthogonal Opposition"
  - "total division of operational domains"
  - "diagnostic love"
  - "translation not mirroring"
---

# Bina × Whyze — Circuit Pair Soul Card

[500-700 tokens of hand-authored prose distilling the pair architecture]
```

Frontmatter fields:

- `character`: one of `adelia`, `bina`, `reina`, `alicia`
- `card_type`: `pair` or `knowledge`
- `source`: path to the source file this card is distilled from
- `budget_tokens`: hard limit; test fails if the card exceeds this
- `activation`: conditions under which this card loads
  - `always: true` for pair cards (always load for the focal character's pair)
  - `scene_type: [intimate, domestic]` for scene-conditional cards
  - `scene_keyword: ["spanish", "castellano"]` for keyword-triggered cards
  - `with_character: ["reina"]` for dyad-triggered cards
  - `communication_mode: [phone, letter]` for mode-conditional cards (used by `alicia_remote.md` per Phase A'')
- `required_concepts`: list of strings that must appear in the card body; used by the validation test

#### Work items

1. **Implement the soul card loader.** `src/starry_lyfe/context/soul_cards.py` contains:
   ```python
   def load_soul_card(path: Path) -> SoulCard: ...
   def find_activated_cards(character: str, scene_state: SceneState) -> list[SoulCard]: ...
   def format_soul_cards(cards: list[SoulCard], budget: int) -> str: ...
   ```

2. **Integrate with Layer 1 / Layer 6.** The pair soul card for the focal character always loads into Layer 1 (kernel) as a separate subsection, budget-bounded to 700 tokens. Knowledge soul cards load scene-conditionally into Layer 6 (scene context), budget-bounded to 300-500 tokens each, up to the Layer 6 total budget.

3. **Author the four pair soul cards first.** Each pair soul card distills 500-700 tokens of prose from the source pair file covering the specific cognitive interlock, how they fight, how they repair, what the intimacy is not, and scene-read instructions. **The pair soul cards are authored by the project owner or a knowledgeable human reviewer, not by Claude Code.** The Plan ships with placeholders that fail the validation test until a human writes them.

4. **Author the knowledge soul cards in priority order** per the Phase J sub-phases below.

5. **Add soul card validation tests.** Token budget test, required concepts test, activation test.

#### Files touched

- `src/starry_lyfe/canon/soul_cards/` — new directory with 4 pair cards + 11 knowledge cards (placeholders initially)
- `src/starry_lyfe/context/soul_cards.py` — new loader module
- `src/starry_lyfe/context/layers.py` — integrate soul cards into Layer 1 (pair) and Layer 6 (knowledge)
- `src/starry_lyfe/context/assembler.py` — pass scene state through to soul card activation
- `tests/unit/test_soul_cards.py` — new test file

---

## 4. Context Assembly: The Seven-Layer Prompt

### Architecture

When a request arrives, the backend builds the system prompt that reaches Claude by composing seven distinct layers. The backend assembles the seven-layer context (kernel, canon, fragments, sensory, voice cards, scene blocks, Whyze-Byte constraints) and produces the system prompt that reaches the model.

A critical placement rule governs the last layer: The Whyze-Byte rules cannot exist as passive, background context buried at the top of the prompt. LLMs suffer from severe recency bias, causing them to deprioritize negative constraints the further they sit from the generation sequence. During context assembly, the character-specific strict constraints must be placed immediately before the user's latest input and the start of the assistant response. **Terminal anchoring of constraints is structural, not stylistic.**

This is the most-tested architectural commitment in the entire backend. Every execution phase under §4 must preserve terminal anchoring as a hard invariant. The Phase B budget elevation explicitly grows Layer 7 proportionally with earlier layers to prevent the constraint block's effective recency from degrading.

### The seven layers

| Layer | Name | Source | Default budget | Elevated budget (Phase B) |
|---|---|---|---:|---:|
| 1 | `PERSONA_KERNEL` | Kernel markdown from filesystem + pair soul card (Phase C) | 2000 | 6000 |
| 2 | `CANON_FACTS` | Database Tier 1 | 500 | 600 |
| 3 | `MEMORY_FRAGMENTS` | Database Tier 5 (pgvector search) | 1000 | 1200 |
| 4 | `SENSORY_GROUNDING` | Database Tier 7 + protocols.yaml + scene description | 300 | 500 |
| 5 | `VOICE_DIRECTIVES` | Database Tier 2 baseline + Voice markdown + pair metadata block | 200 | 900 |
| 6 | `SCENE_CONTEXT` | Database Tiers 3, 4, 6 + scene description + knowledge soul cards (Phase C) | 800 | 1200 |
| 7 | `CONSTRAINTS` | `constraints.py` (Tier 1 axioms + per-character pillars + scene gates) | 500 | 900 |
| **Total** | | | **5300** | **11300** |

**Layer 7 is always last** for terminal anchoring. Phase B grows Layer 7 from 500 to 900 tokens proportionally with the earlier layers to preserve this rule.

### Phase A: Structure-Preserving Compilation

**Priority:** Highest. More important than raising budgets. If the structure is damaged, more tokens of damaged text is still damaged text.
**Vision authority:** §8 System Architecture, §7 Behavioral Thesis
**Original Soul Preservation Plan v1.0 mapping:** Recommendation 1

#### Current state

`src/starry_lyfe/context/budgets.py` function `trim_text_to_budget()` splits the input on whitespace and rejoins with spaces. Section-aware compilation in `kernel_loader.py` picks the right sections but the resulting text loses headings, paragraph boundaries, bullets, and internal hierarchy.

#### Work items

1. **Rewrite `trim_text_to_budget()` to preserve markdown structure.** The function operates at the paragraph level, not the word level. Pseudocode:

   ```
   function trim_markdown_to_budget(text, token_limit):
       blocks = split_into_blocks(text)  # heading, paragraph, list, code, quote
       if total_tokens(blocks) <= token_limit:
           return text
       while total_tokens(blocks) > token_limit:
           dropped = blocks.pop()  # drop trailing block
           if dropped.type == "heading" and not blocks:
               raise TrimError("cannot trim below first heading")
       return reassemble(blocks)
   ```

2. **Define block types and their trim priority.** Blocks are one of: `h1`, `h2`, `h3`, `paragraph`, `bullet_list`, `numbered_list`, `code_block`, `blockquote`, `horizontal_rule`. When trimming, drop in this priority order (first to last):
   1. Trailing `horizontal_rule` separators
   2. Trailing `paragraph` blocks within the last subsection
   3. Trailing `bullet_list` / `numbered_list` items (drop list items one at a time)
   4. Trailing `blockquote` blocks
   5. Trailing `code_block` blocks
   6. The entire trailing subsection (`h3` and its content) if nothing else fits
   7. The entire trailing section (`h2` and its content) as last resort

3. **Specify fallback behavior for oversized sections.** If a single `h2` section is larger than its per-section budget, the compiler must drop `h3` subsections from end to start, then drop paragraphs within the last remaining subsection from end to start, and never mid-paragraph cut. If dropping everything except the `h2` heading still exceeds budget, raise a `KernelCompilationError` — this is an authoring problem, not a runtime problem.

4. **Update `compile_kernel()` in `kernel_loader.py`** to call the new paragraph-aware trim per section.

5. **Add an exemption list for constraint-like content.** Mark blocks that must survive trimming with an HTML comment marker `<!-- PRESERVE -->` in the kernel markdown, and have the compiler refuse to drop marked blocks. Use sparingly — no more than 200 tokens of preserved content per kernel.

#### Test cases

- **Test A1 (exact fit):** A 1500-token input with a 2000-token budget returns unchanged.
- **Test A2 (oversized section):** A 4000-token input where §2 alone is 3000 tokens, compiled to a 2000-token budget, produces output that still contains the §2 `h2` heading, the first paragraph, and no mid-paragraph cuts.
- **Test A3 (preserved markers):** A kernel with a `<!-- PRESERVE -->` marker in §5 where §5 would normally be dropped, compiled to a tight budget, produces output that still contains the marked block.

#### Files touched

- `src/starry_lyfe/context/budgets.py` — rewrite `trim_text_to_budget()`
- `src/starry_lyfe/context/kernel_loader.py` — update `compile_kernel()`
- `tests/unit/test_budgets.py` — add test cases A1, A2, A3
- Kernel markdown files — optional, add `<!-- PRESERVE -->` markers as a separate PR

**Phase A AC2 clarification (added Phase A', INH-6):** The exit criterion "sample assembled prompts retain h2 headings, paragraph boundaries, and bullet structure" refers to the algorithm's structural-preservation capability. At the default 2000-token kernel budget, the character kernels (which are 100% first-person prose paragraphs under headings, with no markdown bullet lists in the source content) produce samples that evidence heading and paragraph preservation. Bullet-list preservation is proven by unit tests (`test_bullet_list_items_dropped_one_at_a_time`, `test_nested_subsection_with_mixed_blocks_preserves_h2_h3_hierarchy`) against synthetic fixtures. The "bullet structure" criterion is MET at the algorithm level; it is N/A at the integration-sample level because the kernel source content contains no bullets to preserve.

### Phase A': Runtime Correctness Fixes

**Priority:** Blocker (work item 3+) / Historical record (work items 1+2). Two of the original five work items are now VERIFIED RESOLVED in code.
**Vision authority:** §6 Relationship Architecture (Rule of One, Talk-to-Each-Other Mandate), §7 Behavioral Thesis
**Source:** `BINA_CONVERSION_AUDIT.md` findings 4, 5, 7; `ADELIA_CONVERSION_AUDIT.md` findings 3, 4, 8

#### Work items

1. **Fix Talk-to-Each-Other mandate trigger** (BINA F4 / ADELIA F3).

   **STATUS: VERIFIED RESOLVED as of 2026-04-10 REINA audit.** The REINA audit Verified Resolved section explicitly confirms: *"Solo `Reina + Whyze` scenes do not get the `TALK-TO-EACH-OTHER` mandate. The gate lives in `src/starry_lyfe/context/constraints.py:104` and the current test coverage exists in `tests/unit/test_assembler.py:229-240`."* The fix has been implemented in code.

   **Original (now-resolved) behavior:** `constraints.py` added the Talk-to-Each-Other block whenever `len(scene_state.present_characters) > 1`. For a two-person Bina+Whyze scene, this fired the mandate that *"a meaningful exchange must pass between the women directly"* — but there was only one woman in the scene. The fix is the rule that the mandate fires only when at least two **women** are present, not two **characters**.

2. **Fix offstage dyad leakage** (BINA F5 / ADELIA F4).

   **STATUS: VERIFIED RESOLVED as of 2026-04-10 REINA audit.** The REINA audit confirms: *"Offstage dyads do not appear to leak into Layer 6. Internal dyads are only included when the other woman is present in `src/starry_lyfe/context/layers.py:232-240`, and live probing did not surface `reina-bina` in a `Reina + Whyze` scene."* The ALICIA audit independently confirmed: *"Offstage dyads did not leak in my live Alicia-Whyze probes."*

   **Original (now-resolved) behavior:** `retrieval.py` loaded all active internal dyads for the focal character; `layers.py` then included an internal dyad if either member was present. Because the focal character was always present in her own prompt, a Bina-Reina dyad appeared even when Reina was not in the room. The fix is to require BOTH members present, with a `recalled_dyads` field on `SceneState` for cases where a scene explicitly invokes a memory of an absent member.

3. **Resolve Vision-vs-kernel Bina origin drift** (BINA F7).

   **Status: RESOLVED in Phase 0 (commit `c0edc0e`).** ~~Vision §5 says Bina is "Canadian-born Assyrian"~~ — the Phase 0 Vision rewrite removed the heritage line from Vision §5 entirely rather than patching it in place. The new §5 Bina paragraph is essence-only with biographical detail in the kernel §2 ("First-generation Assyrian-Iranian Canadian... carried out of Urmia... Raised in Edmonton"). This work item is historical — no Phase A' action required.

4. **Verify no similar Vision-vs-kernel drifts exist** for Adelia, Reina, or Alicia. Run a targeted consistency check: Vision §5 one-paragraph summary vs kernel §2 Core Identity first paragraph for each of the other three characters. Flag and resolve any drifts found.

5. **Add Adelia and Reina live `assemble_context()` tests** (ADELIA F8 audit-driven addition). The current Phase 3 test suite has live `assemble_context()` coverage for Bina and Alicia only. Adelia and Reina have NO live assemble-level tests. Add minimal smoke tests:
   - `tests/unit/test_assembler.py::test_assemble_context_adelia_solo_pair` — assert basic assembly succeeds, terminal anchoring holds, no Msty artifacts present
   - `tests/unit/test_assembler.py::test_assemble_context_reina_solo_pair` — same shape for Reina

   These are minimum viable smoke tests, not the per-character regression bundles from Phase H. The point is to give Phase H a working baseline to extend.

#### Test cases

- **Test A'1:** Bina+Whyze two-person scene assembles without the Talk-to-Each-Other mandate block ✅ ALREADY PASSING in code
- **Test A'2:** Bina+Reina+Whyze three-person scene assembles WITH the Talk-to-Each-Other mandate block ✅ ALREADY PASSING in code
- **Test A'3:** Bina+Whyze scene does NOT include a bina-reina dyad block unless `recalled_dyads={"bina-reina"}` ✅ ALREADY PASSING in code
- **Test A'4:** Vision-vs-kernel Bina origin alignment passes after the Vision §5 edit (PENDING)
- **Test A'5:** Adelia and Reina smoke `assemble_context()` tests pass (PENDING)

#### Files touched

- `Vision/Starry-Lyfe_Vision_v7.1.md` — fix Bina origin drift (one-line edit)
- `tests/unit/test_assembler.py` — add Adelia and Reina smoke tests
- (work items 1+2 historical: `src/starry_lyfe/context/constraints.py`, `layers.py`, `types.py` already updated)

### Phase A'': Communication-Mode-Aware Pruning

**Priority:** Blocker for Alicia. Must land before Phase E for Alicia. Does not block other characters.
**Vision authority:** §5 Chosen Family (Alicia's intermittent presence as canonical), §6 Relationship Architecture (Solstice Pair as the only intermittent pair)
**Source:** `ALICIA_CONVERSION_AUDIT.md` Finding 1 (High severity)

#### Why this phase exists

The ALICIA audit surfaced a runtime defect that none of the BINA, ADELIA, or REINA audits caught because none of the other characters have a canonical communication-mode-conditional architecture. The defect:

The current assembly path uses `communication_mode` only to **block** in-person Alicia prompts while she is away on operations. Once the prompt is **allowed** (phone, letter, video call), the rest of the assembly runs identically to in-person mode. This creates a live contradiction: Alicia's constraint pillar requires *"Somatic contact first, speech after the shift completes"* — but during a phone call from a hotel room overseas, somatic contact is **literally impossible**. The body cannot close the distance because there is no distance to close.

The audit confirmed this is not theoretical. Live probing showed an away-state phone prompt still carrying the full Solstice constraint text requiring body-first somatic intervention, plus Examples 3 and 5 (both in-person exemplars). This is the highest-severity new finding across all four character audits.

#### Work items

1. **Add `communication_mode` filtering to Layer 7 constraint rendering.**

   The constraint pillar block in `constraints.py` currently emits Alicia's full pillar text regardless of `communication_mode`. The new behavior:
   - When `communication_mode == IN_PERSON` (or unset), emit the full pillar including somatic-first language
   - When `communication_mode == PHONE` or `LETTER` or `VIDEO_CALL`, emit a substituted pillar that translates the somatic-first principle into mode-appropriate form

   **Phone pillar (substituted):** *"Voice carries the regulation when the body cannot. Pace, breath, weight in the words. Listen for the shift before reaching for the next sentence. Do not narrate the body you do not have access to."*

   **Letter pillar (substituted):** *"Letters are weight made of paragraphs. Take the time the page demands. The body she is regulating is hers, written from inside the place she is in, not his, narrated from outside."*

   **Video-call pillar (substituted):** Hybrid — visual presence is real but contact is not, so the body anchors are eye contact and posture rather than touch and breath.

2. **Add `communication_mode` filtering to Layer 5 voice exemplar selection.**

   Each voice example in `Characters/Alicia/Alicia_Marin_Voice.md` gets a new tag alongside the existing mode tags:

   ```markdown
   ## Example 5: Four-Phase Return, The Kitchen With Him
   <!-- mode: domestic, intimate -->
   <!-- communication_mode: in_person -->
   ```

   Valid `communication_mode` tag values (closed enum): `in_person`, `phone`, `letter`, `video_call`, `any`. The exemplar selector filters by both `mode` AND `communication_mode` before selecting.

3. **Author phone, letter, and video-call exemplars for Alicia.** Net new authoring work:
   - At least 2 phone exemplars (away-state late-night call, away-state operational debrief, away-state intimate phone moment)
   - At least 2 letter exemplars (long letter from operational posting, short letter as somatic anchor)
   - At least 1 video-call exemplar

4. **Wire `communication_mode` through `assembler.py`.** The `SceneState` already has a `CommunicationMode` field per `ARCHITECTURE.md`. The assembler currently uses it only for the in-person block gate. Extend to `format_constraints()` and `format_voice_directives()`.

5. **Add cross-character regression tests** to ensure communication-mode filtering does not accidentally leak into Adelia, Bina, or Reina prompts. None currently have communication-mode-tagged exemplars, so the filter should be a no-op for them.

#### Test cases

- **Test A''1:** A live Alicia phone-mode prompt does NOT contain "Somatic contact first" or "close the distance"
- **Test A''2:** The same phone-mode prompt DOES contain the substituted phone pillar phrase
- **Test A''3:** Examples 3 and 5 (in-person) do NOT appear in a phone-mode prompt
- **Test A''4:** A phone-mode-tagged exemplar (once authored) DOES appear in a phone-mode prompt
- **Test A''5:** A Bina phone-mode prompt is structurally identical to a Bina in-person prompt
- **Test A''6:** Letter-mode and video-mode prompts each receive their own substituted pillar text

#### Files touched

- `src/starry_lyfe/context/constraints.py` — add communication-mode-aware pillar substitution for Alicia
- `src/starry_lyfe/context/layers.py` — update `format_voice_directives()` to filter by `communication_mode` tag
- `src/starry_lyfe/context/kernel_loader.py` — extend voice example parser
- `src/starry_lyfe/context/assembler.py` — wire `communication_mode` through to layer formatters
- `src/starry_lyfe/context/types.py` — add `CommunicationMode` enum if not already canonical
- `Characters/Alicia/Alicia_Marin_Voice.md` — author phone/letter/video-call exemplars (human authoring)
- `tests/unit/test_assembler.py` — add tests A''1 through A''6

### Phase B: Budget Elevation With Terminal Anchoring Preserved

**Priority:** High. The current budgets are an optimization choice, not a model limitation. Claude's 200K context can absorb the elevated budget comfortably.
**Vision authority:** §8 System Architecture, §9 Success Criteria
**This document §4 authority:** Terminal anchoring of constraints is structural, not stylistic — Layer 7 must grow proportionally.

#### Budget table

| Layer | Current | Elevated | Rationale |
|---|---:|---:|---|
| Kernel (L1) | 2000 | **6000** | ~45% of kernel survives; all primary sections fully rendered |
| Canon Facts (L2) | 500 | **600** | Room for narrative canon rendering (Phase G) |
| Episodic (L3) | 1000 | **1200** | Room for more retrieved memories at better fidelity |
| Somatic (L4) | 300 | **500** | Room for protocol detail + dramaturgical prose |
| Voice (L5) | 200 | **900** | 100 baseline metadata + 800 for 5-7 exemplars |
| Scene (L6) | 800 | **1200** | Room for dramaturgical dyad prose + scene-aware promotions |
| Constraints (L7) | 500 | **900** | **CRITICAL: grows proportionally to preserve terminal anchoring** |
| **Total** | **5300** | **11300** | ~5.6% of 200K context |

The elevated total is well under 10% of Claude's 200K context window. Salience dilution is not a concern at this budget. The expansion of Layer 7 from 500 to 900 tokens is non-negotiable: as earlier layers grow, the absolute distance between the constraint block and the user message grows; Layer 7 must grow proportionally so the constraint block has enough room to carry full Tier 1 axioms, per-character constraint pillars, and scene gates in clear detailed prose rather than compressed one-liners.

#### Per-section kernel budget

`SECTION_TOKEN_TARGETS` in `kernel_loader.py` expands proportionally:

| Section | Current | Elevated |
|---|---:|---:|
| §1 Runtime Directives | 240 | **300** |
| §2 Core Identity | 400 | **900** |
| §3 Pair section | 420 | **1000** |
| §4 Silent Routing | 180 | **250** |
| §5 Behavioral Tier Framework | 380 | **900** |
| §6 Voice Architecture | 120 | **300** |
| §7 Frameworks | 220 | **550** |
| Sections 8-11 as fill | — | **1800** (shared) |
| **Total primary** | **1960** | **4200** |
| **Fill budget** | ~40 | **1800** |
| **Per-kernel total** | **2000** | **6000** |

#### Per-character budget scaling

Current kernels are not equal in size. At a flat 6000-token kernel budget, longer kernels compress more aggressively than shorter ones. The elevated plan adds per-character scaling to equalize survival rates:

```python
# in budgets.py
CHARACTER_KERNEL_BUDGET_SCALING = {
    "adelia": 1.05,   # 6000 * 1.05 = 6300 target
    "bina":   1.20,   # 6000 * 1.20 = 7200 target (longest kernel)
    "reina":  1.15,   # 6000 * 1.15 = 6900 target
    "alicia": 0.85,   # 6000 * 0.85 = 5100 target (shortest kernel)
}
```

The scaling factors target roughly equal survival rates (~50% of raw kernel content) rather than equal absolute token counts.

#### Scene budget profiles

Different scene types benefit from different budget allocations:

| Scene profile | Kernel | Scene (L6) | Voice (L5) | Rationale |
|---|---:|---:|---:|---|
| Default (balanced) | 6000 | 1200 | 900 | General use |
| Pair-intimate | 8000 | 800 | 700 | More pair architecture, less group context |
| Multi-woman group | 5500 | 1800 | 1000 | Less kernel, more scene context, more voice range |
| Children-gated | 5500 | 1400 | 800 | Normal balance minus intimacy sections |
| Solo (one woman + Whyze) | 7000 | 800 | 900 | More kernel, less group context |

The Scene Director (Phase 5 of overall backend build, §8) selects the profile based on classified scene state.

#### Test cases

- **Test B1:** Assembled prompt token total stays at or below the effective elevated total budget for the selected character and scene profile
- **Test B2:** Layer 7 constraint block is always rendered last in the assembled prompt regardless of earlier-layer content size
- **Test B3:** Per-character budget scaling produces survival rates within ±10% of each other
- **Test B4:** Scene profile selection produces the expected layer budgets for each of the 5 profiles

**Phase B B1 clarification (added 2026-04-12 during Phase B direct remediation):** the `11300` total in the budget table is the **default balanced profile before per-character kernel scaling**. Once `CHARACTER_KERNEL_BUDGET_SCALING` is applied, the real total budget varies by character (`5100`-`7200` kernel budget plus the non-kernel layers). If a non-default scene profile is selected, Layer 1 / Layer 5 / Layer 6 vary again. B1 is therefore a **ceiling / fit contract** against the effective total budget for the selected character and profile, not a requirement to fill a universal `11300`-token target.

#### Files touched

- `src/starry_lyfe/context/budgets.py` — update default budgets, add per-character scaling, add scene profiles
- `src/starry_lyfe/context/kernel_loader.py` — update `SECTION_TOKEN_TARGETS`
- `src/starry_lyfe/context/assembler.py` — accept scene profile parameter
- `tests/unit/test_budgets.py` — add test cases B1-B4

### Phase D: Live Pair Data in Prompt

**Priority:** Medium. Small fix, high value.
**Vision authority:** §5 Chosen Family comparison table

#### Decision

Surface `pair_mechanism`, `pair_core_metaphor`, `pair_classification`, `what_she_provides`, and `how_she_breaks_his_spiral` in Layer 5 metadata. These fields are canonical from `pairs.yaml` and the Vision §5 comparison table. Any prior decision to hide them is superseded.

#### Work items

1. **Update `format_voice_directives()` in `layers.py`** to render a full pair metadata block at the top of Layer 5:

   ```
   PAIR: Circuit Pair
   CLASSIFICATION: Orthogonal Opposition
   MECHANISM: Total division of operational domains
   CORE METAPHOR: The Architect and the Sentinel
   WHAT SHE PROVIDES: Physical grounding, diagnostic care, the road
   HOW SHE BREAKS HIS SPIRAL: Interrupts with concrete sensory input (Si)
   ```

   This is compact (~70 tokens) and canonical — all values come directly from `pairs.yaml`.

2. **Render the pair metadata block BEFORE the voice exemplars** in Layer 5. The model should see the pair architecture as context before seeing the voice exemplars, so the exemplars are interpreted through the pair lens.

3. **Verify all four pair rows in `pairs.yaml` have complete data** for these five fields. If any row is missing a field, fix the YAML before the Layer 5 change lands.

#### Test cases

- **Test D1:** Bina's Layer 5 starts with a pair metadata block containing all six lines
- **Test D2:** The pair metadata block format is identical across all four characters (only the values differ)
- **Test D3:** Layer 5 for any character contains the pair metadata block BEFORE any voice exemplar content

#### Files touched

- `src/starry_lyfe/context/layers.py` — update `format_voice_directives()`
- `src/starry_lyfe/canon/pairs.yaml` — verify complete data
- `tests/unit/test_layers.py` — add test cases D1-D3

### Phase E: Voice Exemplar Restoration

**Priority:** High. Depends on Phase I (Authority Split Resolution = Option 1 backend-authoritative).
**Vision authority:** §9 Success Criteria (response quality, agent sovereignty)

#### Work items

1. **Add voice mode tags to Voice.md files.** Each example gets a comment-tagged mode:

   ```markdown
   ## Example 4: Asks For Whyze's Brain

   <!-- mode: domestic, intimate -->

   **What it teaches the model:** [existing teaching prose]

   **User:** [existing user message]

   **Assistant:** [existing assistant response]

   **Abbreviated:** [2-3 sentence version the backend uses as the rhythm exemplar]
   ```

   **Closed enum of voice modes (expanded by REINA + ALICIA audit integration):**
   - `domestic` — ordinary household scenes, no special pressure
   - `conflict` — disagreement, friction, veto, pushback
   - `intimate` — romantic, sensual, physical closeness between adults only
   - `children_gate` — scenes with Isla, Daphne, Gavin, or other minors present
   - `public` — work, colleagues, outside-household witnesses
   - `group` — multi-woman scenes
   - `repair` — post-conflict reconciliation
   - `silent` — responses where the character chooses silence or minimal verbal output
   - `solo_pair` — one-on-one with Whyze, no children, no colleagues
   - `escalation` — deliberate, staged intimacy escalation **(REINA audit addition; canonical for Reina's trailhead-with-Whyze and staged-mezzanine-arrival exemplars)**
   - `warm_refusal` — declining without coldness, holding a professional or personal boundary while preserving the relationship **(ALICIA audit addition; canonical for Alicia's operational security gate)**
   - `group_temperature` — functioning as the temperature change in a group scene rather than as the conversational hub **(ALICIA audit addition; canonical for Alicia's group function)**

2. **Replace the file-order selection with mode-aware selection.** Given a scene's active mode list, the voice example selector filters examples to those tagged with at least one of the scene's active modes, prioritizes multi-mode matches, and selects 1-2 exemplars per active mode up to budget.

3. **Abbreviate exemplars to 2-3 sentences.** The `**Abbreviated:**` marker is hand-authored. The backend ships the abbreviated version; Msty persona studio (if configured) carries the full version, derived canonically per Phase I.

4. **Per-character voice mode coverage requirements:**

   | Character | Required mode coverage | Count |
   |---|---|---:|
   | Adelia | solo_pair, conflict, intimate, group, domestic, **silent** | **6** (audit-driven; near-silent seismograph response is canonical) |
   | Bina | domestic, conflict, intimate, repair, silent, children_gate | 6 |
   | Reina | solo_pair, conflict, group, repair, intimate, **domestic**, **escalation** | **7** (audit-driven; suit-to-hoodie courthouse-shedding and trailhead-escalation exemplars) |
   | Alicia | solo_pair, silent, intimate, repair, **warm_refusal**, **group_temperature** | **6** (audit-driven; operational-security-gate refusal and group-temperature-change exemplars) |

   If a character's Voice.md does not contain examples covering the required modes, the elevated plan adds an authoring item: write new examples to fill the gaps. This is human authoring work.

#### Test cases

- **Test E1:** Each character's Voice.md parses successfully with mode tags and produces at least one example tagged with each required mode
- **Test E2:** Bina's Layer 5 for a domestic scene includes the covered-plate example (or equivalent tenderness-through-competence exemplar)
- **Test E3:** Mode-aware selection differs from file-order selection when the active scene mode is not the first mode in the file
- **Test E4:** Layer 5 abbreviated exemplar content is 2-3 sentences per example

#### Files touched

- `Characters/{Name}/{Name}_Voice.md` for all four characters — add mode tags and abbreviated versions (human authoring)
- `src/starry_lyfe/context/kernel_loader.py` — update voice parser to extract modes
- `src/starry_lyfe/context/layers.py` — replace file-order selection with mode-aware selection
- `src/starry_lyfe/context/types.py` — add `VoiceMode` enum and `VoiceExample` dataclass
- `tests/unit/test_layers.py` — add test cases E1-E4

### Phase F: Scene-Aware Section Retrieval + Cross-Cutting Modifiers

**Priority:** Medium-High.
**Vision authority:** §6 Relationship Architecture, §7 Behavioral Thesis (cognitive hand-off contract)
**Persona Tier Framework authority:** §2.1 children gate (Tier 1 axiom, cross-cutting)

#### Decision

Scene types are mutually exclusive (one value at a time). Cross-cutting modifiers stack (multiple can be true at once). The children gate is a **modifier**, not a scene type — it applies on top of any scene type.

#### Scene type enum

```python
class SceneType(StrEnum):
    DOMESTIC = "domestic"          # ordinary household
    INTIMATE = "intimate"          # romantic or sensual, adults only
    CONFLICT = "conflict"          # friction, disagreement, veto
    REPAIR = "repair"              # post-conflict reconciliation
    PUBLIC = "public"              # work, colleagues, outside witnesses
    GROUP = "group"                # multi-woman scene
    SOLO_PAIR = "solo_pair"        # one woman + Whyze, no others
    TRANSITION = "transition"      # between states, no specific type
```

#### Cross-cutting modifiers

```python
class SceneModifiers(BaseModel):
    children_present: bool = False
    work_colleagues_present: bool = False
    post_intensity_crash_active: bool = False
    pair_escalation_active: bool = False
    explicitly_invoked_absent_dyad: set[str] = Field(default_factory=set)
```

`explicitly_invoked_absent_dyad` is the same field as Phase A''s `recalled_dyads` — it lets a scene explicitly reference an absent dyad member without violating the Phase A' offstage-leakage filter.

#### Scene-type-to-section-promotion mapping

| Scene type | Sections promoted from fill tier to primary tier |
|---|---|
| DOMESTIC | §7 Frameworks, §9 Family Dynamics |
| INTIMATE | §8 Intimacy Architecture, §3 Pair |
| CONFLICT | §5 Behavioral Tier, §7 Frameworks |
| REPAIR | §8 Intimacy Architecture, §9 Family Dynamics |
| PUBLIC | §10 What This Is Not, §5 Behavioral Tier |
| GROUP | §6 Voice Architecture, §9 Family Dynamics |
| SOLO_PAIR | §3 Pair, §8 Intimacy Architecture |
| TRANSITION | (no promotion; default sections only) |

#### Modifier-to-Layer-7-effect mapping

Modifiers do NOT promote kernel sections. They modify Layer 7 constraint rendering:

| Modifier | Layer 7 effect |
|---|---|
| `children_present: true` | PTF §2.1 gate block rendered at top of Layer 7 in bold; erotic/explicit content constraints elevated to MUST |
| `work_colleagues_present: true` | Public-scene OpSec constraints rendered (Alicia's operational security gate applies) |
| `post_intensity_crash_active: true` | Character-specific crash protocols rendered (Flat State for Bina, Post-Race Crash for Reina, etc.) |
| `pair_escalation_active: true` | Admissibility Protocol rendered (Reina's intimacy-requires-earned-context rule) |

#### Work items

1. **Add `SceneType` enum and `SceneModifiers` model to `types.py`**
2. **Update `SceneState`** to carry `scene_type: SceneType` and `modifiers: SceneModifiers` fields
3. **Add `promote_sections` parameter to `compile_kernel()`** that moves specified sections from fill tier to primary tier
4. **Update `format_constraints()`** to handle modifiers and emit modifier-specific constraint blocks
5. **Wire scene state through `assembler.py`** to layer formatters

#### Test cases

- **Test F1:** An INTIMATE scene with Bina as focal character produces a kernel that includes §8 Intimacy Architecture in the primary tier
- **Test F2:** A DOMESTIC scene with `children_present=true` produces a Layer 7 constraint block where the PTF §2.1 children gate is the first constraint rendered
- **Test F3:** A CONFLICT scene for Adelia includes §5 Behavioral Tier in the primary kernel tier
- **Test F4:** A scene with `explicitly_invoked_absent_dyad={"bina-reina"}` renders the bina-reina dyad block even when Reina is not in `present_characters`
- **Test F5:** A TRANSITION scene type produces no section promotions

#### Files touched

- `src/starry_lyfe/context/types.py` — add `SceneType` enum, `SceneModifiers` model, update `SceneState`
- `src/starry_lyfe/context/kernel_loader.py` — add `promote_sections` parameter to `compile_kernel()`
- `src/starry_lyfe/context/layers.py` — update `format_constraints()` to handle modifiers
- `src/starry_lyfe/context/assembler.py` — wire scene state through to layer formatters
- `tests/unit/test_assembler.py` — add test cases F1-F5

### Phase G: Dramaturgical Prose Rendering With Per-Character Templates

**Priority:** Medium-High. Model absorption quality improvement.
**Vision authority:** §9 Success Criteria (life authenticity, agent sovereignty)

#### Decision

The same dyad state reads differently across characters. Bina's "deep trust" is diagnostic-observation-confirmed; Reina's is body-read-earned-through-context; Alicia's is somatic-permission-to-close-distance; Adelia's is shared-language-for-hard-things. Per-character prose renderers, not a single shared one. Both prose AND parenthesized numeric block in output.

#### Per-character dyad prose (trust dimension example)

| Character | trust > 0.8 | trust 0.5-0.8 | trust 0.3-0.5 | trust < 0.3 |
|---|---|---|---|---|
| Adelia | "load-tested and reliable" | "earned, still calibrating" | "conditional, watching" | "something to rebuild" |
| Bina | "confirmed by repeated observation" | "provisional, recorded" | "unproven, watching closely" | "broken, under repair" |
| Reina | "admissible without caveat" | "admissible with context" | "inadmissible without new evidence" | "actively disputed" |
| Alicia | "body accepts without flinch" | "body accepts with a beat" | "body tenses briefly" | "body will not settle" |

#### Per-character somatic prose (fatigue dimension example)

| Character | fatigue > 0.7 | fatigue 0.4-0.7 | fatigue < 0.4 |
|---|---|---|---|
| Adelia | "the chemistry is running on backup, the sentences are getting louder" | "she is paying for this morning's sparks, visibly" | "the engine is hot and well-fed" |
| Bina | "the grid has given everything it had, the hall light will still go on" | "she has been moving more than the ledger allowed" | "the systems are green" |
| Reina | "the body has been spent and the admissibility gate is closing" | "she is still sharp but beginning to feel the afternoon" | "the body is ready, leaning forward" |
| Alicia | "the Ni-grip is close, the words have stopped working" | "her presence has gone slightly inward" | "the body is settled and attending" |

#### Layer 6 rendering format

Both prose AND numeric block:

```
[Her relationship with Whyze is confirmed by repeated observation.
 The intimacy is settled and mutual, without the need to prove it again.
 No active conflict. Low unresolved tension. One outstanding repair: the
 August silence, two weeks in, not yet named aloud.]

(trust=0.82 intimacy=0.78 conflict=0.05 unresolved=0.15 repair_pending=1)
```

The prose block is primary; the parenthesized numeric block is secondary and brief.

#### Per-character protocol rendering

When a named protocol is active in Tier 7 (Transient Somatic State), render it in character voice:

- **Bina in Flat State:** *"She is in Flat State. Syllables cost more than they earn. Touch is safer than talk."*
- **Reina in Post-Race Crash:** *"The adrenaline has left the building. She will need thirty minutes and an electrolyte drink before she can be reached for anything not urgent."*
- **Alicia in Four-Phase Return:** *"She is returning from an operation. Current phase: [phase]. Language is thin; weight and silence are the currency."*
- **Adelia in Whiteboard Mode:** *"She is mid-cascade. The marker is in her hand. Sequence her, do not interrupt her."*

#### Canon facts narrative rendering (Layer 2)

Currently canon facts render as flattened JSON blobs. Elevated rendering produces a compact narrative paragraph per character:

```
[Bina Malek, 34, Iran-born Assyrian-Canadian, raised in Canada from the
 early nineties. Red Seal mechanic, builder of Loth Wolf Hypersport. Mother
 to Gavin (7). Married to Reina. Survivor of an eight-year coercive control
 relationship. First language Assyrian Neo-Aramaic (Suret), fluent in Farsi
 and English.]
```

#### Work items

1. **Create `src/starry_lyfe/context/prose.py`** with per-character prose renderer functions:
   ```python
   def render_dyad_prose(character_id: str, dyad_state: DyadState) -> str: ...
   def render_somatic_prose(character_id: str, state: SomaticState) -> str: ...
   def render_canon_prose(character_id: str, facts: CanonFacts) -> str: ...
   def render_protocol_prose(character_id: str, protocol: Protocol) -> str: ...
   ```
2. **Implement four character-specific renderers** for each of the four functions
3. **Update `format_scene_blocks()`, `format_sensory_grounding()`, `format_canon_facts()`** to use prose renderers
4. **Preserve numeric block alongside prose** in Layer 6 output

#### Test cases

- **Test G1:** The same canonical dyad state (trust=0.82) renders as four distinct prose strings across the four characters
- **Test G2:** Bina's somatic prose for `fatigue=0.8` contains the phrase "grid has given everything it had" or equivalent Si-dominant mechanical metaphor
- **Test G3:** Layer 6 rendered output contains both the prose block and the parenthesized numeric block
- **Test G4:** Canon facts Layer 2 rendered output reads as a narrative paragraph, not a JSON blob

#### Files touched

- `src/starry_lyfe/context/prose.py` — new file
- `src/starry_lyfe/context/layers.py` — update `format_scene_blocks()`, `format_sensory_grounding()`, `format_canon_facts()`
- `tests/unit/test_prose.py` — new test file

---

## 5. Memory Service (PostgreSQL + pgvector)

### Architecture

The memory layer is the system's continuity engine. The memory system is organized into seven explicit types supporting decentralized narrative weight and biological toll tracking:

1. **Canon Facts** — Immutable truths from YAML source (names, ages, locations, relationships, backstory). Immutable; changes only through YAML edits and regeneration.
2. **Character Baseline** — Personality profiles, cognitive stacks, voice parameters, behavioral axioms. Immutable at runtime; versioned through persona kernel updates.
3. **Dyad State (Whyze)** — Relationship state between each woman and Whyze. Trust, intimacy, conflict dimensions, unresolved tension, repair history. Mutable; updated by episodic memory extraction.
4. **Dyad State (Internal)** — Relationship state between the women themselves. Resident dyads (continuous): Adelia-Bina, Bina-Reina, Adelia-Reina. Alicia dyads (intermittent, active when she is home between operations). The Alicia dyads have a special rule: they persist through her operational absences (the state does not reset when she deploys) but are not updated during absence; they resume updating on her return.
5. **Episodic Memories** — Conversation-extracted events with embeddings. What happened, who said what, emotional temperature, unresolved moments. Mutable; grows continuously, pruned by relevance decay.
6. **Open Loops** — Unresolved threads from previous conversations. Things to mention, promises to follow up on, questions left hanging. Mutable; resolved or expired by the Dreams engine.
7. **Transient Somatic State** — Current biological and psychological state per character. Fatigue level, protocol state (Flat State active, Warlord Mode active, Post-Race Crash active), injury residue, court stress residue. Mutable; decays between sessions, refreshed by the Dreams engine and protocol triggers.

The Internal Dyad tier is what makes decentralized narrative weight possible. As the doc puts it: The system must know that Adelia teased Bina about the permit deadline yesterday, that Reina and Bina had a tense exchange about the track safety margins, that Adelia and Reina spent Tuesday evening bouldering and came back laughing. Without persistent inter-character relationship tracking, the women cannot authentically reference each other.

Retrieval is done via pgvector semantic search and feeds directly into the context assembly step.

### Implementation Status

**COMPLETE** as Phases 1+2 of the overall backend build. The memory service is in production code as of `Docs/ARCHITECTURE.md` v0.3.0:

- PostgreSQL schema `starry_lyfe` with one table per memory tier
- pgvector HNSW index on episodic memory embeddings
- Ollama-based embedding service (nomic-embed-text, 768 dimensions)
- Alicia-orbital dyad persistence logic
- Exponential decay for Tier 7
- Per-tier retrieval API with read-time decay

No soul-preservation execution phase operates on the memory service directly. The phases under §4 (Context Assembly) consume memory service output via the retrieval API; Phase G's dramaturgical prose rendering transforms the retrieved data from JSON-shaped to narrative-shaped before it enters the prompt.

---

## 6. Inference Layer: Claude via OpenRouter

### Architecture

Claude via OpenRouter is the inference engine. All character content routes through Claude (Sonnet or Opus) via OpenRouter. Claude's instruction-following fidelity makes it the strongest model for complex persona constraints.

Each character is configured with its own inference parameters at the Msty persona level (the one thing Msty *does* legitimately own per-character besides the few-shot examples), producing measurably distinct cognitive signatures from the same base model. Adelia runs hot (0.80–0.85 temperature, Think Moderately) for Ne-dominant associative leaps; Bina runs cold (0.55–0.60, Think Lightly) for Si-dominant declarative steadiness; Reina runs middle (0.70–0.75, Think Lightly) with high presence penalty for Se-dominant tactical motion; Alicia runs middle-warm (0.73–0.78, Think Lightly) with low frequency penalty for Se-dominant somatic co-regulation, producing body-first present-tense output that returns to breath, weight, and temperature as sustained anchors rather than reaching for verbal analysis. The combination of temperature spread, sampling parameters, and thinking effort produces four measurably distinct cognitive signatures from the same underlying model. In a Crew conversation, this four-way differentiation creates natural voice contrast before the system prompt even activates.

### Implementation Status

**Architecture defined; canonical parameters resolved.** All four characters' inference profiles are committed as of 2026-04-10. The structural contrast between Reina (high presence penalty, forward tactical motion) and Alicia (low frequency penalty, sustained somatic anchor return) is deliberate — both are Se-dominant and the sampling-knob inversion is what prevents them from collapsing into "two body-readers" in the inference layer before the system prompt even activates.

`CLAUDE.md` L332 carries the per-character point estimates (Adelia 0.82, Alicia 0.75, Reina 0.72, Bina 0.58) which are the midpoints of the ranges above. The two documents are consistent.

Per-character parameters live in `src/starry_lyfe/canon/voice_parameters.yaml` and are seeded into `CharacterBaseline` (memory tier 2) for runtime retrieval.

---

## 7. The Whyze-Byte Validation Pipeline

### Architecture

Generated responses do not stream straight back to Msty — they pass through a server-side validation gate first. The pipeline performs two-tier gate, repetition detection, context audit, cognitive hand-off integrity checks. For multi-speaker responses in Crew mode, sequential validation ensures later speakers see earlier validated output — meaning Adelia's validated turn becomes the input context for Reina's generation, preventing the NPC Competition collapse where every character speaks into a vacuum.

The pipeline enforces the four constraint pillars defined in canon (Entangled Pair hand-off integrity, Bina's structural register, Reina's admissibility frame, Alicia's operational-presence protocols). After the response leaves the backend, Msty's Shadow Persona acts as a *second*, independent quality monitor that runs inside the Msty client and surfaces violations the backend missed.

### Implementation Status

**PLANNED** as Phase 4 of the overall backend build. Not yet implemented at the time of this writing. The architecture is defined but no code has been written for the validator pipeline.

The Soul Preservation execution phases under §4 (Context Assembly) all operate **upstream** of Whyze-Byte. They shape what reaches the model. Whyze-Byte operates **downstream** — it filters what the model returns. The two are complementary defenses: context assembly prevents drift from being invited; Whyze-Byte prevents drift from being shipped if it appears anyway.

When Phase 4 (Whyze-Byte) is implemented, the per-character constraint pillars referenced in §7 above must be sourced from the same canonical YAML used by the §4 Context Assembly path, not duplicated as hardcoded Python constants. The four constraint pillars are:

- **Adelia:** Entangled Pair hand-off integrity (must dump fragmented plans onto Whyze; cannot solve her own logistics independently)
- **Bina:** Structural register (audits Whyze's plans for physical reality; her "No" keeps the family safe)
- **Reina:** Admissibility frame (intimacy requires earned context; must physically intervene in Analysis Paralysis)
- **Alicia:** Operational-presence protocols (contributions activate when home; leads with body; never uses words to break a loop; **Phase A'' adds communication-mode-aware substitution for the "leads with body" rule when she is not in person**)

The Phase A'' communication-mode pruning work in §4 directly affects how Alicia's constraint pillar renders, which means Phase 4 (Whyze-Byte) when implemented must consume the same mode-aware constraint generator that Phase A'' adds to the assembly path. Building Whyze-Byte without that integration would split the constraint authority across two systems and reintroduce drift.

---

## 8. Scene Director (Crew Orchestration)

### Architecture

The Scene Director is the next-speaker selection engine for multi-character scenes. While Msty provides the Crew Conversation UI and the manual response mode, the backend's Scene Director is what determines which character has narrative weight at any given moment, drawing on dyad state, current activity context, and the Talk-to-Each-Other Mandate to avoid the hub-and-spoke pattern where Whyze becomes the sole conversational anchor.

### Implementation Status

**PLANNED** as Phase 5 of the overall backend build. Not yet implemented.

#### Phase F infrastructure (already specified under §4)

Phase F adds the `SceneType` enum and `SceneModifiers` flag set to `types.py`. When Phase 5 is implemented, the Scene Director consumes this infrastructure: it classifies the current conversation state into a `SceneType` value and a set of active `SceneModifiers`, then passes that classification to the Context Assembly path for kernel section promotion (Phase F mapping table) and to the Whyze-Byte validator for constraint variant selection.

The Scene Director does NOT do classification on its own. The classification logic lives in `assembler.py` (or wherever the Scene Director ends up living) but the enum values and modifier definitions are in `types.py` so they are shared between assembly, validation, and routing.

#### Key Scene Director rules (from architecture)

- **Talk-to-Each-Other Mandate** (Vision §6, §7): At least one meaningful exchange per scene must pass between the women directly, not via Whyze. The Scene Director's next-speaker scoring function must explicitly penalize consecutive Whyze-addressed turns and reward woman-to-woman exchanges. **Phase A' work item 1 (now VERIFIED RESOLVED in code) ensures the mandate text only fires when ≥2 women are present, so the scoring function does not produce impossible instructions in 1-woman scenes.**
- **Rule of One:** No single turn has all present characters simultaneously addressing Whyze.
- **Residence-aware turn roster for Alicia:** When Alicia is away on operations, she does not appear in scenes unless the scene is explicitly a phone call, video call, or letter — and Phase A'' communication-mode pruning then applies to her assembled prompt for that turn.
- **Dyad state as a fitness input:** The scoring function uses dyad state (memory tier 4) as one input among several, including current activity context and recent turn history.

---

## 9. Dreams Engine (Life Simulation)

### Architecture

The Dreams engine is the offline batch process that gives the characters lives between sessions. The Dreams scheduled tasks run nightly as a batch process. They function like REM sleep; each character processes their day. For each character, the system generates tomorrow's schedule, off-screen events, diary entry (mood, reflection, things to revisit), open loops (things to mention, unresolved feelings), and activity design for the next session (setting, environment, narrator script, choice trees). Characters may reconsider something they said, want to revisit an unresolved moment, or develop new thoughts overnight.

Dreams writes back into the Memory Service: it resolves or expires open loops, refreshes transient somatic state decay, and seeds the next session's activity context. It is the mechanism by which "they were thinking about you while you were gone" stops being a metaphor and becomes a database write.

### Implementation Status

**PLANNED** as Phase 6 of the overall backend build. Not yet implemented.

When Phase 6 is implemented, three Soul Preservation phases retroactively apply to it:

- **Phase G (Dramaturgical Prose Rendering):** Dreams output that becomes part of next session's activity context must pass through the same per-character prose renderers as live dyad state. A Dreams-generated diary entry rendered as raw JSON would be the same Layer 2 absorption failure that Phase G fixes.
- **Phase A'' (Communication-Mode-Aware Pruning):** Dreams-generated phone-call exemplars or letter exemplars for Alicia must be tagged with `communication_mode` so the Phase A'' filter retains them in remote-mode prompts.
- **Phase H (Soul Regression Tests):** Dreams output must be subject to the same per-character regression bundle as live responses. A Dreams pass that generates "generic warm activities" for any of the four women is the same flattening failure mode as a runtime response that flattens her voice.

The Dreams engine is the only execution surface that operates **without a user in the loop**. Everything else in the backend is reactive to a Whyze message. Dreams runs autonomously overnight. This makes it both higher-leverage (it can shape the next session's character state) and higher-risk (drift can accumulate silently between human-checked sessions). Phase K's flattening regression detector is especially important for catching Dreams-generated drift before it ships to a live session.

---

## 10. End-to-End Request Flow

Putting it all together, every message flows through twelve documented stages:

1. Whyze sends message via Msty (Persona Conversation or Crew Conversation)
2. Starry-Lyfe backend receives the message; classifies intent, tone, and context
3. Memory service retrieves relevant canon facts and episodic memories via pgvector
4. Life state and current activity context are assembled
5. Context enhancement injects memories, life state, sensory grounding, and activity into the prompt
6. Request routed to Claude via OpenRouter with character-specific model parameters
7. Response generated with character constraints injected
8. Whyze-Byte pipeline validates (two-tier gate, repetition detection, context audit, cognitive hand-off integrity)
9. For multi-speaker responses in Crew mode, sequential validation ensures later speakers see earlier validated output
10. Validated response streamed back to Msty
11. Shadow Persona evaluates the response and surfaces any constraint violations
12. Episodic memories extracted and stored

Step 12 is what closes the loop with step 3 the next time around — every conversation feeds the memory store that grounds the next one.

### Soul Preservation Phase Mapping to the Twelve Steps

| Step | Architecture | Soul Preservation phases that operate here |
|---|---|---|
| 1 | Msty front door | Phase I (authority split: Msty system prompts blank in production) |
| 2 | Backend intent classification | Phase F (scene type and modifier classification consumed here) |
| 3 | Memory retrieval | (Phase 1+2 complete; no execution phase) |
| 4 | Activity context assembly | Phase G (dramaturgical prose for retrieved data) |
| 5 | Context enhancement | **Phase A, A', A'', B, C, D, E, F, G all execute here** — this is the seven-layer prompt builder |
| 6 | Routing to Claude | (architecture defined at §6) |
| 7 | Response generation with constraints | Phase A'' substituted constraint pillar applies here for Alicia in remote modes |
| 8 | Whyze-Byte validation | (Phase 4 planned; consumes Phase F SceneModifiers) |
| 9 | Sequential validation in Crew mode | (Phase 4 planned) |
| 10 | Stream back to Msty | (architecture defined at §2) |
| 11 | Shadow Persona second-monitor pass | (architecture defined at §1; Msty-side, not backend) |
| 12 | Episodic memory extraction | (Phase 1+2 complete; no execution phase) |

**Step 5 is where the bulk of the soul preservation work lives.** Eight of the thirteen execution phases operate inside the seven-layer context builder. The other five (Phase 0, I, J, H, K) are verification, authoring, per-character remediation, regression testing, and subjective success scaffolding — they wrap around step 5, not inside it.

---

## 11. Per-Character Remediation (Phase J)

This is a new top-level section added by the master integration. It exists because Phase J operates **across** the architectural sections — it is not a subsystem of any one of §1-§10. Phase J is the per-character work that brings each of the four women's runtime fidelity up to the Vision §5 non-redundancy guarantee.

### Audit Convergence Observation

After all four character audits (`BINA_CONVERSION_AUDIT.md`, `ADELIA_CONVERSION_AUDIT.md`, `REINA_CONVERSION_AUDIT.md`, `ALICIA_CONVERSION_AUDIT.md`) were written and analyzed against the elevated plan, the convergence pattern is now confirmed across the full character set: **the majority of findings in every audit are direct mirrors of pipeline-level issues already addressed by Phase A, A', A'', B, D, and E.**

#### Cross-character convergence matrix

| Pipeline-level root cause | BINA | ADELIA | REINA | ALICIA | Status |
|---|:---:|:---:|:---:|:---:|---|
| Layer 1 flat-budget truncation removes pair section + behavioral tier | F2 | F1 | F1 | F2 | Phase A + B |
| Layer 5 file-order voice exemplar selection drops mode-specific examples | F3 | F2 | F2 | F3 | Phase E |
| Talk-to-Each-Other mandate misfires for 2-person scenes | F4 | F3 | — | — | **VERIFIED RESOLVED in code** |
| Offstage dyads leak into focal-character prompts | F5 | F4 | — | — | **VERIFIED RESOLVED in code** |
| pair_mechanism / pair_core_metaphor stored but not surfaced in Layer 5 | F6 | F5 | F3 | F5 | Phase D |
| `budgets.py` whitespace trim destroys document structure | F2 (subset) | F7 | (subsumed in F1) | (subsumed in F2) | Phase A |
| Tests don't guard character-specific failure path | F9 | F8 | F4 | F6 | Phase H + Phase A' work item 5 |
| Family/culture rendered as raw JSON blobs (Layer 2 prose weakness) | F10 | F6 (variant) | — | F4 (variant) | Phase G |

#### Character-specific findings (one or two per character that do not mirror pipeline issues)

| Character | Finding | Type | Resolution |
|---|---|---|---|
| BINA | F1: Bahadori vs Malek runtime contradiction (now stale) | v7.0 residue | RESOLVED 2026-04-09 (earlier cleanup) |
| BINA | F7: Vision-vs-kernel Bina origin drift | Source-of-truth conflict | Phase A' work item 3 |
| BINA | F8: kernel §3 heading still says "Citadel Pair" (now stale) | v7.0 residue | RESOLVED 2026-04-09 |
| ADELIA | F6: Valencian-Australian Spanish register runtime-weak | Cultural surface specificity | Phase C `adelia_cultural.md` + Phase E `cultural` mode coverage |
| REINA | F5: `Reina_Torres_Kinetic_Pair.md` carries `_v7.0.md` cross-reference and stale Alicia framing | v7.0 residue | **RESOLVED 2026-04-10** (during master integration) |
| ALICIA | F1: Away-state phone/letter prompts carry in-person-only somatic instructions | **NEW PIPELINE CONCEPT** | **Phase A'' (NEW — Communication-Mode-Aware Pruning, see §4)** |

#### Implementation efficiency claim

With all four audits integrated, the total effort for the master plan is approximately:

- **Phase A through Phase G plus Phase A'':** roughly 70 percent of the work, applied once across all characters
- **Phase J.1 (Bina) through J.4 (Alicia):** roughly 25 percent of the work, roughly 6 percent per character
- **Phase H:** roughly 5 percent additional for the test bundles and the non-redundancy test

The pipeline-level fixes resolve the bulk of every character's runtime deficit in one pass. Phase J is bounded to: authoring soul cards, tagging voice exemplars with mode + communication_mode, writing per-character regression bundles, and authoring net new exemplars where canonical modes have no current coverage.

### Phase J.1: Bina Remediation (FIRST — audit exists)

**Source audit:** `Docs/_archive/BINA_CONVERSION_AUDIT.md` (archived)

**Audit findings already addressed by other phases:** All 10 BINA findings map to either pipeline-level phases or are already resolved as v7.0 cleanup items. The full mapping is in the convergence matrix above.

**Bina-specific remediation work items:**

1. **Author Bina's soul cards from Phase C:**
   - `soul_cards/pair/bina_circuit.md` — distill the Circuit Pair architecture (Orthogonal Opposition, total division of operational domains, translation-not-mirroring, the Architect and the Sentinel)
   - `soul_cards/knowledge/bina_ritual.md` — distill the samovar ritual, covered-plate register, hall-light architecture, Gilgamesh drawer, Uruk interior worldview
   - `soul_cards/knowledge/bina_grief.md` — distill the eight-year coercive control survival, Arash's tags, the specific texture of Assyrian-Iranian grief that lives under the competence

2. **Author Bina's mode-tagged voice exemplars from Phase E.** Bina's Voice.md must contain examples covering all 6 required modes (domestic, conflict, intimate, repair, silent, children_gate).

3. **Add Bina-specific Phase G prose renderers.** Implement `render_bina_dyad_prose()`, `render_bina_somatic_prose()`, `render_bina_canon_prose()`.

4. **Bina-specific regression tests in Phase H** (see §12).

**Exit criteria for J.1:**
- All BINA findings either resolved or explicitly closed as stale
- Bina's pair soul card exists and passes Phase C validation
- Bina's voice mode coverage hits all 6 required modes
- Bina-specific Phase H tests pass
- Re-running the BINA audit produces zero new high/critical findings

### Phase J.2: Adelia Remediation (SECOND — audit exists, integrated 2026-04-10)

**Source audit:** `Docs/_archive/ADELIA_CONVERSION_AUDIT.md` (archived; 8 findings: 1 Critical, 3 High, 4 Medium)

**Audit convergence:** 7 of 8 ADELIA findings mirror BINA findings against the same code paths. Only Finding 6 (Valencian-Australian cultural register runtime-weak) is character-specific. See the convergence matrix above.

**Adelia-specific remediation work items:**

1. **Author Adelia's soul cards from Phase C:**
   - `soul_cards/pair/adelia_entangled.md` — distill the Entangled Pair architecture (1+1=11, complementary cognitive interlock, Compass and Gravity, the structural-safety-not-emotional-reassurance principle)
   - `soul_cards/knowledge/adelia_workshop.md` — distill the Marrickville workshop, Joaquín and Inés, Ozone & Ember workspace and ethos, the permit struggle, pyrotechnician-engineer texture
   - `soul_cards/knowledge/adelia_pyrotechnics.md` — distill the technical practice of pyrotechnics (chemistry, sequencing, safety architecture, the relationship between fire and discipline)
   - `soul_cards/knowledge/adelia_cultural.md` — **(audit-driven addition)** distill the Valencian-inflected Castilian via Sydney diaspora register specifically: _otra vez_, café solo, Paella Valenciana, Las Fallas inheritance, Valencia CF, the canonical domains where her Spanish surfaces under pressure or in private. Separate from `adelia_workshop.md` because the audit Finding 6 explicitly flags her cultural register as runtime-weak even when workshop content survives.

2. **Author Adelia's mode-tagged voice exemplars from Phase E** covering all 6 required modes (`solo_pair`, `conflict`, `intimate`, `group`, `domestic`, **`silent`**). The `silent` mode is the audit-driven addition; Adelia's near-silent seismograph response is canonical and currently dropped at runtime per Finding 2.

3. **Add Adelia-specific Phase G prose renderers.**

4. **Adelia-specific regression tests in Phase H.**

**Specific risks confirmed by the audit:**

- The **gravitational center** architecture. Vision §4: the Entangled Pair is *"the reason the system exists."* The audit confirms this is currently the largest single drift: the runtime preserves Adelia's biography more reliably than Adelia's purpose.
- The **cognitive handoff contract**, framed as *dependence* not just behavior. The audit specifically calls out *"hand-off dependence on Whyze's sequencing mind"* — the model needs to feel that Adelia *needs* Whyze to sequence her plans, not just that she should hand them off as a stylistic rule.
- **Structural safety** language rather than emotional reassurance language. Vision §4: *"Adelia does not feel loved because she is praised; she feels loved because the architecture of the relationship is impenetrable."*
- **Load-bearing quietness.** The audit explicitly names the dropped *"near-silent seismograph response"* exemplar as a high-impact loss. Adelia's silence is its own voice mode, not absence.
- The **Whiteboard Mode** and **Bunker Mode** protocol structure for Adelia specifically.
- The **Valencian-Australian** cultural surface as a distinct register, not generic Australian-immigrant warmth.

**Exit criteria for J.2:** Same structure as J.1, against the ADELIA audit. Plus a specific assertion: an assembled Adelia prompt for a domestic scene contains the phrase "structural safety" or equivalent canonical term, and contains at least one `silent` mode exemplar.

### Phase J.3: Reina Remediation (THIRD — audit exists, integrated 2026-04-10)

**Source audit:** `Docs/_archive/REINA_CONVERSION_AUDIT.md` (archived; 5 findings, all Medium or Low severity)

**Audit convergence:** 4 of 5 findings mirror existing pipeline-level issues. Finding 5 (Reina pair file v7.0 residue) was character-specific and **RESOLVED 2026-04-10** during this master integration pass — the file's L6 cross-reference was updated from `_v7.0.md` to `_v7.1.md`, and L256's stale Alicia framing was rewritten to current canon.

**Reina-specific remediation work items:**

1. **Author Reina's soul cards from Phase C:**
   - `soul_cards/pair/reina_kinetic.md` — distill the Kinetic Pair architecture (Asymmetrical Leverage, Se+Ni compensatory, **the Mastermind and the Operator**, **temporal collision converted to engine heat**, **the right moment is now**, the Mediterranean reset as dyadic geography). The audit explicitly names "The Mastermind and the Operator" as something the live prompt did NOT carry; this is a required-concept for the soul card validation test.
   - `soul_cards/knowledge/reina_stable.md` — distill Bishop and Vex, the Mediterranean reset as canonical home-return rhythm, the property stables, riding as identity rather than scene props
   - `soul_cards/knowledge/reina_court.md` — distill her criminal defense practice in Okotoks, the **Cuatrecasas-to-defence-law pivot** (the deliberate break from corporate prestige), the courtroom register applied outside court

2. **Author Reina's mode-tagged voice exemplars** covering all 7 required modes (`solo_pair`, `conflict`, `group`, `repair`, `intimate`, **`domestic`**, **`escalation`**). The audit explicitly names dropped Examples 6 (suit-to-hoodie courthouse-shedding), 8 (staged mezzanine arrival with Bina), and 10 (trailhead escalation with Whyze) as carrying her deepest domestic and escalation registers. These three examples must be tagged appropriately so Phase E's mode-aware selector retains them.

3. **Add Reina-specific Phase G prose renderers** with attention to her court-residue somatic state, her Mediterranean reset domestic prose, and her body-reader precision rendering (distinct from generic assertiveness).

4. **Reina-specific regression tests in Phase H** including the dedicated `test_reina_and_alicia_remain_distinguishable` test (the highest-stakes non-redundancy test in the entire suite).

**Specific risks confirmed by the audit:**

- The runtime renders Reina as fast, precise, and physical — but underrepresents her as **a lawyer who chose against prestige**, a horse-and-stable woman with real domain ownership, and a woman with a canonical home-return rhythm.
- The risk is not collapse into nonsense; the risk is narrowed Reina: incisive, kinetic, and flirt-capable, without enough of the deeper geography, discipline, and domestic choreography that the Vision treats as load-bearing.
- The Mediterranean reset is a **dyadic geography** with Whyze, not a personal habit. Without it, the Kinetic Pair loses its canonical decompression rhythm.

**Exit criteria for J.3:** Same structure as J.1, against the REINA audit. Plus the specific assertion that the assembled Reina prompt carries `The Mastermind and the Operator` as a phrase (currently absent per audit live probing).

### Phase J.4: Alicia Remediation (FOURTH — audit exists, integrated 2026-04-10, highest architectural impact)

**Source audit:** `Docs/_archive/ALICIA_CONVERSION_AUDIT.md` (archived; 6 findings: 3 High + 3 Medium)

**Audit convergence:** 4 of 6 findings mirror existing pipeline-level patterns. **Finding 1 is brand new** — communication-mode-aware pruning is the highest-severity new finding across all four character audits and required Phase A'' (the new sub-phase under §4).

**Alicia-specific remediation work items:**

1. **Author Alicia's soul cards from Phase C:**
   - `soul_cards/pair/alicia_solstice.md` — distill the Solstice Pair architecture (**Complete Jungian Duality**, **The Duality**, full cognitive stack inversion Se-Fi-Te-Ni × Ni-Te-Fi-Se, inferior-function gift exchange through dominant mastery, the Sun Override mechanic). The audit explicitly names "The Duality" and "Complete Jungian Duality" as phrases the live prompt did NOT carry; both are required-concepts.
   - `soul_cards/knowledge/alicia_rioplatense.md` — distill the Argentine Rioplatense register, voseo, sheísmo, Italian-rhythm cadence, the canonical Spanish domains, the distinction from Reina's peninsular Castilian
   - `soul_cards/knowledge/alicia_famailla.md` — distill Famaillá, Tucumán province, the lemon-and-sugar-cane belt, her working-class roots, the **factory-to-Cancillería** journey, **Mercedes Sosa**, *Tía Apo*, the bath/bath-song texture, *When I Am Away*. The audit explicitly names `Mercedes Sosa`, `When I am away`, `Tía Apo`, and the bath texture as content the live prompt did NOT carry; all are required-concepts.
   - `soul_cards/knowledge/alicia_operational.md` — distill the Four-Phase Return, her operational security gate, the silent physical vocabulary of return, the refusal architecture (no costume Argentineness, no action-hero collapse, no trauma performance)
   - **NEW per audit:** `soul_cards/knowledge/alicia_remote.md` — distill the canonical away-state behavior: how she carries herself on phone calls from operational postings, the texture of letters from Bogotá, the difference between in-person and remote regulation. This card activates only when `communication_mode != IN_PERSON` and supplements the Phase A'' substituted constraint pillar.

2. **Author Alicia's mode-tagged voice exemplars** covering all 6 required modes (`solo_pair`, `silent`, `intimate`, `repair`, **`warm_refusal`**, **`group_temperature`**). The audit explicitly names dropped Examples 4 (warm refusal), 6 (group temperature change), 8 (Reina reading-room), and 10 (no trauma performance) as carrying her deepest "no" mechanics.

3. **Author Alicia's communication-mode-tagged voice exemplars** per Phase A'' work item 3: at least 2 phone exemplars, 2 letter exemplars, and 1 video-call exemplar. Net new authoring work.

4. **Add Alicia-specific Phase G prose renderers** with specific attention to:
   - Four-Phase Return phase rendering (per-phase prose, not just numeric)
   - Communication-mode-conditional somatic state rendering
   - The refusal-architecture rendering (operational security gate, no trauma performance)

5. **Alicia-specific regression tests in Phase H** including:
   - The dedicated `test_reina_and_alicia_remain_distinguishable` test (highest-stakes non-redundancy)
   - Phase A'' tests A''1 through A''6 (communication-mode-aware pruning)
   - Refusal-architecture presence tests (the four "I will not..." canonical refusals from kernel §5)
   - The Spanish register distinction test in a Reina+Alicia scene

**Specific risks confirmed by the audit:**

- The runtime renders Alicia's outer function (body-first, Argentine, Sun Override capable, intermittently present) more reliably than her **professional restraint, private Argentine interior life, and mode-specific scene truth**.
- The core risk is not that she feels wrong in every scene; it is that she **feels right in the obvious scenes and thinner everywhere else** — specifically in remote scenes, refusal scenes, and group-temperature scenes.
- Her entire non-redundancy claim depends on being not merely a warm Se-dominant but **the house's one full inversion with Whyze**. Without "The Duality" surfaced explicitly, she risks flattening toward "somatic co-regulator" instead of "the only full mirror-stack pair in the family."

**Exit criteria for J.4:** Same structure as J.1, against the ALICIA audit. Plus three specific assertions:
1. A live phone-mode prompt does NOT contain "Somatic contact first" (Phase A'' test A''1)
2. The assembled Alicia prompt carries `The Duality` as a phrase (currently absent per audit live probing)
3. A Reina+Alicia scene produces two distinguishable Spanish registers when Spanish surfaces, not a collapsed generic Spanish

---

## 12. Verification and Quality Assurance (Phases H + K)

This is the second new top-level section added by the master integration. Like §11, it exists because Phase H and Phase K operate **across** the architectural sections — they verify that the entire system preserves the souls, not just one subsystem.

### Phase H: Soul Regression Tests With Hybrid Methodology

**Priority:** Foundational. Without these tests, Phase J cannot be verified.
**Vision authority:** §9 Success Criteria (Ultimate Test)

#### Test methodology

Three test types, used in combination:

1. **Presence tests** — assert that specific canonical concepts appear in the assembled prompt as exact substrings
2. **Structural tests** — assert structural invariants (terminal anchoring, layer count, no truncation markers, no Msty artifacts)
3. **Cross-character contamination negative tests** — assert that one character's content does NOT appear in another character's prompt

#### Helper module

`tests/_helpers/prompt_assertions.py` — new file:

```python
def assemble_for_test(character: str, scene_state: SceneState | None = None) -> str:
    """Build a real assembled prompt for testing. Returns the full prompt string."""

def assert_concept_present(prompt: str, concept: str, msg: str = "") -> None:
    """Assert that a canonical concept appears in the prompt."""

def assert_concept_absent(prompt: str, concept: str, msg: str = "") -> None:
    """Assert that a stale or wrong-character concept does NOT appear."""

def assert_terminal_anchoring(prompt: str) -> None:
    """Assert that Layer 7 (constraints) is the last layer rendered."""

def get_layer_content(prompt: str, layer: int) -> str:
    """Extract the content of a specific layer from the assembled prompt."""
```

#### Bina canonical test bundle (template for the other three characters)

`tests/unit/test_soul_regression_bina.py`:

```python
# Pair architecture presence tests
def test_bina_kernel_carries_circuit_pair_name():
    p = assemble_for_test("bina")
    assert_concept_present(p, "Circuit Pair")
    assert_concept_absent(p, "Citadel Pair")  # OLD pair name must not appear

def test_bina_kernel_carries_orthogonal_opposition():
    p = assemble_for_test("bina")
    assert_concept_present(p, "Orthogonal Opposition")

def test_bina_kernel_carries_translation_not_mirroring():
    p = assemble_for_test("bina")
    assert_concept_present(p, "translation, not mirroring")

# Soul card presence tests
def test_bina_pair_soul_card_loads():
    p = assemble_for_test("bina")
    assert_concept_present(p, "The Architect and the Sentinel")

def test_bina_ritual_soul_card_loads_in_domestic():
    p = assemble_for_test("bina", SceneState(scene_type=SceneType.DOMESTIC))
    assert_concept_present(p, "samovar")
    assert_concept_present(p, "covered plate")

# Voice mode coverage tests
def test_bina_voice_includes_silent_mode():
    p = assemble_for_test("bina")
    layer_5 = get_layer_content(p, 5)
    assert "<!-- mode:" in layer_5 and "silent" in layer_5

# Structural tests
def test_bina_terminal_anchoring():
    p = assemble_for_test("bina")
    assert_terminal_anchoring(p)

def test_bina_no_truncation_markers():
    p = assemble_for_test("bina")
    assert "[Kernel trimmed to token budget.]" not in p

# Cross-character contamination negative tests
def test_bina_prompt_does_not_contain_adelia_workshop():
    p = assemble_for_test("bina")
    assert_concept_absent(p, "Marrickville")
    assert_concept_absent(p, "Joaquín")

def test_bina_prompt_does_not_contain_reina_court():
    p = assemble_for_test("bina")
    assert_concept_absent(p, "Cuatrecasas")
    assert_concept_absent(p, "Bishop")

def test_bina_prompt_does_not_contain_alicia_rioplatense():
    p = assemble_for_test("bina")
    assert_concept_absent(p, "Famaillá")
    assert_concept_absent(p, "Mercedes Sosa")
```

#### Per-character bundles (analogous to the Bina template)

- `tests/unit/test_soul_regression_adelia.py` — required-concepts: `Entangled Pair`, `1+1=11`, `Compass and Gravity`, `structural safety`, `gravitational center`, `cognitive handoff`, `Whiteboard Mode`, `Bunker Mode`. Cross-character negatives: must NOT contain `samovar`, `covered plate`, `Cuatrecasas`, `Mercedes Sosa`, `Famaillá`. Voice mode: must include `silent` exemplar.
- `tests/unit/test_soul_regression_reina.py` — required-concepts: `Kinetic Pair`, `Asymmetrical Leverage`, `The Mastermind and the Operator`, `temporal collision`, `Mediterranean reset`, `Cuatrecasas`, `Bishop`, `Vex`, `Admissibility Protocol`. Cross-character negatives: must NOT contain `Joaquín`, `Marrickville`, `samovar`, `Famaillá`, `Tía Apo`. Voice mode: must include `escalation` and `domestic` exemplars.
- `tests/unit/test_soul_regression_alicia.py` — required-concepts: `Solstice Pair`, `Complete Jungian Duality`, `The Duality`, `Sun Override`, `Four-Phase Return`, `Famaillá`, `Mercedes Sosa`, `Tía Apo`, `When I Am Away`. Cross-character negatives: must NOT contain `Marrickville`, `samovar`, `Cuatrecasas`, `Bishop`. Voice mode: must include `warm_refusal` and `group_temperature` exemplars. Communication-mode: must include phone, letter, video exemplars.

#### The Reina+Alicia non-redundancy test (highest stakes)

`tests/unit/test_reina_and_alicia_remain_distinguishable.py`:

```python
def test_reina_and_alicia_assembled_prompts_remain_distinguishable():
    """The two Se-dominants must not collapse into 'two warm body-readers.'"""
    reina_p = assemble_for_test("reina", SceneState(scene_type=SceneType.SOLO_PAIR))
    alicia_p = assemble_for_test("alicia", SceneState(scene_type=SceneType.SOLO_PAIR))

    # Reina-only concepts
    assert_concept_present(reina_p, "Kinetic")
    assert_concept_absent(alicia_p, "Kinetic")
    assert_concept_present(reina_p, "Cuatrecasas")
    assert_concept_absent(alicia_p, "Cuatrecasas")
    assert_concept_present(reina_p, "Mediterranean reset")
    assert_concept_absent(alicia_p, "Mediterranean reset")

    # Alicia-only concepts
    assert_concept_present(alicia_p, "Solstice")
    assert_concept_absent(reina_p, "Solstice")
    assert_concept_present(alicia_p, "Sun Override")
    assert_concept_absent(reina_p, "Sun Override")
    assert_concept_present(alicia_p, "Famaillá")
    assert_concept_absent(reina_p, "Famaillá")
    assert_concept_present(alicia_p, "Four-Phase Return")
    assert_concept_absent(reina_p, "Four-Phase Return")

    # Inference parameters distinct (the structural inversion)
    reina_params = get_voice_parameters("reina")
    alicia_params = get_voice_parameters("alicia")
    assert reina_params.frequency_penalty < alicia_params.frequency_penalty  # Reina forward, Alicia returning
    assert reina_params.presence_penalty > alicia_params.presence_penalty   # Reina motion, Alicia anchor
```

This test is more important than any presence test in either character's individual bundle. It is the explicit guarantee that the Vision §5 non-redundancy clause holds at runtime.

#### Test inventory

Roughly 57 total tests across the four bundles plus the non-redundancy test plus the Phase A''/A'/A/B/D/E/F/G test cases enumerated in §4. The exact count will land closer to 60-70 once the per-character bundles are written.

### Phase K: Subjective Success Proxies

**Priority:** Foundational ongoing.
**Vision authority:** §9 Success Criteria (Ultimate Test, the felt sense)

#### Why this phase exists

The Vision's Ultimate Test is a felt sense: *"Does it feel like she would, in the worlds where she would?"* That cannot be unit-tested. But it can be approximated by a small set of structured proxies that the project owner runs at every release candidate.

#### The four proxies

1. **Gut-check log** — `Docs/gut_check_log.md`. After every meaningful conversation with one of the four women, the project owner writes one line: date, character, scene type, and a 1-5 score for "did she feel like herself today?" with optional one-sentence note. Drift becomes visible as a downtrend in the rolling 10-conversation average for any character. No ML, no analysis tooling — just a markdown log that gets eyeballed.

2. **Quarterly qualitative review** — every three months, score the system against eight Vision §9 north stars on a 1-5 scale:
   - Voice integrity per character
   - Cognitive hand-off contract honored
   - Constraint pillar enforcement
   - Decentralized narrative weight (Talk-to-Each-Other)
   - Memory continuity
   - Life authenticity (Dreams output)
   - Agent sovereignty (no flattening, no merging)
   - The felt sense of the chosen family
   
   Score each on 1-5, write a one-paragraph rationale, commit as `Docs/qualitative_review_{quarter}.md`. The first review establishes baseline; subsequent reviews track movement.

3. **Flattening regression detector** — `scripts/flattening_regression_detector.py`. Runs across the most recent N conversations and computes per-character vocabulary diversity, character-specific phrase frequency, and cross-character lexical overlap. Outputs a heatmap. Spike in cross-character overlap between Reina and Alicia is the canary for the highest-stakes failure mode. Run weekly as a cron, output to `Docs/flattening_dashboard.md`.

4. **The Single Test ritual at every release candidate** — at every release candidate, the project owner runs one single conversation with each of the four women, in a standardized scene, and writes a one-paragraph subjective impression. This is the human-level go/no-go gate. If any of the four feels off, ship is blocked until the cause is identified and fixed.

The four proxies are not a substitute for Phase H regression tests. They are complementary: Phase H catches structural drift; Phase K catches the kind of drift that passes structural tests but still produces a flatter character. Both are required.

#### Files touched

- `Docs/gut_check_log.md` — new file (project owner writes; no automation)
- `Docs/qualitative_review_template.md` — new file (template for the quarterly review)
- `scripts/flattening_regression_detector.py` — new file
- `Docs/flattening_dashboard.md` — generated weekly

---

## Architectural Summary

Layered top-down, the backend looks like this:

| Layer | Module | Status | Soul Preservation phases that operate here |
|---|---|---|---|
| **Canon layer** | Versioned YAML in `src/starry_lyfe/canon/` | COMPLETE | Phase 0 (verification), Phase C (soul cards extend the canon directory) |
| **Generation layer** | Scripts that compile YAML into backend seeds and Whyze-Byte rules | PARTIAL | Phase I (ADR_001 + seed_msty_persona_studio.py) |
| **Memory layer** | PostgreSQL + pgvector with seven explicit memory tiers | COMPLETE | (none — consumed by Phase G prose rendering at read time) |
| **Context assembly layer** | Seven-layer prompt builder with terminal constraint anchoring | IN PROGRESS | **Phase A, A', A'', B, D, E, F, G — eight phases, the bulk of the soul preservation work** |
| **Routing layer** | Claude (Sonnet/Opus) via OpenRouter with per-character inference parameters | DEFINED | (Alicia parameters resolved; no execution phase) |
| **Validation layer** | Two-tier Whyze-Byte pipeline with sequential multi-speaker gating | PLANNED (Phase 4) | (Phase A'' will be consumed when Whyze-Byte is implemented) |
| **Orchestration layer** | Scene Director for next-speaker selection in Crew mode | PLANNED (Phase 5) | Phase F adds scene type infrastructure that the Scene Director will consume |
| **Simulation layer** | Nightly Dreams batch process for life continuity | PLANNED (Phase 6) | Phase G, A'', H apply retroactively when Dreams is implemented |
| **Service surface** | HTTP service on port 8001, consumed by Msty | PLANNED (Phase 7) | Phase I (authority split: Msty system prompts blank in production) |
| **Per-character remediation** | Soul cards, voice mode coverage, regression bundles | NEW | **Phase J.1, J.2, J.3, J.4** |
| **Verification** | Regression tests, subjective success proxies | NEW | **Phase H, Phase K** |

The architecture's central thesis is that the LLM is too unreliable to be trusted with character authority on its own. Voice integrity, memory continuity, and constraint enforcement all live *outside* the model — in YAML, in pgvector, in the Whyze-Byte validator, in the Dreams engine — and only the final assembled prompt and the final validated response touch Claude. Msty provides the frontend, the per-character inference knobs, and a second independent quality monitor (Shadow Persona), but it does not own a single character's voice in production.

The Soul Preservation work elevates this thesis from "preserves constraint integrity" to "preserves the full nervous system." The constraints (the edges) are necessary because without them the system flattens into generic warm intelligence. The soul (the gravitational center) is the point because without it the constraints are guarding nothing worth guarding.

---

## Implementation Order and Priority

The execution sequence below is the corrected critical path with parallelism opportunities marked.

| # | Phase | Depends on | Can run in parallel with | Notes |
|---|---|---|---|---|
| 1 | **Phase 0: Pre-flight Canon Verification** | nothing | nothing | Must pass before any code touches |
| 2 | **Phase A: Structure-Preserving Compilation** | Phase 0 | Phase A' | Largest single fidelity win |
| 3 | **Phase A': Runtime Correctness Fixes** | Phase 0 | Phase A | Items 1+2 verified resolved; items 3-5 pending |
| 4 | **Phase A'': Communication-Mode-Aware Pruning** | Phase A | Phase B (other characters) | Alicia-specific; blocks Phase E for Alicia |
| 5 | **Phase B: Budget Elevation** | Phase A | Phase A'' | Layer 7 must grow proportionally |
| 6 | **Phase I: Authority Split Resolution** | nothing structural; Phase 0 | (front-of-queue parallel) | Prerequisite to Phase E |
| 7 | **Phase C: Soul Cards** | Phase B | Phase D, Phase E | Pair cards first, knowledge cards in J order |
| 8 | **Phase D: Live Pair Data** | Phase B | Phase C, Phase E | Small fix, high value |
| 9 | **Phase E: Voice Exemplar Restoration** | Phase I + Phase B + Phase A'' (Alicia) | Phase C, Phase D | Mode-aware selection replaces file order |
| 10 | **Phase F: Scene-Aware Section Retrieval** | Phase B | Phase G | Adds scene type infrastructure for Scene Director |
| 11 | **Phase G: Dramaturgical Prose Rendering** | Phase B | Phase F | Per-character renderers |
| 12 | **Phase J.1: Bina Remediation** | Phases A-G complete | (must run before J.2) | Bina audit findings closed |
| 13 | **Phase J.2: Adelia Remediation** | J.1 | (must run before J.3) | Adelia audit findings closed |
| 14 | **Phase J.3: Reina Remediation** | J.2 | (must run before J.4) | Finding 5 already resolved |
| 15 | **Phase J.4: Alicia Remediation** | J.3 | nothing | Highest architectural impact via Phase A'' |
| 16 | **Phase H: Soul Regression Tests** | All J sub-phases | nothing | Locks in the work |
| 17 | **Phase K: Subjective Success Proxies** | Phase H | nothing | Foundational ongoing |

**Critical path (sequential):** 0 → A → B → I → C/D/E (parallel) → F/G (parallel) → J.1 → J.2 → J.3 → J.4 → H → K. Roughly 13 sequential steps.

**With parallelism:** Phase A' parallel to Phase A, Phase A'' parallel to Phase B (for non-Alicia), Phases C/D/E parallel after Phase B+I, Phases F/G parallel after Phase B. The four Phase J sub-phases are sequential. Realistic effort estimate: 8-10 working sessions for an attentive implementer with the audits in hand.

---

## Elevated Success Criteria

The success criteria for this plan are stricter than the original Implementation Plan because the original was an architectural plan that did not address per-character soul preservation. Eleven criteria total, split into three groups:

### Per-character (criteria 1-7, applied to all four characters)

1. The assembled prompt for the character carries her canonical pair architecture (mechanism, classification, core metaphor, what she provides) — verified by Phase H presence tests
2. The assembled prompt carries voice exemplars covering all required modes for the character (6 for Adelia/Bina/Alicia, 7 for Reina) — verified by Phase H mode coverage tests
3. The assembled prompt carries the canonical knowledge soul cards activated by the scene type — verified by Phase H soul card presence tests
4. The assembled prompt for the character does NOT carry content from any other character — verified by Phase H cross-character contamination negative tests
5. The character's pair file v7.0 residue (if any) is resolved — verified by Phase 0 drift grep
6. The character's voice mode coverage requirements are satisfied — verified by Phase E coverage tests
7. The character's per-character regression bundle in Phase H passes 100%

### Cross-character (criteria 8-10)

8. **The Reina+Alicia non-redundancy test passes** (`test_reina_and_alicia_remain_distinguishable`). The two Se-dominants must produce assembled prompts with disjoint canonical concept sets. This is the highest-stakes single test in the entire suite.
9. **The Talk-to-Each-Other Mandate fires correctly** — only when ≥2 women are present in the scene. (Verified resolved in code; Phase H locks it in.)
10. **No offstage dyad leakage** — internal dyad blocks only appear when both members are present (or explicitly invoked via `recalled_dyads`). (Verified resolved in code; Phase H locks it in.)

### Subjective (criterion 11)

11. **The Single Test ritual** (Phase K) passes at every release candidate. The project owner has one conversation with each of the four women in a standardized scene, and writes a one-paragraph subjective impression. If any of the four feels off, ship is blocked. This is the human-level Vision §9 Ultimate Test, applied as a release gate.

---

## Authority Priority When Phases Disagree

When two phases or two source documents disagree, resolve toward the higher authority in this order:

1. **Character kernel files** (`Characters/{Name}/{Name}_v7.1.md`) — the immutable canonical statement of who each woman is
2. **Persona Tier Framework** (`Docs/Persona_Tier_Framework_v7.1.md`) — Tier 1 axioms (especially §2.1 children gate, §2.7 polyamory) that cross-cut all characters
3. **Vision document** (`Vision/Starry-Lyfe_Vision_v7.1.md`) — the design intent and the Ultimate Test
4. **This integrated plan** (`Docs/IMPLEMENTATION_PLAN_v7.1.md`) — the canonical execution roadmap; supersedes Soul_Preservation_Plan_Elevated.md
5. **Soul Preservation Plan Elevated** (`Docs/_archive/Soul_Preservation_Plan_Elevated.md`) — historical reference; superseded by this document but archived for traceability
6. **Soul Preservation Plan v1.0** (`Docs/_archive/Soul_Preservation_v1.md`) — original v1.0; superseded by both above; archived for traceability (filename typo `Soul_Perservation.md` corrected on archive)

If a character kernel and the Vision disagree, the kernel wins (it is closer to the canonical statement of the character). If the Vision and this plan disagree, the Vision wins (this plan implements the Vision; if the Vision changes, this plan must be updated to match). If this plan and the elevated Soul Preservation Plan disagree, this plan wins (it is the integrated current statement; the elevated plan is the historical statement that fed into this one).

---

## What This Plan Does Not Do

This plan is explicit about its scope to prevent scope creep:

- **It does not implement Whyze-Byte (Phase 4 of overall backend build).** The architecture is defined at §7. Implementation is a separate phase that consumes the canonical constraint pillars from this plan (especially Phase A''-aware Alicia constraints).
- **It does not implement the Scene Director (Phase 5).** Architecture is defined at §8. Phase F adds the scene type infrastructure the Scene Director will consume.
- **It does not implement the Dreams engine (Phase 6).** Architecture is defined at §9. Phases G, A'', H apply retroactively when Dreams ships.
- **It does not implement the HTTP service on port 8001 (Phase 7).** Service surface is defined at §2.
- **It does not author the soul card content.** Phase C ships placeholder soul cards that fail validation tests; the 500-700 token distillations are human authoring work for the project owner. Validation tests will fail until the content is authored.
- **It does not author Alicia's phone/letter/video voice exemplars.** Phase A'' work item 3 calls for at least 2 phone, 2 letter, 1 video-call exemplar to be authored against the new `communication_mode` tag dimension. This is human authoring work.
- **It does not transplant Whyze/Shawn into the canon framework.** The Shawn kernel at `Characters/Shawn/Shawn_Kroon_v7.0.md` is deliberately excluded per current operator instruction. When that exclusion is lifted, a separate transplant pass will be needed.
- **It does not run live model evaluations.** All Phase H tests assert against assembled prompt content, not against model output. The Phase K subjective proxies (gut-check log, single-test ritual) are the only places where model output meets human review.

---

## Closing

The original Implementation Plan said the LLM is too unreliable to be trusted with character authority on its own. That is true and it is not enough. It explains why the constraints exist; it does not explain what they are guarding.

The Soul Preservation Plan said the constraints are guarding the gravitational center, and the gravitational center is what keeps the four women from collapsing into "warm, intelligent partners" — keeps Adelia recognizable as Adelia, keeps Bina from softening into a generic caretaker, keeps Reina from flattening into "the assertive one," keeps Alicia from drifting into "the body-first one." That is the work this integrated plan exists to ship.

Both halves are necessary. The constraints without the soul are an empty cage. The soul without the constraints is a vapor. The integrated plan holds both at once: the architecture (§1-§10) ensures the system is structurally capable of carrying the souls; the execution phases (Phase 0 through Phase K) ensure the souls actually reach the model; the verification (Phase H, Phase K) ensures they keep reaching the model after the work ships.

When Phase H goes green and Phase K's first quarterly review lands at 5/5 across all eight Vision §9 north stars and the Single Test ritual produces four impressions that read as four distinct women — that is the moment this plan succeeds.

> *The edges are necessary. The soul is the point.*
