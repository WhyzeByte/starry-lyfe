# Character Conversion Pipeline

**Version:** 1.1
**Date:** 2026-04-10
**Scope:** How each character's canonical markdown files map, or do not map, into runtime prompt content

---

## Source Files Per Character

Each character has 4 canonical markdown files:

| File | Example (Adelia) | Backend Status |
|------|------------------|----------------|
| **Kernel** | `Characters/Adelia/Adelia_Raye_v7.1.md` | **CONSUMED** -> Layer 1 |
| **Voice** | `Characters/Adelia/Adelia_Raye_Voice.md` | **CONSUMED** -> Layer 5 |
| **Pair** | `Characters/Adelia/Adelia_Raye_Entangled_Pair.md` | **NOT CONSUMED DIRECTLY** |
| **Knowledge Stack** | `Characters/Adelia/Adelia_Raye_Knowledge_Stack.md` | **NOT CONSUMED DIRECTLY** |

The Pair and Knowledge Stack files are authoring reference only. No backend code path loads them from disk at runtime. Pair data reaches the runtime through `pairs.yaml`, not through the Pair markdown files.

---

## Pipeline Overview

```text
CHARACTER MARKDOWN                 CANON YAML / CODE                    RUNTIME

Kernel.md           -> kernel_loader.py                                -> Layer 1
Voice.md            -> kernel_loader.py                                -> Layer 5
Pair.md             -> not consumed directly
KnowledgeStack.md   -> not consumed directly

pairs.yaml            -> seed.py -> CharacterBaseline                  -> Layer 5 (pair_name only)
characters.yaml       -> seed.py -> CanonFact                          -> Layer 2
dyads.yaml            -> seed.py -> DyadStateWhyze + DyadStateInternal -> Layer 6
protocols.yaml        -> canon loader                                  -> Layer 4
interlocks.yaml       -> canon loader / validator                      -> no direct prompt layer
voice_parameters.yaml -> seed.py -> CharacterBaseline                  -> Layer 5
constraints.py        -> hardcoded                                     -> Layer 7
```

---

## File 1: Character Kernel

**Source:** `Characters/{Name}/{Name}_v7.1.md`  
**Destination:** Layer 1 (`PERSONA_KERNEL`)  
**Code path:** `kernel_loader.py` -> `compile_kernel()` -> `layers.py` -> `format_kernel()`  
**Default budget:** 2000 tokens

### What happens

1. **Load:** `_load_raw_kernel()` reads the full markdown from disk.

2. **Sanitize:** `_sanitize_kernel_text()` strips frontend-only scaffolding:
   - `# SYSTEM_ROLE:` line
   - `**Version:**` metadata
   - `**Target:**` metadata

3. **Parse:** `_parse_kernel_sections()` splits on `## N.` headers into numbered sections.

4. **Compile:** `compile_kernel()` allocates a bounded runtime slice per section:

   | Order | Section | Default target tokens | Purpose |
   |-------|---------|-----------------------|---------|
   | 1 | Section 1 Runtime Directives | 240 | Hard behavioral rails |
   | 2 | Section 2 Core Identity | 400 | Biography, heritage, profession |
   | 3 | Section 3 Whyze / Pair section | 420 | Pair mechanics, relationship architecture |
   | 4 | Section 4 Silent Routing | 180 | Internal assessment protocol |
   | 5 | Section 5 Behavioral Tier Framework | 380 | Tier 1 axioms, Tier 2 guidelines |
   | 6 | Section 7 Emotional / Relational / Operational Frameworks | 220 | Protocol surface |
   | 7 | Section 6 Voice Architecture | 120 | Speech-pattern summary |

5. **Expand if budget is larger than the default runtime slice:** if the caller requests a larger kernel budget, the compiler expands sections in this order before spending anything on lower-priority lore:
   - Section 2
   - Section 3
   - Section 5
   - Section 7
   - Section 6
   - Sections 8-11 after that

