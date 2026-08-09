from __future__ import annotations

import hashlib
import json
import os
import shlex
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from ask.skills_sdk.handoff_readiness import (
    HANDOFF_READINESS_MAX_AGE,
    HANDOFF_READINESS_INPUT_SCHEMA_VERSION,
    PRE_TESSL_DRY_RUN_LANE_IDS,
    _lane_profile_semantics,
    _nested_receipt_payloads,
    _receipt_codex_exec_invoked,
    _receipt_profile,
    _receipt_status,
    _repo_relative,
    _skill_dir,
    _skill_md,
    build_candidate_identity,
    build_tessl_dry_run_admission,
)
from ask.skills_sdk.handoff_capture import HANDOFF_CAPTURE_SCHEMA_VERSION


HANDOFF_MATERIALIZATION_SCHEMA_VERSION = "skills-sdk.eval-handoff-materialization.v1"
_EVIDENCE_ROOT = (".harness", "evidence", "handoff")


@dataclass(frozen=True)
class HandoffMaterializationRequest:
    """Operator inputs for one candidate-bound handoff materialization."""

    skill: str
    evidence_root: Path
    lane_receipts: tuple[str, ...]
    operation: Literal["preview", "execute"]


def materialize_handoff_bundle(
    repo_root: Path,
    *,
    source_path: Path,
    request: HandoffMaterializationRequest,
) -> dict[str, Any]:
    """Stage current pre-Tessl receipts into one candidate-bound handoff bundle."""
    plan, blockers = _materialization_plan(repo_root, source_path, request)
    if blockers or request.operation == "preview":
        return _receipt(plan, blockers, operation=request.operation)
    return _write_bundle(repo_root, plan)


