#!/usr/bin/env python3
"""Facade module for projection integrity checks."""

from __future__ import annotations

from pathlib import Path
from types import ModuleType
import importlib.util
import sys


def _load_impl() -> ModuleType:
    try:
        from . import projection_integrity_impl as _impl

        return _impl
    except (ImportError, ModuleNotFoundError):  # pragma: no cover - fallback when run as a file
        module_name = "projection_integrity_impl_runtime"
        spec = importlib.util.spec_from_file_location(
            module_name, Path(__file__).with_name("projection_integrity_impl.py")
        )
        if not spec or spec.loader is None:
            raise
        _impl = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = _impl
        spec.loader.exec_module(_impl)
        return _impl


_impl = _load_impl()
globals().update({name: value for name, value in vars(_impl).items() if not name.startswith("_")})


def main() -> int:
    return _impl.main()


if __name__ == "__main__":
    raise SystemExit(main())
