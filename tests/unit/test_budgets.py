"""Phase A tests for the markdown-block-aware trimmer in budgets.py.

Test cases A1, A2, A3 mirror master plan §4 spec test cases exactly.
Adversarial edge-case tests cover the drop-priority algorithm, error
semantics, plain-text fallback, and four-kernel integration.
"""

from __future__ import annotations

import pytest

from starry_lyfe.context.budgets import (
    BlockType,
    estimate_tokens,
    parse_markdown_blocks,
    trim_text_to_budget,
)
from starry_lyfe.context.errors import KernelCompilationError


def _words(n: int) -> str:
    """Generate exactly n words of filler text."""
    return " ".join(f"word{i}" for i in range(n))


def _paragraph(token_target: int) -> str:
    """Generate a paragraph that estimates to approximately token_target tokens."""
    word_count = int(token_target * 0.75)
    return _words(max(1, word_count))


def _build_markdown(sections: list[str]) -> str:
    return "\n\n".join(sections)


class TestA1ExactFit:
    """Test A1: A 1500-token input with a 2000-token budget returns unchanged."""

    def test_a1_exact_fit_returns_unchanged(self) -> None:
        heading = "## 1. Runtime Directives"
        para1 = _paragraph(500)
        bullet_list = "\n".join(f"- item {i}: {_words(20)}" for i in range(10))
        para2 = _paragraph(400)

        text = _build_markdown([heading, para1, bullet_list, para2])
        assert estimate_tokens(text) < 2000

        result = trim_text_to_budget(text, 2000)
        assert result == text


class TestA2OversizedSection:
    """Test A2: oversized input preserves h2 heading and first paragraph."""

    def test_a2_oversized_section_preserves_h2_and_first_paragraph_without_mid_paragraph_cut(
        self,
    ) -> None:
        heading = "## 2. Core Identity"
        first_para = _paragraph(400)
        second_para = _paragraph(500)
        third_para = _paragraph(500)
        fourth_para = _paragraph(500)
        fifth_para = _paragraph(500)
        trailing_hr = "---"

        text = _build_markdown([
            heading, first_para, second_para, third_para,
            fourth_para, fifth_para, trailing_hr,
        ])
        assert estimate_tokens(text) > 2000

        result = trim_text_to_budget(text, 2000)

        assert estimate_tokens(result) <= 2000
        assert "## 2. Core Identity" in result
        assert first_para in result
        for line in result.split("\n"):
            if line.strip() and not line.startswith("#") and not line.startswith("---"):
                assert not line.endswith(" word"), (
                    f"Possible mid-paragraph cut detected: {line[-40:]}"
                )

    def test_a2_no_mid_paragraph_cuts(self) -> None:
        heading = "## 2. Core Identity"
        paragraphs = [_paragraph(300) for _ in range(8)]
        text = _build_markdown([heading, *paragraphs])
        assert estimate_tokens(text) > 1500

        result = trim_text_to_budget(text, 1500)

        blocks = parse_markdown_blocks(result)
        for block in blocks:
            if block.block_type == BlockType.PARAGRAPH:
                original_blocks = parse_markdown_blocks(text)
                original_texts = {
                    b.text for b in original_blocks if b.block_type == BlockType.PARAGRAPH
                }
                assert block.text in original_texts, (
                    "Output contains a paragraph not present in the original "
                    "(indicates a mid-paragraph cut)"
                )


class TestA3PreserveMarker:
    """Test A3: PRESERVE marker prevents block from being dropped."""

    def test_a3_preserve_marker_respected_under_tight_budget(self) -> None:
        sections = [
            "## 1. Runtime Directives",
            _paragraph(300),
            "## 2. Core Identity",
            _paragraph(400),
            "## 3. Pair Dynamics",
            _paragraph(400),
            "<!-- PRESERVE -->",
            "## 5. Behavioral Tier Framework",
            _paragraph(200),
            "## 6. Voice Architecture",
            _paragraph(300),
        ]
        text = _build_markdown(sections)

        budget = 1000
        assert estimate_tokens(text) > budget

        result = trim_text_to_budget(text, budget)

        assert "## 5. Behavioral Tier Framework" in result
        assert estimate_tokens(result) <= budget


class TestDropPriority:
    """Adversarial tests verifying the spec's block drop priority order."""

    def test_trailing_horizontal_rule_dropped_first(self) -> None:
        text = _build_markdown([
            "## 1. Section",
            _paragraph(300),
            "---",
        ])
        tight_budget = estimate_tokens(text) - 2

        result = trim_text_to_budget(text, tight_budget)

        assert "---" not in result
        assert "## 1. Section" in result

    def test_bullet_list_items_dropped_one_at_a_time(self) -> None:
        items = "\n".join(f"- bullet item number {i} with some text" for i in range(5))
        text = _build_markdown([
            "## 1. Section",
            _paragraph(100),
            items,
        ])
        tokens_of_one_item = estimate_tokens("- bullet item number 4 with some text")
        budget = estimate_tokens(text) - tokens_of_one_item - 1

        result = trim_text_to_budget(text, budget)

        assert "## 1. Section" in result
        assert "bullet item number 0" in result

    def test_trailing_code_block_dropped_before_h3_subsection(self) -> None:
        text = _build_markdown([
            "## 1. Section",
            "### 1.1 Subsection",
            _paragraph(100),
            "```python\nprint('hello')\n```",
        ])
        code_tokens = estimate_tokens("```python\nprint('hello')\n```")
        budget = estimate_tokens(text) - code_tokens + 1

        result = trim_text_to_budget(text, budget)

        assert "### 1.1 Subsection" in result
        assert "```python" not in result


