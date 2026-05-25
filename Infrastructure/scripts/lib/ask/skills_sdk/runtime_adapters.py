from __future__ import annotations

import json
import re
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ask.skills_sdk.contracts import runtime_failure_payload, skills_validation_command


ResolveSkillHandle = Callable[..., dict[str, Any]]
CheckCommandHandles = Callable[..., dict[str, Any]]
SUPPORTED_RUNTIME_TARGETS = {"any", "codex", "agents"}
EVIDENCE_RUNTIME_TARGETS = {"codex", "agents"}
WORKSPACE_ROOT_MARKER = "${WORKSPACE_ROOT}"
HOME_MARKER = "${HOME}"
SAFE_EVIDENCE_SEGMENT_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")
RUNTIME_REACHABILITY_FAILURES = {
    "user_runtime_ready",
    "codex_user_runtime_ready",
    "agents_user_runtime_ready",
    "codex_user_link",
    "agents_user_link",
    "codex_user_command_handle_exists",
    "agents_user_command_handle_exists",
}


def normalize_runtime_target(runtime_target: object) -> str:
    """
    Normalize a runtime target value to a lowercase string with surrounding whitespace removed.
    
    Parameters:
        runtime_target (object): The input value to normalize; it will be converted with `str()` before trimming and lowercasing.
    
    Returns:
        The runtime target as a lowercase string with leading and trailing whitespace removed.
    """
    return str(runtime_target).strip().lower()


def invalid_runtime_target_failure(handle: str, runtime_target: object) -> dict[str, Any]:
    """
    Create a standardized runtime validation failure payload for an invalid runtime target.
    
    Parameters:
        handle (str): Skill handle (may include a leading '$'); used to build suggested validation commands.
        runtime_target (object): The original runtime target value provided by the user; will be normalized for the failure message.
    
    Returns:
        dict[str, Any]: A runtime failure payload describing the invalid `runtime_target`, including an error code, failed check id,
        recovery guidance, and suggested validation command(s).
    """
    normalized_target = normalize_runtime_target(runtime_target)
    safe_handle = handle.strip().lstrip("$") or handle
    recovery_guidance = "Use --runtime-target any, --runtime-target codex, or --runtime-target agents."
    return runtime_failure_payload(
        command="skills proof",
        error_code="ERR_VALIDATION",
        failed_check_id="runtime_target",
        path="runtime_target",
        message=f"Invalid runtime target '{normalized_target}'.",
        recovery_guidance=recovery_guidance,
        validation_commands=[
            skills_validation_command("proof", safe_handle, "--runtime-target", "any"),
        ],
    )


def _utc_now() -> str:
    """
    Return the current UTC time formatted as an ISO-8601 timestamp without microseconds and with a trailing 'Z'.
    
    Returns:
        str: ISO-8601 UTC timestamp (e.g. '2024-05-01T12:00:00Z')
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _repo_relative(repo_root: Path, path: Path) -> str:
    """
    Produce a repository-relative string for `path` when it is inside `repo_root`; otherwise return the original path string.
    
    Parameters:
    	repo_root (Path): Repository root path used as the base for relativization.
    	path (Path): Path to be made relative to `repo_root` when possible.
    
    Returns:
    	relative_path (str): `path` made relative to `repo_root` if `path` is beneath `repo_root`, otherwise `str(path)`.
    """
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    """
    Ensure the parent directory exists and write the given payload to the specified path as pretty-printed JSON.
    
    Parameters:
        path (Path): Filesystem path where the JSON will be written; parent directories are created if missing.
        payload (dict[str, Any]): JSON-serializable mapping to write.
    
    Notes:
        The JSON is written with 2-space indentation, keys sorted, encoded as UTF-8, and terminated with a single trailing newline.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _redact_runtime_path(value: str, repo_root: Path) -> str:
    repo_root_text = str(repo_root.resolve())
    home_text = str(Path.home())
    if value == repo_root_text:
        return WORKSPACE_ROOT_MARKER
    if value.startswith(repo_root_text + "/"):
        return WORKSPACE_ROOT_MARKER + value[len(repo_root_text) :]
    if value == home_text:
        return HOME_MARKER
    if value.startswith(home_text + "/"):
        return HOME_MARKER + value[len(home_text) :]
    return value


def _redact_runtime_paths(value: Any, repo_root: Path) -> Any:
    if isinstance(value, str):
        return _redact_runtime_path(value, repo_root)
    if isinstance(value, list):
        return [_redact_runtime_paths(item, repo_root) for item in value]
    if isinstance(value, dict):
        return {key: _redact_runtime_paths(item, repo_root) for key, item in value.items()}
    return value


