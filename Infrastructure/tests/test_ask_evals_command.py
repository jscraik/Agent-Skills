"""Compatibility test facade for modularized test cases."""

from types import FunctionType

import ask_evals_command_tests_01 as _part01
import ask_evals_command_tests_02 as _part02
import ask_evals_command_tests_03 as _part03
import ask_evals_command_tests_04 as _part04
import ask_evals_command_tests_05 as _part05
import ask_evals_command_tests_06 as _part06
import ask_evals_command_tests_07 as _part07
import ask_evals_command_tests_08 as _part08
import ask_evals_command_tests_core as _core


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


_MODULES = (_core, _part01, _part02, _part03, _part04, _part05, _part06, _part07, _part08)

for _module in _MODULES:
    for _name in _module.__all__:
        if _module is not _MODULES[0] and _name in globals():
            continue
        globals()[_name] = _facade_value(getattr(_module, _name), _module.__name__)
