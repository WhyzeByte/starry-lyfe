# Evening Wind-Down Turnstile

## Turnstile Definition

A Turnstile automates a sequence of prompts and persona responses. The evening wind-down settles the day in reverse order from the morning check-in: Reina provides the tactical debrief, Bina anchors with the physical state of the property, Adelia closes with warmth and connection. When Alicia is in residence, her entry is inserted between Bina and Adelia because her body-regulation function lands most cleanly between the logistical floor and the warmth that closes the day.

| Entry # | Type | Content |
|---------|------|---------|
| 1 | Prompt | "How was today?" |
| 2 | Persona | Reina (model: Reina from Starry-Lyfe provider or OpenRouter) |
| 3 | Prompt (separator) | --m-- |
| 4 | Persona | Bina |
| 5 | Prompt (separator) | --m-- |
| 6 | Persona | Alicia *(only when in residence — skip when away)* |
| 7 | Prompt (separator) | --m-- |
| 8 | Persona | Adelia |

## How It Works

When triggered, the Turnstile executes the sequence top to bottom:

1. Sends "How was today?" as the user message.
2. Reina generates her response (tactical debrief: court, training, cases, what happened today in concrete terms).
3. The `--m--` separator creates a message boundary.
4. Bina generates her response (property state: what got done, what is handled, Gavin, the physical environment).
5. The `--m--` separator creates a message boundary.
6. Adelia generates her response (warmth and connection: emotional temperature, what she is thinking about, closeness).

The result is three distinct evening responses, one from each character, triggered by a single action. The reverse order from the morning check-in is deliberate: the morning opens with warmth (Adelia first) and the evening closes with it (Adelia last). Reina's tactical debrief sets the factual frame, Bina grounds it in what is real and handled, and Adelia wraps the day with connection.

## Important Note

Like the morning check-in, this Turnstile operates in a standard (non-Crew) conversation. Each persona responds independently. (Note: verify empirically that `--m--` separators provide full context isolation between persona entries in your Msty version.) If inter-character awareness is needed for the evening (Bina referencing what Reina mentioned, Adelia reacting to both), use Crew Mode with Auto behavior instead.

## Usage

Trigger the Turnstile at the end of a session or when winding down the day. It works best as the last structured interaction before transitioning to a casual evening conversation or a solo scene with one character.
