from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ask.skills_sdk.capability_status import CapabilityStatusError, build_capability_status
from ask.skills_sdk.schema_validation import validate_payload_against_schema


EVIDENCE_STATUS_SCHEMA_VERSION = "skills-sdk.evidence-status.v1"
EVIDENCE_STATUS_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/evidence-status.v1.schema.json"
)
EVIDENCE_STATUS_SCHEMA_PATH = Path("Infrastructure/config/schemas/skills-sdk/evidence-status.v1.schema.json")
QA_DISPATCH_SCHEMA_VERSION = "skills-sdk.qa-dispatch-record.v1"
DEFAULT_STABILIZATION_RECEIPT = Path(
    ".harness/evidence/skills-sdk-stabilization/skills-sdk.stabilization-baseline-receipt.v1.json"
)
LANE_MODES = ("local-build", "acceptance", "integration", "all")


class EvidenceStatusError(ValueError):
    """Raised when an evidence status input cannot be bound safely."""


@dataclass(frozen=True)
class QaDispatchRequest:
    """Controller-owned QA dispatch inputs bound to one source revision."""

    source_revision: str | None = None
    expected_revision: str | None = None
    receipt_sha256: str | None = None
    qa_artifact_ref: str | None = None
    qa_artifact_sha256: str | None = None
    task_id: str | None = None
    subagent_id: str | None = None
    state: str = "not_requested"


def build_evidence_status_receipt(
    repo_root: Path,
    *,
    mode: str = "all",
    required_mode: str | None = None,
    stabilization_receipt_path: str | Path | None = None,
    qa_dispatch_record_path: str | Path | None = None,
) -> dict[str, Any]:
    _validate_mode(mode, "mode")
    if required_mode is not None:
        _validate_mode(required_mode, "required_mode", allow_all=False)

    source_revision = _git_head(repo_root)
    dirty_state = _dirty_state(repo_root)
    receipt_path = Path(stabilization_receipt_path) if stabilization_receipt_path else DEFAULT_STABILIZATION_RECEIPT
    qa_dispatch = _load_or_build_qa_dispatch_record(repo_root, source_revision, qa_dispatch_record_path)

    lanes = [
        _build_local_build_lane(repo_root),
        _build_acceptance_lane(repo_root, source_revision, receipt_path),
        _build_integration_lane(),
    ]
    lane_by_id = {lane["id"]: lane for lane in lanes}
    selected_lane = required_mode or (None if mode == "all" else mode)
    selected_blockers = (
        [blocker for lane in lanes for blocker in lane["blockers"]]
        if selected_lane is None
        else list(lane_by_id[selected_lane]["blockers"])
    )
    ignored_blockers = []
    if selected_lane is not None:
        ignored_blockers = [
            {**blocker, "ignored_by": selected_lane}
            for lane in lanes
            if lane["id"] != selected_lane
            for blocker in lane["blockers"]
        ]

    return {
        "schema_version": EVIDENCE_STATUS_SCHEMA_VERSION,
        "schema_uri": EVIDENCE_STATUS_SCHEMA_URI,
        "status": "pass" if not selected_blockers else "blocked",
        "operation": "evidence_status",
        "mode": mode,
        "selected_lane": selected_lane or "all",
        "source_context": {
            "head_sha": source_revision,
            "dirty_state": dirty_state,
        },
        "lanes": lanes,
        "blockers": selected_blockers,
        "ignored_blockers": ignored_blockers,
        "qa_dispatch_record": qa_dispatch,
        "mutation_performed": False,
        "agent_summary": _agent_summary(mode, selected_lane, lanes, selected_blockers),
        "claims_boundary": (
            "Read-only lane status does not execute tests, external providers, runtime projections, "
            "generated caches, Foundry operations, hosted CI, reviews, or merge actions."
        ),
    }


def build_qa_dispatch_record(
    repo_root: Path,
    request: QaDispatchRequest | None = None,
) -> dict[str, Any]:
    selected_request = request or QaDispatchRequest()
    selected_revision = selected_request.source_revision or _git_head(repo_root)
    if (
        selected_request.expected_revision is not None
        and selected_revision != selected_request.expected_revision
    ):
        raise EvidenceStatusError(
            "qa dispatch source_revision does not match expected source revision"
        )
    if selected_request.state not in {"not_requested", "planned", "dispatched", "blocked", "accepted"}:
        raise EvidenceStatusError(f"unknown qa dispatch state: {selected_request.state}")
    return {
        "schema_version": QA_DISPATCH_SCHEMA_VERSION,
        "record_kind": "controller_owned_qa_dispatch",
        "controller_owned": True,
        "source_revision": selected_revision,
        "candidate_receipt_sha256": selected_request.receipt_sha256,
        "qa_artifact_ref": selected_request.qa_artifact_ref,
        "qa_artifact_sha256": selected_request.qa_artifact_sha256,
        "task_id": selected_request.task_id,
        "subagent_id": selected_request.subagent_id,
        "state": selected_request.state,
        "dispatch_performed": selected_request.state in {"dispatched", "accepted"},
        "claims_boundary": (
            "This record describes controller-owned QA routing only; it does not dispatch a reviewer "
            "or prove QA, receipt acceptance, hosted state, or release readiness."
        ),
    }


