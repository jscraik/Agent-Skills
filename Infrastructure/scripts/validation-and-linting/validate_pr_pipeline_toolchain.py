#!/usr/bin/env python3
"""Validate the Python and uv prerequisites for PR validation jobs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tomllib
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "pr-pipeline.yml"
MISE_CONFIG = REPO_ROOT / ".mise.toml"
REQUIRED_SCOPES = ("audit", "check")
PYTHON_VERSION = "3.12"


def _uv_package() -> str:
    """Read the canonical uv version from the repository toolchain contract."""
    with MISE_CONFIG.open("rb") as handle:
        config = tomllib.load(handle)
    tools = config.get("tools")
    if not isinstance(tools, dict) or not isinstance(tools.get("uv"), str):
        raise ValueError(".mise.toml must define tools.uv as a version string")
    return f"uv=={tools['uv']}"


def parse_args() -> argparse.Namespace:
    """Parse the workflow path and optional machine-readable output flag."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow", type=Path, default=DEFAULT_WORKFLOW)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def _steps_for_job(workflow: dict[str, Any], scope: str) -> list[dict[str, Any]]:
    jobs = workflow.get("jobs")
    if not isinstance(jobs, dict):
        return []
    job = jobs.get(scope)
    if not isinstance(job, dict):
        return []
    steps = job.get("steps")
    if not isinstance(steps, list):
        return []
    return [step for step in steps if isinstance(step, dict)]


def _validation_index(steps: list[dict[str, Any]], scope: str) -> int | None:
    command = f"./bin/ask repo validate --scope={scope}"
    return next((index for index, step in enumerate(steps) if step.get("run") == command), None)


def _python_setup_index(steps: list[dict[str, Any]]) -> int | None:
    for index, step in enumerate(steps):
        uses = step.get("uses")
        with_values = step.get("with")
        if (
            isinstance(uses, str)
            and uses.startswith("actions/setup-python@")
            and isinstance(with_values, dict)
            and str(with_values.get("python-version")) == PYTHON_VERSION
        ):
            return index
    return None


def _uv_install_index(steps: list[dict[str, Any]], uv_package: str) -> int | None:
    return next(
        (
            index
            for index, step in enumerate(steps)
            if isinstance(step.get("run"), str)
            and "python -m pip install" in step["run"]
            and uv_package in step["run"]
        ),
        None,
    )


def validate(workflow: dict[str, Any]) -> list[str]:
    """Return prerequisite violations for each uv-backed validation job."""
    violations: list[str] = []
    try:
        uv_package = _uv_package()
    except (OSError, tomllib.TOMLDecodeError, ValueError) as error:
        return [f"toolchain contract load failed: {error}"]

    for scope in REQUIRED_SCOPES:
        steps = _steps_for_job(workflow, scope)
        if not steps:
            violations.append(f"{scope}: missing job steps")
            continue

        validation = _validation_index(steps, scope)
        if validation is None:
            violations.append(f"{scope}: missing validation command")
            continue

        python_setup = _python_setup_index(steps)
        if python_setup is None:
            violations.append(
                f"{scope}: missing actions/setup-python with python-version {PYTHON_VERSION} before validation"
            )
        elif python_setup >= validation:
            violations.append(f"{scope}: Python {PYTHON_VERSION} setup must precede validation")

        uv_install = _uv_install_index(steps, uv_package)
        if uv_install is None or uv_install >= validation:
            violations.append(f"{scope}: missing {uv_package} installation before validation")
        elif python_setup is not None and python_setup >= uv_install:
            violations.append(f"{scope}: Python {PYTHON_VERSION} setup must precede {uv_package} installation")
    return violations


def main() -> int:
    """Load the workflow, emit the validation result, and return its status."""
    args = parse_args()
    try:
        loaded = yaml.safe_load(args.workflow.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        violations = [f"workflow load failed: {error}"]
    else:
        violations = validate(loaded) if isinstance(loaded, dict) else ["workflow root must be a mapping"]

    payload = {"status": "pass" if not violations else "fail", "violations": violations}
    if args.as_json:
        print(json.dumps(payload, sort_keys=True))
    elif violations:
        print("PR pipeline toolchain validation failed:")
        for violation in violations:
            print(f"- {violation}")
    else:
        print("PR pipeline toolchain validation passed.")
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())
