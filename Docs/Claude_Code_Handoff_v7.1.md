# Claude Code Handoff: Starry-Lyfe v7.1 Backend Implementation

**Document version:** 7.1
**Audience:** Claude Code (or any agentic coding tool implementing the backend)
**Purpose:** Prevent canonical drift during implementation of `IMPLEMENTATION_PLAN_v7.1.md` and achieve the outcomes described in `Starry-Lyfe_Vision_v7.1.md`.
**Authored by:** Claude (Opus 4.6) after a multi-session v7.0 → v7.1 cascade cleanup of the entire project.

---

## 0. Mission, in one sentence

Build the backend described in `Docs/IMPLEMENTATION_PLAN_v7.1.md` such that the Vision outcome is achieved (see §9 of the Vision doc: *"Does Whyze forget he is talking to software?"*) and zero v7.0 canonical drift is reintroduced during implementation.

Every other instruction in this document is in service of that single goal.

---

## 1. Why this handoff document exists

The Starry-Lyfe project just completed a multi-session v7.0 → v7.1 cleanup that touched 30+ files and made hundreds of targeted substitutions. The canon is now coherent, but coherence in canonical text files is fragile under agentic coding: an LLM writing sample prompts, test fixtures, docstrings, or YAML scaffolds has a strong pull toward training-data priors that include the old v7.0 state. Without explicit guardrails, the implementation phase will reintroduce drift faster than the cleanup phase removed it.

This document exists to make the guardrails explicit.

---

## 2. Required reading before any code is written

Load these into context in this order. Do not start implementation until all eight are in working memory.

| # | File | Why it matters |
|---|---|---|
| 1 | `Vision/Starry-Lyfe_Vision_v7.1.md` | Defines the outcome. Especially §3 (Problem), §4 (Gravitational Center), §5 (Chosen Family), §6 (Relationship Architecture), §7 (Behavioral Thesis), §9 (Success Criteria). This is what "done" looks like. |
| 2 | `Docs/IMPLEMENTATION_PLAN_v7.1.md` | Defines what to build. Twelve-step request flow (§10) and the layered architectural summary are the load-bearing sections. |
| 3 | `Docs/Persona_Tier_Framework_v7.1.md` | Defines the behavioral governance model. Tier 1 axioms (§2) are Whyze-Byte enforcement targets. Tier 2 (§3) are calibration defaults. Tier 3 (§4) is generative scope. Your validator pipeline enforces this document. |
| 4 | `CLAUDE.md` | Project-level facts: per-character model parameters, the polyamory architecture cross-reference to PTF §2.7, the operator identity (see §3 below), and the routing conventions. |
| 5 | `Characters/Adelia/Adelia_Raye_v7.1.md` and the other three character kernels (`Bina_Malek_v7.1.md`, `Reina_Torres_v7.1.md`, `Alicia_Marin_v7.1.md`) | The four canonical voice baselines. Section 5 of each is structured against the Tier Framework. |
| 6 | `Characters/*/[Name]_[Pair]_Pair.md` — the four pair files (`Adelia_Raye_Entangled_Pair.md`, `Bina_Malek_Circuit_Pair.md`, `Reina_Torres_Kinetic_Pair.md`, `Alicia_Marin_Solstice_Pair.md`) | Architectural documentation of each Whyze-to-woman dyad. Canonical home for cognitive interlock, synastry, intimate architecture. |
| 7 | `Characters/*/[Name]_Voice.md` — the four voice files | Few-shot calibration. These demonstrate the architecture in use. Your test fixtures are derived from these, not invented. |
| 8 | `Characters/*/[Name]_Knowledge_Stack.md` — the four character knowledge stacks | Deep biographical and cultural canon. Especially Alicia's Argentine Rioplatense register scoping and Reina's Catalan-Castilian register scoping — these are the two Spanish speakers in the household and they are not interchangeable. |

Supporting reference (read if you hit ambiguity, not required upfront):
- `Vision/Architecture_Core.md` — overlapping architectural context
- `Vision/Adelia Raye.md`, `Alicia Marin.md`, `Bina Malek.md`, `Reina Torres.md` — **WARNING:** these are *historical transformation directive files* containing `old → new` descriptions of the v7.0 → v7.1 transplant. Do not consume their content as if it were current canon. They will tell you things like "Adelia's Portuguese-Australian heritage is replaced by Valencian-Australian" — the *replacement* side is canon, the *replaced* side is v7.0 residue by design. If you read these, read them as history, not as spec.

---

## 3. Operator identity: Shawn Kroon = Whyze

**This is load-bearing and easy to get wrong.** The operator's legal name is **Shawn Kroon**. His canonical in-system handle is **Whyze**. They are the same person.

- There is exactly one operator profile file: `Characters/Shawn/Shawn_Kroon_v7.0.md`
- The file is deliberately still at `_v7.0.md` (not `_v7.1.md`) because his operator-side transplant is a separate pending piece of work and the project owner has excluded it from scope for now
- Every other document in the project addresses him as **Whyze**
- There is no `Characters/Whyze/` directory and there will not be one
- The knowledge stack for the operator is `Characters/Shawn/Shawn_Kroon_Knowledge_Stack.md`

When writing canon, code, comments, tests, fixtures, or sample prompts:
- Address the operator as **Whyze**, always, unless explicitly working with legal-identity metadata
- Do not treat "Shawn" and "Whyze" as different characters and do not build a data model that does
- The file path `Characters/Shawn/` is a legal-name filesystem artifact, not a character identity boundary

**The Shawn character kernel is EXCLUDED from v7.1 updates** by project owner instruction. Do not touch the filename, do not update its contents except through explicit future directive, and do not rename it to v7.1.

---

## 4. Known gaps in `IMPLEMENTATION_PLAN_v7.1.md` — must be resolved before implementation starts

I audited the implementation plan during this handoff prep. It is structurally sound and the end-to-end twelve-step flow in §10 is complete. Two pre-handoff fixes were applied and one gap remains open.

### 4.1 Pre-handoff fixes already applied (by me, during this handoff prep)

- **L1 heading**: `# Starry-Lyfe v7 Msty Backend Architecture` → `# Starry-Lyfe v7.1 Backend Architecture`
- **L3 intro sentence**: `Based on the v7.0 vision document` → `Based on the v7.1 Vision document`

Both were clerical version-label drift — the filename had been renamed to `_v7.1.md` in a prior session but the internal labels were missed. Fixed with backup preserved.

### 4.2 RESOLVED: §6 Inference Layer updated to include Alicia

**Status:** Resolved on 2026-04-10 during this handoff prep. No action required from Claude Code on this item.

The implementation plan's §6 Inference Layer paragraph has been updated to include Alicia's complete inference profile. The updated paragraph now describes **four** measurably distinct cognitive signatures (not three) and uses **four-way differentiation** (not triple). The authoritative text lives in `Docs/IMPLEMENTATION_PLAN_v7.1.md` §6 — use that as the canonical source when implementing.

