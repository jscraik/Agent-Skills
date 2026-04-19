#!/usr/bin/env python3
"""Smoke checks for plugin-creator script wrappers."""

from pathlib import Path


def test_creator_wrappers_point_to_impls() -> None:
    """
    Smoke test that verifies wrapper scripts in the repository's scripts directory have corresponding implementation files with a `.pyw` suffix.
    
    Asserts that the wrapper files referenced by this test exist in the sibling `scripts` directory and that each has a same-named `.pyw` implementation; assertion failures indicate missing wrapper or implementation files.
    """
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

