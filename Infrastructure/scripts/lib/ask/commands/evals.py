"""Compatibility facade for modular evaluation commands."""

from __future__ import annotations

from types import FunctionType

from . import evals_core as _evals_core
from . import evals_policy as _evals_policy
from . import evals_staging_parse as _evals_staging_parse
from . import evals_quality as _evals_quality
from . import evals_projection as _evals_projection
from . import evals_project as _evals_project
from . import evals_live_preflight as _evals_live_preflight
from . import evals_local_scenario as _evals_local_scenario
from . import evals_live_run as _evals_live_run
from . import evals_macro as _evals_macro
from . import evals_closeout as _evals_closeout
from . import evals_runner as _evals_runner
from ask.skills_sdk.tessl_live_view import (
    inspect_tessl_live_private_eval,
)


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
    _evals_core,
    _evals_policy,
    _evals_staging_parse,
    _evals_quality,
    _evals_projection,
    _evals_project,
    _evals_live_preflight,
    _evals_local_scenario,
    _evals_live_run,
    _evals_macro,
    _evals_closeout,
    _evals_runner,
)

for _module in _MODULES:
    for _name in _module.__all__:
        if _module is not _MODULES[0] and _name in globals():
            continue
        globals()[_name] = _facade_value(getattr(_module, _name), _module.__name__)
