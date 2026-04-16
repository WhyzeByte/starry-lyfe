"""Phase 10.5b RT3: ``load_kernel`` cache invalidates on rich-YAML mtime.

Before RT3, the cache key was ``{character_id}:{budget}:{profile}:{promo}``
— stable across authorship edits to ``Characters/{name}.yaml``. Edits
during dev or remediation would be silently invisible to cached callers
until a process restart. RT3 folds the rich YAML file mtime into the
cache key so any change to the canonical source on disk produces a fresh
compilation.
"""

from __future__ import annotations

import os
from typing import Any

import pytest

from starry_lyfe.canon.rich_loader import CHARACTERS_DIR, RICH_YAML_FILES
from starry_lyfe.context import kernel_loader


@pytest.fixture(autouse=True)
def _clean_cache() -> Any:
    kernel_loader.clear_kernel_cache()
    yield
    kernel_loader.clear_kernel_cache()


class TestLoadKernelCacheInvalidation:
    def test_cache_invalidates_on_yaml_mtime_change(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A touch that advances mtime must force a fresh kernel compile."""
        yaml_path = CHARACTERS_DIR / RICH_YAML_FILES["adelia"]
        original_mtime = yaml_path.stat().st_mtime

        call_count = {"n": 0}
        real_compile = kernel_loader.compile_kernel_with_soul

        def counting_compile(*args: Any, **kwargs: Any) -> str:
            call_count["n"] += 1
            return real_compile(*args, **kwargs)

        monkeypatch.setattr(
            kernel_loader, "compile_kernel_with_soul", counting_compile,
        )

        try:
            first = kernel_loader.load_kernel("adelia", budget=2000)
            assert call_count["n"] == 1
            cached = kernel_loader.load_kernel("adelia", budget=2000)
            assert cached == first
            assert call_count["n"] == 1, "second identical call should hit cache"

            new_mtime = original_mtime + 10.0
            os.utime(yaml_path, (new_mtime, new_mtime))

            _ = kernel_loader.load_kernel("adelia", budget=2000)
            assert call_count["n"] == 2, (
                "RT3 regression: cache did not invalidate on YAML mtime change"
            )
        finally:
            os.utime(yaml_path, (original_mtime, original_mtime))

    def test_cache_key_stable_across_identical_mtimes(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """No touch, no invalidation — cache continues to serve repeated calls."""
        call_count = {"n": 0}
        real_compile = kernel_loader.compile_kernel_with_soul

        def counting_compile(*args: Any, **kwargs: Any) -> str:
            call_count["n"] += 1
            return real_compile(*args, **kwargs)

        monkeypatch.setattr(
            kernel_loader, "compile_kernel_with_soul", counting_compile,
        )

        kernel_loader.load_kernel("bina", budget=2000)
        kernel_loader.load_kernel("bina", budget=2000)
        kernel_loader.load_kernel("bina", budget=2000)
        assert call_count["n"] == 1

    def test_cache_key_still_includes_profile_name(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """C2 invariant preserved: same budget+char, different profile → miss."""
        call_count = {"n": 0}
        real_compile = kernel_loader.compile_kernel_with_soul

        def counting_compile(*args: Any, **kwargs: Any) -> str:
            call_count["n"] += 1
            return real_compile(*args, **kwargs)

        monkeypatch.setattr(
            kernel_loader, "compile_kernel_with_soul", counting_compile,
        )

        kernel_loader.load_kernel("reina", budget=2000, profile_name="default")
        kernel_loader.load_kernel("reina", budget=2000, profile_name="pair_intimate")
        assert call_count["n"] == 2, (
            "C2 invariant broken: profile_name no longer in cache key"
        )
