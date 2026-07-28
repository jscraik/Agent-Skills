#!/usr/bin/env python3
"""Facade module for lifecycle readiness validation tests."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from types import ModuleType


_TESTING_DIR = Path(__file__).resolve().parent
if str(_TESTING_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTING_DIR))

_IMPLEMENTATION_FILENAMES = (
    "test_skill_lifecycle_validation_impl_catalog.py",
    "test_skill_lifecycle_validation_impl_discovery.py",
    "test_skill_lifecycle_validation_impl_runtime.py",
)


def _load_impl(filename: str) -> ModuleType:
    module_name = f"{Path(filename).stem}_runtime"
    spec = importlib.util.spec_from_file_location(
        module_name,
        _TESTING_DIR / filename,
    )
    if not spec or spec.loader is None:
        raise RuntimeError(f"Failed to locate lifecycle readiness test implementation: {filename}")
    impl = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = impl
    spec.loader.exec_module(impl)
    return impl


for _implementation_filename in _IMPLEMENTATION_FILENAMES:
    _impl = _load_impl(_implementation_filename)
    globals().update({name: value for name, value in vars(_impl).items() if not name.startswith("_")})


if __name__ == "__main__":
    unittest.main()
