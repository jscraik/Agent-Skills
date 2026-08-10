from .package_contracts_core import (
    OPTIMIZATION_ACCEPTANCE_RULES,
    OPTIMIZATION_EDIT_MODES,
    OPTIMIZATION_EDIT_OPERATIONS,
    OPTIMIZATION_GUARD_FAILURE_POLICIES,
    OPTIMIZATION_METRIC_DIRECTIONS,
    OPTIMIZATION_MODES,
    OPTIMIZATION_SPLIT_ROLES,
    OPTIMIZATION_TIE_POLICIES,
    SKILL_OPTIMIZATION_CONTRACT_SCHEMA_PATH,
    SKILL_OPTIMIZATION_CONTRACT_SCHEMA_VERSION,
    _basic_requirement_rubric_check,
    _capability_selector_fields,
    _contract_sequence_contains,
    read_reference_contract,
)
from .package_contracts_rubric import (
    _analytic_rubric_quality_check_for_repo,
    _manifest_declares_multiple_capabilities,
    _requires_tessl_handoff_quality,
)
from .package_contracts_support import (
    Any,
    PACKAGE_IGNORED_FILE_NAMES,
    Path,
    _manifest_orphaned_bundle_files,
    markdown_reference_heading_weak,
    markdown_title,
    package_local_regular_file,
    re,
    read_structured_reference,
    repo_relative_path,
    skill_markdown_text,
)

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


def skill_reference_files(repo_root: Path | None, skill_md: Path | None) -> list[dict[str, Any]]:
    """Return package reference files with repo-relative paths and quality signals."""
    if not skill_md:
        return []
    references_dir = skill_md.parent / "references"
    if not references_dir.is_dir():
        return []
    files: list[dict[str, Any]] = []
    for candidate in sorted(path for path in references_dir.rglob("*") if path.is_file()):
        if candidate.name.startswith(".") or candidate.name in PACKAGE_IGNORED_FILE_NAMES:
            continue
        try:
            text = candidate.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            files.append(
                {
                    "path": repo_relative_path(repo_root, candidate) if repo_root else candidate.as_posix(),
                    "status": "blocked_validation",
                    "reason": f"unreadable: {exc}",
                    "size_bytes": None,
                    "nonempty": False,
                }
            )
            continue
        stripped_lines = [line for line in text.splitlines() if line.strip()]
        files.append(
            {
                "path": repo_relative_path(repo_root, candidate) if repo_root else candidate.as_posix(),
                "status": "pass" if stripped_lines else "blocked_validation",
                "reason": None if stripped_lines else "empty reference file",
                "size_bytes": candidate.stat().st_size,
                "nonempty": bool(stripped_lines),
            }
        )
    return files


