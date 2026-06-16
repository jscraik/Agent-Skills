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
SCRIPT_TIMEOUT_SECONDS = _impl.SCRIPT_TIMEOUT_SECONDS
check_hub_stability = _impl.check_hub_stability
collect_changed_files = _impl.collect_changed_files
doctor_catalog = _impl.doctor_catalog
provider_audit = _impl.provider_audit
repo_closeout = _impl.repo_closeout
repo_doctor = _impl.repo_doctor
repo_status = _impl.repo_status
repo_surface = _impl.repo_surface
repo_validate = _impl.repo_validate
repo_yaml_inspect = _impl.repo_yaml_inspect
subprocess = _impl.subprocess

__all__ = [
    "SCRIPT_TIMEOUT_SECONDS",
    "check_hub_stability",
    "collect_changed_files",
    "doctor_catalog",
    "provider_audit",
    "repo_closeout",
    "repo_doctor",
    "repo_status",
    "repo_surface",
    "repo_validate",
    "repo_yaml_inspect",
    "subprocess",
]
