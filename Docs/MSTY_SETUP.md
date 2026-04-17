# Msty Studio Configuration Guide

**Version:** 1.0.0
**Date:** 2026-04-17
**Backend:** Starry-Lyfe v7 on PC `192.168.1.93`, port `8001`
**Audience:** the operator (Whyze) configuring Msty Studio on a different machine on the LAN.

This guide walks you through setting up Msty Studio on a remote PC to talk to the Starry-Lyfe backend running at `http://192.168.1.93:8001`. End state: five Personas (Adelia, Bina, Reina, Alicia, Shawn) plus optional Crew Conversations that route to your local backend.

> If you are setting up Starry-Lyfe itself (running the API + Dreams daemon), see `Docs/OPERATOR_GUIDE.md` §1 first. **This guide assumes the backend is already up on `192.168.1.93:8001`.**

---

## 1. Pre-flight on the backend PC (192.168.1.93)

Before you touch Msty, make sure the backend is reachable from the LAN.

### 1.1 Confirm the API is bound to all interfaces

Your `.env` on `192.168.1.93` must have:

```
STARRY_LYFE__API__HOST=0.0.0.0
STARRY_LYFE__API__PORT=8001
STARRY_LYFE__API__API_KEY=<choose-a-strong-value>
```

`0.0.0.0` (not `127.0.0.1`) is what makes the API reachable from other machines. Pick an `API_KEY` value you'll paste into Msty later — any non-empty string works.

### 1.2 Open port 8001 on the Windows firewall

On `192.168.1.93`, in an **elevated** PowerShell:

```powershell
New-NetFirewallRule -DisplayName "Starry-Lyfe API (8001)" `
  -Direction Inbound `
  -Protocol TCP `
  -LocalPort 8001 `
  -Action Allow `
  -Profile Private
```

Use `-Profile Private` if your LAN is the Private network in Windows. If your LAN is classified as Public, use `-Profile Public` (and consider re-classifying — `Get-NetConnectionProfile`).

### 1.3 Restart the API after env changes

```powershell
.venv\Scripts\python -m starry_lyfe.api.main
```

Leave this running in a terminal window. (Or run it as a Windows service / scheduled task if you prefer.)

### 1.4 Smoke-test from the Msty PC

From your Msty PC, open a terminal and run:

```bash
# Liveness — should return JSON {"status":"alive"} or similar
curl http://192.168.1.93:8001/health/live

# Readiness — should return 200 if R5 + BD-1 are reachable from the backend
curl http://192.168.1.93:8001/health/ready

# Models registry — confirms the backend exposes the persona model IDs
curl http://192.168.1.93:8001/v1/models
```

The `/v1/models` response should show **five entries**: `starry-lyfe`, `adelia`, `bina`, `reina`, `alicia`. If you get a connection-refused or a timeout, fix the firewall / host binding before continuing — Msty Studio cannot rescue a network-level fault.

### 1.5 Auth a real chat call from the Msty PC

```bash
curl -N http://192.168.1.93:8001/v1/chat/completions \
  -H "X-API-Key: <your-key>" \
  -H "Content-Type: application/json" \
  -d '{"model":"adelia","stream":true,"messages":[{"role":"user","content":"Test from Msty PC."}]}'
```

You should see a stream of `data: {...}` chunks ending with `data: [DONE]`. **If this fails, Msty Studio will fail too.** Resolve the curl call first.

---

## 2. Auth note — X-API-Key vs Authorization Bearer

The Starry-Lyfe backend authenticates **only** via the custom header `X-API-Key`. It does NOT accept `Authorization: Bearer <key>` (the standard OpenAI auth shape).

Most OpenAI-compatible clients (including Msty) default to Bearer auth. **You must configure Msty's provider to send a custom `X-API-Key` header.** Two ways to do this in Msty Studio depending on the version:

- **Newer Msty Studio versions:** the custom OpenAI-compatible provider has a "Custom Headers" or "Additional Headers" field under the model provider's advanced settings. Add a header with name `X-API-Key` and value `<your-key>`. If Msty also requires the standard "API Key" field to be non-empty, paste anything (e.g., `unused`) — the backend ignores Bearer-style auth.
- **Older Msty Studio versions without a custom-header field:** you have two workarounds:
  1. Run a small reverse proxy on the Msty PC (e.g., `nginx` or `caddy`) that translates `Authorization: Bearer <key>` → `X-API-Key: <key>` before forwarding to `192.168.1.93:8001`. Msty then talks to the proxy.
  2. Add Bearer-token support to the backend (a one-line change in `src/starry_lyfe/api/endpoints/chat.py::_enforce_api_key` to accept either header). This is operational work outside the architectural track.

The rest of this guide assumes the **custom-header path** works.

---

## 3. Msty Studio: add the model provider

These steps are written for Msty Studio's "Local AI / Custom Provider" workflow. UI labels may shift between Msty versions; the important fields are the same.

### 3.1 Create a custom OpenAI-compatible provider

1. Open Msty Studio.
2. **Settings → Model Providers → Add Provider** (or whatever your version calls it).
3. Choose **"Custom (OpenAI-compatible)"** as the provider type.
4. Fill in:

   | Field | Value |
   |---|---|
   | **Provider name** | `Starry-Lyfe` (whatever you want to see in lists) |
   | **Base URL** | `http://192.168.1.93:8001/v1` |
   | **API Key** | `<your-key>` (the value of `STARRY_LYFE__API__API_KEY` on the backend PC) |
   | **Auth header** | If you can choose: select "Custom" and use `X-API-Key`. Otherwise see §2 |
   | **Custom Headers** | Add `X-API-Key: <your-key>` here if Msty's API Key field maps to Bearer |
   | **Streaming** | Enabled (SSE) |
   | **Verify SSL** | Off (LAN HTTP) |

