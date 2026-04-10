"""Token budget estimation and layer trimming."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LayerBudgets:
    """Soft token budgets per layer. Configurable per deployment."""

    kernel: int = 2000
    canon_facts: int = 500
    episodic: int = 1000
    somatic: int = 300
    voice: int = 200
    scene: int = 800
    constraints: int = 500

    @property
    def total(self) -> int:
        return (
            self.kernel + self.canon_facts + self.episodic
            + self.somatic + self.voice + self.scene + self.constraints
        )


DEFAULT_BUDGETS = LayerBudgets()


def estimate_tokens(text: str) -> int:
    """Rough token estimate: word count / 0.75.

    This is a conservative approximation for English text with Claude tokenizers.
    For production, replace with tiktoken or the model's actual tokenizer.
    """
    word_count = len(text.split())
    estimated: int = int(word_count / 0.75)
    return max(1, estimated)


def trim_to_budget(texts: list[str], budget_tokens: int) -> list[str]:
    """Trim a list of text items to fit within a token budget.

    Items are kept in order (highest priority first). Items beyond budget are dropped.
    """
    result: list[str] = []
    remaining = budget_tokens
    for text in texts:
        tokens = estimate_tokens(text)
        if tokens <= remaining:
            result.append(text)
            remaining -= tokens
        else:
            break
    return result


def trim_text_to_budget(
    text: str,
    budget_tokens: int,
    suffix: str | None = None,
) -> str:
    """Trim a single text blob to fit within a token budget.

    The suffix is included in the final budget calculation and is only appended
    when trimming actually occurs.
    """
    if estimate_tokens(text) <= budget_tokens:
        return text

    words = text.split()
    suffix_text = suffix or ""

    for cutoff in range(len(words), 0, -1):
        candidate = " ".join(words[:cutoff]).rstrip()
        if suffix_text:
            candidate = f"{candidate}\n\n{suffix_text}"
        if estimate_tokens(candidate) <= budget_tokens:
            return candidate

    # Fall back to the suffix alone if even a single word plus suffix will not fit.
    if suffix_text and estimate_tokens(suffix_text) <= budget_tokens:
        return suffix_text

    # Absolute fallback: return the first word that fits.
    for word in words:
        if estimate_tokens(word) <= budget_tokens:
            return word

    return text
