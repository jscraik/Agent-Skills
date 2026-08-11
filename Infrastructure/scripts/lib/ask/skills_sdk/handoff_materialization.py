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
    readiness, candidate, lanes = _readiness_for_dry_run(path)
    if not _dry_run_result_is_pass(tessl_eval):
        raise ValueError("only a successful private Tessl dry-run can be recorded")
    lane = next((item for item in lanes if isinstance(item, dict) and item.get("id") == "tessl-live-dry-run"), None)
    if not isinstance(lane, dict):
        raise ValueError("handoff readiness manifest is missing tessl-live-dry-run lane")
    existing = _existing_tessl_dry_run(repo_root, lane)
    if existing is not None:
        return existing
    receipt_path = _new_tessl_dry_run_path(path)
    receipt = {
        "schema_version": "skills-sdk.tessl-live-dry-run.v1",
        "status": "pass",
        "lane": "tessl-live-dry-run",
        "candidate": candidate,
        "issued_at": datetime.now(UTC).isoformat(),
        "tessl_eval": _minimal_dry_run_evidence(tessl_eval),
    }
    _write_tessl_dry_run(repo_root, path, readiness, lane, receipt_path, receipt)
    return _repo_relative(repo_root, receipt_path)


def _readiness_for_dry_run(path: Path) -> tuple[dict[str, Any], dict[str, Any], list[Any]]:
    """Load the minimal readiness fields needed to record the first dry run."""
    try:
        readiness = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"handoff readiness manifest is unreadable: {exc}") from exc
    candidate = readiness.get("candidate") if isinstance(readiness, dict) else None
    lanes = readiness.get("lanes") if isinstance(readiness, dict) else None
    if not isinstance(candidate, dict) or not isinstance(lanes, list):
        raise ValueError("handoff readiness manifest must contain candidate and lanes")
    return readiness, candidate, lanes


def _existing_tessl_dry_run(repo_root: Path, lane: dict[str, Any]) -> str | None:
    """Return a prior regular receipt or reject an incomplete passed lane."""
    if lane.get("status") != "pass":
        return None
    raw_path = lane.get("receipt_path")
    existing_path = repo_root / raw_path if isinstance(raw_path, str) else None
    if existing_path is not None and existing_path.is_file() and not existing_path.is_symlink():
        return _repo_relative(repo_root, existing_path)
    raise ValueError("completed Tessl dry-run lane is missing its regular receipt")


def _new_tessl_dry_run_path(readiness_path: Path) -> Path:
    """Reserve the one receipt path that a fresh materialized bundle may own."""
    receipt_path = readiness_path.parent / "tessl-live-dry-run.json"
    if receipt_path.exists() or receipt_path.is_symlink():
        raise ValueError("Tessl dry-run receipt already exists; materialize a fresh handoff bundle before retrying")
    return receipt_path