5. **Test the connection.** Msty should be able to fetch the models registry. If it shows 5 models (`starry-lyfe`, `adelia`, `bina`, `reina`, `alicia`), the provider is wired correctly.

### 3.2 Models the backend exposes

After the provider is registered, Msty knows about these models:

| Model ID | Routes to | Purpose |
|---|---|---|
| `starry-lyfe` | Configured default character (`adelia` in the shipped `.env.example`) | Legacy compatibility model id; treat as "default character" |
| `adelia` | Adelia Raye | Production Persona model id |
| `bina` | Bina Malek | Production Persona model id |
| `reina` | Reina Torres | Production Persona model id |
| `alicia` | Alicia Marin | Production Persona model id |

`shawn` is not currently exposed by the backend. See §6 for what to do.

---

## 4. Per-character Persona setup

Repeat the steps below **once per woman** (Adelia, Bina, Reina, Alicia). The configuration is identical except for the `Name` and `Model ID` fields.

### 4.1 Adelia Raye

1. **Persona Studio → New Persona.**
2. Fill in:

   | Field | Value |
   |---|---|
   | **Persona name** | `Adelia Raye` |
   | **Model provider** | `Starry-Lyfe` (the provider you created in §3.1) |
   | **Model** | `adelia` |
   | **System Prompt Mode** | `Replace` (this is load-bearing — see §7) |
   | **System Prompt** | (leave blank — see §7) |
   | **Streaming** | Enabled |
   | **Temperature, top_p, frequency_penalty, presence_penalty** | Leave Msty defaults; the backend supplies per-character inference parameters in the assembled prompt body. Msty-side knobs are ignored by the upstream LLM. |
   | **Max tokens** | Whatever Msty defaults to (typically 4096 or higher) |

3. Save.

### 4.2 Bina Malek

Same as §4.1 but:

- **Persona name:** `Bina Malek`
- **Model:** `bina`

### 4.3 Reina Torres

Same as §4.1 but:

- **Persona name:** `Reina Torres`
- **Model:** `reina`

### 4.4 Alicia Marin

Same as §4.1 but:

- **Persona name:** `Alicia Marin`
- **Model:** `alicia`

> **Alicia caveat:** Alicia travels for operations as a canonical fact. When she is "away" (per Tier 8 `life_states`), the backend will reject in-person scenes with `AliciaAwayContradictionError` (HTTP 400). If Msty surfaces "Bad Request" errors when chatting Alicia, she's away and the scene needs to be remote (mention "phone", "letter", or "video_call" in the user message). See `OPERATOR_GUIDE.md` §10.5.

### 4.5 Smoke-test each Persona

For each Persona, send one message: *"Test from Msty."* Confirm:

1. The reply streams (you see characters appearing, not a single dump after a delay).
2. The voice sounds character-appropriate (Adelia warm-buoyant, Bina precise-grounded, Reina tactical-direct, Alicia bright-mobile).
3. No `WHYZE_BYTE_FAIL` chunk in the response (terminal validation didn't trip).
4. On the backend, `tail` the logs for `request_received` and `context_assembled` — both should fire per request.

If any Persona fails the smoke test, see §8 Troubleshooting.

---

## 5. Crew Conversation setup

Crew Conversations let multiple personas respond in sequence to a single user turn. The backend handles next-speaker selection and per-speaker validation.

### 5.1 Create a Crew

1. **Persona Studio → New Crew** (or "Group Chat" / "Conversation Group" depending on Msty version).
2. Add the personas you want in the crew. Examples:
   - **The Whole House:** Adelia + Bina + Reina (Alicia adds when home)
   - **Married Pair:** Bina + Reina
   - **Adelia + Bina:** the two most-frequent co-presences
3. **Crew System Prompt:** leave blank.
4. **Endpoint / model provider:** the same `Starry-Lyfe` provider from §3.1.

### 5.2 How Crew expansion is triggered

The backend expands into multiple speakers when **either**:

- The user message ends with `/all`, OR
- There are ≥2 canonical women in the parsed roster AND ≥1 prior persona response in the conversation.

If you want all crew members to weigh in on a single message, append `/all` to the user message. Otherwise the backend may pick a single speaker based on the Talk-to-Each-Other Mandate scoring.

### 5.3 Crew speaker cap

The backend caps the number of speakers per turn at `STARRY_LYFE__API__CREW_MAX_SPEAKERS` (default `3`). Each speaker is rendered inline as `**Name:**\n\n<text>` with a blank line between speakers. You'll see attribution markers in the streamed response.

---

## 6. Shawn (the operator) — current limitation + workaround

**Shawn is not currently a routable Persona** in the backend. Today's `/v1/models` returns 5 entries: `starry-lyfe`, `adelia`, `bina`, `reina`, `alicia` — Shawn is missing.

Reason: the backend's `CharacterID` enum (`src/starry_lyfe/canon/schemas/enums.py:22`) only includes the four women. Shawn exists in canon as `Characters/shawn_kroon.yaml` (the operator's identity surface) but the API has no character-routing path that resolves `model: shawn`. A request with `model: shawn` falls through to the configured default (`adelia`).

You have three options:

### 6.1 Skip Shawn (recommended for now)

Don't create a Shawn Persona. Shawn is the human at the keyboard — the four women's responses are *to Shawn*. Configuring a "Shawn Persona" that talks back to Shawn doesn't match the canonical model.

### 6.2 Placeholder Shawn Persona that routes to `starry-lyfe`

If you want a slot in Persona Studio for Shawn (cosmetic — for naming consistency in your UI), create one that points at the `starry-lyfe` legacy model ID:

| Field | Value |
|---|---|
| **Persona name** | `Shawn (operator placeholder)` |
| **Model** | `starry-lyfe` |
| **System Prompt Mode** | `Replace` |
| **System Prompt** | blank |

Be aware: this Persona will route to whichever character is set as `STARRY_LYFE__API__DEFAULT_CHARACTER` (default `adelia`). It is **not** speaking as Shawn.

### 6.3 Add `shawn` to the backend's character routing

This is the only way to make Msty's `model: shawn` field actually return Shawn-perspective output. It requires backend changes:

1. Add `SHAWN = "shawn"` to `CharacterID` in `src/starry_lyfe/canon/schemas/enums.py`.
2. Update `_assert_complete_character_keys` callers to include shawn in their per-character maps (kernel paths, voice paths, budget scaling, pair mapping, prose banks, constraint pillars). This is what `_assert_complete_character_keys` enforces at module-import time.
3. Decide what an "as Shawn" assembled prompt looks like — Shawn's rich YAML carries his identity but no `pair_architecture` block in the same shape as the women.
4. Add Shawn to the test suite (especially the Phase H regression bundle and the fidelity rubrics).

This is a discrete future-phase scope item, not a flip-the-switch change. Until it ships, skip Shawn or use the `starry-lyfe` placeholder.

---

## 7. Why "System Prompt Mode = Replace, blank" matters

This is the single most important Msty setting. Per **AD-001** (architectural decision recorded in `Docs/ARCHITECTURE.md` §21):

> The backend is the sole voice authority. Msty Persona system prompt is `Replace`-mode empty in production.

What that means concretely:

- The full character voice — kernel, soul essence, pair callbacks, soul cards, voice exemplars, scene context, terminal Whyze-Byte constraints — comes from the backend's 7-layer prompt assembler.
- Anything Msty puts into the system prompt **competes** with that assembled prompt. Even short directives like "Be helpful" or "Respond as Adelia" will fight the canonical voice and produce drift.
- `Replace` mode tells Msty to send only what you typed (which is nothing) instead of merging with a Msty-default system prompt.

If you set **Append** mode or fill the **System Prompt** field, the responses will degrade. Symptoms include character voice flattening, "As an AI…" breaks, refusal of canonical content, or generic chatbot register. If you see those symptoms, check this setting first.

---

## 8. Troubleshooting

### 8.1 "Connection refused" / "Cannot reach host"

- The backend isn't running, OR
- `STARRY_LYFE__API__HOST` is `127.0.0.1` instead of `0.0.0.0`, OR
- Windows firewall is blocking inbound 8001.