def _runtime_status_for_proof(proof: dict[str, Any]) -> str:
    """
    Map a command-handle proof object to a runtime status label.
    
    Examines `proof["status"]` and, when not `"pass"`, inspects
    `proof["runtime_failure"]["failed_check_id"]` (defaults to `"runtime_reachability"`).
    Returns `"implemented_enforced"` when the proof status is `"pass"`;
    returns `"blocked_runtime"` when the failed check id is one of
    `RUNTIME_REACHABILITY_FAILURES`; otherwise returns `"stale_or_drifted"`.
    
    Parameters:
        proof (dict[str, Any]): The command-handle proof payload.
    
    Returns:
        str: One of `"implemented_enforced"`, `"blocked_runtime"`, or `"stale_or_drifted"` describing runtime status.
    """
    if proof.get("status") == "pass":
        return "implemented_enforced"
    runtime_failure = proof.get("runtime_failure")
    failed_check_id = (
        str(runtime_failure.get("failed_check_id"))
        if isinstance(runtime_failure, dict) and runtime_failure.get("failed_check_id")
        else "runtime_reachability"
    )
    return "blocked_runtime" if failed_check_id in RUNTIME_REACHABILITY_FAILURES else "stale_or_drifted"


def _claim_status_for_runtime(runtime_status: str) -> str:
    """
    Map a normalized runtime status to the claim status used in evidence artifacts.
    
    Parameters:
        runtime_status (str): Runtime status string (e.g., "implemented_enforced" for a successful runtime proof).
    
    Returns:
        str: "pass" when `runtime_status` is "implemented_enforced", "blocked" otherwise.
    """
    return "pass" if runtime_status == "implemented_enforced" else "blocked"


def _runtime_display_name(runtime_target: str) -> str:
    """
    Map a runtime target identifier to a human-friendly display name.
    
    Returns:
        display_name (str): "Codex" when `runtime_target` is "codex", "Agents" otherwise.
    """
    return "Codex" if runtime_target == "codex" else "Agents"


def _path_is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(parent.resolve(strict=False))
        return True
    except (OSError, ValueError):
        return False


def _runtime_mode(link: dict[str, object], *, handle_points_to_workspace: bool) -> str:
    if bool(link.get("points_to_workspace_runtime")):
        return "root_symlink"
    if handle_points_to_workspace:
        return "handle_bridge"
    if bool(link.get("exists")):
        return "foreign_or_unmanaged_root"
    return "missing_root"


def _runtime_evidence_path_segment(handle: str) -> str:
    segment = SAFE_EVIDENCE_SEGMENT_PATTERN.sub("-", handle.strip().lstrip("$"))
    return segment.strip(".-") or "unknown"


def _runtime_evidence_context(
    *,
    repo_root: Path,
    proof: dict[str, Any],
    actor_type: str,
) -> dict[str, Any]:
    """
    Builds a standardized context object used to generate runtime-proof evidence artifacts.
    
    Parameters:
    	repo_root (Path): Repository root used to resolve paths and write evidence files.
    	proof (dict[str, Any]): Command-handle runtime proof object; fields inspected include `handle`, `runtime_target`, `resolution`, `status`, and `runtime_failure`.
    	actor_type (str): Actor type to record in the context (e.g., "agent" or "user").
    
    Returns:
    	dict[str, Any]: Context mapping containing:
    		- repo_root: the given repo_root Path
    		- handle: normalized skill handle (no leading `$`, fallback "unknown")
    		- runtime_target: normalized runtime target string
    		- created_at: ISO-8601 UTC timestamp string
    		- evidence_dir, card_path, receipt_path, artifact_path, probe_path: Paths for output artifacts under `.harness/evidence/runtime-proof/...`
    		- command: validation command string for reproducing the proof
    		- runtime_status: normalized runtime status (e.g., "implemented_enforced", "blocked_runtime", "stale_or_drifted")
    		- claim_status: derived claim status ("pass" or "blocked")
    		- runtime_failure: runtime failure dict when present
    		- failed_check_id: failed check identifier (defaults to "runtime_reachability")
    		- blocker: human-readable blocker message or default passed message
    		- exit_code: 0 for proof pass, 2 otherwise
    		- source_paths: list of canonical source path plus related implementation paths
    		- actor_type: the provided actor_type
    """
    handle = str(proof.get("handle") or "unknown").strip().lstrip("$") or "unknown"
    runtime_target = str(proof.get("runtime_target") or "")
    resolution = proof.get("resolution") if isinstance(proof.get("resolution"), dict) else {}
    handle_path_segment = _runtime_evidence_path_segment(handle)
    source_path = str(
        resolution.get("source_path")
        or repo_root / ".agents" / "skills" / handle_path_segment / "SKILL.md"
    )
    source = Path(source_path)
    canonical_source_path = _repo_relative(repo_root, source if source.is_absolute() else repo_root / source_path)
    evidence_dir = repo_root / ".harness" / "evidence" / "runtime-proof" / handle_path_segment / runtime_target
    runtime_status = _runtime_status_for_proof(proof)
    runtime_failure = proof.get("runtime_failure") if isinstance(proof.get("runtime_failure"), dict) else {}
    return {
        "repo_root": repo_root,
        "handle": handle,
        "runtime_target": runtime_target,
        "created_at": _utc_now(),
        "evidence_dir": evidence_dir,
        "card_path": evidence_dir / "runtime-card.json",
        "receipt_path": evidence_dir / "evidence-receipt.json",
        "artifact_path": evidence_dir / "artifact-record.json",
        "probe_path": evidence_dir / "probe.json",
        "command": skills_validation_command("proof", handle, "--runtime-target", runtime_target),
        "runtime_status": runtime_status,
        "claim_status": _claim_status_for_runtime(runtime_status),
        "runtime_failure": runtime_failure,
        "failed_check_id": str(runtime_failure.get("failed_check_id") or "runtime_reachability"),
        "blocker": str(
            runtime_failure.get("message")
            or f"{_runtime_display_name(runtime_target)} runtime proof passed."
        ),
        "exit_code": 0 if proof.get("status") == "pass" else 2,
        "source_paths": [
            canonical_source_path,
            "Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py",
            "Infrastructure/scripts/lib/ask/commands/skills_impl.py",
        ],
        "actor_type": actor_type,
        "runtime_diagnostics": (
            proof.get("runtime_diagnostics")
            if isinstance(proof.get("runtime_diagnostics"), dict)
            else {}
        ),
    }


