"""Read-only, receipt-bound inspection for a submitted private Tessl eval."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

from ask.envelope import CallResult, ErrorObject


def inspect_tessl_live_private_eval(
    repo_root: Path,
    *,
    skill_path: str,
    run_id: str,
    workspace: str,
) -> CallResult:
    """Fetch one receipt-bound result without creating or resubmitting an eval."""
    context = _validated_view_context(repo_root, skill_path, run_id, workspace)
    if isinstance(context, CallResult):
        return context
    project_link_error = _project_link_error(repo_root, context)
    if project_link_error is not None:
        return project_link_error
    process = _run_tessl_view(repo_root, context["run_id"])
    if isinstance(process, CallResult):
        return process
    common = _view_common(repo_root, context, process)
    return _view_result(process, common)


def _validated_view_context(repo_root: Path, skill_path: str, run_id: str, workspace: str) -> dict[str, str] | CallResult:
    """Validate the caller's identity against its existing submitted-run receipt."""
    from ask.commands import evals

    try:
        normalized_workspace = evals._validate_tessl_workspace(workspace)
    except ValueError as exc:
        return _blocked("blocked_validation", str(exc))
    normalized_run_id = evals._tessl_evidence_segment(run_id)
    if normalized_run_id is None:
        return _blocked("blocked_validation", "Tessl view requires a non-empty run id containing only letters, digits, dots, underscores, or hyphens.")
    path = evals._resolve_eval_skill_path(repo_root, skill_path)
    submission_path = evals._tessl_live_evidence_file(repo_root, path, normalized_run_id, "tessl-eval-submission.json")
    if submission_path is None or not submission_path.is_file() or submission_path.is_symlink():
        return _blocked("blocked_validation", "Tessl view requires the current skill's existing submitted-run receipt; it will not inspect an unbound run id.")
    if not _submission_matches(submission_path, normalized_run_id, normalized_workspace, path):
        return _blocked("blocked_validation", "Tessl submitted-run receipt does not bind this run to the requested skill and workspace.")
    return {"run_id": normalized_run_id, "workspace": normalized_workspace, "skill_path": path, "submission_path": str(submission_path)}


def _submission_matches(submission_path: Path, run_id: str, workspace: str, skill_path: str) -> bool:
    """Return whether one regular submitted-run receipt exactly binds the request."""
    try:
        submission = json.loads(submission_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return isinstance(submission, dict) and all((
        submission.get("run_id") == run_id,
        submission.get("workspace") == workspace,
        submission.get("skill_path") == skill_path,
    ))


def _project_link_error(repo_root: Path, context: dict[str, str]) -> CallResult | None:
    """Return the project-link blocker before any native Tessl invocation."""
    from ask.commands import evals

    identity = evals._tessl_project_identity((repo_root / context["skill_path"]).resolve(), context["workspace"])
    context["project_identity"] = identity
    project_link = evals._validate_tessl_project_link_receipt(repo_root, context["skill_path"], context["workspace"], identity)
    if project_link.get("status") == "pass":
        return None
    return _blocked(
        str(project_link.get("blocker_class") or "blocked_validation"),
        str(project_link.get("blocker") or "Tessl view requires a current project-link receipt."),
    )


def _run_tessl_view(repo_root: Path, run_id: str) -> subprocess.CompletedProcess[str] | CallResult:
    """Invoke only the installed native CLI's read-only view command."""
    from ask.commands import evals

    tessl_path = evals.shutil.which("tessl")
    if not tessl_path:
        return _blocked("blocked_runtime", "Installed native tessl CLI was not found on PATH.")
    env = dict(os.environ, TESSL_AUTO_UPDATE_INTERVAL_MINUTES="0")
    try:
        return subprocess.run([tessl_path, "eval", "view", "--json", run_id], cwd=str(repo_root), capture_output=True, text=True, timeout=600, env=env)
    except subprocess.TimeoutExpired:
        return _blocked("blocked_runtime", "Tessl eval view timed out while inspecting the submitted run.")
    except OSError as exc:
        return _blocked("blocked_runtime", f"Failed to inspect Tessl eval view: {exc}")


def _view_common(repo_root: Path, context: dict[str, str], process: subprocess.CompletedProcess[str]) -> dict[str, object]:
    """Capture bounded, receipt-safe evidence metadata for one native view."""
    from ask.commands import evals

    sanitized_view = evals._sanitize_tessl_live_private_payload(process.stdout)
    view_path = evals._write_tessl_live_view_evidence(repo_root, context["skill_path"], context["run_id"], process.stdout)
    submission_path = Path(context["submission_path"])
    return {
        **context,
        "submission_evidence_path": str(submission_path.relative_to(repo_root)),
        "view_evidence_path": view_path,
        "command": "tessl eval view --json <submitted-run-id>",
        "exit_code": process.returncode,
        "view_evidence_bytes": len(sanitized_view.encode("utf-8")),
        "view_evidence_sha256": hashlib.sha256(sanitized_view.encode("utf-8")).hexdigest(),
    }


def _view_result(process: subprocess.CompletedProcess[str], common: dict[str, object]) -> CallResult:
    """Classify one fetched view without collapsing pending into a passing score."""
    from ask.commands import evals

    if process.returncode != 0:
        return _blocked("blocked_runtime", "Tessl eval view failed while inspecting the submitted run.", common)
    payload = evals._parse_json_object_from_text(process.stdout)
    if payload is None:
        return _blocked("blocked_validation", "Tessl eval view returned no JSON object.", common)
    status = evals._tessl_eval_view_status(payload)
    if not evals._tessl_eval_view_has_complete_scores(payload):
        return CallResult(status="success", data={"status": "pending", **common, "view_status": status, "blocker": None})
    return _scored_view_result(evals, payload, status, common)


def _scored_view_result(evals: object, payload: dict[str, object], status: str, common: dict[str, object]) -> CallResult:
    """Apply the configured score and baseline gate to a complete Tessl result."""
    try:
        summary = evals._summarize_tessl_live_eval_view(payload)
    except ValueError as exc:
        return _blocked("blocked_validation", str(exc), {**common, "view_status": status})
    accepted = bool(summary["meets_min_score"]) and bool(summary["beats_baseline"])
    message = None if accepted else "Tessl scored run did not meet the configured score and baseline gate."
    return CallResult(
        status="success" if accepted else "error",
        data={"status": "pass" if accepted else "fail", **common, "view_status": status, "live_result_summary": summary, "blocker": message, "blocker_class": None},
        errors=[] if accepted else [ErrorObject(code="ERR_VALIDATION", message=str(message))],
    )


def _blocked(blocker_class: str, message: str, data: dict[str, object] | None = None) -> CallResult:
    code = "ERR_RUNTIME" if blocker_class == "blocked_runtime" else "ERR_VALIDATION"
    return CallResult(
        status="error",
        data={"status": "blocked", **(data or {}), "blocker": message, "blocker_class": blocker_class},
        errors=[ErrorObject(code=code, message=message)],
    )
