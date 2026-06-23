from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ask.skills_sdk.ir import build_skill_ir


PACKAGE_MANIFEST_SCHEMA_VERSION = "skills-sdk.package-manifest.v0"
PACKAGE_MANIFEST_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/package-manifest.v0.schema.json"
)
PACKAGE_DIGEST_RECEIPT_SCHEMA_VERSION = "skills-sdk.package-digest-receipt.v0"
PACKAGE_DIGEST_RECEIPT_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/package-digest-receipt.v0.schema.json"
)
PACKAGE_DIGEST_ACCEPTANCE_TRACE = ["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022"]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _external_path_label(package_root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(package_root.resolve(strict=False)).as_posix()
    except ValueError:
        return path.name


def _record_path(repo_root: Path, path_ref: str, package_root: Path | None) -> tuple[Path, str]:
    raw_path = Path(path_ref)
    path = raw_path if raw_path.is_absolute() else repo_root / raw_path
    label = _external_path_label(package_root, path) if package_root else path_ref
    return path, label


def _file_record(repo_root: Path, relative_path: str, role: str, package_root: Path | None = None) -> dict[str, Any]:
    path, record_path = _record_path(repo_root, relative_path, package_root)
    return {
        "path": record_path,
        "sha256": _sha256_file(path),
        "size_bytes": path.stat().st_size,
        "role": role,
    }


def _manifest_files(repo_root: Path, ir: dict[str, Any], package_root: Path | None = None) -> list[dict[str, Any]]:
    source = ir["source"]
    candidates: list[tuple[str | None, str]] = [
        (source["skill_md"], "skill_md"),
        (source.get("readme"), "readme"),
    ]
    candidates.extend((path, "reference") for path in source["references"])
    candidates.extend((path, "script") for path in source["scripts"])
    candidates.extend((path, "asset") for path in source["assets"])
    candidates.extend((path, "eval") for path in source["evals"])
    records = [
        _file_record(repo_root, path, role, package_root)
        for path, role in candidates
        if path and _record_path(repo_root, path, package_root)[0].is_file()
    ]
    return sorted(records, key=lambda row: row["path"])


def _normalize_source_value(repo_root: Path, value: str | None, package_root: Path) -> str | None:
    if not value:
        return value
    return _record_path(repo_root, value, package_root)[1]


def _normalize_external_source_block(repo_root: Path, ir: dict[str, Any], package_root: Path) -> dict[str, Any]:
    normalized_ir = dict(ir)
    source = dict(ir["source"])
    for key in ("root", "skill_md", "readme"):
        source[key] = _normalize_source_value(repo_root, source.get(key), package_root)
    for key in ("references", "scripts", "assets", "evals"):
        source[key] = [_normalize_source_value(repo_root, path, package_root) for path in source[key]]
    normalized_ir["source"] = source
    return normalized_ir


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
    except ValueError:
        return False
    return True


def _source_digest(files: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for item in files:
        digest.update(str(item["path"]).encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(item["sha256"]).encode("utf-8"))
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def _package_manifest(ir: dict[str, Any], files: list[dict[str, Any]]) -> dict[str, Any]:
    package_id = ir["identity"]["id"]
    version = ir["identity"]["version"]
    return {
        "schema_version": PACKAGE_MANIFEST_SCHEMA_VERSION,
        "schema_uri": PACKAGE_MANIFEST_SCHEMA_URI,
        "package_id": package_id,
        "version": version,
        "skill_ir_schema_version": ir["schema_version"],
        "source": ir["source"],
        "files": files,
        "provenance": {
            "source": ["SkillIR.v0", "canonical-source"],
            "builder": "ask.skills_sdk.package_build",
        },
        "mutation_performed": False,
    }


def _package_identity(manifest: dict[str, Any], files: list[dict[str, Any]]) -> dict[str, str]:
    return {
        "package_id": manifest["package_id"],
        "version": manifest["version"],
        "source_digest": _source_digest(files),
        "manifest_digest": _sha256_json(manifest),
    }


def build_package_digest_receipt(repo_root: Path, *, source_path: Path, query: str) -> dict[str, Any]:
    """Build a non-mutating package identity receipt from SkillIR.v0."""
    source = source_path if source_path.name == "SKILL.md" else source_path / "SKILL.md"
    package_root = source.parent
    external_package_root = package_root if not _is_relative_to(package_root, repo_root) else None
    ir = build_skill_ir(repo_root, source_path=source, query=query)
    files = _manifest_files(repo_root, ir, external_package_root)
    if external_package_root:
        ir = _normalize_external_source_block(repo_root, ir, external_package_root)
    manifest = _package_manifest(ir, files)
    package_identity = _package_identity(manifest, files)
    package_id = package_identity["package_id"]
    version = package_identity["version"]
    source_digest = _source_digest(files)
    manifest_digest = _sha256_json(manifest)
    return {
        "schema_version": PACKAGE_DIGEST_RECEIPT_SCHEMA_VERSION,
        "schema_uri": PACKAGE_DIGEST_RECEIPT_SCHEMA_URI,
        "status": "built",
        "package_id": package_id,
        "version": version,
        "source_digest": source_digest,
        "manifest_digest": manifest_digest,
        "package_digest": _sha256_json(package_identity),
        "manifest": manifest,
        "included_files": [item["path"] for item in files],
        "excluded_files": [],
        "mutation_performed": False,
        "acceptance_trace": PACKAGE_DIGEST_ACCEPTANCE_TRACE,
    }
