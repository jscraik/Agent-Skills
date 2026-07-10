from __future__ import annotations

import json
from pathlib import Path
from typing import Any


LIFECYCLE_ROUTE_MAP_PATH = Path("Infrastructure/config/skills-sdk/lifecycle-route-map.v1.json")
CAPABILITY_MATRIX_PATH = Path("Infrastructure/config/skills-sdk/capability-matrix.v1.json")
LIFECYCLE_ROUTE_MAP_RECEIPT_SCHEMA_VERSION = "skills-sdk.lifecycle-route-map-receipt.v0"
LIFECYCLE_ROUTE_MAP_RECEIPT_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/lifecycle-route-map-receipt.v0.schema.json"
)
LIFECYCLE_ROUTE_MAP_ACCEPTANCE_TRACE = ["FR-008", "SA-003", "VP-032"]
REQUIRED_ROUTE_IDS = {
    "adoption_decision",
    "command_evidence_plan",
    "lifecycle_route_map",
    "tessl_confirmation_boundary",
    "knowledge_source_durability",
}
REQUIRED_LOOPS = {
    "Entry Lifecycle Cycle",
    "Early Lifecycle Cycle",
    "Middle Lifecycle Cycle",
    "Pre-release Lifecycle Cycle",
    "Runtime Loop",
}
REQUIRED_STAGES = {
    "Foundry",
    "SDK Entry Lifecycle",
    "Guardrails/Sandbox Security Review",
    "SDK Early Lifecycle",
    "Evals/Proof (oss-local)",
    "Tessl Distribution",
    "Local Runtime Truth",
}
ALLOWED_STAGES = REQUIRED_STAGES | {
    "SDK Middle Lifecycle",
    "Evals/Proof (oss-cloud)",
    "SDK Pre-release Lifecycle",
}


