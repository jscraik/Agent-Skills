from __future__ import annotations

from .package_contracts_common import *  # noqa: F403

def repo_relative_path(repo_root: Path, path: Path) -> str | None:
    """Return a repo-relative POSIX path when *path* is inside *repo_root*."""
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return None


def codex_skill_package_abi_source() -> dict[str, Any]:
    """Return repo-neutral provenance for the Codex SkillMetadata ABI shape."""
    return {
        "path": CODEX_SKILL_PACKAGE_ABI_SOURCE_PATH,
        "struct": "SkillMetadata",
        "evidence_fields": list(CODEX_SKILL_PACKAGE_ABI_EVIDENCE_FIELDS),
    }


def metadata_value(frontmatter: dict[str, Any], field: str) -> Any:
    """Return a package field from top-level frontmatter or nested metadata."""
    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
    if field == "version":
        return frontmatter.get("version") or metadata.get("version")
    return metadata.get(field) or frontmatter.get(field)


def normalized_list(value: Any) -> list[str]:
    """Normalize package metadata values into a stable string list."""
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, set):
        return sorted(str(item) for item in value if str(item).strip())
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def package_field_values(frontmatter: dict[str, Any]) -> dict[str, Any]:
    """Extract package readiness metadata from skill frontmatter."""
    values = {field: metadata_value(frontmatter, field) for field in PACKAGE_CONTRACT_FIELDS}
    return {
        "version": values.get("version"),
        "compatible_roles": normalized_list(values.get("compatible_roles")),
        "runtime_needs": normalized_list(values.get("runtime_needs")),
        "maturity": values.get("maturity"),
        "provenance": values.get("provenance"),
        "share_readiness": values.get("share_readiness"),
    }


def read_agents_openai_yaml_fields(skill_md: Path | None) -> dict[str, Any]:
    """Extract a conservative agents/openai.yaml contract view."""
    if not skill_md:
        return {}
    agents_openai = skill_md.parent / "agents" / "openai.yaml"
    if not agents_openai.is_file():
        return {}
    try:
        text = agents_openai.read_text(encoding="utf-8")
    except OSError:
        return {}
    if yaml is not None:
        try:
            loaded = yaml.safe_load(text) or {}
        except yaml.YAMLError:
            loaded = {}
        if isinstance(loaded, dict):
            return {str(key): value for key, value in loaded.items()}
    fields: dict[str, Any] = {}
    current_map: str | None = None
    current_nested_key: str | None = None
    current_list_item: dict[str, Any] | None = None
    lines = text.splitlines()
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if current_map and stripped.startswith("- "):
            nested = fields.setdefault(current_map, {})
            if not isinstance(nested, dict):
                continue
            item_text = stripped[2:].strip()
            if not current_nested_key:
                continue
            values = nested.setdefault(current_nested_key, [])
            if not isinstance(values, list):
                values = []
                nested[current_nested_key] = values
            if ":" in item_text:
                item_key, item_value = item_text.split(":", 1)
                current_list_item = {
                    item_key.strip(): parse_frontmatter_scalar(item_value.strip())
                }
                values.append(current_list_item)
            else:
                values.append(parse_frontmatter_scalar(item_text))
                current_list_item = None
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if indent == 0:
            if value:
                fields[key] = parse_frontmatter_scalar(value)
                current_map = None
                current_nested_key = None
                current_list_item = None
            else:
                fields[key] = {}
                current_map = key
                current_nested_key = None
                current_list_item = None
            continue
        if current_map:
            nested = fields.setdefault(current_map, {})
            if not isinstance(nested, dict):
                continue
            if current_list_item is not None and indent >= 4 and value:
                current_list_item[key] = parse_frontmatter_scalar(value)
                continue
            if value:
                nested[key] = parse_frontmatter_scalar(value)
                current_nested_key = None
                current_list_item = None
            else:
                nested[key] = []
                current_nested_key = key
                current_list_item = None
    return fields


