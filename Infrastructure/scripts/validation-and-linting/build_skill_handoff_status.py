#!/usr/bin/env python3
"""Build a current Skills SDK handoff status artifact for one skill."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _git_commit() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _tessl_summary(tessl_view: Path) -> dict[str, Any]:
    data = _load_json(tessl_view).get("data", {})
    attrs = data.get("attributes") or {}
    return {
        "source": _relative(tessl_view),
        "id": data.get("id"),
        "type": data.get("type"),
        "status": attrs.get("status"),
        "scenario_count": len(attrs.get("scenarios") or []),
        "score": attrs.get("score"),
        "baseline": attrs.get("baseline"),
        "improvement": attrs.get("improvement"),
        "created_at": attrs.get("created_at"),
        "updated_at": attrs.get("updated_at"),
    }


def _template_check(pr_json: Path) -> dict[str, Any]:
    data = _load_json(pr_json)
    hosted = data.get("template_check") or {}
    local_validation = data.get("local_template_validation") or {}
    return {
        "source": _relative(pr_json),
        "pr": {
            "number": data.get("number"),
            "state": data.get("state"),
            "url": data.get("url"),
            "head_ref": data.get("headRefName"),
            "title": data.get("title"),
        },
        "hosted_check": {
            "name": hosted.get("name") or hosted.get("context"),
            "status": hosted.get("status"),
            "conclusion": hosted.get("conclusion"),
            "details_url": hosted.get("detailsUrl") or hosted.get("targetUrl"),
        },
        "local_template_validation": local_validation,
    }


def _skill_paths(skill: Path) -> dict[str, str]:
    return {
        "skill": _relative(skill),
        "skill_md": _relative(skill / "SKILL.md"),
        "evals_yaml": _relative(skill / "references" / "evals.yaml"),
    }


def _current_position(tessl: dict[str, Any], pr: dict[str, Any]) -> str:
    if tessl.get("status") == "pending":
        return "tessl_external_pending_existing_run"
    if pr["hosted_check"].get("conclusion") not in {None, "SUCCESS"}:
        return "pr_template_hosted_check_needs_fresh_event"
    return "needs_current_pipeline_decision"


def build_status(args: argparse.Namespace) -> dict[str, Any]:
    skill = (ROOT / args.skill).resolve()
    tessl = _tessl_summary((ROOT / args.tessl_view).resolve())
    pr = _template_check((ROOT / args.pr_json).resolve())
    return {
        "schema_version": "skills-sdk-handoff-status/v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo": {"root": _relative(ROOT), "head": _git_commit(), "branch": args.branch},
        "skill": _skill_paths(skill),
        "status": {
            "current_position": _current_position(tessl, pr),
            "next_actions": [
                "refresh PR #293 by pushing the current branch so hosted checks see this status artifact",
                "inspect the existing pending Tessl eval before submitting any new live scoring run",
                "treat the older local plan as superseded by this handoff status for technical-writer PR work",
            ],
            "does_not_prove": [
                "PR mergeability",
                "final Tessl score",
                "registry release readiness",
                "installed runtime behavior",
            ],
        },
        "pipeline_lanes": {
            "tessl_external": tessl,
            "pull_request": pr,
            "stale_plan_reconciliation": {
                "source": args.stale_plan,
                "status": "older_local_plan_state_superseded_for_technical_writer_pr",
            },
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", required=True)
    parser.add_argument("--tessl-view", required=True)
    parser.add_argument("--pr-json", required=True)
    parser.add_argument("--stale-plan", required=True)
    parser.add_argument("--branch", default="codex/technical-writer-sdk-pipeline")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = (ROOT / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    status = build_status(args)
    output.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "pass", "output": _relative(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
