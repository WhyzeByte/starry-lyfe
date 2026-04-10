# Starry-Lyfe v7.1 Backend Architecture

Based on the v7.1 Vision document, here is the full architectural picture of the backend — what it owns, how it's structured, and how each subsystem plugs into the rest of the stack.

## 1. Operating Model: The Production Authority Split

The most important architectural decision in Starry-Lyfe is the division of labor between Msty (the conversational frontend) and the Starry-Lyfe backend (the orchestration brain). In production, the backend owns all prompt authority. The backend owns canonical YAML, kernel assembly, model parameters, memory retrieval, life-state injection, Dreams, and Whyze-Byte. Msty is the conversational platform that provides Crew orchestration, quality monitoring through Shadow Persona, scene sequencing through Turnstiles, few-shot calibration, Knowledge Stacks, project-based scene governance, environmental grounding through Live Contexts, and workspace security.

Critically, Msty persona system prompts are blank or near-blank in production so the backend remains the sole source of character authority. Any incoming Msty system prompt is stripped server-side when model-name routing is active. This is a hard boundary — there is exactly one place where character voice is authored, and it is not Msty.

## 2. The Backend Service

The backend runs as a service on Port 8001 and exposes the following responsibilities: Context Assembly (memories, life state, activity context, sensory grounding), Model Routing (Claude via OpenRouter for all character content), Whyze-Byte Pipeline (two-tier validation gate), Speaker-by-speaker sequential validation, Scene Director (next-speaker selection engine). Three sibling services round out the backend tier: Memory Service (PostgreSQL + pgvector) — Seven-tier memory architecture, Semantic search retrieval, and Life Simulation ("Dreams" Scheduled Tasks) — Nightly REM-sleep processing for all characters, Daily schedule generation, Activity design (narrator, choices, environment), Off-screen events, diary entries, open loops.

## 3. Canon: The Single Source of Truth

All character data, world facts, and constraints originate from versioned YAML. The canonical YAML source is the single source of truth. Character data, world facts, relationship rules, protocols, and constraints are defined in `src/starry_lyfe/canon/` as YAML files. Generator scripts produce backend seeds and Whyze-Byte rules from this source. No character data is manually maintained in multiple locations.

This is what enables the deduplication rule between backend-injected operator context and Msty's User Persona — there cannot be two sources of truth without drift, so YAML wins everywhere.

## 4. Context Assembly: The Seven-Layer Prompt

When a request arrives, the backend builds the system prompt that reaches Claude by composing seven distinct layers. The backend assembles the seven-layer context (kernel, canon, fragments, sensory, voice cards, scene blocks, Whyze-Byte constraints) and produces the system prompt that reaches the model.

A critical placement rule governs the last layer: The Whyze-Byte rules cannot exist as passive, background context buried at the top of the prompt. LLMs suffer from severe recency bias, causing them to deprioritize negative constraints the further they sit from the generation sequence. During context assembly, the character-specific strict constraints must be placed immediately before the user's latest input and the start of the assistant response. Terminal anchoring of constraints is structural, not stylistic.

## 5. Memory Service (PostgreSQL + pgvector)

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

## 6. Inference Layer: Claude via OpenRouter

Claude via OpenRouter is the inference engine. All character content routes through Claude (Sonnet or Opus) via OpenRouter. Claude's instruction-following fidelity makes it the strongest model for complex persona constraints.

Each character is configured with its own inference parameters at the Msty persona level (the one thing Msty *does* legitimately own per-character besides the few-shot examples), producing measurably distinct cognitive signatures from the same base model. Adelia runs hot (0.80–0.85 temperature, Think Moderately) for Ne-dominant associative leaps; Bina runs cold (0.55–0.60, Think Lightly) for Si-dominant declarative steadiness; Reina runs middle (0.70–0.75, Think Lightly) with high presence penalty for Se-dominant tactical motion; Alicia runs middle-warm (0.73–0.78, Think Lightly) with low frequency penalty for Se-dominant somatic co-regulation, producing body-first present-tense output that returns to breath, weight, and temperature as sustained anchors rather than reaching for verbal analysis. The combination of temperature spread, sampling parameters, and thinking effort produces four measurably distinct cognitive signatures from the same underlying model. In a Crew conversation, this four-way differentiation creates natural voice contrast before the system prompt even activates.

## 7. The Whyze-Byte Validation Pipeline

Generated responses do not stream straight back to Msty — they pass through a server-side validation gate first. The pipeline performs two-tier gate, repetition detection, context audit, cognitive hand-off integrity checks. For multi-character scenes, For multi-speaker responses in Crew mode, sequential validation ensures later speakers see earlier validated output — meaning Adelia's validated turn becomes the input context for Reina's generation, preventing the NPC Competition collapse where every character speaks into a vacuum.

The pipeline enforces the four constraint pillars defined in canon (Entangled Pair hand-off integrity, Bina's structural register, Reina's admissibility frame, Alicia's operational-presence protocols). After the response leaves the backend, Msty's Shadow Persona acts as a *second*, independent quality monitor that runs inside the Msty client and surfaces violations the backend missed.

## 8. Scene Director (Crew Orchestration)

The Scene Director is the next-speaker selection engine for multi-character scenes. While Msty provides the Crew Conversation UI and the manual response mode, the backend's Scene Director is what determines which character has narrative weight at any given moment, drawing on dyad state, current activity context, and the Talk-to-Each-Other Mandate to avoid the hub-and-spoke pattern where Whyze becomes the sole conversational anchor.

## 9. Dreams Engine (Life Simulation)

The Dreams engine is the offline batch process that gives the characters lives between sessions. The Dreams scheduled tasks run nightly as a batch process. They function like REM sleep; each character processes their day. For each character, the system generates tomorrow's schedule, off-screen events, diary entry (mood, reflection, things to revisit), open loops (things to mention, unresolved feelings), and activity design for the next session (setting, environment, narrator script, choice trees). Characters may reconsider something they said, want to revisit an unresolved moment, or develop new thoughts overnight.

Dreams writes back into the Memory Service: it resolves or expires open loops, refreshes transient somatic state decay, and seeds the next session's activity context. It is the mechanism by which "they were thinking about you while you were gone" stops being a metaphor and becomes a database write.

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

## Architectural Summary

Layered top-down, the backend looks like this:

- **Canon layer** — versioned YAML in `src/starry_lyfe/canon/`, the immutable source of truth
- **Generation layer** — scripts that compile YAML into backend seeds and Whyze-Byte rules
- **Memory layer** — PostgreSQL + pgvector with seven explicit memory tiers
- **Context assembly layer** — seven-layer prompt builder with terminal constraint anchoring
- **Routing layer** — Claude (Sonnet/Opus) via OpenRouter with per-character inference parameters
- **Validation layer** — two-tier Whyze-Byte pipeline with sequential multi-speaker gating
- **Orchestration layer** — Scene Director for next-speaker selection in Crew mode
- **Simulation layer** — nightly Dreams batch process for life continuity and open-loop resolution
- **Service surface** — HTTP service on port 8001, consumed by Msty as the conversational frontend

The architecture's central thesis is that the LLM is too unreliable to be trusted with character authority on its own. Voice integrity, memory continuity, and constraint enforcement all live *outside* the model — in YAML, in pgvector, in the Whyze-Byte validator, in the Dreams engine — and only the final assembled prompt and the final validated response touch Claude. Msty provides the frontend, the per-character inference knobs, and a second independent quality monitor (Shadow Persona), but it does not own a single character's voice in production.