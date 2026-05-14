#!/usr/bin/env python3
"""Facade module for skill state map rendering."""

from __future__ import annotations

from pathlib import Path
from types import ModuleType
import importlib.util
import sys


def _load_impl() -> ModuleType:
    try:
        from . import build_skill_state_map_impl as _impl

        return _impl
    except Exception:  # pragma: no cover - fallback when run as a file
        module_name = "build_skill_state_map_impl_runtime"
        spec = importlib.util.spec_from_file_location(
            module_name, Path(__file__).with_name("build_skill_state_map_impl.py")
        )
        if not spec or spec.loader is None:
            raise
        _impl = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = _impl
        spec.loader.exec_module(_impl)
        return _impl


_impl = _load_impl()
__all__ = [name for name in vars(_impl) if not name.startswith("_")]
for name in __all__:
    globals()[name] = getattr(_impl, name)


def main() -> int:
    return _impl.main()


if __name__ == "__main__":
    raise SystemExit(main())