def _write_tessl_dry_run(
    repo_root: Path,
    readiness_path: Path,
    readiness: dict[str, Any],
    lane: dict[str, Any],
    receipt_path: Path,
    receipt: dict[str, Any],
) -> None:
    """Persist receipt then atomically advance its owning readiness manifest."""
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lane.update(status="pass", receipt_path=_repo_relative(repo_root, receipt_path), blocker=None)
    temporary_path = readiness_path.with_name(f".{readiness_path.name}.tmp")
    try:
        temporary_path.write_text(json.dumps(readiness, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(temporary_path, readiness_path)
    except OSError:
        receipt_path.unlink(missing_ok=True)
        temporary_path.unlink(missing_ok=True)
        raise


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
    path = requested_path.resolve(strict=False)
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
            lane_id,
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
    lane_id: str,
) -> tuple[list[dict[str, Any]], list[Path], list[str], list[str]]:
    if not values:
        return [], [], [], ["missing receipt"]
    payloads: list[dict[str, Any]] = []
    paths: list[Path] = []
    digests: list[str] = []
    errors: list[str] = []
    for value in values:
        payload, path, digest, error = _source_receipt(repo_root, value, candidate, lane_id)
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
    lane_id: str,
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
    binding_error, scenario_case_id = _source_binding_error(
        repo_root,
        payload,
        candidate,
        lane_id,
    )
    if binding_error:
        return {}, path, None, binding_error
    if scenario_case_id is not None:
        # The source receipt is immutable.  These derived facts are only used
        # while projecting a typed completed A/B cloud run into its bounded
        # handoff envelope.
        payload["_materialized_scenario_case_id"] = scenario_case_id
        payload["_materialized_oss_cloud_profile"] = "oss-cloud"
        payload["_materialized_codex_exec_invoked"] = True
    digest = f"sha256:{hashlib.sha256(source_bytes).hexdigest()}"
    return payload, path, digest, None


def _source_binding_error(
    repo_root: Path,
    payload: dict[str, Any],
    candidate: dict[str, str],
    lane_id: str,
) -> tuple[str | None, str | None]:
    if payload.get("schema_version") == HANDOFF_CAPTURE_SCHEMA_VERSION:
        if lane_id == "oss-cloud":
            return (
                "oss-cloud requires a completed FIFO-backed sdk eval ab-run receipt; "
                "generic handoff capture is not admissible",
                None,
            )
        return _capture_binding_error(payload, candidate, lane_id), None
    if lane_id != "oss-cloud":
        return "only oss-cloud accepts a completed sdk eval ab-run receipt", None
    return _ab_run_binding_error(repo_root, payload, candidate)


def _capture_binding_error(
    payload: dict[str, Any],
    candidate: dict[str, str],
    lane_id: str,
) -> str | None:
    observed = payload.get("candidate")
    if not isinstance(observed, dict) or any(observed.get(key) != value for key, value in candidate.items()):
        return "receipt candidate does not match the current skill source"
    if payload.get("lane") != lane_id:
        return f"receipt lane does not match requested lane: expected {lane_id}"
    if payload.get("status") != "pass":
        return "receipt status must be pass"
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


def _ab_run_binding_error(
    repo_root: Path,
    payload: dict[str, Any],
    candidate: dict[str, str],
) -> tuple[str | None, str | None]:
    """Bind OSS cloud evidence to one typed FIFO-backed B-variant scenario."""
    validated, error = _validated_ab_run_receipt(payload)
    if error:
        return error, None
    assert validated is not None
    if (
        validated.execution_lane != "oss-cloud"
        or validated.codex_profile != "oss-cloud"
        or not validated.codex_exec_invoked
        or not validated.provider_invoked
    ):
        return "A/B receipt must prove completed FIFO-backed oss-cloud provider execution", None
    variant_path, error = _b_variant_path(repo_root, validated)
    if error:
        return error, None
    assert variant_path is not None
    variant = build_candidate_identity(repo_root, variant_path)
    if any(variant.get(key) != candidate.get(key) for key in ("candidate_digest", "scenario_set_digest")):
        return "A/B B variant does not match the current skill source", None
    fixture = validated.fixture
    if fixture is None:
        return "A/B receipt must bind a controlled fixture", None
    return _scenario_case_id_for_fixture(
        repo_root,
        variant_path,
        fixture.path,
        fixture.digest,
        fixture.size_bytes,
    )


def _validated_ab_run_receipt(payload: dict[str, Any]) -> tuple[Any | None, str | None]:
    data = payload.get("data")
    ab_run = data.get("skills_sdk_eval_ab_run") if isinstance(data, dict) else None
    receipt = ab_run.get("receipt") if isinstance(ab_run, dict) else None
    if not (
        payload.get("status") == "success"
        and isinstance(ab_run, dict)
        and ab_run.get("schema_version") == "skills-sdk-ab-run.v0"
        and isinstance(receipt, dict)
        and receipt.get("schema_version") == "skills-sdk.ab-run-receipt.v1"
        and receipt.get("status") == "completed"
    ):
        return None, "oss-cloud requires a completed sdk eval ab-run receipt"
    try:
        from ask.skills_sdk.typed_contracts import validate_ab_run_receipt

        return validate_ab_run_receipt(receipt), None
    except (ImportError, ValueError):
        return None, "A/B receipt does not satisfy the canonical completed-run contract"


def _b_variant_path(repo_root: Path, validated: Any) -> tuple[Path | None, str | None]:
    """Resolve the B query through the canonical skill resolver before reading it."""
    skill_b = validated.skill_b
    query = skill_b.query if skill_b is not None else None
    if not isinstance(query, str) or not query.strip():
        return None, "A/B receipt must identify its B variant source path"
    from ask.commands.skills_impl_capabilities import _resolve_doctor_target

    target, audit_target = _resolve_doctor_target(repo_root, query)
    if not target.get("source_exists") or not isinstance(audit_target, str):
        return None, "A/B B variant source must resolve to a canonical contained skill directory"
    variant_path = (repo_root / audit_target).resolve(strict=False)
    try:
        variant_path.relative_to(repo_root.resolve())
    except ValueError:
        return None, "A/B B variant source must resolve to a canonical contained skill directory"
    if not variant_path.is_dir() or variant_path.is_symlink():
        return None, "A/B B variant source must resolve to a canonical contained skill directory"
    return variant_path, None


def _scenario_case_id_for_fixture(
    repo_root: Path,
    variant_path: Path,
    fixture_query: str,
    fixture_digest: str,
    fixture_size_bytes: int,
) -> tuple[str | None, str | None]:
    fixture_bytes, error = _validated_fixture_bytes(
        repo_root, fixture_query, fixture_digest, fixture_size_bytes,
    )
    if error:
        return error, None
    assert fixture_bytes is not None
    return _fixture_scenario_case_id(variant_path, fixture_bytes)


def _validated_fixture_bytes(
    repo_root: Path,
    fixture_query: str,
    fixture_digest: str,
    fixture_size_bytes: int,
) -> tuple[bytes | None, str | None]:
    """Read a regular contained fixture only when it still matches its receipt."""
    fixture_path = (repo_root / fixture_query).resolve(strict=False)
    try:
        fixture_path.relative_to(repo_root.resolve())
    except ValueError:
        return None, "A/B fixture must be contained by the repository"
    if not fixture_path.is_file() or fixture_path.is_symlink():
        return None, "A/B fixture must be a regular contained file"
    try:
        fixture_bytes = fixture_path.read_bytes()
    except OSError:
        return None, "A/B fixture could not be read"
    if (
        f"sha256:{hashlib.sha256(fixture_bytes).hexdigest()}" != fixture_digest
        or len(fixture_bytes) != fixture_size_bytes
    ):
        return None, "A/B fixture bytes do not match the receipt identity"
    return fixture_bytes, None


def _fixture_scenario_case_id(variant_path: Path, fixture_bytes: bytes) -> tuple[str | None, str | None]:
    """Match trusted fixture bytes to exactly one current canonical scenario prompt."""
    evals_path = variant_path / "references" / "evals.yaml"
    if not evals_path.is_file() or evals_path.is_symlink():
        return "A/B B variant is missing a regular references/evals.yaml", None
    try:
        from ask.skills_sdk.scenario_quality import _yaml_safe_load

        evals = _yaml_safe_load(evals_path.read_text(encoding="utf-8"))
    except (ImportError, OSError, ValueError):
        return "A/B B variant references/evals.yaml is unreadable", None
    cases = evals.get("cases") if isinstance(evals, dict) else None
    matches = [
        row["id"]
        for row in cases if isinstance(cases, list) and isinstance(row, dict)
        and isinstance(row.get("id"), str)
        and isinstance(row.get("prompt"), str)
        and row["prompt"].encode("utf-8") == fixture_bytes
    ]
    if len(matches) != 1:
        return "A/B fixture must exactly match one current B references/evals.yaml prompt", None
    return None, matches[0]


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
        evidence.update(_oss_lane_evidence(payloads))
    if lane_id == "tessl-local-proof":
        evidence.update(_tessl_local_proof_evidence(payloads[0]))
    return evidence


def _oss_lane_evidence(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    """Project the profile, execution fact, and case parity evidence for OSS lanes."""
    evidence: dict[str, Any] = {
        "codex_exec_invoked": bool(payloads) and all(_oss_exec_invoked(payload) for payload in payloads),
    }
    profiles = {_oss_profile(payload) for payload in payloads}
    if len(profiles) == 1 and isinstance(next(iter(profiles)), str):
        evidence["codex_profile"] = next(iter(profiles))
    cases = _oss_case_evidence(payloads)
    if cases:
        evidence["cases"] = cases
        evidence["case_count"] = len(cases)
    return evidence


def _oss_profile(payload: dict[str, Any]) -> object:
    return payload.get("_materialized_oss_cloud_profile") or _receipt_profile(payload)


def _oss_exec_invoked(payload: dict[str, Any]) -> bool:
    return bool(payload.get("_materialized_codex_exec_invoked")) or _receipt_codex_exec_invoked(payload)


def _oss_case_evidence(payloads: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Carry only case identifiers and result statuses into the parity receipt."""
    observed: dict[str, str] = {}
    for payload in payloads:
        scenario_case_id = payload.get("_materialized_scenario_case_id")
        if isinstance(scenario_case_id, str):
            observed[scenario_case_id] = "pass"
            continue
        direct_cases = _direct_oss_cases(payload)
        if direct_cases:
            observed.update(direct_cases)
            continue
        if _receipt_status(payload) != "pass":
            continue
        for case_id in _captured_case_ids(payload):
            observed[case_id] = "pass"
    return [
        {"case_id": case_id, "status": status}
        for case_id, status in sorted(observed.items())
    ]


def _direct_oss_cases(payload: dict[str, Any]) -> dict[str, str]:
    """Return explicit result cases from nested canonical receipts."""
    observed: dict[str, str] = {}
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
    return observed


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
        for value in _source_commands(payload)
        if isinstance(value, str) and value.strip()
    ]
    return " && ".join(values)


def _source_commands(payload: dict[str, Any]) -> list[Any]:
    """Return canonical source commands from capture or typed A/B wrapper evidence."""
    commands = payload.get("commands")
    if isinstance(commands, list):
        return commands
    data = payload.get("data")
    ab_run = data.get("skills_sdk_eval_ab_run") if isinstance(data, dict) else None
    commands = ab_run.get("validation_commands") if isinstance(ab_run, dict) else None
    return commands if isinstance(commands, list) else []


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