def _artifact_record(
    context: dict[str, Any],
    *,
    artifact_id: str,
    artifact_type: str,
    path: str,
    consumer_contract: str,
) -> dict[str, Any]:
    """
    Builds a standardized artifact record describing a generated evidence artifact.
    
    Parameters:
        context (dict): Execution context containing at least the keys
            - "source_paths": list of source paths associated with the artifact
            - "repo_root": repository root Path-like object
            - "actor_type": actor type string
            - "command": command string that generated the artifact
            - "claim_status": validation status for the artifact
        artifact_id (str): Stable identifier for the artifact.
        artifact_type (str): Semantic type of the artifact (e.g. "runtime_card", "verifier_output").
        path (str): Filesystem path to the artifact file.
        consumer_contract (str): Identifier of the consumer contract that this artifact satisfies.
    
    Returns:
        dict: Artifact record containing keys:
            - "artifact_id", "artifact_type", "path"
            - "source_identity": with "source_paths" from context
            - "workspace_root": resolved repository root string
            - "actor_type", "mutation_scope", "visibility_status"
            - "generated_by": command from context
            - "validation_status": claim status from context
            - "consumer_contract"
    """
    return {
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "path": path,
        "source_identity": {"source_paths": context["source_paths"]},
        "workspace_root": WORKSPACE_ROOT_MARKER,
        "actor_type": context["actor_type"],
        "mutation_scope": "evidence_write",
        "visibility_status": "user_observable",
        "generated_by": context["command"],
        "validation_status": context["claim_status"],
        "consumer_contract": consumer_contract,
    }


def _probe_payload(context: dict[str, Any], proof: dict[str, Any]) -> dict[str, Any]:
    """
    Build the probe payload used as the verifier output for a command-handle runtime proof.
    
    Parameters:
        context (dict[str, Any]): Runtime evidence context containing keys:
            `handle`, `runtime_target`, `runtime_status`, `created_at`, `command`, and `exit_code`.
        proof (dict[str, Any]): The command-handle proof object to embed in the probe.
    
    Returns:
        dict[str, Any]: Probe payload with the following keys:
            `schema_version` (str): Payload schema identifier (`"command-handle-runtime-probe.v1"`).
            `handle` (str): Normalized skill handle.
            `runtime_target` (str): Target runtime name (e.g., `"codex"`, `"agents"`).
            `runtime_status` (str): Derived runtime status (e.g., `"implemented_enforced"`, `"blocked_runtime"`).
            `observed_at` (str): ISO-8601 UTC timestamp when the probe was created.
            `command` (str): Validation command used to produce or re-run the proof.
            `exit_code` (int): Exit code from the validation command.
            `proof` (dict[str, Any]): The embedded raw proof object.
    """
    return {
        "schema_version": "command-handle-runtime-probe.v1",
        "handle": context["handle"],
        "runtime_target": context["runtime_target"],
        "runtime_status": context["runtime_status"],
        "observed_at": context["created_at"],
        "command": context["command"],
        "exit_code": context["exit_code"],
        "proof": _redact_runtime_paths(proof, context["repo_root"]),
    }


