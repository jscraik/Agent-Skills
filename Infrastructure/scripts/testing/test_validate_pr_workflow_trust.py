from __future__ import annotations

import copy
import shlex
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKOUT_ACTION = "actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0"
BASE_REFS = {
    "${{ github.event.pull_request.base.sha }}",
    "${{ github.event.pull_request.base.sha || github.event.merge_group.base_sha }}",
}
EXPECTED_JOBS = {
    "linear-gate",
    "risk-policy-gate",
    "consistency-drift-advisory",
    "consistency-drift-health",
}
APPROVED_HARNESS_ARGV = {
    (
        "bash",
        "trusted-base/Infrastructure/scripts/harness-cli.sh",
        "linear-gate",
        "--repo-root",
        "trusted-base",
        "--contract",
        "harness.contract.json",
        "--branch",
        branch,
        "--pr-title",
        "$PR_TITLE",
        "--pr-body",
        "$PR_BODY",
        "--json",
    )
    for branch in ("$HEAD_REF", "$BRANCH")
} | {
    (
        "bash",
        "trusted-base/Infrastructure/scripts/harness-cli.sh",
        "linear-gate",
        "--repo-root",
        "trusted-base",
        "--contract",
        "harness.contract.json",
        "--allow-missing-branch",
        "--allow-missing-pr",
        "--json",
    ),
    (
        "bash",
        "trusted-base/Infrastructure/scripts/harness-cli.sh",
        "preflight-gate",
        "--contract",
        "$CONTRACT_PATH",
        "--max-tier",
        "medium",
        "--files",
        "${CHANGED_FILES}",
        "--json",
    ),
    (
        "bash",
        "trusted-base/Infrastructure/scripts/harness-cli.sh",
        "drift-gate",
        "--mode",
        "advisory",
        "--out",
        "artifacts/consistency-gate/consistency-drift-advisory-latest.json",
        "--json",
    ),
    (
        "bash",
        "trusted-base/Infrastructure/scripts/harness-cli.sh",
        "drift-gate",
        "--mode",
        "health",
        "--out",
        "artifacts/consistency-gate/health.json",
        "--json",
    ),
}


