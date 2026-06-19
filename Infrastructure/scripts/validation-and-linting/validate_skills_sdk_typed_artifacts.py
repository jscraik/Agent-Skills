#!/usr/bin/env python3
"""Validate Skills SDK typed artifact contract guardrails."""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


FORBIDDEN_ROOT_PACKAGE_FILES = (
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "pyproject.toml",
    "poetry.lock",
    "uv.lock",
)

ALLOWED_INFRASTRUCTURE_PACKAGE_FILES = (
    "Infrastructure/pyproject.toml",
    "Infrastructure/uv.lock",
)

NO_ANY_PUBLIC_CONTRACT_MODULES = (
    "Infrastructure/scripts/lib/ask/skills_sdk/typed_contracts.py",
    "Infrastructure/scripts/lib/ask/skills_sdk/schema_validation.py",
    "Infrastructure/scripts/lib/ask/envelope.py",
)

FIXTURE_MANIFEST_PATH = "Infrastructure/tests/fixtures/skills_sdk/typed_artifacts/fixture-manifest.json"
VALID_FIXTURE_ORIGINS = {
    "real_emitter",
    "schema_positive",
    "schema_negative",
    "visual_projection",
    "source_artifact",
}

SKILLS_SDK_CHANGED_PREFIXES = (
    "Infrastructure/config/schemas/skills-sdk/",
    "Infrastructure/scripts/lib/ask/skills_sdk/",
    "Infrastructure/tests/fixtures/skills_sdk/",
)

SKILLS_SDK_CHANGED_EXACT = {
    "Infrastructure/scripts/lib/ask/envelope.py",
}

SKILLS_SDK_CHANGED_GLOBS = (
    "Infrastructure/scripts/lib/ask/commands/*.py",
    "Infrastructure/tests/test_skills_sdk*.py",
    ".harness/specs/*skills-sdk*.md",
    ".harness/plan/*skills-sdk*.md",
    ".harness/implementation-notes/*skills-sdk*",
    "artifacts/*skills-sdk*.html",
)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    path: str


@dataclass(frozen=True)
class ValidationCheck:
    id: str
    status: str
    summary: str
    issues: tuple[ValidationIssue, ...] = ()


