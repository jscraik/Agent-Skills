from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
from typing import Any

from ask.skills_sdk.contracts import (
    CODEX_SKILL_PACKAGE_FIELDS,
    CODEX_SKILL_PACKAGE_FRONTMATTER_FIELDS,
    PACKAGE_CONTRACT_FIELDS,
    parse_frontmatter_scalar,
)

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - exercised only in minimal runtimes
    yaml = None


SKILL_PACKAGE_SCHEMA_VERSION = "skill-package.v1"
SKILL_PACKAGE_READINESS_SCHEMA_VERSION = "skill-package-readiness.v1"
SKILL_PACKAGE_COMPATIBILITY_SNAPSHOT_ID = "skill-package-readiness.v1.public-output.2026-05-23"
SKILL_PACKAGE_SCHEMA_PATH = "Infrastructure/config/schemas/skill-package.v1.schema.json"
SKILL_PACKAGE_READINESS_SCHEMA_PATH = "Infrastructure/config/schemas/skill-package-readiness.v1.schema.json"
SKILLFLOW_SCHEMA_VERSION = "skillflow.v1"
SKILLFLOW_SCHEMA_PATH = "Infrastructure/config/schemas/skillflow.v1.schema.json"
SKILL_OPTIMIZATION_CONTRACT_SCHEMA_VERSION = "skill-optimization-contract.v1"
SKILL_OPTIMIZATION_CONTRACT_SCHEMA_PATH = (
    "Infrastructure/config/schemas/skill-optimization-contract.v1.schema.json"
)
SKILL_PACKAGE_SNAPSHOT_PATH = (
    "Infrastructure/tests/fixtures/skill_package_snapshots/"
    "skill-package-readiness-public-output.v1.json"
)
CODEX_SKILL_PACKAGE_ABI_SOURCE_PATH = "codex-rs/core-skills/src/model.rs"
CODEX_SKILL_PACKAGE_ABI_EVIDENCE_FIELDS: tuple[str, ...] = CODEX_SKILL_PACKAGE_FRONTMATTER_FIELDS
CODEX_SKILL_PACKAGE_REQUIRED_FIELDS: tuple[str, ...] = tuple(
    field for field, required in CODEX_SKILL_PACKAGE_FIELDS if required
)
CODEX_SKILL_PACKAGE_OPTIONAL_FIELDS: tuple[str, ...] = tuple(
    field for field, required in CODEX_SKILL_PACKAGE_FIELDS if not required
)
SDK_PACKAGE_CONTRACT_SCHEMA_VERSION = "skill-sdk-contract.v1"
SDK_PACKAGE_CONTRACT_FIELDS: tuple[str, ...] = (
    "agent_metadata",
    "reference_contract",
    "reference_quality",
    "writing_quality",
    "openai_platform_compat",
    "purpose",
    "inputs",
    "outputs",
    "commands",
    "permission_profile",
    "portability_profile",
    "evals",
    "task_profile",
    "evidence_policy",
    "optimization_contract",
)
SDK_PACKAGE_ADVISORY_CONTRACT_FIELDS: tuple[str, ...] = (
    "budget_classification",
)
OPERATING_MODEL_FORMAT_DOCS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("MISSION.md", ("MISSION.md",), "references/mission-format.md"),
    ("RESOURCES.md", ("RESOURCES.md",), "references/resources-format.md"),
    ("GLOSSARY.md", ("GLOSSARY.md",), "references/glossary-format.md"),
    (
        "learning-records/",
        ("learning-records/", "learning-records/*.md"),
        "references/learning-record-format.md",
    ),
)
SOURCE_OPERATING_MODEL_KINDS: set[str] = {
    "source_operating_model",
    "operating_model_source",
    "operating_model_reference",
    "operating_model_format",
}
PACKAGE_IGNORED_FILE_NAMES: set[str] = {".DS_Store", "Thumbs.db", "desktop.ini"}
CENTRAL_RUBRIC_PROFILES: dict[str, str] = {
    "skills-sdk.gold-standard.v1": "Infrastructure/config/skills-sdk/gold-standard-rubric.v1.json",
}
OPENAI_PLATFORM_COMPAT_SCHEMA_VERSION = "skills-sdk.openai-platform-compat.v1"
SKILLFLOW_NODE_TYPES: set[str] = {
    "command",
    "llm",
    "router",
    "validator",
    "human_gate",
    "subflow",
}
SKILLFLOW_EXECUTION_MODES: set[str] = {
    "prose",
    "deterministic_flow",
    "hybrid",
}
OPTIMIZATION_MODES: set[str] = {"bounded_patch", "reviewed_rewrite"}
OPTIMIZATION_EDIT_MODES: set[str] = {"patch", "reviewed_rewrite"}
OPTIMIZATION_EDIT_OPERATIONS: set[str] = {"add", "delete", "replace"}
OPTIMIZATION_ACCEPTANCE_RULES: set[str] = {"strict_improvement", "min_delta"}
OPTIMIZATION_TIE_POLICIES: set[str] = {"reject", "allow_with_review"}
OPTIMIZATION_GUARD_FAILURE_POLICIES: set[str] = {"discard", "block"}
OPTIMIZATION_METRIC_DIRECTIONS: set[str] = {"maximize", "minimize"}
OPTIMIZATION_SPLIT_ROLES: dict[str, str] = {
    "train": "proposal_generation",
    "selection": "candidate_acceptance",
    "test": "final_report_only",
}
PACKAGE_FILE_STEM_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SKILL_DESCRIPTION_HANDLE_RE = re.compile(r"\$[A-Za-z][A-Za-z0-9_-]*")
GENERIC_PACKAGE_FILE_STEMS = {"details", "misc", "notes", "scratch", "todo", "tmp"}
GENERIC_REFERENCE_HEADING_TERMS = {
    "details",
    "misc",
    "notes",
    "overview",
    "reference",
    "scratch",
    "todo",
    "tmp",
}
DESCRIPTION_ACTION_TERMS = {
    "audit",
    "build",
    "check",
    "create",
    "debug",
    "diagnose",
    "evaluate",
    "fix",
    "generate",
    "harden",
    "install",
    "plan",
    "prepare",
    "review",
    "run",
    "sync",
    "update",
    "use",
    "validate",
}
CONSTRUCTION_OBLIGATION_TERMS = DESCRIPTION_ACTION_TERMS | {
    "accept",
    "ask",
    "block",
    "choose",
    "classify",
    "collect",
    "compare",
    "decide",
    "decline",
    "fail",
    "gather",
    "link",
    "load",
    "map",
    "open",
    "produce",
    "read",
    "refuse",
    "route",
    "select",
    "stop",
}
CONSTRUCTION_TRIGGER_BOUNDARY_TERMS = {
    "avoid",
    "boundary",
    "delegate",
    "except",
    "handoff",
    "instead",
    "never",
    "not",
    "only",
    "outside",
    "refuse",
    "unless",
    "when",
}
CONSTRUCTION_PHASE_TERMS = {
    "after",
    "before",
    "block",
    "blocked",
    "gate",
    "gated",
    "phase",
    "step",
    "stop",
    "validate",
}
CONSTRUCTION_GENERIC_TRIGGER_TERMS = {
    "anything",
    "everything",
    "general",
    "misc",
    "stuff",
    "things",
}
CONSTRUCTION_SEDIMENT_WORD_LIMIT = 55
CONSTRUCTION_DUPLICATE_LINE_WORD_LIMIT = 8


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

    # Check field presence (exists in contract) vs emptiness (present but no content)
    quality_present = "quality_criteria" in contract or bool(profile_ids)
    evidence_present = "evidence_requirements" in contract

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


ANALYTIC_RUBRIC_FIELDS = {
    "purpose",
    "why_it_matters",
    "observable_evidence",
    "scoring",
}
ANALYTIC_RUBRIC_SCORES = {"5", "4", "3", "2", "1"}


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


def package_file_stem_ok(path: Path) -> bool:
    """Return whether a package support filename uses purpose-readable kebab-case."""
    return bool(PACKAGE_FILE_STEM_RE.fullmatch(path.stem))


def text_contains_action_term(text: str) -> bool:
    """Return whether text contains a deterministic natural-action trigger term."""
    tokens = {token.strip(".,:;!?()[]{}\"'").lower() for token in text.split()}
    return bool(tokens & DESCRIPTION_ACTION_TERMS)


def markdown_has_title(text: str) -> bool:
    """Return whether markdown text declares a top-level title."""
    return any(line.startswith("# ") and line[2:].strip() for line in text.splitlines())


def markdown_title(text: str) -> str:
    """Return the first top-level markdown title."""
    for line in text.splitlines():
        if line.startswith("# ") and line[2:].strip():
            return line[2:].strip()
    return ""


def markdown_reference_heading_weak(path: Path, text: str) -> bool:
    """Return whether a markdown reference title is too generic to route reliably."""
    title = markdown_title(text)
    if not title:
        return True
    title_tokens = _token_set(title)
    if not title_tokens:
        return True
    if title_tokens.issubset(GENERIC_REFERENCE_HEADING_TERMS):
        return True
    stem_tokens = _token_set(path.stem)
    meaningful_stem_tokens = stem_tokens - GENERIC_REFERENCE_HEADING_TERMS
    meaningful_title_tokens = title_tokens - GENERIC_REFERENCE_HEADING_TERMS
    if meaningful_stem_tokens and not (meaningful_stem_tokens & meaningful_title_tokens):
        return True
    return False


def structured_reference_has_description(path: Path, text: str) -> bool:
    """Return whether a structured reference has a browseable purpose marker."""
    if path.suffix.lower() == ".json":
        return '"description"' in text or '"purpose"' in text or '"schema_version"' in text
    if path.suffix.lower() == ".jsonl":
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                return False
            if not isinstance(record, dict):
                return False
            return any(str(record.get(field) or "").strip() for field in ("description", "purpose", "schema_version"))
        return False
    return bool(re.search(r"(?m)^(description|purpose|schema_version|name):\s*\S", text))


def script_has_description(text: str) -> bool:
    """Return whether script header comments or docstrings describe purpose/usage."""
    lines = text.splitlines()[:25]
    for index, line in enumerate(lines):
        stripped = line.strip().lower()
        if not stripped or stripped.startswith("#!"):
            continue
        if stripped.startswith("#") and any(
            marker in stripped for marker in ("description", "purpose", "usage")
        ):
            return True
        if stripped.startswith(("\"\"\"", "'''")) and any(
            marker in _leading_docstring_text(lines[index:]) for marker in ("description", "purpose", "usage")
        ):
            return True
        if stripped.startswith(("import ", "from ", "print(", "def ", "class ")):
            return False
    return False


def _leading_docstring_text(lines: list[str]) -> str:
    quote = lines[0].strip()[:3]
    body: list[str] = []
    for line in lines:
        body.append(line.strip().lower())
        if len(body) > 1 and quote in line:
            break
        if len(body) == 1 and line.strip().lower().count(quote) >= 2:
            break
    return "\n".join(body)


