from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ask.skills_sdk.review_plan import canonical_receipt_digest


REVIEW_VERIFICATION_SCHEMA_VERSION = "skills-sdk.review-verification-receipt.v1"
REVIEW_VERIFICATION_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/sdk-review-verification-receipt.v1.schema.json"
)
REVIEW_HANDOFF_SCHEMA_VERSION = "skills-sdk.review-handoff-receipt.v1"


def build_review_verification(
    repo_root: Path,
    *,
    handoff_path: str,
    receipt_out: str | None = None,
) -> dict[str, Any]:
    source_handoff_path = _safe_repo_path(repo_root, handoff_path, label="handoff path")
    source_handoff = _load_json_object(source_handoff_path, label="review handoff receipt")
    _validate_handoff_shape(source_handoff)

    artifact_results = [_artifact_result(repo_root, artifact) for artifact in source_handoff["required_artifacts"]]
    missing_or_invalid = [
        result["path"]
        for result in artifact_results
        if result["status"] != "pass"
    ]
    receipt: dict[str, Any] = {
        "schema_version": REVIEW_VERIFICATION_SCHEMA_VERSION,
        "schema_uri": REVIEW_VERIFICATION_SCHEMA_URI,
        "status": "pass" if not missing_or_invalid else "fail",
        "source_review_handoff": {
            "path": _repo_relative(repo_root, source_handoff_path),
            "schema_version": source_handoff["schema_version"],
            "receipt_sha256": canonical_receipt_digest(source_handoff),
            "receipt_path": source_handoff.get("receipt_path"),
        },
        "target": source_handoff["target"],
        "target_kind": source_handoff["target_kind"],
        "task_intent": source_handoff["task_intent"],
        "reviewer_roles": source_handoff["reviewer_roles"],
        "required_artifacts": source_handoff["required_artifacts"],
        "artifact_results": artifact_results,
        "review_artifacts_verified": not missing_or_invalid,
        "missing_or_invalid_artifacts": missing_or_invalid,
        "evidence_boundaries": source_handoff["evidence_boundaries"],
        "not_proven": _preserve_not_proven(source_handoff),
        "next_commands": _next_commands(missing_or_invalid),
        "mutation_performed": False,
        "receipt_written": False,
        "receipt_path": None,
    }
    if receipt_out:
        output_path = _safe_repo_path(repo_root, receipt_out, label="receipt_out")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        receipt["receipt_written"] = True
        receipt["receipt_path"] = _repo_relative(repo_root, output_path)
        output_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def _validate_handoff_shape(source_handoff: dict[str, Any]) -> None:
    if source_handoff.get("schema_version") != REVIEW_HANDOFF_SCHEMA_VERSION:
        raise ValueError("source review handoff schema_version is unsupported.")
    if source_handoff.get("status") != "pass":
        raise ValueError("source review handoff must have pass status.")
    for key in (
        "target",
        "target_kind",
        "task_intent",
        "reviewer_roles",
        "required_artifacts",
        "evidence_boundaries",
        "not_proven",
    ):
        if key not in source_handoff:
            raise ValueError(f"source review handoff is missing {key}.")
    for key in ("reviewer_roles", "required_artifacts", "evidence_boundaries", "not_proven"):
        value = source_handoff[key]
        if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
            raise ValueError(f"source review handoff {key} must be a non-empty string list.")
    for key in ("target", "target_kind", "task_intent"):
        value = source_handoff[key]
        if not isinstance(value, str) or not value:
            raise ValueError(f"source review handoff {key} must be a non-empty string.")


def _artifact_result(repo_root: Path, artifact: str) -> dict[str, Any]:
    path = _safe_repo_path(repo_root, artifact, label="required artifact")
    exists = path.exists()
    is_file = path.is_file()
    byte_size = path.stat().st_size if exists and is_file else 0
    status = "pass" if exists and is_file and byte_size > 0 else "fail"
    reason = "ok"
    digest = None
    if not exists:
        reason = "missing"
    elif not is_file:
        reason = "not_file"
    elif byte_size <= 0:
        reason = "empty"
    else:
        digest = _sha256_file(path)
    return {
        "path": _repo_relative(repo_root, path),
        "status": status,
        "reason": reason,
        "exists": exists,
        "is_file": is_file,
        "byte_size": byte_size,
        "sha256": digest,
    }


def _preserve_not_proven(source_handoff: dict[str, Any]) -> list[str]:
    not_proven = list(source_handoff["not_proven"])
    for lane in (
        "ci_passed",
        "pr_mergeable",
        "review_threads_resolved",
        "tracker_updated",
        "external_service_state",
    ):
        if lane not in not_proven:
            not_proven.append(lane)
    return not_proven


def _next_commands(missing_or_invalid: list[str]) -> list[str]:
    if missing_or_invalid:
        return [
            "Create or repair every required review artifact listed in missing_or_invalid_artifacts.",
            "./bin/ask sdk review verify --handoff <handoff-receipt> --json --robot",
        ]
    return [
        "Review artifacts are locally verified; check PR, CI, review-thread, tracker, and merge-readiness lanes separately.",
    ]


def _safe_repo_path(repo_root: Path, path: str, *, label: str) -> Path:
    if not isinstance(path, str) or not path:
        raise ValueError(f"{label} must be a non-empty string.")
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    resolved_repo = repo_root.resolve()
    resolved = candidate.resolve()
    try:
        resolved.relative_to(resolved_repo)
    except ValueError as exc:
        raise ValueError(f"{label} must resolve inside the repository root.") from exc
    return resolved


def _load_json_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"{label} does not exist.") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} is invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} root must be an object.")
    return payload


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _repo_relative(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()
