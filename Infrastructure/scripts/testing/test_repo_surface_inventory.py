from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "check_repo_surface_inventory.py"
)
SPEC = importlib.util.spec_from_file_location("check_repo_surface_inventory", SCRIPT_PATH)
assert SPEC is not None
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["check_repo_surface_inventory"] = MODULE
SPEC.loader.exec_module(MODULE)


def test_artifact_event_stream_is_historical_artifact() -> None:
    finding = MODULE.classify_path("artifacts/skill-graphs/runs/20260401/events.jsonl")

    assert finding.classification == "historical_artifact"
    assert finding.status == "warning"
    assert finding.code == "tracked_historical_artifact"
    assert finding.blocking is False


def test_inventory_reports_identify_the_agent_skills_service() -> None:
    report = MODULE.build_report([], strict=False)
    assert report["metadata"]["service"] == "agent-skills"

    args = type("Args", (), {"strict": False})()
    error = MODULE.error_report(args, RuntimeError("fixture failure"))
    assert error["metadata"]["service"] == "agent-skills"
    assert error["findings"][0]["allowlist_entry"] is None


def test_harness_review_artifact_is_nonblocking_historical_evidence() -> None:
    finding = MODULE.classify_path(".harness/review-artifacts/pu-010-adversarial-cli-tests-status.md")

    assert finding.classification == "historical_artifact"
    assert finding.status == "warning"
    assert finding.code == "tracked_harness_snapshot"
    assert finding.blocking is False


