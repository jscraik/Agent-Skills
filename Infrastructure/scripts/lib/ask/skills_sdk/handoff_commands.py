from __future__ import annotations

from pathlib import Path

from ask.commands import skills as skills_commands
from ask.envelope import CallResult, ErrorObject
from ask.skills_sdk.handoff_materialization import (
    HandoffMaterializationRequest,
    materialize_handoff_bundle,
)
from ask.skills_sdk.handoff_capture import HandoffCaptureRequest, capture_handoff_lane


def materialize_handoff_command(
    repo_root: Path,
    *,
    request: HandoffMaterializationRequest,
) -> CallResult:
    """Expose the candidate-bound materializer without extending skills_impl."""
    result = CallResult()
    result.metadata["command"] = "sdk eval handoff-materialize"
    target_info, _audit_target = skills_commands.resolve_doctor_target(repo_root, request.skill.strip())
    source_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_value)) if source_value else None
    if source_path is not None and not source_path.is_absolute():
        source_path = repo_root / source_path
    if source_path is None:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Skills SDK handoff materialization is missing a canonical SKILL.md source for '{request.skill}'.",
        ))
        return result

    receipt = materialize_handoff_bundle(repo_root, source_path=source_path, request=request)
    payload = {
        "schema_version": "skills-sdk-eval-handoff-materialize.v0",
        "status": receipt["status"],
        "ready_for_tessl_dry_run": receipt["ready_for_tessl_dry_run"],
        "skill": request.skill,
        "receipt": receipt,
        "mutation_performed": receipt["mutation_performed"],
        "validation_commands": [_validation_command(request)],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_eval_handoff_materialize"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message=payload["agent_summary"]))
    return result


def capture_handoff_command(
    repo_root: Path,
    *,
    request: HandoffCaptureRequest,
) -> CallResult:
    """Run one canonical pre-Tessl command and persist its receipt."""
    result = CallResult()
    result.metadata["command"] = "sdk eval handoff-capture"
    target_info, _audit_target = skills_commands.resolve_doctor_target(repo_root, request.skill.strip())
    source_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_value)) if source_value else None
    if source_path is not None and not source_path.is_absolute():
        source_path = repo_root / source_path
    if source_path is None:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Skills SDK handoff capture is missing a canonical SKILL.md source for '{request.skill}'.",
        ))
        return result

    receipt = capture_handoff_lane(repo_root, source_path=source_path, request=request)
    payload = {
        "schema_version": "skills-sdk-eval-handoff-capture.v1",
        "status": receipt["status"],
        "skill": request.skill,
        "lane": request.lane_id,
        "receipt": receipt,
        "mutation_performed": receipt["mutation_performed"],
        "validation_commands": receipt["commands"],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_eval_handoff_capture"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message=payload["agent_summary"]))
    return result


import shlex


def _validation_command(request: HandoffMaterializationRequest) -> str:
    operation = "--execute" if request.operation == "execute" else "--preview"
    return shlex.join([
        "./bin/ask", "sdk", "eval", "handoff-materialize",
        "--skill", request.skill,
        "--evidence-root", str(request.evidence_root),
        operation,
    ])
