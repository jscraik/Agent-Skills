from .package_contracts_core import *  # noqa: F403

def _analytic_rubric_quality_check(contract: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, str]]]:
    """Return whether quality_criteria follow the gold-standard analytic rubric shape."""
    return _analytic_rubric_quality_check_for_repo(contract, None)


def _analytic_rubric_quality_check_for_repo(
    contract: dict[str, Any],
    repo_root: Path | None,
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    """Return whether merged centralized/local rubric criteria follow analytic shape."""
    quality_criteria, automatic_failures, profile_errors, profile_ids = _combined_rubric_quality_criteria(
        repo_root,
        contract,
    )
    findings: list[str] = []
    checked: list[str] = []
    if not isinstance(quality_criteria, dict) or not quality_criteria:
        findings.append("quality_criteria")
    else:
        for key, value in quality_criteria.items():
            criterion_id = str(key)
            if criterion_id.endswith("_selection"):
                continue
            checked.append(criterion_id)
            findings.extend(_analytic_rubric_criterion_findings(criterion_id, value))
    if not checked:
        findings.append("quality_criteria.observable_analytic_criterion")
    findings.extend(profile_errors)
    if not [item for item in automatic_failures if isinstance(item, str) and item.strip()]:
        findings.append("automatic_failure_conditions")
    check = _analytic_rubric_quality_check_payload(findings, checked, profile_ids)
    blockers: list[dict[str, str]] = []
    if findings:
        blockers.append(
            {
                "rule_id": "analytic_rubric_quality_missing",
                "path": "references/contract.yaml",
                "message": (
                    "references/contract.yaml must define analytic rubric criteria "
                    "with purpose, why_it_matters, observable_evidence, scoring anchors 5-1, "
                    "and automatic_failure_conditions before Tessl handoff."
                ),
            }
        )
    return check, blockers


def _analytic_rubric_criterion_findings(criterion_id: str, value: object) -> list[str]:
    prefix = f"quality_criteria.{criterion_id}"
    if not isinstance(value, dict) or not value:
        return [f"{prefix}:analytic_mapping_required"]
    findings = [f"{prefix}.{field}" for field in ANALYTIC_RUBRIC_FIELDS if field not in value]
    for field in ("purpose", "why_it_matters"):
        if field in value and (not isinstance(value.get(field), str) or not str(value.get(field)).strip()):
            findings.append(f"{prefix}.{field}:nonempty_string_required")
    observable_evidence = value.get("observable_evidence")
    if "observable_evidence" in value and not _valid_observable_evidence(observable_evidence):
        findings.append(f"{prefix}.observable_evidence:nonempty_string_or_list_required")
    return [*findings, *_analytic_rubric_scoring_findings(prefix, value)]


def _valid_observable_evidence(value: object) -> bool:
    return (isinstance(value, str) and bool(value.strip())) or (
        isinstance(value, list) and any(isinstance(item, str) and item.strip() for item in value)
    )


def _analytic_rubric_scoring_findings(prefix: str, value: dict[str, Any]) -> list[str]:
    scoring = value.get("scoring")
    if not isinstance(scoring, dict) or not scoring:
        return [f"{prefix}.scoring:nonempty_mapping_required"] if "scoring" in value else []
    findings = [f"{prefix}.scoring.{score}" for score in ANALYTIC_RUBRIC_SCORES - {str(key) for key in scoring}]
    findings.extend(
        f"{prefix}.scoring.{key}:nonempty_string_required"
        for key, item in scoring.items()
        if not isinstance(item, str) or not item.strip()
    )
    return findings


def _analytic_rubric_quality_check_payload(
    findings: list[str], checked: list[str], profile_ids: list[str],
) -> dict[str, Any]:
    return {
        "name": "analytic_rubric_quality", "status": "pass" if not findings else "blocked_validation",
        "path": "references/contract.yaml", "criteria_checked": sorted(checked),
        "missing": sorted(findings), "rubric_profiles": profile_ids,
        "policy": "Skills SDK rubric criteria must use an analytic rubric shape. Shared criteria may come from centralized rubric_profile entries; skill-local criteria should only add selectors or domain-specific overrides.",
    }


def _requires_tessl_handoff_quality(contract: dict[str, Any]) -> bool:
    """Return whether this reference contract declares a live Tessl handoff lane."""
    tessl_policy = contract.get("tessl_scenario_policy")
    return isinstance(tessl_policy, dict) and not (
        tessl_policy.get("structure_only") is True
        or tessl_policy.get("structure_check_only") is True
    )


def _manifest_declares_multiple_capabilities(manifest: dict[str, Any]) -> tuple[bool, list[str]]:
    """Return whether a capsule manifest exposes multiple selectable facets."""
    facet_values: set[str] = set()
    selected_facets = manifest.get("selected_facets")
    if isinstance(selected_facets, list):
        for item in selected_facets:
            if isinstance(item, str) and item.strip():
                facet_values.add(item.split(":", 1)[-1])
    upstream_packs = manifest.get("upstream_packs")
    if isinstance(upstream_packs, list):
        for item in upstream_packs:
            if not isinstance(item, dict):
                continue
            default_facets = item.get("default_facets")
            if isinstance(default_facets, list):
                facet_values.update(
                    str(facet) for facet in default_facets if isinstance(facet, str) and facet
                )
    capsules = manifest.get("capsules")
    if isinstance(capsules, list):
        for item in capsules:
            if isinstance(item, dict) and isinstance(item.get("facet_id"), str):
                facet_values.add(item["facet_id"])
    return len(facet_values) > 1, sorted(facet_values)


def skill_markdown_text(skill_md: Path | None) -> str:
    """Return SKILL.md body text for contract discovery without raising."""
    if not skill_md or not skill_md.is_file():
        return ""
    try:
        return skill_md.read_text(encoding="utf-8")
    except OSError:
        return ""


def markdown_heading_declared(text: str, heading: str) -> bool:
    """Return whether a markdown heading with *heading* exists."""
    target = heading.strip().lower()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        title = stripped.lstrip("#").strip().lower()
        if title == target:
            return True
    return False


def markdown_section_body(text: str, heading: str) -> str:
    """Return the body for a markdown heading without following sibling sections."""
    target = heading.strip().lower()
    collecting = False
    heading_level = 0
    body: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            title = stripped.lstrip("#").strip().lower()
            level = len(stripped) - len(stripped.lstrip("#"))
            if collecting and level <= heading_level:
                break
            if title == target:
                collecting = True
                heading_level = level
                continue
        if collecting:
            body.append(line)
    return "\n".join(body).strip()


def progressive_disclosure_reference_paths(body: str) -> list[str]:
    """Return referenced package paths declared in the progressive-disclosure section."""
    return [raw for raw in body.split("`")[1::2] if raw.startswith("references/")]


def package_local_regular_file(skill_md: Path | None, raw_path: str) -> bool:
    """Return whether a declared package path is a regular file under the skill package."""
    if not skill_md:
        return False
    path = Path(raw_path)
    if path.is_absolute() or "\\" in raw_path or ".." in path.parts:
        return False
    package_root = skill_md.parent
    candidate = package_root / path
    if _path_has_symlink_component(package_root, candidate):
        return False
    try:
        candidate.resolve(strict=True).relative_to(package_root.resolve())
    except (OSError, ValueError):
        return False
    return candidate.is_file()


def package_local_reference_path(raw_path: str) -> bool:
    """Return whether a manifest target path is a package-local reference path."""
    path = Path(raw_path)
    return (
        bool(raw_path.strip())
        and not path.is_absolute()
        and "\\" not in raw_path
        and ".." not in path.parts
        and path.parts[:1] == ("references",)
    )


def _path_has_symlink_component(root: Path, path: Path) -> bool:
    try:
        relative_parts = path.relative_to(root).parts
    except ValueError:
        return True
    current = root
    for part in relative_parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def missing_progressive_disclosure_references(
    skill_md: Path | None,
    reference_paths: list[str],
) -> list[str]:
    """Return progressive-disclosure references that are absent from the skill package."""
    return [raw for raw in reference_paths if not package_local_regular_file(skill_md, raw)]


def operating_model_format_contract(skill_md: Path | None, text: str) -> dict[str, Any]:
    """Return whether named workspace artifacts keep first-class format docs."""
    if not skill_md or not text:
        return {
            "artifacts_declared": [],
            "required_format_references": [],
            "present_format_references": [],
            "missing_format_references": [],
            "format_references_ready": False,
            "policy": (
                "Skills that name durable workspace artifacts must preserve their "
                "operating-model docs as package-local references instead of "
                "compressing them into SKILL.md."
            ),
        }

    artifacts: list[str] = []
    required: list[str] = []
    present: list[str] = []
    missing: list[str] = []
    for artifact, needles, reference_path in OPERATING_MODEL_FORMAT_DOCS:
        if not any(needle in text for needle in needles):
            continue
        artifacts.append(artifact)
        required.append(reference_path)
        if package_local_regular_file(skill_md, reference_path):
            present.append(reference_path)
        else:
            missing.append(reference_path)

    return {
        "artifacts_declared": artifacts,
        "required_format_references": required,
        "present_format_references": present,
        "missing_format_references": missing,
        "format_references_ready": bool(artifacts) and not missing,
        "policy": (
            "Skills that name durable workspace artifacts must preserve their "
            "operating-model docs as package-local references instead of "
            "compressing them into SKILL.md."
        ),
    }


def source_operating_model_contract(skill_md: Path | None, progressive_body: str) -> dict[str, Any]:
    """Return whether source operating-model context is preserved as routed references."""
    source_context_path = skill_md.parent / "references" / "source-context.yaml" if skill_md else None
    if not source_context_path or not source_context_path.is_file():
        return {
            "schema_version": "source-operating-model-preservation.v1",
            "status": "not_declared",
            "source_context_declared": False,
            "declared_references": [],
            "present_references": [],
            "missing_references": [],
            "missing_progressive_routes": [],
            "policy": (
                "When source-context declares operating-model source material, "
                "the package must preserve it as package-local references and route "
                "agents to it through Progressive Disclosure."
            ),
        }

    loaded, error = read_structured_reference(source_context_path)
    declared: list[str] = []
    missing: list[str] = []
    missing_routes: list[str] = []
    if error is None and isinstance(loaded, dict):
        references = loaded.get("references")
        if isinstance(references, list):
            for item in references:
                if not isinstance(item, dict):
                    continue
                kind = str(item.get("kind") or "").strip()
                path = str(item.get("path") or "").strip()
                if kind not in SOURCE_OPERATING_MODEL_KINDS or not path:
                    continue
                declared.append(path)
                if not package_local_regular_file(skill_md, path):
                    missing.append(path)
                quoted_path = f"`{path}`"
                if quoted_path not in progressive_body and path not in progressive_body:
                    missing_routes.append(path)
        for path in _source_operating_model_paths_from_text(source_context_path):
            if path in declared:
                continue
            declared.append(path)
            if not package_local_regular_file(skill_md, path):
                missing.append(path)
            quoted_path = f"`{path}`"
            if quoted_path not in progressive_body and path not in progressive_body:
                missing_routes.append(path)
    elif error is not None:
        missing.append("references/source-context.yaml")

    present = [path for path in declared if path not in missing]
    blocked = bool(missing or missing_routes)
    return {
        "schema_version": "source-operating-model-preservation.v1",
        "status": "blocked_validation" if blocked else ("pass" if declared else "not_declared"),
        "source_context_declared": True,
        "source_context_error": error,
        "declared_references": declared,
        "present_references": present,
        "missing_references": missing,
        "missing_progressive_routes": missing_routes,
        "policy": (
            "When source-context declares operating-model source material, "
            "the package must preserve it as package-local references and route "
            "agents to it through Progressive Disclosure."
        ),
    }


def _source_operating_model_paths_from_text(path: Path) -> list[str]:
    """Extract source operating-model paths from source-context.yaml without PyYAML."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    paths: list[str] = []
    current_path: str | None = None
    current_kind: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- path:"):
            if current_path and current_kind in SOURCE_OPERATING_MODEL_KINDS:
                paths.append(current_path)
            current_path = stripped.split(":", 1)[1].strip().strip("'\"")
            current_kind = None
            continue
        if stripped.startswith("kind:"):
            current_kind = stripped.split(":", 1)[1].strip().strip("'\"")
    if current_path and current_kind in SOURCE_OPERATING_MODEL_KINDS:
        paths.append(current_path)
    return [source_path for source_path in paths if source_path]


def progressive_disclosure_contract(
    repo_root: Path | None,
    skill_md: Path | None,
    text: str,
) -> dict[str, Any]:
    """Return deterministic compaction/progressive-disclosure signals."""
    line_count = len(text.splitlines()) if text else 0
    body = markdown_section_body(text, "Progressive Disclosure")
    reference_paths = progressive_disclosure_reference_paths(body)
    missing = missing_progressive_disclosure_references(skill_md, reference_paths)
    existing_count = len(reference_paths) - len(missing)
    compact_entrypoint = bool(text) and line_count <= 250
    near_threshold_line_limit = 220
    over_near_threshold = bool(text) and line_count > near_threshold_line_limit
    section_declared = bool(body)
    references_declared = existing_count > 0
    operating_model_formats = operating_model_format_contract(skill_md, text)
    format_refs_ready = (
        not operating_model_formats["artifacts_declared"]
        or operating_model_formats["format_references_ready"]
    )
    source_operating_model = source_operating_model_contract(skill_md, body)
    source_operating_model_ready = source_operating_model["status"] in {"pass", "not_declared"}
    return {
        "skill_md_line_count": line_count,
        "skill_md_under_500_lines": line_count <= 500 if text else False,
        "skill_md_under_250_lines": compact_entrypoint,
        "skill_md_near_threshold_line_limit": near_threshold_line_limit,
        "skill_md_over_near_threshold": over_near_threshold,
        "progressive_disclosure_declared": section_declared,
        "progressive_disclosure_reference_count": existing_count,
        "progressive_disclosure_missing_references": missing,
        "progressive_disclosure_ready": (
            compact_entrypoint
            and section_declared
            and references_declared
            and not missing
            and format_refs_ready
            and source_operating_model_ready
        ),
        "operating_model_formats": operating_model_formats,
        "source_operating_model": source_operating_model,
        "progressive_disclosure_policy": (
            "Keep SKILL.md as the compact entrypoint and route task-specific "
            "details and source operating-model docs to existing references."
        ),
        "source_path": repo_relative_path(repo_root, skill_md) if repo_root and skill_md else None,
    }
__all__ = [name for name in globals() if not name.startswith("__")]
