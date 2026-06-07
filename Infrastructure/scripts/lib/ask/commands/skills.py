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
globals().update({name: value for name, value in vars(_impl).items() if not (name.startswith("__") and name.endswith("__"))})

_PATCHABLE_IMPL_NAMES = (
    "audit_skill",
    "discover_catalog_entries",
    "discover_skill_entries",
    "handles_report",
    "route_skills",
    "improve_skills",
    "install_skill",
    "list_skills",
    "goal_skills",
    "resolve_skill_handle",
    "sync_skills",
    "skill_invocation_analytics",
    "skills_proof",
    "_skill_sections",
    "_skill_workout_candidates",
    "refresh_workspace_plugin_caches",
    "prune_unowned_skillset_files",
)
_ORIGINAL_IMPL_VALUES = {
    name: getattr(_impl, name)
    for name in _PATCHABLE_IMPL_NAMES
    if hasattr(_impl, name)
}
_FACADE_WRAPPERS: dict[str, object] = {}


def _sync_patchable_impl_names() -> None:
    """Mirror wrapper-level patches into the implementation module."""
    for name in _PATCHABLE_IMPL_NAMES:
        if name in globals():
            value = globals()[name]
            if _FACADE_WRAPPERS.get(name) is value:
                continue
            if name in _ORIGINAL_IMPL_VALUES and value is _ORIGINAL_IMPL_VALUES[name]:
                continue
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


def install_skill(*args, **kwargs):
    return _call_impl("install_skill", *args, **kwargs)


def list_skills(*args, **kwargs):
    return _call_impl("list_skills", *args, **kwargs)


def goal_skills(*args, **kwargs):
    return _call_impl("goal_skills", *args, **kwargs)


def sync_skills(*args, **kwargs):
    return _call_impl("sync_skills", *args, **kwargs)


def skills_sdk_status(*args, **kwargs):
    return _call_impl("skills_sdk_status", *args, **kwargs)


def skills_sdk_project_install(*args, **kwargs):
    return _call_impl("skills_sdk_project_install", *args, **kwargs)


def skills_sdk_project_conformance(*args, **kwargs):
    return _call_impl("skills_sdk_project_conformance", *args, **kwargs)


_FACADE_WRAPPERS.update(
    {
        "skills_proof": skills_proof,
        "skills_prove": skills_prove,
        "explain_skill": explain_skill,
        "improve_skills": improve_skills,
        "install_skill": install_skill,
        "list_skills": list_skills,
        "goal_skills": goal_skills,
        "sync_skills": sync_skills,
        "skills_sdk_status": skills_sdk_status,
        "skills_sdk_project_install": skills_sdk_project_install,
        "skills_sdk_project_conformance": skills_sdk_project_conformance,
    }
)

_skill_sections = _impl._skill_sections
_skill_workout_candidates = _impl._skill_workout_candidates

audit_skill = _impl.audit_skill
extract_family_fail_lines = _impl.extract_family_fail_lines
external_review_skill = _impl.external_review_skill
fold_skills = _impl.fold_skills
format_capabilities_human = _impl.format_capabilities_human
format_codex_preview_human = _impl.format_codex_preview_human
init_skill = _impl.init_skill
reviewers_resolve = _impl.reviewers_resolve
route_skills = _impl.route_skills
skills_budget = _impl.skills_budget
skills_capabilities = _impl.skills_capabilities
skills_codex_preview = _impl.skills_codex_preview
skills_config_explain = _impl.skills_config_explain
skills_conformance_run = _impl.skills_conformance_run
skills_doctor = _impl.skills_doctor
skills_events = _impl.skills_events
skills_explain_boundary = _impl.skills_explain_boundary
skills_handles = _impl.skills_handles
skills_implicit_preview = _impl.skills_implicit_preview
skills_inject_preview = _impl.skills_inject_preview
skills_load_preview = _impl.skills_load_preview
skills_memory = _impl.skills_memory
skills_package = _impl.skills_package
skills_package_verify = _impl.skills_package_verify
skills_parse = _impl.skills_parse
skills_profiles = _impl.skills_profiles
skills_render_preview = _impl.skills_render_preview
skills_resolve = _impl.skills_resolve
skills_sdk_check = _impl.skills_sdk_check
skills_sdk_install_preview = _impl.skills_sdk_install_preview
skills_sdk_placeholder_lifecycle = _impl.skills_sdk_placeholder_lifecycle
validate_openai_skill_format = _impl.validate_openai_skill_format
validate_skill_boundaries = _impl.validate_skill_boundaries
validate_skill_gate = _impl.validate_skill_gate

__all__ = [
    "audit_skill",
    "explain_skill",
    "extract_family_fail_lines",
    "external_review_skill",
    "fold_skills",
    "format_capabilities_human",
    "format_codex_preview_human",
    "goal_skills",
    "improve_skills",
    "init_skill",
    "install_skill",
    "list_skills",
    "reviewers_resolve",
    "route_skills",
    "skills_budget",
    "skills_capabilities",
    "skills_codex_preview",
    "skills_config_explain",
    "skills_conformance_run",
    "skills_implicit_preview",
    "skills_inject_preview",
    "skills_doctor",
    "skills_events",
    "skills_explain_boundary",
    "skills_handles",
    "skills_load_preview",
    "skills_memory",
    "skills_package",
    "skills_package_verify",
    "skills_parse",
    "skills_profiles",
    "skills_proof",
    "skills_prove",
    "skills_render_preview",
    "skills_resolve",
    "skills_sdk_check",
    "skills_sdk_install_preview",
    "skills_sdk_placeholder_lifecycle",
    "skills_sdk_project_conformance",
    "skills_sdk_project_install",
    "skills_sdk_status",
    "sync_skills",
    "validate_openai_skill_format",
    "validate_skill_boundaries",
    "validate_skill_gate",
]
