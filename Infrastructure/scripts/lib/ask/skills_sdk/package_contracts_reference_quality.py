from __future__ import annotations

from .package_contracts_common import *  # noqa: F403
from .package_contracts_parsing import *  # noqa: F403
from .package_contracts_assets import *  # noqa: F403
from .package_contracts_writing_support import *  # noqa: F403

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