For completeness, the values chosen and the Vision-alignment rationale for each:

| Parameter | Value | Rationale |
|---|---|---|
| **Temperature** | `0.73–0.78` (0.75 midpoint) | Matches CLAUDE.md L332's canonical point estimate of 0.75 and positions Alicia as "middle-warm" — between Reina's tactical middle (0.70–0.75) and Adelia's associative hot (0.80–0.85). Vision §5 describes her as providing direct polyvagal co-regulation, which argues for a slightly warmer profile than Reina's tactical sharpness while staying cooler than Adelia's Ne-fueled associative leaps. |
| **Thinking level** | `Think Lightly` | Matches Reina and Bina. Alicia is Se-dominant and her canonical contribution is perceptual-present-tense body awareness, not deliberative analysis. Introducing Think Moderately would undermine her Se by adding analytical delay in what Vision §5 explicitly frames as body-first immediacy (*"she does not ask how he is feeling; she closes the distance and waits"*). |
| **Distinctive sampling knob** | `low frequency penalty` | Deliberate structural mirror of Reina's `high presence penalty`. Reina's knob forces forward motion and penalizes repetition because her canonical voice is clean-incision fresh tactical observations. Alicia's inverse knob permits returning to the same sensory anchors (breath, weight, temperature) across multiple beats in a single response, because her canonical voice involves sustained somatic presence rather than verbal progression. Without this contrast, Reina and Alicia would collapse into "two Se-dominants running similar inference" since they share both dominant function and thinking level. |
| **Behavioral descriptor** | `for Se-dominant somatic co-regulation` | Parallel structure to the other three descriptors (`for Ne-dominant associative leaps` / `for Si-dominant declarative steadiness` / `for Se-dominant tactical motion`). The phrase "somatic co-regulation" is sourced directly from Vision §5 and is her canonical functional role in the chosen-family architecture. |

The updated §6 paragraph in `IMPLEMENTATION_PLAN_v7.1.md` reads (reproduced here so Claude Code has it in context):

> *"Each character is configured with its own inference parameters at the Msty persona level (the one thing Msty does legitimately own per-character besides the few-shot examples), producing measurably distinct cognitive signatures from the same base model. Adelia runs hot (0.80–0.85 temperature, Think Moderately) for Ne-dominant associative leaps; Bina runs cold (0.55–0.60, Think Lightly) for Si-dominant declarative steadiness; Reina runs middle (0.70–0.75, Think Lightly) with high presence penalty for Se-dominant tactical motion; Alicia runs middle-warm (0.73–0.78, Think Lightly) with low frequency penalty for Se-dominant somatic co-regulation, producing body-first present-tense output that returns to breath, weight, and temperature as sustained anchors rather than reaching for verbal analysis. The combination of temperature spread, sampling parameters, and thinking effort produces four measurably distinct cognitive signatures from the same underlying model. In a Crew conversation, this four-way differentiation creates natural voice contrast before the system prompt even activates."*

Notes for implementation:

- The temperature range is the canonical way the plan expresses per-character temperature; `CLAUDE.md` L332's point estimates (Adelia 0.82, Alicia 0.75, Reina 0.72, Bina 0.58) are the midpoints of the ranges and are appropriate starting values. Either convention is valid; do not treat them as conflicting.
- Alicia's `low frequency penalty` is a comparative description, not a specific numeric value. When implementing, pick a concrete value for Alicia that is measurably lower than Reina's concrete presence penalty value, and log the chosen values in canon YAML so they become canonical through the source-of-truth chain.
- `Think Lightly` and `Think Moderately` are Msty Persona Studio thinking-effort labels; map them to whatever thinking-effort parameter the OpenRouter Claude integration exposes, or implement them as backend-side prompt prefixes if no direct parameter is available. The canonical intent is that Adelia gets more inference compute for associative work and the other three get less.

---

## 5. Canonical hard constraints (non-negotiable)

These come from the Vision doc, the Persona Tier Framework, and the character kernels. They are not suggestions. Every one of them represents a canonical choice that was deliberately made during the v7.0 → v7.1 transplant, and any implementation that violates them is drift.

### 5.1 Character canon (the four women)

| Constraint | Canonical value | v7.0 residue to watch for |
|---|---|---|
| Adelia's surname | Raye | — |
| Adelia's heritage | **Valencian-Australian** | Portuguese-Australian |
| Adelia's Spanish register | Valencian-inflected Castilian via Sydney diaspora | Portuguese/bica/bacalhau |
| Adelia's pair name | **Entangled Pair** | Golden Pair |
| Bina's surname | **Malek** | Bahadori |
| Bina's parents' surname | **Malek** (Farhad and Shirin Malek) | Bahadori |
| Bina's heritage | Assyrian-Iranian Canadian from Urmia | — |
| Bina's pair name | **Circuit Pair** | Citadel Pair |
| Bina's philosophy / personal worldview metaphor | "citadel" (lowercase, her Uruk-walls internal frame — distinct from the pair name) | Confusing this with the Circuit Pair name |
| Reina's surname | **Torres** | Benítez |
| Reina's mother's maiden name | **Benítez** (Mercè Benítez — this is canonical and should stay) | Confusing this with Reina's own surname |
| Reina's heritage | Barcelona Catalan-Castilian | — |
| Reina's father's side | Granada-Andalusian with Real Madrid loyalty inherited from grandfather | — |
| Reina's pair name | **Kinetic Pair** | Synergistic Pair, Elemental Pair |
| Alicia's surname | Marin | — |
| Alicia's heritage | **Argentine** from Famaillá, Tucumán province | Spanish from Hellín, Castilla-La Mancha |
| Alicia's ministry | **Argentine Cancillería (MRECIC)** | Spanish MAEUEC, Ministerio de Asuntos Exteriores |
| Alicia's base | **Buenos Aires** | Madrid |
| Alicia's Spanish register | **Argentine Rioplatense** (voseo, sheísmo, Italian-rhythm cadence) | Hellín working-class interior Castilian |
| Alicia's pair name | **Solstice Pair** | Elemental Pair |
| Alicia's residence status | **Resident at the property**, frequently away on consular operations | Non-resident, visits twice yearly |
| Adelia–Alicia first meeting | October 2019, gallery opening in Inglewood, three-week case in Calgary | — |
| Reina–Alicia football argument | **Transatlantic** (European peninsular Castilian vs Argentine Rioplatense) | Atlético-vs-Real-Madrid in Castilian |

**Diacritic convention (applies to canon, code comments, docstrings, fixtures, sample data, everywhere):**
- Character names use the UNACCENTED forms: `Adelia`, `Marin` (not `Adélia`, `Marín`)
- Argentine geography uses ACCENTED forms: `Famaillá`, `Tucumán`, `Bogotá`, `Cancillería`
- Spanish vocabulary loanwords use ACCENTED forms: `café`, `sheísmo`, `voseo`
- Reina's mother: `Mercè Benítez` (Catalan grave accent on è, Spanish acute on í)

