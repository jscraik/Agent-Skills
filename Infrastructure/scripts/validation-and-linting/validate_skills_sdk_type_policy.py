#!/usr/bin/env python3
"""Enforce the Skills SDK schema/type policy.

JSON Schemas remain the public compatibility authority. This validator is a
small migration gate: it rejects new handwritten ``NewType`` public values,
unbranded identity fields in changed schemas, and new unitless duration
annotations. Existing legacy duration fields remain visible until their owner
slice migrates them to ``duration.v1``. A clean full-repository invocation
validates every tracked Skills SDK schema and emitter surface; legacy fields
are allowed only when the same path and annotation already existed in the
parent commit.
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
ID_FIELD_NAMES = frozenset({"receipt_instance_id", "trace_id", "request_id", "experiment_id"})
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
        if (path := line.strip()) and (path.endswith(".schema.json") or path.endswith(".py"))
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
    return _walk_schema_identity(payload, path, "$", expected_pattern, brands, legacy_patterns)


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
    brands = id_contract.get("brands") if isinstance(id_contract.get("brands"), dict) else {}
    legacy_patterns = (
        id_contract.get("legacy_compatibility_patterns")
        if isinstance(id_contract.get("legacy_compatibility_patterns"), dict)
        else {}
    )
    return expected_pattern, brands, legacy_patterns


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
            if isinstance(name, str) and name in ID_FIELD_NAMES and isinstance(child, dict):
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
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and (
            (isinstance(node.func, ast.Name) and node.func.id == "NewType")
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
            issues.extend(_duration_annotation_issue(node, path, legacy_duration_fields, repo_root))
    return issues


def _duration_annotation_issue(
    node: ast.AnnAssign | ast.arg,
    path: str,
    legacy_duration_fields: set[str],
    repo_root: Path,
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
    if name in legacy_duration_fields and _legacy_annotation_exists_in_parent(repo_root, path, name, annotation):
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
    return any(isinstance(node, ast.Name) and node.id in {"int", "float"} for node in ast.walk(annotation))


def _annotation_keys(tree: ast.AST) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.annotation is not None:
            keys.add((node.target.id, ast.unparse(node.annotation)))
        elif isinstance(node, ast.arg) and node.annotation is not None:
            keys.add((node.arg, ast.unparse(node.annotation)))
    return keys


def _legacy_annotation_exists_in_parent(repo_root: Path, path: str, name: str, annotation: ast.AST) -> bool:
    result = subprocess.run(
        ["git", "rev-list", "--parents", "-n", "1", "HEAD"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return False
    for parent in result.stdout.split()[1:]:
        baseline_result = subprocess.run(
            ["git", "show", f"{parent}:{path}"],
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if baseline_result.returncode != 0:
            continue
        try:
            baseline = ast.parse(baseline_result.stdout, filename=path)
        except SyntaxError:
            continue
        if (name, ast.unparse(annotation)) in _annotation_keys(baseline):
            return True
    return False


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