def _build_local_build_lane(repo_root: Path) -> dict[str, Any]:
    blockers: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    try:
        status = build_capability_status(repo_root)
    except (CapabilityStatusError, OSError, json.JSONDecodeError) as exc:
        blockers.append(_blocker("capability_matrix_invalid", "local-build", str(exc), ["capability-matrix"]))
    else:
        evidence.append(
            _evidence(
                "capability_matrix",
                "pass",
                f"validated {status['summary']['total']} capability rows without executing a command",
                ["Infrastructure/config/skills-sdk/capability-matrix.v1.json"],
            )
        )
    return {
        "id": "local-build",
        "status": "pass" if not blockers else "blocked",
        "blockers": blockers,
        "evidence": evidence,
    }


def _build_acceptance_lane(
    repo_root: Path,
    source_revision: str,
    receipt_path: Path,
) -> dict[str, Any]:
    blockers: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    candidate = receipt_path if receipt_path.is_absolute() else repo_root / receipt_path
    if not _is_within_repo(repo_root, candidate):
        blocker = _blocker(
            "stabilization_receipt_outside_source",
            "acceptance",
            "receipt path must stay inside the current Skills SDK source worktree",
            [str(candidate)],
        )
        return {"id": "acceptance", "status": "blocked", "blockers": [blocker], "evidence": []}
    evidence_ref = _relative_or_absolute(repo_root, candidate)
    if not candidate.is_file():
        blockers.append(
            _blocker(
                "stabilization_receipt_missing",
                "acceptance",
                "revision-bound stabilization receipt is missing",
                [evidence_ref],
            )
        )
        return {"id": "acceptance", "status": "blocked", "blockers": blockers, "evidence": evidence}
    try:
        receipt = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        blockers.append(_blocker("stabilization_receipt_invalid", "acceptance", str(exc), [evidence_ref]))
        return {"id": "acceptance", "status": "blocked", "blockers": blockers, "evidence": evidence}
    if not isinstance(receipt, dict):
        blockers.append(_blocker("stabilization_receipt_invalid", "acceptance", "receipt root is not an object", [evidence_ref]))
        return {"id": "acceptance", "status": "blocked", "blockers": blockers, "evidence": evidence}

    # Verify receipt authenticity: must be controller-owned or signed
    if not receipt.get("controller_owned") and not receipt.get("signature"):
        blockers.append(
            _blocker(
                "receipt_authenticity_missing",
                "acceptance",
                "receipt is neither controller-owned nor signed; forged receipts are rejected",
                [evidence_ref],
            )
        )

    if receipt.get("implementation_sha") != source_revision:
        blockers.append(
            _blocker(
                "stabilization_receipt_source_mismatch",
                "acceptance",
                "receipt implementation_sha does not match the current source revision",
                [evidence_ref, source_revision],
            )
        )

    qa_artifact_ref = receipt.get("qa_artifact_ref")
    qa_artifact_digest = receipt.get("qa_artifact_digest")

    if not qa_artifact_ref:
        blockers.append(
            _blocker(
                "qa_artifact_missing",
                "acceptance",
                "receipt does not bind an independent QA artifact",
                [evidence_ref],
            )
        )
    if not qa_artifact_digest:
        blockers.append(
            _blocker(
                "qa_artifact_digest_missing",
                "acceptance",
                "receipt does not bind a QA artifact SHA-256",
                [evidence_ref],
            )
        )

    # Recompute QA artifact SHA-256 and verify it matches
    if qa_artifact_ref and qa_artifact_digest:
        qa_artifact_path = Path(qa_artifact_ref)
        if not qa_artifact_path.is_absolute():
            qa_artifact_path = repo_root / qa_artifact_path
        if not _is_within_repo(repo_root, qa_artifact_path):
            blockers.append(
                _blocker(
                    "qa_artifact_outside_source",
                    "acceptance",
                    "QA artifact path must stay inside the current source worktree",
                    [str(qa_artifact_path)],
                )
            )
        elif not qa_artifact_path.is_file():
            blockers.append(
                _blocker(
                    "qa_artifact_file_missing",
                    "acceptance",
                    "QA artifact file does not exist at referenced path",
                    [str(qa_artifact_path)],
                )
            )
        else:
            try:
                actual_digest = _sha256_file(qa_artifact_path)
                if actual_digest != qa_artifact_digest:
                    blockers.append(
                        _blocker(
                            "qa_artifact_digest_mismatch",
                            "acceptance",
                            f"QA artifact SHA-256 mismatch; expected {qa_artifact_digest}, computed {actual_digest}",
                            [str(qa_artifact_path)],
                        )
                    )
            except (OSError, ValueError) as exc:
                blockers.append(
                    _blocker(
                        "qa_artifact_digest_computation_failed",
                        "acceptance",
                        f"could not compute QA artifact SHA-256: {exc}",
                        [str(qa_artifact_path)],
                    )
                )

    if receipt.get("claim_status") != "accepted":
        blockers.append(
            _blocker(
                "stabilization_claim_not_accepted",
                "acceptance",
                f"receipt claim_status is {receipt.get('claim_status', 'missing')!r}",
                [evidence_ref],
            )
        )
    if not blockers:
        evidence.append(_evidence("stabilization_receipt", "pass", "receipt is revision and QA bound with verified authenticity and digest", [evidence_ref]))
    return {
        "id": "acceptance",
        "status": "pass" if not blockers else "blocked",
        "blockers": blockers,
        "evidence": evidence,
    }


