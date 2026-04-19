#!/usr/bin/env python3
"""Smoke checks for plugin-installer script wrappers."""

from pathlib import Path


def test_installer_wrapper_points_to_impl() -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "install-plugin-from-github.py"
    impl_path = script_path.with_suffix(".pyw")

    assert script_path.exists()
    assert impl_path.exists()

