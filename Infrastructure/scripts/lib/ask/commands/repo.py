#!/usr/bin/env python3
"""Facade module for repository command handlers."""

from __future__ import annotations

from pathlib import Path
from types import ModuleType
import importlib.util
import sys


def _load_impl() -> ModuleType:
    try:
        from . import repo_impl as _impl

        return _impl
    except Exception:  # pragma: no cover - fallback when executed as a file
        module_name = "repo_impl_runtime"
        spec = importlib.util.spec_from_file_location(
            module_name,
            Path(__file__).with_name("repo_impl.py"),
        )
        if not spec or spec.loader is None:
            raise
        _impl = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = _impl
        spec.loader.exec_module(_impl)
        return _impl


_impl = _load_impl()
globals().update({name: value for name, value in vars(_impl).items() if not name.startswith("_")})

__all__ = [
    "Any",
    "COMMAND_HANDLE_CHECK_COMMAND",
    "CANONICAL_SKILL_PREFIXES",
    "CallResult",
    "DOCTOR_SIGNAL_PRIORITY",
    "ErrorCode",
    "ErrorObject",
    "GENERATED_SURFACE_PREFIXES",
    "List",
    "PACKAGE_READINESS_SENTINEL",
    "Path",
    "SCRIPT_TIMEOUT_SECONDS",
    "annotations",
    "build_golden_path_payload",
    "check_hub_stability",
    "collect_changed_files",
    "compute_catalog_parity",
    "doctor_catalog",
    "json",
    "provider_audit",
    "re",
    "repo_closeout",
    "repo_doctor",
    "repo_status",
    "repo_surface",
    "repo_validate",
    "run_bootstrap_checks",
    "shlex",
    "skills_budget",
    "skills_events",
    "skills_handles",
    "skills_memory",
    "skills_package",
    "skills_profiles",
    "subprocess",
    "sys",
]
