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
    assert finding.status == "violation"
    assert finding.code == "tracked_historical_artifact"
    assert finding.blocking is True


def test_duplicated_infrastructure_path_is_violation() -> None:
    finding = MODULE.classify_path(
        "Infrastructure/Infrastructure/artifacts/validation/20260417T215252Z/projection-integrity.json"
    )

    assert finding.classification == "unknown"
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


def test_root_architecture_is_front_door_source() -> None:
    finding = MODULE.classify_path("ARCHITECTURE.md")

    assert finding.classification == "source"
    assert finding.status == "ok"
    assert finding.code == "authored_source_surface"
    assert finding.blocking is False


def test_stale_root_proposal_requires_relocation() -> None:
    finding = MODULE.classify_path("PROPOSED_CODE_FILE_REORGANIZATION_PLAN.md")

    assert finding.classification == "unknown"
    assert finding.status == "unknown"
    assert finding.code == "unknown_surface"
    assert finding.blocking is True


def test_hidden_root_migration_script_requires_relocation() -> None:
    """
    Test that a hidden root migration script is classified as an unknown surface and treated as a blocking violation.
    
    Asserts the classifier marks ".move.sh" with:
    - classification: "unknown"
    - status: "unknown"
    - code: "unknown_surface"
    - blocking: True
    """
    finding = MODULE.classify_path(".move.sh")

    assert finding.classification == "unknown"
    assert finding.status == "unknown"
    assert finding.code == "unknown_surface"
    assert finding.blocking is True


def test_lowercase_docs_path_is_casing_drift() -> None:
    finding = MODULE.classify_path("docs/goals/jsc-329/notes/gap-analysis.md")

    assert finding.classification == "unknown"
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

    assert finding.classification == "unknown"
    assert finding.status == "unknown"
    assert finding.code == "ownership_decision_required"
    assert finding.blocking is True


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
    }

    for path, (classification, code) in cases.items():
        finding = MODULE.classify_path(path)
        assert finding.classification == classification
        assert finding.status == "ok"
        assert finding.code == code


def test_harness_runtime_outputs_are_violations() -> None:
    """
    Verifies that selected `.harness/` runtime output paths are classified as violations.

    Asserts each path produces a finding with status "violation", `blocking` set to True, and the expected violation `code`.
    """
    cases = {
        ".harness/backups/abc.bak": "tracked_harness_backup",
        ".harness/ci-migrate-snapshots/snapshot.json": "tracked_harness_snapshot",
    }

    for path, code in cases.items():
        finding = MODULE.classify_path(path)
        assert finding.status == "violation"
        assert finding.blocking is True
        assert finding.code == code


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
        "allowlist_entry",
        "reason",
        "recommendation",
        "metadata",
    }
    for finding in report["findings"]:
        assert required <= finding.keys()
        assert "next_steps" in finding["metadata"]
        for step in finding["metadata"]["next_steps"]:
            assert {"type", "command", "rationale"} <= step.keys()
    for step in report["metadata"]["next_steps"]:
        assert {"type", "command", "rationale"} <= step.keys()


def test_non_strict_report_status_warns_when_blockers_exist() -> None:
    findings = MODULE.classify_paths(["artifacts/run/events.jsonl"])
    report = MODULE.build_report(findings, strict=False)

    assert report["status"] == "warning"
    assert report["summary"]["blocking_findings"] == 1


def test_allowlist_downgrades_matching_blocker_to_warning() -> None:
    entry = MODULE.AllowlistEntry(
        id="historical-artifact-fixture",
        match_type="prefix",
        pattern="artifacts/fixture",
        classification="historical_artifact",
        reason="Stable fixture retained for regression coverage.",
        owner="test",
        review_after="2026-06-01",
    )

    [finding] = MODULE.classify_paths(["artifacts/fixture/events.jsonl"], [entry])

    assert finding.status == "warning"
    assert finding.severity == "warning"
    assert finding.blocking is False
    assert finding.allowlist_entry == "historical-artifact-fixture"


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


def test_cli_strict_json_mode_fails_with_json_only_stdout() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--strict", "--json"],
        text=True,
        capture_output=True,
        check=False,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["status"] == "error"
    assert payload["findings"][0]["blocking"] is True
    assert payload["findings"][0]["severity"] == "error"
    assert result.stderr == ""
