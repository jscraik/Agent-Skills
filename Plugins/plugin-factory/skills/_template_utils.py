#!/usr/bin/env python3
"""Shared template render/drift helpers for plugin-factory skills."""

from __future__ import annotations

from pathlib import Path
import runpy

_IMPL_PATH = Path(__file__).with_suffix(".pyw")
_NAMESPACE = runpy.run_path(str(_IMPL_PATH))

for name, value in _NAMESPACE.items():
    if name.startswith("__") and name not in {"__doc__", "__all__"}:
        continue
    globals()[name] = value
