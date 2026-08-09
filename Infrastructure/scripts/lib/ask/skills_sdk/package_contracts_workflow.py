from __future__ import annotations

from .package_contracts_common import *  # noqa: F403
from .package_contracts_parsing import *  # noqa: F403
from .package_contracts_assets import *  # noqa: F403

def skill_package_file_path(
    repo_root: Path | None,
    skill_md: Path | None,
    relative_path: str,
) -> str | None:
    """Return a repo-relative package file path when present."""
    if not skill_md:
        return None
    candidate = skill_md.parent / relative_path
    if not candidate.is_file():
        return None
    if repo_root:
        return repo_relative_path(repo_root, candidate) or candidate.as_posix()
    return candidate.as_posix()


def skillflow_contract(repo_root: Path | None, skill_md: Path | None, reference_contract: dict[str, Any]) -> dict[str, Any]:
    """Return optional deterministic workflow contract metadata for one skill package."""
    workflow_decl = reference_contract.get("workflow")
    if not isinstance(workflow_decl, dict):
        workflow_decl = {}
    execution_mode = str(
        reference_contract.get("execution_mode") or workflow_decl.get("execution_mode") or "prose"
    )
    workflow_path_value = str(workflow_decl.get("path") or "workflows/skillflow.json")
    required = bool(workflow_decl.get("required") or execution_mode in {"deterministic_flow", "hybrid"})
    path = None
    rel_path = None
    if skill_md:
        path = skill_md.parent / workflow_path_value
        rel_path = repo_relative_path(repo_root, path) if repo_root else path.as_posix()
    exists = bool(path and path.is_file())
    checks: list[dict[str, Any]] = [
        {
            "name": "execution_mode_declared",
            "status": "pass" if execution_mode in SKILLFLOW_EXECUTION_MODES else "blocked_validation",
            "value": execution_mode,
            "allowed_values": sorted(SKILLFLOW_EXECUTION_MODES),
        },
        {
            "name": "workflow_file_presence",
            "status": "pass" if exists else ("blocked_validation" if required else "not_applicable"),
            "path": rel_path,
            "required": required,
        },
    ]
    blockers: list[dict[str, Any]] = []
    if execution_mode not in SKILLFLOW_EXECUTION_MODES:
        blockers.append(
            {
                "rule_id": "skillflow_execution_mode_invalid",
                "path": "references/contract.yaml",
                "message": f"execution_mode must be one of: {', '.join(sorted(SKILLFLOW_EXECUTION_MODES))}.",
            }
        )
    if required and not exists:
        blockers.append(
            {
                "rule_id": "skillflow_required_file_missing",
                "path": rel_path,
                "message": "Package declares deterministic workflow behavior but workflows/skillflow.json is missing.",
            }
        )

    node_count = 0
    side_effecting_nodes = 0
    human_gate_count = 0
    output_names: list[str] = []
    if exists and path:
        loaded, error = read_structured_reference(path)
        checks.append(
            {
                "name": "skillflow_parse",
                "status": "pass" if error is None and isinstance(loaded, dict) else "blocked_validation",
                "path": rel_path,
            }
        )
        if error is not None or not isinstance(loaded, dict):
            blockers.append(
                {
                    "rule_id": "skillflow_unparseable",
                    "path": rel_path,
                    "message": error or "skillflow must parse to an object.",
                }
            )
        else:
            schema_version = loaded.get("schema_version")
            nodes = loaded.get("nodes")
            inputs = loaded.get("inputs")
            outputs = loaded.get("outputs")
            checks.append(
                {
                    "name": "skillflow_schema_version",
                    "status": "pass" if schema_version == SKILLFLOW_SCHEMA_VERSION else "blocked_validation",
                    "expected": SKILLFLOW_SCHEMA_VERSION,
                    "actual": schema_version,
                }
            )
            if schema_version != SKILLFLOW_SCHEMA_VERSION:
                blockers.append(
                    {
                        "rule_id": "skillflow_schema_version_invalid",
                        "path": rel_path,
                        "message": f"schema_version must be {SKILLFLOW_SCHEMA_VERSION}.",
                    }
                )
            checks.append(
                {
                    "name": "skillflow_typed_inputs_outputs",
                    "status": "pass" if isinstance(inputs, dict) and isinstance(outputs, dict) else "blocked_validation",
                    "inputs_declared": isinstance(inputs, dict),
                    "outputs_declared": isinstance(outputs, dict),
                }
            )
            if not isinstance(inputs, dict) or not isinstance(outputs, dict):
                blockers.append(
                    {
                        "rule_id": "skillflow_inputs_outputs_missing",
                        "path": rel_path,
                        "message": "skillflow must declare typed inputs and outputs objects.",
                    }
                )
            if isinstance(outputs, dict):
                output_names = sorted(str(name) for name in outputs)
            if not isinstance(nodes, list) or not nodes:
                checks.append(
                    {
                        "name": "skillflow_nodes_declared",
                        "status": "blocked_validation",
                        "node_count": 0,
                    }
                )
                blockers.append(
                    {
                        "rule_id": "skillflow_nodes_missing",
                        "path": rel_path,
                        "message": "skillflow must declare at least one node.",
                    }
                )
            else:
                node_count = len(nodes)
                node_ids: list[str] = []
                duplicate_ids: set[str] = set()
                invalid_nodes: list[str] = []
                for node in nodes:
                    if not isinstance(node, dict):
                        invalid_nodes.append("<non-object>")
                        continue
                    node_id = str(node.get("id") or "")
                    node_type = str(node.get("type") or "")
                    if node_id in node_ids:
                        duplicate_ids.add(node_id)
                    if node_id:
                        node_ids.append(node_id)
                    if node_type not in SKILLFLOW_NODE_TYPES:
                        invalid_nodes.append(node_id or "<missing-id>")
                    if node.get("side_effect") or node.get("side_effecting"):
                        side_effecting_nodes += 1
                    if node_type == "human_gate":
                        human_gate_count += 1
                checks.append(
                    {
                        "name": "skillflow_nodes_declared",
                        "status": "pass",
                        "node_count": node_count,
                    }
                )
                checks.append(
                    {
                        "name": "skillflow_node_ids_unique",
                        "status": "pass" if not duplicate_ids else "blocked_validation",
                        "duplicates": sorted(duplicate_ids),
                    }
                )
                if duplicate_ids:
                    blockers.append(
                        {
                            "rule_id": "skillflow_duplicate_node_ids",
                            "path": rel_path,
                            "message": f"Duplicate node ids: {', '.join(sorted(duplicate_ids))}.",
                        }
                    )
                checks.append(
                    {
                        "name": "skillflow_node_types_allowed",
                        "status": "pass" if not invalid_nodes else "blocked_validation",
                        "invalid_nodes": invalid_nodes,
                        "allowed_types": sorted(SKILLFLOW_NODE_TYPES),
                    }
                )
                if invalid_nodes:
                    blockers.append(
                        {
                            "rule_id": "skillflow_node_type_invalid",
                            "path": rel_path,
                            "message": f"Invalid or missing node type on nodes: {', '.join(invalid_nodes)}.",
                        }
                    )
    status = "blocked_validation" if blockers else ("pass" if exists else "not_declared")
    return {
        "schema_version": "skillflow-contract.v1",
        "skillflow_schema_version": SKILLFLOW_SCHEMA_VERSION,
        "skillflow_schema_path": SKILLFLOW_SCHEMA_PATH,
        "status": status,
        "execution_mode": execution_mode,
        "required": required,
        "declared": exists,
        "path": rel_path,
        "node_count": node_count,
        "side_effecting_node_count": side_effecting_nodes,
        "human_gate_count": human_gate_count,
        "outputs": output_names,
        "adapt_policy": workflow_decl.get("adapt_policy")
        or {
            "retry_failed_node": "allowed",
            "choose_declared_branch": "allowed",
            "fill_typed_hole": "allowed",
            "add_node": "forbidden",
            "rewire_edge": "forbidden",
        },
        "amend_policy": workflow_decl.get("amend_policy") or "reviewed",
        "checks": checks,
        "blockers": blockers,
        "what_this_proves": [
            "workflow_contract_shape",
            "declared_node_graph_resolves_structurally",
        ] if exists and not blockers else [],
        "what_this_does_not_prove": [
            "workflow_runtime_execution",
            "llm_node_quality",
            "side_effect_idempotency",
        ],
    }


def _string_list(value: Any) -> list[str]:
    """Return a string list without treating scalar text as a complete contract."""
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return []


def _path_exists_for_contract(skill_md: Path | None, path_value: Any) -> bool | None:
    """Return existence for a package-relative path, or None for template placeholders."""
    if not skill_md or not isinstance(path_value, str) or not path_value.strip():
        return None
    if "<" in path_value or ">" in path_value:
        return None
    candidate = skill_md.parent / path_value
    return candidate.exists()


def _positive_int(value: Any) -> int | None:
    """Return a positive integer from structured YAML or simple fallback scalars."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value > 0:
        return value
    if isinstance(value, str) and value.strip().isdigit():
        parsed = int(value.strip())
        return parsed if parsed > 0 else None
    return None

__all__ = [name for name in globals() if not name.startswith("__")]