def _repo_relative(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def _normalize_changed_path(path: str) -> str:
    return path.strip().replace("\\", "/").removeprefix("./")


def is_skills_sdk_changed_path(path: str) -> bool:
    normalized = _normalize_changed_path(path)
    if not normalized:
        return False
    if normalized in SKILLS_SDK_CHANGED_EXACT:
        return True
    if any(normalized.startswith(prefix) for prefix in SKILLS_SDK_CHANGED_PREFIXES):
        return True
    return any(Path(normalized).match(pattern) for pattern in SKILLS_SDK_CHANGED_GLOBS)


def validate_root_package_boundary(repo_root: Path) -> ValidationCheck:
    issues: list[ValidationIssue] = []
    for name in FORBIDDEN_ROOT_PACKAGE_FILES:
        candidate = repo_root / name
        if candidate.exists():
            issues.append(
                ValidationIssue(
                    code="skills_sdk_root_package_manager_forbidden",
                    message=(
                        "Skills SDK Python typing must stay under Infrastructure/pyproject.toml; "
                        "the repository root must not grow a package-manager manifest or lockfile."
                    ),
                    path=_repo_relative(candidate, repo_root),
                )
            )

    for name in ALLOWED_INFRASTRUCTURE_PACKAGE_FILES:
        candidate = repo_root / name
        if not candidate.exists():
            issues.append(
                ValidationIssue(
                    code="skills_sdk_infrastructure_package_manager_missing",
                    message="Infrastructure-level Python manifest and lockfile are required for SDK typing.",
                    path=name,
                )
            )

    if issues:
        return ValidationCheck(
            id="root_package_boundary",
            status="fail",
            summary="root package-manager boundary is violated",
            issues=tuple(issues),
        )

    return ValidationCheck(
        id="root_package_boundary",
        status="pass",
        summary="root package-manager boundary is enforced",
    )


def validate_no_any_contract_modules(repo_root: Path) -> ValidationCheck:
    issues: list[ValidationIssue] = []
    for relative_path in NO_ANY_PUBLIC_CONTRACT_MODULES:
        path = repo_root / relative_path
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative_path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == "Any":
                issues.append(
                    ValidationIssue(
                        code="skills_sdk_public_contract_any_forbidden",
                        message="Public Skills SDK contract modules must use explicit object narrowing, not Any.",
                        path=f"{relative_path}:{node.lineno}",
                    )
                )
            if isinstance(node, ast.Attribute) and node.attr == "Any":
                issues.append(
                    ValidationIssue(
                        code="skills_sdk_public_contract_any_forbidden",
                        message="Public Skills SDK contract modules must use explicit object narrowing, not Any.",
                        path=f"{relative_path}:{node.lineno}",
                    )
                )

    if issues:
        return ValidationCheck(
            id="no_any_public_contracts",
            status="fail",
            summary="public contract modules use Any",
            issues=tuple(issues),
        )

    return ValidationCheck(
        id="no_any_public_contracts",
        status="pass",
        summary="public contract modules avoid Any",
    )


def validate_fixture_provenance(repo_root: Path) -> ValidationCheck:
    manifest_path = repo_root / FIXTURE_MANIFEST_PATH
    issues: list[ValidationIssue] = []
    if not manifest_path.exists():
        return ValidationCheck(
            id="fixture_provenance",
            status="fail",
            summary="fixture provenance sidecar is missing",
            issues=(
                ValidationIssue(
                    code="skills_sdk_fixture_manifest_missing",
                    message="Typed artifact fixtures must declare sidecar provenance.",
                    path=FIXTURE_MANIFEST_PATH,
                ),
            ),
        )

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    fixtures = payload.get("fixtures")
    if not isinstance(fixtures, list):
        issues.append(
            ValidationIssue(
                code="skills_sdk_fixture_manifest_invalid",
                message="Fixture manifest must contain a fixtures array.",
                path=FIXTURE_MANIFEST_PATH,
            )
        )
        fixtures = []

    for index, entry in enumerate(fixtures):
        path_label = f"{FIXTURE_MANIFEST_PATH}:fixtures[{index}]"
        if not isinstance(entry, dict):
            issues.append(
                ValidationIssue(
                    code="skills_sdk_fixture_manifest_invalid",
                    message="Fixture entry must be an object.",
                    path=path_label,
                )
            )
            continue
        fixture_path = entry.get("path")
        origin = entry.get("origin")
        schema_version = entry.get("schema_version")
        source_class = entry.get("source_artifact_class")
        rationale = entry.get("static_fixture_rationale")
        if origin not in VALID_FIXTURE_ORIGINS:
            issues.append(
                ValidationIssue(
                    code="skills_sdk_fixture_origin_invalid",
                    message="Fixture origin must be one of the accepted provenance origins.",
                    path=path_label,
                )
            )
        if not isinstance(schema_version, str) or not schema_version:
            issues.append(
                ValidationIssue(
                    code="skills_sdk_fixture_schema_version_missing",
                    message="Fixture entry must record a schema version.",
                    path=path_label,
                )
            )
        if not isinstance(source_class, str) or not source_class:
            issues.append(
                ValidationIssue(
                    code="skills_sdk_fixture_source_class_missing",
                    message="Fixture entry must record a source artifact class.",
                    path=path_label,
                )
            )
        if not isinstance(rationale, str) or not rationale:
            issues.append(
                ValidationIssue(
                    code="skills_sdk_fixture_rationale_missing",
                    message="Static fixtures must explain why they are static.",
                    path=path_label,
                )
            )
        if not isinstance(fixture_path, str) or not (repo_root / fixture_path).exists():
            issues.append(
                ValidationIssue(
                    code="skills_sdk_fixture_path_missing",
                    message="Fixture entry path must exist in the repo.",
                    path=path_label,
                )
            )

    if issues:
        return ValidationCheck(
            id="fixture_provenance",
            status="fail",
            summary="fixture provenance sidecar is invalid",
            issues=tuple(issues),
        )

    return ValidationCheck(
        id="fixture_provenance",
        status="pass",
        summary="fixture provenance sidecar is valid",
    )


def validate_changed_path_classifier(paths: Iterable[str]) -> ValidationCheck:
    normalized_paths = tuple(_normalize_changed_path(path) for path in paths if _normalize_changed_path(path))
    matched = tuple(path for path in normalized_paths if is_skills_sdk_changed_path(path))
    if not normalized_paths:
        return ValidationCheck(
            id="changed_path_classifier",
            status="pass",
            summary="no changed paths supplied; full validation remains eligible",
        )
    if matched:
        return ValidationCheck(
            id="changed_path_classifier",
            status="pass",
            summary=f"{len(matched)} Skills SDK changed path(s) matched",
        )
    return ValidationCheck(
        id="changed_path_classifier",
        status="pass",
        summary="changed paths supplied, but none belong to the Skills SDK typed artifact lane",
    )


def _read_changed_files(path: Path) -> tuple[str, ...]:
    return tuple(line.rstrip("\n") for line in path.read_text(encoding="utf-8").splitlines())


def _json_payload(checks: Sequence[ValidationCheck]) -> dict[str, object]:
    issue_count = sum(len(check.issues) for check in checks)
    return {
        "schema_version": "skills-sdk.typed-artifact-validation.v1",
        "status": "fail" if issue_count else "pass",
        "issue_count": issue_count,
        "checks": [asdict(check) for check in checks],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--changed-files", nargs="*", default=())
    parser.add_argument("--changed-files-from")
    args = parser.parse_args(argv)

    changed_files = tuple(args.changed_files)
    if args.changed_files_from:
        changed_files = changed_files + _read_changed_files(Path(args.changed_files_from))

    repo_root = Path(args.repo_root).resolve()
    checks = (
        validate_root_package_boundary(repo_root),
        validate_no_any_contract_modules(repo_root),
        validate_fixture_provenance(repo_root),
        validate_changed_path_classifier(changed_files),
    )
    payload = _json_payload(checks)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for check in checks:
            print(f"{check.status}: {check.id}: {check.summary}")
            for issue in check.issues:
                print(f"{issue.path}: {issue.code}: {issue.message}", file=sys.stderr)

    return 1 if payload["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