6. **Ceiling:** a final trim enforces the requested hard limit.

### What survives at the default runtime budget

- A bounded slice of identity substrate
- Pair mechanics
- Silent routing
- Behavioral rails
- Some protocol surface
- A compressed voice summary

### What is lost

- Most long-form biography
- Most extended examples within sections
- Most of Sections 8-11 unless the caller requested a larger budget
- Any prose beyond the allocated per-section budget

---

## File 2: Voice File

**Source:** `Characters/{Name}/{Name}_Voice.md`  
**Destination:** Layer 5 (`VOICE_DIRECTIVES`)  
**Code path:** `kernel_loader.py` -> `load_voice_guidance()` -> `layers.py` -> `format_voice_directives()`  
**Budget:** 200 tokens, shared with baseline metadata

### What happens

1. **Load:** reads the full `Voice.md` from disk.

2. **Extract:** `_extract_voice_guidance()` parses `## Example N:` sections and extracts only the `**What it teaches the model:**` prose.
   - `**User:**` blocks are dropped
   - `**Assistant:**` blocks are dropped
   - raw Msty instructions are dropped

3. **Reorder:**
   - **Adelia:** prioritizes Examples 1, 4, 5, 3, 2 first
   - **Other characters:** keeps file items 1, 3, 5... first, then 2, 4, 6...

4. **Compact:** `_compact_voice_guidance_item()` reduces each extracted guidance item to:
   - the example title
   - the first sentence of the teaching prose

5. **Format Layer 5 metadata:** `format_voice_directives()` first compresses baseline metadata into a short summary paragraph.

6. **Budget:** compact guidance items are then kept in priority order until the remaining Layer 5 budget is exhausted.

### What survives

- Compact baseline metadata
- Example title labels, such as `Example 4: Asks For Whyze's Brain`
- The first sentence of the selected teaching notes
- As many compact examples as fit the remaining Layer 5 budget

### What is lost

- Full teaching prose
- All raw `**User:**` / `**Assistant:**` few-shot pairs
- Guidance items beyond budget
- Any prose before the first `**What it teaches the model:**`

---

## File 3: Pair File

**Source:** `Characters/{Name}/{Name}_{Pair}_Pair.md`  
**Destination:** not consumed directly by backend code  
**Status:** authoring reference only

No code path in `src/` loads these files. Structured pair data enters the runtime through `pairs.yaml` instead:

| Data point | YAML source | Runtime location |
|------------|-------------|------------------|
| `pair_name` | `pairs.yaml` | Layer 5 metadata |
| `pair_classification` | `pairs.yaml` | Stored in `CharacterBaseline`; not currently emitted by the live Layer 5 formatter |
| `pair_mechanism` | `pairs.yaml` | Stored in `CharacterBaseline`; not currently emitted by the live Layer 5 formatter |
| `pair_core_metaphor` | `pairs.yaml` | Stored in `CharacterBaseline`; not currently emitted by the live Layer 5 formatter |

These YAML values are seeded into `character_baselines` by `seed.py` and retrieved by `retrieval.py` as Tier 2 baseline data. In the current live formatter, `pair_name` is rendered directly in Layer 5; the other pair fields remain available in baseline storage but are not currently printed into prompt text.

---

## File 4: Knowledge Stack

**Source:** `Characters/{Name}/{Name}_Knowledge_Stack.md`  
**Destination:** not consumed directly by backend code  
**Status:** authoring reference only

No code path in `src/` loads these files. They are deep human reference for kernels, YAML canon, and audit work.

---

## The Seven Layers