def _workflow(relative_path: str) -> dict[object, object]:
    payload = yaml.safe_load((REPO_ROOT / relative_path).read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    if True in payload and "on" not in payload:
        payload["on"] = payload.pop(True)
    return payload


def _steps(job: dict[object, object]) -> list[dict[object, object]]:
    steps = job.get("steps")
    assert isinstance(steps, list)
    assert all(isinstance(step, dict) for step in steps)
    return steps


def _token_jobs(workflow: dict[object, object]) -> dict[str, dict[object, object]]:
    jobs = workflow.get("jobs")
    assert isinstance(jobs, dict)
    return {
        str(name): job
        for name, job in jobs.items()
        if isinstance(job, dict) and "${{ secrets.NPM_TOKEN }}" in str(job)
    }


def _assert_job_trust(job: dict[object, object]) -> None:
    steps = _steps(job)
    trusted = _trusted_checkouts(steps)
    assert len(trusted) == 1
    inputs = trusted[0]["with"]
    assert inputs.get("persist-credentials") is False
    assert inputs.get("ref") in BASE_REFS
    harness_runs = _harness_runs(steps)
    assert harness_runs
    assert all("trusted-base/Infrastructure/scripts/harness-cli.sh" in run for run in harness_runs)
    assert all("bash Infrastructure/scripts/harness-cli.sh" not in run for run in harness_runs)
    _assert_only_approved_harness_executables(steps)


def _assert_only_approved_harness_executables(steps: list[dict[object, object]]) -> None:
    for step in steps:
        run = str(step.get("run", ""))
        _assert_no_package_exec_runner(run)
        invocations = _approved_harness_invocations(run)
        for line in run.splitlines():
            stripped = line.strip()
            if "harness-cli.sh" in stripped and not stripped.startswith("#"):
                assert any(stripped in invocation for invocation in invocations)


def _assert_no_package_exec_runner(run: str) -> None:
    tokens = _shell_tokens(run)
    assert not any(_is_unsafe_harness_token(token) for token in tokens)
    assert not any(token in {"npx", "bunx"} for token in tokens)
    assert not any(
        token in {"npm", "pnpm", "yarn"}
        and index + 1 < len(tokens)
        and tokens[index + 1] in {"exec", "dlx"}
        for index, token in enumerate(tokens)
    )


def _is_unsafe_harness_token(token: str) -> bool:
    if "harness" not in token.lower():
        return False
    if token in {
        "trusted-base/Infrastructure/scripts/harness-cli.sh",
        "harness.contract.json",
        "CONTRACT_PATH=trusted-base/harness.contract.json",
    }:
        return False
    if token.startswith("::error::") or '"reason":"' in token:
        return False
    return True


def _shell_tokens(command: str) -> list[str]:
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
    lexer.commenters = "#"
    lexer.whitespace_split = True
    return list(lexer)


def _approved_harness_invocations(run: str) -> list[list[str]]:
    lines = run.splitlines()
    invocations: list[list[str]] = []
    index = 0
    approved_prefix = "bash trusted-base/Infrastructure/scripts/harness-cli.sh "
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith("#") or "harness-cli.sh" not in stripped:
            index += 1
            continue
        assert stripped.startswith(approved_prefix)
        block = [stripped]
        while block[-1].endswith("\\"):
            index += 1
            assert index < len(lines)
            block.append(lines[index].strip())
        tokens = _shell_tokens(" ".join(line.removesuffix("\\").strip() for line in block))
        assert tuple(tokens) in APPROVED_HARNESS_ARGV
        invocations.append(block)
        index += 1
    return invocations


def _assert_linear_gate_policy_root(job: dict[object, object]) -> None:
    linear_runs = [run for run in _harness_runs(_steps(job)) if " linear-gate " in run]
    assert linear_runs
    for run in linear_runs:
        invocations = _linear_invocations(run)
        assert invocations
        for invocation in invocations:
            tokens = shlex.split(" ".join(line.removesuffix("\\").strip() for line in invocation))
            _assert_exact_flag(tokens, "--repo-root", "trusted-base")
            _assert_exact_flag(tokens, "--contract", "harness.contract.json")


def _assert_exact_flag(tokens: list[str], flag: str, expected_value: str) -> None:
    assert all(not token.startswith(f"{flag}=") for token in tokens)
    assert tokens.count(flag) == 1
    flag_index = tokens.index(flag)
    assert flag_index + 1 < len(tokens)
    assert tokens[flag_index + 1] == expected_value


def _linear_invocations(run: str) -> list[list[str]]:
    invocations = _approved_harness_invocations(run)
    assert all(
        _shell_tokens(invocation[0].removesuffix("\\").strip())[:3]
        == ["bash", "trusted-base/Infrastructure/scripts/harness-cli.sh", "linear-gate"]
        for invocation in invocations
    )
    return invocations


def _trusted_checkouts(steps: list[dict[object, object]]) -> list[dict[object, object]]:
    return [
        step
        for step in steps
        if step.get("uses") == CHECKOUT_ACTION
        and isinstance(step.get("with"), dict)
        and step["with"].get("path") == "trusted-base"
    ]


def _harness_runs(steps: list[dict[object, object]]) -> list[str]:
    return [str(step.get("run")) for step in steps if "harness-cli.sh" in str(step.get("run"))]


def _linear_command(job: dict[object, object]) -> dict[object, object]:
    return next(step for step in _steps(job) if " linear-gate " in str(step.get("run")))


def _assert_repo_root_mutation_rejected(job: dict[object, object], unsafe_root: str) -> None:
    variant = copy.deepcopy(job)
    command = _linear_command(variant)
    command["run"] = str(command["run"]).replace(
        "--repo-root trusted-base",
        f"--repo-root {unsafe_root}",
    )
    with pytest.raises(AssertionError):
        _assert_linear_gate_policy_root(variant)


def _assert_missing_contract_rejected(job: dict[object, object]) -> None:
    variant = copy.deepcopy(job)
    command = _linear_command(variant)
    command["run"] = str(command["run"]).replace("--contract harness.contract.json", "")
    with pytest.raises(AssertionError):
        _assert_linear_gate_policy_root(variant)


def _assert_duplicate_root_rejected(job: dict[object, object]) -> None:
    variant = copy.deepcopy(job)
    command = _linear_command(variant)
    command["run"] = str(command["run"]).replace(
        "--repo-root trusted-base \\",
        "--repo-root trusted-base \\\n  --repo-root trusted-base \\",
        1,
    )
    with pytest.raises(AssertionError):
        _assert_linear_gate_policy_root(variant)


def _assert_unbalanced_invocations_rejected(job: dict[object, object]) -> None:
    variant = copy.deepcopy(job)
    command = _linear_command(variant)
    run = str(command["run"])
    run = run.replace("--repo-root trusted-base \\\n", "", 1)
    run = run.replace("--contract harness.contract.json \\\n", "", 1)
    run = run.replace(
        "--repo-root trusted-base \\",
        "--repo-root trusted-base \\\n    --repo-root trusted-base \\",
        1,
    )
    run = run.replace(
        "--contract harness.contract.json \\",
        "--contract harness.contract.json \\\n    --contract harness.contract.json \\",
        1,
    )
    command["run"] = run
    with pytest.raises(AssertionError):
        _assert_linear_gate_policy_root(variant)


def _assert_decoy_flags_rejected(job: dict[object, object]) -> None:
    variant = copy.deepcopy(job)
    command = _linear_command(variant)
    run = str(command["run"])
    run = run.replace("--repo-root trusted-base \\\n", "", 1)
    run = run.replace("--contract harness.contract.json \\\n", "", 1)
    decoy = (
        "printf 'decoy' \\\n"
        "  --repo-root trusted-base \\\n"
        "  --contract harness.contract.json \\\n"
        "  >/dev/null\n"
    )
    command["run"] = f"{decoy}{run}"
    with pytest.raises(AssertionError):
        _assert_linear_gate_policy_root(variant)


def test_all_token_bearing_jobs_use_trusted_base_wrappers() -> None:
    workflows = (
        _workflow(".github/workflows/pr-template.yml"),
        _workflow(".github/workflows/pr-pipeline.yml"),
    )
    jobs = {name: job for workflow in workflows for name, job in _token_jobs(workflow).items()}
    assert set(jobs) == EXPECTED_JOBS
    for job in jobs.values():
        _assert_job_trust(job)


def test_linear_gates_bind_policy_inputs_to_trusted_base_checkout() -> None:
    workflows = (
        _workflow(".github/workflows/pr-template.yml"),
        _workflow(".github/workflows/pr-pipeline.yml"),
    )
    for workflow in workflows:
        jobs = workflow["jobs"]
        assert isinstance(jobs, dict)
        job = jobs["linear-gate"]
        assert isinstance(job, dict)
        _assert_linear_gate_policy_root(job)

        for unsafe_root in (".", "trusted-base/..", "${{ github.workspace }}"):
            _assert_repo_root_mutation_rejected(job, unsafe_root)
        _assert_missing_contract_rejected(job)
        _assert_duplicate_root_rejected(job)


def test_linear_gate_rejects_cross_invocation_flag_redistribution() -> None:
    pipeline = _workflow(".github/workflows/pr-pipeline.yml")
    jobs = pipeline["jobs"]
    assert isinstance(jobs, dict)
    job = jobs["linear-gate"]
    assert isinstance(job, dict)
    _assert_unbalanced_invocations_rejected(job)


def test_linear_gate_rejects_policy_flags_attached_to_decoy_command() -> None:
    metadata = _workflow(".github/workflows/pr-template.yml")
    jobs = metadata["jobs"]
    assert isinstance(jobs, dict)
    job = jobs["linear-gate"]
    assert isinstance(job, dict)
    _assert_decoy_flags_rejected(job)


def test_alternate_token_bearing_harness_job_is_governed_and_rejected() -> None:
    pipeline = _workflow(".github/workflows/pr-pipeline.yml")
    jobs = pipeline["jobs"]
    assert isinstance(jobs, dict)
    jobs["alternate-harness"] = {
        "runs-on": "ubuntu-latest",
        "env": {"NODE_AUTH_TOKEN": "${{ secrets.NPM_TOKEN }}"},
        "steps": [{"run": "npm exec -- harness linear-gate --json"}],
    }
    token_jobs = _token_jobs(pipeline)
    assert "alternate-harness" in token_jobs
    with pytest.raises(AssertionError):
        _assert_job_trust(token_jobs["alternate-harness"])


@pytest.mark.parametrize(
    "extra_flag",
    (
        "--repo-root attacker",
        "--repo-root=attacker",
        "--contract attacker.json",
        "--contract=attacker.json",
    ),
)
def test_linear_gate_rejects_conflicting_effective_flags(extra_flag: str) -> None:
    metadata = _workflow(".github/workflows/pr-template.yml")
    jobs = metadata["jobs"]
    assert isinstance(jobs, dict)
    job = copy.deepcopy(jobs["linear-gate"])
    assert isinstance(job, dict)
    command = _linear_command(job)
    command["run"] = str(command["run"]).replace(
        "--json",
        f"{extra_flag} \\\n  --json",
        1,
    )
    with pytest.raises(AssertionError):
        _assert_linear_gate_policy_root(job)


def test_approved_wrapper_cannot_mask_alternate_harness_execution() -> None:
    pipeline = _workflow(".github/workflows/pr-pipeline.yml")
    jobs = pipeline["jobs"]
    assert isinstance(jobs, dict)
    job = copy.deepcopy(jobs["linear-gate"])
    assert isinstance(job, dict)
    job_steps = _steps(job)
    job_steps.append({"run": "npm exec -- harness linear-gate --json"})
    with pytest.raises(AssertionError):
        _assert_job_trust(job)


@pytest.mark.parametrize(
    "alternate_execution",
    (
        "; npm  exec -- harness linear-gate --json",
        "&& npx\tharness linear-gate --json",
        "&& command harness linear-gate --json",
        "&& bunx harness linear-gate --json",
        "&& yarn dlx harness linear-gate --json",
        "|| true",
    ),
)
def test_approved_wrapper_rejects_chained_execution_or_success_override(
    alternate_execution: str,
) -> None:
    metadata = _workflow(".github/workflows/pr-template.yml")
    jobs = metadata["jobs"]
    assert isinstance(jobs, dict)
    job = copy.deepcopy(jobs["linear-gate"])
    assert isinstance(job, dict)
    command = _linear_command(job)
    command["run"] = str(command["run"]).replace("--json", f"--json {alternate_execution}", 1)
    with pytest.raises(AssertionError):
        _assert_job_trust(job)


@pytest.mark.parametrize(
    "alternate_execution",
    (
        "command npm  exec -- harness linear-gate --json",
        "command npx\tharness linear-gate --json",
        "command bunx harness linear-gate --json",
        "command yarn dlx harness linear-gate --json",
    ),
)
def test_approved_wrapper_rejects_sibling_alternate_execution(
    alternate_execution: str,
) -> None:
    metadata = _workflow(".github/workflows/pr-template.yml")
    jobs = metadata["jobs"]
    assert isinstance(jobs, dict)
    job = copy.deepcopy(jobs["linear-gate"])
    assert isinstance(job, dict)
    _steps(job).append({"run": alternate_execution})
    with pytest.raises(AssertionError):
        _assert_job_trust(job)


def test_shell_comments_may_describe_harness_commands_without_executing_them() -> None:
    metadata = _workflow(".github/workflows/pr-template.yml")
    jobs = metadata["jobs"]
    assert isinstance(jobs, dict)
    job = copy.deepcopy(jobs["linear-gate"])
    assert isinstance(job, dict)
    _steps(job).append(
        {
            "run": (
                "# npx harness is intentionally prohibited here\n"
                "# bash trusted-base/Infrastructure/scripts/harness-cli.sh is the approved route"
            )
        }
    )
    _assert_job_trust(job)


@pytest.mark.parametrize(
    "alternate_execution",
    (
        "bash -c 'harness linear-gate --json'",
        "sh -c 'npm exec -- harness linear-gate --json'",
        "eval 'harness linear-gate --json'",
        "runner=harness; \"$runner\" linear-gate --json",
        "/tmp/harness linear-gate --json",
        "env SAFE=1 /tmp/harness linear-gate --json",
        "result=$(/tmp/harness linear-gate --json)",
        "result=`/tmp/harness linear-gate --json`",
    ),
)
def test_token_job_rejects_indirect_or_absolute_harness_execution(
    alternate_execution: str,
) -> None:
    metadata = _workflow(".github/workflows/pr-template.yml")
    jobs = metadata["jobs"]
    assert isinstance(jobs, dict)
    job = copy.deepcopy(jobs["linear-gate"])
    assert isinstance(job, dict)
    _steps(job).append({"run": alternate_execution})
    with pytest.raises(AssertionError):
        _assert_job_trust(job)


@pytest.mark.parametrize(
    "trailing_syntax",
    (
        "--undeclared value",
        "<<'EOF'\npayload\nEOF",
    ),
)
def test_approved_wrapper_rejects_argv_or_redirection_outside_closed_contract(
    trailing_syntax: str,
) -> None:
    metadata = _workflow(".github/workflows/pr-template.yml")
    jobs = metadata["jobs"]
    assert isinstance(jobs, dict)
    job = copy.deepcopy(jobs["linear-gate"])
    assert isinstance(job, dict)
    command = _linear_command(job)
    command["run"] = str(command["run"]).replace(
        "--json",
        f"--json {trailing_syntax}",
        1,
    )
    with pytest.raises(AssertionError):
        _assert_job_trust(job)


def test_pr_workflow_contract_suites_are_wired_into_required_test_scope() -> None:
    validate_all = (REPO_ROOT / "Infrastructure" / "scripts" / "validate_all_impl.sh").read_text(
        encoding="utf-8"
    )
    assert "skill-lifecycle-tests|pr-template-contract-tests|skill-authoring-family" in validate_all
    assert 'pr-template-contract-tests "🧾 Validating PR metadata workflow contracts..."' in validate_all
    assert "scripts/testing/test_validate_pr_template_body.py" in validate_all
    assert "scripts/testing/test_validate_pr_workflow_trust.py" in validate_all


@pytest.mark.parametrize(
    ("job_name", "checkout_name", "command_name"),
    (
        ("consistency-drift-advisory", "Checkout trusted advisory drift gate", "Run advisory drift gate"),
        ("consistency-drift-health", "Checkout trusted health drift gate", "Run health drift gate"),
    ),
)
def test_drift_jobs_reject_head_checkout_and_checkout_owned_wrapper(
    job_name: str,
    checkout_name: str,
    command_name: str,
) -> None:
    pipeline = _workflow(".github/workflows/pr-pipeline.yml")
    jobs = pipeline["jobs"]
    assert isinstance(jobs, dict)
    job = jobs[job_name]
    assert isinstance(job, dict)

    head_variant = copy.deepcopy(job)
    checkout = next(step for step in _steps(head_variant) if step.get("name") == checkout_name)
    checkout["with"]["ref"] = "${{ github.event.pull_request.head.sha }}"
    with pytest.raises(AssertionError):
        _assert_job_trust(head_variant)

    wrapper_variant = copy.deepcopy(job)
    command = next(step for step in _steps(wrapper_variant) if step.get("name") == command_name)
    command["run"] = str(command["run"]).replace(
        "trusted-base/Infrastructure/scripts/harness-cli.sh",
        "Infrastructure/scripts/harness-cli.sh",
    )
    with pytest.raises(AssertionError):
        _assert_job_trust(wrapper_variant)
