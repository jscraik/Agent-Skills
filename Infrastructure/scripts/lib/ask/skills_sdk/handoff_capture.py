from __future__ import annotations

import json
import shlex
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Literal

from ask.skills_sdk.handoff_readiness import (
    PRE_TESSL_DRY_RUN_LANE_IDS,
    _repo_relative,
    build_candidate_identity,
)


HANDOFF_CAPTURE_SCHEMA_VERSION = "skills-sdk.eval-handoff-lane.v1"
_EVIDENCE_ROOT = (".harness", "evidence", "handoff")
_RunCommand = Callable[..., subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class HandoffCaptureRequest:
    """Inputs for exactly one pre-Tessl command and its durable receipt."""

    skill: str
    lane_id: str
    receipt_path: Path
    operation: Literal["preview", "execute"]
    cases: tuple[str, ...] = ()
    timeout_seconds: int = 180
    workspace: str = "jscraik"


def capture_handoff_lane(
    repo_root: Path,
    *,
    source_path: Path,
    request: HandoffCaptureRequest,
    run_command: _RunCommand = subprocess.run,
) -> dict[str, Any]:
    """Run one canonical pre-Tessl lane and write its candidate-bound receipt."""
    receipt_path, blockers = _validate_request(repo_root, request)
    candidate = build_candidate_identity(repo_root, source_path)
    command_parts = _command_parts(request)
    receipt = _receipt(candidate, request, command_parts, command_results=[], blockers=blockers)
    if blockers or request.operation == "preview":
        return receipt

    command_results = _run_commands(repo_root, command_parts, run_command)
    receipt = _receipt(candidate, request, command_parts, command_results=command_results, blockers=[])
    if any(item["status"] != "pass" for item in command_results):
        receipt["status"] = "blocked"
        receipt["blockers"] = ["captured command did not pass"]
        receipt["agent_summary"] = f"{request.lane_id} capture is blocked; inspect command_results before retrying."

    if receipt_path is None:
        return receipt
    receipt["mutation_performed"] = True
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def _validate_request(repo_root: Path, request: HandoffCaptureRequest) -> tuple[Path | None, list[str]]:
    blockers: list[str] = []
    if request.lane_id not in PRE_TESSL_DRY_RUN_LANE_IDS:
        blockers.append(f"unsupported pre-Tessl lane: {request.lane_id}")
    if request.timeout_seconds < 1:
        blockers.append("timeout_seconds must be >= 1")
    if request.lane_id in {"oss-local", "oss-cloud"}:
        if not request.cases:
            blockers.append(f"{request.lane_id} capture requires explicit one- or two-case shards")
        elif len(request.cases) > 2:
            blockers.append(f"{request.lane_id} capture supports at most two cases per shard")
        elif len(set(request.cases)) != len(request.cases):
            blockers.append(f"{request.lane_id} capture cases must be unique")
    if request.lane_id == "tessl-local-proof" and request.workspace != "jscraik":
        blockers.append("tessl-local-proof workspace must be jscraik")
    receipt_path = request.receipt_path if request.receipt_path.is_absolute() else repo_root / request.receipt_path
    evidence_root = repo_root.joinpath(*_EVIDENCE_ROOT).resolve()
    try:
        receipt_path.resolve(strict=False).relative_to(evidence_root)
    except ValueError:
        blockers.append("receipt path must be contained by .harness/evidence/handoff")
        return None, blockers
    if receipt_path.exists() or receipt_path.is_symlink():
        blockers.append(f"receipt path must be a new regular file: {_repo_relative(repo_root, receipt_path)}")
    return receipt_path, blockers


def _command_parts(request: HandoffCaptureRequest) -> list[list[str]]:
    target = request.skill
    previews = {
        "security_risk_modes": ["sdk", "security", "risk-modes", target, "--preview"],
        "scenario_quality": ["sdk", "eval", "scenario-quality", target, "--preview"],
        "scorer_quality": ["sdk", "eval", "scorer-quality", target, "--preview"],
        "scorer_calibration": ["sdk", "eval", "scorer-calibration", target, "--preview"],
        "tessl-local-proof": [
            "sdk", "eval", "tessl-local-proof", "--skill", target,
            "--workspace", request.workspace, "--execute", "--timeout-seconds", str(request.timeout_seconds),
        ],
    }
    if request.lane_id == "mechanical_validation":
        return [
            ["skills", "audit", target, "--level", "strict"],
            ["skills", "package", "verify", target, "--strict"],
        ]
    if request.lane_id in previews:
        return [previews[request.lane_id]]
    mode = "release" if request.lane_id in {"oss-local", "oss-cloud"} else "smoke"
    command = ["sdk", "eval", "run", target, "--runner", "internal", "--mode", mode]
    if request.lane_id in {"deterministic_local_gates", "oss-local", "oss-cloud"}:
        profile = "oss-local" if request.lane_id == "deterministic_local_gates" else request.lane_id
        command.extend(["--codex-profile", profile])
    command.extend(["--timeout-seconds", str(request.timeout_seconds)])
    for case_id in request.cases:
        command.extend(["--case", case_id])
    return [command]


def _run_commands(
    repo_root: Path,
    command_parts: list[list[str]],
    run_command: _RunCommand,
    timeout_seconds: int,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for arguments in command_parts:
        try:
            process = run_command(
                [str(repo_root / "bin" / "ask"), *arguments, "--json", "--robot"],
                cwd=repo_root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            results.append({
                "command": shlex.join(["./bin/ask", *arguments, "--json", "--robot"]),
                "exit_code": None,
                "status": "blocked",
                "result": None,
                "diagnostic": f"child command exceeded {timeout_seconds}s",
            })
            break
        results.append(_command_result(arguments, process))
    return results


def _command_result(arguments: list[str], process: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    logical_command = shlex.join(["./bin/ask", *arguments, "--json", "--robot"])
    try:
        output = json.loads(process.stdout)
    except json.JSONDecodeError:
        return {
            "command": logical_command,
            "exit_code": process.returncode,
            "status": "blocked",
            "result": None,
            "diagnostic": "child command did not emit a JSON envelope",
        }
    passed = process.returncode == 0 and isinstance(output, dict) and output.get("status") == "success"
    return {
        "command": logical_command,
        "exit_code": process.returncode,
        "status": "pass" if passed else "blocked",
        "data": _minimal_child_data(arguments, output),
    }


def _minimal_child_data(arguments: list[str], output: dict[str, Any]) -> dict[str, Any] | None:
    data = output.get("data")
    if not isinstance(data, dict):
        return None
    if arguments[:3] == ["sdk", "eval", "run"]:
        return _eval_run_data(data)
    if arguments[:3] == ["sdk", "eval", "tessl-local-proof"]:
        return _tessl_local_proof_data(data)
    return None


def _eval_run_data(data: dict[str, Any]) -> dict[str, Any] | None:
    value = data.get("skills_sdk_eval_run")
    receipt = value.get("receipt") if isinstance(value, dict) else None
    if not isinstance(receipt, dict):
        return None
    values = receipt.get("cases")
    cases = [
        {"case_id": item.get("case_id"), "status": item.get("status")}
        for item in values
        if isinstance(item, dict)
        and isinstance(item.get("case_id"), str)
        and isinstance(item.get("status"), str)
    ] if isinstance(values, list) else []
    return {"skills_sdk_eval_run": {"receipt": {
        "status": receipt.get("status"),
        "profile": receipt.get("profile"),
        "codex_profile": receipt.get("codex_profile"),
        "codex_exec_invoked": receipt.get("codex_exec_invoked"),
        "cases": cases,
    }}}


def _tessl_local_proof_data(data: dict[str, Any]) -> dict[str, Any] | None:
    value = data.get("skills_sdk_eval_tessl_local_proof")
    receipt = value.get("receipt") if isinstance(value, dict) else None
    if not isinstance(receipt, dict):
        return None
    return {"skills_sdk_eval_tessl_local_proof": {"receipt": {
        "schema_version": receipt.get("schema_version"),
        "status": receipt.get("status"),
        "execute": receipt.get("execute"),
    }}}


def _receipt(
    candidate: dict[str, str],
    request: HandoffCaptureRequest,
    command_parts: list[list[str]],
    *,
    command_results: list[dict[str, Any]],
    blockers: list[str],
) -> dict[str, Any]:
    status = "blocked" if blockers else "preview" if request.operation == "preview" else "pass"
    receipt: dict[str, Any] = {
        "schema_version": HANDOFF_CAPTURE_SCHEMA_VERSION,
        "status": status,
        "lane": request.lane_id,
        "candidate": candidate,
        "issued_at": datetime.now(UTC).isoformat(),
        "commands": [shlex.join(["./bin/ask", *parts, "--json", "--robot"]) for parts in command_parts],
        "command_results": command_results,
        "blockers": blockers,
        "mutation_performed": False,
        "agent_summary": (
            f"{request.lane_id} capture is ready to execute."
            if status == "preview"
            else f"{request.lane_id} capture is blocked: {blockers[0]}"
            if blockers
            else f"{request.lane_id} capture passed."
        ),
    }
    data = _single_command_data(command_results)
    if data is not None:
        receipt["data"] = data
    facts = _shared_eval_facts(command_results)
    if facts:
        receipt.update(facts)
    return receipt


def _single_command_data(command_results: list[dict[str, Any]]) -> dict[str, Any] | None:
    if len(command_results) != 1:
        return None
    data = command_results[0].get("data")
    return data if isinstance(data, dict) else None


def _shared_eval_facts(command_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Project only profile facts shared by every captured eval shard."""
    receipts: list[dict[str, Any]] = []
    for item in command_results:
        data = item.get("data")
        value = data.get("skills_sdk_eval_run") if isinstance(data, dict) else None
        receipt = value.get("receipt") if isinstance(value, dict) else None
        if isinstance(receipt, dict):
            receipts.append(receipt)
    if not receipts:
        return {}
    profiles = {receipt.get("codex_profile") for receipt in receipts}
    invoked = all(receipt.get("codex_exec_invoked") is True for receipt in receipts)
    facts: dict[str, Any] = {"codex_exec_invoked": invoked}
    if len(profiles) == 1 and isinstance(next(iter(profiles)), str):
        facts["codex_profile"] = next(iter(profiles))
    return facts
