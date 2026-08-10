#!/usr/bin/env python3
"""Facade module for repository command handlers."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType


def _load_impl() -> ModuleType:
    try:
        from . import repo_impl as _impl

        return _impl
    except Exception:  # pragma: no cover - fallback when executed as a file
        package_root = Path(__file__).resolve().parents[2]
        command_root = Path(__file__).resolve().parent
        lifecycle_root = Path(__file__).resolve().parents[3] / "lifecycle-and-sync"
        for import_root in (package_root, command_root, lifecycle_root):
            if str(import_root) not in sys.path:
                sys.path.insert(0, str(import_root))
        return importlib.import_module("ask.commands.repo_impl")


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
