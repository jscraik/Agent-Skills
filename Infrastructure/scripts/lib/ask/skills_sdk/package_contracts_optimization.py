from __future__ import annotations

from .package_contracts_common import *  # noqa: F403
from .package_contracts_parsing import *  # noqa: F403
from .package_contracts_assets import *  # noqa: F403
from .package_contracts_workflow import _path_exists_for_contract, _positive_int, _string_list

def optimization_contract(
    repo_root: Path | None,
    skill_md: Path | None,
    reference_contract: dict[str, Any],
) -> dict[str, Any]:
    """Return optional SkillOpt-style bounded optimization contract metadata."""
    optimization_decl = reference_contract.get("optimization")
    if not isinstance(optimization_decl, dict):
        optimization_decl = {}
    enabled = bool(optimization_decl.get("enabled"))
    target_artifact = str(optimization_decl.get("target_artifact") or "SKILL.md")
    target_path = skill_md.parent / target_artifact if skill_md and target_artifact else None
    target_rel = (
        repo_relative_path(repo_root, target_path) if repo_root and target_path else (
            target_path.as_posix() if target_path else None
        )
    )

    checks: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []

    if not enabled:
        return {
            "schema_version": "skill-optimization-readiness.v1",
            "optimization_schema_version": SKILL_OPTIMIZATION_CONTRACT_SCHEMA_VERSION,
            "optimization_schema_path": SKILL_OPTIMIZATION_CONTRACT_SCHEMA_PATH,
            "status": "not_declared",
            "enabled": False,
            "target_artifact": target_artifact,
            "target_path": target_rel,
            "optimizer_mode": None,
            "split_seed": None,
            "edit_policy": None,
            "acceptance_gate": None,
            "anti_cheat": None,
            "evidence": None,
            "promotion": None,
            "roles": None,
            "checks": [
                {
                    "name": "optimization_declared",
                    "status": "not_applicable",
                    "enabled": False,
                }
            ],
            "blockers": [],
            "what_this_proves": [],
            "what_this_does_not_prove": [
                "optimized_skill_quality",
                "selection_gate_pass",
                "held_out_generalization",
                "anti_cheat_pass",
            ],
        }

    optimizer_mode = str(optimization_decl.get("optimizer_mode") or "")
    checks.append(
        {
            "name": "optimizer_mode_allowed",
            "status": "pass" if optimizer_mode in OPTIMIZATION_MODES else "blocked_validation",
            "value": optimizer_mode,
            "allowed_values": sorted(OPTIMIZATION_MODES),
        }
    )
    if optimizer_mode not in OPTIMIZATION_MODES:
        blockers.append(
            {
                "rule_id": "optimization_optimizer_mode_invalid",
                "path": "references/contract.yaml",
                "message": f"optimizer_mode must be one of: {', '.join(sorted(OPTIMIZATION_MODES))}.",
            }
        )

    target_exists = bool(target_path and target_path.is_file())
    checks.append(
        {
            "name": "optimization_target_artifact_exists",
            "status": "pass" if target_exists else "blocked_validation",
            "path": target_rel,
        }
    )
    if not target_exists:
        blockers.append(
            {
                "rule_id": "optimization_target_artifact_missing",
                "path": target_rel,
                "message": "optimization.target_artifact must resolve to a package file.",
            }
        )

    roles = optimization_decl.get("roles")
    role_names = ("target_runner", "optimizer", "promoter")
    missing_roles: list[str] = []
    if not isinstance(roles, dict):
        missing_roles = list(role_names)
        roles = {}
    else:
        missing_roles = [
            role
            for role in role_names
            if not isinstance(roles.get(role), dict) or not roles.get(role, {}).get("may_edit")
        ]
    checks.append(
        {
            "name": "optimization_roles_declared",
            "status": "pass" if not missing_roles else "blocked_validation",
            "missing": missing_roles,
        }
    )
    if missing_roles:
        blockers.append(
            {
                "rule_id": "optimization_roles_incomplete",
                "path": "references/contract.yaml",
                "message": f"Missing optimization role policies: {', '.join(missing_roles)}.",
            }
        )

    splits = optimization_decl.get("splits")
    split_seed = None
    split_checks: list[dict[str, Any]] = []
    if not isinstance(splits, dict):
        splits = {}
    else:
        split_seed = _positive_int(splits.get("split_seed")) or splits.get("split_seed")
    for split_name, expected_role in OPTIMIZATION_SPLIT_ROLES.items():
        split = splits.get(split_name)
        status = "blocked_validation"
        path_value = None
        role_value = None
        if isinstance(split, dict):
            path_value = split.get("path")
            role_value = split.get("role")
            if isinstance(path_value, str) and path_value.strip() and role_value == expected_role:
                status = "pass"
        path_exists = _path_exists_for_contract(skill_md, path_value)
        split_checks.append(
            {
                "split": split_name,
                "status": status,
                "path": path_value,
                "role": role_value,
                "expected_role": expected_role,
                "path_exists": path_exists,
            }
        )
    checks.append(
        {
            "name": "optimization_splits_declared",
            "status": "pass" if all(item["status"] == "pass" for item in split_checks) else "blocked_validation",
            "splits": split_checks,
        }
    )
    if not all(item["status"] == "pass" for item in split_checks):
        blockers.append(
            {
                "rule_id": "optimization_splits_incomplete",
                "path": "references/contract.yaml",
                "message": "optimization.splits must declare train, selection, and test with distinct roles.",
            }
        )

    edit_policy = optimization_decl.get("edit_policy")
    if not isinstance(edit_policy, dict):
        edit_policy = {}
    edit_mode = str(edit_policy.get("mode") or "")
    operations = set(_string_list(edit_policy.get("operations")))
    max_edits = _positive_int(edit_policy.get("max_edits"))
    edit_policy_ok = (
        edit_mode in OPTIMIZATION_EDIT_MODES
        and bool(operations)
        and operations.issubset(OPTIMIZATION_EDIT_OPERATIONS)
        and max_edits is not None
    )
    checks.append(
        {
            "name": "optimization_edit_policy_declared",
            "status": "pass" if edit_policy_ok else "blocked_validation",
            "mode": edit_mode,
            "operations": sorted(operations),
            "max_edits": max_edits,
        }
    )
    if not edit_policy_ok:
        blockers.append(
            {
                "rule_id": "optimization_edit_policy_incomplete",
                "path": "references/contract.yaml",
                "message": "optimization.edit_policy must declare mode, allowed operations, and positive max_edits.",
            }
        )

    acceptance_gate = optimization_decl.get("acceptance_gate")
    if not isinstance(acceptance_gate, dict):
        acceptance_gate = {}
    acceptance_ok = (
        bool(acceptance_gate.get("metric"))
        and acceptance_gate.get("direction") in OPTIMIZATION_METRIC_DIRECTIONS
        and acceptance_gate.get("rule") in OPTIMIZATION_ACCEPTANCE_RULES
        and acceptance_gate.get("ties") in OPTIMIZATION_TIE_POLICIES
        and acceptance_gate.get("guard_failure") in OPTIMIZATION_GUARD_FAILURE_POLICIES
    )
    checks.append(
        {
            "name": "optimization_acceptance_gate_declared",
            "status": "pass" if acceptance_ok else "blocked_validation",
            "metric": acceptance_gate.get("metric"),
            "direction": acceptance_gate.get("direction"),
            "rule": acceptance_gate.get("rule"),
            "ties": acceptance_gate.get("ties"),
            "guard_failure": acceptance_gate.get("guard_failure"),
        }
    )
    if not acceptance_ok:
        blockers.append(
            {
                "rule_id": "optimization_acceptance_gate_incomplete",
                "path": "references/contract.yaml",
                "message": "optimization.acceptance_gate must declare metric, direction, rule, tie policy, and guard failure policy.",
            }
        )

    anti_cheat = optimization_decl.get("anti_cheat")
    if not isinstance(anti_cheat, dict):
        anti_cheat = {}
    protected_paths = _string_list(anti_cheat.get("protected_paths"))
    anti_cheat_checks = _string_list(anti_cheat.get("checks"))
    anti_cheat_ok = bool(protected_paths) and bool(anti_cheat_checks)
    checks.append(
        {
            "name": "optimization_anti_cheat_declared",
            "status": "pass" if anti_cheat_ok else "blocked_validation",
            "protected_path_count": len(protected_paths),
            "checks": anti_cheat_checks,
        }
    )
    if not anti_cheat_ok:
        blockers.append(
            {
                "rule_id": "optimization_anti_cheat_incomplete",
                "path": "references/contract.yaml",
                "message": "optimization.anti_cheat must declare protected_paths and checks.",
            }
        )

    evidence = optimization_decl.get("evidence")
    if not isinstance(evidence, dict):
        evidence = {}
    evidence_required = [
        "root",
        "rollout_jsonl",
        "rejected_buffer_jsonl",
        "candidate_artifact",
        "promotion_manifest",
    ]
    missing_evidence = [
        field for field in evidence_required if not isinstance(evidence.get(field), str) or not evidence.get(field)
    ]
    checks.append(
        {
            "name": "optimization_evidence_paths_declared",
            "status": "pass" if not missing_evidence else "blocked_validation",
            "missing": missing_evidence,
            "root": evidence.get("root"),
        }
    )
    if missing_evidence:
        blockers.append(
            {
                "rule_id": "optimization_evidence_paths_incomplete",
                "path": "references/contract.yaml",
                "message": f"Missing optimization evidence fields: {', '.join(missing_evidence)}.",
            }
        )

    promotion = optimization_decl.get("promotion")
    if not isinstance(promotion, dict):
        promotion = {}
    promotion_checks = _string_list(promotion.get("required_checks"))
    promotion_ok = promotion.get("canonical_edit_requires_review") is True and bool(promotion_checks)
    checks.append(
        {
            "name": "optimization_promotion_policy_declared",
            "status": "pass" if promotion_ok else "blocked_validation",
            "canonical_edit_requires_review": promotion.get("canonical_edit_requires_review"),
            "required_checks": promotion_checks,
        }
    )
    if not promotion_ok:
        blockers.append(
            {
                "rule_id": "optimization_promotion_policy_incomplete",
                "path": "references/contract.yaml",
                "message": "optimization.promotion must require review for canonical edits and list required checks.",
            }
        )

    status = "blocked_validation" if blockers else "pass"
    return {
        "schema_version": "skill-optimization-readiness.v1",
        "optimization_schema_version": SKILL_OPTIMIZATION_CONTRACT_SCHEMA_VERSION,
        "optimization_schema_path": SKILL_OPTIMIZATION_CONTRACT_SCHEMA_PATH,
        "status": status,
        "enabled": True,
        "target_artifact": target_artifact,
        "target_path": target_rel,
        "optimizer_mode": optimizer_mode,
        "split_seed": split_seed,
        "edit_policy": edit_policy or None,
        "acceptance_gate": acceptance_gate or None,
        "anti_cheat": anti_cheat or None,
        "evidence": evidence or None,
        "promotion": promotion or None,
        "roles": roles or None,
        "checks": checks,
        "blockers": blockers,
        "what_this_proves": [
            "optimization_contract_shape",
            "bounded_candidate_policy_declared",
            "selection_gate_policy_declared",
            "anti_cheat_policy_declared",
        ] if status == "pass" else [],
        "what_this_does_not_prove": [
            "optimized_skill_quality",
            "selection_gate_pass",
            "held_out_generalization",
            "anti_cheat_pass",
        ],
    }

__all__ = [name for name in globals() if not name.startswith("__")]
