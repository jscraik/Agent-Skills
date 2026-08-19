"""Compatibility facade for repository command implementations."""

from types import FunctionType
from typing import Any

from . import repo_impl_closeout as _closeout
from . import repo_impl_core as _core
from . import repo_impl_doctor as _doctor
from . import repo_impl_git as _git
from . import repo_impl_surfaces as _surfaces


def _facade_value(value: Any, module_name: str) -> Any:
    if not isinstance(value, FunctionType) or value.__module__ != module_name:
        return value
    rebound = FunctionType(value.__code__, globals(), value.__name__, value.__defaults__, value.__closure__)
    rebound.__kwdefaults__ = value.__kwdefaults__
    rebound.__annotations__ = value.__annotations__
    rebound.__dict__.update(value.__dict__)
    rebound.__doc__ = value.__doc__
    rebound.__qualname__ = value.__qualname__
    rebound.__module__ = __name__
    return rebound


for _module in (_core, _doctor, _closeout, _git, _surfaces):
    for _name in _module.__all__:
        if _module is not _core and _name in globals():
            continue
        globals()[_name] = _facade_value(getattr(_module, _name), _module.__name__)

del _module, _name