def read_reference_contract(skill_md: Path | None) -> dict[str, Any]:
    """Return references/contract.yaml when the skill declares a richer contract."""
    if not skill_md:
        return {}
    contract_path = skill_md.parent / "references" / "contract.yaml"
    if not contract_path.is_file():
        return {}
    try:
        text = contract_path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if yaml is None:
        json_loaded = read_json_like_yaml_reference(text)
        if isinstance(json_loaded, dict):
            return json_loaded
        ruby_loaded = read_yaml_with_ruby(text)
        if isinstance(ruby_loaded, dict):
            return ruby_loaded
        return read_reference_contract_fallback(text)
    try:
        loaded = yaml.safe_load(text) or {}
    except yaml.YAMLError:
        return read_reference_contract_fallback(text)
    return loaded if isinstance(loaded, dict) else {}


def read_structured_reference(path: Path) -> tuple[dict[str, Any] | list[Any] | None, str | None]:
    """Read a JSON/YAML reference file and return structured data plus an error."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, str(exc)
    suffix = path.suffix.lower()
    if suffix == ".json":
        try:
            import json

            loaded = json.loads(text)
        except (OSError, ValueError) as exc:
            return None, str(exc)
        if isinstance(loaded, (dict, list)):
            return loaded, None
        return None, "structured reference must parse to an object or list"
    if suffix in {".yaml", ".yml"}:
        if yaml is None:
            json_loaded = read_json_like_yaml_reference(text)
            if isinstance(json_loaded, (dict, list)):
                return json_loaded, None
            ruby_loaded = read_yaml_with_ruby(text)
            if isinstance(ruby_loaded, (dict, list)):
                return ruby_loaded, None
            loaded = read_structured_reference_fallback(text)
            return loaded, None
        try:
            loaded = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            return None, str(exc)
        if isinstance(loaded, (dict, list)):
            return loaded, None
        return None, "structured reference must parse to an object or list"
    return None, None


def read_json_like_yaml_reference(text: str) -> dict[str, Any] | list[Any] | None:
    stripped = text.lstrip()
    if not stripped.startswith(("{", "[")):
        return None
    try:
        loaded = json.loads(text)
    except ValueError:
        return None
    return loaded if isinstance(loaded, (dict, list)) else None


def read_yaml_with_ruby(text: str) -> dict[str, Any] | list[Any] | None:
    """Parse YAML with Ruby stdlib when PyYAML is unavailable."""
    code = "require 'yaml'; require 'json'; print JSON.generate(YAML.safe_load(STDIN.read, permitted_classes: [], aliases: false))"
    try:
        completed = subprocess.run(
            ["ruby", "-e", code],
            input=text,
            text=True,
            capture_output=True,
            check=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    try:
        loaded = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return None
    return loaded if isinstance(loaded, (dict, list)) else None


def read_structured_reference_fallback(text: str) -> dict[str, Any]:
    """Parse enough top-level YAML shape for reference presence checks.

    This is intentionally not a general YAML parser. It lets the public ask
    wrapper validate reference-quality core fields in Python runtimes where
    PyYAML is unavailable.
    """
    fields: dict[str, Any] = {}
    current_sequence_key: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped == "---" or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent == 0 and not stripped.startswith("- ") and ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value:
                fields[key] = parse_frontmatter_scalar(value)
                current_sequence_key = None
            else:
                fields[key] = []
                current_sequence_key = key
            continue
        if current_sequence_key and stripped.startswith("- "):
            values = fields.setdefault(current_sequence_key, [])
            if not isinstance(values, list):
                values = []
                fields[current_sequence_key] = values
            values.append(parse_frontmatter_scalar(stripped[2:].strip()))
    return fields


def read_reference_contract_fallback(text: str) -> dict[str, Any]:
    """Parse the simple nested YAML fields used by references/contract.yaml."""
    meaningful_lines = [
        line for line in text.splitlines() if line.strip() and not line.strip().startswith("#")
    ]
    fields: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any] | list[Any]]] = [(-1, fields)]
    for index, line in enumerate(meaningful_lines):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if stripped.startswith("- "):
            if isinstance(parent, list):
                parent.append(parse_frontmatter_scalar(stripped[2:].strip()))
            continue
        if ":" not in stripped or not isinstance(parent, dict):
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value:
            parent[key] = parse_frontmatter_scalar(value)
            continue
        next_is_list = False
        if index + 1 < len(meaningful_lines):
            next_line = meaningful_lines[index + 1]
            next_indent = len(next_line) - len(next_line.lstrip(" "))
            next_is_list = next_indent > indent and next_line.strip().startswith("- ")
        child: dict[str, Any] | list[Any] = [] if next_is_list else {}
        parent[key] = child
        stack.append((indent, child))
    return fields


def _contract_sequence_contains(contract: dict[str, Any], field: str, value: str) -> bool:
    """Return whether a simple contract sequence contains a string value."""
    values = contract.get(field)
    return isinstance(values, list) and value in {item for item in values if isinstance(item, str)}


def _capability_selector_fields(contract: dict[str, Any]) -> dict[str, str]:
    """Return selector keys and expected input/output field names."""
    quality_criteria = contract.get("quality_criteria")
    selectors: dict[str, str] = {}
    if isinstance(quality_criteria, dict):
        for key, value in quality_criteria.items():
            if key.endswith("_selection") and isinstance(value, dict) and value:
                selectors[key] = key.removesuffix("_selection")
    capability_selection = contract.get("capability_selection")
    if isinstance(capability_selection, dict) and capability_selection:
        selectors.setdefault("capability_selection", "capability")
    return selectors


def _contract_rubric_profile_ids(contract: dict[str, Any]) -> list[str]:
    """Return declared centralized rubric profile ids."""
    value = contract.get("rubric_profiles", contract.get("rubric_profile"))
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def _central_rubric_profiles(
    repo_root: Path | None,
    contract: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], list[str], list[str]]:
    """Load centralized Skills SDK rubric profiles declared by a contract."""
    profiles: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    profile_ids = _contract_rubric_profile_ids(contract)
    for profile_id in profile_ids:
        rel_path = CENTRAL_RUBRIC_PROFILES.get(profile_id)
        if not rel_path:
            errors.append(f"rubric_profile.{profile_id}:unknown")
            continue
        if repo_root is None:
            errors.append(f"rubric_profile.{profile_id}:repo_root_unavailable")
            continue
        loaded, error = read_structured_reference(repo_root / rel_path)
        if error is not None:
            errors.append(f"rubric_profile.{profile_id}:{error}")
            continue
        if not isinstance(loaded, dict):
            errors.append(f"rubric_profile.{profile_id}:invalid_shape")
            continue
        if str(loaded.get("rubric_id") or "") != profile_id:
            errors.append(f"rubric_profile.{profile_id}:rubric_id_mismatch")
            continue
        profiles[profile_id] = loaded
    return profiles, errors, profile_ids


def _combined_rubric_quality_criteria(
    repo_root: Path | None,
    contract: dict[str, Any],
) -> tuple[dict[str, Any], list[str], list[str], list[str]]:
    """Merge centralized rubric criteria with skill-local selector/override criteria."""
    central_profiles, profile_errors, profile_ids = _central_rubric_profiles(repo_root, contract)
    combined: dict[str, Any] = {}
    automatic_failures: list[str] = []
    for profile in central_profiles.values():
        profile_criteria = profile.get("quality_criteria")
        if isinstance(profile_criteria, dict):
            combined.update(profile_criteria)
        profile_failures = profile.get("automatic_failure_conditions")
        if isinstance(profile_failures, list):
            automatic_failures.extend(str(item) for item in profile_failures if str(item).strip())
    local_criteria = contract.get("quality_criteria")
    if isinstance(local_criteria, dict):
        combined.update(local_criteria)
    local_failures = contract.get("automatic_failure_conditions")
    if isinstance(local_failures, list):
        automatic_failures.extend(str(item) for item in local_failures if str(item).strip())
    return combined, automatic_failures, profile_errors, profile_ids


def _basic_requirement_rubric_check(
    contract: dict[str, Any],
    selectors: dict[str, str],
    repo_root: Path | None = None,
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    """Return whether the reference contract defines observable skill success."""
    evidence_requirements = contract.get("evidence_requirements")
    quality_criteria, _automatic_failures, profile_errors, profile_ids = _combined_rubric_quality_criteria(
        repo_root,
        contract,
    )
    missing: list[str] = []
    quality_keys: list[str] = []
    selector_keys: list[str] = []

    has_quality = isinstance(quality_criteria, dict) and quality_criteria
    has_evidence = isinstance(evidence_requirements, list) and [
        item for item in evidence_requirements if isinstance(item, str) and item.strip()
    ]

    if not has_quality:
        missing.append("quality_criteria")
    else:
        quality_keys = sorted(str(key) for key in quality_criteria)
        selector_keys = sorted(key for key in quality_keys if key.endswith("_selection"))
        observable_quality_keys = [key for key in quality_keys if not key.endswith("_selection")]
        if not observable_quality_keys:
            missing.append("quality_criteria.observable_success")
        for selector_key in selectors:
            if selector_key not in quality_criteria and not contract.get(selector_key):
                missing.append(f"quality_criteria.{selector_key}")

    missing.extend(profile_errors)

    if not has_evidence:
        missing.append("evidence_requirements")

    check = {
        "name": "basic_requirement_rubric",
        "status": "pass" if not missing else "blocked_validation",
        "path": "references/contract.yaml",
        "missing": missing,
        "quality_criteria": quality_keys,
        "selector_criteria": selector_keys,
        "rubric_profiles": profile_ids,
        "policy": (
            "Every Skills SDK contract must define observable quality criteria "
            "and evidence requirements for the skill's basic job before handoff."
        ),
    }
    blockers = []
    if missing:
        blockers.append(
            {
                "rule_id": "basic_requirement_rubric_missing",
                "path": "references/contract.yaml",
                "message": (
                    "references/contract.yaml must declare quality_criteria and "
                    "evidence_requirements so package verification can score the "
                    "skill's basic requirement before Tessl handoff."
                ),
            }
        )
    return check, blockers


ANALYTIC_RUBRIC_FIELDS = frozenset({
    "purpose",
    "why_it_matters",
    "observable_evidence",
    "scoring",
})
ANALYTIC_RUBRIC_SCORES = frozenset({"5", "4", "3", "2", "1"})


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
            if not isinstance(value, dict) or not value:
                findings.append(f"quality_criteria.{criterion_id}:analytic_mapping_required")
                continue
            missing_fields = sorted(field for field in ANALYTIC_RUBRIC_FIELDS if field not in value)
            findings.extend(f"quality_criteria.{criterion_id}.{field}" for field in missing_fields)
            for field in ("purpose", "why_it_matters"):
                if field in value and (not isinstance(value.get(field), str) or not str(value.get(field)).strip()):
                    findings.append(f"quality_criteria.{criterion_id}.{field}:nonempty_string_required")
            observable_evidence = value.get("observable_evidence")
            if "observable_evidence" in value and not (
                (isinstance(observable_evidence, str) and observable_evidence.strip())
                or (
                    isinstance(observable_evidence, list)
                    and any(isinstance(item, str) and item.strip() for item in observable_evidence)
                )
            ):
                findings.append(
                    f"quality_criteria.{criterion_id}.observable_evidence:nonempty_string_or_list_required"
                )
            scoring = value.get("scoring")
            if not isinstance(scoring, dict) or not scoring:
                continue
            score_keys = {str(score_key) for score_key in scoring}
            missing_scores = sorted(ANALYTIC_RUBRIC_SCORES - score_keys, reverse=True)
            findings.extend(f"quality_criteria.{criterion_id}.scoring.{score}" for score in missing_scores)
            for score_key, score_value in scoring.items():
                if not isinstance(score_value, str) or not score_value.strip():
                    findings.append(f"quality_criteria.{criterion_id}.scoring.{score_key}:nonempty_string_required")

    if not checked:
        findings.append("quality_criteria.observable_analytic_criterion")
    findings.extend(profile_errors)
    if not [item for item in automatic_failures if isinstance(item, str) and item.strip()]:
        findings.append("automatic_failure_conditions")

    check = {
        "name": "analytic_rubric_quality",
        "status": "pass" if not findings else "blocked_validation",
        "path": "references/contract.yaml",
        "criteria_checked": sorted(checked),
        "missing": sorted(findings),
        "rubric_profiles": profile_ids,
        "policy": (
            "Skills SDK rubric criteria must use an analytic rubric shape. "
            "Shared criteria may come from centralized rubric_profile entries; "
            "skill-local criteria should only add selectors or domain-specific overrides."
        ),
    }
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

__all__ = [name for name in globals() if not name.startswith("__")]