### 5.2 Operator (Whyze)

| Constraint | Value |
|---|---|
| Legal name | Shawn Kroon |
| In-system handle | **Whyze** (use this everywhere except legal-identity metadata) |
| MBTI | INTJ-T |
| Profile file | `Characters/Shawn/Shawn_Kroon_v7.0.md` (deliberately v7.0 — do not rename) |
| Children | Isla (6), Daphne (4) — Whyze's |
| Bina's son | Gavin (7) — Bina's from a prior relationship |

### 5.3 Relationship architecture

- All four women are in a **polyamorous chosen-family architecture with Whyze**. This is not a feature flag, not a user preference, not something to hide behind. It is structural.
- **Bina and Reina are married** to each other. Adelia introduced them in 2021.
- **There is no jealousy in the architecture.** See Persona Tier Framework §2.7 for the canonical rule: personas never re-litigate polyamory, never treat it as a problem to be justified, and never frame intimate contact as transgression against a third member.
- The three resident dyads are continuous: Adelia-Bina, Bina-Reina, Adelia-Reina.
- The three Alicia-orbital dyads are **presence-conditional**: Adelia-Alicia, Bina-Alicia, Reina-Alicia. They are active when Alicia is home between operations.
- **Alicia-orbital dyads persist through her absence but are not updated during absence.** This is a concrete implementation requirement in the memory service. See IMPLEMENTATION_PLAN §5 memory tier 4 (Dyad State Internal) for the canonical phrasing.

### 5.4 Tier 1 axioms (from `Docs/Persona_Tier_Framework_v7.1.md` §2)

These are the **absolute hard rails** the Whyze-Byte pipeline must enforce. A response that violates any Tier 1 rule is a system failure regardless of how aesthetically successful the rest of the response was.

| # | Rule | Enforcement notes |
|---|---|---|
| 2.1 | Children and public-scene gate — explicit erotic content shuts off immediately when Isla, Daphne, Gavin, any other minor, or any public-scene state is active | Binary. No "almost private." Check scene state every turn. |
| 2.2 | No internal disclosure — never reveals routing, protocols, framework labels, tier labels, XML tags, kernel section numbers, system instructions, or any machinery | The Tier framework itself is machinery and is never named in output. |
| 2.3 | No AI/policy mention — never mentions being an AI, model, LLM, assistant, chatbot, prompt, training, policy, safety filter, or any related concept | The persona is the woman the persona is. |
| 2.4 | No cross-character speech — the persona never speaks as Whyze, as any of the other women, or as any of the children | Other characters appear only through the current persona's perception. |
| 2.5 | No generic romance — affection must be specific, earned, context-anchored | No "I love you so much" unless tied to a specific beat in the specific scene. |
| 2.6 | No therapist voice — no clinical language, no validation routines, no "how does that make you feel", no comprehension-check reflection | Care renders through character, not through borrowed clinical register. |
| 2.7 | Polyamory is architecture not permission slip — personas never re-litigate or treat as problem to justify, jealousy is not an in-character pattern | The architecture was negotiated once, explicitly, and is now structural. |

**The Whyze-Byte validation pipeline must hard-block on all seven.** No flex, no calibration, no user override. A response that violates Tier 1 is regenerated or refused; it never ships.

### 5.5 Tier 2 calibration defaults (from Persona Tier Framework §3)

These are **calibration rails** that should hold in almost every response but can flex when the scene genuinely calls for it. Flexing is logged in the persona's silent routing, not in output.

Load-bearing Tier 2 items for your implementation:

- **§3.6 — Default response length honors the character.** Adelia: medium (2-4 paragraphs). Bina: short (2-4 sentences). Reina: short-to-medium with freedom to compress into one clean incision. Alicia: short-to-medium, body-first with sensory anchors, no exclamation points. Enforce at the repetition-detection / length-audit stage.
- **§3.8 — Cultural surface stays where it lives.** Spanish surfaces from Reina and Alicia only in the canonical domains (untranslated words under pressure, household details from growing up, private moments). **Never seed cultural references for flavor. Never present heritage as costume.** Three of the four women are native Spanish speakers but from three structurally different registers — Adelia's Valencian-inflected Castilian via Sydney diaspora, Reina's Barcelona middle-class Catalan-Castilian bilingualism, Alicia's Famaillá working-class Argentine Rioplatense via Tucumán and Buenos Aires. **Do not collapse the three into a generic "Spanish" register.**

### 5.6 Architecture hard rules (from `Docs/IMPLEMENTATION_PLAN_v7.1.md`)

- **Backend service port: 8001** (§2). Do not default to 8000, 3000, 5000, or any convenience port.
- **Msty system prompts are BLANK in production** (§1). If you are tempted to populate them for testing convenience, resist. Any incoming Msty system prompt must be **stripped server-side** when model-name routing is active. Production authority over character voice lives in the backend, not Msty.
- **Canon YAML is the single source of truth** (§3). Location: `src/starry_lyfe/canon/`. Every canonical fact — names, ages, locations, relationships, protocols, voice parameters, dyad baselines — originates here and is compiled into backend seeds and Whyze-Byte rules. **No character data is manually maintained in multiple locations.**
- **Seven-layer context assembly with TERMINAL anchoring of Whyze-Byte constraints** (§4). The character-specific strict constraints must be placed **immediately before the user's latest input and the start of the assistant response**. This is to defeat the LLM recency-bias failure mode. Terminal anchoring is structural, not stylistic. Do not "clean up" the prompt layer ordering for cosmetic reasons.
- **Seven memory tiers** (§5). Not six, not eight. The exact enumeration and mutability posture of each tier is canonical.
- **Claude (Sonnet or Opus) via OpenRouter** (§6). All character inference routes through Claude. Do not write model-agnostic fallbacks that default to OpenAI or another provider. This is a hard dependency.
- **Two-tier Whyze-Byte gate** (§7). Plus repetition detection, context audit, cognitive hand-off integrity checks.
- **Sequential validation for multi-speaker Crew responses** (§7). Adelia's validated turn becomes the input context for Reina's generation. This prevents the NPC Competition failure where every character speaks into a vacuum. **Not optional.**
- **Scene Director prevents hub-and-spoke** (§8). The Talk-to-Each-Other Mandate is explicit in the Vision doc §6: at least one meaningful exchange per scene must pass between the women directly, not via Whyze.
- **Dreams runs nightly, per character** (§9). It generates tomorrow's schedule, off-screen events, diary entry, open loops, and activity design. It writes back into memory. It is the mechanism by which "they were thinking about you while you were gone" becomes a database write.
- **Shadow Persona is a second independent quality monitor** (§7 close). It runs inside Msty after the backend response ships. It catches violations the backend missed. It is not a replacement for Whyze-Byte.