def _receipt_payload(context: dict[str, Any], relative_card_path: str, relative_probe_path: str) -> dict[str, Any]:
    """
    Builds the runtime-proof receipt payload describing the claim, status, artifacts, verifier, and observed timestamp.
    
    Parameters:
        context (dict[str, Any]): Evidence context (as produced by _runtime_evidence_context) containing at least:
            - handle, runtime_target, claim_status, runtime_status
            - command, exit_code, source_paths, created_at, blocker (when blocked)
        relative_card_path (str): Repository-relative path to the runtime card artifact.
        relative_probe_path (str): Repository-relative path to the probe artifact.
    
    Returns:
        dict[str, Any]: A receipt dictionary including:
            - `receipt_id`: deterministic id "runtime-proof-<handle>-<runtime_target>"
            - `claim` and `claim_status`
            - runtime fields (`runtime_target`, `runtime_status`)
            - command/probe commands and exit codes
            - `artifact_path` and `probe_artifact_path` (relative paths)
            - `blocker_class`: equals the runtime status when not "implemented_enforced", otherwise "none"
            - `source_paths`, `verifier`, and `observed_at`
            - `blocker` present when `context["claim_status"] == "blocked"`
    """
    receipt = {
        "receipt_id": f"runtime-proof-{context['handle']}-{context['runtime_target']}",
        "claim": (
            "$"
            + context["handle"]
            + f" is reachable in the {_runtime_display_name(context['runtime_target'])} runtime."
        ),
        "claim_status": context["claim_status"],
        "runtime_target": context["runtime_target"],
        "runtime_status": context["runtime_status"],
        "evidence_type": "command",
        "command": context["command"],
        "exit_code": context["exit_code"],
        "probe_command": context["command"],
        "probe_exit_code": context["exit_code"],
        "probe_artifact_path": relative_probe_path,
        "blocker_class": context["runtime_status"] if context["runtime_status"] != "implemented_enforced" else "none",
        "artifact_path": relative_card_path,
        "source_paths": context["source_paths"],
        "verifier": "ask.skills.proof",
        "observed_at": context["created_at"],
    }
    if context["claim_status"] == "blocked":
        receipt["blocker"] = context["blocker"]
    return receipt


def _recovery_plan(context: dict[str, Any]) -> dict[str, Any]:
    """
    Constructs a recovery plan describing actions and expectations to remediate or confirm a skill's runtime reachability.
    
    Parameters:
        context (dict): Evidence context containing at least the keys:
            - "runtime_failure": dict with optional "recovery_guidance"
            - "claim_status": str, e.g. "blocked" or "pass"
            - "handle": skill handle string
            - "runtime_target": runtime target string (used for display)
            - "runtime_status": overall runtime status string
            - "command": validation command string to rerun
    
    Returns:
        dict: A recovery plan with the following keys:
            - "recovery_status": current runtime status
            - "reason": human-readable reason or recovery guidance
            - "next_commands": list of command steps (each with "command", "preconditions",
              "permission_profile", and "expected_outcome")
            - "preconditions": list of high-level preconditions for recovery
            - "permission_profile": required permissions for recovery actions
            - "expected_outcome": expected result after following the plan
    """
    if context["claim_status"] == "blocked":
        guidance = context["runtime_failure"].get("recovery_guidance")
        recovery_reason = (
            str(guidance)
            if guidance
            else f"Recovery guidance unavailable for blocked {context['runtime_target']} runtime."
        )
    else:
        recovery_reason = (
            "$"
            + context["handle"]
            + f" is reachable in the {_runtime_display_name(context['runtime_target'])} runtime."
        )
    runtime_diagnostics = (
        context.get("runtime_diagnostics")
        if isinstance(context.get("runtime_diagnostics"), dict)
        else {}
    )
    diagnostic_commands = runtime_diagnostics.get("recovery_commands")
    if isinstance(diagnostic_commands, list) and diagnostic_commands:
        next_commands = [
            {
                "command": str(item.get("command") or context["command"]),
                "preconditions": item.get("preconditions")
                if isinstance(item.get("preconditions"), list) and item.get("preconditions")
                else [
                    f"{_runtime_display_name(context['runtime_target'])} skill runtime can be inspected."
                ],
                "permission_profile": item.get("permission_profile")
                if isinstance(item.get("permission_profile"), dict)
                else {
                    "filesystem": "read workspace and user runtime skill links",
                    "network": "not required",
                },
                "expected_outcome": str(
                    item.get("expected_outcome")
                    or "Runtime proof can be rerun with fresher user-runtime evidence."
                ),
            }
            for item in diagnostic_commands
            if isinstance(item, dict)
        ]
    else:
        next_commands = [
            {
                "command": context["command"],
                "preconditions": [
                    f"{_runtime_display_name(context['runtime_target'])} skill runtime points at "
                    "the workspace command-handle projection."
                ],
                "permission_profile": {
                    "filesystem": "read workspace and user runtime skill links",
                    "network": "not required",
                },
                "expected_outcome": (
                    "RuntimeCard is updated with implemented_enforced proof or typed blocked_runtime evidence."
                ),
            }
        ]
    return {
        "recovery_status": context["runtime_status"],
        "reason": recovery_reason,
        "next_commands": next_commands,
        "preconditions": [
            "Run workspace and user skill sync if the runtime link or command handle is absent."
        ],
        "permission_profile": {
            "filesystem": "workspace evidence write and user runtime link read",
            "network": "not required",
        },
        "expected_outcome": "Operator can rerun the proof command and inspect schema-valid runtime evidence.",
    }


