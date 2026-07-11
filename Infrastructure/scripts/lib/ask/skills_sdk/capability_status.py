from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


CAPABILITY_STATUS_SCHEMA_VERSION = "skills-sdk.capability-status.v1"
CAPABILITY_STATUS_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/capability-status.v1.schema.json"
)
MATRIX_PATH = Path("Infrastructure/config/skills-sdk/capability-matrix.v1.json")
ALLOWED_STATUSES = frozenset(
    {
        "implemented",
        "preview_only",
        "placeholder_optional",
        "placeholder_blocked",
        "blocked_missing_adapter",
        "deferred",
        "out_of_scope",
    }
)
MUTATING_CAPABILITY_IDS = frozenset(
    {
        "ab_judge_score",
        "ab_run",
        "real_install",
        "refs_ingestion",
        "review_execution",
        "rollback",
        "sdk_plugin_lifecycle",
        "trust_store",
        "uninstall",
    }
)
REQUIRED_CAPABILITY_IDS = (
    "authoring",
    "check",
    "manifest_schema",
    "receipt_schema",
    "risk_classification",
    "risk_mode_taxonomy",
    "package_security_signature",
    "skill_ir",
    "package_identity",
    "install_preview",
    "skill_intake",
    "skill_intake_review",
    "lockfile_preview",
    "real_install",
    "project_conformance",
    "sdk_lenses",
    "review_plan",
    "review_handoff",
    "review_execution",
    "review_verification",
    "determinism_audit",
    "trust_store",
    "observability_feedback",
    "refs_ingestion",
    "evals",
    "eval_profiles",
    "ab_rubric",
    "ab_preview",
    "ab_plan",
    "ab_run",
    "ab_judge_preview",
    "ab_judge_score",
    "scenario_quality_gate",
    "package_verify",
    "signing",
    "sandbox",
    "security_adapter",
    "static_docs",
    "capability_evidence",
    "skill_explorer",
    "schema_registry",
    "registry",
    "local_plugin_readiness",
    "sdk_plugin_lifecycle",
    "remote_marketplace",
    "publish",
    "rollback",
    "uninstall",
    "compiled_package_pipeline",
    "emitters",
    "ci_adoption_gates",
    "package_hardening",
)
CAPABILITY_ROW_KEYS = frozenset(
    {
        "evidence_refs",
        "feature_executed",
        "id",
        "mutation_performed",
        "next_slice",
        "notes",
        "owner_surface",
        "pipeline_sections",
        "status",
        "title",
    }
)


class CapabilityStatusError(ValueError):
    """Raised when the capability matrix would overclaim SDK truth."""


def load_capability_matrix(repo_root: Path) -> dict[str, Any]:
    matrix_path = repo_root / MATRIX_PATH
    try:
        payload = json.loads(matrix_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CapabilityStatusError(f"missing capability matrix: {MATRIX_PATH}") from exc
    except json.JSONDecodeError as exc:
        raise CapabilityStatusError(f"invalid capability matrix JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise CapabilityStatusError("capability matrix root must be an object")
    validate_capability_matrix(payload)
    return payload


def validate_capability_matrix(payload: dict[str, Any]) -> None:
    if payload.get("schema_version") != CAPABILITY_STATUS_SCHEMA_VERSION:
        raise CapabilityStatusError("capability matrix schema_version is invalid")
    if payload.get("schema_uri") != CAPABILITY_STATUS_SCHEMA_URI:
        raise CapabilityStatusError("capability matrix schema_uri is invalid")
    if payload.get("status") != "truth_surface":
        raise CapabilityStatusError("capability matrix status must be truth_surface")
    capabilities = payload.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        raise CapabilityStatusError("capability matrix must include capabilities")

    seen: set[str] = set()
    required = set(REQUIRED_CAPABILITY_IDS)
    for index, row in enumerate(capabilities):
        if not isinstance(row, dict):
            raise CapabilityStatusError(f"capability row {index} must be an object")
        extra_keys = sorted(set(row) - CAPABILITY_ROW_KEYS)
        if extra_keys:
            raise CapabilityStatusError(f"capability row {index} has unexpected keys: {', '.join(extra_keys)}")
        capability_id = _required_string(row, "id", index)
        if capability_id in seen:
            raise CapabilityStatusError(f"duplicate capability id: {capability_id}")
        seen.add(capability_id)
        status = _required_string(row, "status", index)
        if status not in ALLOWED_STATUSES:
            raise CapabilityStatusError(f"unknown status for {capability_id}: {status}")
        feature_executed = row.get("feature_executed")
        mutation_performed = row.get("mutation_performed")
        if not isinstance(feature_executed, bool):
            raise CapabilityStatusError(f"{capability_id} feature_executed must be boolean")
        if not isinstance(mutation_performed, bool):
            raise CapabilityStatusError(f"{capability_id} mutation_performed must be boolean")
        if status == "implemented" and not feature_executed:
            raise CapabilityStatusError(f"{capability_id} cannot be implemented without feature execution")
        if mutation_performed and capability_id not in MUTATING_CAPABILITY_IDS:
            raise CapabilityStatusError(f"{capability_id} cannot report mutation_performed")
        if mutation_performed and status != "implemented":
            raise CapabilityStatusError(f"{capability_id} cannot mutate unless implemented")
        for key in ("title", "owner_surface", "next_slice", "notes"):
            _required_string(row, key, index)
        for key in ("pipeline_sections", "evidence_refs"):
            values = row.get(key)
            if not isinstance(values, list) or not values or not all(isinstance(item, str) and item for item in values):
                raise CapabilityStatusError(f"{capability_id} {key} must be a non-empty string list")

    missing = sorted(required - seen)
    extra = sorted(seen - required)
    if missing:
        raise CapabilityStatusError(f"missing required capability ids: {', '.join(missing)}")
    if extra:
        raise CapabilityStatusError(f"unexpected capability ids: {', '.join(extra)}")


def build_capability_status(repo_root: Path) -> dict[str, Any]:
    matrix = load_capability_matrix(repo_root)
    capabilities = matrix["capabilities"]
    by_status = Counter(row["status"] for row in capabilities)
    summary = {
        "total": len(capabilities),
        "by_status": {status: by_status.get(status, 0) for status in sorted(ALLOWED_STATUSES)},
        "feature_executed_count": sum(1 for row in capabilities if row["feature_executed"]),
        "mutation_performed_count": sum(1 for row in capabilities if row["mutation_performed"]),
    }
    return {
        "schema_version": CAPABILITY_STATUS_SCHEMA_VERSION,
        "schema_uri": CAPABILITY_STATUS_SCHEMA_URI,
        "status": matrix["status"],
        "generated_from": matrix["generated_from"],
        "capabilities": capabilities,
        "summary": summary,
        "source_artifacts": matrix["source_artifacts"],
        "validation_commands": matrix["validation_commands"],
        "agent_summary": (
            "Skills SDK capability truth reports "
            f"{summary['feature_executed_count']} executable or preview-backed row(s), "
            f"{summary['by_status']['deferred']} deferred row(s), and "
            f"{summary['by_status']['out_of_scope']} out-of-scope row(s); "
            f"{summary['mutation_performed_count']} row(s) perform bounded mutation."
        ),
    }


def _required_string(row: dict[str, Any], key: str, index: int) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value:
        raise CapabilityStatusError(f"capability row {index} {key} must be a non-empty string")
    return value