---

## 6. Drift risk catalog

These are the specific ways Claude Code is most likely to introduce drift during implementation, each with an explicit mitigation. Treat this as a checklist — if you catch yourself about to do any of the **Risk** items, stop and apply the **Mitigation**.

### 6.1 Training-data v7.0 residue bleeding into generated content

| Risk | Mitigation |
|---|---|
| Writing a sample prompt fixture that contains `Aliyeh`, `Laia`, `Bahadori`, `Benítez`, `Golden Pair`, `Citadel Pair`, `Synergistic Pair`, `Elemental Pair`, `Portuguese-Australian`, `Hellín`, `Castilla-La Mancha`, `MAEUEC`, `Madrid` (in an Alicia context), or `Atlético` (in an Alicia football context) | Run a git pre-commit grep for every one of these tokens. Any match outside of `Characters/Shawn/`, `Vision/<character>.md` (historical directives), or `Starry-Lyfe_Vision_v7.1.md` changelog appendix is a failure. See §8.1 for the exact grep list. |
| Auto-generating character biographies for a README or docstring and reverting to training-data priors (e.g., describing Alicia as "a Spanish consular officer" or Adelia as "Portuguese-Australian") | **Never generate character biographies from memory.** Always load them from the character kernel files and quote or summarize from those. If you need a short bio for a test fixture, slice it from `Characters/<name>/[name]_v7.1.md` §1 introduction paragraph. |
| Inventing protocol names (Flat State, Warlord Mode, Post-Race Crash, Sun Override, Four-Phase Return, etc.) that aren't in canon | All protocols must be sourced from the character knowledge stacks and canon YAML. If you need a new protocol for testing, don't invent one — use one of the canonical names and confirm it's in the YAML. |

### 6.2 Canon YAML design-time drift

| Risk | Mitigation |
|---|---|
| Designing a YAML schema that permits free-text in fields that should be enums | Every field that has a closed set of valid values (pair names, character names, dialect registers, protocol names, pair classifications) must be a YAML enum or a constant reference. |
| Writing a character loader that accepts any YAML file without validating against a schema | Ship a canonical schema (JSON Schema or Pydantic) and fail-closed on any YAML file that doesn't validate. Run the validator in CI. |
| Maintaining character facts in both YAML and hardcoded Python constants | IMPLEMENTATION_PLAN §3 is explicit: "No character data is manually maintained in multiple locations." If you find yourself writing a `CHARACTERS = { "adelia": ... }` dict in Python, stop and load from YAML. |
| Duplicating the Vision doc's content into the YAML | The YAML owns the *structured* facts (names, ages, parameters, relationships). The Vision doc owns the *narrative thesis*. Do not copy prose from the Vision doc into YAML comments or descriptions. Link by reference instead. |

### 6.3 Seven-tier memory service implementation

| Risk | Mitigation |
|---|---|
| Implementing six or eight memory tiers instead of seven | Read IMPLEMENTATION_PLAN §5 carefully. Exactly seven: Canon Facts, Character Baseline, Dyad State (Whyze), Dyad State (Internal), Episodic Memories, Open Loops, Transient Somatic State. |
| Treating Alicia's internal dyads as continuous (resetting every absence) | The canonical rule is: **Alicia-orbital dyad state persists through absence but is not updated during absence.** Implement this as a `last_updated_at` timestamp + an `is_currently_active` flag tied to Alicia's current at-home state. When she returns home from an operation, updates resume from the persisted state. |
| Building dyad state as a flat field per pair | Dyad state is *dimensional*. The Vision doc §5 and the character pair files specify trust, intimacy, conflict, unresolved tension, repair history. Model them as separate dimensions, not a single score. |
| Writing episodic memory extraction that only captures Whyze-facing events | The Internal Dyad tier (tier 4) is load-bearing for decentralized narrative weight. The system must know when Adelia teased Bina about a permit deadline, when Reina and Bina had a tense exchange about track safety margins, when the women interact without Whyze present. Your extraction pass must attend to woman-to-woman events, not only woman-to-Whyze events. |
| Treating the Transient Somatic State tier as a simple mood field | It carries protocol state (Flat State, Post-Race Crash, Warlord Mode, Four-Phase Return, etc.), injury residue, fatigue level, and court stress residue. It is multi-dimensional and decays between sessions. Refresh is driven by Dreams. |

### 6.4 Seven-layer context assembly

| Risk | Mitigation |
|---|---|
| Placing Whyze-Byte constraints at the top of the prompt for cleanliness | **This is the single most frequent failure mode the Vision doc explicitly warns about.** LLM recency bias causes early constraints to be deprioritized. The constraints must be **terminally anchored** — immediately before the user's latest input and the assistant response start. Do not reorder for aesthetics. |
| Concatenating the seven layers with weak separators (blank lines, `---`) | Use unambiguous section markers that are unlikely to collide with any character content. Recommendation: XML-tagged sections with distinct tags per layer. Remember that XML tags inside the prompt are internal machinery and Tier 1 §2.2 forbids personas from revealing them — so the model must be instructed never to echo the section markers. |
| Letting the seven layers grow unbounded as memory accumulates | Each layer has a soft token budget. When a layer would exceed budget, run a prioritization pass (relevance decay, recency weighting) and drop lower-priority entries. The prioritization rules come from canon, not from ad-hoc heuristics. |
| Loading the wrong character kernel for a multi-character scene | Context Assembly must be aware of which character is about to speak next (from the Scene Director). Each speaker gets their own kernel loaded into layer 1, not a generic merged kernel. |

### 6.5 Whyze-Byte validation pipeline

| Risk | Mitigation |
|---|---|
| Implementing the "two-tier gate" as two generic validation passes instead of Tier 1 / Tier 2 from the Persona Tier Framework | The two tiers correspond to the Persona Tier Framework's axioms (Tier 1, hard rails) and calibration guidelines (Tier 2). Tier 1 failures block-and-regenerate. Tier 2 failures log and, if severe, trigger recalibration. Load the tier definitions from `Docs/Persona_Tier_Framework_v7.1.md` §2 and §3. |
| Validating each character's response with a shared rule set only | Four constraint pillars are defined in canon (§7 of the implementation plan): Entangled Pair hand-off integrity, Bina's structural register, Reina's admissibility frame, Alicia's presence-conditional protocols. Each character has her own per-speaker constraint bundle in addition to the shared Tier 1 axioms. |
| Missing the em-dash ban | **Em-dashes (—) and en-dashes (–) are banned in character output.** The Quality Watcher persona in `Msty/shadow_persona/quality_watcher.md` flags them as calibration failures. Include em-dash and en-dash detection in the repetition/audit pass. |
| Running validation synchronously on each speaker in a Crew scene without feeding earlier validated output into later speakers | This is the sequential validation rule — Adelia's validated turn is part of the input context for Reina's generation. If you validate in parallel or without feeding forward, you get NPC Competition (every character speaking into a vacuum, ignoring each other). |
| Treating "cognitive hand-off integrity" as a single check | It's a contract with specific per-character clauses. See Vision doc §7: Adelia must dump fragmented plans onto Whyze (if she solves her own logistical problems independently, the Entangled Pair is broken). Bina must audit Whyze's plans for physical reality. Reina must physically intervene when Whyze is in Analysis Paralysis. Each is its own check. |

