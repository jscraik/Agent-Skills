#!/usr/bin/env python3
"""Facade module for lifecycle readiness validation tests."""

from __future__ import annotations

from pathlib import Path
from types import ModuleType
import importlib.util
import sys


def _load_impl() -> ModuleType:
    module_name = "test_skill_lifecycle_validation_impl_runtime"
    spec = importlib.util.spec_from_file_location(
        module_name,
        Path(__file__).with_name("test_skill_lifecycle_validation_impl.py"),
    )
    if not spec or spec.loader is None:
        raise RuntimeError("Failed to locate test_skill_lifecycle_validation implementation")
    impl = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = impl
    spec.loader.exec_module(impl)
    return impl


_impl = _load_impl()
globals().update({name: value for name, value in vars(_impl).items() if not name.startswith("_")})


if __name__ == "__main__":
    from unittest import main as _unittest_main

    _main = getattr(_impl, "main", None)
    if _main is None:
        _unittest_main()
    else:
        raise SystemExit(_main())
