from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from ask.skills_sdk.review_plan import canonical_receipt_digest


REVIEW_EXECUTION_SCHEMA_VERSION = "skills-sdk.review-execution-receipt.v1"
REVIEW_EXECUTION_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/sdk-review-execution-receipt.v1.schema.json"
)
REVIEW_HANDOFF_SCHEMA_VERSION = "skills-sdk.review-handoff-receipt.v1"


def build_review_execution(
    repo_root: Path,
    *,
    handoff_path: str,
    receipt_out: str | None = None,
    clock_provider: Callable[[], datetime] | None = None,
) -> dict[str, Any]:
    source_handoff_path = _safe_repo_path(repo_root, handoff_path, label="handoff path")
    source_handoff = _load_json_object(source_handoff_path, label="review handoff receipt")
    _validate_handoff_shape(source_handoff)
    artifact_paths = _resolve_required_artifact_paths(repo_root, source_handoff["required_artifacts"])
    output_path = _resolve_receipt_output_path(
        repo_root,
        receipt_out,
        handoff_path=source_handoff_path,
        artifact_paths=[path for _artifact, path in artifact_paths],
    )

    executed_at = _format_timestamp((clock_provider or _default_clock_provider)())
    blocked_artifact_results = [
        _artifact_blocker(repo_root, path)
        for _artifact, path in artifact_paths
    ]
    known_failed_artifacts = [
        result["path"]
        for result in blocked_artifact_results
        if result is not None
    ]
    artifact_results = [
        _materialize_artifact(
            repo_root,
            source_handoff,
            artifact,
            path,
            executed_at=executed_at,
            blocked_result=blocked_result,
            failed_artifacts=known_failed_artifacts,
        )
        for (artifact, path), blocked_result in zip(artifact_paths, blocked_artifact_results, strict=True)
    ]
    failed_artifacts = [result["path"] for result in artifact_results if result["status"] != "pass"]
    receipt: dict[str, Any] = {
        "schema_version": REVIEW_EXECUTION_SCHEMA_VERSION,
        "schema_uri": REVIEW_EXECUTION_SCHEMA_URI,
        "status": "pass" if not failed_artifacts else "fail",
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
        "execution_mode": "local_governed_artifact_execution",
        "runner": {
            "name": "skills-sdk-local-review-executor",
            "version": REVIEW_EXECUTION_SCHEMA_VERSION,
            "external_services_used": False,
        },
        "artifact_results": artifact_results,
        "review_execution_completed": not failed_artifacts,
        "failed_artifacts": failed_artifacts,
        "evidence_boundaries": _execution_boundaries(source_handoff),
        "not_proven": _not_proven_after_execution(source_handoff),
        "next_commands": _next_commands(failed_artifacts),
        "mutation_performed": True,
        "receipt_written": False,
        "receipt_path": None,
    }
    if output_path is not None:
        receipt["receipt_written"] = True
        receipt["receipt_path"] = _repo_relative(repo_root, output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def _default_clock_provider() -> datetime:
    return datetime.now(timezone.utc)


def _format_timestamp(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("clock_provider must return a timezone-aware datetime.")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


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


def _resolve_required_artifact_paths(repo_root: Path, artifacts: list[str]) -> list[tuple[str, Path]]:
    artifact_paths = [(artifact, _safe_repo_path(repo_root, artifact, label="required artifact")) for artifact in artifacts]
    _validate_required_artifact_paths_do_not_overlap(artifact_paths)
    return artifact_paths


def _validate_required_artifact_paths_do_not_overlap(artifact_paths: list[tuple[str, Path]]) -> None:
    for index, (_artifact, path) in enumerate(artifact_paths):
        for _other_artifact, other_path in artifact_paths[index + 1 :]:
            if _paths_overlap(path, other_path):
                raise ValueError("required artifact paths must be distinct and non-overlapping.")


def _resolve_receipt_output_path(
    repo_root: Path,
    receipt_out: str | None,
    *,
    handoff_path: Path,
    artifact_paths: list[Path],
) -> Path | None:
    if receipt_out is None:
        return None
    output_path = _safe_repo_path(repo_root, receipt_out, label="receipt_out")
    if any(_paths_overlap(output_path, blocked_path) for blocked_path in [handoff_path, *artifact_paths]):
        raise ValueError(
            "receipt_out must be distinct from and non-overlapping with the handoff and required artifact paths."
        )
    if output_path.exists() and not output_path.is_file():
        raise ValueError("receipt_out must resolve to a file path.")
    if _parent_file_collision(repo_root, output_path):
        raise ValueError("receipt_out parent must resolve to a directory path.")
    return output_path


def _paths_overlap(path: Path, other_path: Path) -> bool:
    return path == other_path or _path_is_inside(path, other_path) or _path_is_inside(other_path, path)


def _path_is_inside(path: Path, parent_path: Path) -> bool:
    try:
        path.relative_to(parent_path)
    except ValueError:
        return False
    return path != parent_path


def _materialize_artifact(
    repo_root: Path,
    source_handoff: dict[str, Any],
    artifact: str,
    path: Path,
    *,
    executed_at: str,
    blocked_result: dict[str, Any] | None,
    failed_artifacts: list[str],
) -> dict[str, Any]:
    if blocked_result is not None:
        return blocked_result

    if path.exists() and path.stat().st_size > 0:
        return _artifact_result(repo_root, path, status="pass", action="preserved", reason="already_present")

    path.parent.mkdir(parents=True, exist_ok=True)
    content = _artifact_content(source_handoff, artifact, executed_at=executed_at, failed_artifacts=failed_artifacts)
    path.write_text(content, encoding="utf-8")
    return _artifact_result(repo_root, path, status="pass", action="written", reason="ok")


def _artifact_blocker(repo_root: Path, path: Path) -> dict[str, Any] | None:
    if path.exists() and not path.is_file():
        return _artifact_result(repo_root, path, status="fail", action="blocked", reason="not_file")
    if _parent_file_collision(repo_root, path):
        return _artifact_result(repo_root, path, status="fail", action="blocked", reason="parent_not_directory")
    return None


def _parent_file_collision(repo_root: Path, path: Path) -> bool:
    resolved_repo = repo_root.resolve()
    parent = path.parent.resolve()
    while True:
        if parent.exists():
            return not parent.is_dir()
        if parent == resolved_repo or parent.parent == parent:
            return False
        parent = parent.parent


def _artifact_content(
    source_handoff: dict[str, Any],
    artifact: str,
    *,
    executed_at: str,
    failed_artifacts: list[str],
) -> str:
    name = Path(artifact).name
    if name == "review-summary.md":
        return _review_summary(source_handoff, executed_at=executed_at)
    if name == "reviewer-findings.json":
        return json.dumps(_reviewer_findings(source_handoff, executed_at=executed_at), indent=2, sort_keys=True) + "\n"
    if name == "validation-evidence.json":
        return json.dumps(
            _validation_evidence(source_handoff, executed_at=executed_at, failed_artifacts=failed_artifacts),
            indent=2,
            sort_keys=True,
        ) + "\n"
    if artifact.endswith(".json"):
        return json.dumps(_generic_json_artifact(source_handoff, artifact, executed_at=executed_at), indent=2, sort_keys=True) + "\n"
    return _generic_text_artifact(source_handoff, artifact, executed_at=executed_at)


def _review_summary(source_handoff: dict[str, Any], *, executed_at: str) -> str:
    roles = "\n".join(f"- {role}" for role in source_handoff["reviewer_roles"])
    boundaries = "\n".join(f"- {boundary}" for boundary in source_handoff["evidence_boundaries"])
    not_proven = "\n".join(f"- {lane}" for lane in _not_proven_after_execution(source_handoff))
    return (
        "# SDK Review Execution Summary\n\n"
        f"- Target: {source_handoff['target']}\n"
        f"- Target kind: {source_handoff['target_kind']}\n"
        f"- Task intent: {source_handoff['task_intent']}\n"
        f"- Execution mode: local_governed_artifact_execution\n"
        f"- Executed at: {executed_at}\n\n"
        "## Reviewer Roles\n\n"
        f"{roles}\n\n"
        "## Findings Summary\n\n"
        "The Skills SDK materialized the required local review evidence packet from the handoff receipt. "
        "This artifact records governed local execution and does not assert independent reviewer approval, "
        "CI state, PR state, tracker state, or merge readiness.\n\n"
        "## Evidence Boundaries\n\n"
        f"{boundaries}\n\n"
        "## Not Proven\n\n"
        f"{not_proven}\n"
    )


def _reviewer_findings(source_handoff: dict[str, Any], *, executed_at: str) -> dict[str, Any]:
    return {
        "schema_version": "skills-sdk.reviewer-findings.v1",
        "status": "no_findings_asserted",
        "target": source_handoff["target"],
        "task_intent": source_handoff["task_intent"],
        "executed_at": executed_at,
        "reviewer_results": [
            {
                "role": role,
                "status": "artifact_materialized",
                "findings": [],
                "not_proven": ["independent_reviewer_approval", "substantive_human_review"],
            }
            for role in source_handoff["reviewer_roles"]
        ],
    }


def _validation_evidence(source_handoff: dict[str, Any], *, executed_at: str, failed_artifacts: list[str]) -> dict[str, Any]:
    command: dict[str, Any] = {
        "command": "./bin/ask sdk review execute --handoff <handoff-receipt> --json --robot",
        "outcome": "fail" if failed_artifacts else "pass",
        "evidence": (
            "required local review artifacts were not fully materialized from the handoff receipt"
            if failed_artifacts
            else "required local review artifacts materialized from the handoff receipt"
        ),
    }
    if failed_artifacts:
        command["failed_artifacts"] = failed_artifacts
    return {
        "schema_version": "skills-sdk.validation-evidence.v1",
        "status": "local_execution_failed" if failed_artifacts else "local_execution_recorded",
        "target": source_handoff["target"],
        "task_intent": source_handoff["task_intent"],
        "executed_at": executed_at,
        "commands": [command],
        "not_proven": _not_proven_after_execution(source_handoff),
    }


def _generic_json_artifact(source_handoff: dict[str, Any], artifact: str, *, executed_at: str) -> dict[str, Any]:
    return {
        "schema_version": "skills-sdk.generic-review-artifact.v1",
        "artifact": artifact,
        "target": source_handoff["target"],
        "task_intent": source_handoff["task_intent"],
        "executed_at": executed_at,
        "status": "materialized",
    }


def _generic_text_artifact(source_handoff: dict[str, Any], artifact: str, *, executed_at: str) -> str:
    return (
        "# SDK Review Artifact\n\n"
        f"- Artifact: {artifact}\n"
        f"- Target: {source_handoff['target']}\n"
        f"- Task intent: {source_handoff['task_intent']}\n"
        f"- Executed at: {executed_at}\n"
    )


def _artifact_result(repo_root: Path, path: Path, *, status: str, action: str, reason: str) -> dict[str, Any]:
    exists = path.exists()
    is_file = path.is_file()
    byte_size = path.stat().st_size if exists and is_file else 0
    return {
        "path": _repo_relative(repo_root, path),
        "status": status,
        "action": action,
        "reason": reason,
        "exists": exists,
        "is_file": is_file,
        "byte_size": byte_size,
        "sha256": _sha256_file(path) if status == "pass" and exists and is_file and byte_size > 0 else None,
    }


def _execution_boundaries(source_handoff: dict[str, Any]) -> list[str]:
    boundaries = list(source_handoff["evidence_boundaries"])
    extra = [
        "review execution receipt proves only local SDK artifact materialization",
        "review execution receipt does not prove independent reviewer approval",
        "review execution receipt does not prove external PR, CI, tracker, or merge-readiness state",
    ]
    for boundary in extra:
        if boundary not in boundaries:
            boundaries.append(boundary)
    return boundaries


def _not_proven_after_execution(source_handoff: dict[str, Any]) -> list[str]:
    not_proven = [lane for lane in source_handoff["not_proven"] if lane != "reviewers_completed"]
    for lane in (
        "independent_reviewer_approval",
        "substantive_human_review",
        "ci_passed",
        "pr_mergeable",
        "review_threads_resolved",
        "tracker_updated",
        "external_service_state",
    ):
        if lane not in not_proven:
            not_proven.append(lane)
    return not_proven


def _next_commands(failed_artifacts: list[str]) -> list[str]:
    if failed_artifacts:
        return [
            "Repair every failed artifact path listed in failed_artifacts.",
            "./bin/ask sdk review execute --handoff <handoff-receipt> --json --robot",
        ]
    return [
        "./bin/ask sdk review verify --handoff <handoff-receipt> --json --robot",
        "Check CI, PR, review-thread, tracker, and merge-readiness lanes separately.",
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
    except (IsADirectoryError, NotADirectoryError) as exc:
        raise ValueError(f"{label} must resolve to a file path.") from exc
    except UnicodeDecodeError as exc:
        raise ValueError(f"{label} must be valid UTF-8 JSON.") from exc
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
