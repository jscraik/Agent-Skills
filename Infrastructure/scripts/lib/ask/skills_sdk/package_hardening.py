from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any


PACKAGE_HARDENING_RECEIPT_SCHEMA_VERSION = "skills-sdk.package-hardening-receipt.v0"
PACKAGE_HARDENING_RECEIPT_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/package-hardening-receipt.v0.schema.json"
)
PACKAGE_HARDENING_ACCEPTANCE_TRACE = ["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022"]
MAX_PACKAGE_FILE_COUNT = 250
MAX_PACKAGE_TOTAL_BYTES = 5 * 1024 * 1024

_FORBIDDEN_PATH_PARTS = {
    ".agents",
    ".cache",
    ".codex",
    ".git",
    ".harness",
    ".plugin-appserver",
    "__pycache__",
    "artifacts",
    "dist",
    "node_modules",
}
_FORBIDDEN_FILENAMES = {
    ".env",
    ".env.local",
    ".envrc",
    ".netrc",
    ".npmrc",
    "id_rsa",
    "id_ed25519",
}
_FORBIDDEN_SUFFIXES = (".pem", ".key", ".p12", ".pfx")
_REQUIRED_PROVENANCE = {"SkillIR.v0", "canonical-source"}


def _check(
    check_id: str,
    status: str,
    severity: str,
    message: str,
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": check_id,
        "status": status,
        "severity": severity,
        "message": message,
        "evidence": evidence or [],
    }


def _forbidden_reason(path: str) -> str | None:
    parsed = PurePosixPath(path)
    parts = parsed.parts
    if parsed.is_absolute():
        return "forbidden_absolute_path"
    if any(part == ".." for part in parts):
        return "forbidden_parent_relative_path"
    lowered_parts = [part.lower() for part in parts]
    if any(part in _FORBIDDEN_PATH_PARTS for part in lowered_parts):
        return "forbidden_path_part"
    name = (lowered_parts[-1] if lowered_parts else path.lower())
    if name in _FORBIDDEN_FILENAMES:
        return "forbidden_filename"
    if name.startswith(".env."):
        return "forbidden_env_family"
    if name.endswith(_FORBIDDEN_SUFFIXES):
        return "forbidden_secret_suffix"
    return None


def _file_paths(receipt: dict[str, Any]) -> list[str]:
    manifest = receipt.get("manifest")
    if not isinstance(manifest, dict):
        return []
    files = manifest.get("files")
    if not isinstance(files, list):
        return []
    paths: list[str] = []
    for item in files:
        if isinstance(item, dict) and isinstance(item.get("path"), str):
            paths.append(item["path"])
    return paths


def _manifest(package_receipt: dict[str, Any]) -> dict[str, Any]:
    manifest = package_receipt.get("manifest")
    return manifest if isinstance(manifest, dict) else {}


