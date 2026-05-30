from __future__ import annotations

import hashlib
import json
import stat
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from ask.skills_sdk.contracts import read_skill_frontmatter_fields
from ask.skills_sdk.package_contracts import (
    normalized_list,
    package_field_values,
    repo_relative_path,
    sdk_package_contract,
    skill_package_contract,
)


PACKAGE_VERIFY_SCHEMA_VERSION = "skill-package-verify.v1"
TRUSTED_PROVENANCE_SOURCES = {
    "agent-skills",
    "agent-skills-kit",
    "canonical-source",
    "frontmatter",
    "internal",
    "local-fixture",
    "repo-owned-fixture",
    "trusted",
}
PACKAGE_MANIFEST_NAMES = (
    "skill-package-manifest.json",
    "package-manifest.json",
    "manifest.json",
)
RUNTIME_MUTATION_SENTINELS = (
    ".agents",
    ".codex",
    "Plugins/cache",
    "runtime",
)


def _normalized_trusted_sources(trusted_sources: set[str] | None = None) -> set[str]:
    return {source.strip().lower() for source in (trusted_sources or TRUSTED_PROVENANCE_SOURCES) if source.strip()}


def _provenance_value_trusted(value: str, trusted_sources: set[str]) -> bool:
    source = value.strip().lower()
    if not source:
        return False
    if source in trusted_sources:
        return True
    parts = [part.strip() for part in source.split(":") if part.strip()]
    return len(parts) >= 3 and parts[0] == "frontmatter" and parts[-1] == "canonical-source"


