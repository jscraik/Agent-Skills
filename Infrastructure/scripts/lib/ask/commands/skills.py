#!/usr/bin/env python3
"""Facade module for skill command handlers.

This keeps public behavior stable while moving implementation into
`skills_impl.py` for easier maintenance.
"""

from __future__ import annotations

from pathlib import Path
from types import ModuleType
import importlib.util


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
globals().update({name: value for name, value in vars(_impl).items() if not (name.startswith("__") and name.endswith("__"))})

__all__ = getattr(_impl, "__all__", [name for name in globals() if not name.startswith("_")])

_IMPL_EXPLAIN_SKILL = _impl.explain_skill
_IMPL_SKILLS_PROOF = _impl.skills_proof
_IMPL_SKILLS_PROVE = _impl.skills_prove
_FACADE_SKILLS_PROOF = None


_PATCHABLE_IMPL_GLOBALS = (
    "audit_skill",
    "improve_skills",
    "resolve_skill_handle",
    "skills_proof",
    "skill_invocation_analytics",
    "_skill_sections",
    "_skill_workout_candidates",
)


def _sync_patchable_impl_globals() -> None:
    """Mirror facade monkeypatches into the implementation module before delegation."""
    for name in _PATCHABLE_IMPL_GLOBALS:
        if name in globals():
            setattr(_impl, name, globals()[name])
    if globals().get("skills_proof") is _FACADE_SKILLS_PROOF:
        _impl.skills_proof = _IMPL_SKILLS_PROOF


def explain_skill(repo_root: Path, handle: str):
    _sync_patchable_impl_globals()
    return _IMPL_EXPLAIN_SKILL(repo_root, handle)


def skills_proof(repo_root: Path, handle: str):
    _sync_patchable_impl_globals()
    return _IMPL_SKILLS_PROOF(repo_root, handle)


_FACADE_SKILLS_PROOF = skills_proof


def skills_prove(repo_root: Path, handle: str):
    _sync_patchable_impl_globals()
    return _IMPL_SKILLS_PROVE(repo_root, handle)