def test_harness_evidence_trace_is_trackable_historical_evidence() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    path = ".harness/evidence/harness/traces/example.md"
    finding = MODULE.classify_path(path)

    assert finding.classification == "historical_artifact"
    assert finding.status == "warning"
    assert finding.code == "tracked_harness_snapshot"
    assert finding.blocking is False

    result = subprocess.run(
        ["git", "check-ignore", "--quiet", path],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1, result.stderr


def test_harness_evidence_trace_blocks_new_tracked_output() -> None:
    path = ".harness/evidence/harness/traces/example.md"
    blocked = MODULE.classify_paths([path], changed_files={path})[0]

    assert blocked.blocking is True
    assert blocked.code == "new_historical_artifact_debt"


def test_generated_agent_review_roots_are_ignored() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    generated_paths = (
        "artifacts/agent-runs/example/manifest.json",
        ".harness/agent-runs/example/manifest.json",
        ".harness/review-artifacts/example.md",
        ".harness/traces/example.md",
    )

    result = subprocess.run(
        ["git", "check-ignore", "--stdin"],
        cwd=repo_root,
        input="\n".join(generated_paths),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == list(generated_paths)



def test_infrastructure_package_policy_files_are_policy_surface() -> None:
    cases = ["Infrastructure/pyproject.toml", "Infrastructure/uv.lock"]

    for path in cases:
        finding = MODULE.classify_path(path)

        assert finding.classification == "policy"
        assert finding.status == "ok"
        assert finding.code == "policy_surface"
        assert finding.blocking is False


def test_duplicated_infrastructure_path_is_violation() -> None:
    finding = MODULE.classify_path(
        "Infrastructure/Infrastructure/artifacts/validation/20260417T215252Z/projection-integrity.json"
    )

    assert finding.classification == "classification_required"
    assert finding.status == "violation"
    assert finding.code == "duplicated_infrastructure_path"
    assert finding.blocking is True


def test_skill_source_path_is_source() -> None:
    """
    Verify that a SKILL.md file under Skills/... is classified as source surface.
    
    Asserts the resulting finding has classification "source", status "ok", and is not blocking.
    """
    finding = MODULE.classify_path("Skills/agent-ops/autofix/SKILL.md")

    assert finding.classification == "source"
    assert finding.status == "ok"
    assert finding.blocking is False


def test_skill_scorer_calibration_examples_are_source() -> None:
    finding = MODULE.classify_path(
        "Skills/agent-ops/sdk-scenario-generator/references/scorer-calibration/examples.jsonl"
    )

    assert finding.classification == "source"
    assert finding.status == "ok"
    assert finding.code == "authored_source_surface"
    assert finding.blocking is False


def test_codex_scorer_calibration_examples_are_source() -> None:
    finding = MODULE.classify_path(
        "codex/agents/evals/workflow-guardrail-candidates/"
        "references/scorer-calibration/examples.jsonl"
    )

    assert finding.classification == "source"
    assert finding.status == "ok"
    assert finding.code == "authored_source_surface"
    assert finding.blocking is False


def test_scorer_calibration_generated_output_is_not_source() -> None:
    paths = [
        "Skills/agent-ops/sdk-scenario-generator/references/scorer-calibration/run.log",
        (
            "codex/agents/evals/workflow-guardrail-candidates/"
            "references/scorer-calibration/events.jsonl"
        ),
    ]

    for path in paths:
        finding = MODULE.classify_path(path)
        assert finding.classification == "historical_artifact"
        assert finding.status == "warning"
        assert finding.code == "generated_evidence_pattern"
        assert finding.blocking is False


def test_artifact_agent_guide_is_policy_surface() -> None:
    finding = MODULE.classify_path("artifacts/AGENTS.md")

    assert finding.classification == "policy"
    assert finding.status == "ok"
    assert finding.code == "policy_surface"
    assert finding.blocking is False


def test_pipeline_status_artifact_is_governed_source() -> None:
    finding = MODULE.classify_path("artifacts/recommended-skills-sdk-pipeline.html")

    assert finding.classification == "source"
    assert finding.status == "ok"
    assert finding.code == "authored_source_surface"
    assert finding.blocking is False


def test_lifecycle_status_artifact_is_governed_source() -> None:
    finding = MODULE.classify_path("artifacts/skills-sdk-user-lifecycle-one-page.html")

    assert finding.classification == "source"
    assert finding.status == "ok"
    assert finding.code == "authored_source_surface"
    assert finding.blocking is False


def test_root_architecture_is_front_door_source() -> None:
    finding = MODULE.classify_path("ARCHITECTURE.md")

    assert finding.classification == "source"
    assert finding.status == "ok"
    assert finding.code == "authored_source_surface"
    assert finding.blocking is False


def test_stale_root_proposal_requires_relocation() -> None:
    finding = MODULE.classify_path("PROPOSED_CODE_FILE_REORGANIZATION_PLAN.md")

    assert finding.classification == "classification_required"
    assert finding.status == "violation"
    assert finding.code == "classification_required"
    assert finding.blocking is True


def test_hidden_root_migration_script_requires_relocation() -> None:
    """
    Test that a hidden root migration script is classified as requiring ownership and treated as a blocking violation.
    
    Asserts the classifier marks ".move.sh" with:
    - classification: "classification_required"
    - status: "violation"
    - code: "classification_required"
    - blocking: True
    """
    finding = MODULE.classify_path(".move.sh")

    assert finding.classification == "classification_required"
    assert finding.status == "violation"
    assert finding.code == "classification_required"
    assert finding.blocking is True


def test_lowercase_docs_path_is_casing_drift() -> None:
    finding = MODULE.classify_path("docs/goals/jsc-329/notes/gap-analysis.md")

    assert finding.classification == "classification_required"
    assert finding.status == "violation"
    assert finding.code == "lowercase_docs_drift"
    assert finding.blocking is True


def test_git_ls_files_omits_worktree_deleted_paths(monkeypatch, tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    kept = repo / "kept.txt"
    kept.write_text("kept", encoding="utf-8")

    class Completed:
        stdout = "kept.txt\ndeleted.txt\n"

    def fake_run(*args, **kwargs):
        return Completed()

    monkeypatch.setattr(MODULE.subprocess, "run", fake_run)

    assert MODULE.git_ls_files(repo) == ["kept.txt"]


def test_plugin_fixtures_are_classified_before_plugin_source_catchall() -> None:
    finding = MODULE.classify_path(
        "Plugins/harness-engineering/fixtures/budget-archive/2026-04-21/references/routing.md"
    )

    assert finding.classification == "fixture"
    assert finding.status == "ok"
    assert finding.code == "plugin_fixture_surface"


def test_plugin_references_are_classified_before_plugin_source_catchall() -> None:
    finding = MODULE.classify_path("Plugins/harness-engineering/references/routing-map.json")

    assert finding.classification == "reference"
    assert finding.status == "ok"
    assert finding.code == "plugin_reference_surface"


def test_skillsets_are_generated_tracked_projections() -> None:
    cases = [
        ".skillsets/harness-engineering/manifest.jsonl",
        ".skillsets/command-surface.json",
    ]

    for path in cases:
        finding = MODULE.classify_path(path)
        assert finding.classification == "generated_tracked"
        assert finding.status == "ok"
        assert finding.code == "generated_skillset_projection"
        assert finding.blocking is False


def test_skills_system_is_governed_system_skill_surface() -> None:
    finding = MODULE.classify_path("skills-system/imagegen/SKILL.md")

    assert finding.classification == "generated_tracked"
    assert finding.status == "ok"
    assert finding.code == "system_skill_surface"
    assert finding.blocking is False
    assert "skills-system-upstream.lock.json" in finding.reason


def test_skills_system_stray_path_still_requires_ownership_decision() -> None:
    finding = MODULE.classify_path("skills-system/generated-skill/SKILL.md")

    assert finding.classification == "classification_required"
    assert finding.status == "violation"
    assert finding.code == "ownership_decision_required"
    assert finding.blocking is True


def test_harness_archive_is_intentional_archive_not_unknown() -> None:
    finding = MODULE.classify_path(
        ".harness/archive/2026-05-18-plans-and-specs/specs/2026-05-09-agent-skills-first-principles-contract-spec.md"
    )

    assert finding.classification == "intentional_archive"
    assert finding.status == "ok"
    assert finding.code == "harness_archive_surface"
    assert finding.blocking is False


def test_harness_database_is_runtime_state_violation() -> None:
    finding = MODULE.classify_path(".harness/context-compound.db")

    assert finding.classification == "runtime_state"
    assert finding.status == "violation"
    assert finding.code == "tracked_runtime_database"


def test_harness_curated_context_paths_are_classified() -> None:
    cases = {
        ".harness/README.md": ("policy", "policy_surface"),
        ".harness/core/architecture-invariants.md": ("policy", "policy_surface"),
        ".harness/decisions/jsc-001.md": ("policy", "policy_surface"),
        ".harness/linear/agent-skills-linear-plan.md": ("policy", "policy_surface"),
        ".harness/reframes/ask-control-plane-decomposition.md": ("policy", "policy_surface"),
        ".harness/refactors/legacy-decomposition.md": ("policy", "policy_surface"),
        ".harness/brainstorm/he-routing.md": ("policy", "policy_surface"),
        ".harness/solutions/README.md": ("policy", "policy_surface"),
        ".harness/solutions/repeated-ci-blocker.md": ("policy", "policy_surface"),
        ".harness/specs/agent-skills-ask-control-plane-decomposition-spec.md": (
            "reference",
            "harness_reference_surface",
        ),
        ".harness/review/agent-skills-architecture-review.md": (
            "reference",
            "harness_reference_surface",
        ),
        ".harness/media/2026-05-09-he-trust-repair-before-after.md": (
            "reference",
            "harness_reference_surface",
        ),
        ".harness/media/2026-05-09-he-trust-repair-before-after.png": (
            "reference",
            "harness_reference_surface",
        ),
        ".harness/evidence/runtime-proof/testing/codex/runtime-card.json": (
            "reference",
            "harness_reference_surface",
        ),
        ".harness/implementation-notes/2026-06-04-skills-sdk-v1-0-product-implementation-notes.html": (
            "reference",
            "harness_reference_surface",
        ),
        ".harness/reports/skills-sdk-v1-0-product-implementation/pu-007-closeout.md": (
            "reference",
            "harness_reference_surface",
        ),
        ".harness/research/audits/2026-05-28-skillopt-skills-sdk-gap-analysis.md": (
            "reference",
            "harness_reference_surface",
        ),
        ".harness/reviews/2026-05-21-jsc-329-goal-governor/testing.md": (
            "reference",
            "harness_reference_surface",
        ),
    }

    for path, (classification, code) in cases.items():
        finding = MODULE.classify_path(path)
        assert finding.classification == classification
        assert finding.status == "ok"
        assert finding.code == code


def test_current_tracked_inventory_has_no_classification_required_paths() -> None:
    findings = MODULE.classify_paths(MODULE.git_ls_files(MODULE.REPO_ROOT))
    offenders = [
        finding.path
        for finding in findings
        if finding.classification == "classification_required" and finding.blocking
    ]

    assert offenders == []


def test_harness_runtime_outputs_are_violations() -> None:
    finding = MODULE.classify_path(".harness/backups/abc.bak")

    assert finding.status == "violation"
    assert finding.blocking is True
    assert finding.code == "tracked_harness_backup"


def test_json_report_has_required_fields_and_deterministic_order() -> None:
    findings = MODULE.classify_paths(
        [
            "Skills/agent-ops/autofix/SKILL.md",
            "Infrastructure/Infrastructure/artifacts/validation/out.json",
            "artifacts/run/events.jsonl",
            ".harness/context-compound.db",
        ]
    )
    report = MODULE.build_report(findings, strict=True)

    assert report["schema_version"] == 1
    assert report["status"] == "error"
    assert report["metadata"]["next_steps"]
    paths = [finding["path"] for finding in report["findings"]]
    assert paths == [
        ".harness/context-compound.db",
        "Infrastructure/Infrastructure/artifacts/validation/out.json",
        "artifacts/run/events.jsonl",
        "Skills/agent-ops/autofix/SKILL.md",
    ]
    required = {
        "path",
        "classification",
        "status",
        "code",
        "severity",
        "blocking",
        "reason",
        "recommendation",
        "allowlist_entry",
        "metadata",
    }
    for finding in report["findings"]:
        assert required <= finding.keys()
        assert "next_steps" in finding["metadata"]
        for step in finding["metadata"]["next_steps"]:
            assert {"type", "command", "rationale"} <= step.keys()
    for step in report["metadata"]["next_steps"]:
        assert {"type", "command", "rationale"} <= step.keys()


def test_non_strict_report_status_warns_when_warnings_exist() -> None:
    findings = MODULE.classify_paths(["artifacts/run/events.jsonl"])
    report = MODULE.build_report(findings, strict=False)

    assert report["status"] == "warning"
    assert report["summary"]["blocking_findings"] == 0
    assert report["summary"]["counts_by_status"] == {"warning": 1}


def test_changed_historical_artifact_debt_blocks_future_artifacts() -> None:
    findings = MODULE.classify_paths(
        ["artifacts/run/events.jsonl"],
        changed_files=["artifacts/run/events.jsonl"],
    )
    report = MODULE.build_report(
        findings,
        strict=True,
        changed_files=["artifacts/run/events.jsonl"],
    )

    [finding] = findings
    assert finding.classification == "historical_artifact"
    assert finding.status == "violation"
    assert finding.severity == "error"
    assert finding.blocking is True
    assert finding.code == "new_historical_artifact_debt"
    assert finding.metadata["original_code"] == "tracked_historical_artifact"
    assert finding.metadata["changed_files_policy"] == "future_artifact_debt_blocked"
    assert report["status"] == "error"
    assert report["summary"]["blocking_findings"] == 1
    assert report["metadata"]["changed_files_policy"] == "future_artifact_debt_blocking"


def test_changed_generated_harness_evidence_blocks_future_artifacts() -> None:
    for path in (
        ".harness/evidence/runtime-proof/events.jsonl",
        ".harness/evidence/runtime-proof/run.log",
    ):
        findings = MODULE.classify_paths([path], changed_files=[path])

        [finding] = findings
        assert finding.classification == "historical_artifact"
        assert finding.status == "violation"
        assert finding.severity == "error"
        assert finding.blocking is True
        assert finding.code == "new_historical_artifact_debt"
        assert finding.metadata["original_code"] == "generated_evidence_pattern"


def test_curated_harness_evidence_remains_reference_surface() -> None:
    finding = MODULE.classify_path(
        ".harness/evidence/runtime-proof/testing/codex/runtime-card.json"
    )

    assert finding.classification == "reference"
    assert finding.code == "harness_reference_surface"


def test_unchanged_historical_artifact_backlog_remains_advisory() -> None:
    findings = MODULE.classify_paths(
        ["artifacts/run/events.jsonl"],
        changed_files=["Skills/agent-ops/example/SKILL.md"],
    )
    report = MODULE.build_report(
        findings,
        strict=True,
        changed_files=["Skills/agent-ops/example/SKILL.md"],
    )

    [finding] = findings
    assert finding.code == "tracked_historical_artifact"
    assert finding.status == "warning"
    assert finding.blocking is False
    assert report["status"] == "warning"
    assert report["summary"]["blocking_findings"] == 0


def test_cli_json_mode_writes_json_only_stdout() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--json"],
        text=True,
        capture_output=True,
        check=True,
    )

    payload = json.loads(result.stdout)
    assert payload["schema_version"] == 1
    assert "findings" in payload
    assert result.stderr == ""


def test_cli_strict_json_mode_passes_without_blockers() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--strict", "--json"],
        text=True,
        capture_output=True,
        check=False,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["status"] in {"ok", "warning"}
    assert payload["summary"]["blocking_findings"] == 0
    assert result.stderr == ""
