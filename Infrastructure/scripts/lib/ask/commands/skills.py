#!/usr/bin/env python3
"""Facade module for skill command handlers.

This keeps public behavior stable while moving implementation into
`skills_impl.py` for easier maintenance.
"""

from __future__ import annotations

from types import ModuleType
import importlib.util
from pathlib import Path


def _load_impl() -> ModuleType:
    try:
        from . import skills_impl as _impl

        return _impl
    except Exception:  # pragma: no cover - fallback when run as a file
        spec = importlib.util.spec_from_file_location(
            "skills_impl", Path(__file__).with_name("skills_impl.py")
        )
        if not spec or spec.loader is None:
            raise
        _impl = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_impl)
        return _impl


_impl = _load_impl()
globals().update({name: value for name, value in vars(_impl).items() if not name.startswith("_")})

_PATCHABLE_IMPL_NAMES = (
    "audit_skill",
    "improve_skills",
    "resolve_skill_handle",
    "skill_invocation_analytics",
    "skills_proof",
    "_skill_sections",
    "_skill_workout_candidates",
)
_ORIGINAL_IMPL_VALUES = {
    name: getattr(_impl, name)
    for name in _PATCHABLE_IMPL_NAMES
    if hasattr(_impl, name)
}


def _sync_patchable_impl_names() -> None:
    """Mirror wrapper-level patches into the implementation module."""
    for name in _PATCHABLE_IMPL_NAMES:
        if name in globals():
            value = globals()[name]
            if (
                name in _ORIGINAL_IMPL_VALUES
                and getattr(value, "__module__", None) == __name__
                and getattr(value, "__name__", None) == name
            ):
                value = _ORIGINAL_IMPL_VALUES[name]
            setattr(_impl, name, value)


def _call_impl(name: str, *args, **kwargs):
    original_values = {
        impl_name: getattr(_impl, impl_name)
        for impl_name in _PATCHABLE_IMPL_NAMES
        if hasattr(_impl, impl_name)
    }
    try:
        _sync_patchable_impl_names()
        return getattr(_impl, name)(*args, **kwargs)
    finally:
        for impl_name, value in original_values.items():
            setattr(_impl, impl_name, value)


def skills_proof(*args, **kwargs):
    return _call_impl("skills_proof", *args, **kwargs)


def skills_prove(*args, **kwargs):
    return _call_impl("skills_prove", *args, **kwargs)


def explain_skill(*args, **kwargs):
    return _call_impl("explain_skill", *args, **kwargs)


def improve_skills(*args, **kwargs):
    return _call_impl("improve_skills", *args, **kwargs)


_skill_sections = _impl._skill_sections
_skill_workout_candidates = _impl._skill_workout_candidates

__all__ = getattr(_impl, "__all__", [name for name in globals() if not name.startswith("_")])
