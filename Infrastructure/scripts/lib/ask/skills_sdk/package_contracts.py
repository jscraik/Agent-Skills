"""Compatibility facade for Skills SDK package contracts."""

from types import FunctionType
from typing import Any

from . import package_contracts_core as _core
from . import package_contracts_optimization as _optimization
from . import package_contracts_platform as _platform
from . import package_contracts_readiness as _readiness
from . import package_contracts_rubric as _rubric
from . import package_contracts_support as _support
from . import package_contracts_writing_checks as _writing_checks
from . import package_contracts_writing_core as _writing_core


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


for _module in (
    _core,
    _rubric,
    _support,
    _optimization,
    _writing_core,
    _writing_checks,
    _platform,
    _readiness,
):
    for _name in _module.__all__:
        if _module is not _core and _name in globals():
            continue
        globals()[_name] = _facade_value(getattr(_module, _name), _module.__name__)

del _module, _name

_skill_package_contract_impl = skill_package_contract


def skill_package_contract(
    repo_root: Path,
    source_path: Path | None,
    frontmatter: dict[str, Any],
) -> dict[str, Any]:
    """Return the Codex-native package contract through the stable service facade."""
    return _skill_package_contract_impl(repo_root, source_path, frontmatter)