def _runtime_card_payload(
    context: dict[str, Any],
    *,
    proof: dict[str, Any],
    artifact_record: dict[str, Any],
    probe_record: dict[str, Any],
    receipt: dict[str, Any],
) -> dict[str, Any]:
    """
    Builds a RuntimeCard payload that aggregates runtime-proof metadata, artifacts, verifier results and a recovery plan for a skill handle.
    
    Parameters:
        context (dict): Context produced by _runtime_evidence_context. Required keys used:
            - 'handle', 'runtime_target', 'runtime_status', 'created_at',
              'repo_root', 'actor_type', 'claim_status', 'blocker', 'failed_check_id'.
        proof (dict): The original proof object; used for verifier status, required gates and gate details.
        artifact_record (dict): Artifact record describing the generated runtime card.
        probe_record (dict): Artifact record for the probe/verifier output.
        receipt (dict): Evidence receipt associated with the runtime proof.
    
    Returns:
        dict: A RuntimeCard payload (schema_version 1) containing:
            - card and session identifiers and timestamps
            - runtime and workspace metadata
            - included artifacts and evidence receipts
            - verifier_results (including failed_check_id when blocked)
            - permission profile, mutation scope, visibility, limitations
            - a recovery_plan produced from the provided context
    """
    runtime_session = {
        "session_id": f"runtime-proof-{context['handle']}-{context['runtime_target']}",
        "runtime_target": context["runtime_target"],
        "runtime_status": context["runtime_status"],
        "created_at": context["created_at"],
        "workspace_root": WORKSPACE_ROOT_MARKER,
        "actor_type": context["actor_type"],
        "visibility_status": "user_observable",
    }
    if context["claim_status"] == "blocked":
        runtime_session["unavailable_reason"] = context["blocker"]
    return {
        "schema_version": 1,
        "card_id": f"runtime-card-{context['handle']}-{context['runtime_target']}",
        "created_at": context["created_at"],
        "runtime_target": context["runtime_target"],
        "runtime_status": context["runtime_status"],
        "skill_handle": context["handle"],
        "command_handle": "$" + context["handle"],
        "runtime_session": runtime_session,
        "thread_runs": [],
        "turn_events": [],
        "artifacts": [artifact_record, probe_record],
        "evidence_receipts": [receipt],
        "verifier_results": [
            {
                "verifier": "ask.skills.proof",
                "status": proof.get("status"),
                "runtime_target": context["runtime_target"],
                "required_gates": proof.get("gate_policy", {}).get("required", []),
                "gates": proof.get("gates", {}),
                "failed_check_id": context["failed_check_id"] if context["claim_status"] == "blocked" else None,
                "runtime_diagnostics": _redact_runtime_paths(
                    context["runtime_diagnostics"],
                    context["repo_root"],
                ),
            }
        ],
        "permission_profile": {
            "filesystem": "workspace evidence write",
            "network": "not required",
        },
        "workspace_root": WORKSPACE_ROOT_MARKER,
        "actor_type": context["actor_type"],
        "mutation_scope": "evidence_write",
        "visibility_status": "user_observable",
        "limitations": [
            {
                "class": "manual_session_gate",
                "message": (
                    "Runtime reachability proves command-handle wiring; it does not execute an interactive "
                    "Codex session."
                ),
            }
        ],
        "runtime_diagnostics": _redact_runtime_paths(
            context["runtime_diagnostics"],
            context["repo_root"],
        ),
        "recovery_plan": _recovery_plan(context),
    }