def build_lifecycle_route_map_receipt(repo_root: Path) -> dict[str, Any]:
    map_path = repo_root / LIFECYCLE_ROUTE_MAP_PATH
    try:
        payload = json.loads(map_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        payload = {"routes": []}
        checks = [_check("route_map_load", "blocker", "Lifecycle route map must load as JSON.", [str(exc)])]
    else:
        checks = [_check("route_map_load", "pass", "Lifecycle route map loaded as JSON.", [LIFECYCLE_ROUTE_MAP_PATH.as_posix()])]
    routes = payload.get("routes") if isinstance(payload, dict) else None
    capability_ids, capability_checks = _capability_ids(repo_root)
    checks.extend(capability_checks)
    route_checks = _route_checks(repo_root, routes, capability_ids)
    checks.extend(route_checks)
    blockers = [check for check in checks if check["status"] == "blocker"]
    status = "pass" if not blockers else "blocked"
    return {
        "schema_version": LIFECYCLE_ROUTE_MAP_RECEIPT_SCHEMA_VERSION,
        "schema_uri": LIFECYCLE_ROUTE_MAP_RECEIPT_SCHEMA_URI,
        "status": status,
        "operation": "lifecycle_route_map_preview",
        "route_map_path": LIFECYCLE_ROUTE_MAP_PATH.as_posix(),
        "route_count": len(routes) if isinstance(routes, list) else 0,
        "routes": routes if isinstance(routes, list) else [],
        "checks": checks,
        "blockers": blockers,
        "mutation_performed": False,
        "command_execution_performed": False,
        "acceptance_trace": LIFECYCLE_ROUTE_MAP_ACCEPTANCE_TRACE,
        "agent_summary": (
            f"Lifecycle route map validation {status}; routes bind SDK commands to modules, schemas, tests, "
            "capability rows, pipeline stages, and feedback loops."
        ),
    }


def _route_checks(repo_root: Path, routes: Any, capability_ids: set[str]) -> list[dict[str, Any]]:
    if not isinstance(routes, list) or not routes:
        return [_check("routes_present", "blocker", "Lifecycle route map must contain routes.", [])]
    checks = [_check("routes_present", "pass", "Lifecycle route map contains routes.", [str(len(routes))])]
    checks.extend(_required_route_checks(routes))
    for route in routes:
        if not isinstance(route, dict):
            checks.append(_check("route_shape", "blocker", "Each lifecycle route must be an object.", [repr(route)]))
            continue
        checks.extend(_route_file_checks(repo_root, str(route.get("id") or "missing"), route, capability_ids))
    return checks


def _required_route_checks(routes: list[Any]) -> list[dict[str, Any]]:
    route_ids = {route.get("id") for route in routes if isinstance(route, dict)}
    loops = {route.get("loop") for route in routes if isinstance(route, dict)}
    stages = {route.get("pipeline_stage") for route in routes if isinstance(route, dict)}
    missing = sorted(REQUIRED_ROUTE_IDS - route_ids)
    missing_loops = sorted(REQUIRED_LOOPS - loops)
    missing_stages = sorted(REQUIRED_STAGES - stages)
    unknown_stages = sorted(str(stage) for stage in stages if stage not in ALLOWED_STAGES)
    return [
        _required_routes_check(missing),
        _check("required_loops_present", "blocker" if missing_loops else "pass", "Route map must name the lifecycle and runtime cycles.", missing_loops),
        _check("required_stages_present", "blocker" if missing_stages else "pass", "Route map must include all required pipeline stages.", missing_stages),
        _check("pipeline_stages_known", "blocker" if unknown_stages else "pass", "Route map stages must use canonical pipeline names.", unknown_stages),
    ]


def _required_routes_check(missing: list[str]) -> dict[str, Any]:
    return (
        _check(
            "required_routes_present",
            "blocker" if missing else "pass",
            "The five current Skills SDK direction recommendations must stay represented.",
            missing,
        )
    )


def _route_file_checks(repo_root: Path, route_id: str, route: dict[str, Any], capability_ids: set[str]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for key in ("command", "owner_module", "receipt_schema", "test_ref", "capability_id", "proof_boundary"):
        value = route.get(key)
        checks.append(_check(f"{route_id}.{key}", "pass" if isinstance(value, str) and value else "blocker", f"Route {route_id} must define {key}.", [] if value else [key]))
    for key in ("receipt_schema", "test_ref"):
        value = route.get(key)
        if not isinstance(value, str) or not value:
            continue
        path = (repo_root / value).resolve(strict=False)
        inside = path.is_relative_to(repo_root.resolve())
        exists = inside and path.is_file()
        checks.append(
            _check(
                f"{route_id}.{key}_exists",
                "pass" if exists else "blocker",
                f"Route {route_id} {key} must point to a repo-local artifact.",
                [value],
            )
        )
    checks.extend(_route_capability_binding_checks(route_id, route, capability_ids))
    return checks


def _route_capability_binding_checks(route_id: str, route: dict[str, Any], capability_ids: set[str]) -> list[dict[str, Any]]:
    capability_id = route.get("capability_id")
    if not isinstance(capability_id, str) or not capability_id:
        return []
    capability_exists = capability_id in capability_ids
    return [
        _check(
            f"{route_id}.capability_id_exists",
            "pass" if capability_exists else "blocker",
            f"Route {route_id} capability_id must point to a capability matrix row.",
            [capability_id],
        )
    ]


def _capability_ids(repo_root: Path) -> tuple[set[str], list[dict[str, Any]]]:
    matrix_path = repo_root / CAPABILITY_MATRIX_PATH
    try:
        payload = json.loads(matrix_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return set(), [_check("capability_matrix_load", "blocker", "Capability matrix must load as JSON.", [str(exc)])]
    capabilities = payload.get("capabilities") if isinstance(payload, dict) else None
    if not isinstance(capabilities, list):
        return set(), [_check("capability_matrix_load", "blocker", "Capability matrix must contain capabilities.", [CAPABILITY_MATRIX_PATH.as_posix()])]
    capability_ids = {row["id"] for row in capabilities if isinstance(row, dict) and isinstance(row.get("id"), str) and row["id"]}
    return capability_ids, [_check("capability_matrix_load", "pass", "Capability matrix loaded for route capability binding.", [CAPABILITY_MATRIX_PATH.as_posix()])]


def _check(check_id: str, status: str, message: str, evidence: list[str]) -> dict[str, Any]:
    return {
        "id": check_id,
        "status": status,
        "severity": "blocker" if status == "blocker" else "info",
        "message": message,
        "evidence": evidence,
    }