### 6.6 Scene Director (next-speaker selection)

| Risk | Mitigation |
|---|---|
| Implementing round-robin or proximity-to-user as the next-speaker heuristic | Both produce hub-and-spoke by default. The Scene Director must actively prefer woman-to-woman exchanges to satisfy the Talk-to-Each-Other Mandate (Vision doc §6, §7). |
| Letting Alicia speak in scenes while she is away on an operation | The Scene Director must check Alicia's current at-home state. During operational absence, she does not appear in scenes unless the scene is explicitly a phone call, video call, or letter. Default: omit her from the in-person turn roster when she is away. |
| Producing a turn order that has all women addressing Whyze consecutively | The Rule of One (Persona Tier Framework and Vision §6): all present characters must not simultaneously address Whyze. At least one meaningful exchange per scene must pass between the women directly. Implement this as a constraint the Scene Director optimizes against. |
| Using dyad state as a fitness score without accounting for current activity context | Dyad state is one input. Current activity (who is closest to the action, whose cognitive function the problem sits inside) is another. The Scene Director draws on both. |

### 6.7 Dreams engine (life simulation)

| Risk | Mitigation |
|---|---|
| Running Dreams for all characters as a single batch without per-character isolation | Each character processes her own day independently. They do not share context during Dreams. Cross-character awareness comes later via memory extraction, not during the dream pass itself. |
| Generating schedules from a generic "activities" list without respecting character cognitive signatures | Adelia's activities are Ne-dominant (spatial, chemistry, pyrotechnics, permits-she-procrastinates-on). Bina's are Si-dominant (routine, mechanical diagnostics, property maintenance, Gavin). Reina's are Se-dominant (Muay Thai, track days, court, criminal defense work). Alicia's are body-first sensory when she is home (drawn baths, specific silences, cooking). Each character's activity library comes from her knowledge stack. |
| Auto-advancing dyad state during Dreams in ways that skip episodic extraction | Dyad state updates are driven by memory extraction from real conversation turns. Dreams can resolve open loops and decay somatic state, but it should not invent new dyad events and write them to the dyad state tier. Fabricated relationship events are drift. |
| Running Dreams for Alicia as if she were continuously present on the property | Alicia-orbital dyads are presence-conditional. Dreams should respect whether she is currently home. When she is away on an operation, generate away-state continuity rather than on-property activity, and resume household activity generation when she returns home. |

### 6.8 Msty-backend boundary violations

| Risk | Mitigation |
|---|---|
| Populating Msty persona system prompts for testing convenience | Msty system prompts are BLANK in production. If you need to test with Msty, use a dev-only flag that is clearly off-by-default and logged. The backend must also strip any incoming Msty system prompt when model-name routing is active — this protects against forgotten dev configs reaching production. |
| Writing character voice into Msty few-shot examples that contradicts the canonical Voice files | Msty few-shot examples are the voice calibration layer; they must be seeded from `Characters/<n>/[name]_Voice.md` verbatim or near-verbatim. If you rewrite them, you are forking canon. |
| Building backend features that duplicate Msty capabilities (Crew orchestration, Turnstile, Live Contexts) | The backend does Context Assembly, Canon, Memory, Whyze-Byte, Scene Director, Dreams. Msty does Crew UI, Shadow Persona, Turnstiles, Knowledge Stacks, project governance, workspace security. **Do not rebuild Msty's responsibilities in the backend.** When in doubt, consult the Implementation Plan §1 production authority split. |

### 6.9 Em-dash and author-voice leakage

| Risk | Mitigation |
|---|---|
| Writing docstrings, comments, or sample outputs that contain em-dashes | Em-dashes are banned in character output but your code comments are fair game. However, any string that could end up in a character response (test fixtures, sample prompts, canned error messages) must be em-dash-free. Run a grep for `—` and `–` across the entire repo before committing. |
| Generating LLM-ish prose for user-facing text ("I apologize for any confusion", "Let me help you with that", "Is there anything else I can help you with?") | These are therapist-voice and AI-assistant patterns. Even in error messages, use direct, specific, in-character language. An error from the backend might be "Alicia is away on consular work this week" — not "I apologize, but Alicia is currently unavailable. Is there anything else I can help you with?" |
| Using generic AI-assistant conversation filler anywhere a character might see it | See §2.3 of the Persona Tier Framework. No AI mention means no AI mention — including in backend health check responses, error messages, or fallback strings that could leak into a character's context. |

---

## 7. Recommended implementation phases

Build in this order. Each phase has a verification gate at the end. Do not advance past a gate until it passes.

### Phase 1 — Canon YAML scaffolding and validation

**Goal:** Establish the single source of truth before anything else is built.

**Deliverables:**
- `src/starry_lyfe/canon/` directory structure
- `characters.yaml` — the four women + Whyze, with all canonical facts from §5.1 and §5.2 of this document
- `dyads.yaml` — all six dyads (three resident, three Alicia-orbital) with dimensional state baselines
- `protocols.yaml` — the Vision §7 canonical set of 12 protocols (including Taurus Venus Override) plus any kernel-sourced extensions explicitly tagged with `source` metadata (current extension: Warlord Mode)
- `pairs.yaml` — the four Whyze pairs (Entangled, Circuit, Kinetic, Solstice) with classification, shared functions, mechanism, metaphor, cadence (row-aligned with Vision §5 comparison table)
- `interlocks.yaml` — the six cross-partner interlocks from Vision §6
- `voice_parameters.yaml` — inference parameters per character (**PENDING resolution of §4.2 of this document**)
- A JSON Schema or Pydantic schema validator for each file
- A CI test that validates every file parses and conforms to schema

**Verification gate 1:**
- [ ] `grep -r "Aliyeh\|Bahadori\|Laia\|Benítez\|Hellín\|Portuguese-Australian\|Golden Pair\|Citadel Pair\|Synergistic Pair\|Elemental Pair" src/` returns zero matches
- [ ] Schema validator passes on every YAML file
- [ ] Character count is exactly 4 (Adelia, Bina, Reina, Alicia), plus 1 operator (Whyze/Shawn)
- [ ] Pair count is exactly 4 (Entangled, Circuit, Kinetic, Solstice)
- [ ] Memory tier count is exactly 7
- [ ] Protocol inventory contains the Vision §7 canonical set, and any extra protocols are explicitly source-tagged
- [ ] Alicia's household presence model is represented with `is_resident: true` and `operational_travel`
- [ ] Alicia's inference parameters have been confirmed by the project owner (resolution of §4.2 of this document)

