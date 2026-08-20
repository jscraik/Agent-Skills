#!/usr/bin/env python3
"""Compatibility facade for skill-authoring family benchmark validation."""

import importlib
import sys
from pathlib import Path
from types import FunctionType
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

_cli = importlib.import_module("validate_skill_authoring_family_benchmarks_cli")
_context_checks = importlib.import_module("validate_skill_authoring_family_benchmarks_context_checks")
_core = importlib.import_module("validate_skill_authoring_family_benchmarks_core")
_eval_checks = importlib.import_module("validate_skill_authoring_family_benchmarks_eval_checks")


_HELPER_MODULE_NAMES = frozenset(
    module.__name__ for module in (_core, _eval_checks, _context_checks, _cli)
)


def _facade_value(value: Any) -> Any:
    """Rebind helper functions so facade-level patching remains authoritative."""

    if not isinstance(value, FunctionType) or value.__module__ not in _HELPER_MODULE_NAMES:
        return value
    rebound = FunctionType(value.__code__, globals(), value.__name__, value.__defaults__, value.__closure__)
    rebound.__kwdefaults__ = value.__kwdefaults__
    rebound.__annotations__ = value.__annotations__
    rebound.__dict__.update(value.__dict__)
    rebound.__doc__ = value.__doc__
    rebound.__qualname__ = value.__qualname__
    rebound.__module__ = __name__
    return rebound


for _module in (_core, _eval_checks, _context_checks, _cli):
    for _name in _module.__all__:
        globals()[_name] = _facade_value(getattr(_module, _name))

del _module, _name


if __name__ == "__main__":
    raise SystemExit(globals()["main"](sys.argv[1:]))
