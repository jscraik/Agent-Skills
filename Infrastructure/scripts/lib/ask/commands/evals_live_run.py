from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from .evals_core import (
    TESSL_LIVE_PRIVATE_VIEW_POLL_SECONDS,
    TESSL_LIVE_PRIVATE_VIEW_TIMEOUT_SECONDS,
    _as_text,
    _extract_tessl_eval_run_id,
    _parse_json_object_from_text,
    _tessl_eval_view_failure_reason,
    _tessl_eval_view_has_complete_scores,
    _tessl_eval_view_status,
    _validate_tessl_project_link_receipt,
    _write_tessl_live_submission_evidence,
    _write_tessl_live_view_evidence,
)
from .evals_live_preflight import (
    _stage_tessl_live_private_source,
    _tessl_live_budget_preflight,
    _tessl_live_oss_scenario_parity,
)
from .evals_policy import _tessl_live_private_policy
from .evals_project import (
    _tessl_live_private_eval_run_command,
    _tessl_pending_run_preflight,
    _tessl_run_budget_preflight,
)
from .evals_projection import _tessl_live_tile_slug
from .evals_quality import _tessl_project_identity, _validate_tessl_workspace
from .evals_shared import (
    EvalArtifactReadError,
    _sanitize_tessl_live_private_payload,
    _summarize_tessl_live_eval_view,
)

def _tessl_eval_result_common(
    *,
    command: str,
    source_path: str,
    staged_source: Path,
    copied_files: list[str],
    workspace: str,
    project_identity: dict[str, str | None],
    dry_run: bool,
) -> dict:
    plugin_version = None
    try:
        manifest = json.loads((staged_source / ".tessl-plugin" / "plugin.json").read_text(encoding="utf-8"))
        raw_version = manifest.get("version") if isinstance(manifest, dict) else None
        if isinstance(raw_version, str):
            plugin_version = raw_version
    except (OSError, json.JSONDecodeError):
        plugin_version = None
    return {
        "command": command,
        "source_path": source_path,
        "staged_source": str(staged_source),
        "plugin_manifest": str(staged_source / ".tessl-plugin" / "plugin.json"),
        "plugin_version": plugin_version,
        "tessl_project_marker": str(staged_source / "tessl.json") if (staged_source / "tessl.json").exists() else None,
        "staged_files": copied_files,
        "staging_policy": "stable_tmp_private_plugin_evidence",
        "workspace": workspace,
        "project_identity": project_identity,
        "visibility": "private",
        "dry_run": dry_run,
        "live_private": True,
        "evidence_retention": f"staged directory is left under {tempfile.gettempdir()}/ask-tessl-evals for inspection",
        "policy": _tessl_live_private_policy(workspace),
    }


def _tessl_live_scenario_preflight(
    repo_root: Path,
    path: str,
    staged_source: Path,
    common: dict,
) -> dict | None:
    try:
        parity = _tessl_live_oss_scenario_parity(repo_root, path, staged_source)
        budget_preflight = _tessl_live_budget_preflight(staged_source)
    except EvalArtifactReadError as exc:
        return {
            "status": "blocked", **common, "raw_output": "", "raw_error": str(exc),
            "blocker": "Tessl live preflight could not read a JSON evidence artifact.",
            "blocker_class": "blocked_validation",
        }
    common["oss_scenario_parity"] = parity
    common["budget_preflight"] = budget_preflight
    if parity.get("status") != "pass":
        return {
            "status": "blocked", **common, "raw_output": "", "raw_error": "",
            "blocker": "Tessl live scenario set includes scenarios without both oss-local and oss-cloud pass evidence.",
            "blocker_class": "blocked_validation",
        }
    if budget_preflight.get("status") != "pass":
        blockers = budget_preflight.get("blockers")
        blocker_text = "; ".join(str(item) for item in blockers) if isinstance(blockers, list) else None
        return {
            "status": "blocked", **common, "raw_output": "", "raw_error": "",
            "blocker": blocker_text or "Tessl live budget preflight blocked the staged scenario set.",
            "blocker_class": budget_preflight.get("blocker_class") or "blocked_validation",
        }
    return None


def _tessl_live_blocked(command: str, path: str, workspace: str | None, dry_run: bool, error: str, blocker: str) -> dict:
    return {
        "status": "blocked", "command": command, "source_path": path,
        "raw_output": "", "raw_error": error, "blocker": blocker,
        "blocker_class": "blocked_validation", "policy": _tessl_live_private_policy(workspace),
        "live_private": True, "dry_run": dry_run,
    }


