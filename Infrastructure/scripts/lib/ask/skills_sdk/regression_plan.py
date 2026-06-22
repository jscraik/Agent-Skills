from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ask.skills_sdk.tessl_score_receipt import build_tessl_score_receipt


REGRESSION_PLAN_SCHEMA_VERSION = "skills-sdk.eval-regression-plan.v0"
REGRESSION_PLAN_SCHEMA_URI = "https://jscraik.local/agent-skills/schemas/skills-sdk/eval-regression-plan.v0.schema.json"
OWNER_CHOICES = ("skill", "task", "criteria", "scorer", "environment")
DEFAULT_PLAN_RELATIVE_PATH = Path("references/eval-regression-plan.json")


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not isinstance(loaded, dict):
        return None, "json_root_not_object"
    return loaded, None


def _skill_md(source_path: Path) -> Path:
    return source_path if source_path.name == "SKILL.md" else source_path / "SKILL.md"


def _skill_dir(source_path: Path) -> Path:
    return source_path.parent if source_path.name == "SKILL.md" else source_path


def _load_plan(skill_dir: Path, override: Path | None) -> tuple[dict[str, Any], Path | None, str | None]:
    candidates = [override] if override is not None else [
        skill_dir / DEFAULT_PLAN_RELATIVE_PATH,
        skill_dir / "references" / "regression-plan.json",
    ]
    for path in candidates:
        if path is None or not path.is_file():
            continue
        payload, error = _load_json(path)
        return payload or {}, path, error
    return {}, None, "missing_regression_plan"


