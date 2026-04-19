#!/usr/bin/env python3
"""Smoke checks for plugin-builder script wrappers."""

from pathlib import Path


def test_plugin_builder_wrapper_points_to_impl() -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "plugin_builder.py"
    impl_path = script_path.with_suffix(".pyw")

    assert script_path.exists()
    assert impl_path.exists()
    wrapper_source = script_path.read_text(encoding="utf-8")
    assert "runpy.run_path" in wrapper_source
    assert ".pyw" in wrapper_source

