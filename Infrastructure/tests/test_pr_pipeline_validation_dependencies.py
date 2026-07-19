"""Regression coverage for PR validation-job toolchain prerequisites."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import tomllib

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "pr-pipeline.yml"
VALIDATOR_PATH = REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting" / "validate_pr_pipeline_toolchain.py"
UV_BACKED_VALIDATION_SCOPES = ("audit", "check")
PYTHON_VERSION = "3.12"
with (REPO_ROOT / ".mise.toml").open("rb") as handle:
    UV_VERSION = tomllib.load(handle)["tools"]["uv"]


def _workflow_jobs() -> dict[str, object]:
    workflow = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
    return workflow["jobs"]


def _job_steps(job: object) -> list[dict[str, object]]:
    assert isinstance(job, dict)
    steps = job["steps"]
    assert isinstance(steps, list)
    return [step for step in steps if isinstance(step, dict)]


def _validation_step_index(steps: list[dict[str, object]], scope: str) -> int:
    expected = f"./bin/ask repo validate --scope={scope}"
    return next(index for index, step in enumerate(steps) if step.get("run") == expected)


def _python_setup_index(steps: list[dict[str, object]]) -> int:
    return next(
        index
        for index, step in enumerate(steps)
        if isinstance(step.get("uses"), str)
        and step["uses"].startswith("actions/setup-python@")
        and isinstance(step.get("with"), dict)
        and str(step["with"].get("python-version")) == PYTHON_VERSION
    )


def _uv_install_index(steps: list[dict[str, object]]) -> int:
    return next(
        index
        for index, step in enumerate(steps)
        if isinstance(step.get("run"), str)
        and "python -m pip install" in step["run"]
        and f"uv=={UV_VERSION}" in step["run"]
    )


def test_uv_backed_validation_jobs_materialize_uv_before_execution() -> None:
    jobs = _workflow_jobs()

    for scope in UV_BACKED_VALIDATION_SCOPES:
        steps = _job_steps(jobs[scope])

        python_setup = _python_setup_index(steps)
        uv_install = _uv_install_index(steps)
        validation = _validation_step_index(steps, scope)

        assert python_setup < uv_install < validation, (
            f"{scope} must set up Python {PYTHON_VERSION} and install uv=={UV_VERSION} "
            "before its validation command"
        )


def _run_validator(workflow_text: str) -> subprocess.CompletedProcess[str]:
    with TemporaryDirectory() as temp_dir:
        workflow = Path(temp_dir) / "pr-pipeline.yml"
        workflow.write_text(workflow_text, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), "--workflow", str(workflow), "--json"],
            text=True,
            capture_output=True,
            check=False,
        )


def test_toolchain_validator_rejects_wrong_version_and_late_uv_install() -> None:
    workflow = f"""\
jobs:
  audit:
    steps:
      - uses: actions/setup-python@abc
        with:
          python-version: "3.11"
      - run: ./bin/ask repo validate --scope=audit
      - run: python -m pip install --upgrade pip uv==0.10.0 pyyaml pytest jsonschema
  check:
    steps:
      - uses: actions/setup-python@abc
        with:
          python-version: "3.12"
      - run: python -m pip install --upgrade pip uv=={UV_VERSION}0 pyyaml pytest jsonschema
      - run: ./bin/ask repo validate --scope=check
"""

    result = _run_validator(workflow)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "fail"
    messages = "\n".join(payload["violations"])
    assert "audit: missing actions/setup-python with python-version 3.12" in messages
    assert f"audit: missing uv=={UV_VERSION} installation before validation" in messages
    assert f"check: missing uv=={UV_VERSION} installation before validation" in messages
