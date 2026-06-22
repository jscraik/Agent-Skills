from __future__ import annotations

import json
from pathlib import Path
import re
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
    section_declared = bool(body)
    references_declared = existing_count > 0
    return {
        "skill_md_line_count": line_count,
        "skill_md_under_500_lines": line_count <= 500 if text else False,
        "skill_md_under_250_lines": compact_entrypoint,
        "progressive_disclosure_declared": section_declared,
        "progressive_disclosure_reference_count": existing_count,
        "progressive_disclosure_missing_references": missing,
        "progressive_disclosure_ready": (
            compact_entrypoint
            and section_declared
            and references_declared
            and not missing
        ),
        "progressive_disclosure_policy": (
            "Keep SKILL.md as the compact entrypoint and route task-specific "
            "details to existing references."
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
    return {
        "count": len(files),
        "filenames_kebab_case": not bad_names,
        "generic_names": [repo_relative_path(repo_root, path) or path.as_posix() for path in generic_names],
        "missing_descriptions": [
            repo_relative_path(repo_root, path) or path.as_posix() for path in missing_descriptions
        ],
        "description_coverage_count": len(files) - len(missing_descriptions),
        "ready": not unsafe_paths and not bad_names and not generic_names and not missing_descriptions,
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
    manifest_declared = bool(manifest_path and manifest_path.is_file())
    capsule_paths: list[str] = []
    if manifest_path and manifest_path.is_file():
        manifest, error = read_structured_reference(manifest_path)
        if error is None and isinstance(manifest, dict):
            capsules = manifest.get("capsules")
            if isinstance(capsules, list):
                capsule_paths = _knowledge_capsule_target_paths(capsules)
        if not capsule_paths:
            capsule_paths = _knowledge_capsule_target_paths_from_text(manifest_path)
    routing_declared = bool(routing_path and routing_path.is_file())
    routing_text = skill_markdown_text(routing_path) if routing_path else ""
    missing_from_routing = [
        path for path in capsule_paths
        if routing_declared and path and path not in routing_text
    ]
    skill_mentions_routing = "knowledge-capsule-routing.md" in text
    ready = (
        not manifest_declared
        or (
            routing_declared
            and skill_mentions_routing
            and bool(capsule_paths)
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
        "first_party_routing_path": (
            repo_relative_path(repo_root, routing_path) if repo_root and routing_path else None
        ),
        "first_party_routing_declared": routing_declared,
        "skill_mentions_first_party_routing": skill_mentions_routing,
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
        try:
            text = candidate.read_text(encoding="utf-8")
        except OSError as exc:
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
    tessl_policy = reference_contract.get("tessl_scenario_policy")
    if isinstance(tessl_policy, dict) and not (
        tessl_policy.get("structure_only") is True
        or tessl_policy.get("structure_check_only") is True
    ):
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
    reference_quality = sdk_contract["values"].get("reference_quality")
    reference_blockers: list[str] = []
    if (
        isinstance(reference_quality, dict)
        and reference_quality.get("required_for_package_readiness") is True
        and reference_quality.get("status") == "blocked_validation"
    ):
        reference_blockers = [
            f"reference_quality:{blocker.get('rule_id', 'blocked_validation')}"
            for blocker in reference_quality.get("blockers", [])
            if isinstance(blocker, dict)
        ] or ["reference_quality:blocked_validation"]
        blocked_reasons.extend(reference_blockers)
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
