#!/usr/bin/env python3
"""Enforce the Skills SDK schema/type policy.

JSON Schemas remain the public compatibility authority. This validator is a
small migration gate: it rejects new handwritten ``NewType`` public values,
unbranded identity fields in changed schemas, and new unitless duration
annotations. Existing legacy duration fields remain visible until their owner
slice migrates them to ``duration.v1``. A clean full-repository invocation
validates every tracked Skills SDK schema and emitter surface; legacy fields
are allowed only when the same path and annotation already existed in the
merge-base (or the first-parent baseline when the merge-base ref is unavailable).
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


POLICY_PATH = "Infrastructure/config/schemas/skills-sdk/type-policy.v1.json"
DURATION_FIELD_NAMES = frozenset(
    {
        "timeout_seconds",
        "ttl_seconds",
        "duration_seconds",
        "stability_seconds",
        "stability_interval_seconds",
        "cooldown_seconds",
    }
)
_TOKEN_ALPHABET_PATTERNS = {"lowercase_ascii_alphanumeric": "[a-z0-9]"}
_BRANDED_PREFIX_PATTERN = r"[a-z][a-z0-9]{0,15}"


@dataclass(frozen=True)
class PolicyIssue:
    code: str
    message: str
    path: str


def _load_policy(repo_root: Path) -> dict[str, object]:
    payload = json.loads((repo_root / POLICY_PATH).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("type policy must be a JSON object")
    return payload


def _policy_surface_paths(repo_root: Path) -> tuple[str, ...]:
    result = subprocess.run(
        ["git", "ls-files", "--", "Infrastructure/config/schemas/skills-sdk", "Infrastructure/scripts/lib/ask"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"unable to enumerate tracked Skills SDK policy surfaces: {result.stderr.strip()}")
    return tuple(
        path
        for line in result.stdout.splitlines()
        if (path := line.strip())
        and (path == POLICY_PATH or path.endswith(".schema.json") or path.endswith(".py"))
    )


def _is_public_schema(path: str) -> bool:
    return path.startswith("Infrastructure/config/schemas/skills-sdk/") and path.endswith(".schema.json")


def _schema_identity_issues(repo_root: Path, path: str, policy: dict[str, object]) -> list[PolicyIssue]:
    if not _is_public_schema(path):
        return []
    schema_path = repo_root / path
    if not schema_path.exists():
        return [PolicyIssue("type_policy_path_missing", "changed schema path does not exist", path)]
    payload = json.loads(schema_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return [PolicyIssue("type_policy_schema_invalid", "changed schema must be a JSON object", path)]
    details = _identity_contract_details(repo_root, policy)
    if isinstance(details, list):
        return details
    expected_pattern, brands, legacy_patterns = details
    return [
        *_walk_schema_identity(payload, path, "$", expected_pattern, brands, legacy_patterns),
        *_schema_duration_issues(repo_root, path, payload, policy),
    ]


def _identity_contract_details(
    repo_root: Path, policy: dict[str, object]
) -> tuple[str, dict[str, object], dict[str, object]] | list[PolicyIssue]:
    id_contract = policy.get("id_contract")
    if not isinstance(id_contract, dict):
        return [PolicyIssue("type_policy_invalid", "id_contract is missing from the policy", POLICY_PATH)]
    id_schema_path = id_contract.get("schema_path")
    if not isinstance(id_schema_path, str):
        return [PolicyIssue("type_policy_invalid", "id_contract.schema_path must be a string", POLICY_PATH)]
    id_schema = repo_root / id_schema_path
    if not id_schema.exists():
        return [PolicyIssue("type_policy_path_missing", "branded ID schema path does not exist", id_schema_path)]
    id_schema_payload = json.loads(id_schema.read_text(encoding="utf-8"))
    expected_pattern = id_schema_payload.get("pattern") if isinstance(id_schema_payload, dict) else None
    if not isinstance(expected_pattern, str):
        return [PolicyIssue("type_policy_invalid", "branded ID schema must declare a string pattern", id_schema_path)]
    canonical_pattern = _canonical_branded_id_pattern(id_contract)
    if isinstance(canonical_pattern, PolicyIssue):
        return [canonical_pattern]
    if expected_pattern != canonical_pattern:
        return [
            PolicyIssue(
                "type_policy_invalid",
                "branded ID schema pattern must match the declared alphabet and token-length contract",
                id_schema_path,
            )
        ]
    brands = id_contract.get("brands") if isinstance(id_contract.get("brands"), dict) else {}
    legacy_patterns = (
        id_contract.get("legacy_compatibility_patterns")
        if isinstance(id_contract.get("legacy_compatibility_patterns"), dict)
        else {}
    )
    return expected_pattern, brands, legacy_patterns


def _canonical_branded_id_pattern(id_contract: dict[str, object]) -> str | PolicyIssue:
    alphabet = id_contract.get("token_alphabet")
    token_pattern = _TOKEN_ALPHABET_PATTERNS.get(alphabet) if isinstance(alphabet, str) else None
    minimum = id_contract.get("minimum_token_length")
    maximum = id_contract.get("maximum_token_length")
    if token_pattern is None or not isinstance(minimum, int) or isinstance(minimum, bool) or not isinstance(maximum, int) or isinstance(maximum, bool):
        return PolicyIssue("type_policy_invalid", "id_contract must declare a supported token alphabet and integer token lengths", POLICY_PATH)
    if minimum < 1 or maximum < minimum:
        return PolicyIssue("type_policy_invalid", "id_contract token lengths must define a positive inclusive range", POLICY_PATH)
    return f"^{_BRANDED_PREFIX_PATTERN}_{token_pattern}{{{minimum},{maximum}}}$"


def _walk_schema_identity(
    node: object,
    path: str,
    node_path: str,
    expected_pattern: str,
    brands: dict[str, object],
    legacy_patterns: dict[str, object],
) -> list[PolicyIssue]:
    if not isinstance(node, dict):
        return []
    issues: list[PolicyIssue] = []
    properties = node.get("properties")
    if isinstance(properties, dict):
        for name, child in properties.items():
            if isinstance(name, str) and name in brands and isinstance(child, dict):
                issues.extend(_identity_property_issues(path, node_path, name, child, expected_pattern, brands, legacy_patterns))
            issues.extend(_walk_schema_identity(child, path, f"{node_path}.{name}", expected_pattern, brands, legacy_patterns))
    issues.extend(_walk_schema_children(node, path, node_path, expected_pattern, brands, legacy_patterns))
    return issues


def _identity_property_issues(
    path: str,
    node_path: str,
    name: str,
    child: dict[str, object],
    expected_pattern: str,
    brands: dict[str, object],
    legacy_patterns: dict[str, object],
) -> list[PolicyIssue]:
    brand = brands.get(name)
    branded_pattern = f"^{brand}_[a-z0-9]{{12,32}}$" if isinstance(brand, str) else expected_pattern
    allowed = {branded_pattern} if isinstance(brand, str) else {expected_pattern}
    compatibility = legacy_patterns.get(name)
    if isinstance(compatibility, list):
        allowed.update(item for item in compatibility if isinstance(item, str))
    declared_pattern = child.get("pattern")
    if not _is_string_schema_type(child.get("type")):
        return [
            PolicyIssue(
                "identity_schema_type",
                f"{name} must declare JSON Schema type string",
                f"{path}:{node_path}.{name}",
            )
        ]
    if declared_pattern in allowed:
        return []
    return [
        PolicyIssue(
            "unbranded_identity_schema",
            f"{name} must use the canonical branded-id pattern",
            f"{path}:{node_path}.{name}",
        )
    ]


def _is_string_schema_type(value: object) -> bool:
    if value == "string":
        return True
    return isinstance(value, list) and all(isinstance(item, str) for item in value) and set(value) == {"string", "null"}


def _walk_schema_children(
    node: dict[str, object],
    path: str,
    node_path: str,
    expected_pattern: str,
    brands: dict[str, object],
    legacy_patterns: dict[str, object],
) -> list[PolicyIssue]:
    issues: list[PolicyIssue] = []
    for key in ("items", "definitions", "$defs", "oneOf", "allOf", "anyOf", "if", "then", "else"):
        child = node.get(key)
        if key in {"definitions", "$defs"} and isinstance(child, dict):
            for definition_name, definition in child.items():
                issues.extend(_walk_schema_identity(definition, path, f"{node_path}.{key}.{definition_name}", expected_pattern, brands, legacy_patterns))
        elif isinstance(child, dict):
            issues.extend(_walk_schema_identity(child, path, f"{node_path}.{key}", expected_pattern, brands, legacy_patterns))
        elif isinstance(child, list):
            for index, item in enumerate(child):
                issues.extend(_walk_schema_identity(item, path, f"{node_path}.{key}[{index}]", expected_pattern, brands, legacy_patterns))
    return issues


def _python_policy_issues(repo_root: Path, path: str, policy: dict[str, object]) -> list[PolicyIssue]:
    if not path.endswith(".py"):
        return []
    candidate = repo_root / path
    if not candidate.exists():
        return [PolicyIssue("type_policy_path_missing", "changed Python path does not exist", path)]
    try:
        tree = ast.parse(candidate.read_text(encoding="utf-8"), filename=path)
    except SyntaxError as exc:
        return [PolicyIssue("type_policy_python_invalid", str(exc), path)]
    return _python_tree_issues(tree, path, _legacy_duration_fields(policy), repo_root)


def _legacy_duration_fields(policy: dict[str, object]) -> set[str]:
    duration_contract = policy.get("duration_contract")
    if isinstance(duration_contract, dict) and isinstance(duration_contract.get("legacy_compatibility_fields"), list):
        return {item for item in duration_contract["legacy_compatibility_fields"] if isinstance(item, str)}
    return set(DURATION_FIELD_NAMES)


def _python_tree_issues(
    tree: ast.AST,
    path: str,
    legacy_duration_fields: set[str],
    repo_root: Path,
) -> list[PolicyIssue]:
    issues: list[PolicyIssue] = []
    newtype_aliases = _newtype_aliases(tree)
    parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and (
            (isinstance(node.func, ast.Name) and node.func.id in newtype_aliases)
            or (isinstance(node.func, ast.Attribute) and node.func.attr == "NewType")
        ):
            issues.append(
                PolicyIssue(
                    "manual_newtype_forbidden",
                    "public SDK values must be schema-derived; handwritten NewType aliases are forbidden",
                    f"{path}:{node.lineno}",
                )
            )
        if isinstance(node, (ast.AnnAssign, ast.arg)):
            issues.extend(_duration_annotation_issue(node, path, legacy_duration_fields, repo_root, _annotation_owner(node, parents)))
    return issues


def _newtype_aliases(tree: ast.AST) -> set[str]:
    aliases = {"NewType"}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or node.module not in {"typing", "typing_extensions"}:
            continue
        for imported in node.names:
            if imported.name == "NewType":
                aliases.add(imported.asname or imported.name)
    return aliases


def _duration_annotation_issue(
    node: ast.AnnAssign | ast.arg,
    path: str,
    legacy_duration_fields: set[str],
    repo_root: Path,
    owner_path: tuple[str, ...],
) -> list[PolicyIssue]:
    if isinstance(node, ast.AnnAssign):
        if isinstance(node.target, ast.Name):
            name = node.target.id
        elif isinstance(node.target, ast.Attribute):
            name = node.target.attr
        else:
            return []
    else:
        name = node.arg
    if not name.endswith("_seconds"):
        return []
    annotation = node.annotation
    if annotation is None or not _contains_raw_numeric(annotation):
        return []
    if name in legacy_duration_fields and _legacy_annotation_exists_in_parent(repo_root, path, name, annotation, owner_path=owner_path):
        return []
    rendered_annotation = ast.unparse(annotation)
    return [
        PolicyIssue(
            "unitless_duration_annotation",
            f"{name} must use a schema-backed duration value; raw {rendered_annotation} is forbidden on new surfaces",
            f"{path}:{node.lineno}",
        )
    ]


def _contains_raw_numeric(annotation: ast.AST) -> bool:
    return any(
        (isinstance(node, ast.Name) and node.id in {"int", "float"})
        or (isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value.strip() in {"int", "float"})
        for node in ast.walk(annotation)
    )


def _annotation_owner(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> tuple[str, ...]:
    owners: list[str] = []
    current = parents.get(node)
    while current is not None:
        if isinstance(current, (ast.AsyncFunctionDef, ast.ClassDef, ast.FunctionDef)):
            owners.append(current.name)
        current = parents.get(current)
    return tuple(reversed(owners))


def _annotation_keys(tree: ast.AST) -> set[tuple[tuple[str, ...], str, str]]:
    keys: set[tuple[tuple[str, ...], str, str]] = set()
    parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and node.annotation is not None:
            target = node.target
            if isinstance(target, ast.Name):
                name = target.id
            elif isinstance(target, ast.Attribute):
                name = target.attr
            else:
                name = None
            if name is not None:
                keys.add((_annotation_owner(node, parents), name, ast.unparse(node.annotation)))
        elif isinstance(node, ast.arg) and node.annotation is not None:
            keys.add((_annotation_owner(node, parents), node.arg, ast.unparse(node.annotation)))
    return keys


def _legacy_annotation_exists_in_parent(
    repo_root: Path,
    path: str,
    name: str,
    annotation: ast.AST,
    *,
    owner_path: tuple[str, ...] = (),
) -> bool:
    """Allow a legacy annotation only when it exists in the PR base baseline."""
    baseline = _baseline_source_tree(repo_root, path)
    return baseline is not None and (owner_path, name, ast.unparse(annotation)) in _annotation_keys(baseline)


def _baseline_revision(repo_root: Path) -> str:
    merge_base = subprocess.run(
        ["git", "merge-base", "HEAD", "origin/main"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if merge_base.returncode == 0 and merge_base.stdout.strip():
        return merge_base.stdout.strip()
    first_parent = subprocess.run(
        ["git", "rev-parse", "HEAD^1"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return first_parent.stdout.strip() if first_parent.returncode == 0 else ""


def _baseline_source_tree(repo_root: Path, path: str) -> ast.AST | None:
    revision = _baseline_revision(repo_root)
    if not revision:
        return None
    result = subprocess.run(
        ["git", "show", f"{revision}:{path}"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    try:
        return ast.parse(result.stdout, filename=path)
    except SyntaxError:
        return None


def _resolve_local_schema_ref(node: object, root: object) -> object:
    if not isinstance(node, dict):
        return node
    reference = node.get("$ref")
    if not isinstance(reference, str) or not reference.startswith("#/"):
        return node
    current = root
    for raw_part in reference[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or part not in current:
            return node
        current = current[part]
    return current


def _schema_declares_numeric_type(declared_type: object) -> bool:
    if isinstance(declared_type, str):
        return declared_type in {"integer", "number"}
    return isinstance(declared_type, list) and any(item in {"integer", "number"} for item in declared_type)


def _schema_combinator_items(node: dict[str, object]) -> tuple[object, ...]:
    return tuple(
        item
        for key in ("oneOf", "anyOf", "allOf")
        for item in (node.get(key) if isinstance(node.get(key), list) else ())
    )


def _schema_has_numeric_type(node: object, root: object | None = None, seen_refs: frozenset[str] = frozenset()) -> bool:
    if not isinstance(node, dict):
        return False
    root = node if root is None else root
    reference = node.get("$ref")
    if isinstance(reference, str) and reference not in seen_refs:
        resolved = _resolve_local_schema_ref(node, root)
        if resolved is not node and _schema_has_numeric_type(resolved, root, seen_refs | {reference}):
            return True
    return _schema_declares_numeric_type(node.get("type")) or any(
        _schema_has_numeric_type(item, root, seen_refs) for item in _schema_combinator_items(node)
    )


def _schema_duration_property_entries(
    properties: object, node_path: str, root: object
) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    if not isinstance(properties, dict):
        return result
    for name, child in properties.items():
        child_path = f"{node_path}.properties.{name}"
        if (
            isinstance(name, str)
            and name.endswith("_seconds")
            and isinstance(child, dict)
            and _schema_has_numeric_type(child, root)
        ):
            result[child_path] = child
        result.update(_schema_duration_properties(child, child_path, root))
    return result


def _schema_duration_branch_entries(
    child: object, key: str, node_path: str, root: object
) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    if isinstance(child, dict):
        entries = child.items() if key in {"definitions", "$defs"} else ((key, child),)
        for name, definition in entries:
            branch_path = f"{node_path}.{key}.{name}" if key in {"definitions", "$defs"} else f"{node_path}.{key}"
            result.update(_schema_duration_properties(definition, branch_path, root))
    elif isinstance(child, list):
        for index, item in enumerate(child):
            result.update(_schema_duration_properties(item, f"{node_path}.{key}[{index}]", root))
    return result


def _schema_duration_properties(
    node: object, node_path: str = "$", root: object | None = None
) -> dict[str, dict[str, object]]:
    if not isinstance(node, dict):
        return {}
    root = node if root is None else root
    result = _schema_duration_property_entries(node.get("properties"), node_path, root)
    for key in ("items", "definitions", "$defs", "oneOf", "allOf", "anyOf", "if", "then", "else"):
        result.update(_schema_duration_branch_entries(node.get(key), key, node_path, root))
    return result


def _schema_duration_issues(repo_root: Path, path: str, payload: dict[str, object], policy: dict[str, object]) -> list[PolicyIssue]:
    duration_contract = policy.get("duration_contract")
    if not isinstance(duration_contract, dict) or not duration_contract.get("unitless_numeric_duration_fields_are_forbidden_on_new_surfaces", False):
        return []
    current = _schema_duration_properties(payload)
    if not current:
        return []
    baseline: dict[str, dict[str, object]] = {}
    baseline_revision = _baseline_revision(repo_root)
    if baseline_revision:
        result = subprocess.run(
            ["git", "show", f"{baseline_revision}:{path}"],
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode == 0:
            try:
                baseline_payload = json.loads(result.stdout)
            except json.JSONDecodeError:
                baseline_payload = None
            if isinstance(baseline_payload, dict):
                baseline = _schema_duration_properties(baseline_payload)
    return [
        PolicyIssue(
            "unitless_duration_schema_property",
            f"{node_path} must use the schema-backed duration object instead of a new numeric *_seconds property",
            f"{path}:{node_path}",
        )
        for node_path in current
        if node_path not in baseline
    ]


def _read_duration_schema(repo_root: Path, policy: dict[str, object]) -> tuple[str | None, dict[str, object] | None, PolicyIssue | None]:
    duration_contract = policy.get("duration_contract")
    if not isinstance(duration_contract, dict):
        return None, None, None
    schema_path = duration_contract.get("schema_path")
    if not isinstance(schema_path, str):
        return None, None, None
    schema_file = repo_root / schema_path
    if not schema_file.exists():
        return schema_path, None, None
    try:
        schema = json.loads(schema_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return schema_path, None, PolicyIssue("duration_schema_contract_invalid", "duration schema must be valid JSON", schema_path)
    if not isinstance(schema, dict):
        return schema_path, None, PolicyIssue("duration_schema_contract_invalid", "duration schema must be a JSON object", schema_path)
    return schema_path, schema, None


def _duration_schema_field_issues(schema: dict[str, object], contract: dict[str, object], schema_path: str) -> list[PolicyIssue]:
    required = schema.get("required")
    properties = schema.get("properties")
    value = properties.get("value") if isinstance(properties, dict) else None
    unit = properties.get("unit") if isinstance(properties, dict) else None
    issues = []
    if not isinstance(required, list) or not {"value", "unit"}.issubset(required):
        issues.append(PolicyIssue("duration_schema_required", "duration schema must require value and unit", schema_path))
    if not isinstance(value, dict) or value.get("minimum") != contract.get("value_minimum"):
        issues.append(PolicyIssue("duration_schema_value_minimum", "duration schema value.minimum must match duration_contract.value_minimum", schema_path))
    if not isinstance(unit, dict) or unit.get("enum") != contract.get("units"):
        issues.append(PolicyIssue("duration_schema_units", "duration schema unit enum must match duration_contract.units", schema_path))
    return issues


def _duration_schema_contract_issues(repo_root: Path, policy: dict[str, object]) -> list[PolicyIssue]:
    schema_path, schema, load_issue = _read_duration_schema(repo_root, policy)
    if load_issue is not None:
        return [load_issue]
    if schema is None or schema_path is None:
        return []
    contract = policy["duration_contract"]
    issues = []
    if schema.get("type") != contract.get("representation"):
        issues.append(PolicyIssue("duration_schema_representation", "duration schema type must match duration_contract.representation", schema_path))
    issues.extend(_duration_schema_field_issues(schema, contract, schema_path))
    return issues


def _policy_issues(repo_root: Path, policy: dict[str, object]) -> list[PolicyIssue]:
    issues: list[PolicyIssue] = []
    identity_details = _identity_contract_details(repo_root, policy)
    if isinstance(identity_details, list):
        issues.extend(identity_details)

    duration_contract = policy.get("duration_contract")
    if not isinstance(duration_contract, dict):
        issues.append(PolicyIssue("type_policy_invalid", "duration_contract is missing from the policy", POLICY_PATH))
    else:
        duration_schema_path = duration_contract.get("schema_path")
        if not isinstance(duration_schema_path, str):
            issues.append(PolicyIssue("type_policy_invalid", "duration_contract.schema_path must be a string", POLICY_PATH))
        elif not (repo_root / duration_schema_path).exists():
            issues.append(PolicyIssue("type_policy_path_missing", "duration schema path does not exist", duration_schema_path))
        legacy_fields = duration_contract.get("legacy_compatibility_fields")
        if not isinstance(legacy_fields, list) or not all(isinstance(field, str) for field in legacy_fields):
            issues.append(PolicyIssue("type_policy_invalid", "duration_contract.legacy_compatibility_fields must be a string list", POLICY_PATH))
        issues.extend(_duration_schema_contract_issues(repo_root, policy))
    return issues


def validate_paths(repo_root: Path, paths: Iterable[str]) -> tuple[PolicyIssue, ...]:
    policy = _load_policy(repo_root)
    issues: list[PolicyIssue] = []
    for path in paths:
        normalized = path.strip().replace("\\", "/").removeprefix("./")
        if not normalized:
            continue
        if normalized == POLICY_PATH:
            issues.extend(_policy_issues(repo_root, policy))
        else:
            issues.extend(_schema_identity_issues(repo_root, normalized, policy))
            issues.extend(_python_policy_issues(repo_root, normalized, policy))
    return tuple(issues)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--changed-files", nargs="*", default=())
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    paths = tuple(args.changed_files) or _policy_surface_paths(repo_root)
    issues = validate_paths(repo_root, paths)
    payload = {
        "schema_version": "skills-sdk.type-policy-validation.v1",
        "status": "fail" if issues else "pass",
        "changed_files": list(paths),
        "issues": [asdict(issue) for issue in issues],
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"{payload['status']}: {len(issues)} issue(s)")
        for issue in issues:
            print(f"{issue.path}: {issue.code}: {issue.message}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