def _tessl_live_effects_block(command: str, path: str, workspace: str | None, dry_run: bool) -> dict | None:
    unmocked_test_process = os.environ.get("PYTEST_CURRENT_TEST") and type(subprocess.run).__module__ != "unittest.mock"
    if not dry_run and unmocked_test_process:
        return _tessl_live_blocked(
            command, path, workspace, dry_run, "",
            "Tessl live evaluation is blocked by the hermetic test effect policy unless subprocess execution is an in-process mock.",
        )
    if dry_run or os.environ.get("ASK_EXTERNAL_EFFECTS", "deny") == "allow":
        return None
    return _tessl_live_blocked(
        command, path, workspace, dry_run, "",
        "Tessl live evaluation is blocked by the external-effect policy; provider submission requires a separately authorised operator process with ASK_EXTERNAL_EFFECTS=allow.",
    )


def _tessl_live_prepare(repo_root: Path, path: str, workspace: str | None, dry_run: bool, command: str) -> tuple[str, Path, list[str], str] | dict:
    try:
        normalized_workspace = _validate_tessl_workspace(workspace)
        staged_source, copied_files = _stage_tessl_live_private_source(repo_root, path, normalized_workspace)
    except (OSError, ValueError) as exc:
        return _tessl_live_blocked(command, path, workspace, dry_run, str(exc), f"Failed to stage private Tessl plugin eval source: {exc}")
    return normalized_workspace, staged_source, copied_files, f"tessl eval run --json --workspace {normalized_workspace} {staged_source}"


def _tessl_live_dry_result(common: dict) -> dict:
    return {"status": "pass", **common, "raw_output": "", "raw_error": "", "exit_code": 0, "blocker": None, "blocker_class": None}


def _tessl_live_runtime_preflight(repo_root: Path, path: str, workspace: str, staged_source: Path, common: dict) -> tuple[str, dict[str, str]] | dict:
    tessl_path = shutil.which("tessl")
    if not tessl_path:
        return {"status": "blocked", **common, "raw_output": "", "raw_error": "", "blocker": "Installed native tessl CLI was not found on PATH.", "blocker_class": "blocked_runtime"}
    project_link = _validate_tessl_project_link_receipt(repo_root, path, workspace, common["project_identity"])
    common["project_link"] = project_link
    if project_link.get("status") == "blocked":
        return {"status": "blocked", **common, "raw_output": "", "raw_error": "", "blocker": project_link.get("blocker"), "blocker_class": project_link.get("blocker_class")}
    tessl_env = dict(os.environ)
    tessl_env["TESSL_AUTO_UPDATE_INTERVAL_MINUTES"] = "0"
    project_name = str(common["project_identity"].get("project") or _tessl_live_tile_slug(repo_root / path))
    return _tessl_live_run_preflights(tessl_path, workspace, project_name, staged_source, tessl_env, common)


def _tessl_live_run_preflights(tessl_path: str, workspace: str, project_name: str, staged_source: Path, tessl_env: dict[str, str], common: dict) -> tuple[str, dict[str, str]] | dict:
    pending = _tessl_pending_run_preflight(tessl_path, workspace, project_name, staged_source, tessl_env)
    common["pending_run_preflight"] = pending
    if pending.get("status") == "blocked":
        return _tessl_live_preflight_block(common, pending)
    budget = _tessl_run_budget_preflight(tessl_path, workspace, staged_source, tessl_env)
    common["run_budget_preflight"] = budget
    if budget.get("status") == "blocked":
        return _tessl_live_preflight_block(common, budget)
    return tessl_path, tessl_env


def _tessl_live_preflight_block(common: dict, preflight: dict) -> dict:
    return {
        "status": "blocked", **common,
        "raw_output": str(preflight.get("raw_output") or ""),
        "raw_error": str(preflight.get("raw_error") or ""),
        "blocker": preflight.get("blocker"), "blocker_class": preflight.get("blocker_class"),
    }


def _tessl_live_process(repo_root: Path, path: str, workspace: str, staged_source: Path, tessl_path: str, tessl_env: dict[str, str], common: dict) -> dict:
    try:
        process = subprocess.run(_tessl_live_private_eval_run_command(tessl_path, workspace, staged_source), cwd=str(staged_source), capture_output=True, text=True, timeout=600, env=tessl_env)
    except subprocess.TimeoutExpired as exc:
        return {"status": "blocked", **common, "raw_output": _as_text(exc.stdout), "raw_error": _as_text(exc.stderr), "blocker": "Tessl private plugin eval timed out after 600 seconds.", "blocker_class": "blocked_runtime"}
    except OSError as exc:
        return {"status": "blocked", **common, "raw_output": "", "raw_error": str(exc), "blocker": f"Failed to run Tessl private plugin eval: {exc}", "blocker_class": "blocked_runtime"}
    return _tessl_live_process_result(repo_root, path, workspace, staged_source, tessl_path, tessl_env, common, process)