def _manifest_files(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    files = manifest.get("files")
    if not isinstance(files, list):
        return []
    return [item for item in files if isinstance(item, dict)]


def _total_size(manifest_files: list[dict[str, Any]]) -> int:
    return sum(item.get("size_bytes", 0) for item in manifest_files)


def _non_mutating_check(package_receipt: dict[str, Any]) -> dict[str, Any]:
    mutation_performed = package_receipt.get("mutation_performed")
    return _check(
        "non_mutating_package_identity",
        "pass" if mutation_performed is False else "blocker",
        "blocker",
        "Package hardening requires a read-only package digest receipt.",
        [f"mutation_performed:{mutation_performed!s}"],
    )


def _forbidden_paths_check(included_files: list[str]) -> dict[str, Any]:
    forbidden = [
        {"path": path, "reason": reason}
        for path in included_files
        for reason in [_forbidden_reason(path)]
        if reason is not None
    ]
    return _check(
        "forbidden_package_paths",
        "pass" if not forbidden else "blocker",
        "blocker",
        "Package manifest must not include local runtime, generated artifact, dependency, or secret-bearing paths.",
        [f"{item['path']}:{item['reason']}" for item in forbidden],
    )


def _size_budget_check(manifest_files: list[dict[str, Any]], total_size: int) -> dict[str, Any]:
    within_budget = len(manifest_files) <= MAX_PACKAGE_FILE_COUNT and total_size <= MAX_PACKAGE_TOTAL_BYTES
    return _check(
        "package_size_budget",
        "pass" if within_budget else "warning",
        "warning",
        "Package contents should stay inside the read-only hardening budget before archive emission is approved.",
        [f"files:{len(manifest_files)}", f"total_size_bytes:{total_size}"],
    )


def _provenance_check(manifest: dict[str, Any]) -> dict[str, Any]:
    provenance = manifest.get("provenance")
    provenance_sources = provenance.get("source") if isinstance(provenance, dict) else []
    provenance_set = set(provenance_sources) if isinstance(provenance_sources, list) else set()
    return _check(
        "provenance_trace",
        "pass" if _REQUIRED_PROVENANCE.issubset(provenance_set) else "blocker",
        "blocker",
        "Package hardening requires SkillIR and canonical-source provenance.",
        [str(item) for item in sorted(provenance_set)],
    )


def _skill_role_check(manifest_files: list[dict[str, Any]]) -> dict[str, Any]:
    roles = sorted(
        {
            str(item.get("role"))
            for item in manifest_files
            if isinstance(item.get("role"), str)
        }
    )
    return _check(
        "required_skill_manifest_role",
        "pass" if "skill_md" in roles else "blocker",
        "blocker",
        "Package manifest must include a skill_md role.",
        roles,
    )


def _readme_role_check(manifest_files: list[dict[str, Any]]) -> dict[str, Any]:
    roles = sorted(
        {
            str(item.get("role"))
            for item in manifest_files
            if isinstance(item.get("role"), str)
        }
    )
    return _check(
        "required_registry_readme_role",
        "pass" if "readme" in roles else "blocker",
        "blocker",
        "Skills SDK packages must include README.md as registry presentation; agent runtime instructions remain in SKILL.md.",
        roles,
    )


def _hardening_checks(
    package_receipt: dict[str, Any],
    manifest: dict[str, Any],
    manifest_files: list[dict[str, Any]],
    included_files: list[str],
    total_size: int,
) -> list[dict[str, Any]]:
    return [
        _non_mutating_check(package_receipt),
        _forbidden_paths_check(included_files),
        _size_budget_check(manifest_files, total_size),
        _provenance_check(manifest),
        _skill_role_check(manifest_files),
        _readme_role_check(manifest_files),
    ]


def build_package_hardening_receipt(package_receipt: dict[str, Any]) -> dict[str, Any]:
    """Build a read-only package hardening receipt from a package digest receipt."""
    manifest = _manifest(package_receipt)
    manifest_files = _manifest_files(manifest)
    included_files = [path for path in _file_paths(package_receipt)]
    total_size = _total_size(manifest_files)
    checks = _hardening_checks(package_receipt, manifest, manifest_files, included_files, total_size)
    blockers = [check for check in checks if check["status"] == "blocker"]
    warnings = [check for check in checks if check["status"] == "warning"]
    status = "blocked" if blockers else "pass"

    return {
        "schema_version": PACKAGE_HARDENING_RECEIPT_SCHEMA_VERSION,
        "schema_uri": PACKAGE_HARDENING_RECEIPT_SCHEMA_URI,
        "status": status,
        "package_id": str(package_receipt.get("package_id") or ""),
        "version": str(package_receipt.get("version") or ""),
        "source_digest": str(package_receipt.get("source_digest") or ""),
        "manifest_digest": str(package_receipt.get("manifest_digest") or ""),
        "package_digest": str(package_receipt.get("package_digest") or ""),
        "included_files": included_files,
        "file_count": len(manifest_files),
        "total_size_bytes": total_size,
        "hardening_checks": checks,
        "blockers": blockers,
        "warnings": warnings,
        "mutation_performed": False,
        "acceptance_trace": PACKAGE_HARDENING_ACCEPTANCE_TRACE,
    }
