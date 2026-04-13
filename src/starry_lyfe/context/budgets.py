"""Token budget estimation, markdown-block-aware trimming, and layer budgets."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum


class BlockType(StrEnum):
    """Markdown block types recognized by the structure-preserving trimmer."""

    HEADING = "heading"
    PARAGRAPH = "paragraph"
    BULLET_LIST = "bullet_list"
    NUMBERED_LIST = "numbered_list"
    CODE_BLOCK = "code_block"
    BLOCKQUOTE = "blockquote"
    HORIZONTAL_RULE = "horizontal_rule"


@dataclass
class MarkdownBlock:
    """A single parsed markdown block with type, content, and metadata."""

    block_type: BlockType
    text: str
    heading_level: int = 0
    preserved: bool = False
    estimated_tokens: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self.estimated_tokens = estimate_tokens(self.text)


@dataclass
class LayerBudgets:
    """Soft token budgets per layer. Configurable per deployment."""

    kernel: int = 6000
    canon_facts: int = 600
    episodic: int = 1200
    somatic: int = 500
    voice: int = 900
    scene: int = 1200
    constraints: int = 900

    @property
    def total(self) -> int:
        return (
            self.kernel + self.canon_facts + self.episodic
            + self.somatic + self.voice + self.scene + self.constraints
        )


DEFAULT_BUDGETS = LayerBudgets()

CHARACTER_KERNEL_BUDGET_SCALING: dict[str, float] = {
    "adelia": 1.05,
    "bina": 1.20,
    "reina": 1.15,
    "alicia": 0.85,
}


def resolve_kernel_budget(character_id: str, base_budget: int = DEFAULT_BUDGETS.kernel) -> int:
    """Resolve per-character kernel budget with scaling factor."""
    scale = CHARACTER_KERNEL_BUDGET_SCALING.get(character_id, 1.0)
    return int(base_budget * scale)


@dataclass
class SceneBudgetProfile:
    """Budget allocation profile for different scene types."""

    name: str
    kernel: int
    scene: int
    voice: int

    @property
    def total(self) -> int:
        return (
            self.kernel + DEFAULT_BUDGETS.canon_facts + DEFAULT_BUDGETS.episodic
            + DEFAULT_BUDGETS.somatic + self.voice + self.scene
            + DEFAULT_BUDGETS.constraints
        )


SCENE_PROFILES: dict[str, SceneBudgetProfile] = {
    "default": SceneBudgetProfile(name="default", kernel=6000, scene=1200, voice=900),
    "pair_intimate": SceneBudgetProfile(name="pair_intimate", kernel=8000, scene=800, voice=700),
    "multi_woman_group": SceneBudgetProfile(name="multi_woman_group", kernel=5500, scene=1800, voice=1000),
    "solo": SceneBudgetProfile(name="solo", kernel=7000, scene=800, voice=900),
}


def get_scene_profile(profile_name: str = "default") -> SceneBudgetProfile:
    """Get a scene budget profile by name. Stub selector — always returns named profile."""
    return SCENE_PROFILES.get(profile_name, SCENE_PROFILES["default"])

_HEADING_RE = re.compile(r"^(#{1,6})\s")
_HR_RE = re.compile(r"^(?:---+|___+|\*\*\*+)\s*$")
_BULLET_RE = re.compile(r"^[\-*+]\s")
_NUMBERED_RE = re.compile(r"^\d+[.)]\s")
_BLOCKQUOTE_RE = re.compile(r"^>")
_CODE_FENCE_RE = re.compile(r"^```")
_PRESERVE_RE = re.compile(r"^\s*<!--\s*PRESERVE\s*-->\s*$")

_DROP_TIERS: list[set[BlockType]] = [
    {BlockType.HORIZONTAL_RULE},
    {BlockType.PARAGRAPH},
    {BlockType.BULLET_LIST, BlockType.NUMBERED_LIST},
    {BlockType.BLOCKQUOTE},
    {BlockType.CODE_BLOCK},
]


def _strip_preserve_markers(text: str) -> str:
    """Remove <!-- PRESERVE --> markers from output text."""
    if "<!-- PRESERVE -->" not in text:
        return text
    lines = text.split("\n")
    return "\n".join(line for line in lines if not _PRESERVE_RE.match(line.strip())).strip()


def estimate_tokens(text: str) -> int:
    """Rough token estimate: word count / 0.75.

    Conservative approximation for English text with Claude tokenizers.
    For production, replace with tiktoken or the model's actual tokenizer.
    """
    word_count = len(text.split())
    estimated: int = int(word_count / 0.75)
    return max(1, estimated)


def parse_markdown_blocks(text: str) -> list[MarkdownBlock]:
    """Parse markdown text into a flat list of typed blocks.

    Handles headings, paragraphs, bullet lists, numbered lists, code
    fences, blockquotes, horizontal rules, and <!-- PRESERVE --> markers.
    The PRESERVE marker annotates the next content block as protected
    from trimming and is stripped from the block list itself.
    """
    lines = text.split("\n")
    blocks: list[MarkdownBlock] = []
    current_lines: list[str] = []
    in_code_fence = False
    preserve_next = False

    def _flush() -> None:
        nonlocal preserve_next
        if not current_lines:
            return
        chunk = "\n".join(current_lines)
        if not chunk.strip():
            current_lines.clear()
            return
        block = _classify_chunk(chunk, preserve_next)
        blocks.append(block)
        preserve_next = False
        current_lines.clear()

    for line in lines:
        stripped = line.strip()

        if _CODE_FENCE_RE.match(stripped):
            if in_code_fence:
                current_lines.append(line)
                block = MarkdownBlock(
                    block_type=BlockType.CODE_BLOCK,
                    text="\n".join(current_lines),
                    preserved=preserve_next,
                )
                blocks.append(block)
                preserve_next = False
                current_lines = []
                in_code_fence = False
                continue
            _flush()
            current_lines = [line]
            in_code_fence = True
            continue

        if in_code_fence:
            current_lines.append(line)
            continue

        if _PRESERVE_RE.match(line):
            _flush()
            preserve_next = True
            continue

        if not stripped:
            _flush()
            continue

        if _HEADING_RE.match(stripped):
            _flush()
            level = len(_HEADING_RE.match(stripped).group(1))  # type: ignore[union-attr]
            blocks.append(MarkdownBlock(
                block_type=BlockType.HEADING,
                text=line,
                heading_level=level,
                preserved=preserve_next,
            ))
            preserve_next = False
            continue

        if _HR_RE.match(stripped):
            _flush()
            blocks.append(MarkdownBlock(
                block_type=BlockType.HORIZONTAL_RULE,
                text=line,
                preserved=preserve_next,
            ))
            preserve_next = False
            continue

        current_lines.append(line)

    if in_code_fence and current_lines:
        blocks.append(MarkdownBlock(
            block_type=BlockType.CODE_BLOCK,
            text="\n".join(current_lines),
            preserved=preserve_next,
        ))
    else:
        _flush()

    return blocks


def _classify_chunk(text: str, preserved: bool) -> MarkdownBlock:
    """Classify a non-heading, non-HR chunk of contiguous lines."""
    first_line = ""
    for line in text.split("\n"):
        if line.strip():
            first_line = line.strip()
            break

    if _BULLET_RE.match(first_line):
        return MarkdownBlock(
            block_type=BlockType.BULLET_LIST, text=text, preserved=preserved,
        )
    if _NUMBERED_RE.match(first_line):
        return MarkdownBlock(
            block_type=BlockType.NUMBERED_LIST, text=text, preserved=preserved,
        )
    if _BLOCKQUOTE_RE.match(first_line):
        return MarkdownBlock(
            block_type=BlockType.BLOCKQUOTE, text=text, preserved=preserved,
        )
    return MarkdownBlock(
        block_type=BlockType.PARAGRAPH, text=text, preserved=preserved,
    )


def _total_block_tokens(blocks: list[MarkdownBlock]) -> int:
    """Estimate total tokens across all blocks plus inter-block whitespace."""
    if not blocks:
        return 0
    text_tokens = sum(b.estimated_tokens for b in blocks)
    join_overhead = len(blocks) - 1
    return text_tokens + join_overhead


def _reassemble_blocks(blocks: list[MarkdownBlock]) -> str:
    """Reassemble blocks into markdown text with blank-line separators."""
    return "\n\n".join(b.text for b in blocks)


def _find_last_droppable_heading(
    blocks: list[MarkdownBlock],
    level: int,
) -> int | None:
    """Find the index of the last heading at the given level that is droppable."""
    for i in reversed(range(len(blocks))):
        b = blocks[i]
        if (
            b.block_type == BlockType.HEADING
            and b.heading_level == level
            and not b.preserved
        ):
            owned_blocks = _blocks_owned_by_heading(blocks, i)
            if not any(blocks[j].preserved for j in owned_blocks):
                return i
    return None


def _blocks_owned_by_heading(blocks: list[MarkdownBlock], heading_idx: int) -> list[int]:
    """Return indices of blocks owned by the heading at heading_idx.

    A heading "owns" all subsequent blocks until the next heading of the
    same or higher (lower number) level, or end of list.
    """
    heading = blocks[heading_idx]
    owned = [heading_idx]
    for j in range(heading_idx + 1, len(blocks)):
        if (
            blocks[j].block_type == BlockType.HEADING
            and blocks[j].heading_level <= heading.heading_level
        ):
            break
        owned.append(j)
    return owned


_DROPPABLE_CONTENT: set[BlockType] = {
    BlockType.PARAGRAPH,
    BlockType.BULLET_LIST,
    BlockType.NUMBERED_LIST,
    BlockType.BLOCKQUOTE,
    BlockType.CODE_BLOCK,
}


def _trim_blocks_to_budget(
    blocks: list[MarkdownBlock],
    budget: int,
) -> list[MarkdownBlock]:
    """Apply the spec drop-priority algorithm to fit blocks within budget.

    Drop priority (first to drop):
    1. All non-preserved horizontal_rule blocks (pure formatting, no content)
    2. Trailing content blocks from the end — paragraph, list, blockquote,
       code_block — popped one at a time from the tail
    3. Entire trailing h3 subsection (heading + owned content)
    4. Entire trailing h2 section (heading + owned content) as last resort

    Preserved blocks are never dropped. Raises KernelCompilationError
    if budget cannot be met after exhausting all tiers.
    """
    from .errors import KernelCompilationError

    result = list(blocks)

    if _total_block_tokens(result) <= budget:
        return result

    result = [
        b for b in result
        if b.block_type != BlockType.HORIZONTAL_RULE or b.preserved
    ]

    if _total_block_tokens(result) <= budget:
        return result

    while _total_block_tokens(result) > budget and result:
        last = result[-1]
        if last.block_type in _DROPPABLE_CONTENT and not last.preserved:
            if last.block_type in {BlockType.BULLET_LIST, BlockType.NUMBERED_LIST}:
                items = last.text.split("\n")
                if len(items) > 1:
                    items.pop()
                    result[-1] = MarkdownBlock(
                        block_type=last.block_type,
                        text="\n".join(items),
                        preserved=last.preserved,
                    )
                    continue
            result.pop()
        else:
            break

    if _total_block_tokens(result) <= budget:
        return result

    for heading_level in (3, 2):
        while _total_block_tokens(result) > budget:
            idx = _find_last_droppable_heading(result, heading_level)
            if idx is None:
                break
            owned = _blocks_owned_by_heading(result, idx)
            for j in reversed(owned):
                result.pop(j)

    if _total_block_tokens(result) > budget:
        raise KernelCompilationError(
            f"Cannot fit content within {budget}-token budget: "
            f"{_total_block_tokens(result)} tokens remain after "
            f"dropping all non-preserved, non-heading content"
        )

    return result


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
    *,
    strict: bool = False,
) -> str:
    """Trim a single text blob to fit within a token budget.

    Uses markdown-block-aware trimming when the text has recognizable
    structure (multiple blocks). Falls back to word-level trimming for
    plain text or when block-level trimming cannot satisfy the budget
    without raising an error (permissive mode for non-kernel callers).

    When strict=True, KernelCompilationError propagates instead of
    falling back to word-level trim. compile_kernel uses strict=True
    so authoring problems surface as errors rather than silent degradation.

    The suffix is included in the final budget calculation and is only
    appended when word-level fallback trimming actually occurs.
    """
    clean = _strip_preserve_markers(text)
    if estimate_tokens(clean) <= budget_tokens:
        return clean

    blocks = parse_markdown_blocks(text)
    if len(blocks) > 1 or strict:
        try:
            trimmed = _trim_blocks_to_budget(blocks, budget_tokens)
            result = _reassemble_blocks(trimmed)
            if strict and not result.strip():
                from .errors import KernelCompilationError
                raise KernelCompilationError(
                    f"Cannot fit any content within {budget_tokens}-token budget: "
                    f"all blocks dropped (heading alone exceeds budget)"
                )
            if result.strip() and estimate_tokens(result) <= budget_tokens:
                return result
        except Exception:
            if strict:
                raise

    return _word_level_trim(text, budget_tokens, suffix)


def _word_level_trim(
    text: str,
    budget_tokens: int,
    suffix: str | None,
) -> str:
    """Fallback word-level trimmer for plain text or emergency fallback."""
    words = text.split()
    suffix_text = suffix or ""

    for cutoff in range(len(words), 0, -1):
        candidate = " ".join(words[:cutoff]).rstrip()
        if suffix_text:
            candidate = f"{candidate}\n\n{suffix_text}"
        if estimate_tokens(candidate) <= budget_tokens:
            return candidate

    if suffix_text and estimate_tokens(suffix_text) <= budget_tokens:
        return suffix_text

    for word in words:
        if estimate_tokens(word) <= budget_tokens:
            return word

    return text