def _tessl_live_process_result(repo_root: Path, path: str, workspace: str, staged_source: Path, tessl_path: str, tessl_env: dict[str, str], common: dict, process: subprocess.CompletedProcess) -> dict:
    raw_output, raw_error = process.stdout, process.stderr
    status, blocker, blocker_class = _tessl_live_process_status(process.returncode, raw_output, raw_error, repo_root, path, workspace)
    eval_run_id = _extract_tessl_eval_run_id(raw_output)
    submission = _write_tessl_live_submission_evidence(repo_root, path, run_id=eval_run_id, workspace=workspace, staged_source=staged_source, project_identity=common["project_identity"])
    view = _tessl_live_view_result(tessl_path, staged_source, tessl_env, eval_run_id, status, blocker, blocker_class)
    view["evidence_path"] = _write_tessl_live_view_evidence(repo_root, path, eval_run_id, view["raw_output"])
    return _tessl_live_result(common, process.returncode, raw_output, raw_error, eval_run_id, submission, view)


def _tessl_live_process_status(returncode: int, raw_output: str, raw_error: str, repo_root: Path, path: str, workspace: str) -> tuple[str, str | None, str | None]:
    rules = _tessl_live_blocker_rules(repo_root, path, workspace)
    matched = next((rule for rule in rules if returncode != 0 and rule[0] in f"{raw_output}\n{raw_error}".lower()), None)
    if matched is None:
        return ("pass" if returncode == 0 else "fail"), None, None
    _marker, blocker_class, message = matched
    return "blocked", message, blocker_class


def _tessl_live_blocker_rules(repo_root: Path, path: str, workspace: str) -> tuple[tuple[str, str, str], ...]:
    project = f"{workspace}/{_tessl_live_tile_slug(repo_root / path)}"
    return (
        ("authenticate with tessl", "blocked_auth", "Tessl CLI is installed locally, but authentication is required before private plugin evals can run."),
        ("no existing project safely matches this directory", "blocked_validation", "Tessl CLI is authenticated, but no Tessl project/workspace is linked for the temp-staged private plugin eval directory. Run tessl project create/link/repair for a live project lane."),
        ("no tessl project found", "blocked_validation", "Tessl CLI could not find a tessl.json project marker in the staged private plugin eval directory."),
        ("project that was not found or is not accessible", "blocked_validation", f"Tessl project {project} was not found or is not accessible. Create, link, or repair that project in workspace {workspace} before running live evals."),
        ("points at a different repository or directory path", "blocked_validation", "Tessl project binding points at a different source directory than the temp-staged private eval directory."),
    )


def _tessl_live_view_result(tessl_path: str, staged_source: Path, tessl_env: dict[str, str], eval_run_id: str | None, status: str, blocker: str | None, blocker_class: str | None) -> dict:
    result = {"status": status, "blocker": blocker, "blocker_class": blocker_class, "summary": None, "raw_output": "", "raw_error": "", "attempts": 0, "view_status": None}
    if status != "pass":
        return result
    if not eval_run_id:
        result.update(status="blocked", blocker="Tessl private plugin eval completed but did not return an eval run id for score/baseline verification.", blocker_class="blocked_validation")
        return result
    return _tessl_live_poll_view(tessl_path, staged_source, tessl_env, eval_run_id, result)


def _tessl_live_poll_view(tessl_path: str, staged_source: Path, tessl_env: dict[str, str], eval_run_id: str, result: dict) -> dict:
    deadline = time.monotonic() + TESSL_LIVE_PRIVATE_VIEW_TIMEOUT_SECONDS
    try:
        while True:
            result["attempts"] += 1
            process = subprocess.run([tessl_path, "eval", "view", "--json", eval_run_id], cwd=str(staged_source), capture_output=True, text=True, timeout=600, env=tessl_env)
            result["raw_output"], result["raw_error"] = process.stdout, process.stderr
            payload = _parse_json_object_from_text(process.stdout) if process.returncode == 0 else None
            result["view_status"] = _tessl_eval_view_status(payload) if payload else None
            if process.returncode != 0 or _tessl_live_view_terminal(payload, result["view_status"], deadline):
                return _tessl_live_assess_view(process.returncode, payload, deadline, result)
            time.sleep(TESSL_LIVE_PRIVATE_VIEW_POLL_SECONDS)
    except subprocess.TimeoutExpired as exc:
        result.update(status="blocked", blocker="Tessl private plugin eval view timed out while waiting for scored results.", blocker_class="blocked_runtime", raw_output=_as_text(exc.stdout), raw_error=_as_text(exc.stderr))
    except OSError as exc:
        result.update(status="blocked", blocker=f"Failed to inspect Tessl private plugin eval results: {exc}", blocker_class="blocked_runtime", raw_error=str(exc))
    return result