def emit_command_handle_runtime_evidence(
    *,
    repo_root: Path,
    proof: dict[str, Any],
    actor_type: str = "agent",
) -> dict[str, Any]:
    """
    Emit runtime-proof evidence files for an explicit 'codex' or 'agents' runtime target.
    
    Parameters:
    	repo_root (Path): Repository root used to compute evidence output paths.
    	proof (dict[str, Any]): Command-handle proof payload that must include a `runtime_target` entry.
    	actor_type (str): Actor classification to include in generated evidence (default: "agent").
    
    Returns:
    	dict[str, Any]: Result summary containing:
    		- "status": runtime status string (e.g. "implemented_enforced", "blocked_runtime", "stale_or_drifted").
    		- "evidence_dir": repository-relative evidence directory path.
    		- "runtime_card_path": repository-relative path to the written runtime card JSON.
    		- "evidence_receipt_path": repository-relative path to the written receipt JSON.
    		- "artifact_record_path": repository-relative path to the written artifact record JSON.
    		- "probe_artifact_path": repository-relative path to the written probe JSON.
    		- "validation_command": a CLI string that can be used to validate the emitted runtime card.
    	
    	If the proof's `runtime_target` is not "codex" or "agents", returns:
    		{"status": "skipped", "reason": "runtime evidence is only emitted for explicit codex or agents targets"}.
    """
    runtime_target = str(proof.get("runtime_target") or "")
    if runtime_target not in EVIDENCE_RUNTIME_TARGETS:
        return {
            "status": "skipped",
            "reason": "runtime evidence is only emitted for explicit codex or agents targets",
        }

    context = _runtime_evidence_context(repo_root=repo_root, proof=proof, actor_type=actor_type)
    relative_card_path = _repo_relative(repo_root, context["card_path"])
    relative_receipt_path = _repo_relative(repo_root, context["receipt_path"])
    relative_artifact_path = _repo_relative(repo_root, context["artifact_path"])
    relative_probe_path = _repo_relative(repo_root, context["probe_path"])

    probe = _probe_payload(context, proof)
    receipt = _receipt_payload(context, relative_card_path, relative_probe_path)
    card_record = _artifact_record(
        context,
        artifact_id=f"runtime-card-{context['handle']}-{context['runtime_target']}",
        artifact_type="runtime_card",
        path=relative_card_path,
        consumer_contract="RuntimeCard v1 consumed by validate_runtime_cards.py and governed closeout.",
    )
    probe_record = _artifact_record(
        context,
        artifact_id=f"runtime-probe-{context['handle']}-{context['runtime_target']}",
        artifact_type="verifier_output",
        path=relative_probe_path,
        consumer_contract="Probe JSON records the raw command-handle proof used by the RuntimeCard.",
    )
    card = _runtime_card_payload(
        context,
        proof=proof,
        artifact_record=card_record,
        probe_record=probe_record,
        receipt=receipt,
    )

    _write_json(context["probe_path"], probe)
    _write_json(context["receipt_path"], receipt)
    _write_json(context["artifact_path"], card_record)
    _write_json(context["card_path"], card)

    return {
        "status": context["runtime_status"],
        "evidence_dir": _repo_relative(repo_root, context["evidence_dir"]),
        "runtime_card_path": relative_card_path,
        "evidence_receipt_path": relative_receipt_path,
        "artifact_record_path": relative_artifact_path,
        "probe_artifact_path": relative_probe_path,
        "validation_command": (
            "python3 Infrastructure/scripts/validation-and-linting/validate_runtime_cards.py "
            f"{relative_card_path} --require-shared-workspace --workspace-root {WORKSPACE_ROOT_MARKER} --json"
        ),
    }