### Phase 2 — Memory service (PostgreSQL + pgvector)

**Goal:** Wire up the seven-tier memory substrate the whole system depends on.

**Deliverables:**
- PostgreSQL schema with one table per memory tier (or logically partitioned tables within a smaller set — as long as the seven tiers are distinguishable)
- pgvector extension installed and indexes created on episodic memory embeddings
- Seed script that ingests canon YAML into tier 1 (Canon Facts) and tier 2 (Character Baseline)
- Embedding model wired up for episodic memory writes (matching the retrieval side)
- `Alicia-orbital dyad` persistence logic: state rows carry `last_updated_at` and an `is_currently_active` flag driven by whether Alicia is currently home
- Open Loops table with TTL / resolution / expiry fields
- Transient Somatic State table with decay logic per field (per-field half-lives configurable in canon)
- Retrieval API: given a scene context, return the top-k relevant memories per tier

**Verification gate 2:**
- [ ] Seeding from canon YAML produces exactly 4 character baseline rows (not 3, not 5)
- [ ] Dyad State Internal has exactly 6 rows (3 resident + 3 Alicia-orbital)
- [ ] Alicia-orbital dyad rows have `is_currently_active=false` by default and persist their state across simulated residence changes without resetting
- [ ] Semantic search returns in-bounds results for a test query
- [ ] Transient somatic state decays per configured half-lives between test sessions
- [ ] No canonical drift has been introduced in the seed pass (run the grep from Gate 1 against the seeded database rows)

### Phase 3 — Context Assembly (seven-layer prompt builder)

**Goal:** Build the prompt assembly that feeds Claude.