Re-run the §1.4 curl smoke test from the Msty PC. If curl can't reach the backend either, fix the network layer; Msty cannot help.

### 8.2 "401 Unauthorized" on every Msty request

The `X-API-Key` header isn't being sent (Msty is using Bearer instead). Re-check §3.1 — the custom header must be `X-API-Key`, not `Authorization`. If your Msty version doesn't support custom headers, see §2 for the proxy workaround.

### 8.3 Msty connects but `/v1/models` shows 0 models

The auth check is failing silently — Msty got a 200 from `/health/live` (no auth required) but `/v1/models` is also unauthenticated. If 0 models, more likely your provider's Base URL is wrong. Confirm it ends with `/v1` (e.g., `http://192.168.1.93:8001/v1`).

### 8.4 Chat hangs forever

Streaming is disabled in your Msty provider settings, or your client doesn't recognize SSE chunks. Re-enable streaming in §3.1.

### 8.5 First chunk arrives, then nothing

The backend is producing output but the BD-1 upstream provider (OpenRouter / Anthropic) hit a circuit breaker or timeout mid-stream. Check the backend logs for `bdone_circuit_open` or `upstream_stream_failed`. See `OPERATOR_GUIDE.md` §10.1.

### 8.6 Wrong character is responding

Most likely your Persona's **Model** field is set to the Msty UI's display name instead of the backend model ID. The model field must be exactly one of: `adelia` / `bina` / `reina` / `alicia` / `starry-lyfe` (lowercase, no spaces). If Msty has a dropdown after registering the provider, use it; don't type the name manually.

### 8.7 `WHYZE_BYTE_FAIL` chunk in the response

The backend's Whyze-Byte validator caught a Tier-1 failure (AI-ism, framework leak, XML tag bleed, prompt-marker echo, etc.). The response was streamed up to the failure point but the validator refused to certify it. This is the system protecting voice integrity. See `OPERATOR_GUIDE.md` §4.2 (`whyze_byte_validated` log event) for the violation detail.

### 8.8 `AliciaAwayContradictionError` (HTTP 400) on Alicia chats

Alicia is on operations per Tier 8 `life_states.is_away=true`. Either her travel has been recorded (a Dreams nightly pass set the flag), or her residency is mis-configured. See `OPERATOR_GUIDE.md` §10.5 for the resolution path.

### 8.9 Crew Conversation only produces one speaker

The backend's crew detection needs `/all` at the end of the user message OR a roster of ≥2 canonical women plus ≥1 prior persona response. Add `/all` to test crew expansion explicitly.

### 8.10 Msty shows the response but the character voice feels flat / generic

Almost always: the System Prompt Mode is wrong. Re-check §7. Set every Persona to `Replace` mode with an empty system prompt.

---

## 9. Summary checklist

Use this as a deployment dry-run before declaring the Msty integration complete.

- [ ] Backend `.env` has `STARRY_LYFE__API__HOST=0.0.0.0` and a non-empty `API_KEY`.
- [ ] Windows firewall on the backend PC allows inbound TCP 8001.
- [ ] Backend API service is running (`.venv\Scripts\python -m starry_lyfe.api.main`).
- [ ] From the Msty PC, `curl http://192.168.1.93:8001/health/ready` returns 200.
- [ ] From the Msty PC, the curl smoke test from §1.5 streams a real chat completion.
- [ ] Msty Studio has a custom OpenAI-compatible provider named `Starry-Lyfe` with base URL `http://192.168.1.93:8001/v1` and an `X-API-Key` custom header set to your API key.
- [ ] The provider's models list shows 5 entries.
- [ ] **Persona: Adelia Raye** — model `adelia`, System Prompt Mode `Replace`, blank prompt.
- [ ] **Persona: Bina Malek** — model `bina`, same settings.
- [ ] **Persona: Reina Torres** — model `reina`, same settings.
- [ ] **Persona: Alicia Marin** — model `alicia`, same settings.
- [ ] **Shawn:** intentional skip per §6.1, OR placeholder per §6.2, OR future backend work per §6.3.
- [ ] Each woman's Persona returns a streaming response with character-appropriate voice on a smoke-test message.
- [ ] (Optional) At least one Crew Conversation with `/all` produces multi-speaker output with `**Name:**` attribution.

When every box is checked, the Msty integration is production-ready.

---

## 10. Where to look next

- **`Docs/OPERATOR_GUIDE.md`** — full backend operator manual: log events, Dreams operations, Phase 10.7 QA workflow, troubleshooting recipes, backup/restore.
- **`Docs/ARCHITECTURE.md`** — top-down as-built reference for the backend.
- **`CLAUDE.md` §16** — the operator axioms (no jealousy, activity distribution, character integrity rules) that govern how the Personas should behave once connected.
