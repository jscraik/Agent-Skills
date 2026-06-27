from __future__ import annotations

import importlib.util
import json
import sys
from argparse import Namespace
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "build_skill_handoff_status.py"
)
SPEC = importlib.util.spec_from_file_location("build_skill_handoff_status", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
build_skill_handoff_status = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = build_skill_handoff_status
SPEC.loader.exec_module(build_skill_handoff_status)


def _write_tessl_view(path: Path) -> None:
    payload = {
        "data": {
            "id": "019f0933-e8cc-724c-951a-7f1341590e50",
            "type": "eval-run",
            "attributes": {
                "status": "pending",
                "scenarios": [{"id": "one"}, {"id": "two"}],
            },
        }
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_pr_json(path: Path) -> None:
    payload = {
        "number": 293,
        "state": "OPEN",
        "url": "https://github.com/jscraik/Agent-Skills/pull/293",
        "headRefName": "codex/technical-writer-sdk-pipeline",
        "title": "SDK pipeline hardening",
        "template_check": {
            "name": "pr-template",
            "status": "COMPLETED",
            "conclusion": "FAILURE",
            "detailsUrl": "https://github.com/jscraik/Agent-Skills/actions/runs/28295850081/job/83836996111",
        },
        "local_template_validation": {
            "status": "pass",
            "command": "gh pr view 293 --repo jscraik/Agent-Skills --json body --jq '.body' | python3 .github/scripts/validate_pr_template_body.py",
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_tessl_score(path: Path) -> None:
    payload = {
        "data": {
            "skills_sdk_eval_tessl_score": {
                "status": "blocked",
                "ready": False,
                "receipt": {
                    "blocker_class": "blocked_validation",
                    "blocker": "Tessl feedback loop is open.",
                    "feedback_loop": {
                        "status": "open",
                        "regression_count": 1,
                        "regression_paths": ["reader-testing"],
                    },
                    "score_summary": {
                        "usage_percent": 76.8,
                        "baseline_percent": 65.2,
                        "scenario_count": 32,
                    },
                },
            }
        }
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _build_status(tmp_path: Path, tessl_score: Path | None = None) -> dict:
    tessl = tmp_path / "tessl-eval-view.json"
    pr_json = tmp_path / "pr-293.json"
    _write_tessl_view(tessl)
    _write_pr_json(pr_json)
    return build_skill_handoff_status.build_status(
        Namespace(
            skill="Skills/agent-ops/technical-writer",
            tessl_view=str(tessl),
            tessl_score=str(tessl_score) if tessl_score else None,
            pr_json=str(pr_json),
            stale_plan=".harness/plan/old.md",
            branch="codex/technical-writer-sdk-pipeline",
        )
    )


def test_build_status_separates_pending_tessl_from_pr_template_state(tmp_path: Path) -> None:
    status = _build_status(tmp_path)
    assert status["status"]["current_position"] == "tessl_external_pending_existing_run"
    assert status["pipeline_lanes"]["tessl_external"]["scenario_count"] == 2
    assert status["pipeline_lanes"]["pull_request"]["hosted_check"]["conclusion"] == "FAILURE"
    assert "PR mergeability" in status["status"]["does_not_prove"]


def test_build_status_reports_tessl_feedback_loop_when_score_blocks(tmp_path: Path) -> None:
    score = tmp_path / "tessl-score-preview.json"
    _write_tessl_score(score)
    status = _build_status(tmp_path, tessl_score=score)

    assert status["status"]["current_position"] == "tessl_feedback_loop_open"
    assert any(
        action.startswith("classify the five Tessl baseline-win regressions by owner")
        for action in status["status"]["next_actions"]
    )
    assert status["pipeline_lanes"]["tessl_external"]["score_receipt"]["regression_paths"] == [
        "reader-testing"
    ]


def test_existing_artifact_freshness_flags_stale_head(tmp_path: Path) -> None:
    output = tmp_path / "status.json"
    output.write_text(json.dumps({"repo": {"head": "old"}}), encoding="utf-8")

    freshness = build_skill_handoff_status._existing_artifact_freshness(output, "new")

    assert freshness["status"] == "stale"
    assert freshness["artifact_head"] == "old"
    assert freshness["current_head"] == "new"
