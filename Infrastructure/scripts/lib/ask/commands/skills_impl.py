"""Compatibility facade for modular skill commands."""

from __future__ import annotations

from types import FunctionType

from . import skills_impl_core as _skills_impl_core
from . import skills_impl_catalog as _skills_impl_catalog
from . import skills_impl_listing as _skills_impl_listing
from . import skills_impl_memory_profiles as _skills_impl_memory_profiles
from . import skills_impl_profile_ops as _skills_impl_profile_ops
from . import skills_impl_capabilities as _skills_impl_capabilities
from . import skills_impl_doctor_intake as _skills_impl_doctor_intake
from . import skills_impl_sdk_intake as _skills_impl_sdk_intake
from . import skills_impl_sdk_eval as _skills_impl_sdk_eval
from . import skills_impl_sdk_calibration as _skills_impl_sdk_calibration
from . import skills_impl_plugin_ab as _skills_impl_plugin_ab
from . import skills_impl_ab_receipts as _skills_impl_ab_receipts
from . import skills_impl_release_sets as _skills_impl_release_sets
from . import skills_impl_project_improve as _skills_impl_project_improve
from . import skills_impl_project_conformance as _skills_impl_project_conformance
from . import skills_impl_audit_validation as _skills_impl_audit_validation
from . import skills_impl_external_review as _skills_impl_external_review
from . import skills_impl_install_improve as _skills_impl_install_improve
from . import skills_impl_improve_fallback as _skills_impl_improve_fallback
from . import skills_impl_runtime_sync as _skills_impl_runtime_sync


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
    _skills_impl_core,
    _skills_impl_catalog,
    _skills_impl_listing,
    _skills_impl_memory_profiles,
    _skills_impl_profile_ops,
    _skills_impl_capabilities,
    _skills_impl_doctor_intake,
    _skills_impl_sdk_intake,
    _skills_impl_sdk_eval,
    _skills_impl_sdk_calibration,
    _skills_impl_plugin_ab,
    _skills_impl_ab_receipts,
    _skills_impl_release_sets,
    _skills_impl_project_improve,
    _skills_impl_project_conformance,
    _skills_impl_audit_validation,
    _skills_impl_external_review,
    _skills_impl_install_improve,
    _skills_impl_improve_fallback,
    _skills_impl_runtime_sync,
)

for _module in _MODULES:
    for _name in _module.__all__:
        if _module is not _MODULES[0] and _name in globals():
            continue
        globals()[_name] = _facade_value(getattr(_module, _name), _module.__name__)