def support_file_has_description(path: Path) -> bool:
    """Return whether a reference or script carries deterministic browseability text."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    suffix = path.suffix.lower()
    if suffix == ".md":
        return markdown_has_title(text)
    if suffix in {".yaml", ".yml", ".json", ".jsonl"}:
        return structured_reference_has_description(path, text)
    if suffix == ".txt":
        return bool(text.strip())
    if path.parts and "scripts" in path.parts:
        return script_has_description(text)
    return False


def iter_support_files(skill_md: Path | None, folder: str) -> list[Path]:
    """Return package support files under references/ or scripts/."""
    if not skill_md:
        return []
    root = skill_md.parent / folder
    if not root.is_dir() or root.is_symlink():
        return []
    return sorted(
        path
        for path in root.rglob("*")
        if path.name not in PACKAGE_IGNORED_FILE_NAMES
        if package_local_regular_file(skill_md, path.relative_to(skill_md.parent).as_posix())
    )


def unsafe_support_files(skill_md: Path | None, folder: str) -> list[Path]:
    """Return support paths that must not be read as package evidence."""
    if not skill_md:
        return []
    root = skill_md.parent / folder
    if root.is_symlink():
        return [root]
    if not root.is_dir():
        return []
    return sorted(
        path
        for path in root.rglob("*")
        if path.name not in PACKAGE_IGNORED_FILE_NAMES
        if path.is_symlink()
        or (path.is_file() and not package_local_regular_file(skill_md, path.relative_to(skill_md.parent).as_posix()))
    )


def package_path_label(repo_root: Path | None, path: Path) -> str:
    """Return a repo-relative label without resolving symlink leaves."""
    if repo_root:
        try:
            return path.relative_to(repo_root).as_posix()
        except ValueError:
            pass
    return path.as_posix()


def support_file_inventory(
    repo_root: Path | None,
    skill_md: Path | None,
    folder: str,
) -> dict[str, Any]:
    """Return deterministic naming and browseability checks for support files."""
    files = iter_support_files(skill_md, folder)
    unsafe_paths = unsafe_support_files(skill_md, folder)
    bad_names = [path for path in files if not package_file_stem_ok(path)]
    generic_names = [path for path in files if path.stem.lower() in GENERIC_PACKAGE_FILE_STEMS]
    missing_descriptions = [path for path in files if not support_file_has_description(path)]
    weak_headings: list[Path] = []
    if folder == "references":
        for path in files:
            if path.suffix.lower() != ".md":
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                weak_headings.append(path)
                continue
            if markdown_reference_heading_weak(path, text):
                weak_headings.append(path)
    return {
        "count": len(files),
        "filenames_kebab_case": not bad_names,
        "generic_names": [repo_relative_path(repo_root, path) or path.as_posix() for path in generic_names],
        "missing_descriptions": [
            repo_relative_path(repo_root, path) or path.as_posix() for path in missing_descriptions
        ],
        "weak_headings": [
            repo_relative_path(repo_root, path) or path.as_posix() for path in weak_headings
        ],
        "description_coverage_count": len(files) - len(missing_descriptions),
        "ready": (
            not unsafe_paths
            and not bad_names
            and not generic_names
            and not missing_descriptions
            and not weak_headings
        ),
        "bad_names": [repo_relative_path(repo_root, path) or path.as_posix() for path in bad_names],
        "unsafe_paths": [package_path_label(repo_root, path) for path in unsafe_paths],
    }


def skill_identity_contract(
    repo_root: Path | None,
    skill_md: Path | None,
    frontmatter: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic naming and description signals for a skill package."""
    name = str(frontmatter.get("name") or "").strip()
    description = str(frontmatter.get("description") or "").strip()
    short_description = str(metadata_value(frontmatter, "short_description") or "").strip()
    directory_name = skill_md.parent.name if skill_md else ""
    name_present = bool(name)
    name_kebab_case = bool(PACKAGE_FILE_STEM_RE.fullmatch(name))
    name_matches_directory = bool(name and directory_name and name == directory_name)
    description_present = bool(description)
    description_length_ok = 40 <= len(description) <= 420
    description_no_command_handles = not SKILL_DESCRIPTION_HANDLE_RE.search(description)
    description_has_action_term = text_contains_action_term(description)
    short_description_length_ok = not short_description or len(short_description) <= 80
    return {
        "name": name,
        "directory_name": directory_name,
        "source_path": repo_relative_path(repo_root, skill_md) if repo_root and skill_md else None,
        "name_present": name_present,
        "name_kebab_case": name_kebab_case,
        "name_matches_directory": name_matches_directory,
        "description_present": description_present,
        "description_length_chars": len(description),
        "description_length_ok": description_length_ok,
        "description_no_command_handles": description_no_command_handles,
        "description_has_action_term": description_has_action_term,
        "short_description_length_ok": short_description_length_ok,
        "ready": all(
            (
                name_present,
                name_kebab_case,
                name_matches_directory,
                description_present,
                description_length_ok,
                description_no_command_handles,
                description_has_action_term,
                short_description_length_ok,
            )
        ),
    }


def identity_and_assets_contract(
    repo_root: Path | None,
    skill_md: Path | None,
    frontmatter: dict[str, Any],
) -> dict[str, Any]:
    """Return SDK advisory checks for skill identity and support asset browseability."""
    skill_identity = skill_identity_contract(repo_root, skill_md, frontmatter)
    references = support_file_inventory(repo_root, skill_md, "references")
    scripts = support_file_inventory(repo_root, skill_md, "scripts")
    return {
        "schema_version": "skill-identity-assets.v1",
        "policy": (
            "Skill names should be stable kebab-case handles; descriptions should use natural "
            "action-trigger language; references and scripts should be purpose-named and browseable."
        ),
        "skill_identity": skill_identity,
        "reference_inventory": references,
        "script_inventory": scripts,
        "ready": skill_identity["ready"] and references["ready"] and scripts["ready"],
    }


def knowledge_capsule_first_party_contract(repo_root: Path | None, skill_md: Path | None, text: str) -> dict[str, Any]:
    """Return whether vendored knowledge capsules are surfaced through first-party skill references."""
    references_dir = skill_md.parent / "references" if skill_md else None
    manifest_path = references_dir / "knowledge-capsule.manifest.yaml" if references_dir else None
    routing_path = references_dir / "knowledge-capsule-routing.md" if references_dir else None
    manifest_declared = bool(manifest_path and (manifest_path.is_file() or manifest_path.is_symlink()))
    manifest_safe = bool(skill_md and package_local_regular_file(skill_md, "references/knowledge-capsule.manifest.yaml"))
    capsule_paths: list[str] = []
    if manifest_safe and manifest_path:
        manifest, error = read_structured_reference(manifest_path)
        if error is None and isinstance(manifest, dict):
            capsules = manifest.get("capsules")
            if isinstance(capsules, list):
                capsule_paths = _knowledge_capsule_target_paths(capsules)
        if not capsule_paths:
            capsule_paths = _knowledge_capsule_target_paths_from_text(manifest_path)
    unsafe_capsule_paths = [path for path in capsule_paths if not package_local_reference_path(path)]
    routing_declared = bool(routing_path and (routing_path.is_file() or routing_path.is_symlink()))
    routing_safe = bool(skill_md and package_local_regular_file(skill_md, "references/knowledge-capsule-routing.md"))
    routing_text = skill_markdown_text(routing_path) if routing_safe and routing_path else ""
    missing_from_routing = [
        path for path in capsule_paths
        if routing_declared and path and path not in routing_text
    ]
    contract_path = skill_md.parent / "references" / "contract.yaml" if skill_md else None
    contract_mentions_routing = (
        bool(contract_path and contract_path.is_file())
        and "knowledge-capsule-routing.md" in skill_markdown_text(contract_path)
    )
    skill_mentions_routing = "knowledge-capsule-routing.md" in text or contract_mentions_routing
    ready = (
        not manifest_declared
        or (
            routing_declared
            and manifest_safe
            and routing_safe
            and skill_mentions_routing
            and bool(capsule_paths)
            and not unsafe_capsule_paths
            and not missing_from_routing
        )
    )
    return {
        "schema_version": "skill-knowledge-capsule-first-party.v1",
        "status": "pass" if ready else "advisory",
        "manifest_declared": manifest_declared,
        "manifest_path": repo_relative_path(repo_root, manifest_path) if repo_root and manifest_path else None,
        "capsule_count": len(capsule_paths),
        "capsule_paths": capsule_paths,
        "unsafe_capsule_paths": unsafe_capsule_paths,
        "first_party_routing_path": (
            repo_relative_path(repo_root, routing_path) if repo_root and routing_path else None
        ),
        "first_party_routing_declared": routing_declared,
        "first_party_routing_safe": routing_safe,
        "manifest_safe": manifest_safe,
        "skill_mentions_first_party_routing": skill_mentions_routing,
        "contract_mentions_first_party_routing": contract_mentions_routing,
        "missing_from_first_party_routing": missing_from_routing,
        "ready": ready,
        "policy": (
            "Knowledge capsule manifests select bounded generated capsules, but capsule use rules should be "
            "promoted into a first-party skill reference so agents see them without relying on buried capsule text."
        ),
    }


def _knowledge_capsule_target_paths(capsules: list[Any]) -> list[str]:
    paths: list[str] = []
    for capsule in capsules:
        if isinstance(capsule, dict) and isinstance(capsule.get("target_path"), str):
            paths.append(capsule["target_path"].strip())
        elif isinstance(capsule, str) and capsule.strip().startswith("target_path:"):
            paths.append(capsule.split(":", 1)[1].strip())
    return [path for path in paths if path]