def _tessl_live_view_terminal(payload: dict | None, view_status: str | None, deadline: float) -> bool:
    return payload is None or _tessl_eval_view_has_complete_scores(payload) or view_status in {"failed", "error", "cancelled", "canceled"} or time.monotonic() >= deadline


def _tessl_live_assess_view(returncode: int, payload: dict | None, deadline: float, result: dict) -> dict:
    if returncode != 0:
        result.update(status="blocked", blocker="Tessl private plugin eval completed but result inspection failed.", blocker_class="blocked_validation")
        return result
    try:
        summary = _tessl_live_view_summary(payload, deadline, result["view_status"])
    except ValueError as exc:
        detail = str(exc)
        quota_block = "EVAL_QUOTA_EXCEEDED" in detail
        result.update(
            status="blocked",
            blocker=detail if quota_block else f"Failed to parse Tessl private plugin eval score summary: {detail}",
            blocker_class="blocked_environment" if quota_block else result["blocker_class"] or "blocked_validation",
        )
        return result
    result["summary"] = summary
    if not summary["meets_min_score"] or not summary["beats_baseline"]:
        score, baseline = round(float(summary["score"]) * 100, 2), round(float(summary["baseline_score"]) * 100, 2)
        result.update(status="fail", blocker=f"Tessl private plugin eval completed but failed readiness: score {score}% vs baseline {baseline}%.", blocker_class=None)
    return result


def _tessl_live_view_summary(payload: dict | None, deadline: float, view_status: str | None) -> dict:
    if payload is None:
        raise ValueError("No JSON object found in Tessl eval view output.")
    if _tessl_eval_view_has_complete_scores(payload):
        return _summarize_tessl_live_eval_view(payload)
    failure = _tessl_eval_view_failure_reason(payload)
    if failure:
        code, message = failure
        raise ValueError(f"Tessl eval run failed before scoring: {code}: {message}")
    if time.monotonic() >= deadline:
        raise ValueError("Tessl eval view did not reach complete scored results before timeout.")
    raise ValueError(f"Tessl eval view is not scored yet (status={view_status or 'unknown'}).")


def _tessl_live_result(common: dict, exit_code: int, raw_output: str, raw_error: str, eval_run_id: str | None, submission: str | None, view: dict) -> dict:
    return {
        "status": view["status"], **common, "exit_code": exit_code, "eval_run_id": eval_run_id,
        "submission_evidence_path": submission, "live_result_summary": view["summary"],
        "view_attempts": view["attempts"], "view_status": view["view_status"], "view_evidence_path": view["evidence_path"],
        "view_raw_output": _sanitize_tessl_live_private_payload(view["raw_output"]),
        "view_raw_error": _sanitize_tessl_live_private_payload(view["raw_error"]),
        "raw_output": _sanitize_tessl_live_private_payload(raw_output), "raw_error": _sanitize_tessl_live_private_payload(raw_error),
        "blocker": view["blocker"], "blocker_class": view["blocker_class"],
    }


def _run_tessl_live_private_eval(repo_root: Path, path: str, *, workspace: str | None, dry_run: bool = False) -> dict:
    """Run or preview the opt-in private Tessl plugin eval lane."""
    command = "tessl eval run --json --workspace <workspace> <staged-plugin-dir>"
    prepared = _tessl_live_prepare(repo_root, path, workspace, dry_run, command)
    if isinstance(prepared, dict):
        return prepared
    normalized_workspace, staged_source, copied_files, command = prepared
    common = _tessl_eval_result_common(command=command, source_path=path, staged_source=staged_source, copied_files=copied_files, workspace=normalized_workspace, project_identity=_tessl_project_identity((repo_root / path).resolve(), normalized_workspace), dry_run=dry_run)
    if blocked := _tessl_live_scenario_preflight(repo_root, path, staged_source, common):
        return blocked
    if blocked := _tessl_live_effects_block(command, path, normalized_workspace, dry_run):
        return blocked
    if dry_run:
        return _tessl_live_dry_result(common)
    runtime = _tessl_live_runtime_preflight(repo_root, path, normalized_workspace, staged_source, common)
    if isinstance(runtime, dict):
        return runtime
    tessl_path, tessl_env = runtime
    return _tessl_live_process(repo_root, path, normalized_workspace, staged_source, tessl_path, tessl_env, common)

__all__ = [name for name in globals() if not name.startswith("__")]