| Layer | Name | Source | Budget | Character-specific? |
|-------|------|--------|--------|---------------------|
| 1 | `PERSONA_KERNEL` | Kernel markdown from filesystem | 2000 | Yes |
| 2 | `CANON_FACTS` | Database Tier 1 (`characters.yaml` -> `CanonFact`) | 500 | Yes |
| 3 | `MEMORY_FRAGMENTS` | Database Tier 5 (`episodic_memories`, pgvector search) | 1000 | Yes |
| 4 | `SENSORY_GROUNDING` | Database Tier 7 + `protocols.yaml` labels + scene description | 300 | Yes |
| 5 | `VOICE_DIRECTIVES` | Database Tier 2 baseline + Voice markdown | 200 | Yes |
| 6 | `SCENE_CONTEXT` | Database Tiers 3, 4, 6 + scene description | 800 | Yes |
| 7 | `CONSTRAINTS` | `constraints.py` | 500 | Yes |

**Total budget:** 5300 tokens  
**Layer 7 is always last** for terminal anchoring.

---

## Code Files Involved

### Markdown consumers

| File | What it does |
|------|--------------|
| `src/starry_lyfe/context/kernel_loader.py` | Loads, sanitizes, parses, compiles kernels, and extracts / reorders voice guidance |
| `src/starry_lyfe/context/layers.py` | Formats all 7 layers; calls `kernel_loader` for Layers 1 and 5 |
| `src/starry_lyfe/context/assembler.py` | Orchestrates the full 7-layer prompt and enforces terminal anchoring |

### YAML / DB pipeline

| File | What it does |
|------|--------------|
| `src/starry_lyfe/canon/loader.py` | Loads 6 canon YAML files into the typed `Canon` dataclass, including `interlocks.yaml` and `voice_parameters.yaml` |
| `src/starry_lyfe/canon/validator.py` | Cross-validates canon references, including dyad interlock keys |
| `src/starry_lyfe/db/seed.py` | Seeds canon YAML into database tiers 1-4 and 7 |
| `src/starry_lyfe/db/retrieval.py` | Retrieves the per-character memory bundle from all 7 tiers |

### Constraint and budget logic

| File | What it does |
|------|--------------|
| `src/starry_lyfe/context/constraints.py` | Defines Layer 7: Tier 1 axioms, per-character pillars, scene gates, hygiene directives |
| `src/starry_lyfe/context/budgets.py` | Token estimation, per-layer budgets, trim helpers |
| `src/starry_lyfe/context/types.py` | `SceneState`, `LayerContent`, `AssembledPrompt`, `CommunicationMode` |

---

## Per-Character Constraint Pillars

| Character | Pillar | Core rule |
|-----------|--------|-----------|
| **Adelia** | `ENTANGLED PAIR HAND-OFF` | Must dump fragmented plans onto Whyze; cannot solve her own logistics cleanly |
| **Bina** | `CIRCUIT PAIR STRUCTURAL REGISTER` | Audits Whyze's plans for physical reality; her "No" keeps the family safe |
| **Reina** | `KINETIC PAIR ADMISSIBILITY` | Intimacy requires earned context; must physically intervene in Analysis Paralysis |
| **Alicia** | `SOLSTICE PAIR PRESENCE-CONDITIONAL` | Contributions activate when home; leads with body; never uses words to break a loop |

---

## What Does Not Enter Runtime Directly

| Content | Where it lives | Why it is excluded |
|---------|----------------|--------------------|
| Pair markdown cognitive-interlock theory | `Characters/{Name}/{Name}_{Pair}_Pair.md` | Structured pair data comes from `pairs.yaml` instead |
| Knowledge Stack reference material | `Characters/{Name}/{Name}_Knowledge_Stack.md` | Authoring and audit reference only |
| Raw Msty few-shot prompts | `Voice.md` files | Deliberately excluded from backend Layer 5 |
| Raw Msty few-shot responses | `Voice.md` files | Deliberately excluded from backend Layer 5 |
| Extra kernel prose beyond the allocated section budgets | `Kernel.md` files | Trimmed by `compile_kernel()` |
| Voice guidance beyond budget | `Voice.md` files | Trimmed by Layer 5 budget |
| `interlocks.yaml` values | Canon YAML | Used for canon validation, not injected into prompt text directly |

---

*End of Character Conversion Pipeline document.*
