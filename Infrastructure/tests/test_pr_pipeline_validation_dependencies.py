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
BOOTSTRAP_ACTION_PATH = REPO_ROOT / ".github" / "actions" / "bootstrap-locked-python" / "action.yml"
VALIDATOR_PATH = REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting" / "validate_pr_pipeline_toolchain.py"
LOCKED_PYTHON_VALIDATION_SCOPES = ("lint", "typecheck", "test")
BOOTSTRAP_ACTION_USES = "./.github/actions/bootstrap-locked-python"
PYTHON_VERSION = "3.12"
LOCKED_BOOTSTRAP_COMMAND = (
    "uv run --frozen --project Infrastructure --group test --group lint "
    "bash scripts/bootstrap-ask.sh --json"
)
LOCKED_VALIDATION_PREFIX = "uv run --frozen --project Infrastructure --group test --group lint ./bin/ask"
with (REPO_ROOT / ".mise.toml").open("rb") as handle:
    UV_VERSION = tomllib.load(handle)["tools"]["uv"]


def _workflow_jobs() -> dict[str, object]:
    workflow = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
    return workflow["jobs"]


def _workflow_triggers() -> dict[str, object]:
    workflow = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
    triggers = workflow.get("on", workflow.get(True))
    assert isinstance(triggers, dict)
    return triggers


def _bootstrap_action_steps() -> list[dict[str, object]]:
    action = yaml.safe_load(BOOTSTRAP_ACTION_PATH.read_text(encoding="utf-8"))
    assert isinstance(action, dict)
    runs = action["runs"]
    assert isinstance(runs, dict)
    assert runs["using"] == "composite"
    steps = runs["steps"]
    assert isinstance(steps, list)
    return [step for step in steps if isinstance(step, dict)]


def test_pr_template_revalidates_when_pull_request_description_changes() -> None:
    triggers = _workflow_triggers()

    pull_request = triggers["pull_request"]

    assert isinstance(pull_request, dict)
    assert set(pull_request["types"]) == {"opened", "reopened", "synchronize", "edited"}
    assert triggers["merge_group"] is None


def _job_steps(job: object) -> list[dict[str, object]]:
    assert isinstance(job, dict)
    steps = job["steps"]
    assert isinstance(steps, list)
    return [step for step in steps if isinstance(step, dict)]


def _validation_command(scope: str) -> str:
    prefix = LOCKED_VALIDATION_PREFIX if scope in LOCKED_PYTHON_VALIDATION_SCOPES else "./bin/ask"
    return f"{prefix} repo validate --scope={scope}"


def _validation_step_index(steps: list[dict[str, object]], scope: str) -> int:
    expected = _validation_command(scope)
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


def _bootstrap_index(steps: list[dict[str, object]]) -> int:
    return next(
        index
        for index, step in enumerate(steps)
        if step.get("run") == LOCKED_BOOTSTRAP_COMMAND
    )


def _bootstrap_action_index(steps: list[dict[str, object]]) -> int:
    return next(index for index, step in enumerate(steps) if step.get("uses") == BOOTSTRAP_ACTION_USES)


def test_locked_python_validation_jobs_bootstrap_before_execution() -> None:
    jobs = _workflow_jobs()
    action_steps = _bootstrap_action_steps()

    python_setup = _python_setup_index(action_steps)
    uv_install = _uv_install_index(action_steps)
    bootstrap = _bootstrap_index(action_steps)
    assert python_setup < uv_install < bootstrap, (
        "the shared bootstrap action must set up Python, install uv, and bootstrap "
        "the locked Infrastructure environment in that order"
    )
    assert action_steps[uv_install]["run"] == (
        f"python -m pip install --disable-pip-version-check uv=={UV_VERSION}"
    )
    assert action_steps[bootstrap]["run"] == LOCKED_BOOTSTRAP_COMMAND

    for scope in LOCKED_PYTHON_VALIDATION_SCOPES:
        steps = _job_steps(jobs[scope])

        bootstrap_action = _bootstrap_action_index(steps)
        validation = _validation_step_index(steps, scope)

        assert bootstrap_action < validation, (
            f"{scope} must invoke the shared locked-Python bootstrap action before "
            "its validation command"
        )