def reference_quality_contract(repo_root: Path | None, skill_md: Path | None) -> dict[str, Any]:
    """Return deterministic reference-quality checks for package readiness."""
    references_dir = skill_md.parent / "references" if skill_md else None
    references_dir_path = (
        repo_relative_path(repo_root, references_dir) if repo_root and references_dir else None
    )
    files = skill_reference_files(repo_root, skill_md)
    checks: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []

    checks.append(
        {
            "name": "reference_inventory",
            "status": "pass" if references_dir and references_dir.is_dir() else "not_applicable",
            "path": references_dir_path,
            "file_count": len(files),
        }
    )
    for item in files:
        checks.append(
            {
                "name": "reference_file_nonempty",
                "status": item["status"],
                "path": item["path"],
                "size_bytes": item["size_bytes"],
            }
        )
        if item["status"] != "pass":
            blockers.append(
                {
                    "rule_id": "reference_file_empty_or_unreadable",
                    "path": item["path"],
                    "message": item["reason"],
                }
            )

    if references_dir and references_dir.is_dir():
        for candidate in sorted(references_dir.rglob("*.md")):
            if not candidate.is_file():
                continue
            rel_path = repo_relative_path(repo_root, candidate) if repo_root else candidate.as_posix()
            package_rel = (
                candidate.relative_to(skill_md.parent).as_posix()
                if skill_md is not None
                else candidate.name
            )
            if skill_md is not None and not package_local_regular_file(skill_md, package_rel):
                checks.append(
                    {
                        "name": "reference_heading_invocable",
                        "status": "blocked_validation",
                        "path": rel_path,
                        "reason": "reference path must be a package-local regular file",
                    }
                )
                blockers.append(
                    {
                        "rule_id": "reference_heading_not_invocable",
                        "path": rel_path,
                        "message": "Markdown reference must stay inside the package and must not be a symlink.",
                    }
                )
                continue
            try:
                text = candidate.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                checks.append(
                    {
                        "name": "reference_heading_invocable",
                        "status": "blocked_validation",
                        "path": rel_path,
                        "reason": str(exc),
                    }
                )
                blockers.append(
                    {
                        "rule_id": "reference_heading_not_invocable",
                        "path": rel_path,
                        "message": "Markdown reference could not be read for heading validation.",
                    }
                )
                continue
            weak_heading = markdown_reference_heading_weak(candidate, text)
            checks.append(
                {
                    "name": "reference_heading_invocable",
                    "status": "blocked_validation" if weak_heading else "pass",
                    "path": rel_path,
                    "title": markdown_title(text),
                    "policy": (
                        "Markdown reference and KnowledgeOS capsule headings must be "
                        "specific, filename-aligned, and invocable by routing agents."
                    ),
                }
            )
            if weak_heading:
                blockers.append(
                    {
                        "rule_id": "reference_heading_not_invocable",
                        "path": rel_path,
                        "message": (
                            "Markdown reference heading is missing, generic, or misaligned "
                            "with the file purpose; rewrite it as a specific routing trigger."
                        ),
                    }
                )

    if references_dir and references_dir.is_dir():
        for candidate in sorted(references_dir.rglob("*")):
            if not candidate.is_file() or candidate.suffix.lower() not in {".json", ".yaml", ".yml"}:
                continue
            loaded, error = read_structured_reference(candidate)
            rel_path = repo_relative_path(repo_root, candidate) if repo_root else candidate.as_posix()
            status = "pass" if error is None else "blocked_validation"
            checks.append(
                {
                    "name": "structured_reference_parse",
                    "status": status,
                    "path": rel_path,
                    "format": candidate.suffix.lower().lstrip("."),
                }
            )
            if error is not None:
                blockers.append(
                    {
                        "rule_id": "structured_reference_unparseable",
                        "path": rel_path,
                        "message": error,
                    }
                )
                continue
            if candidate.name == "contract.yaml":
                missing = []
                if not isinstance(loaded, dict):
                    missing = ["purpose", "inputs", "outputs"]
                else:
                    missing = [
                        field
                        for field in ("purpose", "inputs", "outputs")
                        if not loaded.get(field)
                    ]
                checks.append(
                    {
                        "name": "reference_contract_core_fields",
                        "status": "pass" if not missing else "blocked_validation",
                        "path": rel_path,
                        "missing": missing,
                    }
                )
                if missing:
                    blockers.append(
                        {
                            "rule_id": "reference_contract_incomplete",
                            "path": rel_path,
                            "message": f"Missing reference contract fields: {', '.join(missing)}.",
                        }
                    )
            if candidate.name == "evals.yaml":
                missing = []
                if not isinstance(loaded, dict):
                    missing = ["claims", "cases"]
                else:
                    for field in ("claims", "cases"):
                        value = loaded.get(field)
                        if not isinstance(value, list) or not value:
                            missing.append(field)
                checks.append(
                    {
                        "name": "reference_evals_core_fields",
                        "status": "pass" if not missing else "blocked_validation",
                        "path": rel_path,
                        "missing": missing,
                    }
                )
                if missing:
                    blockers.append(
                        {
                            "rule_id": "reference_evals_incomplete",
                            "path": rel_path,
                            "message": f"Missing eval reference fields: {', '.join(missing)}.",
                        }
                    )

    reference_contract = read_reference_contract(skill_md)
    reference_contract_selectors = _capability_selector_fields(reference_contract)
    requires_tessl_handoff_quality = _requires_tessl_handoff_quality(reference_contract)
    if references_dir and (references_dir / "contract.yaml").is_file():
        rubric_check, rubric_blockers = _basic_requirement_rubric_check(
            reference_contract,
            reference_contract_selectors,
            repo_root,
        )
        checks.append(rubric_check)
        blockers.extend(rubric_blockers)
        analytic_rubric_check, analytic_rubric_blockers = _analytic_rubric_quality_check_for_repo(
            reference_contract,
            repo_root,
        )
        checks.append(analytic_rubric_check)
        if requires_tessl_handoff_quality:
            blockers.extend(analytic_rubric_blockers)
    if references_dir and references_dir.is_dir():
        manifest_path = references_dir / "knowledge-capsule.manifest.yaml"
        routing_path = references_dir / "knowledge-capsule-routing.md"
        if manifest_path.is_file():
            orphaned_bundle_files = _manifest_orphaned_bundle_files(
                repo_root,
                skill_md,
                skill_markdown_text(skill_md),
            )
            checks.append(
                {
                    "name": "orphaned_bundle_reference",
                    "status": "blocked_validation" if orphaned_bundle_files else "pass",
                    "path": "references/knowledge-capsule.manifest.yaml",
                    "orphaned_paths": orphaned_bundle_files,
                    "policy": (
                        "When a knowledge capsule manifest exists, bundle support files "
                        "must be routed by SKILL.md, capsule routing, or package contracts."
                    ),
                }
            )
            if orphaned_bundle_files:
                blockers.append(
                    {
                        "rule_id": "orphaned_bundle_reference",
                        "path": "references/knowledge-capsule.manifest.yaml",
                        "message": (
                            "Knowledge capsule bundle files are present without a routed "
                            "package entrypoint: "
                            f"{', '.join(orphaned_bundle_files)}."
                        ),
                    }
                )
            manifest, manifest_error = read_structured_reference(manifest_path)
            manifest_payload = manifest if isinstance(manifest, dict) else {}
            has_multi_capability_manifest, manifest_facets = _manifest_declares_multiple_capabilities(
                manifest_payload
            )
            if has_multi_capability_manifest:
                selectors = reference_contract_selectors
                missing_selector: list[str] = []
                if manifest_error is not None:
                    missing_selector.append("knowledge-capsule.manifest.yaml")
                if not routing_path.is_file():
                    missing_selector.append("knowledge-capsule-routing.md")
                if not selectors:
                    missing_selector.append("capability_selection")
                for selector_key, selector_field in selectors.items():
                    if not _contract_sequence_contains(reference_contract, "inputs", selector_field):
                        missing_selector.append(f"inputs.{selector_field}")
                    if not _contract_sequence_contains(reference_contract, "outputs", selector_field):
                        missing_selector.append(f"outputs.{selector_field}")
                    quality_criteria = reference_contract.get("quality_criteria")
                    if (
                        selector_key != "capability_selection"
                        and (
                            not isinstance(quality_criteria, dict)
                            or not isinstance(quality_criteria.get(selector_key), dict)
                            or not quality_criteria.get(selector_key)
                        )
                    ):
                        missing_selector.append(f"quality_criteria.{selector_key}")
                skill_text = skill_markdown_text(skill_md)
                named_capsule_refs = sorted(
                    {
                        match
                        for match in re.findall(
                            r"references/knowledge-capsules/[^\s`<>]+\.md",
                            skill_text,
                        )
                        if "<capsule>" not in match
                    }
                )
                if named_capsule_refs:
                    missing_selector.append("progressive_disclosure_named_capsules")
                checks.append(
                    {
                        "name": "capability_selector_contract",
                        "status": "pass" if not missing_selector else "blocked_validation",
                        "path": "references/contract.yaml",
                        "missing": missing_selector,
                        "selectors": sorted(selectors),
                        "manifest_facets": manifest_facets,
                        "named_capsule_refs": named_capsule_refs,
                    }
                )
                if missing_selector:
                    blockers.append(
                        {
                            "rule_id": "capability_selector_contract_missing",
                            "path": "references/contract.yaml",
                            "message": (
                                "Skills with multi-facet capsule manifests must declare a "
                                "capability selector in references/contract.yaml and route "
                                "through top-level capsule references before Tessl handoff."
                            ),
                        }
                    )

    tessl_policy = reference_contract.get("tessl_scenario_policy")
    if requires_tessl_handoff_quality and isinstance(tessl_policy, dict):
        scenario_drift_review = tessl_policy.get("scenario_drift_review")
        missing_review = []
        if not isinstance(scenario_drift_review, dict):
            missing_review = ["scenario_drift_review"]
        else:
            if scenario_drift_review.get("required_after_skill_change") is not True:
                missing_review.append("required_after_skill_change")
            review_decisions = scenario_drift_review.get("review_decisions")
            allowed_decisions = {"keep", "update", "add", "remove"}
            if (
                not isinstance(review_decisions, list)
                or any(not isinstance(item, str) or item not in allowed_decisions for item in review_decisions)
                or {item for item in review_decisions if isinstance(item, str)} != allowed_decisions
            ):
                missing_review.append("review_decisions")
            review_surfaces = scenario_drift_review.get("review_surfaces")
            required_surfaces = {"references/evals.yaml", "references/evals/*.md"}
            surfaces_set = (
                {item.strip() for item in review_surfaces if isinstance(item, str) and item.strip()}
                if isinstance(review_surfaces, list)
                else set()
            )
            if not required_surfaces.issubset(surfaces_set):
                missing_review.append("review_surfaces")
        checks.append(
            {
                "name": "tessl_scenario_drift_review",
                "status": "pass" if not missing_review else "blocked_validation",
                "path": "references/contract.yaml",
                "missing": missing_review,
            }
        )
        if missing_review:
            blockers.append(
                {
                    "rule_id": "tessl_scenario_drift_review_missing",
                    "path": "references/contract.yaml",
                    "message": "Live Tessl scenario policy must declare scenario drift review after skill changes.",
                }
            )

    status = "blocked_validation" if blockers else "pass"
    return {
        "schema_version": "skill-reference-quality.v1",
        "policy": "references_are_package_contract",
        "required_for_package_readiness": True,
        "status": status,
        "references_dir": references_dir_path,
        "files": files,
        "checks": checks,
        "blockers": blockers,
    }
__all__ = [name for name in globals() if not name.startswith("__")]