def sha256_bytes(data: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(data)
    return digest.hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalize_expected_digest(expected_sha256: str | None) -> str | None:
    if not expected_sha256:
        return None
    value = expected_sha256.strip().lower()
    if value.startswith("sha256:"):
        value = value.split(":", 1)[1]
    return value or None


def _blocker(rule_id: str, message: str, *, path: str | None = None, evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    blocker: dict[str, Any] = {
        "rule_id": rule_id,
        "class": rule_id,
        "status": "blocked",
        "message": message,
    }
    if path is not None:
        blocker["path"] = path
    if evidence:
        blocker["evidence"] = evidence
    return blocker


def _check(name: str, status: str, evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": status, "evidence": evidence or {}}


def _entry_is_symlink(info: zipfile.ZipInfo) -> bool:
    mode = (info.external_attr >> 16) & 0o170000
    return stat.S_IFMT(mode) == stat.S_IFLNK


def _unsafe_archive_entry(name: str) -> str | None:
    if not name or "\x00" in name:
        return None
    normalized = name.replace("\\", "/")
    path = PurePosixPath(normalized.rstrip("/"))
    if normalized.startswith("/") or path.is_absolute():
        return "absolute_archive_path"
    if len(normalized) >= 2 and normalized[1] == ":":
        return "absolute_archive_path"
    if any(part in {"..", ""} for part in path.parts):
        return "archive_path_traversal"
    return None


def _safe_link_target(target: str) -> bool:
    if not target or "\x00" in target:
        return False
    normalized = target.replace("\\", "/")
    path = PurePosixPath(normalized)
    if path.is_absolute():
        return False
    if len(normalized) >= 2 and normalized[1] == ":":
        return False
    return not any(part in {"..", ""} for part in path.parts)


def _load_manifest(zip_file: zipfile.ZipFile) -> tuple[dict[str, Any] | None, str | None]:
    names = set(zip_file.namelist())
    for candidate in PACKAGE_MANIFEST_NAMES:
        if candidate in names:
            try:
                loaded = json.loads(zip_file.read(candidate).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                return None, candidate
            return loaded if isinstance(loaded, dict) else None, candidate
    return None, None


def _trusted_provenance(
    manifest: dict[str, Any] | None,
    trusted_sources: set[str],
) -> tuple[bool, dict[str, Any]]:
    provenance = manifest.get("provenance") if isinstance(manifest, dict) else None
    if not isinstance(provenance, dict):
        return False, {}
    sources = normalized_list(provenance.get("source") or provenance.get("sources"))
    normalized_sources = {source.strip().lower() for source in sources if source.strip()}
    trusted = any(source in trusted_sources for source in normalized_sources)
    return trusted, provenance


def _manifest_files(manifest: dict[str, Any] | None) -> list[dict[str, Any]]:
    files = manifest.get("files") if isinstance(manifest, dict) else None
    if not isinstance(files, list):
        return []
    return [item for item in files if isinstance(item, dict)]


def _read_jsonl(text: str, path: str) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            loaded = json.loads(line)
        except json.JSONDecodeError:
            entries.append({"line": line_number, "valid_json": False})
            continue
        if isinstance(loaded, dict):
            entries.append({"line": line_number, "valid_json": True, **loaded})
        else:
            entries.append({"line": line_number, "valid_json": False})
    has_decision = any(
        entry.get("action") in {"rollback", "restore", "promote", "verify"} or entry.get("decision")
        for entry in entries
    )
    return {
        "status": "pass" if entries and has_decision and all(entry.get("valid_json") for entry in entries) else "blocked_validation",
        "path": path,
        "entries": entries,
    }


def _read_external_rollback_journal(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {"status": "missing", "path": None, "entries": []}
    try:
        return _read_jsonl(path.read_text(encoding="utf-8"), path.as_posix())
    except OSError as exc:
        return {
            "status": "blocked_missing_artifact",
            "path": path.as_posix(),
            "entries": [],
            "error": exc.__class__.__name__,
        }


def _runtime_sentinels(repo_root: Path | None) -> dict[str, bool]:
    if repo_root is None:
        return {}
    return {path: (repo_root / path).exists() for path in RUNTIME_MUTATION_SENTINELS}


def verify_archive_package(
    archive_path: Path,
    *,
    expected_sha256: str | None = None,
    trusted_sources: set[str] | None = None,
    rollback_journal_path: Path | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    blockers: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []
    manifest: dict[str, Any] | None = None
    manifest_path: str | None = None
    rollback_journal: dict[str, Any] = {"status": "missing", "path": None, "entries": []}
    trusted_sources = _normalized_trusted_sources(trusted_sources)
    runtime_before = _runtime_sentinels(repo_root)
    archive_sha256 = sha256_file(archive_path) if archive_path.is_file() else None

    if not archive_path.is_file():
        blockers.append(
            _blocker(
                "blocked_missing_artifact",
                "Package archive does not exist.",
                path=archive_path.as_posix(),
            )
        )
        checks.append(_check("archive_format", "blocked", {"archive_type": None}))
    else:
        try:
            with zipfile.ZipFile(archive_path) as zip_file:
                infos = zip_file.infolist()
                names = {info.filename for info in infos}
                for info in infos:
                    unsafe_rule = _unsafe_archive_entry(info.filename)
                    entry = {
                        "path": info.filename,
                        "size": info.file_size,
                        "is_symlink": _entry_is_symlink(info),
                        "safe_path": unsafe_rule is None,
                    }
                    entries.append(entry)
                    if unsafe_rule:
                        blockers.append(
                            _blocker(
                                unsafe_rule,
                                "Archive entry would escape the staged extraction root.",
                                path=info.filename,
                            )
                        )
                    if entry["is_symlink"]:
                        try:
                            target = zip_file.read(info).decode("utf-8", errors="replace")
                        except (KeyError, OSError):
                            target = ""
                        entry["link_target"] = target
                        entry["safe_link_target"] = _safe_link_target(target)
                        if not entry["safe_link_target"]:
                            blockers.append(
                                _blocker(
                                    "archive_symlink_escape",
                                    "Archive symlink target would escape the staged extraction root.",
                                    path=info.filename,
                                    evidence={"target": target},
                                )
                            )

                manifest, manifest_path = _load_manifest(zip_file)
                if manifest_path is None:
                    blockers.append(
                        _blocker(
                            "missing_provenance_manifest",
                            "Archive does not contain a package manifest with provenance and digest rules.",
                        )
                    )
                elif manifest is None:
                    blockers.append(
                        _blocker(
                            "invalid_provenance_manifest",
                            "Archive package manifest is not valid JSON object data.",
                            path=manifest_path,
                        )
                    )

                trusted, provenance = _trusted_provenance(manifest, trusted_sources)
                if not trusted:
                    blockers.append(
                        _blocker(
                            "untrusted_provenance",
                            "Archive provenance is absent or not trusted by the local verification policy.",
                            path=manifest_path,
                        )
                    )

                for item in _manifest_files(manifest):
                    item_path = str(item.get("path") or "")
                    expected = str(item.get("sha256") or "")
                    if not item_path or item_path not in names:
                        blockers.append(
                            _blocker(
                                "manifest_file_missing",
                                "Manifest references a file that is absent from the archive.",
                                path=item_path or None,
                            )
                        )
                        continue
                    actual = sha256_bytes(zip_file.read(item_path))
                    if expected and actual != expected:
                        blockers.append(
                            _blocker(
                                "digest_mismatch",
                                "Archive file digest does not match the package manifest.",
                                path=item_path,
                                evidence={"actual_sha256": actual, "expected_sha256": expected},
                            )
                        )

                declared_rollback = None
                if isinstance(manifest, dict):
                    declared_rollback = (
                        manifest.get("rollback_journal")
                        or manifest.get("rollback_journal_path")
                        or manifest.get("rollback")
                    )
                if rollback_journal_path is not None:
                    rollback_journal = _read_external_rollback_journal(rollback_journal_path)
                elif declared_rollback:
                    rollback_journal = {
                        "status": "missing_external_journal",
                        "path": str(declared_rollback),
                        "entries": [],
                        "declared_in_manifest": True,
                    }
                if rollback_journal["status"] != "pass":
                    blockers.append(
                        _blocker(
                            "rollback_journal_missing",
                            "Archive package verification requires rollback journal evidence before mutation.",
                            path=rollback_journal.get("path"),
                            evidence={"journal_status": rollback_journal["status"]},
                        )
                    )
        except zipfile.BadZipFile:
            blockers.append(_blocker("invalid_archive", "Target is not a readable zip archive."))

        checks.append(_check("archive_format", "pass" if entries or not blockers else "fail", {"archive_type": "zip"}))

    expected_archive_sha = _normalize_expected_digest(expected_sha256)
    if expected_archive_sha is None:
        warnings.append(
            {
                "rule_id": "archive_digest_not_supplied",
                "class": "archive_digest_not_supplied",
                "message": "No expected archive sha256 was supplied; manifest file digests are still checked when present.",
            }
        )
        checks.append(_check("archive_digest_match", "warning", {"actual_sha256": archive_sha256, "expected_sha256": None}))
    elif archive_sha256 != expected_archive_sha:
        blockers.append(
            _blocker(
                "digest_mismatch",
                "Package archive sha256 does not match the expected digest.",
                evidence={"actual_sha256": archive_sha256, "expected_sha256": expected_archive_sha},
            )
        )
        checks.append(
            _check(
                "archive_digest_match",
                "fail",
                {"actual_sha256": archive_sha256, "expected_sha256": expected_archive_sha},
            )
        )
    else:
        checks.append(
            _check(
                "archive_digest_match",
                "pass",
                {"actual_sha256": archive_sha256, "expected_sha256": expected_archive_sha},
            )
        )

    rule_ids = [item["rule_id"] for item in blockers]
    checks.extend(
        [
            _check("archive_traversal", "fail" if any(rule in {"archive_path_traversal", "absolute_archive_path"} for rule in rule_ids) else "pass"),
            _check("symlink_escape", "fail" if "archive_symlink_escape" in rule_ids else "pass"),
            _check("manifest_digest_match", "fail" if "digest_mismatch" in rule_ids else "pass"),
            _check(
                "trusted_provenance",
                "fail" if "untrusted_provenance" in rule_ids or "missing_provenance_manifest" in rule_ids else "pass",
                {"manifest_path": manifest_path, "trusted_sources": sorted(trusted_sources)},
            ),
            _check("rollback_journal", "pass" if rollback_journal["status"] == "pass" else "fail", {"journal": rollback_journal}),
        ]
    )

    runtime_after = _runtime_sentinels(repo_root)
    runtime_mutations = [
        {"path": path, "before_exists": runtime_before[path], "after_exists": runtime_after[path]}
        for path in runtime_before
        if runtime_before[path] != runtime_after[path]
    ]
    if runtime_mutations:
        blockers.append(
            _blocker(
                "runtime_mutation",
                "Package verification mutated runtime/projection state.",
                evidence={"mutations": runtime_mutations},
            )
        )
    checks.append(_check("no_runtime_mutation", "fail" if runtime_mutations else "pass", {"sentinels": runtime_after}))

    status = "blocked" if blockers else "pass"
    return {
        "schema_version": PACKAGE_VERIFY_SCHEMA_VERSION,
        "target_kind": "archive",
        "target_path": archive_path.as_posix(),
        "archive_identity": {
            "path": archive_path.as_posix(),
            "sha256": archive_sha256,
            "size_bytes": archive_path.stat().st_size if archive_path.is_file() else None,
        },
        "provenance_identity": {
            "manifest_path": manifest_path,
            "trusted": not any(item["rule_id"] == "untrusted_provenance" for item in blockers),
            "policy": sorted(trusted_sources),
            "provenance": manifest.get("provenance") if isinstance(manifest, dict) else None,
        },
        "entry_count": len(entries),
        "entries": entries,
        "checks": checks,
        "blockers": blockers,
        "warnings": warnings,
        "rule_results": blockers,
        "mutation_status": {
            "status": "pass" if not runtime_mutations else "fail",
            "mutated": bool(runtime_mutations),
            "runtime_roots_mutated": bool(runtime_mutations),
            "install_attempted": False,
            "archive_extracted": False,
            "network_used": False,
        },
        "runtime_mutation": {
            "status": "pass" if not runtime_mutations else "fail",
            "mutations": runtime_mutations,
            "sentinels": runtime_after,
        },
        "rollback_journal": rollback_journal,
        "rollback_hint": "No extraction or install was performed. Fix blockers and rerun staged verification before mutation.",
        "status": status,
        "agent_summary": (
            f"Package verification blocked: {blockers[0]['message']}"
            if blockers
            else "Package verification passed without archive extraction or runtime mutation."
        ),
        "validation_commands": ["./bin/ask skills package verify <archive-or-skill> --json --robot"],
    }


def verify_skill_directory(
    repo_root: Path,
    skill_md: Path,
    query: str,
    *,
    trusted_sources: set[str] | None = None,
) -> dict[str, Any]:
    blockers: list[dict[str, Any]] = []
    trusted_sources = _normalized_trusted_sources(trusted_sources)
    frontmatter = read_skill_frontmatter_fields(skill_md)
    contract = skill_package_contract(repo_root, skill_md, frontmatter)
    sdk_contract = sdk_package_contract(repo_root, skill_md, frontmatter)
    values = package_field_values(frontmatter)
    missing = contract.get("required_fields", {}).get("missing", [])
    reference_quality = sdk_contract.get("values", {}).get("reference_quality", {})
    reference_blockers = reference_quality.get("blockers", [])
    if missing:
        blockers.append(
            _blocker(
                "skill_package_contract_incomplete",
                f"Skill package is missing required Codex metadata: {', '.join(missing)}.",
                path=repo_relative_path(repo_root, skill_md),
            )
        )
    if reference_blockers:
        first_reference_blocker = reference_blockers[0]
        blockers.append(
            _blocker(
                "reference_quality_blocked",
                "Skill references failed package-readiness quality checks.",
                path=first_reference_blocker.get("path"),
                evidence={
                    "policy": reference_quality.get("policy"),
                    "status": reference_quality.get("status"),
                    "blockers": reference_blockers,
                },
            )
        )
    provenance_values = normalized_list(values.get("provenance"))
    provenance_trusted = any(
        _provenance_value_trusted(value, trusted_sources) for value in provenance_values
    )
    if not provenance_trusted:
        blockers.append(
            _blocker(
                "untrusted_provenance",
                "Skill package has no provenance metadata for staged package verification.",
                path=repo_relative_path(repo_root, skill_md),
            )
        )
    return {
        "schema_version": PACKAGE_VERIFY_SCHEMA_VERSION,
        "target_kind": "skill_directory",
        "query": query,
        "target_path": repo_relative_path(repo_root, skill_md) or skill_md.as_posix(),
        "archive_identity": None,
        "provenance_identity": {
            "trusted": provenance_trusted,
            "policy": sorted(trusted_sources),
            "values": provenance_values,
        },
        "contract": contract,
        "sdk_contract": sdk_contract,
        "checks": [
            _check("skill_md_present", "pass", {"path": repo_relative_path(repo_root, skill_md)}),
            _check("frontmatter_read", "pass", {"fields": sorted(frontmatter)}),
            _check("package_metadata_complete", "fail" if missing else "pass", {"missing": missing}),
            _check("package_contract", "fail" if missing else "pass", {"missing": missing}),
            _check(
                "reference_quality",
                "fail" if reference_blockers else "pass",
                {
                    "status": reference_quality.get("status"),
                    "blockers": reference_blockers,
                },
            ),
            _check(
                "trusted_provenance",
                "pass" if provenance_trusted else "fail",
                {"values": provenance_values, "trusted_sources": sorted(trusted_sources)},
            ),
            _check("no_runtime_mutation", "pass", {"install_attempted": False, "archive_extracted": False}),
        ],
        "blockers": blockers,
        "rule_results": blockers,
        "mutation_status": {
            "status": "pass",
            "mutated": False,
            "runtime_roots_mutated": False,
            "install_attempted": False,
            "archive_extracted": False,
            "network_used": False,
        },
        "rollback_journal": {
            "status": "not_required",
            "reason": "Directory verification is read-only and performs no extraction or install.",
        },
        "rollback_hint": "Directory verification is read-only. Package archive verification must pass before install mutation.",
        "status": "blocked" if blockers else "pass",
        "agent_summary": (
            f"Package verification blocked: {blockers[0]['message']}"
            if blockers
            else f"{query} package verification passed without runtime mutation."
        ),
        "validation_commands": ["./bin/ask skills package verify <archive-or-skill> --json --robot"],
    }