class TestKernelCompilationError:
    """Verify KernelCompilationError is raised for unfittable content."""

    def test_kernel_compilation_error_raised_when_single_heading_exceeds_budget(
        self,
    ) -> None:
        text = _build_markdown([
            "## 2. Core Identity With Extended Biographical Subtitle That Is Very Long",
            _paragraph(200),
        ])

        with pytest.raises(KernelCompilationError):
            trim_text_to_budget(text, 3, strict=True)

    def test_preserve_marker_on_oversized_preserved_block_raises(self) -> None:
        text = _build_markdown([
            "<!-- PRESERVE -->",
            "## 5. Behavioral Tier Framework With Additional Descriptive Title Words",
            _paragraph(500),
        ])

        with pytest.raises(KernelCompilationError):
            trim_text_to_budget(text, 3, strict=True)


class TestBackwardCompatibility:
    """Verify trim_text_to_budget remains safe for non-kernel callers."""

    def test_plain_text_input_no_markdown_falls_back_gracefully(self) -> None:
        text = _words(200)
        assert estimate_tokens(text) > 100

        result = trim_text_to_budget(text, 100, "[Trimmed to budget.]")

        assert estimate_tokens(result) <= 100
        assert "[Trimmed to budget.]" in result

    def test_short_text_returns_unchanged(self) -> None:
        text = "Hello world."
        result = trim_text_to_budget(text, 1000, "[Trimmed.]")
        assert result == text

    def test_suffix_not_appended_when_block_trim_succeeds(self) -> None:
        text = _build_markdown([
            "## 1. Section",
            _paragraph(200),
            _paragraph(200),
            _paragraph(200),
        ])
        budget = estimate_tokens(text) - 100

        result = trim_text_to_budget(text, budget, "[Should not appear.]")

        assert "[Should not appear.]" not in result
        assert estimate_tokens(result) <= budget


class TestBlockParser:
    """Verify parse_markdown_blocks correctly classifies block types."""

    def test_heading_detection(self) -> None:
        text = "## 2. Core Identity\n\nSome paragraph text."
        blocks = parse_markdown_blocks(text)
        assert len(blocks) == 2
        assert blocks[0].block_type == BlockType.HEADING
        assert blocks[0].heading_level == 2
        assert blocks[1].block_type == BlockType.PARAGRAPH

    def test_bullet_list_detection(self) -> None:
        text = "- item one\n- item two\n- item three"
        blocks = parse_markdown_blocks(text)
        assert len(blocks) == 1
        assert blocks[0].block_type == BlockType.BULLET_LIST

    def test_code_fence_detection(self) -> None:
        text = "Some intro.\n\n```python\nx = 1\n\ny = 2\n```\n\nAfter code."
        blocks = parse_markdown_blocks(text)
        types = [b.block_type for b in blocks]
        assert BlockType.CODE_BLOCK in types

    def test_preserve_marker_annotates_next_block(self) -> None:
        text = "## 1. Section\n\n<!-- PRESERVE -->\n\n## 2. Protected Section\n\nContent."
        blocks = parse_markdown_blocks(text)
        protected = [b for b in blocks if b.preserved]
        assert len(protected) == 1
        assert protected[0].text.startswith("## 2.")

    def test_horizontal_rule_detection(self) -> None:
        text = "Some text.\n\n---\n\nMore text."
        blocks = parse_markdown_blocks(text)
        types = [b.block_type for b in blocks]
        assert BlockType.HORIZONTAL_RULE in types

    def test_nested_subsection_with_mixed_blocks_preserves_h2_h3_hierarchy(
        self,
    ) -> None:
        text = _build_markdown([
            "## 2. Section",
            _paragraph(100),
            "### 2.1 Subsection",
            _paragraph(100),
            "- bullet one\n- bullet two",
            "```python\ncode_here()\n```",
        ])

        budget = estimate_tokens(text) - estimate_tokens("```python\ncode_here()\n```") + 1
        result = trim_text_to_budget(text, budget)

        assert "## 2. Section" in result
        assert "### 2.1 Subsection" in result
        assert "```python" not in result


class TestF1Regression:
    """F1 regression: compile_kernel must never return over-budget content."""

    def test_compile_kernel_tiny_budget_raises_or_respects_ceiling(self) -> None:
        from starry_lyfe.context.errors import KernelCompilationError
        from starry_lyfe.context.kernel_loader import clear_kernel_cache, compile_kernel

        clear_kernel_cache()
        try:
            result = compile_kernel("adelia", budget=120)
            assert estimate_tokens(result) <= 120, (
                f"compile_kernel returned {estimate_tokens(result)} tokens "
                f"for a 120-token budget"
            )
        except KernelCompilationError:
            pass
