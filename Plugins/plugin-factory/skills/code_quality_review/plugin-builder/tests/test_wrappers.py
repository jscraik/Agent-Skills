#!/usr/bin/env python3
"""Smoke checks for plugin-builder script wrappers."""

from pathlib import Path
import sys

HELPERS_ROOT = Path(__file__).resolve().parents[3]
if str(HELPERS_ROOT) not in sys.path:
    sys.path.insert(0, str(HELPERS_ROOT))

from tests_shared import find_repo_root


def test_plugin_builder_wrapper_points_to_impl() -> None:
    current = Path(__file__).resolve()
    repo_root = find_repo_root(current)
    script_path = (
        repo_root
        / "Plugins"
        / "plugin-factory"
        / "skills"
        / "code_quality_review"
        / "plugin-builder"
        / "scripts"
        / "plugin_builder.py"
    )
    impl_path = script_path.with_suffix(".pyw")

    assert script_path.exists()
    assert impl_path.exists()
    wrapper_source = script_path.read_text(encoding="utf-8")
    assert "runpy.run_path" in wrapper_source
    assert ".pyw" in wrapper_source