def _run_validator(
    workflow_text: str, bootstrap_action_text: str | None = None
) -> subprocess.CompletedProcess[str]:
    with TemporaryDirectory() as temp_dir:
        workflow = Path(temp_dir) / "pr-pipeline.yml"
        workflow.write_text(workflow_text, encoding="utf-8")
        bootstrap_action = Path(temp_dir) / "action.yml"
        if bootstrap_action_text is not None:
            bootstrap_action.write_text(bootstrap_action_text, encoding="utf-8")
        return subprocess.run(
            [
                sys.executable,
                str(VALIDATOR_PATH),
                "--workflow",
                str(workflow),
                "--bootstrap-action",
                str(bootstrap_action if bootstrap_action_text is not None else BOOTSTRAP_ACTION_PATH),
                "--json",
            ],
            text=True,
            capture_output=True,
            check=False,
        )


def _workflow_with_shared_bootstrap_action() -> str:
    jobs = {
        scope: {
            "steps": [
                {"uses": "actions/setup-python@abc", "with": {"python-version": PYTHON_VERSION}},
                {"run": f"python -m pip install --upgrade pip uv=={UV_VERSION} pyyaml pytest jsonschema"},
                {"run": _validation_command(scope)},
            ]
        }
        for scope in ("audit", "check")
    }
    jobs.update(
        {
            scope: {
                "steps": [{"uses": BOOTSTRAP_ACTION_USES}, {"run": _validation_command(scope)}]
            }
            for scope in LOCKED_PYTHON_VALIDATION_SCOPES
        }
    )
    return yaml.safe_dump({"jobs": jobs}, sort_keys=False)


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


def test_toolchain_validator_rejects_missing_locked_python_bootstrap() -> None:
    workflow = f"""\
jobs:
  lint:
    steps:
      - uses: actions/setup-python@abc
        with:
          python-version: "3.12"
      - run: python -m pip install --upgrade pip uv=={UV_VERSION} pyyaml pytest jsonschema
      - run: {LOCKED_VALIDATION_PREFIX} repo validate --scope=lint
  typecheck:
    steps:
      - uses: actions/setup-python@abc
        with:
          python-version: "3.12"
      - run: python -m pip install --upgrade pip uv=={UV_VERSION} pyyaml pytest jsonschema
      - run: {LOCKED_VALIDATION_PREFIX} repo validate --scope=typecheck
  test:
    steps:
      - uses: actions/setup-python@abc
        with:
          python-version: "3.12"
      - run: python -m pip install --upgrade pip uv=={UV_VERSION} pyyaml pytest jsonschema
      - run: {LOCKED_VALIDATION_PREFIX} repo validate --scope=test
"""

    result = _run_validator(workflow)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "fail"
    messages = "\n".join(payload["violations"])
    for scope in LOCKED_PYTHON_VALIDATION_SCOPES:
        assert f"{scope}: missing {BOOTSTRAP_ACTION_USES} before validation" in messages


def test_toolchain_validator_rejects_incomplete_shared_bootstrap_action() -> None:
    workflow = _workflow_with_shared_bootstrap_action()
    incomplete_action = """\
runs:
  using: composite
  steps:
    - uses: actions/setup-python@abc
      with:
        python-version: "3.12"
    - shell: bash
      run: python -m pip install --upgrade pip uv==0.0.0 pyyaml pytest jsonschema
"""

    result = _run_validator(workflow, incomplete_action)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "fail"
    messages = "\n".join(payload["violations"])
    assert "bootstrap action: missing actions/setup-python with python-version 3.12" in messages
    assert f"bootstrap action: missing uv=={UV_VERSION} installation" in messages
    assert "bootstrap action: missing locked Python bootstrap" in messages