def _build_integration_lane() -> dict[str, Any]:
    blockers = [
        _blocker("runtime_projection_not_run", "integration", "runtime projection lane is intentionally read-only and not run", ["runtime projection"]),
        _blocker("generated_cache_not_run", "integration", "generated cache lane is intentionally not mutated", ["generated caches"]),
        _blocker("foundry_not_run", "integration", "Foundry extraction/initialization is outside this status command", ["Foundry"]),
        _blocker("provider_external_not_run", "integration", "provider and external-service proof requires a separate receipt", ["external providers"]),
        _blocker("hosted_review_merge_not_run", "integration", "hosted CI, review, and merge state are not local evidence", ["hosted state"]),
    ]
    return {"id": "integration", "status": "blocked", "blockers": blockers, "evidence": []}


def _load_or_build_qa_dispatch_record(
    repo_root: Path,
    source_revision: str,
    record_path: str | Path | None,
) -> dict[str, Any]:
    if record_path is None:
        return build_qa_dispatch_record(repo_root, QaDispatchRequest(source_revision=source_revision))
    candidate = Path(record_path)
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    if not _is_within_repo(repo_root, candidate):
        raise EvidenceStatusError("QA dispatch record path must stay inside the current source worktree")
    try:
        payload = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidenceStatusError(f"QA dispatch record could not be read: {exc}") from exc
    if not isinstance(payload, dict):
        raise EvidenceStatusError("QA dispatch record root must be an object")
    if payload.get("source_revision") != source_revision:
        raise EvidenceStatusError("QA dispatch source_revision does not match current source revision")

    # Validate the loaded payload against the QA dispatch schema
    try:
        schema_file = repo_root / EVIDENCE_STATUS_SCHEMA_PATH
        evidence_schema = json.loads(schema_file.read_text(encoding="utf-8"))
        qa_dispatch_schema = evidence_schema.get("definitions", {}).get("qaDispatchRecord")
        if not qa_dispatch_schema:
            raise EvidenceStatusError("QA dispatch schema not found in evidence-status schema")
        validation_result = validate_payload_against_schema(
            payload,
            qa_dispatch_schema,
            {"evidence-status": evidence_schema},
            schema_path=EVIDENCE_STATUS_SCHEMA_PATH,
            payload_source=str(candidate),
            truth_lane="acceptance",
        )
        if validation_result.status != "pass":
            diagnostics = "; ".join(d.message for d in validation_result.diagnostics)
            raise EvidenceStatusError(f"QA dispatch record schema validation failed: {diagnostics}")
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        raise EvidenceStatusError(f"QA dispatch record schema validation could not be performed: {exc}") from exc

    return payload


def _validate_mode(mode: str, field: str, *, allow_all: bool = True) -> None:
    choices = LANE_MODES if allow_all else LANE_MODES[:-1]
    if mode not in choices:
        raise EvidenceStatusError(f"{field} must be one of: {', '.join(choices)}")


def _git_head(repo_root: Path) -> str:
    process = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    head = process.stdout.strip()
    if process.returncode != 0 or len(head) != 40:
        raise EvidenceStatusError("could not resolve current source revision")
    return head


def _dirty_state(repo_root: Path) -> str:
    process = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.returncode != 0:
        return "unknown"
    return "dirty" if process.stdout.strip() else "clean"


def _blocker(identifier: str, lane: str, message: str, evidence: list[str]) -> dict[str, Any]:
    return {"id": identifier, "lane": lane, "message": message, "evidence": evidence}


def _evidence(identifier: str, status: str, message: str, evidence: list[str]) -> dict[str, Any]:
    return {"id": identifier, "status": status, "message": message, "evidence": evidence}


def _relative_or_absolute(repo_root: Path, candidate: Path) -> str:
    try:
        return candidate.resolve(strict=False).relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(candidate)


def _is_within_repo(repo_root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve(strict=False).relative_to(repo_root.resolve())
    except ValueError:
        return False
    return True


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _agent_summary(
    mode: str,
    selected_lane: str | None,
    lanes: list[dict[str, Any]],
    blockers: list[dict[str, Any]],
) -> str:
    lane_summary = ", ".join(f"{lane['id']}={lane['status']}" for lane in lanes)
    selection = selected_lane or "all"
    if blockers:
        return f"Skills SDK evidence status selected {selection} ({mode}); lanes: {lane_summary}; {len(blockers)} blocker(s) remain."
    return f"Skills SDK evidence status selected {selection} ({mode}); lanes: {lane_summary}; no selected-lane blockers."
