# Morning Check-In Turnstile

## Turnstile Definition

A Turnstile automates a sequence of prompts and persona responses. The morning check-in sends a single greeting and collects individual responses from the four resident characters in sequence, skipping Alicia when she is away on a consular operation.

| Entry # | Type | Content |
|---------|------|---------|
| 1 | Prompt | "Good morning." |
| 2 | Persona | Adelia (model: Adelia from configured provider) |
| 3 | Prompt (separator) | --m-- |
| 4 | Persona | Reina |
| 5 | Prompt (separator) | --m-- |
| 6 | Persona | Bina |
| 7 | Prompt (separator) | --m-- |
| 8 | Persona | Alicia *(skip when away on a consular operation)* |

## How It Works

When triggered, the Turnstile executes the sequence top to bottom:

1. Sends "Good morning." as the user message.
2. Adelia generates her response (emotional temperature, what she is working on, energy level).
3. The `--m--` separator creates a message boundary.
4. Reina generates her response (tactical status: court docket, training plans, horse check, what is on the schedule).
5. The `--m--` separator creates a message boundary.
6. Bina generates her response (logistical status: Gavin update, garage queue, property state, what is handled).
7. When Alicia is in residence, the `--m--` separator and her entry are appended. Her response is body-first and present-tense (arrival state, what her body is asking for this morning, one small observation about the room). Skip the entry entirely on days when she is not at the property.

The result is three distinct morning responses (or four when Alicia is home), one from each character in residence, triggered by a single action.

## Important Note

The Turnstile operates in a standard (non-Crew) conversation. Each persona responds independently; they do NOT see each other's prior responses. (Note: this expected behavior should be verified empirically in your Msty version. The `--m--` separator creates message boundaries, but full context isolation between persona entries is not explicitly documented in all Msty versions.) If inter-character awareness is required for the morning check-in, Crew Mode with Auto behavior is the correct tool instead. The Turnstile is appropriate when you want three independent, parallel morning snapshots rather than a coordinated group conversation.

## Usage

Trigger the Turnstile from the Msty conversation interface. It works best as the first interaction of a session, providing a snapshot of each character's current state, mood, and plans for the day.
