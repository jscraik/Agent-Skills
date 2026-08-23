#!/usr/bin/env python3
"""Compatibility facade for the modular skill evaluation runner."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import FunctionType

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_skill_evals_assertions as _run_skill_evals_assertions  # noqa: E402
import run_skill_evals_assertions_core as _run_skill_evals_assertions_core  # noqa: E402
import run_skill_evals_cli as _run_skill_evals_cli  # noqa: E402
import run_skill_evals_core as _run_skill_evals_core  # noqa: E402
import run_skill_evals_discovery as _run_skill_evals_discovery  # noqa: E402
import run_skill_evals_loading as _run_skill_evals_loading  # noqa: E402
_run_skill_evals_outputs = importlib.import_module("run_skill_evals_outputs")
_run_skill_evals_workflow = importlib.import_module("run_skill_evals_workflow")
import run_skill_evals_main as _run_skill_evals_main  # noqa: E402
import run_skill_evals_preflight as _run_skill_evals_preflight  # noqa: E402
import run_skill_evals_runners as _run_skill_evals_runners  # noqa: E402


def _facade_value(value, module_name: str):
    if not isinstance(value, FunctionType) or value.__module__ != module_name:
        return value
    rebound = FunctionType(
        value.__code__,
        globals(),
        name=value.__name__,
        argdefs=value.__defaults__,
        closure=value.__closure__,
    )
    rebound.__kwdefaults__ = value.__kwdefaults__
    rebound.__annotations__ = value.__annotations__
    rebound.__dict__.update(value.__dict__)
    rebound.__doc__ = value.__doc__
    rebound.__qualname__ = value.__qualname__
    rebound.__module__ = __name__
    return rebound


_MODULES = (
    _run_skill_evals_core,
    _run_skill_evals_loading,
    _run_skill_evals_assertions_core,
    _run_skill_evals_assertions,
    _run_skill_evals_runners,
    _run_skill_evals_preflight,
    _run_skill_evals_cli,
    _run_skill_evals_discovery,
    _run_skill_evals_outputs,
    _run_skill_evals_workflow,
    _run_skill_evals_main,
)

for _module in _MODULES:
    for _name in _module.__all__:
        if _module is not _MODULES[0] and _name in globals():
            continue
        globals()[_name] = _facade_value(getattr(_module, _name), _module.__name__)


if __name__ == "__main__":
    raise SystemExit(globals()["main"]())