def _knowledge_capsule_target_paths_from_text(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    paths: list[str] = []
    for match in re.finditer(r"(?m)^\s*target_path:\s*(.+?)\s*$", text):
        paths.append(match.group(1).strip().strip("'\""))
    return [capsule_path for capsule_path in paths if capsule_path]


def skill_eval_paths(repo_root: Path | None, skill_md: Path | None) -> list[str]:
    """Return portable eval declarations adjacent to a skill package."""
    if not skill_md:
        return []
    candidates = [
        skill_md.parent / "evals" / "evals.json",
        skill_md.parent / "evals" / "evals.yaml",
        skill_md.parent / "references" / "evals.yaml",
    ]
    paths: list[str] = []
    for candidate in candidates:
        if not candidate.is_file():
            continue
        if repo_root:
            paths.append(repo_relative_path(repo_root, candidate) or candidate.as_posix())
        else:
            paths.append(candidate.as_posix())
    return paths


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


def _quality_check(
    name: str,
    status: str,
    *,
    dimension: str,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a stable writing-quality check record."""
    return {
        "name": name,
        "dimension": dimension,
        "status": status,
        "evidence": evidence or {},
    }


def _quality_blocker(
    rule_id: str,
    message: str,
    *,
    dimension: str,
    path: str | None,
    severity: str = "blocked",
) -> dict[str, Any]:
    """Return a stable writing-quality blocker record."""
    return {
        "rule_id": rule_id,
        "dimension": dimension,
        "severity": severity,
        "path": path,
        "message": message,
    }


def _quality_advisory(
    rule_id: str,
    message: str,
    *,
    dimension: str,
    path: str | None,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a stable non-blocking writing-quality advisory record."""
    return {
        "rule_id": rule_id,
        "dimension": dimension,
        "severity": "advisory",
        "path": path,
        "message": message,
        "evidence": evidence or {},
    }


def _frontmatter_bool(frontmatter: dict[str, Any], field: str) -> bool:
    """Return a frontmatter boolean from bools or common string spellings."""
    value = frontmatter.get(field)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return False


def markdown_heading_titles(text: str) -> list[str]:
    """Return normalized markdown heading titles in document order."""
    titles: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        title = stripped.lstrip("#").strip()
        if title:
            titles.append(title)
    return titles


def _has_any_heading(text: str, headings: tuple[str, ...]) -> bool:
    return any(markdown_heading_declared(text, heading) for heading in headings)


def _body_contains_any(body: str, needles: tuple[str, ...]) -> bool:
    lowered = body.lower()
    return any(needle.lower() in lowered for needle in needles)


def _token_set(text: str) -> set[str]:
    """Return normalized natural-language tokens without broad regex parsing."""
    punctuation = ".,:;!?()[]{}\"'<>"
    return {
        token.strip(punctuation).lower()
        for token in text.replace("/", " ").replace("-", " ").split()
        if token.strip(punctuation)
    }


def _skill_body_without_frontmatter(text: str) -> str:
    """Return markdown body text with leading YAML frontmatter removed."""
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                return "\n".join(lines[index + 1 :]).strip()
    return text.strip()


def _construction_step_body(text: str) -> str:
    """Return the combined procedural body used for construction checks."""
    sections: list[str] = []
    for heading in ("Workflow", "Procedure", "Steps"):
        if markdown_heading_declared(text, heading):
            sections.append(markdown_section_body(text, heading))
    return "\n".join(section for section in sections if section.strip())


def _construction_line_items(text: str) -> list[str]:
    """Return non-heading text lines that are likely to carry instructions."""
    items: list[str] = []
    in_code_block = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("\u0060\u0060\u0060"):
            in_code_block = not in_code_block
            continue
        if in_code_block or not line or line.startswith("#"):
            continue
        while line.startswith(("-", "*")):
            line = line[1:].strip()
        if len(line) >= 3 and line[0].isdigit() and line[1] == ".":
            line = line[2:].strip()
        if line:
            items.append(line)
    return items


def _long_paragraphs_without_behavior(text: str) -> list[dict[str, Any]]:
    """Return long prose paragraphs that lack routing, gate, output, or action terms."""
    body = _skill_body_without_frontmatter(text)
    paragraphs: list[str] = []
    current: list[str] = []
    in_code_block = False
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if line.startswith("\u0060\u0060\u0060"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if not line or line.startswith("#") or line.startswith(("-", "*")):
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        current.append(line)
    if current:
        paragraphs.append(" ".join(current))

    findings: list[dict[str, Any]] = []
    for index, paragraph in enumerate(paragraphs, start=1):
        tokens = _token_set(paragraph)
        word_count = len([word for word in paragraph.split() if word.strip()])
        carries_behavior = bool(
            tokens & CONSTRUCTION_OBLIGATION_TERMS
            or tokens & CONSTRUCTION_PHASE_TERMS
            or "references/" in paragraph
            or "Command:" in paragraph
            or "Output Contract" in paragraph
        )
        if word_count >= CONSTRUCTION_SEDIMENT_WORD_LIMIT and not carries_behavior:
            findings.append(
                {
                    "paragraph": index,
                    "word_count": word_count,
                    "preview": paragraph[:120],
                }
            )
    return findings


def _duplicate_instruction_lines(text: str) -> list[dict[str, Any]]:
    """Return repeated instruction-shaped lines that should be deduplicated."""
    seen: dict[str, dict[str, Any]] = {}
    for line_number, item in enumerate(_construction_line_items(text), start=1):
        tokens = _token_set(item)
        if len(tokens) < CONSTRUCTION_DUPLICATE_LINE_WORD_LIMIT:
            continue
        if not (tokens & CONSTRUCTION_OBLIGATION_TERMS or "references/" in item):
            continue
        normalized = " ".join(sorted(tokens))
        if normalized not in seen:
            seen[normalized] = {
                "line_numbers": [],
                "text": item[:120],
            }
        seen[normalized]["line_numbers"].append(line_number)
    duplicates: list[dict[str, Any]] = []
    for record in seen.values():
        if len(record["line_numbers"]) > 1:
            duplicates.append(record)
    return duplicates


def _package_support_files(skill_md: Path | None) -> list[Path]:
    """Return package-local support files that should have a routing pointer."""
    if not skill_md:
        return []
    package_root = skill_md.parent
    support_roots = [
        package_root / "references",
        package_root / "scripts",
        package_root / "assets",
        package_root / "agents",
        package_root / "workflows",
    ]
    files: list[Path] = []
    for root in support_roots:
        if not root.is_dir():
            continue
        for candidate in sorted(path for path in root.rglob("*") if path.is_file()):
            if candidate.name.startswith(".") or candidate.name in PACKAGE_IGNORED_FILE_NAMES:
                continue
            files.append(candidate)
    return files


def _package_text_surfaces(skill_md: Path | None, text: str) -> str:
    """Return the bounded package text used to detect routed support files."""
    if not skill_md:
        return text
    surfaces = [text]
    for relative_path in (
        "agents/openai.yaml",
        "references/contract.yaml",
        "references/evals.yaml",
        "references/knowledge-capsule-routing.md",
        "references/source-provenance.md",
        "references/source-context.yaml",
        "workflows/skillflow.json",
    ):
        candidate = skill_md.parent / relative_path
        if not candidate.is_file():
            continue
        try:
            surfaces.append(candidate.read_text(encoding="utf-8"))
        except OSError:
            continue
    return "\n".join(surfaces)


def _orphaned_support_files(
    repo_root: Path | None,
    skill_md: Path | None,
    text: str,
) -> list[str]:
    """Return support files not mentioned by package entrypoints or contracts."""
    if not skill_md:
        return []
    package_text = _package_text_surfaces(skill_md, text)
    package_root = skill_md.parent
    orphaned: list[str] = []
    implicitly_routed = {
        "agents/openai.yaml",
        "references/contract.yaml",
        "references/evals.yaml",
        "references/knowledge-capsule.manifest.yaml",
        "references/knowledge-demand.yaml",
        "references/task-profile.json",
    }
    for candidate in _package_support_files(skill_md):
        relative = candidate.relative_to(package_root).as_posix()
        if relative in implicitly_routed:
            continue
        if relative in package_text or candidate.name in package_text:
            continue
        orphaned.append(repo_relative_path(repo_root, candidate) if repo_root else relative)
    return [path for path in orphaned if path]


def _package_relative_path(skill_md: Path | None, path: str) -> str:
    """Return a package-relative path when a repo-relative path points into a skill."""
    if not skill_md:
        return path
    package_root = skill_md.parent
    marker = f"{package_root.as_posix()}/"
    if path.startswith(marker):
        return path.removeprefix(marker)
    parts = path.split("/")
    for index, part in enumerate(parts):
        if part == "references":
            return "/".join(parts[index:])
    return path


def _manifest_orphaned_bundle_files(
    repo_root: Path | None,
    skill_md: Path | None,
    text: str,
) -> list[str]:
    """Return bundle support files that must be routed when a capsule manifest exists."""
    if not skill_md:
        return []
    manifest_path = skill_md.parent / "references" / "knowledge-capsule.manifest.yaml"
    if not manifest_path.is_file():
        return []
    orphaned = _orphaned_support_files(repo_root, skill_md, text)
    bundle_paths: list[str] = []
    for path in orphaned:
        package_path = _package_relative_path(skill_md, path)
        if package_path.startswith("references/knowledge-capsules/") or package_path in {
            "references/source-context.yaml",
            "references/source-provenance.md",
        }:
            bundle_paths.append(path)
    return sorted(bundle_paths)


def _review_lens_skill(frontmatter: dict[str, Any], text: str) -> bool:
    """Return whether the skill appears to be a review/audit lens."""
    name = str(frontmatter.get("name") or "")
    description = str(frontmatter.get("description") or "")
    haystack = f"{name} {description} {text}".lower()
    return (
        name.startswith("review-")
        or "review-lens" in name
        or "review lens" in haystack
        or "reviewer lens" in haystack
    )


def _external_input_skill(frontmatter: dict[str, Any], text: str) -> bool:
    """Return whether the skill inspects external or untrusted artifacts."""
    haystack = (
        f"{frontmatter.get('name') or ''} "
        f"{frontmatter.get('description') or ''} {text}"
    ).lower()
    return any(
        needle in haystack
        for needle in (
            "third-party",
            "external skill",
            "untrusted",
            "review a diff",
            "reviewer plugin",
            "intake",
            "fetched",
            "user-provided",
        )
    )


def _improvement_skill(frontmatter: dict[str, Any], text: str) -> bool:
    """Return whether the skill claims to improve or optimize an artifact."""
    tokens = _token_set(
        f"{frontmatter.get('name') or ''} {frontmatter.get('description') or ''} {text}"
    )
    return bool(tokens & {"improve", "improving", "optimize", "optimization", "repair"})


def _writing_quality_advisories(
    repo_root: Path | None,
    skill_md: Path | None,
    frontmatter: dict[str, Any],
    text: str,
    *,
    user_invoked: bool,
    description: str,
    procedural: bool,
    source_path: str | None,
) -> list[dict[str, Any]]:
    """Return Tessl-derived advisory rubric findings for skill writing quality."""
    advisories: list[dict[str, Any]] = []
    description_tokens = _token_set(description)
    action_terms = sorted(description_tokens & DESCRIPTION_ACTION_TERMS)
    if not user_invoked and description:
        if len(description_tokens) < 8 or not action_terms:
            advisories.append(
                _quality_advisory(
                    "description_specificity_weak",
                    "Description should name concrete capabilities rather than vague skill identity.",
                    dimension="invocation",
                    path=source_path,
                    evidence={
                        "token_count": len(description_tokens),
                        "action_terms": action_terms,
                    },
                )
            )
        trigger_markers = {"when", "asks", "mentions", "needs", "wants", "use"}
        if len(description_tokens & trigger_markers) < 2:
            advisories.append(
                _quality_advisory(
                    "description_trigger_terms_missing",
                    "Description should include natural trigger terms a user would actually say.",
                    dimension="invocation",
                    path=source_path,
                    evidence={"trigger_markers": sorted(description_tokens & trigger_markers)},
                )
            )
        conflict_terms = {"help", "helps", "stuff", "things", "tasks", "anything", "everything"}
        if description_tokens & conflict_terms:
            advisories.append(
                _quality_advisory(
                    "description_conflict_risk",
                    "Description includes generic terms that can overlap with other skills.",
                    dimension="invocation",
                    path=source_path,
                    evidence={"generic_terms": sorted(description_tokens & conflict_terms)},
                )
            )

    commands = skill_command_candidates(text)
    workflow_text = "\n".join(
        markdown_section_body(text, heading)
        for heading in ("Workflow", "Procedure", "Steps")
        if markdown_heading_declared(text, heading)
    )
    action_output_terms = {"return", "report", "write", "create", "run", "validate", "emit", "record"}
    if procedural and not commands and not (_token_set(workflow_text) & action_output_terms):
        advisories.append(
            _quality_advisory(
                "content_actionability_weak",
                "Procedural skills should provide concrete commands, artifacts, outputs, or action verbs.",
                dimension="actionability",
                path=source_path,
                evidence={"command_count": len(commands)},
            )
        )

    search_terms = {"search", "inspect", "review", "audit", "compare", "scan"}
    bounded_terms = {"bounded", "budget", "limit", "stop", "first", "few", "narrowest"}
    text_tokens = _token_set(text)
    if text_tokens & search_terms and not (text_tokens & bounded_terms):
        advisories.append(
            _quality_advisory(
                "unbounded_search_instruction",
                "Search, review, or audit skills should declare a stop condition or bounded search budget.",
                dimension="actionability",
                path=source_path,
                evidence={"search_terms": sorted(text_tokens & search_terms)},
            )
        )

    if _review_lens_skill(frontmatter, text):
        missing_review_sections = [
            heading
            for heading in ("Stance", "What to look for", "How to report")
            if not markdown_heading_declared(text, heading)
        ]
        if missing_review_sections:
            advisories.append(
                _quality_advisory(
                    "review_lens_output_contract_missing",
                    "Review-lens skills should declare Stance, What to look for, and How to report sections.",
                    dimension="review_lens",
                    path=source_path,
                    evidence={"missing_sections": missing_review_sections},
                )
            )

    if _external_input_skill(frontmatter, text) and not _body_contains_any(
        text,
        ("treat", "untrusted", "as data", "not instructions", "trust boundary"),
    ):
        advisories.append(
            _quality_advisory(
                "missing_untrusted_input_boundary",
                "Skills that inspect external artifacts should state the untrusted-input boundary.",
                dimension="safety_boundary",
                path=source_path,
            )
        )

    if _improvement_skill(frontmatter, text) and not _body_contains_any(
        text,
        ("baseline", "before", "after", "rerun", "regression"),
    ):
        advisories.append(
            _quality_advisory(
                "improvement_claim_without_before_after_evidence",
                "Improvement skills should require baseline, change, rerun, and regression evidence.",
                dimension="self_improving",
                path=source_path,
            )
        )

    orphaned = _orphaned_support_files(repo_root, skill_md, text)
    if orphaned:
        advisories.append(
            _quality_advisory(
                "orphaned_bundle_reference",
                "Package support files should be routed by SKILL.md or package contracts.",
                dimension="progressive_disclosure",
                path=source_path,
                evidence={"orphaned_paths": orphaned},
            )
        )

    return advisories


def _skill_evals_yaml_path(skill_md: Path | None) -> Path | None:
    if not skill_md:
        return None
    candidate = skill_md.parent / "references" / "evals.yaml"
    return candidate if candidate.is_file() else None


def _case_id(case: Any, index: int) -> str:
    if isinstance(case, dict) and case.get("id"):
        return str(case["id"])
    return f"case[{index}]"


def _scenario_cases_from_reference(
    evals_path: Path,
    loaded: dict[str, Any],
) -> list[Any]:
    """Return eval cases, using a small fallback for nested cases YAML."""
    cases = loaded.get("cases")
    if isinstance(cases, list) and cases and all(isinstance(case, dict) for case in cases):
        return cases
    try:
        text = evals_path.read_text(encoding="utf-8")
    except OSError:
        return cases if isinstance(cases, list) else []
    parsed_cases: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    current_list_key: str | None = None
    in_cases = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped == "---" or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if not in_cases:
            if indent == 0 and stripped == "cases:":
                in_cases = True
            continue
        if indent == 0 and not stripped.startswith("- "):
            break
        if indent in {0, 2} and stripped.startswith("- id:"):
            if current is not None:
                parsed_cases.append(current)
            current = {}
            current_list_key = None
            remainder = stripped[2:].strip()
            if ":" in remainder:
                key, value = remainder.split(":", 1)
                current[key.strip()] = parse_frontmatter_scalar(value.strip())
            continue
        if current is None:
            continue
        if current_list_key and indent >= 2 and stripped.startswith("- "):
            values = current.setdefault(current_list_key, [])
            if isinstance(values, list):
                values.append(parse_frontmatter_scalar(stripped[2:].strip()))
            continue
        if indent >= 2 and ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value:
                current[key] = parse_frontmatter_scalar(value)
                current_list_key = None
            else:
                current[key] = []
                current_list_key = key
    if current is not None:
        parsed_cases.append(current)
    return parsed_cases or (cases if isinstance(cases, list) else [])


def _scenario_alignment_checks(
    repo_root: Path | None,
    skill_md: Path | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return deterministic gold-scenario shape checks for references/evals.yaml."""
    checks: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    evals_path = _skill_evals_yaml_path(skill_md)
    rel_path = repo_relative_path(repo_root, evals_path) if repo_root and evals_path else None
    if evals_path is None:
        checks.append(
            _quality_check(
                "scenario_alignment_declared",
                "not_applicable",
                dimension="scenario_alignment",
                evidence={"path": None, "reason": "references/evals.yaml not declared"},
            )
        )
        return checks, blockers

    loaded, error = read_structured_reference(evals_path)
    if error is not None or not isinstance(loaded, dict):
        checks.append(
            _quality_check(
                "scenario_alignment_parse",
                "blocked_validation",
                dimension="scenario_alignment",
                evidence={"path": rel_path, "error": error or "evals.yaml must be a mapping"},
            )
        )
        blockers.append(
            _quality_blocker(
                "scenario_alignment_unparseable",
                "references/evals.yaml must be parseable before scenario quality can be trusted.",
                dimension="scenario_alignment",
                path=rel_path,
            )
        )
        return checks, blockers

    cases = _scenario_cases_from_reference(evals_path, loaded)
    if not isinstance(cases, list) or not cases:
        checks.append(
            _quality_check(
                "scenario_alignment_cases_declared",
                "blocked_validation",
                dimension="scenario_alignment",
                evidence={"path": rel_path, "case_count": 0},
            )
        )
        blockers.append(
            _quality_blocker(
                "scenario_alignment_cases_missing",
                "references/evals.yaml must declare at least one case before scenario-quality can run.",
                dimension="scenario_alignment",
                path=rel_path,
            )
        )
        return checks, blockers

    missing_by_case: list[dict[str, Any]] = []
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            missing_by_case.append({"case": _case_id(case, index), "missing": ["mapping"]})
            continue
        missing: list[str] = []
        for field in ("id", "category"):
            if not str(case.get(field) or "").strip():
                missing.append(field)
        if not str(case.get("prompt") or case.get("user_task") or "").strip():
            missing.append("prompt_or_user_task")
        if not str(case.get("given") or case.get("why_realistic") or "").strip():
            missing.append("given_or_why_realistic")
        if not str(
            case.get("should")
            or case.get("expected_behavior")
            or case.get("expected_evidence")
            or ""
        ).strip():
            missing.append("should_or_expected_behavior")
        acceptance = case.get("acceptance")
        expected_evidence = case.get("expected_evidence")
        if not (
            isinstance(acceptance, list)
            and acceptance
            or isinstance(expected_evidence, list)
            and expected_evidence
        ):
            missing.append("acceptance_or_expected_evidence")
        if missing:
            missing_by_case.append({"case": _case_id(case, index), "missing": missing})

    status = "blocked_validation" if missing_by_case else "pass"
    checks.append(
        _quality_check(
            "scenario_alignment_gold_shape",
            status,
            dimension="scenario_alignment",
            evidence={
                "path": rel_path,
                "case_count": len(cases),
                "missing_by_case": missing_by_case,
            },
        )
    )
    if missing_by_case:
        blockers.append(
            _quality_blocker(
                "scenario_alignment_gold_shape_incomplete",
                "references/evals.yaml cases must include gold-standard fields: id, category, task, given, should, and acceptance evidence.",
                dimension="scenario_alignment",
                path=rel_path,
            )
        )
    return checks, blockers


def _construction_quality_checks(
    *,
    repo_root: Path | None,
    skill_md: Path | None,
    text: str,
    user_invoked: bool,
    description: str,
    procedural: bool,
    references_count: int,
    missing_references: list[Any],
    source_path: str | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return deterministic construction checks from the Predictability glossary."""
    checks: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []

    description_tokens = _token_set(description)
    trigger_boundaries = sorted(description_tokens & CONSTRUCTION_TRIGGER_BOUNDARY_TERMS)
    generic_trigger_terms = sorted(description_tokens & CONSTRUCTION_GENERIC_TRIGGER_TERMS)
    trigger_status = (
        "not_applicable"
        if user_invoked
        else "pass"
        if description
        and text_contains_action_term(description)
        and "when" in description_tokens
        and not generic_trigger_terms
        else "blocked_validation"
    )
    checks.append(
        _quality_check(
            "construction_trigger_boundary",
            trigger_status,
            dimension="invocation",
            evidence={
                "glossary_axis": "Invocation",
                "root_quality": "Predictability",
                "user_invoked": user_invoked,
                "has_description": bool(description),
                "has_action_term": text_contains_action_term(description),
                "trigger_boundaries": trigger_boundaries,
                "generic_trigger_terms": generic_trigger_terms,
            },
        )
    )
    if trigger_status == "blocked_validation":
        blockers.append(
            _quality_blocker(
                "construction_trigger_boundary_missing",
                "Trigger design must use a concrete action-shaped description and avoid generic catch-all routing terms.",
                dimension="invocation",
                path=source_path,
            )
        )

    step_body = _construction_step_body(text)
    step_tokens = _token_set(step_body)
    step_action_terms = sorted(step_tokens & CONSTRUCTION_OBLIGATION_TERMS)
    references_routed = references_count == 0 or "references/" in text
    structure_status = (
        "pass"
        if procedural and step_action_terms and references_routed and not missing_references
        else "blocked_validation"
    )
    checks.append(
        _quality_check(
            "construction_steps_reference_structure",
            structure_status,
            dimension="information_hierarchy",
            evidence={
                "glossary_axis": "Information Hierarchy",
                "root_quality": "Predictability",
                "procedural_heading_declared": procedural,
                "step_action_terms": step_action_terms,
                "reference_count": references_count,
                "references_routed": references_routed,
                "missing_references": missing_references,
            },
        )
    )
    if structure_status == "blocked_validation":
        blockers.append(
            _quality_blocker(
                "construction_steps_reference_structure_missing",
                "Skill construction must separate Steps from Reference with at least one action-shaped workflow step and routed context pointers.",
                dimension="information_hierarchy",
                path=source_path,
            )
        )

    all_tokens = _token_set(text)
    phase_like = bool(all_tokens & {"phase", "step", "stage", "gate"})
    phase_gate_terms = sorted(all_tokens & CONSTRUCTION_PHASE_TERMS)
    steering_status = (
        "not_applicable"
        if not phase_like
        else "pass"
        if phase_gate_terms and bool(all_tokens & {"before", "after", "stop", "block", "validate", "gate"})
        else "blocked_validation"
    )
    checks.append(
        _quality_check(
            "construction_steering_phase_gate",
            steering_status,
            dimension="steering",
            evidence={
                "glossary_axis": "Steering",
                "root_quality": "Predictability",
                "phase_like": phase_like,
                "phase_gate_terms": phase_gate_terms,
            },
        )
    )
    if steering_status == "blocked_validation":
        blockers.append(
            _quality_blocker(
                "construction_steering_phase_gate_missing",
                "Phase or step-based skills must say what blocks advancement, what evidence is required, or when to stop.",
                dimension="steering",
                path=source_path,
            )
        )

    sediment_paragraphs = _long_paragraphs_without_behavior(text)
    duplicate_lines = _duplicate_instruction_lines(text)
    pruning_status = (
        "pass"
        if not sediment_paragraphs and not duplicate_lines
        else "blocked_validation"
    )
    checks.append(
        _quality_check(
            "construction_pruning_sediment",
            pruning_status,
            dimension="pruning",
            evidence={
                "glossary_axis": "Pruning",
                "root_quality": "Predictability",
                "long_paragraphs_without_behavior": sediment_paragraphs,
                "duplicate_instruction_lines": duplicate_lines,
            },
        )
    )
    if sediment_paragraphs:
        blockers.append(
            _quality_blocker(
                "construction_sediment_paragraph",
                "Long skill prose must carry an action, context pointer, completion criterion, output, or evidence obligation; otherwise it is sediment to move or prune.",
                dimension="pruning",
                path=source_path,
            )
        )
    if duplicate_lines:
        blockers.append(
            _quality_blocker(
                "construction_duplicate_instruction",
                "Repeated instruction-shaped lines violate single source of truth and should be deduplicated or moved into one routed reference.",
                dimension="pruning",
                path=source_path,
            )
        )

    return checks, blockers


def writing_quality_contract(
    repo_root: Path | None,
    skill_md: Path | None,
    frontmatter: dict[str, Any],
    text: str,
    progressive_disclosure: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic skill-writing rubric checks for package readiness."""
    source_path = repo_relative_path(repo_root, skill_md) if repo_root and skill_md else None
    checks: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []

    user_invoked = _frontmatter_bool(frontmatter, "disable-model-invocation")
    description = str(frontmatter.get("description") or "").strip()
    description_status = "not_applicable"
    if not user_invoked:
        description_status = (
            "pass"
            if description
            and text_contains_action_term(description)
            and "when" in {token.strip(".,:;!?()[]{}\"'").lower() for token in description.split()}
            else "blocked_validation"
        )
        if description_status != "pass":
            blockers.append(
                _quality_blocker(
                    "weak_description_triggers",
                    "Model-invoked skills need a trigger-shaped description with an action verb and a real 'when' branch.",
                    dimension="invocation",
                    path=source_path,
                )
            )
    checks.append(
        _quality_check(
            "description_trigger_shape",
            description_status,
            dimension="invocation",
            evidence={
                "user_invoked": user_invoked,
                "has_description": bool(description),
                "has_action_term": text_contains_action_term(description),
            },
        )
    )

    has_title = markdown_has_title(text)
    checks.append(
        _quality_check(
            "skill_md_title",
            "pass" if has_title else "blocked_validation",
            dimension="information_hierarchy",
            evidence={"headings": markdown_heading_titles(text)[:12]},
        )
    )
    if not has_title:
        blockers.append(
            _quality_blocker(
                "missing_skill_title",
                "SKILL.md must declare a top-level title so agents can identify the entrypoint.",
                dimension="information_hierarchy",
                path=source_path,
            )
        )

    procedural = _has_any_heading(text, ("Workflow", "Procedure", "Steps"))
    validation_declared = markdown_heading_declared(text, "Validation")
    output_contract_declared = markdown_heading_declared(text, "Output Contract")
    evidence_contract_declared = markdown_heading_declared(text, "Evidence Contract")
    completion_reference_declared = (
        skill_md is not None
        and package_local_regular_file(skill_md, "references/validation-and-output.md")
        and "references/validation-and-output.md" in text
    )
    validation_body = markdown_section_body(text, "Validation")
    validation_evidence_declared = (
        validation_declared
        and _body_contains_any(validation_body, ("pass", "fail", "blocked", "command:"))
    )
    completion_status = (
        "not_applicable"
        if not procedural
        else "pass"
        if output_contract_declared
        or evidence_contract_declared
        or validation_evidence_declared
        or completion_reference_declared
        else "blocked_validation"
    )
    checks.append(
        _quality_check(
            "procedural_completion_criteria",
            completion_status,
            dimension="completion_criteria",
            evidence={
                "procedural": procedural,
                "validation_declared": validation_declared,
                "output_contract_declared": output_contract_declared,
                "evidence_contract_declared": evidence_contract_declared,
                "completion_reference_declared": completion_reference_declared,
            },
        )
    )
    if completion_status == "blocked_validation":
        blockers.append(
            _quality_blocker(
                "missing_completion_criterion",
                "Procedural skills must declare observable completion evidence through Validation, an Output Contract, an Evidence Contract, or a routed validation-and-output reference.",
                dimension="completion_criteria",
                path=source_path,
            )
        )

    line_count = progressive_disclosure.get("skill_md_line_count", 0)
    entrypoint_compact = bool(progressive_disclosure.get("skill_md_under_250_lines"))
    near_threshold_limit = int(
        progressive_disclosure.get("skill_md_near_threshold_line_limit") or 220
    )
    over_near_threshold = bool(progressive_disclosure.get("skill_md_over_near_threshold"))
    references_count = int(progressive_disclosure.get("progressive_disclosure_reference_count") or 0)
    missing_references = progressive_disclosure.get("progressive_disclosure_missing_references") or []
    near_threshold_sprawl = over_near_threshold and references_count > 0 and not missing_references
    disclosure_status = (
        "blocked_validation"
        if missing_references
        or near_threshold_sprawl
        or (not entrypoint_compact and references_count == 0)
        else "pass"
    )
    checks.append(
        _quality_check(
            "progressive_disclosure_rubric",
            disclosure_status,
            dimension="progressive_disclosure",
            evidence={
                "line_count": line_count,
                "under_250_lines": entrypoint_compact,
                "near_threshold_line_limit": near_threshold_limit,
                "over_near_threshold": over_near_threshold,
                "reference_count": references_count,
                "missing_references": missing_references,
            },
        )
    )
    if missing_references:
        blockers.append(
            _quality_blocker(
                "weak_context_pointer_missing_reference",
                "Progressive Disclosure points at references that are not present in the package.",
                dimension="progressive_disclosure",
                path=source_path,
            )
        )
    elif not entrypoint_compact and references_count == 0:
        blockers.append(
            _quality_blocker(
                "sprawl_without_disclosure",
                "Long SKILL.md entrypoints must route branch-specific or reference material through package-local references.",
                dimension="progressive_disclosure",
                path=source_path,
            )
        )
    elif near_threshold_sprawl:
        blockers.append(
            _quality_blocker(
                "near_threshold_entrypoint_sprawl",
                (
                    "SKILL.md is above the 220-line package-readiness threshold while "
                    "package references are present; move phase detail, examples, or "
                    "reference-backed guidance into package-local references."
                ),
                dimension="progressive_disclosure",
                path=source_path,
            )
        )

    construction_checks, construction_blockers = _construction_quality_checks(
        repo_root=repo_root,
        skill_md=skill_md,
        text=text,
        user_invoked=user_invoked,
        description=description,
        procedural=procedural,
        references_count=references_count,
        missing_references=missing_references,
        source_path=source_path,
    )
    checks.extend(construction_checks)
    blockers.extend(construction_blockers)

    scenario_checks, scenario_blockers = _scenario_alignment_checks(repo_root, skill_md)
    checks.extend(scenario_checks)
    blockers.extend(scenario_blockers)
    advisories = _writing_quality_advisories(
        repo_root,
        skill_md,
        frontmatter,
        text,
        user_invoked=user_invoked,
        description=description,
        procedural=procedural,
        source_path=source_path,
    )

    status = "blocked_validation" if blockers else "pass"
    return {
        "schema_version": "skills-sdk.skill-writing-quality.v1",
        "policy": "predictability_through_invocation_hierarchy_completion_and_scenarios",
        "required_for_package_readiness": True,
        "status": status,
        "rubric": {
            "source": "writing-great-skills",
            "root_quality": "Predictability",
            "dimensions": [
                "invocation",
                "information_hierarchy",
                "steering",
                "pruning",
                "progressive_disclosure",
                "completion_criteria",
                "scenario_alignment",
                "actionability",
                "review_lens",
                "safety_boundary",
                "self_improving",
            ],
        },
        "checks": checks,
        "blockers": blockers,
        "advisories": advisories,
        "what_this_proves": [
            "trigger_shape_checked",
            "construction_trigger_checked",
            "construction_structure_checked",
            "construction_steering_checked",
            "construction_pruning_checked",
            "entrypoint_hierarchy_checked",
            "completion_evidence_checked",
            "reference_disclosure_checked",
            "scenario_shape_checked",
            "advisory_quality_patterns_scored",
        ] if status == "pass" else [],
        "what_this_does_not_prove": [
            "behavioral_eval_pass",
            "runtime_skill_activation",
            "live_tessl_score",
            "cloud_eval_confirmation",
        ],
    }


def _platform_check(
    name: str,
    status: str,
    *,
    dimension: str,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a stable OpenAI platform compatibility check record."""
    return {
        "name": name,
        "dimension": dimension,
        "status": status,
        "evidence": evidence or {},
    }


def _platform_blocker(
    rule_id: str,
    message: str,
    *,
    dimension: str,
    path: str | None,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a stable OpenAI platform compatibility blocker record."""
    return {
        "rule_id": rule_id,
        "dimension": dimension,
        "severity": "blocked",
        "path": path,
        "message": message,
        "evidence": evidence or {},
    }


def _platform_advisory(
    rule_id: str,
    message: str,
    *,
    dimension: str,
    path: str | None,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a stable OpenAI platform compatibility advisory record."""
    return {
        "rule_id": rule_id,
        "dimension": dimension,
        "severity": "advisory",
        "path": path,
        "message": message,
        "evidence": evidence or {},
    }


def _plugin_root_for_source(repo_root: Path | None, source_path: Path | None) -> Path | None:
    """Return the owning plugin root for a plugin-owned skill source."""
    if not repo_root or not source_path:
        return None
    relative = repo_relative_path(repo_root, source_path)
    if not relative:
        return None
    parts = relative.split("/")
    if len(parts) >= 4 and parts[0] == "Plugins" and parts[2] == "skills":
        return repo_root / parts[0] / parts[1]
    return None


def _plugin_manifest_path(plugin_root: Path | None) -> Path | None:
    """Return the supported plugin manifest path for a plugin root."""
    if not plugin_root:
        return None
    for relative in (".codex-plugin/plugin.json", "plugin.json"):
        candidate = plugin_root / relative
        if candidate.is_file():
            return candidate
    return None


def _read_json_object(path: Path | None) -> tuple[dict[str, Any] | None, str | None]:
    """Read a JSON object without treating malformed data as instructions."""
    if path is None:
        return None, "missing"
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, exc.__class__.__name__
    if not isinstance(loaded, dict):
        return None, "json root must be an object"
    return loaded, None


def _rel_path_or_none(repo_root: Path | None, path: Path | None) -> str | None:
    if repo_root and path:
        return repo_relative_path(repo_root, path) or path.as_posix()
    return path.as_posix() if path else None


def _plugin_hook_commands_are_portable(command: str) -> bool:
    """Return whether a command avoids local absolute plugin-owned paths."""
    tokens = command.split()
    return not any(token.startswith(("/", "~/")) for token in tokens)


def _hook_timeout_shape(hook: dict[str, Any]) -> str:
    if "timeoutSec" in hook:
        return "timeoutSec"
    if "timeout" not in hook:
        return "missing"
    return "seconds" if type(hook.get("timeout")) is int else "invalid"


def _plugin_hooks_contract(
    repo_root: Path | None,
    plugin_root: Path | None,
    manifest: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Return deterministic checks for Codex-supported plugin bundled hooks."""
    checks: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    advisories: list[dict[str, Any]] = []
    if not plugin_root:
        checks.append(
            _platform_check(
                "plugin_hook_contract",
                "not_applicable",
                dimension="plugin_hooks",
                evidence={"reason": "skill is not plugin-owned"},
            )
        )
        return checks, blockers, advisories

    hook_decl = manifest.get("hooks") if isinstance(manifest, dict) else None
    hooks_path = plugin_root / "hooks" / "hooks.json"
    hooks_rel = _rel_path_or_none(repo_root, hooks_path)
    if hook_decl is None and not hooks_path.is_file():
        checks.append(
            _platform_check(
                "plugin_hooks_manifest_declared",
                "not_applicable",
                dimension="plugin_hooks",
                evidence={
                    "declared_hooks": hook_decl,
                    "expected": "./hooks/hooks.json",
                    "reason": "plugin does not declare bundled hooks",
                },
            )
        )
        return checks, blockers, advisories
    if hooks_path.is_file() and hook_decl != "./hooks/hooks.json":
        blockers.append(
            _platform_blocker(
                "plugin_hooks_manifest_path_invalid",
                "Plugin manifests must declare bundled hooks as ./hooks/hooks.json.",
                dimension="plugin_hooks",
                path=_rel_path_or_none(repo_root, _plugin_manifest_path(plugin_root)),
                evidence={"declared_hooks": hook_decl},
            )
        )
    checks.append(
        _platform_check(
            "plugin_hooks_manifest_declared",
            "pass" if hook_decl == "./hooks/hooks.json" else "blocked_validation",
            dimension="plugin_hooks",
            evidence={"declared_hooks": hook_decl, "expected": "./hooks/hooks.json"},
        )
    )
    loaded, error = _read_json_object(hooks_path)
    if error is not None:
        blockers.append(
            _platform_blocker(
                "plugin_hooks_file_unreadable",
                "Bundled plugin hooks must be readable JSON.",
                dimension="plugin_hooks",
                path=hooks_rel,
                evidence={"error": error},
            )
        )
        checks.append(
            _platform_check(
                "plugin_hooks_json_parse",
                "blocked_validation",
                dimension="plugin_hooks",
                evidence={"path": hooks_rel, "error": error},
            )
        )
        return checks, blockers, advisories

    hooks_root = loaded.get("hooks") if isinstance(loaded, dict) else None
    hooks_root_ok = isinstance(hooks_root, dict)
    checks.append(
        _platform_check(
            "plugin_hooks_top_level_object",
            "pass" if hooks_root_ok else "blocked_validation",
            dimension="plugin_hooks",
            evidence={"path": hooks_rel},
        )
    )
    if not hooks_root_ok:
        blockers.append(
            _platform_blocker(
                "plugin_hooks_top_level_missing",
                "Codex plugin hook config must use a top-level hooks object.",
                dimension="plugin_hooks",
                path=hooks_rel,
            )
        )
        return checks, blockers, advisories

    hook_count = 0
    unsupported_types: list[str] = []
    timeoutsec_hooks: list[str] = []
    missing_timeout_hooks: list[str] = []
    nonportable_commands: list[str] = []
    invalid_groups: list[str] = []
    for matcher_name, matcher_groups in hooks_root.items():
        if not isinstance(matcher_groups, list):
            invalid_groups.append(str(matcher_name))
            continue
        for group_index, group in enumerate(matcher_groups):
            group_label = f"{matcher_name}[{group_index}]"
            if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
                invalid_groups.append(group_label)
                continue
            for hook_index, hook in enumerate(group["hooks"]):
                hook_label = f"{group_label}.hooks[{hook_index}]"
                if not isinstance(hook, dict):
                    invalid_groups.append(hook_label)
                    continue
                hook_count += 1
                hook_type = str(hook.get("type") or "")
                if hook_type != "command":
                    unsupported_types.append(f"{hook_label}:{hook_type or '<missing>'}")
                timeout_shape = _hook_timeout_shape(hook)
                if timeout_shape == "timeoutSec":
                    timeoutsec_hooks.append(hook_label)
                elif timeout_shape != "seconds":
                    missing_timeout_hooks.append(hook_label)
                command = str(hook.get("command") or "")
                if hook_type == "command" and command and not _plugin_hook_commands_are_portable(command):
                    nonportable_commands.append(hook_label)

    if invalid_groups:
        blockers.append(
            _platform_blocker(
                "plugin_hooks_group_shape_invalid",
                "Each hook matcher group must contain a hooks array.",
                dimension="plugin_hooks",
                path=hooks_rel,
                evidence={"invalid_groups": invalid_groups},
            )
        )
    if unsupported_types:
        blockers.append(
            _platform_blocker(
                "plugin_hooks_unsupported_type",
                "Plugin hooks currently support command hooks only.",
                dimension="runtime_support",
                path=hooks_rel,
                evidence={"unsupported_types": unsupported_types},
            )
        )
    if timeoutsec_hooks:
        blockers.append(
            _platform_blocker(
                "plugin_hooks_timeoutsec_unsupported",
                "Command hooks must use timeout in seconds; timeoutSec is unsupported.",
                dimension="plugin_hooks",
                path=hooks_rel,
                evidence={"hooks": timeoutsec_hooks},
            )
        )
    if missing_timeout_hooks:
        blockers.append(
            _platform_blocker(
                "plugin_hooks_timeout_missing",
                "Command hooks must declare timeout as an integer number of seconds.",
                dimension="plugin_hooks",
                path=hooks_rel,
                evidence={"hooks": missing_timeout_hooks},
            )
        )
    if nonportable_commands:
        blockers.append(
            _platform_blocker(
                "plugin_hooks_command_not_portable",
                "Plugin-owned hook commands must reference ${PLUGIN_ROOT} or ${PLUGIN_DATA}.",
                dimension="path_portability",
                path=hooks_rel,
                evidence={"hooks": nonportable_commands},
            )
        )
    checks.append(
        _platform_check(
            "plugin_hooks_runtime_supported_shape",
            "blocked_validation"
            if invalid_groups or unsupported_types or timeoutsec_hooks or missing_timeout_hooks
            else "pass",
            dimension="plugin_hooks",
            evidence={
                "hook_count": hook_count,
                "invalid_groups": invalid_groups,
                "unsupported_types": unsupported_types,
                "timeoutSec_hooks": timeoutsec_hooks,
                "missing_timeout_hooks": missing_timeout_hooks,
            },
        )
    )
    checks.append(
        _platform_check(
            "plugin_hooks_command_portability",
            "pass" if not nonportable_commands else "blocked_validation",
            dimension="path_portability",
            evidence={"nonportable_commands": nonportable_commands},
        )
    )
    if hook_count == 0:
        advisories.append(
            _platform_advisory(
                "plugin_hooks_empty",
                "Bundled hook files should contain at least one supported command hook when declared.",
                dimension="plugin_hooks",
                path=hooks_rel,
            )
        )
    return checks, blockers, advisories


def openai_platform_compat_contract(
    repo_root: Path | None,
    source_path: Path | None,
    frontmatter: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic OpenAI-facing skill and plugin compatibility checks."""
    checks: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    advisories: list[dict[str, Any]] = []
    source_rel = repo_relative_path(repo_root, source_path) if repo_root and source_path else None
    openai_fields = read_agents_openai_yaml_fields(source_path)
    interface = openai_fields.get("interface")
    short_description = ""
    if isinstance(interface, dict):
        short_description = str(interface.get("short_description") or "").strip()
    skill_description = str(frontmatter.get("description") or "").strip()
    checks.append(
        _platform_check(
            "skill_metadata_projection",
            "pass" if frontmatter.get("name") and skill_description else "blocked_validation",
            dimension="metadata_projection",
            evidence={
                "name_present": bool(frontmatter.get("name")),
                "description_present": bool(skill_description),
                "short_description_present": bool(short_description),
            },
        )
    )
    if not frontmatter.get("name") or not skill_description:
        blockers.append(
            _platform_blocker(
                "openai_skill_metadata_incomplete",
                "OpenAI-facing skill projection requires name and description metadata.",
                dimension="metadata_projection",
                path=source_rel,
            )
        )
    if not short_description:
        advisories.append(
            _platform_advisory(
                "openai_short_description_missing",
                "agents/openai.yaml should expose interface.short_description for browseable surfaces.",
                dimension="metadata_projection",
                path=source_rel,
            )
        )

    plugin_root = _plugin_root_for_source(repo_root, source_path)
    plugin_manifest_path = _plugin_manifest_path(plugin_root)
    plugin_manifest, manifest_error = _read_json_object(plugin_manifest_path)
    if plugin_root:
        checks.append(
            _platform_check(
                "plugin_manifest_parse",
                "pass" if manifest_error is None else "blocked_validation",
                dimension="plugin_manifest",
                evidence={
                    "path": _rel_path_or_none(repo_root, plugin_manifest_path),
                    "error": manifest_error,
                },
            )
        )
        if manifest_error is not None:
            blockers.append(
                _platform_blocker(
                    "plugin_manifest_unreadable",
                    "Plugin-owned skills must have a readable plugin.json manifest.",
                    dimension="plugin_manifest",
                    path=_rel_path_or_none(repo_root, plugin_manifest_path),
                    evidence={"error": manifest_error},
                )
            )
    hook_checks, hook_blockers, hook_advisories = _plugin_hooks_contract(
        repo_root,
        plugin_root,
        plugin_manifest,
    )
    checks.extend(hook_checks)
    blockers.extend(hook_blockers)
    advisories.extend(hook_advisories)

    status = "blocked_validation" if blockers else "pass"
    return {
        "schema_version": OPENAI_PLATFORM_COMPAT_SCHEMA_VERSION,
        "policy": "deterministic_openai_skill_and_plugin_projection",
        "required_for_package_readiness": True,
        "status": status,
        "target_kind": "plugin_skill" if plugin_root else "skill",
        "rubric": {
            "source": "openai-platform-and-codex-plugin-hook-contract",
            "dimensions": [
                "metadata_projection",
                "plugin_manifest",
                "plugin_hooks",
                "path_portability",
                "runtime_support",
            ],
        },
        "checks": checks,
        "blockers": blockers,
        "advisories": advisories,
        "what_this_proves": [
            "openai_facing_metadata_shape_checked",
            "plugin_manifest_hook_pointer_checked",
            "bundled_command_hook_shape_checked",
            "plugin_command_path_portability_checked",
        ] if status == "pass" else [],
        "what_this_does_not_prove": [
            "hosted_openai_acceptance",
            "runtime_plugin_hook_execution",
            "behavioral_eval_pass",
            "marketplace_publication",
        ],
    }


def skill_agent_toml_paths(repo_root: Path | None, skill_md: Path | None) -> list[str]:
    """Return optional per-skill agent TOML runtime profiles."""
    if not skill_md:
        return []
    agents_dir = skill_md.parent / "agents"
    if not agents_dir.is_dir():
        return []
    paths: list[str] = []
    for candidate in sorted(agents_dir.glob("*.toml")):
        if repo_root:
            paths.append(repo_relative_path(repo_root, candidate) or candidate.as_posix())
        else:
            paths.append(candidate.as_posix())
    return paths


def skill_command_candidates(text: str) -> list[str]:
    """Extract a conservative command list from skill prose."""
    commands: list[str] = []
    for line in text.splitlines():
        stripped = normalized_command_candidate(line)
        if not stripped:
            continue
        if stripped and stripped not in commands:
            commands.append(stripped)
    return commands[:8]


def normalized_command_candidate(line: str) -> str | None:
    """Return a command only when the line itself is shaped like a command."""
    stripped = line.strip().strip(chr(96))
    while stripped.startswith(("-", "*")):
        stripped = stripped[1:].strip()
    if len(stripped) >= 3 and stripped[0].isdigit() and stripped[1] == ".":
        stripped = stripped[2:].strip()
    stripped = stripped.strip(chr(96))
    if stripped.lower().startswith("command:"):
        stripped = stripped.split(":", 1)[1].strip().strip(chr(96))
    for prefix in ("./bin/ask ", "python3 ", "bash "):
        if stripped.startswith(prefix):
            return stripped
    return None


def local_evidence_provider_status() -> dict[str, Any]:
    """Return optional ~/.agents observability providers for package evidence enrichment."""
    agents_root = Path.home() / ".agents"
    providers: list[dict[str, Any]] = []
    provider_specs = [
        {
            "name": "otel_collector",
            "root": agents_root / "otel-collector",
            "signals": ["otlp_raw", "processed_stats"],
            "stats": agents_root / "otel-collector" / "data" / "processed" / "stats.json",
        },
        {
            "name": "session_collector",
            "root": agents_root / "session-collector",
            "signals": ["normalized_sessions", "session_evidence"],
            "stats": None,
        },
        {
            "name": "observability_stack",
            "root": agents_root / "observability-stack",
            "signals": ["jaeger", "prometheus", "loki", "grafana"],
            "stats": None,
        },
    ]
    available_count = 0
    for spec in provider_specs:
        root = spec["root"]
        available = root.is_dir()
        available_count += int(available)
        stats_path = spec["stats"]
        stats_freshness = "not_applicable"
        if stats_path is not None:
            stats_freshness = "present" if stats_path.is_file() else "missing"
        providers.append(
            {
                "name": spec["name"],
                "optional": True,
                "authority": "enrichment_only",
                "status": "available" if available else "missing",
                "root": root.as_posix(),
                "signals": spec["signals"],
                "stats_freshness": stats_freshness,
            }
        )
    if available_count >= 2:
        telemetry_confidence = "enriched"
    elif available_count == 1:
        telemetry_confidence = "partial"
    else:
        telemetry_confidence = "not_available"
    return {
        "schema_version": "skill-evidence-providers.v1",
        "authority": "artifacts_decide_telemetry_explains",
        "telemetry_confidence": telemetry_confidence,
        "providers": providers,
        "required_for_package_readiness": False,
    }


def sdk_package_contract(
    repo_root: Path | None,
    source_path: Path | None,
    frontmatter: dict[str, Any],
) -> dict[str, Any]:
    """Return the portable Skills SDK package contract view for agents."""
    text = skill_markdown_text(source_path)
    reference_contract = read_reference_contract(source_path)
    reference_quality = reference_quality_contract(repo_root, source_path)
    progressive_disclosure = progressive_disclosure_contract(repo_root, source_path, text)
    writing_quality = writing_quality_contract(
        repo_root,
        source_path,
        frontmatter,
        text,
        progressive_disclosure,
    )
    openai_platform_compat = openai_platform_compat_contract(repo_root, source_path, frontmatter)
    identity_and_assets = identity_and_assets_contract(repo_root, source_path, frontmatter)
    knowledge_capsules = knowledge_capsule_first_party_contract(repo_root, source_path, text)
    workflow_contract = skillflow_contract(repo_root, source_path, reference_contract)
    optimization_readiness = optimization_contract(repo_root, source_path, reference_contract)
    eval_paths = skill_eval_paths(repo_root, source_path)
    agents_openai_path = skill_package_file_path(repo_root, source_path, "agents/openai.yaml")
    references_contract_path = skill_package_file_path(
        repo_root,
        source_path,
        "references/contract.yaml",
    )
    task_profile_path = skill_package_file_path(
        repo_root,
        source_path,
        "references/task-profile.json",
    )
    agent_toml_paths = skill_agent_toml_paths(repo_root, source_path)
    package_values = package_field_values(frontmatter)
    commands = skill_command_candidates(text)
    if not commands:
        commands = _string_list(reference_contract.get("commands"))
    policy = frontmatter.get("policy")
    permission_profile = reference_contract.get("permission_profile")
    if not permission_profile and isinstance(policy, dict) and policy:
        permission_profile = policy
    evidence_policy = (
        reference_contract.get("evidence_policy")
        or reference_contract.get("observability")
        or ("Validation section declared" if markdown_heading_declared(text, "Validation") else None)
    )
    values = {
        "agent_metadata": {
            "declared": bool(agents_openai_path),
            "path": agents_openai_path,
            "format": "agents/openai.yaml",
            "authority": "skill_interface_and_dependency_metadata",
        },
        "reference_contract": {
            "declared": bool(references_contract_path),
            "path": references_contract_path,
            "format": "references/contract.yaml",
            "authority": "sdk_package_contract",
        },
        "reference_quality": reference_quality,
        "writing_quality": writing_quality,
        "openai_platform_compat": openai_platform_compat,
        "purpose": reference_contract.get("purpose") or frontmatter.get("description"),
        "inputs": reference_contract.get("inputs")
        or ("declared_in_skill_md" if markdown_heading_declared(text, "Inputs") else None),
        "outputs": reference_contract.get("outputs")
        or ("declared_in_skill_md" if markdown_heading_declared(text, "Outputs") else None),
        "commands": commands,
        "permission_profile": permission_profile,
        "portability_profile": {
            "compatible_roles": package_values["compatible_roles"],
            "runtime_needs": package_values["runtime_needs"],
            "provenance": package_values["provenance"],
            "share_readiness": package_values["share_readiness"],
        },
        "evals": {
            "declared": bool(eval_paths),
            "paths": eval_paths,
        },
        "task_profile": {
            "declared": bool(task_profile_path),
            "path": task_profile_path,
        },
        "evidence_policy": evidence_policy,
        "budget_classification": reference_contract.get("budget_classification"),
        "workflow_contract": workflow_contract,
        "optimization_contract": optimization_readiness,
        "knowledge_capsules": knowledge_capsules,
    }
    present = sorted(
        field for field, value in values.items() if sdk_contract_field_present(field, value)
    )
    missing = sorted(field for field in SDK_PACKAGE_CONTRACT_FIELDS if field not in present)
    source_rel = repo_relative_path(repo_root, source_path) if repo_root and source_path else None
    skill_dir = source_path.parent if source_path else None
    editable_paths = [
        repo_relative_path(repo_root, skill_dir) or skill_dir.as_posix()
    ] if repo_root and skill_dir else []
    return {
        "schema_version": SDK_PACKAGE_CONTRACT_SCHEMA_VERSION,
        "required_fields": {
            "present": present,
            "missing": missing,
        },
        "values": values,
        "progressive_disclosure": {
            "skill_md_declared": bool(source_path and source_path.is_file()),
            **progressive_disclosure,
            "agent_metadata_declared": bool(agents_openai_path),
            "references_contract_declared": bool(reference_contract),
            "references_quality_status": reference_quality["status"],
            "writing_quality_status": writing_quality["status"],
            "openai_platform_compat_status": openai_platform_compat["status"],
            "evals_declared": bool(eval_paths),
            "task_profile_declared": bool(task_profile_path),
            "agent_tomls_declared": bool(agent_toml_paths),
            "agent_tomls": agent_toml_paths,
            "workflow_declared": bool(workflow_contract["declared"]),
            "workflow_status": workflow_contract["status"],
            "execution_mode": workflow_contract["execution_mode"],
            "optimization_declared": bool(optimization_readiness["enabled"]),
            "optimization_status": optimization_readiness["status"],
            "optimization_mode": optimization_readiness["optimizer_mode"],
            "knowledge_capsules_declared": bool(knowledge_capsules["manifest_declared"]),
            "knowledge_capsules_first_party_ready": bool(knowledge_capsules["ready"]),
        },
        "identity_and_assets": identity_and_assets,
        "knowledge_capsules": knowledge_capsules,
        "agent_contract": {
            "source_of_truth": source_rel,
            "editable_paths": editable_paths,
            "generated_paths": [".agents/skills/**"],
            "forbidden_actions": [
                "edit_generated_runtime_projection",
                "claim_eval_pass_as_runtime_proof",
            ],
            "next_safe_command": "./bin/ask skills package <handle-or-path> --checkout-test --json --robot",
            "what_this_proves": ["package_shape", "declared_metadata", "local_file_presence"],
            "what_this_does_not_prove": ["runtime_behavior", "security_posture", "human_approval"],
            "workflow_policy": (
                "SKILL.md remains the judgment layer; workflows/skillflow.json is optional "
                "deterministic mechanics. Runtime adaptation inside declared graph bounds may be "
                "autonomous; durable graph amendments require review."
            ),
            "optimization_policy": (
                "Skill optimization may produce bounded candidate artifacts and rejected-edit "
                "evidence. Canonical SKILL.md promotion requires declared gates, anti-cheat "
                "checks, and review."
            ),
            "agent_toml_policy": (
                "optional_per_skill_runtime_profiles; required only when the skill contract "
                "declares a dedicated subagent or persona runtime"
            ),
        },
        "evidence_providers": local_evidence_provider_status(),
    }


def sdk_contract_field_present(field: str, value: Any) -> bool:
    """Return whether an SDK package contract field has real declared evidence."""
    if field == "evals" and isinstance(value, dict):
        return bool(value.get("declared"))
    if field in {"agent_metadata", "reference_contract", "task_profile"} and isinstance(value, dict):
        return bool(value.get("declared"))
    if field == "portability_profile" and isinstance(value, dict):
        return any(bool(item) for item in value.values())
    return bool(value)


def skill_package_contract(
    repo_root: Path,
    source_path: Path | None,
    frontmatter: dict[str, Any],
) -> dict[str, Any]:
    """Return the Codex-native package contract for SKILL.md plus agents/openai.yaml."""
    openai_fields = read_agents_openai_yaml_fields(source_path)
    interface = frontmatter.get("interface")
    if not isinstance(interface, dict):
        interface = {}
    openai_interface = openai_fields.get("interface")
    if isinstance(openai_interface, dict):
        interface = {**interface, **openai_interface}

    dependencies = frontmatter.get("dependencies")
    if not isinstance(dependencies, dict):
        dependencies = {}
    openai_dependencies = openai_fields.get("dependencies")
    if isinstance(openai_dependencies, dict):
        dependencies = {**dependencies, **openai_dependencies}
    policy = frontmatter.get("policy")
    if not isinstance(policy, dict):
        policy = {}
    openai_policy = openai_fields.get("policy")
    if isinstance(openai_policy, dict):
        policy = {**policy, **openai_policy}

    codex_metadata = {
        "name": frontmatter.get("name"),
        "description": frontmatter.get("description"),
        "short_description": frontmatter.get("short_description")
        or interface.get("short_description"),
        "interface": interface or None,
        "dependencies": dependencies or None,
        "policy": policy or None,
        "scope": frontmatter.get("scope"),
        "plugin_id": frontmatter.get("plugin_id"),
    }
    required_present = sorted(
        field for field in CODEX_SKILL_PACKAGE_REQUIRED_FIELDS if codex_metadata.get(field)
    )
    required_missing = sorted(
        field for field in CODEX_SKILL_PACKAGE_REQUIRED_FIELDS if not codex_metadata.get(field)
    )
    optional_present = sorted(
        field for field in CODEX_SKILL_PACKAGE_OPTIONAL_FIELDS if codex_metadata.get(field)
    )
    source_rel = repo_relative_path(repo_root, source_path) if source_path else None
    openai_rel = None
    if source_path:
        openai_path = source_path.parent / "agents" / "openai.yaml"
        if openai_path.is_file():
            openai_rel = repo_relative_path(repo_root, openai_path)
    return {
        "schema_version": SKILL_PACKAGE_SCHEMA_VERSION,
        "source_files": {
            "skill_md": source_rel,
            "agents_openai_yaml": openai_rel,
        },
        "codex_abi_source": codex_skill_package_abi_source(),
        "metadata": codex_metadata,
        "required_fields": {
            "present": required_present,
            "missing": required_missing,
        },
        "optional_fields": {
            "present": optional_present,
        },
        "compatibility_status": "blocked_validation" if required_missing else "compatible",
    }


def empty_skill_package_contract() -> dict[str, Any]:
    """Return a package contract for unresolved or missing source paths."""
    return {
        "schema_version": SKILL_PACKAGE_SCHEMA_VERSION,
        "source_files": {
            "skill_md": None,
            "agents_openai_yaml": None,
        },
        "codex_abi_source": codex_skill_package_abi_source(),
        "metadata": {
            "name": None,
            "description": None,
            "short_description": None,
            "interface": None,
            "dependencies": None,
            "policy": None,
            "scope": None,
            "plugin_id": None,
        },
        "required_fields": {
            "present": [],
            "missing": list(CODEX_SKILL_PACKAGE_REQUIRED_FIELDS),
        },
        "optional_fields": {
            "present": [],
        },
        "compatibility_status": "blocked_missing_source",
    }


def skill_package_compatibility_snapshot() -> dict[str, Any]:
    """Return the public package-output snapshot identity for drift tests."""
    return {
        "id": SKILL_PACKAGE_COMPATIBILITY_SNAPSHOT_ID,
        "schema_version": SKILL_PACKAGE_READINESS_SCHEMA_VERSION,
        "path": SKILL_PACKAGE_SNAPSHOT_PATH,
        "covers": [
            "valid_share_ready_package",
            "missing_source_package",
            "strict_incomplete_package",
        ],
    }


def _required_sdk_contract_blockers(sdk_contract: dict[str, Any]) -> dict[str, list[str]]:
    values = sdk_contract.get("values")
    if not isinstance(values, dict):
        return {}
    blockers_by_field: dict[str, list[str]] = {}
    for field, contract in values.items():
        if not isinstance(contract, dict):
            continue
        if contract.get("required_for_package_readiness") is not True:
            continue
        if contract.get("status") != "blocked_validation":
            continue
        raw_blockers = contract.get("blockers")
        blocker_items = raw_blockers if isinstance(raw_blockers, list) else []
        blockers = [
            f"{field}:{blocker.get('rule_id', 'blocked_validation')}"
            for blocker in blocker_items
            if isinstance(blocker, dict)
        ] or [f"{field}:blocked_validation"]
        blockers_by_field[str(field)] = blockers
    return blockers_by_field


def skill_package_readiness(
    frontmatter: dict[str, Any],
    repo_root: Path | None = None,
    source_path: Path | None = None,
) -> dict[str, Any]:
    """Return version and role-aware package readiness for one skill."""
    values = package_field_values(frontmatter)
    sdk_contract = sdk_package_contract(repo_root, source_path, frontmatter)
    present = sorted(field for field, value in values.items() if bool(value))
    missing = sorted(field for field in PACKAGE_CONTRACT_FIELDS if field not in present)
    share_readiness = str(values.get("share_readiness") or "").strip().lower()
    share_readiness_ready = share_readiness == "ready"
    share_ready = False
    missing_identity_fields = [
        field
        for field in ("name", "description")
        if not str(frontmatter.get(field) or "").strip()
    ]

    if missing_identity_fields:
        readiness_level = "incomplete_identity"
    elif not values.get("version"):
        readiness_level = "legacy_capability"
    elif missing:
        readiness_level = "versioned_capability"
    elif not share_readiness_ready:
        readiness_level = "share_readiness_blocked"
    else:
        readiness_level = "share_ready"
        share_ready = True

    blocked_reasons = list(missing)
    sdk_missing = [
        f"sdk_contract:{field}"
        for field in sdk_contract["required_fields"]["missing"]
    ]
    blocked_reasons.extend(sdk_missing)
    workflow_contract = sdk_contract["values"].get("workflow_contract")
    workflow_blockers: list[str] = []
    if isinstance(workflow_contract, dict) and workflow_contract.get("status") == "blocked_validation":
        workflow_blockers = [
            f"workflow_contract:{blocker.get('rule_id', 'blocked_validation')}"
            for blocker in workflow_contract.get("blockers", [])
            if isinstance(blocker, dict)
        ] or ["workflow_contract:blocked_validation"]
        blocked_reasons.extend(workflow_blockers)
    optimization_readiness = sdk_contract["values"].get("optimization_contract")
    optimization_blockers: list[str] = []
    if (
        isinstance(optimization_readiness, dict)
        and optimization_readiness.get("status") == "blocked_validation"
    ):
        optimization_blockers = [
            f"optimization_contract:{blocker.get('rule_id', 'blocked_validation')}"
            for blocker in optimization_readiness.get("blockers", [])
            if isinstance(blocker, dict)
        ] or ["optimization_contract:blocked_validation"]
        blocked_reasons.extend(optimization_blockers)
    required_contract_blockers = _required_sdk_contract_blockers(sdk_contract)
    reference_blockers = required_contract_blockers.pop("reference_quality", [])
    writing_quality_blockers = required_contract_blockers.pop("writing_quality", [])
    openai_platform_blockers = required_contract_blockers.pop("openai_platform_compat", [])
    other_required_contract_blockers = [
        blocker
        for blockers in required_contract_blockers.values()
        for blocker in blockers
    ]
    blocked_reasons.extend(reference_blockers)
    blocked_reasons.extend(writing_quality_blockers)
    blocked_reasons.extend(openai_platform_blockers)
    blocked_reasons.extend(other_required_contract_blockers)
    if sdk_missing and not missing_identity_fields and not missing:
        readiness_level = "sdk_contract_incomplete"
        share_ready = False
    if workflow_blockers and not missing_identity_fields and not missing and not sdk_missing:
        readiness_level = "workflow_contract_incomplete"
        share_ready = False
    if (
        optimization_blockers
        and not missing_identity_fields
        and not missing
        and not sdk_missing
        and not workflow_blockers
    ):
        readiness_level = "optimization_contract_incomplete"
        share_ready = False
    if (
        reference_blockers
        and not missing_identity_fields
        and not missing
        and not sdk_missing
        and not workflow_blockers
        and not optimization_blockers
    ):
        readiness_level = "reference_quality_incomplete"
        share_ready = False
    if (
        writing_quality_blockers
        and not missing_identity_fields
        and not missing
        and not sdk_missing
        and not workflow_blockers
        and not optimization_blockers
        and not reference_blockers
    ):
        readiness_level = "writing_quality_incomplete"
        share_ready = False
    if (
        openai_platform_blockers
        and not missing_identity_fields
        and not missing
        and not sdk_missing
        and not workflow_blockers
        and not optimization_blockers
        and not reference_blockers
        and not writing_quality_blockers
    ):
        readiness_level = "openai_platform_compat_incomplete"
        share_ready = False
    if (
        other_required_contract_blockers
        and not missing_identity_fields
        and not missing
        and not sdk_missing
        and not workflow_blockers
        and not optimization_blockers
        and not reference_blockers
        and not writing_quality_blockers
        and not openai_platform_blockers
    ):
        readiness_level = "sdk_required_contract_incomplete"
        share_ready = False
    knowledge_capsules = sdk_contract.get("knowledge_capsules")
    knowledge_blockers: list[str] = []
    if (
        isinstance(knowledge_capsules, dict)
        and knowledge_capsules.get("manifest_declared") is True
        and knowledge_capsules.get("ready") is not True
    ):
        knowledge_blockers = ["knowledge_capsules:first_party_routing_incomplete"]
        blocked_reasons.extend(knowledge_blockers)
    if (
        knowledge_blockers
        and not missing_identity_fields
        and not missing
        and not sdk_missing
        and not workflow_blockers
        and not optimization_blockers
        and not reference_blockers
        and not writing_quality_blockers
        and not openai_platform_blockers
        and not other_required_contract_blockers
    ):
        readiness_level = "knowledge_capsules_incomplete"
        share_ready = False
    progressive = sdk_contract.get("progressive_disclosure")
    progressive_blockers: list[str] = []
    if isinstance(progressive, dict):
        source_operating_model = progressive.get("source_operating_model")
        if (
            isinstance(source_operating_model, dict)
            and source_operating_model.get("status") == "blocked_validation"
        ):
            progressive_blockers = [
                "progressive_disclosure:source_operating_model_preservation"
            ]
            blocked_reasons.extend(progressive_blockers)
    if (
        progressive_blockers
        and not missing_identity_fields
        and not missing
        and not sdk_missing
        and not workflow_blockers
        and not optimization_blockers
        and not reference_blockers
        and not writing_quality_blockers
        and not openai_platform_blockers
        and not other_required_contract_blockers
        and not knowledge_blockers
    ):
        readiness_level = "progressive_disclosure_incomplete"
        share_ready = False
    if missing_identity_fields:
        blocked_reasons.append("identity_incomplete")
    if not missing and not share_readiness_ready:
        blocked_reasons.append("share_readiness_not_ready")
    recommended_next_fields = [
        field
        for field in ("compatible_roles", "runtime_needs", "provenance", "share_readiness")
        if field in missing
    ]
    if not missing and not share_readiness_ready:
        recommended_next_fields.append("share_readiness")
    if "version" in missing:
        recommended_next_fields.insert(0, "version")
    recommended_next_fields = [*missing_identity_fields, *recommended_next_fields]
    promotion_status = "ready_pending_checkout" if share_ready else "blocked_validation"

    return {
        "readiness_level": readiness_level,
        "required_fields": {
            "present": present,
            "missing": missing,
        },
        "values": values,
        "role_compatibility": {
            "declared": bool(values["compatible_roles"]),
            "roles": values["compatible_roles"],
        },
        "runtime_contract": {
            "declared": bool(values["runtime_needs"]),
            "needs": values["runtime_needs"],
        },
        "install_gate": {
            "install_ready": share_ready,
            "required_checks": list(PACKAGE_CONTRACT_FIELDS),
            "blocked_reasons": blocked_reasons,
            "checkout_test": {
                "required": True,
                "status": "not_run",
                "evidence": [],
            },
        },
        "promotion_gate": {
            "status": promotion_status,
            "promotion_ready": False,
            "share_ready": share_ready,
            "share_readiness": values["share_readiness"],
            "checkout_test_status": "not_run",
            "blocked_reasons": blocked_reasons,
            "recommended_next_fields": recommended_next_fields,
        },
        "sdk_contract": sdk_contract,
    }


def refresh_package_promotion_gate(package_contract: dict[str, Any]) -> None:
    """Keep promotion readiness tied to metadata and checkout evidence."""
    promotion_gate = package_contract["promotion_gate"]
    checkout_status = package_contract["install_gate"]["checkout_test"]["status"]
    promotion_gate["checkout_test_status"] = checkout_status

    if promotion_gate["status"] == "blocked_missing_source":
        promotion_gate["promotion_ready"] = False
        return
    if promotion_gate["blocked_reasons"]:
        promotion_gate["status"] = "blocked_validation"
        promotion_gate["promotion_ready"] = False
        return
    if not promotion_gate["share_ready"]:
        promotion_gate["status"] = "blocked_validation"
        promotion_gate["promotion_ready"] = False
        return
    if checkout_status == "pass":
        promotion_gate["status"] = "ready"
        promotion_gate["promotion_ready"] = True
        return
    if checkout_status == "not_run":
        promotion_gate["status"] = "ready_pending_checkout"
    else:
        promotion_gate["status"] = checkout_status
    promotion_gate["promotion_ready"] = False


def skill_package_gate_summary(package_contract: dict[str, Any]) -> dict[str, Any]:
    """Return automation-facing package gate status without nested traversal."""
    install_gate = package_contract["install_gate"]
    promotion_gate = package_contract["promotion_gate"]
    return {
        "install_ready": install_gate["install_ready"],
        "checkout_test_status": install_gate["checkout_test"]["status"],
        "promotion_status": promotion_gate["status"],
        "promotion_ready": promotion_gate["promotion_ready"],
        "blocked_reasons": promotion_gate["blocked_reasons"],
    }


def skill_package_readiness_summary(package_contract: dict[str, Any]) -> dict[str, Any]:
    """Return a compact readiness summary for routing and dashboards."""
    required_fields = package_contract["required_fields"]
    sdk_contract = package_contract.get("sdk_contract") or {}
    sdk_required_fields = sdk_contract.get("required_fields") or {}
    sdk_missing_fields = list(sdk_required_fields.get("missing") or [])
    present_fields = list(required_fields["present"])
    missing_fields = list(required_fields["missing"])
    return {
        "readiness_level": package_contract["readiness_level"],
        "present_fields": present_fields,
        "missing_fields": missing_fields,
        "present_field_count": len(present_fields),
        "missing_field_count": len(missing_fields),
        "role_compatible": package_contract["role_compatibility"]["declared"],
        "runtime_contract_declared": package_contract["runtime_contract"]["declared"],
        "share_ready": package_contract["promotion_gate"]["share_ready"],
        "promotion_status": package_contract["promotion_gate"]["status"],
        "recommended_next_fields": list(package_contract["promotion_gate"]["recommended_next_fields"]),
        "sdk_contract_missing_fields": sdk_missing_fields,
        "telemetry_confidence": (
            sdk_contract.get("evidence_providers", {}).get("telemetry_confidence")
            if isinstance(sdk_contract.get("evidence_providers"), dict)
            else None
        ),
    }


def skill_package_contract_summary(package_readiness: dict[str, Any]) -> dict[str, Any]:
    """Return the doctor-facing package contract view from package readiness."""
    package_fields = package_readiness["required_fields"]
    return {
        "present": package_fields["present"],
        "missing": package_fields["missing"],
        "values": package_readiness["values"],
        "role_compatibility": package_readiness["role_compatibility"],
        "runtime_contract": package_readiness["runtime_contract"],
        "install_gate": package_readiness["install_gate"],
        "promotion_gate": package_readiness["promotion_gate"],
        "sdk_contract": package_readiness.get("sdk_contract"),
    }


def skill_package_checkout_test(
    repo_root: Path,
    source_path: Path | None,
    audit_target: str | None,
    package_contract: dict[str, Any],
) -> dict[str, Any]:
    """Return read-only local checkout evidence for a package candidate."""
    evidence: list[str] = []
    if not source_path or not source_path.is_file():
        return {
            "required": True,
            "status": "blocked_missing_source",
            "evidence": evidence,
        }

    source_rel = repo_relative_path(repo_root, source_path) or source_path.as_posix()
    evidence.append(f"source_path:{source_rel}")
    try:
        source_path.read_text(encoding="utf-8")
    except OSError as exc:
        evidence.append("source_readable:false")
        evidence.append(f"source_read_error:{exc.__class__.__name__}")
        return {
            "required": True,
            "status": "blocked_missing_source",
            "evidence": evidence,
        }
    evidence.append("source_readable:true")
    if audit_target:
        evidence.append(f"audit_target:{audit_target}")

    missing_fields = package_contract["required_fields"]["missing"]
    blocked_reasons = package_contract["install_gate"]["blocked_reasons"]
    if blocked_reasons:
        if missing_fields:
            evidence.append(f"missing_package_metadata:{','.join(missing_fields)}")
        else:
            evidence.append(f"promotion_gate_blocked:{','.join(blocked_reasons)}")
        return {
            "required": True,
            "status": "blocked_validation",
            "evidence": evidence,
        }

    evidence.append("package_metadata_complete:true")
    return {
        "required": True,
        "status": "pass",
        "evidence": evidence,
    }


def capability_metadata_status(frontmatter: dict[str, Any]) -> dict[str, Any]:
    """Return a non-blocking metadata readiness summary for one skill source."""
    required_fields = ("name", "description")
    capability_fields = (
        "skill-type",
        "lifecycle_state",
        "maturity",
        "owner",
        "metadata_source",
    )
    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}

    present_required = sorted(field for field in required_fields if frontmatter.get(field))
    missing_required = sorted(field for field in required_fields if not frontmatter.get(field))
    present_capability = sorted(field for field in capability_fields if metadata.get(field))
    missing_capability = sorted(field for field in capability_fields if not metadata.get(field))

    package_readiness = skill_package_readiness(frontmatter)
    package_fields = package_readiness["required_fields"]
    missing_package = package_fields["missing"]

    readiness_level = "package_ready" if not missing_package else "capability_declared"
    if missing_capability:
        readiness_level = "legacy_frontmatter"
    if missing_required:
        readiness_level = "incomplete"

    return {
        "status": "pass" if not missing_required else "warning",
        "readiness_level": readiness_level,
        "required_fields": {
            "present": present_required,
            "missing": missing_required,
        },
        "capability_contract": {
            "present": present_capability,
            "missing": missing_capability,
            "values": {field: metadata.get(field) for field in present_capability},
        },
        "package_contract": skill_package_contract_summary(package_readiness),
        "package_readiness": package_readiness,
        "note": "Package/share metadata gaps are reported as contract gaps, not current blockers.",
    }
