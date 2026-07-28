#!/usr/bin/env python3
"""Shared helpers for lifecycle readiness validation tests."""

from __future__ import annotations

import importlib
import importlib.util
import sys
from datetime import date, timedelta
import subprocess
import textwrap
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting" / "verify_skill_catalog_freshness.py"
SHADOW_SCRIPT = REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting" / "check_plugin_skill_shadowing.sh"
SELECTION_POLICY_SCRIPT = REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync" / "selection_policy.py"
SKILL_DISCOVERY_SCRIPT = REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync" / "skill_discovery.py"
CODEX_PREVIEW_SCRIPT = REPO_ROOT / "Infrastructure" / "scripts" / "lib" / "ask" / "services" / "codex_preview.py"
RUNTIME_SURFACE_POLICY_SCRIPT = (
    REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync" / "runtime_surface_policy.py"
)
SYNC_SCRIPT = REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync" / "sync_skills.sh"
SYNC_IMPL_SCRIPT = REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync" / "sync_skills_impl.sh"
SKILLS_IMPL_SCRIPT = REPO_ROOT / "Infrastructure" / "scripts" / "lib" / "ask" / "commands" / "skills_impl.py"
# macOS ships bash 3.2 which lacks features (mapfile, declare -A) used by
# shell scripts in this repo. Prefer a known bash 4+ path when available.
def _find_bash4() -> str:
    import shutil
    for candidate in ["/opt/homebrew/bin/bash", "/usr/local/bin/bash"]:
        if shutil.which(candidate):
            return candidate
    return "bash"

_BASH4 = _find_bash4()


def run_validator(repo_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(SCRIPT), "--repo-root", str(repo_root), "--strict"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def run_shadow_check(repo_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [_BASH4, str(SHADOW_SCRIPT), "--repo-root", str(repo_root)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


def iso_days_ago(days: int) -> str:
    return (date.today() - timedelta(days=days)).isoformat()


def load_validator_module():
    spec = importlib.util.spec_from_file_location("verify_skill_catalog_freshness", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load validator module from {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_codex_preview_module():
    spec = importlib.util.spec_from_file_location("codex_preview", CODEX_PREVIEW_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load Codex preview module from {CODEX_PREVIEW_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_selection_policy_module():
    script_dir = str(SELECTION_POLICY_SCRIPT.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location("selection_policy", SELECTION_POLICY_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load selection policy module from {SELECTION_POLICY_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_skill_discovery_module():
    script_dir = str(SKILL_DISCOVERY_SCRIPT.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location("skill_discovery", SKILL_DISCOVERY_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load skill discovery module from {SKILL_DISCOVERY_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_runtime_surface_policy_module():
    script_dir = str(RUNTIME_SURFACE_POLICY_SCRIPT.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location("runtime_surface_policy", RUNTIME_SURFACE_POLICY_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load runtime surface policy module from {RUNTIME_SURFACE_POLICY_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_skills_impl_module():
    for path in (
        REPO_ROOT / "Infrastructure" / "scripts" / "lib",
        REPO_ROOT / "Infrastructure" / "scripts",
        REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync",
    ):
        script_dir = str(path)
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
    return importlib.import_module("ask.commands.skills_impl")
