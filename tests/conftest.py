"""Shared test fixtures for Starry-Lyfe test suite."""

from pathlib import Path

import pytest

CANON_DIR = Path(__file__).resolve().parent.parent / "src" / "starry_lyfe" / "canon"
SRC_DIR = Path(__file__).resolve().parent.parent / "src"


@pytest.fixture
def canon_dir() -> Path:
    """Path to the canon YAML directory."""
    return CANON_DIR


@pytest.fixture
def src_dir() -> Path:
    """Path to the src directory."""
    return SRC_DIR