def record_tessl_dry_run(
    repo_root: Path,
    *,
    readiness_path: Path,
    tessl_eval: dict[str, Any],
) -> str:
    """Bind one successful private dry-run to its materialized handoff bundle."""
    path, error = _validate_readiness_path(repo_root, readiness_path)
    if error or path is None:
        raise ValueError(error or "handoff readiness path is invalid")
    try:
        readiness = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"handoff readiness manifest is unreadable: {exc}") from exc
    candidate = readiness.get("candidate") if isinstance(readiness, dict) else None
    lanes = readiness.get("lanes") if isinstance(readiness, dict) else None
    if not isinstance(candidate, dict) or not isinstance(lanes, list):
        raise ValueError("handoff readiness manifest must contain candidate and lanes")
    if not _dry_run_result_is_pass(tessl_eval):
        raise ValueError("only a successful private Tessl dry-run can be recorded")
    lane = next((item for item in lanes if isinstance(item, dict) and item.get("id") == "tessl-live-dry-run"), None)
    if not isinstance(lane, dict):
        raise ValueError("handoff readiness manifest is missing tessl-live-dry-run lane")
    receipt_path = path.parent / "tessl-live-dry-run.json"
    if lane.get("status") == "pass":
        raw_receipt_path = lane.get("receipt_path")
        existing_path = repo_root / raw_receipt_path if isinstance(raw_receipt_path, str) else None
        if existing_path is not None and existing_path.is_file() and not existing_path.is_symlink():
            return _repo_relative(repo_root, existing_path)
        raise ValueError("completed Tessl dry-run lane is missing its regular receipt")
    if receipt_path.exists() or receipt_path.is_symlink():
        raise ValueError("Tessl dry-run receipt already exists; materialize a fresh handoff bundle before retrying")
    receipt = {
        "schema_version": "skills-sdk.tessl-live-dry-run.v1",
        "status": "pass",
        "lane": "tessl-live-dry-run",
        "candidate": candidate,
        "issued_at": datetime.now(UTC).isoformat(),
        "tessl_eval": _minimal_dry_run_evidence(tessl_eval),
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lane["status"] = "pass"
    lane["receipt_path"] = _repo_relative(repo_root, receipt_path)
    lane["blocker"] = None
    temporary_path = path.with_name(f".{path.name}.tmp")
    try:
        temporary_path.write_text(json.dumps(readiness, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(temporary_path, path)
    except OSError:
        receipt_path.unlink(missing_ok=True)
        temporary_path.unlink(missing_ok=True)
        raise
    return _repo_relative(repo_root, receipt_path)


def _materialization_plan(
    repo_root: Path,
    source_path: Path,
    request: HandoffMaterializationRequest,
) -> tuple[dict[str, Any], list[str]]:
    receipts, receipt_errors = _assignment_map(request.lane_receipts, "lane receipt")
    target_root, root_error = _validate_evidence_root(repo_root, request.evidence_root)
    candidate = build_candidate_identity(repo_root, source_path)
    lanes, envelopes, lane_errors = _lanes_and_envelopes(
        repo_root, source_path, target_root, candidate, receipts,
    )
    blockers = receipt_errors + lane_errors
    if root_error:
        blockers.append(root_error)
    if target_root is not None and target_root.exists():
        blockers.append(f"evidence root already exists: {_repo_relative(repo_root, target_root)}")
    return {
        "repo_root": repo_root,
        "query": request.skill,
        "source_path": source_path,
        "candidate": candidate,
        "target_root": target_root,
        "lanes": lanes,
        "envelopes": envelopes,
    }, blockers


def _assignment_map(values: tuple[str, ...], label: str) -> tuple[dict[str, list[str]], list[str]]:
    assignments: dict[str, list[str]] = {}
    errors: list[str] = []
    for value in values:
        lane_id, separator, assigned = value.partition("=")
        lane_id, assigned = lane_id.strip(), assigned.strip()
        if not separator or not lane_id or not assigned:
            errors.append(f"{label} must use lane-id=value: {value}")
        else:
            assignments.setdefault(lane_id, []).append(assigned)
    unexpected = sorted(set(assignments) - set(PRE_TESSL_DRY_RUN_LANE_IDS))
    missing = [lane_id for lane_id in PRE_TESSL_DRY_RUN_LANE_IDS if lane_id not in assignments]
    errors.extend(f"unsupported {label} lane: {lane_id}" for lane_id in unexpected)
    errors.extend(f"missing {label} for lane: {lane_id}" for lane_id in missing)
    for lane_id, paths in assignments.items():
        if lane_id not in {"oss-local", "oss-cloud"} and len(paths) != 1:
            errors.append(f"{label} lane accepts one receipt: {lane_id}")
    return assignments, errors


def _validate_evidence_root(repo_root: Path, requested_root: Path) -> tuple[Path | None, str | None]:
    target_root = requested_root if requested_root.is_absolute() else repo_root / requested_root
    evidence_root = (repo_root.joinpath(*_EVIDENCE_ROOT)).resolve()
    target_root = target_root.resolve(strict=False)
    try:
        target_root.relative_to(evidence_root)
    except ValueError:
        return None, "evidence root must be contained by .harness/evidence/handoff"
    if target_root == evidence_root:
        return None, "evidence root must name a new bundle directory below .harness/evidence/handoff"
    return target_root, None


def _validate_readiness_path(repo_root: Path, requested_path: Path) -> tuple[Path | None, str | None]:
    candidate = requested_path if requested_path.is_absolute() else repo_root / requested_path
    path = candidate.resolve(strict=False)
    evidence_root = (repo_root.joinpath(*_EVIDENCE_ROOT)).resolve()
    try:
        path.relative_to(evidence_root)
    except ValueError:
        return None, "handoff readiness manifest must be contained by .harness/evidence/handoff"
    if path.name != "eval-handoff-readiness.json" or path.is_symlink() or not path.is_file():
        return None, "handoff readiness manifest must be an existing regular eval-handoff-readiness.json file"
    return path, None


def _dry_run_result_is_pass(tessl_eval: dict[str, Any]) -> bool:
    return (
        tessl_eval.get("status") == "pass"
        and tessl_eval.get("dry_run") is True
        and tessl_eval.get("live_private") is True
    )


def _minimal_dry_run_evidence(tessl_eval: dict[str, Any]) -> dict[str, Any]:
    """Persist stable gate facts, excluding staged paths and raw provider output."""
    parity = tessl_eval.get("oss_scenario_parity")
    budget = tessl_eval.get("budget_preflight")
    return {
        "status": tessl_eval.get("status"),
        "dry_run": tessl_eval.get("dry_run"),
        "live_private": tessl_eval.get("live_private"),
        "workspace": tessl_eval.get("workspace"),
        "visibility": tessl_eval.get("visibility"),
        "oss_scenario_parity": {
            "status": parity.get("status"),
            "staged_case_count": parity.get("staged_case_count"),
            "staged_case_ids": parity.get("staged_case_ids"),
        } if isinstance(parity, dict) else None,
        "budget_preflight": {
            "status": budget.get("status"),
            "scenario_count": budget.get("scenario_count"),
            "max_scenarios_default": budget.get("max_scenarios_default"),
        } if isinstance(budget, dict) else None,
    }


def _lanes_and_envelopes(
    repo_root: Path,
    source_path: Path,
    target_root: Path | None,
    candidate: dict[str, str],
    receipts: dict[str, list[str]],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], list[str]]:
    lanes: list[dict[str, Any]] = []
    envelopes: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for lane_id in PRE_TESSL_DRY_RUN_LANE_IDS:
        payloads, source_receipts, source_digests, errors_for_lane = _source_receipts(
            repo_root,
            receipts.get(lane_id),
            candidate,
        )
        if errors_for_lane:
            errors.extend(f"{lane_id}: {error}" for error in errors_for_lane)
            continue
        lane = _lane(repo_root, lane_id, target_root, _captured_command(payloads))
        envelope = _envelope(repo_root, candidate, lane_id, source_receipts, source_digests, payloads)
        if not _valid_lane(lane_id, lane, envelope):
            errors.append(f"{lane_id}: receipt does not prove the declared handoff lane")
            continue
        lanes.append(lane)
        envelopes[lane_id] = envelope
    lanes.append(_pending_dry_run_lane(repo_root, source_path, target_root))
    return lanes, envelopes, errors


def _source_receipts(
    repo_root: Path,
    values: list[str] | None,
    candidate: dict[str, str],
) -> tuple[list[dict[str, Any]], list[Path], list[str], list[str]]:
    if not values:
        return [], [], [], ["missing receipt"]
    payloads: list[dict[str, Any]] = []
    paths: list[Path] = []
    digests: list[str] = []
    errors: list[str] = []
    for value in values:
        payload, path, digest, error = _source_receipt(repo_root, value, candidate)
        if error:
            errors.append(error)
        elif path is not None and digest is not None:
            payloads.append(payload)
            paths.append(path)
            digests.append(digest)
    return payloads, paths, digests, errors


def _source_receipt(
    repo_root: Path,
    value: str,
    candidate: dict[str, str],
) -> tuple[dict[str, Any], Path | None, str | None, str | None]:
    path = Path(value)
    if not path.is_file() or path.is_symlink():
        return {}, path, None, "receipt must be a regular non-symlink JSON file"
    try:
        path.resolve(strict=True).relative_to(repo_root.resolve())
    except ValueError:
        return {}, path, None, "receipt must be contained by the repository"
    try:
        source_bytes = path.read_bytes()
        payload = json.loads(source_bytes)
    except (OSError, json.JSONDecodeError) as exc:
        return {}, path, None, str(exc)
    if not isinstance(payload, dict):
        return {}, path, None, "json_root_not_object"
    binding_error = _source_binding_error(payload, candidate)
    if binding_error:
        return {}, path, None, binding_error
    digest = f"sha256:{hashlib.sha256(source_bytes).hexdigest()}"
    return payload, path, digest, None


def _source_binding_error(payload: dict[str, Any], candidate: dict[str, str]) -> str | None:
    if payload.get("schema_version") != HANDOFF_CAPTURE_SCHEMA_VERSION:
        return "receipt must be produced by sdk eval handoff-capture"
    observed = payload.get("candidate")
    if not isinstance(observed, dict) or any(observed.get(key) != value for key, value in candidate.items()):
        return "receipt candidate does not match the current skill source"
    issued_at = payload.get("issued_at")
    if not isinstance(issued_at, str):
        return "receipt must include an RFC3339 issued_at timestamp"
    try:
        observed_at = datetime.fromisoformat(issued_at.replace("Z", "+00:00"))
        if observed_at.tzinfo is None:
            raise ValueError("timestamp_has_no_timezone")
    except ValueError:
        return "receipt must include an RFC3339 issued_at timestamp"
    age = datetime.now(UTC) - observed_at.astimezone(UTC)
    if age.total_seconds() < 0 or age > HANDOFF_READINESS_MAX_AGE:
        return "receipt issued_at must be current and no older than 24 hours"
    return None


def _envelope(
    repo_root: Path,
    candidate: dict[str, str],
    lane_id: str,
    source_paths: list[Path],
    source_digests: list[str],
    payloads: list[dict[str, Any]],
) -> dict[str, Any]:
    source_path = source_paths[0] if len(source_paths) == 1 else None
    source_digest = source_digests[0] if len(source_digests) == 1 else None
    command = _captured_command(payloads)
    return {
        **_minimal_lane_evidence(lane_id, payloads),
        "schema_version": HANDOFF_MATERIALIZATION_SCHEMA_VERSION,
        "status": "pass",
        "candidate": candidate,
        "lane": lane_id,
        # The materialized receipt is itself a lane receipt.  Keep the
        # canonical, source-derived command here as well as in the bundle
        # manifest so a shard set remains inspectable without relying on a
        # singular source-receipt field.
        "command": command,
        "source_receipt_path": _repo_relative(repo_root, source_path) if source_path else None,
        "source_receipt_digest": source_digest,
        "source_receipt_paths": [_repo_relative(repo_root, path) for path in source_paths],
        "source_receipt_digests": source_digests,
    }


def _minimal_lane_evidence(lane_id: str, payloads: list[dict[str, Any]]) -> dict[str, Any]:
    """Keep only source facts the established lane-semantic checks consume."""
    evidence: dict[str, Any] = {}
    statuses = {_receipt_status(payload) for payload in payloads}
    if statuses == {"pass"}:
        evidence["status"] = "pass"
    if lane_id in {"oss-local", "oss-cloud"}:
        profiles = {_receipt_profile(payload) for payload in payloads}
        if len(profiles) == 1 and isinstance(next(iter(profiles)), str):
            evidence["codex_profile"] = next(iter(profiles))
        evidence["codex_exec_invoked"] = bool(payloads) and all(
            _receipt_codex_exec_invoked(payload) for payload in payloads
        )
        cases = _oss_case_evidence(payloads)
        if cases:
            evidence["cases"] = cases
    if lane_id == "tessl-local-proof" and payloads:
        evidence.update(_tessl_local_proof_evidence(payloads[0]))
    return evidence


def _oss_case_evidence(payloads: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Carry only case identifiers and result statuses into the parity receipt."""
    observed: dict[str, str] = {}
    for payload in payloads:
        has_direct_cases = False
        for receipt in _nested_receipt_payloads(payload):
            values = receipt.get("cases")
            if not isinstance(values, list):
                continue
            for value in values:
                if not isinstance(value, dict):
                    continue
                case_id, status = value.get("case_id"), value.get("status")
                if isinstance(case_id, str) and isinstance(status, str):
                    observed[case_id] = status
                    has_direct_cases = True
        if has_direct_cases:
            continue
        if _receipt_status(payload) != "pass":
            continue
        for case_id in _captured_case_ids(payload):
            observed[case_id] = "pass"
    return [
        {"case_id": case_id, "status": status}
        for case_id, status in sorted(observed.items())
    ]


def _captured_case_ids(payload: dict[str, Any]) -> list[str]:
    """Read bounded case ids from the canonical command recorded by a passing capture."""
    case_ids: list[str] = []
    commands = payload.get("commands")
    if not isinstance(commands, list):
        return case_ids
    for command in commands:
        if not isinstance(command, str):
            continue
        try:
            arguments = shlex.split(command)
        except ValueError:
            continue
        for index, value in enumerate(arguments[:-1]):
            if value == "--case" and arguments[index + 1]:
                case_ids.append(arguments[index + 1])
    return case_ids


def _tessl_local_proof_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    for receipt in _nested_receipt_payloads(payload):
        if receipt.get("schema_version") != "skills-sdk.tessl-local-proof.v1":
            continue
        return {
            "receipt": {
                "schema_version": receipt["schema_version"],
                "status": receipt.get("status"),
                "execute": receipt.get("execute"),
            }
        }
    return {}


def _lane(repo_root: Path, lane_id: str, target_root: Path | None, command: str) -> dict[str, Any]:
    receipt_path = target_root / f"{lane_id}.json" if target_root else Path(f"{lane_id}.json")
    return {
        "id": lane_id,
        "status": "pass",
        "command": command,
        "receipt_path": _repo_relative(repo_root, receipt_path),
    }


def _captured_command(payloads: list[dict[str, Any]]) -> str:
    values = [
        value.strip()
        for payload in payloads
        for value in (payload.get("commands") if isinstance(payload.get("commands"), list) else [])
        if isinstance(value, str) and value.strip()
    ]
    return " && ".join(values)


def _valid_lane(lane_id: str, lane: dict[str, Any], envelope: dict[str, Any]) -> bool:
    status = (_receipt_status(envelope) or "").lower()
    return status in {"pass", "success", "scored"} and _lane_profile_semantics(lane_id, lane, envelope)["ok"]


def _pending_dry_run_lane(repo_root: Path, source_path: Path, target_root: Path | None) -> dict[str, Any]:
    receipt_path = target_root / "tessl-live-dry-run.json" if target_root else Path("tessl-live-dry-run.json")
    readiness_path = (
        target_root / "eval-handoff-readiness.json"
        if target_root
        else Path("eval-handoff-readiness.json")
    )
    skill = _repo_relative(repo_root, _skill_dir(source_path))
    return {
        "id": "tessl-live-dry-run",
        "status": "blocked",
        "command": (
            f"./bin/ask evals run {skill} --tessl-live-private --tessl-workspace jscraik "
            f"--tessl-live-dry-run --handoff-readiness {_repo_relative(repo_root, readiness_path)} --json --robot"
        ),
        "receipt_path": _repo_relative(repo_root, receipt_path),
        "blocker": "not_run: materialize current pre-Tessl lanes, then run the recorded private Tessl dry-run once.",
    }


def _manifest(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": HANDOFF_READINESS_INPUT_SCHEMA_VERSION,
        "candidate": plan["candidate"],
        "issued_at": datetime.now(UTC).isoformat(),
        "lanes": plan["lanes"],
    }


def _receipt(
    plan: dict[str, Any],
    blockers: list[str],
    *,
    operation: Literal["preview", "execute"],
) -> dict[str, Any]:
    root = plan["target_root"]
    repo_root = plan["repo_root"]
    return {
        "schema_version": HANDOFF_MATERIALIZATION_SCHEMA_VERSION,
        "status": "blocked" if blockers else ("pass" if operation == "execute" else "preview"),
        "operation": "eval_handoff_materialize",
        "query": plan["query"],
        "candidate": plan["candidate"],
        "evidence_root": _repo_relative(repo_root, root) if root else None,
        "manifest_path": _repo_relative(repo_root, root / "eval-handoff-readiness.json") if root else None,
        "planned_lanes": [lane["id"] for lane in plan["lanes"]],
        "blockers": blockers,
        "ready_for_tessl_dry_run": not blockers,
        "mutation_performed": operation == "execute",
        "agent_summary": (
            "Handoff bundle materialized; the private Tessl dry-run is the next gate."
            if operation == "execute" and not blockers
            else "Handoff materialization is blocked: correct the lane receipt or command inputs."
            if blockers
            else "Handoff bundle preview is valid; rerun with --execute to write it."
        ),
    }


def _write_bundle(repo_root: Path, plan: dict[str, Any]) -> dict[str, Any]:
    target_root = plan["target_root"]
    if not isinstance(target_root, Path):
        return _receipt(plan, ["missing validated evidence root"], operation="preview")
    target_root.parent.mkdir(parents=True, exist_ok=True)
    target_root.mkdir(exist_ok=False)
    try:
        for lane_id, envelope in plan["envelopes"].items():
            (target_root / f"{lane_id}.json").write_text(
                json.dumps(envelope, indent=2, sort_keys=True) + "\n", encoding="utf-8",
            )
        readiness_path = target_root / "eval-handoff-readiness.json"
        readiness_path.write_text(json.dumps(_manifest(plan), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        admission = build_tessl_dry_run_admission(
            repo_root,
            source_path=_skill_md(plan["source_path"]),
            query=plan["query"],
            readiness_path=readiness_path,
        )
        if not admission["ready_for_tessl_dry_run"]:
            shutil.rmtree(target_root)
            return _receipt(
                plan,
                ["materialized bundle did not satisfy Tessl dry-run admission"],
                operation="preview",
            )
    except (OSError, ValueError):
        shutil.rmtree(target_root)
        raise
    return _receipt(plan, [], operation="execute")