def build_command_handle_proof(
    *,
    repo_root: Path,
    handle: str,
    runtime_target: object,
    resolve_skill_handle_fn: ResolveSkillHandle,
    check_command_handles_fn: CheckCommandHandles,
    home_path: Path,
) -> dict[str, Any]:
    """
    Build a runtime reachability proof for a generated skill command handle.
    
    Parameters:
    	repo_root (Path): Repository root used to resolve workspace paths.
    	handle (str): Skill handle identifier (may include a leading `$`).
    	runtime_target (object): Requested runtime target; will be normalized to a lowercase string (e.g. "any", "codex", "agents").
    	resolve_skill_handle_fn (callable): Callable used to resolve the handle to repository resolution metadata.
    	check_command_handles_fn (callable): Callable used to validate generated command handle(s) in the workspace.
    	home_path (Path): User home path used to inspect user runtime projections under `.codex` and `.agents`.
    
    Returns:
    	proof (dict[str, Any]): A proof payload (schema_version "command-handle-proof.v2") describing gate results, validation commands, resolution and workspace/user runtime state, available runtimes, and, on failure, a `runtime_failure` entry with recovery guidance. If required runtime gates are satisfied, the payload may include a `live_runtime_invocation` hint for manual verification.
    """
    runtime_target = normalize_runtime_target(runtime_target)
    normalized = handle.strip().lstrip("$") or handle
    if runtime_target not in SUPPORTED_RUNTIME_TARGETS:
        runtime_failure = invalid_runtime_target_failure(normalized, runtime_target)
        return {
            "schema_version": "command-handle-proof.v2",
            "handle": normalized,
            "runtime_target": runtime_target,
            "status": "fail",
            "validation_commands": runtime_failure["validation_commands"],
            "gates": {
                "runtime_target": False,
            },
            "gate_policy": {
                "required": ["runtime_target"],
                "runtime_target": runtime_target,
                "required_semantics": runtime_failure["recovery_guidance"],
                "supporting_runtime_diagnostics": [],
            },
            "available_runtimes": [],
            "runtime_satisfied_by": None,
            "resolution": None,
            "command_handle_check": None,
            "workspace_runtime": None,
            "user_runtime_links": None,
            "user_runtime_command_handles": None,
            "runtime_failure": runtime_failure,
        }
    resolution = resolve_skill_handle_fn(handle, repo_root_path=repo_root)
    normalized = str(resolution.get("handle", normalized))
    handle_check = check_command_handles_fn(repo_root_path=repo_root)
    workspace_handle = repo_root / str(resolution.get("command_handle_path", ""))
    user_codex_handle = home_path / ".codex" / "skills" / str(normalized) / "SKILL.md"
    user_agents_handle = home_path / ".agents" / "skills" / str(normalized) / "SKILL.md"
    codex_skills = home_path / ".codex" / "skills"
    agents_skills = home_path / ".agents" / "skills"
    expected_runtime = repo_root / ".agents" / "skills"

    handle_violations = [
        violation
        for violation in handle_check.get("violations", [])
        if violation.get("handle") == normalized
    ]
    handle_check_ok = handle_check.get("status") == "pass" or not handle_violations

    def link_payload(path: Path) -> dict[str, object]:
        payload: dict[str, object] = {
            "path": str(path),
            "exists": path.exists(),
            "is_symlink": path.is_symlink(),
        }
        if path.is_symlink():
            payload["target"] = str(path.resolve())
            payload["points_to_workspace_runtime"] = path.resolve() == expected_runtime.resolve()
        else:
            payload["target"] = None
            payload["points_to_workspace_runtime"] = False
        return payload

    def handle_points_to_workspace(handle_path: Path) -> bool:
        return handle_path.exists() and _path_is_under(handle_path, expected_runtime)

    codex_link = link_payload(codex_skills)
    agents_link = link_payload(agents_skills)
    codex_handle_points = handle_points_to_workspace(user_codex_handle)
    agents_handle_points = handle_points_to_workspace(user_agents_handle)
    gates = {
        "resolver": resolution.get("status") == "ok",
        "generated_command_handle_check": handle_check_ok,
        "workspace_command_handle_exists": workspace_handle.is_file(),
        "codex_user_link": bool(codex_link["points_to_workspace_runtime"]),
        "agents_user_link": bool(agents_link["points_to_workspace_runtime"]),
        "codex_user_command_handle_exists": user_codex_handle.is_file(),
        "agents_user_command_handle_exists": user_agents_handle.is_file(),
        "codex_user_command_handle_points_to_workspace": codex_handle_points,
        "agents_user_command_handle_points_to_workspace": agents_handle_points,
    }
    core_gates = (
        gates["resolver"],
        gates["generated_command_handle_check"],
        gates["workspace_command_handle_exists"],
    )
    codex_runtime_ready = gates["codex_user_command_handle_points_to_workspace"]
    agents_runtime_ready = gates["agents_user_command_handle_points_to_workspace"]
    user_runtime_ready = codex_runtime_ready or agents_runtime_ready
    gates["codex_user_runtime_ready"] = codex_runtime_ready
    gates["agents_user_runtime_ready"] = agents_runtime_ready
    gates["user_runtime_ready"] = user_runtime_ready
    required_runtime_gate = {
        "any": "user_runtime_ready",
        "codex": "codex_user_runtime_ready",
        "agents": "agents_user_runtime_ready",
    }[runtime_target]
    required_runtime_ready = bool(gates[required_runtime_gate])
    failed_check_id = (
        None
        if all(core_gates) and required_runtime_ready
        else next(
            (
                check_id
                for check_id in (
                    "resolver",
                    "generated_command_handle_check",
                    "workspace_command_handle_exists",
                    required_runtime_gate,
                )
                if not gates.get(check_id)
            ),
            "runtime_reachability",
        )
    )
    validation_args = [str(normalized)]
    if runtime_target != "any":
        validation_args.extend(["--runtime-target", runtime_target])
    runtime_diagnostics = {
        "schema_version": "command-handle-runtime-diagnostics.v1",
        "selected_runtime_target": runtime_target,
        "failed_gate": failed_check_id,
        "expected_workspace_runtime": str(expected_runtime),
        "runtime_modes": {
            "codex_user_runtime": _runtime_mode(
                codex_link,
                handle_points_to_workspace=codex_handle_points,
            ),
            "agents_user_runtime": _runtime_mode(
                agents_link,
                handle_points_to_workspace=agents_handle_points,
            ),
        },
        "missing_command_handles": [
            {
                "runtime": runtime_name,
                "path": str(handle_path),
                "expected_under": str(expected_runtime),
            }
            for runtime_name, handle_path, exists, points_to_workspace in (
                (
                    "codex_user_runtime",
                    user_codex_handle,
                    gates["codex_user_command_handle_exists"],
                    gates["codex_user_command_handle_points_to_workspace"],
                ),
                (
                    "agents_user_runtime",
                    user_agents_handle,
                    gates["agents_user_command_handle_exists"],
                    gates["agents_user_command_handle_points_to_workspace"],
                ),
            )
            if not exists or not points_to_workspace
        ],
        "recovery_risk": (
            "User-scope sync mutates home-directory runtime links; preview with --dry-run before applying."
        ),
        "recovery_commands": [
            {
                "kind": "preview_user_runtime_sync",
                "command": skills_validation_command(
                    "sync",
                    "--scope",
                    "user",
                    "--projection",
                    "rooted",
                    "--dry-run",
                ),
                "preconditions": ["Workspace rooted projection validates cleanly."],
                "permission_profile": {
                    "filesystem": "read workspace and user runtime links",
                    "network": "not required",
                },
                "expected_outcome": (
                    "Reports whether ~/.codex/skills or ~/.agents/skills would be relinked before mutation."
                ),
            },
            {
                "kind": "refresh_workspace_projection",
                "command": skills_validation_command("sync", "--scope", "workspace", "--projection", "rooted"),
                "preconditions": ["Canonical skill sources are ready to project."],
                "permission_profile": {
                    "filesystem": "write workspace runtime projection",
                    "network": "not required",
                },
                "expected_outcome": "Refreshes .agents/skills command handles from canonical sources.",
            },
            {
                "kind": "apply_user_runtime_sync",
                "command": skills_validation_command("sync", "--scope", "user", "--projection", "rooted"),
                "preconditions": ["Dry-run output is acceptable to the operator."],
                "permission_profile": {
                    "filesystem": "write home-directory runtime links",
                    "network": "not required",
                },
                "expected_outcome": "Makes user-level Codex and Agents skill runtimes point at the workspace projection.",
            },
            {
                "kind": "rerun_runtime_proof",
                "command": skills_validation_command("proof", *validation_args),
                "preconditions": ["User runtime link or handle bridge now points at the workspace projection."],
                "permission_profile": {
                    "filesystem": "read workspace and user runtime links; write runtime-proof evidence",
                    "network": "not required",
                },
                "expected_outcome": "Updates runtime evidence with pass or a narrower blocked_runtime reason.",
            },
        ],
    }
    proof = {
        "schema_version": "command-handle-proof.v2",
        "handle": normalized,
        "runtime_target": runtime_target,
        "status": "pass" if all(core_gates) and required_runtime_ready else "fail",
        "validation_commands": [
            skills_validation_command("proof", *validation_args),
        ],
        "gates": gates,
        "gate_policy": {
            "required": [
                "resolver",
                "generated_command_handle_check",
                "workspace_command_handle_exists",
                required_runtime_gate,
            ],
            "runtime_target": runtime_target,
            "required_semantics": (
                "user_runtime_ready accepts either supported user runtime link."
                if runtime_target == "any"
                else f"{required_runtime_gate} must be true for runtime_target={runtime_target}."
            ),
            "supporting_runtime_diagnostics": [
                "codex_user_link",
                "codex_user_command_handle_exists",
                "codex_user_command_handle_points_to_workspace",
                "codex_user_runtime_ready",
                "agents_user_link",
                "agents_user_command_handle_exists",
                "agents_user_command_handle_points_to_workspace",
                "agents_user_runtime_ready",
            ],
        },
        "available_runtimes": [
            runtime_name
            for runtime_name, ready in (
                ("codex_user_runtime", codex_runtime_ready),
                ("agents_user_runtime", agents_runtime_ready),
            )
            if ready
        ],
        "runtime_satisfied_by": (
            "codex_user_runtime"
            if runtime_target in {"any", "codex"} and codex_runtime_ready
            else "agents_user_runtime"
            if runtime_target in {"any", "agents"} and agents_runtime_ready
            else None
        ),
        "resolution": resolution,
        "command_handle_check": {
            key: value
            for key, value in handle_check.items()
            if key != "violations" or value
        },
        "workspace_runtime": {
            "path": str(expected_runtime),
            "command_handle_path": str(workspace_handle),
            "command_handle_exists": workspace_handle.is_file(),
        },
        "user_runtime_links": {
            "codex_skills": codex_link,
            "agents_skills": agents_link,
        },
        "user_runtime_command_handles": {
            "codex_handle": str(user_codex_handle),
            "codex_handle_exists": user_codex_handle.is_file(),
            "codex_handle_points_to_workspace": codex_handle_points,
            "agents_handle": str(user_agents_handle),
            "agents_handle_exists": user_agents_handle.is_file(),
            "agents_handle_points_to_workspace": agents_handle_points,
        },
        "runtime_diagnostics": runtime_diagnostics,
    }
    if proof["status"] != "pass":
        recovery_guidance = (
            "Preview with ./bin/ask skills sync --scope user --projection rooted --dry-run, "
            "then run workspace/user sync only if the user-runtime relink plan is acceptable."
        )
        proof["runtime_failure"] = runtime_failure_payload(
            command="skills proof",
            error_code="ERR_VALIDATION",
            failed_check_id=str(failed_check_id),
            path=f"gates.{failed_check_id}",
            message=f"Command handle proof failed for '{normalized}'.",
            recovery_guidance=recovery_guidance,
            validation_commands=proof["validation_commands"],
        )
    if required_runtime_ready:
        runtime = proof["runtime_satisfied_by"]
        operator_action = (
            "Open or reload a Codex session and verify the handle appears in the picker or can be invoked as a $ handle."
            if runtime == "codex_user_runtime"
            else "Open or reload the Agents runtime and verify the handle is available there."
        )
        proof["live_runtime_invocation"] = {
            "status": "manual_session_gate",
            "runtime_satisfied_by": runtime,
            "operator_action": operator_action,
        }
    return proof
