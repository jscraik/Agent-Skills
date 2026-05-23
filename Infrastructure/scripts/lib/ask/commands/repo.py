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
globals().update({name: value for name, value in vars(_impl).items() if not name.startswith("_")})

__all__ = list(getattr(_impl, "__all__", [name for name in globals() if not name.startswith("_")]))
