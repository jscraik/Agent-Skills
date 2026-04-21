#!/usr/bin/env python3
"""CLI wrapper for create_basic_plugin implementation."""

from __future__ import annotations

from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_suffix(".pyw")), run_name="__main__")