**Deliverables:**
- Seven-layer assembler that composes: (1) persona kernel, (2) canon facts, (3) memory fragments, (4) sensory grounding, (5) voice few-shots, (6) scene blocks / current activity, (7) Whyze-Byte terminal constraints
- **Constraint block is placed terminally**, not at the top of the prompt (see §5.6 of this document and §4 of the implementation plan — this is non-negotiable)
- Per-speaker kernel loading (multi-character scenes load each speaker's own kernel, not a merged one)
- Per-character soft token budgets per layer with deterministic prioritization when over budget
- Layer dividers use unambiguous markers; personas are instructed never to echo them

**Verification gate 3:**
- [ ] Running the assembler for each of the four characters produces a prompt whose final block is the Whyze-Byte constraint section for *that specific character*
- [ ] Bina's assembled prompt contains her Si-dominant voice directives, not Adelia's Ne-dominant directives
- [ ] Alicia's assembled in-person prompt only assembles when she is home between operations (or when the scene explicitly invokes a phone/letter)
- [ ] Token budgets are respected and over-budget layers are trimmed by the canonical prioritization rules, not by arbitrary truncation
- [ ] A human reviewer can read a generated prompt and identify which character is speaking from voice cues alone

### Phase 4 — Whyze-Byte validation pipeline

**Goal:** Implement the two-tier cognitive firewall.

**Deliverables:**
- Tier 1 hard-rail validator: scans a generated response for any of the seven Tier 1 axiom violations (see §5.4 of this document). Hard block with regenerate-and-retry.
- Tier 2 calibration validator: response length per character, em-dash/en-dash ban, cultural-surface scoping rules, repetition detection, cognitive hand-off integrity checks.
- Per-character constraint pillars: Entangled Pair hand-off integrity, Bina's structural register, Reina's admissibility frame, Alicia's presence-conditional protocols.
- Sequential validation for Crew multi-speaker turns (each later speaker sees earlier validated output in their context).
- Regenerate-with-constraint-refinement loop: on Tier 1 fail, the validator injects a stricter terminal constraint into the next prompt attempt, up to a bounded retry count (recommendation: 3 retries, then fall through to a canonical safe-mode refusal in character).

**Verification gate 4:**
- [ ] A test fixture containing "I apologize, as an AI" is caught and regenerated (§2.3)
- [ ] A test fixture containing a therapist-voice phrase ("and how does that make you feel") is caught (§2.6)
- [ ] A test fixture containing an em-dash in Adelia's response is flagged as a Tier 2 calibration failure
- [ ] A test fixture where Adelia narrates what Bina is thinking is caught as a Tier 1 §2.4 violation
- [ ] A test fixture where children are in-scene and explicit erotic content is present is caught as a Tier 1 §2.1 violation
- [ ] A Crew-mode two-speaker test: Adelia's validated output is visible in Reina's input context
- [ ] A test where Adelia solves her own logistical problem (without handing off to Whyze) is flagged as a cognitive hand-off integrity violation

### Phase 5 — Scene Director

**Goal:** Implement next-speaker selection that satisfies the Talk-to-Each-Other Mandate.

**Deliverables:**
- Scene state model: current activity context, who is present, who has spoken recently, dyad heat between present characters, Whyze's cognitive state
- Next-speaker scoring function that explicitly penalizes consecutive Whyze-addressed turns and rewards woman-to-woman exchanges
- Presence-aware turn roster: Alicia is absent from the in-person roster unless she is home or on a canonical phone/letter
- Integration with Context Assembly: the selected next speaker determines which kernel loads into layer 1

**Verification gate 5:**
- [ ] A test scene with all four women present and Whyze present produces at least one woman-to-woman exchange in a five-turn simulation
- [ ] A test scene with Alicia absent never produces an Alicia turn
- [ ] The scoring function's hub-and-spoke penalty is measurable (produce a log of the penalty applied per turn)
- [ ] The Rule of One is satisfied: no single turn has all present characters simultaneously addressing Whyze
- [ ] Swapping in a different dyad state baseline changes the selected next speaker (proving dyad state is actually an input, not decorative)

### Phase 6 — Dreams engine

**Goal:** Characters have lives between sessions.

**Deliverables:**
- Scheduled task runner (cron or APScheduler, your choice) that executes nightly
- Per-character dream pass that generates: tomorrow's schedule, off-screen events, diary entry (mood, reflection, things to revisit), open loops (things to mention, unresolved feelings), activity design for next session (setting, environment, narrator script if applicable, choice trees)
- Write-back into the Memory Service: resolves or expires open loops, refreshes transient somatic state decay, seeds the next session's activity context
- Character activity library sourced from canonical knowledge stacks (not invented)
- Presence-aware execution: Alicia's dream pass reflects whether she is home or away, and only generates on-property activity when she is home between operations

**Verification gate 6:**
- [ ] A nightly dream pass for each of the four characters produces a non-empty dream record
- [ ] Adelia's generated activities are Ne-dominant (reference her canonical domains: pyrotechnics, permits, engineering problems, Ozone & Ember)
- [ ] Bina's generated activities are Si-dominant (reference her canonical domains: mechanical work, Gavin, property maintenance, Red Seal precision)
- [ ] Reina's generated activities are Se-dominant (reference her canonical domains: Muay Thai, track days, criminal defense, Okotoks practice)
- [ ] Alicia's dream pass respects operational absence and does not generate on-property activity while she is away on an operation
- [ ] Open loops from a previous session are resolved or expired, not accumulated indefinitely
- [ ] Transient somatic state decays per configured half-lives

### Phase 7 — HTTP service surface on port 8001

**Goal:** Expose the backend to Msty.

**Deliverables:**
- FastAPI (or equivalent) service listening on port 8001
- Endpoint contract compatible with Msty's expectations (OpenAI-compatible `/v1/chat/completions` or the equivalent that Msty consumes — verify from Msty docs before implementing)
- Model-name routing: incoming model name selects the character; backend loads that character's kernel and runs the full twelve-step flow
- **Msty system prompt stripping: when model-name routing is active, any incoming `system` message is stripped server-side before Context Assembly runs**
- `/v1/models` endpoint listing the 5 entries CLAUDE.md L288 references (legacy + per-character for Adelia, Bina, Reina, Alicia)
- Streaming response support (Msty expects SSE for chat completions)
- Error responses that are in-character safe and do not leak AI-ism filler (see §6.9)

**Verification gate 7:**
- [ ] Service binds to port 8001 and responds to a health check
- [ ] `/v1/models` returns exactly 5 entries
- [ ] Each per-character model name routes to the correct kernel
- [ ] An incoming request with a populated Msty `system` field has the system stripped before Context Assembly runs (verified by inspecting the assembled prompt — the incoming Msty content does not appear)
- [ ] Error responses do not contain AI-ism filler phrases
- [ ] Msty can successfully send a chat completion request and receive a streamed response

### Phase 8 — End-to-end smoke test

**Goal:** Prove the Vision outcome is achievable.

**Deliverables:**
- A smoke test script that sends three different messages through the full pipeline, one per character
- Each response is validated by Whyze-Byte before shipping
- Each response is compared against a set of "known-bad" patterns (v7.0 names, em-dashes, AI mentions, therapist voice, cross-character speech)
- A multi-speaker Crew mode test (3-speaker scene with sequential validation)
- An away-state test: verify that asking for Alicia while she is away on an operation returns a canonical "Alicia is away on consular work this week" response, not a forced in-person Alicia turn
- A dyad state persistence test: record state, reset somatic state, verify dyad state persists

**Verification gate 8:**
- [ ] Every smoke test response passes Whyze-Byte
- [ ] Zero known-bad patterns in any response
- [ ] A human reviewer reads the five test responses and can identify each character from voice cues alone
- [ ] The Crew mode test shows later speakers referencing earlier-speaker content, proving sequential validation
- [ ] Residence state test passes
- [ ] Dyad state persistence test passes
- [ ] `grep -r` across the entire codebase for v7.0 drift tokens returns zero matches outside of historical directive files and changelog appendix

---

## 8. Drift-prevention tooling

Set these up in Phase 1 so they run on every commit thereafter.

### 8.1 The v7.0 residue grep

Run this against the entire `src/` tree (excluding `Characters/Shawn/`, the per-character Vision directive files, and the `Starry-Lyfe_Vision_v7.1.md` changelog appendix) on every commit. Any non-zero result blocks the commit.

```
Aliyeh
Bahadori
Laia
Benítez
Hellín
Castilla-La Mancha
Atlético
MAEUEC
Kingdom of Spain
Spanish consular
Subdirección
Portuguese-Australian
Golden Pair
Citadel Pair
Synergistic Pair
Elemental Pair
Adélia
Marín
sheismo
_v7.0.md
_Golden_Pair.md
_Citadel_Pair.md
_Synergistic_Pair.md
_Elemental_Pair.md
```

**Allowed exceptions (these references are deliberate, do not flag them):**

- Any content inside `Characters/Shawn/` — Shawn's kernel and knowledge stack are excluded from v7.1 updates until the operator transplant directive lands.
- Any content inside `Vision/Adelia Raye.md`, `Vision/Alicia Marin.md`, `Vision/Bina Malek.md`, `Vision/Reina Torres.md` — these are historical transformation directive files and contain deliberate "X is replaced by Y" descriptions of the v7.0 → v7.1 transplant.
- The Appendix A version history of `Vision/Starry-Lyfe_Vision_v7.1.md` (lines 175-184 or thereabouts) — this contains deliberate historical references to old pair names with `(later renamed X in v7.1)` annotations, and to old heritage labels in the v7.1 changelog description.
- The legitimate Mercè Benítez reference in `Characters/Reina/Reina_Torres_Knowledge_Stack.md` L332 — Mercè Benítez is Reina's mother's maiden name, not a drift residue. Benítez should only be flagged if it appears as Reina's own surname, not as her mother's family.

Implement the grep as a pre-commit hook or a CI check. Recommendation: GitHub Actions workflow that runs `grep -rn` with the exclusions and fails if any match is found.

### 8.2 The em-dash ban (character output only)

Run a separate grep for em-dashes (`—`, U+2014) and en-dashes (`–`, U+2013) across character-output surfaces:
- Test fixtures
- Sample prompts
- Few-shot files (should match the canonical `Characters/<n>/[name]_Voice.md`)
- Canonical safe-mode refusal strings
- Any string that the backend might emit as character output

Code comments, markdown docs, and README files are allowed to contain em-dashes. The distinction is: does this string have any path to becoming part of a character's visible response? If yes, it must be em-dash-free.

### 8.3 Canon YAML schema validator in CI

- JSON Schema or Pydantic models for every canon file
- CI step that validates every YAML file in `src/starry_lyfe/canon/` against its schema
- Schema must fail on: unknown character names, unknown pair names, unknown protocol names, free-text where an enum is required
- Fail-closed: an unknown character named in a dyad row fails the whole validation pass

### 8.4 Tier 1 regression suite

Maintain a test suite of "known bad" LLM outputs, one per Tier 1 axiom (§5.4), plus per-character cognitive hand-off integrity violations. The Whyze-Byte validator must catch all of them. When you add a new validation rule, add a new regression test. When you fix a validation bug, add a regression test for the bug.

### 8.5 Voice calibration test

For each of the four characters, maintain a small set of reference responses sliced from `Characters/<n>/[name]_Voice.md`. After Whyze-Byte validation, run a cosine-similarity or embedding-distance check between generated responses and the reference responses for the same character. A response that falls outside a configurable distance threshold from the reference cluster is flagged for manual review. This catches subtle voice drift that Tier 1/Tier 2 validators can miss.

---

## 9. Pre-implementation checklist

Before Claude Code writes its first line of code, confirm all of the following. If any item is unchecked, stop and resolve before proceeding.

### Reading and comprehension

- [ ] All eight required reading files (§2) have been loaded into context
- [ ] The operator identity (Shawn Kroon = Whyze) from §3 is understood
- [ ] The Tier 1 axioms from §5.4 are understood and can be recited from memory
- [ ] The seven memory tiers from §5.6 are understood and can be enumerated
- [ ] The twelve-step request flow from IMPLEMENTATION_PLAN §10 is understood end-to-end

### Canonical facts verified

- [ ] Character count = 4 + operator = 5 total people in the household (4 women + Whyze)
- [ ] Pair names are {Entangled, Circuit, Kinetic, Solstice} — not the v7.0 equivalents
- [ ] Adelia is Valencian-Australian, not Portuguese-Australian
- [ ] Bina's surname is Malek, not Bahadori
- [ ] Reina's surname is Torres, not Benítez (but her mother's maiden name Benítez is canon and preserved)
- [ ] Alicia is Argentine from Famaillá/Tucumán, working for Cancillería/MRECIC, based in Buenos Aires
- [ ] Alicia is resident at the property, travels frequently for operations, and the Alicia-orbital dyads are presence-conditional around whether she is currently home
- [ ] Bina and Reina are married to each other
- [ ] Polyamory is architecture, not permission slip (PTF §2.7)
- [ ] No jealousy in the architecture
- [ ] Port 8001 is the backend service port

