#!/usr/bin/env python3
"""Compatibility wrapper for moved script entrypoint.

This wrapper supports both CLI execution and import-based callers that still
import ``Infrastructure/scripts/verify_skills_system_upstream_lock.py``.
"""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
import runpy
import sys

_TARGET_PATH = (
    Path(__file__).resolve().parent
    / "validation-and-linting/verify_skills_system_upstream_lock.py"
)


def _load_target_module() -> ModuleType:
    spec = spec_from_file_location(
        "_verify_skills_system_upstream_lock_impl",
        _TARGET_PATH,
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load spec for {_TARGET_PATH}")

    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_TARGET_MODULE = _load_target_module()
for _name in dir(_TARGET_MODULE):
    if _name.startswith("_"):
        continue
    globals()[_name] = getattr(_TARGET_MODULE, _name)

if __name__ == "__main__":
    # Target script raises SystemExit with return code; let it propagate
    runpy.run_path(str(_TARGET_PATH), run_name="__main__")
