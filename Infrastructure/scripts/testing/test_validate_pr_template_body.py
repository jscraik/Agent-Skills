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
    template_job = _assert_refresh_job_identity(template_workflow, pipeline_workflow)
    _assert_refresh_execution_contract(template_workflow, template_job)


def _assert_refresh_triggers(
    template_workflow: dict[object, object],
    pipeline_workflow: dict[object, object],
) -> None:
    template_on = _mapping(template_workflow.get("on"), "dedicated workflow trigger")
    pull_request = _mapping(template_on.get("pull_request"), "dedicated pull_request trigger")
    assert pull_request.get("types") == ["opened", "synchronize", "reopened", "edited"]
    assert "merge_group" in template_on
    pipeline_on = _mapping(pipeline_workflow.get("on"), "pipeline trigger")
    pipeline_pull_request = pipeline_on.get("pull_request")
    assert pipeline_pull_request is None or pipeline_pull_request == {}


def _assert_refresh_job_identity(
    template_workflow: dict[object, object],
    pipeline_workflow: dict[object, object],
) -> dict[object, object]:
    template_jobs = _mapping(template_workflow.get("jobs"), "dedicated workflow jobs")
    pipeline_jobs = _mapping(pipeline_workflow.get("jobs"), "pipeline jobs")
    assert list(template_jobs) == ["pr-template"]
    template_job = _mapping(template_jobs.get("pr-template"), "dedicated pr-template job")
    pipeline_admission = _mapping(
        pipeline_jobs.get("pr-template-admission"),
        "pipeline pr-template-admission job",
    )
    displayed_names = [
        job.get("name")
        for jobs in (template_jobs, pipeline_jobs)
        for job in jobs.values()
        if isinstance(job, dict)
    ]
    assert displayed_names.count("pr-template") == 1
    assert template_job.get("name") == "pr-template"
    assert "permissions" not in template_job
    assert pipeline_admission.get("name") == "pr-template-admission"
    return template_job


def _assert_refresh_execution_contract(
    template_workflow: dict[object, object],
    template_job: dict[object, object],
) -> None:
    _assert_refresh_workflow_boundary(template_workflow, template_job)
    checkout = _named_step(template_job, "Checkout trusted PR template validator")
    assert set(checkout) == {"name", "if", "uses", "with"}
    assert checkout.get("if") == "github.event_name == 'pull_request'"
    assert checkout.get("uses") == "actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0"
    checkout_with = _mapping(checkout.get("with"), "checkout inputs")
    assert checkout_with == {
        "persist-credentials": False,
        "ref": "${{ github.event.pull_request.base.sha }}",
        "path": "trusted-base",
    }

    validate = _named_step(template_job, "Validate PR template completion")
    assert set(validate) == {"name", "if", "env", "run"}
    assert validate.get("if") == "github.event_name == 'pull_request'"
    validate_env = _mapping(validate.get("env"), "validator environment")
    assert validate_env == {"PR_BODY": "${{ github.event.pull_request.body }}"}
    run = validate.get("run")
    assert run == (
        "python3 trusted-base/.github/scripts/validate_pr_template_body.py \\\n"
        "  --template trusted-base/.github/PULL_REQUEST_TEMPLATE.md \\\n"
        "  --body-env PR_BODY\n"
    )
    merge_group = _named_step(template_job, "Skip PR template enforcement for merge queue")
    assert set(merge_group) == {"name", "if", "run"}
    assert merge_group.get("if") == "github.event_name == 'merge_group'"


def _assert_refresh_workflow_boundary(
    template_workflow: dict[object, object],
    template_job: dict[object, object],
) -> None:
    assert template_workflow.get("permissions") == {"contents": "read", "pull-requests": "read"}
    assert template_workflow.get("concurrency") == {
        "group": "pr-template-${{ github.event.pull_request.number || github.event.merge_group.head_sha || github.run_id }}",
        "cancel-in-progress": True,
    }
    assert [step.get("name") for step in _steps(template_job)] == [
        "Checkout trusted PR template validator",
        "Validate PR template completion",
        "Skip PR template enforcement for merge queue",
    ]


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
    duplicate_admission["name"] = "pr-template"
    _assert_contract_rejects(template_workflow, duplicate_check)


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


def test_pr_template_refresh_contract_rejects_stale_runs_or_event_guard_drift() -> None:
    template_workflow = _workflow(".github/workflows/pr-template.yml")
    pipeline_workflow = _workflow(".github/workflows/pr-pipeline.yml")
    no_cancellation = copy.deepcopy(template_workflow)
    _mapping(no_cancellation["concurrency"], "concurrency")["cancel-in-progress"] = False
    _assert_contract_rejects(no_cancellation, pipeline_workflow)
    no_guard = copy.deepcopy(template_workflow)
    job = _mapping(_mapping(no_guard["jobs"], "jobs")["pr-template"], "job")
    _named_step(job, "Validate PR template completion").pop("if")
    _assert_contract_rejects(no_guard, pipeline_workflow)
    swapped_guard = copy.deepcopy(template_workflow)
    job = _mapping(_mapping(swapped_guard["jobs"], "jobs")["pr-template"], "job")
    _named_step(job, "Skip PR template enforcement for merge queue")["if"] = (
        "github.event_name == 'pull_request'"
    )
    _assert_contract_rejects(swapped_guard, pipeline_workflow)


def _assert_contract_rejects(
    template_workflow: dict[object, object],
    pipeline_workflow: dict[object, object],
) -> None:
    try:
        _assert_pr_template_refresh_contract(template_workflow, pipeline_workflow)
    except AssertionError:
        return
    raise AssertionError("Unsafe or stale workflow mutation unexpectedly satisfied the contract")
