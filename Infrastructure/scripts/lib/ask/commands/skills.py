#!/usr/bin/env python3
"""Facade module for skill command handlers.

This keeps public behavior stable while moving implementation into
`skills_impl.py` for easier maintenance.
"""

from __future__ import annotations

from pathlib import Path
from types import ModuleType
import importlib.util


def _load_impl() -> ModuleType:
    try:
        from . import skills_impl as _impl

        return _impl
    except Exception:  # pragma: no cover - fallback when run as a file
        spec = importlib.util.spec_from_file_location(
            "skills_impl", Path(__file__).with_name("skills_impl.py")
        )
        if not spec or spec.loader is None:
            raise
        _impl = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_impl)
        return _impl


_impl = _load_impl()
globals().update({name: value for name, value in vars(_impl).items() if not name.startswith("_")})

__all__ = getattr(_impl, "__all__", [name for name in globals() if not name.startswith("_")])
