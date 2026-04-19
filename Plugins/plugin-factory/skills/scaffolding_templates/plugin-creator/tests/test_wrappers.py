#!/usr/bin/env python3
"""Smoke checks for plugin-creator script wrappers."""

from pathlib import Path


def test_creator_wrappers_point_to_impls() -> None:
    scripts_dir = Path(__file__).resolve().parents[1] / "scripts"
    script_names = (
        "create_basic_plugin.py",
        "check_plugin_creator_template_drift.py",
    )

    for script_name in script_names:
        script_path = scripts_dir / script_name
        impl_path = script_path.with_suffix(".pyw")
        assert script_path.exists()
        assert impl_path.exists()

