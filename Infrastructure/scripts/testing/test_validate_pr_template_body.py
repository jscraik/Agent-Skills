from __future__ import annotations

import copy
import importlib.util
import re
import sys
from pathlib import Path
from types import ModuleType

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_validator() -> ModuleType:
    path = REPO_ROOT / ".github" / "scripts" / "validate_pr_template_body.py"
    spec = importlib.util.spec_from_file_location("validate_pr_template_body", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _template() -> str:
    return (REPO_ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")


def _workflow(relative_path: str) -> dict[object, object]:
    payload = yaml.safe_load((REPO_ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"Workflow must be a mapping: {relative_path}")
    # PyYAML's YAML 1.1 loader treats the unquoted GitHub Actions `on` key as true.
    if True in payload and "on" not in payload:
        payload["on"] = payload.pop(True)
    return payload


def _mapping(value: object, label: str) -> dict[object, object]:
    if not isinstance(value, dict):
        raise TypeError(f"{label} must be a mapping")
    return value


def _steps(job: dict[object, object]) -> list[dict[object, object]]:
    raw_steps = job.get("steps")
    if not isinstance(raw_steps, list) or not all(isinstance(step, dict) for step in raw_steps):
        raise TypeError("workflow job steps must be a list of mappings")
    return raw_steps


def _named_step(job: dict[object, object], name: str) -> dict[object, object]:
    for step in _steps(job):
        if step.get("name") == name:
            return step
    raise AssertionError(f"Missing workflow step: {name}")


def _assert_pr_template_refresh_contract(
    template_workflow: dict[object, object],
    pipeline_workflow: dict[object, object],
) -> None:
    _assert_refresh_triggers(template_workflow, pipeline_workflow)
    template_job, edited_linear = _assert_refresh_job_identity(template_workflow, pipeline_workflow)
    _assert_refresh_execution_contract(template_workflow, template_job)
    _assert_edited_linear_contract(edited_linear)
    _assert_pipeline_admission_contract(pipeline_workflow)


def _assert_refresh_triggers(
    template_workflow: dict[object, object],
    pipeline_workflow: dict[object, object],
) -> None:
    template_on = _mapping(template_workflow.get("on"), "dedicated workflow trigger")
    assert set(template_on) == {"pull_request"}
    pull_request = _mapping(template_on.get("pull_request"), "dedicated pull_request trigger")
    assert set(pull_request) == {"types"}
    assert pull_request.get("types") == ["edited"]
    pipeline_on = _mapping(pipeline_workflow.get("on"), "pipeline trigger")
    assert set(pipeline_on) == {"pull_request", "merge_group"}
    assert pipeline_on.get("pull_request") is None
    assert pipeline_on.get("merge_group") is None


def _assert_refresh_job_identity(
    template_workflow: dict[object, object],
    pipeline_workflow: dict[object, object],
) -> tuple[dict[object, object], dict[object, object]]:
    assert set(template_workflow) == {"name", "on", "permissions", "concurrency", "jobs"}
    assert template_workflow.get("name") == "PR Metadata Validation"
    template_jobs = _mapping(template_workflow.get("jobs"), "dedicated workflow jobs")
    pipeline_jobs = _mapping(pipeline_workflow.get("jobs"), "pipeline jobs")
    assert list(template_jobs) == ["pr-template", "linear-gate"]
    template_job = _mapping(template_jobs.get("pr-template"), "dedicated pr-template job")
    edited_linear = _mapping(template_jobs.get("linear-gate"), "dedicated linear-gate job")
    pipeline_admission = _mapping(
        pipeline_jobs.get("pr-template-admission"),
        "pipeline pr-template-admission job",
    )
    assert template_job.get("name") == "pr-template"
    assert set(template_job) == {"name", "runs-on", "steps"}
    assert edited_linear.get("name") == "linear-gate"
    assert pipeline_admission.get("name") == "pr-template"
    return template_job, edited_linear


def _assert_refresh_execution_contract(
    template_workflow: dict[object, object],
    template_job: dict[object, object],
) -> None:
    _assert_refresh_workflow_boundary(template_workflow, template_job)
    checkout = _named_step(template_job, "Checkout trusted PR template validator")
    assert set(checkout) == {"name", "uses", "with"}
    assert checkout.get("uses") == "actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0"
    checkout_with = _mapping(checkout.get("with"), "checkout inputs")
    assert checkout_with == {
        "persist-credentials": False,
        "ref": "${{ github.event.pull_request.base.sha }}",
        "path": "trusted-base",
    }

    validate = _named_step(template_job, "Validate PR template completion")
    assert set(validate) == {"name", "env", "run"}
    validate_env = _mapping(validate.get("env"), "validator environment")
    assert validate_env == {"PR_BODY": "${{ github.event.pull_request.body }}"}
    run = validate.get("run")
    assert run == (
        "python3 trusted-base/.github/scripts/validate_pr_template_body.py \\\n"
        "  --template trusted-base/.github/PULL_REQUEST_TEMPLATE.md \\\n"
        "  --body-env PR_BODY\n"
    )


def _assert_refresh_workflow_boundary(
    template_workflow: dict[object, object],
    template_job: dict[object, object],
) -> None:
    assert template_workflow.get("permissions") == {"contents": "read", "pull-requests": "read"}
    assert template_workflow.get("concurrency") == {
        "group": "pr-metadata-${{ github.event.pull_request.number || github.run_id }}",
        "cancel-in-progress": True,
    }
    assert [step.get("name") for step in _steps(template_job)] == [
        "Checkout trusted PR template validator",
        "Validate PR template completion",
    ]


def _assert_edited_linear_contract(job: dict[object, object]) -> None:
    assert set(job) == {"name", "runs-on", "needs", "if", "steps"}
    assert job.get("needs") == ["pr-template"]
    assert job.get("if") == "${{ always() }}"
    _assert_edited_linear_prerequisite(job)
    _assert_edited_linear_checkout(job)
    _assert_edited_linear_command(job)


def _assert_edited_linear_prerequisite(job: dict[object, object]) -> None:
    prerequisite = _named_step(job, "Require PR template validation")
    assert prerequisite.get("if") == "needs.pr-template.result != 'success'"
    assert prerequisite.get("run") == (
        'echo "::error::PR template validation did not pass."\n'
        "exit 1\n"
    )


def _assert_edited_linear_checkout(job: dict[object, object]) -> None:
    checkout = _named_step(job, "Checkout trusted Linear gate")
    assert checkout.get("uses") == "actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0"
    assert _mapping(checkout.get("with"), "edited Linear checkout") == {
        "persist-credentials": False,
        "ref": "${{ github.event.pull_request.base.sha }}",
        "path": "trusted-base",
    }


def _assert_edited_linear_command(job: dict[object, object]) -> None:
    refresh = _named_step(job, "Refresh Linear-first issue tracking policy")
    assert refresh.get("shell") == "bash"
    assert _mapping(refresh.get("env"), "edited Linear environment") == {
        "HARNESS_CLI_ALLOW_NPM_EXEC": "1",
        "NODE_AUTH_TOKEN": "${{ secrets.NPM_TOKEN }}",
        "HEAD_REF": "${{ github.head_ref }}",
        "PR_TITLE": "${{ github.event.pull_request.title }}",
        "PR_BODY": "${{ github.event.pull_request.body }}",
    }
    run = str(refresh.get("run"))
    assert '"status":"blocked","reason":"edited_event_harness_auth_unavailable"' in run
    assert "exit 1" in run
    assert '"status":"deferred"' not in run
    assert "bash trusted-base/Infrastructure/scripts/harness-cli.sh linear-gate \\\n" in run
    assert "bash Infrastructure/scripts/harness-cli.sh" not in run
    assert '--branch "$HEAD_REF"' in run
    assert '--pr-title "$PR_TITLE"' in run
    assert '--pr-body "$PR_BODY"' in run


def _assert_pipeline_admission_contract(pipeline_workflow: dict[object, object]) -> None:
    jobs = _mapping(pipeline_workflow.get("jobs"), "pipeline jobs")
    _assert_pipeline_template_admission(jobs)
    _assert_pipeline_linear_admission(jobs)
    _assert_pipeline_risk_admission(jobs)
    _assert_dependency_review_conditions(jobs)


def _assert_pipeline_template_admission(jobs: dict[object, object]) -> None:
    admission = _mapping(jobs.get("pr-template-admission"), "pipeline admission")
    assert admission.get("name") == "pr-template"
    merge_skip = _named_step(admission, "Skip PR template enforcement for merge queue")
    assert merge_skip == {
        "name": "Skip PR template enforcement for merge queue",
        "if": "github.event_name == 'merge_group'",
        "run": 'echo "merge_group event detected; PR template enforcement is pull_request-only."',
    }


def _assert_pipeline_linear_admission(jobs: dict[object, object]) -> None:
    linear = _mapping(jobs.get("linear-gate"), "pipeline linear-gate")
    assert linear.get("needs") == ["pr-template-admission"]
    assert linear.get("if") == "${{ always() }}"
    linear_prerequisite = _named_step(linear, "Require PR template admission")
    assert linear_prerequisite.get("if") == "needs.pr-template-admission.result != 'success'"
    assert str(linear_prerequisite.get("run")).endswith("exit 1\n")
    _assert_pipeline_trusted_checkout(linear, "Checkout trusted Linear gate", fetch_depth=False)
    command = _named_step(linear, "Enforce Linear-first issue tracking policy")
    run = str(command.get("run"))
    assert '"status":"blocked","reason":"harness_auth_unavailable"' in run
    assert '"status":"deferred"' not in run
    assert "exit 1" in run
    assert "bash trusted-base/Infrastructure/scripts/harness-cli.sh linear-gate \\\n" in run
    assert "bash Infrastructure/scripts/harness-cli.sh" not in run


def _assert_pipeline_risk_admission(jobs: dict[object, object]) -> None:
    risk = _mapping(jobs.get("risk-policy-gate"), "pipeline risk-policy-gate")
    assert risk.get("needs") == ["pr-template-admission", "linear-gate"]
    assert risk.get("if") == "${{ always() }}"
    risk_prerequisite = _named_step(risk, "Require admission gates")
    assert risk_prerequisite.get("if") == (
        "needs.pr-template-admission.result != 'success' || "
        "needs.linear-gate.result != 'success'"
    )
    assert str(risk_prerequisite.get("run")).endswith("exit 1\n")
    _assert_pipeline_trusted_checkout(risk, "Checkout trusted risk policy gate", fetch_depth=True)
    command = _named_step(risk, "Run fast preflight policy gate")
    run = str(command.get("run"))
    assert '"status":"blocked","reason":"harness_auth_unavailable"' in run
    assert '"status":"deferred"' not in run
    assert "exit 1" in run
    assert 'CONTRACT_PATH="trusted-base/harness.contract.json"' in run
    assert "git -C trusted-base diff --name-only" in run
    assert "bash trusted-base/Infrastructure/scripts/harness-cli.sh preflight-gate \\\n" in run
    assert "bash Infrastructure/scripts/harness-cli.sh" not in run


def _assert_pipeline_trusted_checkout(
    job: dict[object, object],
    step_name: str,
    *,
    fetch_depth: bool,
) -> None:
    checkout = _named_step(job, step_name)
    assert checkout.get("uses") == "actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0"
    expected: dict[str, object] = {
        "persist-credentials": False,
        "ref": "${{ github.event.pull_request.base.sha || github.event.merge_group.base_sha }}",
        "path": "trusted-base",
    }
    if fetch_depth:
        expected["fetch-depth"] = 0
    assert _mapping(checkout.get("with"), f"{step_name} inputs") == expected


def _assert_dependency_review_conditions(jobs: dict[object, object]) -> None:
    dependency_review = _mapping(jobs.get("dependency-review"), "pipeline dependency-review")
    assert _named_step(dependency_review, "Run dependency review (pull_request)").get("if") == (
        "${{ github.event_name == 'pull_request' && "
        "steps.dependency-review-support.outputs.supported == 'true' }}"
    )
    assert _named_step(
        dependency_review,
        "Skip dependency review when repository support is unavailable",
    ).get("if") == (
        "${{ github.event_name == 'pull_request' && "
        "steps.dependency-review-support.outputs.supported != 'true' }}"
    )


def _filled_template_body() -> str:
    validator = _load_validator()
    body = _template()
    body = body.replace("- [ ]", "- [x]")
    body = validator.PLACEHOLDER_RE.sub("repo-relative evidence", body)
    replacements = {
        "describe the observable behavior, issue, or n.a. reason": "validated template contract enforcement",
        "list exact commands run here": "python3 .github/scripts/validate_pr_template_body.py --body-file /tmp/body.md",
        "record pass/fail/blocked for each command here": "pass",
        "pass/fail/n.a. with reason": "pass",
        "pass/fail/blocked (reason)": "pass",
        "pass/fail/blocked (<reason>)": "pass",
        "pass/fail/n.a.": "pass",
        "pass/fail": "pass",
        "Add one-paragraph merge rationale here.": "Template validator keeps PR bodies aligned with the repo contract.",
    }
    for before, after in replacements.items():
        body = body.replace(before, after)
    body = validator.FIELD_LINE_RE.sub(
        lambda match: f"- {match.group('label')}: repo-relative evidence"
        if match.group("value").strip() == ""
        else match.group(0),
        body,
    )
    return body


def test_accepts_filled_canonical_template_shape() -> None:
    validator = _load_validator()

    errors = validator.validate_pr_body(_template(), _filled_template_body())

    assert errors == []


def test_template_contract_tracks_release_boundary_section_and_fields() -> None:
    validator = _load_validator()
    contract = validator._template_contract(_template())

    assert contract.sections == [
        "What Problem This Solves",
        "Release Boundary",
        "Why This Change Was Made",
        "Behavior Proof",
        "Work performed",
        "Checklist",
        "Testing",
        "Review artifacts",
        "Notes",
    ]
    assert contract.fields_by_section["Release Boundary"] == [
        "Release mode",
        "Done line",
        "Explicit non-goals",
        "Allowed polish",
        "Deferred polish / follow-up work",
        "Promotion rule",
    ]


def test_rejects_missing_required_field_from_each_templated_section() -> None:
    validator = _load_validator()
    contract = validator._template_contract(_template())
    body = _filled_template_body()

    for section, fields in contract.fields_by_section.items():
        section_block = validator._section_blocks(body)[section]
        for field in fields:
            candidate = body.replace(
                section_block,
                re.sub(
                    rf"^- {re.escape(field)}:.*(?:\n|$)",
                    "",
                    section_block,
                    count=1,
                    flags=re.MULTILINE,
                ),
                1,
            )
            errors = validator.validate_pr_body(_template(), candidate)

            assert f"Missing required field in ## {section}: {field}:" in errors


def test_rejects_short_body_that_only_matches_legacy_required_sections() -> None:
    validator = _load_validator()
    body = """## Summary

- Add a focused typed-contract regression.

## Checklist

- [x] Code change is scoped.
- [x] Local validation passed.

## Testing

- pytest -> pass

## Review artifacts

- CodeRabbit: pass

## Notes

Intentionally isolated.
"""

    errors = validator.validate_pr_body(_template(), body)

    assert any("PR body sections must match" in error for error in errors)
    assert "Missing required section: ## What Problem This Solves" in errors
    assert "Missing required section: ## Why This Change Was Made" in errors
    assert "Missing required section: ## Behavior Proof" in errors
    assert "Missing required section: ## Work performed" in errors
    assert any("Checklist item text/order must match" in error for error in errors)


def test_rejects_body_with_template_section_reordered() -> None:
    validator = _load_validator()
    body = _filled_template_body().replace("## What Problem This Solves", "## What Problem This Solves Renamed", 1)

    errors = validator.validate_pr_body(_template(), body)

    assert any("PR body sections must match" in error for error in errors)
    assert "Missing required section: ## What Problem This Solves" in errors


def test_rejects_unresolved_placeholder_tokens() -> None:
    validator = _load_validator()
    body = _filled_template_body().replace("repo-relative evidence", "<link / artifact path / comment ID>", 1)

    errors = validator.validate_pr_body(_template(), body)

    assert "Replace unresolved placeholder token: <link / artifact path / comment ID>" in errors


def test_rejects_empty_required_fields() -> None:
    validator = _load_validator()
    body = _filled_template_body().replace("- Problem: repo-relative evidence", "- Problem:", 1)

    errors = validator.validate_pr_body(_template(), body)

    assert "Required field in ## Why This Change Was Made is empty: Problem:" in errors


def test_rejects_duplicate_required_fields() -> None:
    validator = _load_validator()
    body = _filled_template_body().replace(
        "- Problem: repo-relative evidence",
        "- Problem: repo-relative evidence\n- Problem: duplicate evidence",
        1,
    )

    errors = validator.validate_pr_body(_template(), body)

    assert "Duplicate field in ## Why This Change Was Made: Problem:" in errors


def test_accepts_required_field_with_nested_continuation_content() -> None:
    validator = _load_validator()
    body = _filled_template_body()
    body = body.replace(
        "- Any other command(s): repo-relative evidence",
        "- Any other command(s):\n  - Command: `pytest` -> pass",
        1,
    )

    errors = validator.validate_pr_body(_template(), body)

    assert errors == []


def test_accepts_unchecked_checklist_item_with_status_marker() -> None:
    body = _filled_template_body()
    body = body.replace(
        "- [x] Any CodeRabbit Semgrep findings were either fixed or explicitly justified when warning-level-only.",
        "- [ ] **(N/A)** Any CodeRabbit Semgrep findings were either fixed or explicitly justified when warning-level-only.",
        1,
    )
    validator = _load_validator()

    errors = validator.validate_pr_body(_template(), body)

    assert errors == []


def test_accepts_angle_tokens_not_owned_by_template() -> None:
    validator = _load_validator()
    body = _filled_template_body().replace(
        "repo-relative evidence",
        "See <https://github.com/jscraik/Agent-Skills/pull/275> for hosted proof.",
        1,
    )

    errors = validator.validate_pr_body(_template(), body)

    assert not any("Replace unresolved placeholder token" in error for error in errors)


def test_pr_template_gate_refreshes_after_pr_body_edits() -> None:
    _assert_pr_template_refresh_contract(
        _workflow(".github/workflows/pr-template.yml"),
        _workflow(".github/workflows/pr-pipeline.yml"),
    )


def test_pr_template_refresh_contract_rejects_unsafe_or_stale_variants() -> None:
    template_workflow = _workflow(".github/workflows/pr-template.yml")
    pipeline_workflow = _workflow(".github/workflows/pr-pipeline.yml")
    missing_edited = copy.deepcopy(template_workflow)
    _mapping(
        _mapping(missing_edited["on"], "trigger")["pull_request"],
        "pull_request trigger",
    )["types"] = ["opened", "synchronize", "reopened"]
    _assert_contract_rejects(missing_edited, pipeline_workflow)
    head_checkout = copy.deepcopy(template_workflow)
    head_job = _mapping(_mapping(head_checkout["jobs"], "jobs")["pr-template"], "job")
    _mapping(
        _named_step(head_job, "Checkout trusted PR template validator")["with"],
        "checkout inputs",
    )["ref"] = "${{ github.event.pull_request.head.sha }}"
    _assert_contract_rejects(head_checkout, pipeline_workflow)
    credentialed_checkout = copy.deepcopy(template_workflow)
    credentialed_job = _mapping(
        _mapping(credentialed_checkout["jobs"], "jobs")["pr-template"],
        "job",
    )
    _mapping(
        _named_step(credentialed_job, "Checkout trusted PR template validator")["with"],
        "checkout inputs",
    )["persist-credentials"] = True
    _assert_contract_rejects(credentialed_checkout, pipeline_workflow)


def test_pr_template_refresh_contract_rejects_wrong_body_or_validator() -> None:
    template_workflow = _workflow(".github/workflows/pr-template.yml")
    pipeline_workflow = _workflow(".github/workflows/pr-pipeline.yml")

    stale_body = copy.deepcopy(template_workflow)
    stale_body_job = _mapping(_mapping(stale_body["jobs"], "jobs")["pr-template"], "job")
    _mapping(
        _named_step(stale_body_job, "Validate PR template completion")["env"],
        "validator environment",
    )["PR_BODY"] = "${{ github.event.pull_request.title }}"
    _assert_contract_rejects(stale_body, pipeline_workflow)
    untrusted_validator = copy.deepcopy(template_workflow)
    untrusted_job = _mapping(
        _mapping(untrusted_validator["jobs"], "jobs")["pr-template"],
        "job",
    )
    _named_step(untrusted_job, "Validate PR template completion")["run"] = (
        "python3 .github/scripts/validate_pr_template_body.py --body-env PR_BODY"
    )
    _assert_contract_rejects(untrusted_validator, pipeline_workflow)


def test_pr_template_refresh_contract_rejects_broad_or_duplicate_check() -> None:
    template_workflow = _workflow(".github/workflows/pr-template.yml")
    pipeline_workflow = _workflow(".github/workflows/pr-pipeline.yml")

    broad_pipeline = copy.deepcopy(pipeline_workflow)
    _mapping(broad_pipeline["on"], "pipeline trigger")["pull_request"] = {
        "types": ["opened", "synchronize", "reopened", "edited"]
    }
    _assert_contract_rejects(template_workflow, broad_pipeline)
    duplicate_check = copy.deepcopy(pipeline_workflow)
    duplicate_admission = _mapping(
        _mapping(duplicate_check["jobs"], "jobs")["pr-template-admission"],
        "pipeline admission",
    )
    duplicate_admission["name"] = "pr-template-admission"
    _assert_contract_rejects(template_workflow, duplicate_check)


def test_pr_template_refresh_contract_rejects_suppressing_event_filters() -> None:
    template_workflow = _workflow(".github/workflows/pr-template.yml")
    pipeline_workflow = _workflow(".github/workflows/pr-pipeline.yml")
    for filter_name in ("branches", "branches-ignore", "paths", "paths-ignore"):
        filtered = copy.deepcopy(template_workflow)
        pull_request = _mapping(
            _mapping(filtered["on"], "trigger")["pull_request"],
            "pull_request trigger",
        )
        pull_request[filter_name] = ["never-match-this-change"]
        _assert_contract_rejects(filtered, pipeline_workflow)


def test_pr_template_refresh_contract_rejects_privilege_or_secret_expansion() -> None:
    template_workflow = _workflow(".github/workflows/pr-template.yml")
    pipeline_workflow = _workflow(".github/workflows/pr-pipeline.yml")
    privileged_job = copy.deepcopy(template_workflow)
    _mapping(privileged_job["jobs"], "jobs")["extra"] = {
        "permissions": {"actions": "write"},
        "runs-on": "ubuntu-latest",
        "steps": [{"run": "echo ${{ secrets.NPM_TOKEN }}"}],
    }
    _assert_contract_rejects(privileged_job, pipeline_workflow)
    job_permission = copy.deepcopy(template_workflow)
    job = _mapping(_mapping(job_permission["jobs"], "jobs")["pr-template"], "job")
    job["permissions"] = {"actions": "write"}
    _assert_contract_rejects(job_permission, pipeline_workflow)
    secret_checkout = copy.deepcopy(template_workflow)
    job = _mapping(_mapping(secret_checkout["jobs"], "jobs")["pr-template"], "job")
    checkout = _named_step(job, "Checkout trusted PR template validator")
    _mapping(checkout["with"], "checkout inputs")["token"] = "${{ secrets.PRIVATE_TOKEN }}"
    _assert_contract_rejects(secret_checkout, pipeline_workflow)


def test_pr_template_refresh_contract_rejects_supply_chain_or_noop_substitution() -> None:
    template_workflow = _workflow(".github/workflows/pr-template.yml")
    pipeline_workflow = _workflow(".github/workflows/pr-pipeline.yml")
    substituted_action = copy.deepcopy(template_workflow)
    job = _mapping(_mapping(substituted_action["jobs"], "jobs")["pr-template"], "job")
    checkout = _named_step(job, "Checkout trusted PR template validator")
    checkout["uses"] = "attacker/checkout@0000000000000000000000000000000000000000"
    _assert_contract_rejects(substituted_action, pipeline_workflow)
    no_op_validator = copy.deepcopy(template_workflow)
    job = _mapping(_mapping(no_op_validator["jobs"], "jobs")["pr-template"], "job")
    validate = _named_step(job, "Validate PR template completion")
    validate["run"] = f"exit 0\n{validate['run']}"
    _assert_contract_rejects(no_op_validator, pipeline_workflow)


def test_pr_template_refresh_contract_rejects_failure_masking_controls() -> None:
    template_workflow = _workflow(".github/workflows/pr-template.yml")
    pipeline_workflow = _workflow(".github/workflows/pr-pipeline.yml")
    continued_failure = copy.deepcopy(template_workflow)
    job = _mapping(_mapping(continued_failure["jobs"], "jobs")["pr-template"], "job")
    validate = _named_step(job, "Validate PR template completion")
    validate["continue-on-error"] = True
    _assert_contract_rejects(continued_failure, pipeline_workflow)
    masking_shell = copy.deepcopy(template_workflow)
    job = _mapping(_mapping(masking_shell["jobs"], "jobs")["pr-template"], "job")
    validate = _named_step(job, "Validate PR template completion")
    validate["shell"] = "bash {0} || true"
    _assert_contract_rejects(masking_shell, pipeline_workflow)


def test_pr_template_refresh_contract_rejects_parent_failure_masking_controls() -> None:
    template_workflow = _workflow(".github/workflows/pr-template.yml")
    pipeline_workflow = _workflow(".github/workflows/pr-pipeline.yml")
    job_continuation = copy.deepcopy(template_workflow)
    job = _mapping(_mapping(job_continuation["jobs"], "jobs")["pr-template"], "job")
    job["continue-on-error"] = True
    _assert_contract_rejects(job_continuation, pipeline_workflow)
    workflow_shell = copy.deepcopy(template_workflow)
    workflow_shell["defaults"] = {"run": {"shell": "bash {0} || true"}}
    _assert_contract_rejects(workflow_shell, pipeline_workflow)
    job_shell = copy.deepcopy(template_workflow)
    job = _mapping(_mapping(job_shell["jobs"], "jobs")["pr-template"], "job")
    job["defaults"] = {"run": {"shell": "bash {0} || true"}}
    _assert_contract_rejects(job_shell, pipeline_workflow)


def test_pr_template_refresh_contract_rejects_stale_runs_or_event_guard_drift() -> None:
    template_workflow = _workflow(".github/workflows/pr-template.yml")
    pipeline_workflow = _workflow(".github/workflows/pr-pipeline.yml")
    no_cancellation = copy.deepcopy(template_workflow)
    _mapping(no_cancellation["concurrency"], "concurrency")["cancel-in-progress"] = False
    _assert_contract_rejects(no_cancellation, pipeline_workflow)
    stale_linear_dependency = copy.deepcopy(template_workflow)
    job = _mapping(_mapping(stale_linear_dependency["jobs"], "jobs")["linear-gate"], "job")
    job["needs"] = []
    _assert_contract_rejects(stale_linear_dependency, pipeline_workflow)
    stale_linear_guard = copy.deepcopy(template_workflow)
    job = _mapping(_mapping(stale_linear_guard["jobs"], "jobs")["linear-gate"], "job")
    _named_step(job, "Require PR template validation")["if"] = "false"
    _assert_contract_rejects(stale_linear_guard, pipeline_workflow)

    head_linear_checkout = copy.deepcopy(template_workflow)
    job = _mapping(_mapping(head_linear_checkout["jobs"], "jobs")["linear-gate"], "job")
    checkout = _named_step(job, "Checkout trusted Linear gate")
    _mapping(checkout["with"], "checkout inputs")["ref"] = "${{ github.event.pull_request.head.sha }}"
    _assert_contract_rejects(head_linear_checkout, pipeline_workflow)

    untrusted_linear_wrapper = copy.deepcopy(template_workflow)
    job = _mapping(_mapping(untrusted_linear_wrapper["jobs"], "jobs")["linear-gate"], "job")
    refresh = _named_step(job, "Refresh Linear-first issue tracking policy")
    refresh["run"] = str(refresh["run"]).replace(
        "trusted-base/Infrastructure/scripts/harness-cli.sh",
        "Infrastructure/scripts/harness-cli.sh",
    )
    _assert_contract_rejects(untrusted_linear_wrapper, pipeline_workflow)


def test_pr_template_refresh_contract_rejects_pipeline_dependency_drift() -> None:
    template_workflow = _workflow(".github/workflows/pr-template.yml")
    pipeline_workflow = _workflow(".github/workflows/pr-pipeline.yml")

    wrong_linear_needs = copy.deepcopy(pipeline_workflow)
    _mapping(_mapping(wrong_linear_needs["jobs"], "jobs")["linear-gate"], "linear")["needs"] = []
    _assert_contract_rejects(template_workflow, wrong_linear_needs)

    skipped_linear = copy.deepcopy(pipeline_workflow)
    _mapping(_mapping(skipped_linear["jobs"], "jobs")["linear-gate"], "linear")["if"] = (
        "needs.pr-template-admission.result == 'success'"
    )
    _assert_contract_rejects(template_workflow, skipped_linear)

    wrong_risk_needs = copy.deepcopy(pipeline_workflow)
    _mapping(_mapping(wrong_risk_needs["jobs"], "jobs")["risk-policy-gate"], "risk")["needs"] = [
        "linear-gate"
    ]
    _assert_contract_rejects(template_workflow, wrong_risk_needs)

    skipped_risk = copy.deepcopy(pipeline_workflow)
    _mapping(_mapping(skipped_risk["jobs"], "jobs")["risk-policy-gate"], "risk")["if"] = (
        "needs.linear-gate.result == 'success'"
    )
    _assert_contract_rejects(template_workflow, skipped_risk)

    malformed_dependency_review = copy.deepcopy(pipeline_workflow)
    dependency_review = _mapping(
        _mapping(malformed_dependency_review["jobs"], "jobs")["dependency-review"],
        "dependency-review",
    )
    _named_step(dependency_review, "Run dependency review (pull_request)")["if"] = (
        "github.event_name == 'pull_request' && "
        "${{ steps.dependency-review-support.outputs.supported == 'true' }}"
    )
    _assert_contract_rejects(template_workflow, malformed_dependency_review)


def test_pr_template_refresh_contract_rejects_untrusted_or_false_green_pipeline_gates() -> None:
    template_workflow = _workflow(".github/workflows/pr-template.yml")
    pipeline_workflow = _workflow(".github/workflows/pr-pipeline.yml")

    for job_name, checkout_name in (
        ("linear-gate", "Checkout trusted Linear gate"),
        ("risk-policy-gate", "Checkout trusted risk policy gate"),
    ):
        head_checkout = copy.deepcopy(pipeline_workflow)
        job = _mapping(_mapping(head_checkout["jobs"], "jobs")[job_name], job_name)
        checkout = _named_step(job, checkout_name)
        _mapping(checkout["with"], "checkout inputs")["ref"] = (
            "${{ github.event.pull_request.head.sha }}"
        )
        _assert_contract_rejects(template_workflow, head_checkout)

    untrusted_linear = copy.deepcopy(pipeline_workflow)
    job = _mapping(_mapping(untrusted_linear["jobs"], "jobs")["linear-gate"], "linear")
    step = _named_step(job, "Enforce Linear-first issue tracking policy")
    step["run"] = str(step["run"]).replace("trusted-base/Infrastructure", "Infrastructure")
    _assert_contract_rejects(template_workflow, untrusted_linear)

    deferred_risk = copy.deepcopy(pipeline_workflow)
    job = _mapping(_mapping(deferred_risk["jobs"], "jobs")["risk-policy-gate"], "risk")
    step = _named_step(job, "Run fast preflight policy gate")
    step["run"] = str(step["run"]).replace(
        '"status":"blocked","reason":"harness_auth_unavailable"',
        '"status":"deferred","reason":"harness_auth_unavailable"',
    ).replace("exit 1", "exit 0", 1)
    _assert_contract_rejects(template_workflow, deferred_risk)


def test_pr_template_refresh_contract_rejects_merge_queue_noop() -> None:
    template_workflow = _workflow(".github/workflows/pr-template.yml")
    pipeline_workflow = _workflow(".github/workflows/pr-pipeline.yml")
    no_op_merge_queue = copy.deepcopy(pipeline_workflow)
    admission = _mapping(
        _mapping(no_op_merge_queue["jobs"], "jobs")["pr-template-admission"],
        "pipeline admission",
    )
    _named_step(admission, "Skip PR template enforcement for merge queue")["run"] = "exit 1"

    _assert_contract_rejects(template_workflow, no_op_merge_queue)


def test_pr_template_contract_suite_is_wired_into_required_test_scope() -> None:
    validate_all = (REPO_ROOT / "Infrastructure" / "scripts" / "validate_all_impl.sh").read_text(
        encoding="utf-8"
    )

    assert "skill-lifecycle-tests|pr-template-contract-tests|skill-authoring-family" in validate_all
    assert 'pr-template-contract-tests "🧾 Validating PR metadata workflow contracts..."' in validate_all
    assert "Infrastructure/scripts/testing/test_validate_pr_template_body.py" in validate_all


def _assert_contract_rejects(
    template_workflow: dict[object, object],
    pipeline_workflow: dict[object, object],
) -> None:
    try:
        _assert_pr_template_refresh_contract(template_workflow, pipeline_workflow)
    except AssertionError:
        return
    raise AssertionError("Unsafe or stale workflow mutation unexpectedly satisfied the contract")
