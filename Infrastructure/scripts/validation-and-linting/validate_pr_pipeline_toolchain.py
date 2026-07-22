#!/usr/bin/env python3
"""Validate the Python and uv prerequisites for PR validation jobs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "pr-pipeline.yml"
DEFAULT_BOOTSTRAP_ACTION = REPO_ROOT / ".github" / "actions" / "bootstrap-locked-python" / "action.yml"
MISE_CONFIG = REPO_ROOT / ".mise.toml"
UV_BACKED_VALIDATION_SCOPES = ("audit", "check")
LOCKED_PYTHON_VALIDATION_SCOPES = ("lint", "typecheck", "test")
BOOTSTRAP_ACTION_USES = "./.github/actions/bootstrap-locked-python"
PYTHON_VERSION = "3.12"


def _uv_package() -> str:
    """Read the canonical uv version from the repository toolchain contract."""
    try:
        config = MISE_CONFIG.read_text(encoding="utf-8")
    except OSError as error:
        raise ValueError(f"could not read {MISE_CONFIG.name}: {error}") from error

    in_tools = False
    for line in config.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_tools = stripped == "[tools]"
            continue
        if not in_tools:
            continue
        uv_version = re.fullmatch(r'"?uv"?\s*=\s*"(?P<version>[^"]+)"', stripped)
        if uv_version is not None:
            return f"uv=={uv_version.group('version')}"

    raise ValueError(".mise.toml must define tools.uv as a version string")


def parse_args() -> argparse.Namespace:
    """Parse the workflow path and optional machine-readable output flag."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow", type=Path, default=DEFAULT_WORKFLOW)
    parser.add_argument("--bootstrap-action", type=Path, default=DEFAULT_BOOTSTRAP_ACTION)
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
            and re.search(rf'\b{re.escape(uv_package)}(?:\s|$)', step["run"])
        ),
        None,
    )


def _bootstrap_index(steps: list[dict[str, Any]]) -> int | None:
    return next(
        (
            index
            for index, step in enumerate(steps)
            if step.get("run") == "bash scripts/bootstrap-ask.sh --json"
        ),
        None,
    )


def _bootstrap_action_index(steps: list[dict[str, Any]]) -> int | None:
    return next(
        (index for index, step in enumerate(steps) if step.get("uses") == BOOTSTRAP_ACTION_USES),
        None,
    )


def _required_before(
    index: int | None,
    boundary: int,
    missing_message: str,
    late_message: str | None = None,
    predecessor: int | None = None,
    predecessor_message: str | None = None,
) -> str | None:
    if index is None:
        return missing_message
    if index >= boundary:
        return late_message or missing_message
    if predecessor is not None and predecessor >= index:
        return predecessor_message
    return None


def _scope_violations(scope: str, steps: list[dict[str, Any]], uv_package: str) -> list[str]:
    if not steps:
        return [f"{scope}: missing job steps"]
    validation = _validation_index(steps, scope)
    if validation is None:
        return [f"{scope}: missing validation command"]

    if scope in LOCKED_PYTHON_VALIDATION_SCOPES:
        message = _required_before(
            _bootstrap_action_index(steps),
            validation,
            f"{scope}: missing {BOOTSTRAP_ACTION_USES} before validation",
        )
        return [message] if message else []

    python_setup = _python_setup_index(steps)
    uv_install = _uv_install_index(steps, uv_package)
    messages = [
        _required_before(
            python_setup,
            validation,
            f"{scope}: missing actions/setup-python with python-version {PYTHON_VERSION} before validation",
            f"{scope}: Python {PYTHON_VERSION} setup must precede validation",
        ),
        _required_before(
            uv_install,
            validation,
            f"{scope}: missing {uv_package} installation before validation",
            predecessor=python_setup,
            predecessor_message=f"{scope}: Python {PYTHON_VERSION} setup must precede {uv_package} installation",
        ),
    ]
    return [message for message in messages if message]


def _bootstrap_action_violations(action: dict[str, Any], uv_package: str) -> list[str]:
    runs = action.get("runs")
    if not isinstance(runs, dict) or runs.get("using") != "composite":
        return ["bootstrap action: runs.using must be composite"]
    steps = runs.get("steps")
    if not isinstance(steps, list):
        return ["bootstrap action: runs.steps must be a list"]
    action_steps = [step for step in steps if isinstance(step, dict)]
    python_setup = _python_setup_index(action_steps)
    uv_install = _uv_install_index(action_steps, uv_package)
    bootstrap = _bootstrap_index(action_steps)
    messages = [
        _required_before(
            python_setup,
            len(action_steps),
            f"bootstrap action: missing actions/setup-python with python-version {PYTHON_VERSION}",
        ),
        _required_before(
            uv_install,
            len(action_steps),
            f"bootstrap action: missing {uv_package} installation",
            predecessor=python_setup,
            predecessor_message=f"bootstrap action: Python {PYTHON_VERSION} setup must precede {uv_package} installation",
        ),
        _required_before(
            bootstrap,
            len(action_steps),
            "bootstrap action: missing locked Python bootstrap",
            predecessor=uv_install,
            predecessor_message=f"bootstrap action: {uv_package} installation must precede locked Python bootstrap",
        ),
    ]
    for index in (uv_install, bootstrap):
        if index is not None and action_steps[index].get("shell") != "bash":
            messages.append("bootstrap action: run steps must declare shell: bash")
    return [message for message in messages if message]


def validate(workflow: dict[str, Any], bootstrap_action: dict[str, Any]) -> list[str]:
    """Return prerequisite violations for uv-backed and locked-Python validation jobs."""
    try:
        uv_package = _uv_package()
    except ValueError as error:
        return [f"toolchain contract load failed: {error}"]

    scopes = (*UV_BACKED_VALIDATION_SCOPES, *LOCKED_PYTHON_VALIDATION_SCOPES)
    return _bootstrap_action_violations(bootstrap_action, uv_package) + [
        violation
        for scope in scopes
        for violation in _scope_violations(scope, _steps_for_job(workflow, scope), uv_package)
    ]


def main() -> int:
    """Load the workflow, emit the validation result, and return its status."""
    args = parse_args()
    try:
        loaded = yaml.safe_load(args.workflow.read_text(encoding="utf-8"))
        bootstrap_action = yaml.safe_load(args.bootstrap_action.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        violations = [f"workflow or bootstrap action load failed: {error}"]
    else:
        if not isinstance(loaded, dict):
            violations = ["workflow root must be a mapping"]
        elif not isinstance(bootstrap_action, dict):
            violations = ["bootstrap action root must be a mapping"]
        else:
            violations = validate(loaded, bootstrap_action)

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