def _plan_regression_index(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    regressions = plan.get("regressions")
    if not isinstance(regressions, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for item in regressions:
        if not isinstance(item, dict):
            continue
        scenario_id = item.get("scenario_id") or item.get("scenario_path") or item.get("path")
        if isinstance(scenario_id, str) and scenario_id.strip():
            result[scenario_id.strip()] = item
    return result


def _score_regressions(score_receipt: dict[str, Any]) -> list[dict[str, Any]]:
    summary = score_receipt.get("score_summary")
    regressions = summary.get("regressions") if isinstance(summary, dict) else []
    return [item for item in regressions if isinstance(item, dict)]


def _check(check_id: str, status: str, message: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {"id": check_id, "status": status, "severity": "blocker", "message": message, "evidence": evidence or []}


def _patch_plan_valid(entries: list[Any]) -> bool:
    for item in entries:
        if not isinstance(item, dict):
            continue
        file_value = item.get("file")
        change = item.get("change")
        if isinstance(file_value, str) and file_value.strip() and isinstance(change, str) and change.strip():
            return True
    return False


def _retained_valid(repo_root: Path, retained: Any) -> bool:
    if not isinstance(retained, dict):
        return False
    if retained.get("status") not in {"retained", "imported"}:
        return False
    retained_path = retained.get("path")
    if not isinstance(retained_path, str) or not retained_path.strip():
        return False
    path = Path(retained_path)
    if not path.is_absolute():
        path = repo_root / path
    return path.exists()


def _validation_valid(entries: Any) -> bool:
    return isinstance(entries, list) and bool(entries) and all(isinstance(item, str) and item.strip() for item in entries)


def _row_checks(repo_root: Path, scenario_id: str, plan_item: dict[str, Any] | None) -> list[dict[str, Any]]:
    fields = _plan_fields(plan_item)
    return [
        _owner_check(scenario_id, fields["owner"]),
        _failure_mode_check(scenario_id, fields["failure_mode"]),
        _patch_plan_check(scenario_id, fields["patch_plan"]),
        _retained_check(repo_root, scenario_id, fields["retained"]),
        _validation_plan_check(scenario_id, fields["validation"]),
    ]


def _regression_row(repo_root: Path, regression: dict[str, Any], plan_item: dict[str, Any] | None) -> dict[str, Any]:
    scenario_id = str(regression.get("path") or "unknown")
    checks = _row_checks(repo_root, scenario_id, plan_item)
    fields = _plan_fields(plan_item)
    return {
        "scenario_id": scenario_id,
        "usage_score": regression.get("usage_score"),
        "baseline_score": regression.get("baseline_score"),
        "max_score": regression.get("max_score"),
        "owner": fields["owner"] or None,
        "failure_mode": fields["failure_mode"] or None,
        "patch_plan": fields["patch_plan"],
        "retained_regression": fields["retained"] if isinstance(fields["retained"], dict) else None,
        "validation_commands": fields["validation"] if isinstance(fields["validation"], list) else [],
        "checks": checks,
        "blockers": [check for check in checks if check["status"] == "blocker"],
    }


def _plan_fields(plan_item: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(plan_item, dict):
        return {"owner": "", "failure_mode": "", "patch_plan": [], "retained": None, "validation": []}
    patch_plan = plan_item.get("patch_plan")
    return {
        "owner": str(plan_item.get("owner") or ""),
        "failure_mode": str(plan_item.get("failure_mode") or ""),
        "patch_plan": patch_plan if isinstance(patch_plan, list) else [],
        "retained": plan_item.get("retained_regression"),
        "validation": plan_item.get("validation_commands"),
    }


def _owner_check(scenario_id: str, owner: str) -> dict[str, Any]:
    owner_ok = owner in OWNER_CHOICES
    return _check(
        "owner_classified",
        "pass" if owner_ok else "blocker",
        "Every Tessl baseline-win regression must be classified as skill, task, criteria, scorer, or environment.",
        [owner] if owner_ok else [scenario_id],
    )


def _failure_mode_check(scenario_id: str, failure_mode: str) -> dict[str, Any]:
    return _check(
        "failure_mode_recorded",
        "pass" if failure_mode.strip() else "blocker",
        "Every regression must record the concrete failure mode before rerun.",
        [] if failure_mode.strip() else [scenario_id],
    )


def _patch_plan_check(scenario_id: str, patch_plan: list[Any]) -> dict[str, Any]:
    patch_ok = _patch_plan_valid(patch_plan)
    return _check(
        "patch_plan_present",
        "pass" if patch_ok else "blocker",
        "Every regression must include at least one patch-plan item with file and change.",
        [] if patch_ok else [scenario_id],
    )


def _retained_check(repo_root: Path, scenario_id: str, retained: Any) -> dict[str, Any]:
    retained_ok = _retained_valid(repo_root, retained)
    evidence = [str(retained.get("path"))] if isinstance(retained, dict) and retained.get("path") else [scenario_id]
    return _check(
        "retained_regression_present",
        "pass" if retained_ok else "blocker",
        "Every regression must retain or import an internal regression artifact before rerun.",
        evidence,
    )


def _validation_plan_check(scenario_id: str, validation: Any) -> dict[str, Any]:
    validation_ok = _validation_valid(validation)
    return _check(
        "validation_plan_present",
        "pass" if validation_ok else "blocker",
        "Every regression must name rerun validation commands before another live Tessl handoff.",
        validation if validation_ok else [scenario_id],
    )


def _quality_checks(repo_root: Path, score_receipt: dict[str, Any], plan_path: Path | None, plan_error: str | None, regression_count: int) -> list[dict[str, Any]]:
    return [
        _check(
            "tessl_score_receipt_available",
            "pass" if score_receipt.get("score_summary") else "blocker",
            "Regression planning requires a parsed Tessl score receipt.",
            [],
        ),
        _check(
            "baseline_regressions_present",
            "pass" if regression_count else "blocker",
            "Regression planning requires at least one baseline-win scenario.",
            [],
        ),
        _check(
            "regression_plan_artifact_present",
            "pass" if plan_path is not None and plan_error is None else "blocker",
            "A regression plan artifact must classify every baseline-win scenario before live rerun.",
            [_repo_relative(repo_root, plan_path)] if plan_path else [plan_error or "missing_regression_plan"],
        ),
    ]


def _next_actions(blockers: list[dict[str, Any]], rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return ["Run tessl-score first and inspect whether the feedback loop is open."]
    blocker_ids = {check["id"] for check in blockers}
    actions = [_ACTION_BY_BLOCKER[blocker_id] for blocker_id in _ACTION_BY_BLOCKER if blocker_id in blocker_ids]
    return actions or ["Run scenario-quality, scorer-quality, scorer-calibration, dry Tessl staging, then live Tessl when budget allows."]


_ACTION_BY_BLOCKER = {
    "regression_plan_artifact_present": "Create references/eval-regression-plan.json with one owner-classified entry per baseline-win scenario.",
    "owner_classified": "Classify every regression owner as skill, task, criteria, scorer, or environment.",
    "retained_regression_present": "Retain or import an internal regression case for every baseline-win scenario.",
    "patch_plan_present": "Add patch-plan items naming file and change for each regression.",
    "validation_plan_present": "Name rerun validation commands before spending another live Tessl run.",
}


def _agent_summary(blockers: list[dict[str, Any]], regression_count: int, query: str) -> str:
    if blockers:
        return (
            f"Regression plan for {query} is blocked: {regression_count} baseline-win "
            "scenario(s) need owner classification, retained regression proof, patch plan, and rerun commands."
        )
    return f"Regression plan for {query} is ready for internal rerun proof before live Tessl."


def build_regression_plan_receipt(
    repo_root: Path,
    *,
    view_json: Path,
    source_path: Path,
    query: str,
    run_id: str | None = None,
    plan_path: Path | None = None,
) -> dict[str, Any]:
    skill_dir = _skill_dir(source_path)
    score_receipt = build_tessl_score_receipt(repo_root, view_json=view_json, skill=query, run_id=run_id)
    plan, loaded_plan_path, plan_error = _load_plan(skill_dir, plan_path)
    plan_index = _plan_regression_index(plan)
    regressions = _score_regressions(score_receipt)
    rows = _regression_rows(repo_root, regressions, plan_index)
    checks = _quality_checks(repo_root, score_receipt, loaded_plan_path, plan_error, len(regressions))
    blockers = _receipt_blockers(checks, rows)
    return {
        "schema_version": REGRESSION_PLAN_SCHEMA_VERSION,
        "schema_uri": REGRESSION_PLAN_SCHEMA_URI,
        "status": "blocked" if blockers else "preview",
        "operation": "eval_regression_plan_preview",
        "query": query,
        "skill_path": _repo_relative(repo_root, _skill_md(source_path)),
        "view_json": _repo_relative(repo_root, view_json),
        "plan_path": _repo_relative(repo_root, loaded_plan_path) if loaded_plan_path else None,
        "run_id": str(score_receipt.get("run_id") or run_id or ""),
        "source_score": score_receipt.get("score_summary"),
        "regression_count": len(regressions),
        "regressions": rows,
        "quality_checks": checks,
        "blockers": blockers,
        "ready_for_live_rerun": not blockers,
        "required_next_actions": _next_actions(blockers, rows),
        "mutation_performed": False,
        "promotion_performed": False,
        "agent_summary": _agent_summary(blockers, len(regressions), query),
    }


def _regression_rows(
    repo_root: Path,
    regressions: list[dict[str, Any]],
    plan_index: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        _regression_row(repo_root, regression, plan_index.get(str(regression.get("path") or "")))
        for regression in regressions
    ]


def _receipt_blockers(checks: list[dict[str, Any]], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [check for check in checks if check["status"] == "blocker"] + [
        blocker for row in rows for blocker in row["blockers"]
    ]
