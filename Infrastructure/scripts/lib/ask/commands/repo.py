#!/usr/bin/env python3
"""Facade module for repository command handlers."""

from __future__ import annotations

from pathlib import Path
from types import ModuleType
import importlib.util
import sys


def _load_impl() -> ModuleType:
    try:
        from . import repo_impl as _impl

        return _impl
    except Exception:  # pragma: no cover - fallback when executed as a file
        module_name = "repo_impl_runtime"
        spec = importlib.util.spec_from_file_location(
            module_name,
            Path(__file__).with_name("repo_impl.py"),
        )
        if not spec or spec.loader is None:
            raise
        _impl = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = _impl
        spec.loader.exec_module(_impl)
        return _impl


_impl = _load_impl()

# Explicit list of public command functions to export
__all__ = [
    "check_hub_stability",
    "collect_changed_files",
    "doctor_catalog",
    "provider_audit",
    "repo_closeout",
    "repo_doctor",
    "repo_status",
    "repo_surface",
    "repo_validate",
    "repo_yaml_inspect",
]

# Populate only the symbols listed in __all__ from the implementation module
for name in __all__:
    globals()[name] = getattr(_impl, name)