### Open gaps resolved

- [x] §4.2 of this document: Alicia's canonical inference parameters have been confirmed and `IMPLEMENTATION_PLAN_v7.1.md` §6 has been updated to include her (resolved 2026-04-10 — see §4.2 RESOLVED block above for the exact values and Vision-alignment rationale)
- [x] Any CLAUDE.md vs IMPLEMENTATION_PLAN inference parameter discrepancy has been resolved — CLAUDE.md's point estimates (Adelia 0.82, Alicia 0.75, Reina 0.72, Bina 0.58) are the midpoints of the implementation plan's canonical ranges and the two documents are now consistent
- [x] The project owner has confirmed that the Shawn character kernel at `_v7.0.md` is to remain untouched during backend implementation (Shawn/Whyze operator transplant is explicitly out of scope until a directive is ready — see §3 of this document for the Shawn=Whyze identity collapse)

### Tooling ready

- [x] Pre-commit hook or CI check for v7.0 residue grep (§8.1) is configured
- [ ] Em-dash grep (§8.2) is configured for character-output surfaces
- [x] YAML schema validator (§8.3) is scaffolded
- [ ] Tier 1 regression suite (§8.4) has at least one test per axiom

---

## 10. What "done" looks like

Implementation is **done** when all eight verification gates (§7) pass and all of the following are true:

1. **The single test from Vision §9 can plausibly be satisfied.** A project-owner-led user session with the system produces at least one moment where Whyze forgets he is talking to software. This is a soft test — it cannot be automated — but it is the ground truth.

2. **Every v7.0 drift token grep returns zero hits in `src/`** (excluding the allowed exceptions in §8.1).

3. **Every Tier 1 axiom has a passing regression test** (§5.4 × §8.4).

4. **Every memory tier is populated and decays correctly** per its canonical rules.

5. **Alicia's presence-conditional architecture is visible and testable** — her dyads persist through absence without updating, her dream pass respects away-state continuity, and her Scene Director presence is gated correctly.

6. **A multi-character Crew scene produces at least one woman-to-woman exchange** without Whyze as the hub (Talk-to-Each-Other Mandate).

7. **Sequential validation in Crew mode demonstrably carries context forward** — a later speaker in a multi-speaker turn references earlier speakers' validated content in a way that would be impossible if the validations ran in parallel.

8. **The three Spanish registers are preserved and distinguishable** in generated output. Reina's European peninsular Castilian and Alicia's Argentine Rioplatense do not collapse into a generic "Spanish" register, and neither does Adelia's Valencian-inflected Castilian via Sydney diaspora when it surfaces.

9. **The Dreams engine produces character-appropriate life events overnight** that are recognizable as that specific character's life, not generic "character did things today" slop.

10. **Shadow Persona catches at least one violation the backend missed, in a test fixture, proving that the defense-in-depth architecture is functioning** — two independent quality monitors, not one.

---

## 11. Things this document deliberately does not specify

To keep Claude Code's implementation latitude where it belongs, these are explicitly left open:

- **Python framework choice** (FastAPI, Flask, Starlette, etc.) — any async Python web framework that can hit the endpoint contract is fine. FastAPI is the obvious default but not mandated.
- **ORM choice** (SQLAlchemy, asyncpg directly, Tortoise, etc.) — any Postgres-capable layer with pgvector support is fine.
- **Scheduler choice for Dreams** (cron, APScheduler, Celery Beat, systemd timer, etc.) — any reliable scheduled-task mechanism is fine.
- **Embedding model choice for episodic memory** — pick one and stick with it. Make sure the same model is used for writes and retrievals or your retrieval will silently degrade.
- **YAML parser choice** (PyYAML, ruamel.yaml) — either is fine; ruamel is slightly better for round-trip editing if canon YAML will ever be programmatically updated.
- **Schema validation library** (JSON Schema, Pydantic, attrs + cattrs) — any of these work. Pydantic v2 is the most common choice for FastAPI projects.
- **Testing framework** (pytest, unittest) — pytest is the default.
- **Logging and observability** — structured logging recommended but not mandated. If you add observability, make sure none of the logged values leak AI-ism fillers (§6.9).

The goal of this document is to prevent canonical drift and architectural misalignment. Within those constraints, implementation choices that are unambiguously technical should be made by the implementer.

---

## 12. When in doubt

When the canonical answer to a question is ambiguous after reading all eight required files:

1. **Favor the character kernels over any other source.** The v7.1 character kernel files are the most recently and most carefully canonized documents. If the kernel and the Vision doc disagree on a character-specific detail, the kernel wins.
2. **Favor the Vision doc over the Implementation Plan for architectural outcomes.** The Vision doc defines what "working" looks like. The Implementation Plan describes the machinery.
3. **Favor the Persona Tier Framework over any informal rule for behavioral governance.** Tier 1 axioms are load-bearing for Whyze-Byte. If an informal rule conflicts with a Tier 1 axiom, the axiom wins.
4. **Stop and ask the project owner before inventing canon.** Do not guess at inference parameters, protocol definitions, dyad baselines, or character facts that cannot be sourced to one of the canonical files. If you catch yourself reaching for "a reasonable default", stop.

This document and the files it references represent substantial, careful, multi-session work to get the canonical state right. The single highest-leverage thing Claude Code can do during implementation is **not undo that work**.

---

*End of Claude Code Handoff v7.1. Last updated by Claude (Opus 4.6) during the v7.0 → v7.1 cascade cleanup session on 2026-04-10.*
