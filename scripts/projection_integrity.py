#!/usr/bin/env python3
"""Synchronize and verify canonical projection trees and aliases."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

SCHEMA_VERSION = "projection-parity.v1"
HEADER_TOKEN = "GENERATED PROJECTION:"
IGNORED_FILE_NAMES = {".DS_Store"}
IGNORED_DIR_NAMES = {"__pycache__"}
IGNORED_SUFFIXES = {".pyc"}
STAMPABLE_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".toml", ".py", ".sh"}
SCOPE_CHOICES = ("all", "skill-factory", "plugin-factory", "plugin-caches")


@dataclass(frozen=True)
class SymlinkProjection:
    name: str
    alias_path: str
    canonical_path: str
    tags: tuple[str, ...]


@dataclass(frozen=True)
class MirrorProjection:
    name: str
    source_path: str
    projection_path: str
    tags: tuple[str, ...]


SYMLINK_PROJECTIONS: tuple[SymlinkProjection, ...] = (
    SymlinkProjection(
        name="skill-factory-skill-builder-alias",
        alias_path="utilities/skill-builder",
        canonical_path="plugins/skill-factory/skills/skill-builder",
        tags=("skill-factory",),
    ),
    SymlinkProjection(
        name="skill-factory-skillify-alias",
        alias_path="utilities/skillify",
        canonical_path="plugins/skill-factory/skills/skillify",
        tags=("skill-factory",),
    ),
    SymlinkProjection(
        name="skill-factory-skill-creator-alias",
        alias_path="skills-system/skill-creator",
        canonical_path="plugins/skill-factory/skills/skill-creator",
        tags=("skill-factory",),
    ),
    SymlinkProjection(
        name="skill-factory-skill-installer-alias",
        alias_path="skills-system/skill-installer",
        canonical_path="plugins/skill-factory/skills/skill-installer",
        tags=("skill-factory",),
    ),
    SymlinkProjection(
        name="plugin-factory-plugin-builder-alias",
        alias_path="utilities/plugin-builder",
        canonical_path="plugins/plugin-factory/skills/plugin-builder",
        tags=("plugin-factory",),
    ),
    SymlinkProjection(
        name="plugin-factory-plugin-creator-alias",
        alias_path="skills-system/plugin-creator",
        canonical_path="plugins/plugin-factory/skills/plugin-creator",
        tags=("plugin-factory",),
    ),
    SymlinkProjection(
        name="plugin-factory-plugin-installer-alias",
        alias_path="skills-system/plugin-installer",
        canonical_path="plugins/plugin-factory/skills/plugin-installer",
        tags=("plugin-factory",),
    ),
)

MIRROR_PROJECTIONS: tuple[MirrorProjection, ...] = (
    MirrorProjection(
        name="cache-arscontexta",
        source_path="plugins/arscontexta",
        projection_path="plugins/cache/agent-skills-local/arscontexta/local",
        tags=("plugin-caches",),
    ),
    MirrorProjection(
        name="cache-coderabbit",
        source_path="plugins/coderabbit",
        projection_path="plugins/cache/agent-skills-local/coderabbit/local",
        tags=("plugin-caches",),
    ),
    MirrorProjection(
        name="cache-harness-engineering",
        source_path="plugins/harness-engineering",
        projection_path="plugins/cache/agent-skills-local/harness-engineering/local",
        tags=("plugin-caches",),
    ),
    MirrorProjection(
        name="cache-plugin-factory",
        source_path="plugins/plugin-factory",
        projection_path="plugins/cache/agent-skills-local/plugin-factory/local",
        tags=("plugin-caches", "plugin-factory"),
    ),
    MirrorProjection(
        name="cache-skill-factory",
        source_path="plugins/skill-factory",
        projection_path="plugins/cache/agent-skills-local/skill-factory/local",
        tags=("plugin-caches", "skill-factory"),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("sync", "verify"), help="Operation mode.")
    parser.add_argument(
        "--scope",
        default="all",
        choices=SCOPE_CHOICES,
        help="Projection scope to process.",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repo root override (defaults to parent of this script).",
    )
    parser.add_argument(
        "--manifest-out",
        default=None,
        help="Optional JSON report output path.",
    )
    parser.add_argument(
        "--format",
        default="text",
        choices=("text", "json"),
        help="Console output format.",
    )
    return parser.parse_args()


def is_ignored(path: Path) -> bool:
    if path.name in IGNORED_FILE_NAMES:
        return True
    if path.suffix in IGNORED_SUFFIXES:
        return True
    return any(part in IGNORED_DIR_NAMES for part in path.parts)


def iter_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(root)
        if is_ignored(rel):
            continue
        yield rel


def hash_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def hash_text(content: str) -> str:
    return hash_bytes(content.encode("utf-8"))


def manifest_digest(entries: dict[str, str]) -> str:
    serialized = "".join(f"{path}\t{digest}\n" for path, digest in sorted(entries.items()))
    return hash_text(serialized)


def projection_header_for(rel_source_path: str, suffix: str) -> str:
    if suffix == ".md":
        return f"<!-- {HEADER_TOKEN} source={rel_source_path}; DO NOT EDIT PROJECTION COPY. -->"
    return f"# {HEADER_TOKEN} source={rel_source_path}; DO NOT EDIT PROJECTION COPY."


def strip_projection_header(text: str, suffix: str) -> tuple[str, bool]:
    lines = text.splitlines(keepends=True)
    if not lines:
        return text, False

    def remove_at(index: int) -> tuple[str, bool]:
        if index < 0 or index >= len(lines):
            return text, False
        if HEADER_TOKEN not in lines[index]:
            return text, False
        new_lines = lines[:index] + lines[index + 1 :]
        if index < len(new_lines) and new_lines[index].strip() == "":
            new_lines = new_lines[:index] + new_lines[index + 1 :]
        return "".join(new_lines), True

    if suffix == ".md":
        if lines[0].strip() == "---":
            for idx in range(1, len(lines)):
                if lines[idx].strip() == "---":
                    if idx + 1 < len(lines) and HEADER_TOKEN in lines[idx + 1]:
                        return remove_at(idx + 1)
                    break
        if HEADER_TOKEN in lines[0]:
            return remove_at(0)
        return text, False

    if lines[0].startswith("#!"):
        if len(lines) > 1 and HEADER_TOKEN in lines[1]:
            return remove_at(1)
        return text, False

    if HEADER_TOKEN in lines[0]:
        return remove_at(0)
    return text, False


def apply_projection_header(text: str, rel_source_path: str, suffix: str) -> str:
    stripped, _ = strip_projection_header(text, suffix)
    header = projection_header_for(rel_source_path, suffix)
    lines = stripped.splitlines(keepends=True)
    if not lines:
        return f"{header}\n"

    if suffix == ".md":
        if lines[0].strip() == "---":
            for idx in range(1, len(lines)):
                if lines[idx].strip() == "---":
                    insert_at = idx + 1
                    out = lines[:insert_at] + [f"{header}\n", "\n"] + lines[insert_at:]
                    return "".join(out)
        return "".join([f"{header}\n", "\n", *lines])

    if lines[0].startswith("#!"):
        out = [lines[0], f"{header}\n", "\n", *lines[1:]]
        return "".join(out)

    return "".join([f"{header}\n", "\n", *lines])


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def ensure_symlink(repo_root: Path, spec: SymlinkProjection) -> dict[str, object]:
    alias_abs = repo_root / spec.alias_path
    canonical_abs = repo_root / spec.canonical_path
    alias_abs.parent.mkdir(parents=True, exist_ok=True)
    if not canonical_abs.is_dir():
        return {
            "name": spec.name,
            "type": "symlink",
            "status": "error",
            "reason": "canonical_missing",
            "alias": spec.alias_path,
            "canonical": spec.canonical_path,
        }
    rel_target = os.path.relpath(canonical_abs, alias_abs.parent)
    status = "synced"
    changed = False

    if alias_abs.exists() or alias_abs.is_symlink():
        if alias_abs.is_symlink():
            current_target = os.readlink(alias_abs)
            current_abs = (alias_abs.parent / current_target).resolve()
            if current_abs == canonical_abs.resolve():
                return {
                    "name": spec.name,
                    "type": "symlink",
                    "status": "ok",
                    "alias": spec.alias_path,
                    "canonical": spec.canonical_path,
                    "target": current_target,
                    "changed": False,
                }
            alias_abs.unlink()
            changed = True
        elif alias_abs.is_dir():
            return {
                "name": spec.name,
                "type": "symlink",
                "status": "error",
                "reason": "alias_requires_manual_migration",
                "alias": spec.alias_path,
                "canonical": spec.canonical_path,
            }
        else:
            alias_abs.unlink()
            changed = True

    alias_abs.symlink_to(rel_target, target_is_directory=True)
    if changed:
        status = "replaced"
    return {
        "name": spec.name,
        "type": "symlink",
        "status": status,
        "alias": spec.alias_path,
        "canonical": spec.canonical_path,
        "target": rel_target,
        "changed": True,
    }


def verify_symlink(repo_root: Path, spec: SymlinkProjection) -> dict[str, object]:
    alias_abs = repo_root / spec.alias_path
    canonical_abs = repo_root / spec.canonical_path
    if not canonical_abs.is_dir():
        return {
            "name": spec.name,
            "type": "symlink",
            "status": "drift",
            "reason": "canonical_missing",
            "alias": spec.alias_path,
            "canonical": spec.canonical_path,
        }
    if not alias_abs.exists() and not alias_abs.is_symlink():
        return {
            "name": spec.name,
            "type": "symlink",
            "status": "drift",
            "reason": "alias_missing",
            "alias": spec.alias_path,
            "canonical": spec.canonical_path,
        }
    if not alias_abs.is_symlink():
        return {
            "name": spec.name,
            "type": "symlink",
            "status": "drift",
            "reason": "alias_not_symlink",
            "alias": spec.alias_path,
            "canonical": spec.canonical_path,
        }
    current_target = os.readlink(alias_abs)
    current_abs = (alias_abs.parent / current_target).resolve()
    if current_abs != canonical_abs.resolve():
        return {
            "name": spec.name,
            "type": "symlink",
            "status": "drift",
            "reason": "wrong_target",
            "alias": spec.alias_path,
            "canonical": spec.canonical_path,
            "target": current_target,
        }
    return {
        "name": spec.name,
        "type": "symlink",
        "status": "pass",
        "alias": spec.alias_path,
        "canonical": spec.canonical_path,
        "target": current_target,
    }


def sync_mirror(repo_root: Path, spec: MirrorProjection) -> dict[str, object]:
    source_abs = repo_root / spec.source_path
    projection_abs = repo_root / spec.projection_path
    if not source_abs.is_dir():
        return {
            "name": spec.name,
            "type": "mirror",
            "status": "error",
            "reason": "source_missing",
            "source": spec.source_path,
            "projection": spec.projection_path,
        }

    projection_abs.parent.mkdir(parents=True, exist_ok=True)
    sync_engine = "python"
    changed_files = 0
    deleted_files = 0
    if projection_abs.exists() and not projection_abs.is_dir():
        projection_abs.unlink()
    projection_abs.mkdir(parents=True, exist_ok=True)

    rsync_bin = shutil.which("rsync")
    if rsync_bin:
        sync_engine = "rsync"
        before_files = {rel.as_posix() for rel in iter_files(projection_abs)}
        subprocess.run(
            [
                rsync_bin,
                "-a",
                "--delete",
                "--exclude",
                "__pycache__/",
                "--exclude",
                "*.pyc",
                "--exclude",
                ".DS_Store",
                f"{source_abs}/",
                f"{projection_abs}/",
            ],
            check=True,
        )
        after_files = {rel.as_posix() for rel in iter_files(projection_abs)}
        deleted_files = len(before_files - after_files)
        changed_files = -1
    else:
        source_files = {rel.as_posix(): rel for rel in iter_files(source_abs)}
        projection_files = {rel.as_posix(): rel for rel in iter_files(projection_abs)}

        for rel_key in sorted(set(projection_files) - set(source_files)):
            stale = projection_abs / projection_files[rel_key]
            stale.unlink()
            deleted_files += 1

        for rel_key, rel in source_files.items():
            source_file = source_abs / rel
            projection_file = projection_abs / rel
            projection_file.parent.mkdir(parents=True, exist_ok=True)
            if source_file.is_symlink():
                source_target = os.readlink(source_file)
                if projection_file.is_symlink() and os.readlink(projection_file) == source_target:
                    continue
                if projection_file.exists() or projection_file.is_symlink():
                    projection_file.unlink()
                projection_file.symlink_to(source_target)
                changed_files += 1
                continue

            source_bytes = source_file.read_bytes()
            if projection_file.exists() and projection_file.is_file() and projection_file.read_bytes() == source_bytes:
                continue
            if projection_file.exists() or projection_file.is_symlink():
                projection_file.unlink()
            projection_file.write_bytes(source_bytes)
            changed_files += 1

        for path in sorted(projection_abs.rglob("*"), reverse=True):
            if path.is_dir() and not path.is_symlink():
                try:
                    path.rmdir()
                except OSError:
                    continue

    stamped_files = 0
    for rel in iter_files(projection_abs):
        if rel.suffix not in STAMPABLE_SUFFIXES:
            continue
        projection_file = projection_abs / rel
        source_rel = (Path(spec.source_path) / rel).as_posix()
        try:
            original = read_text(projection_file)
        except UnicodeDecodeError:
            continue
        updated = apply_projection_header(original, source_rel, rel.suffix)
        if updated != original:
            write_text(projection_file, updated)
        stamped_files += 1

    return {
        "name": spec.name,
        "type": "mirror",
        "status": "synced",
        "source": spec.source_path,
        "projection": spec.projection_path,
        "sync_engine": sync_engine,
        "changed_files": changed_files,
        "deleted_files": deleted_files,
        "stamped_files": stamped_files,
    }


def verify_mirror(repo_root: Path, spec: MirrorProjection) -> dict[str, object]:
    source_abs = repo_root / spec.source_path
    projection_abs = repo_root / spec.projection_path
    result: dict[str, object] = {
        "name": spec.name,
        "type": "mirror",
        "source": spec.source_path,
        "projection": spec.projection_path,
    }
    if not source_abs.is_dir():
        result.update({"status": "drift", "reason": "source_missing"})
        return result
    if not projection_abs.is_dir():
        result.update({"status": "drift", "reason": "projection_missing"})
        return result

    source_files = {rel.as_posix(): rel for rel in iter_files(source_abs)}
    projection_files = {rel.as_posix(): rel for rel in iter_files(projection_abs)}
    source_manifest_hashes = {
        rel_key: hash_bytes((source_abs / rel).read_bytes()) for rel_key, rel in source_files.items()
    }
    projection_manifest_hashes: dict[str, str] = {}
    for rel_key, rel in projection_files.items():
        projection_bytes = (projection_abs / rel).read_bytes()
        if rel.suffix not in STAMPABLE_SUFFIXES:
            projection_manifest_hashes[rel_key] = hash_bytes(projection_bytes)
            continue
        try:
            projection_text = projection_bytes.decode("utf-8")
        except UnicodeDecodeError:
            projection_manifest_hashes[rel_key] = hash_bytes(projection_bytes)
            continue
        normalized_projection, _ = strip_projection_header(projection_text, rel.suffix)
        projection_manifest_hashes[rel_key] = hash_text(normalized_projection)

    missing_in_projection = sorted(set(source_files) - set(projection_files))
    extra_in_projection = sorted(set(projection_files) - set(source_files))
    mismatched_files: list[dict[str, str]] = []
    unstamped_files: list[str] = []

    for rel_key in sorted(set(source_files) & set(projection_files)):
        rel = source_files[rel_key]
        source_file = source_abs / rel
        projection_file = projection_abs / rel
        source_bytes = source_file.read_bytes()
        projection_bytes = projection_file.read_bytes()

        if rel.suffix in STAMPABLE_SUFFIXES:
            try:
                source_text = source_bytes.decode("utf-8")
                projection_text = projection_bytes.decode("utf-8")
            except UnicodeDecodeError:
                mismatched_files.append(
                    {
                        "path": rel_key,
                        "reason": "expected_utf8_projection_text",
                        "source_sha256": hash_bytes(source_bytes),
                        "projection_sha256": hash_bytes(projection_bytes),
                    }
                )
                continue

            normalized_projection, had_header = strip_projection_header(projection_text, rel.suffix)
            if not had_header:
                unstamped_files.append(rel_key)
            if source_text != normalized_projection:
                mismatched_files.append(
                    {
                        "path": rel_key,
                        "reason": "content_mismatch",
                        "source_sha256": hash_bytes(source_bytes),
                        "projection_sha256": hash_bytes(projection_bytes),
                    }
                )
        else:
            if source_bytes != projection_bytes:
                mismatched_files.append(
                    {
                        "path": rel_key,
                        "reason": "binary_mismatch",
                        "source_sha256": hash_bytes(source_bytes),
                        "projection_sha256": hash_bytes(projection_bytes),
                    }
                )

    source_manifest_sha = manifest_digest(source_manifest_hashes)
    projection_manifest_sha = manifest_digest(projection_manifest_hashes)
    manifest_mismatch = source_manifest_sha != projection_manifest_sha

    result.update(
        {
            "policy": "hash-manifest-plus-path-diff",
            "missing_in_projection": missing_in_projection,
            "extra_in_projection": extra_in_projection,
            "mismatched_files": mismatched_files,
            "unstamped_files": unstamped_files,
            "checked_files": len(source_files),
            "source_manifest_sha256": source_manifest_sha,
            "projection_manifest_sha256": projection_manifest_sha,
            "manifest_mismatch": manifest_mismatch,
        }
    )
    is_pass = (
        not missing_in_projection
        and not extra_in_projection
        and not mismatched_files
        and not unstamped_files
        and not manifest_mismatch
    )
    result["status"] = "pass" if is_pass else "drift"
    return result


def select_symlinks(scope: str) -> tuple[SymlinkProjection, ...]:
    if scope == "all":
        return SYMLINK_PROJECTIONS
    return tuple(spec for spec in SYMLINK_PROJECTIONS if scope in spec.tags)


def select_mirrors(scope: str) -> tuple[MirrorProjection, ...]:
    if scope == "all":
        return MIRROR_PROJECTIONS
    return tuple(spec for spec in MIRROR_PROJECTIONS if scope in spec.tags)


def write_manifest(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def render_text(payload: dict[str, object]) -> str:
    lines = [
        f"[projection-integrity] schema: {payload['schema_version']}",
        f"[projection-integrity] mode: {payload['mode']}",
        f"[projection-integrity] scope: {payload['scope']}",
        f"[projection-integrity] status: {payload['status']}",
    ]
    for entry in payload.get("results", []):
        name = entry.get("name", "unknown")
        status = entry.get("status", "unknown")
        entry_type = entry.get("type", "unknown")
        lines.append(f"- {name} ({entry_type}): {status}")
        if status in {"drift", "error"}:
            reason = entry.get("reason")
            if isinstance(reason, str) and reason:
                lines.append(f"    reason: {reason}")
            if entry.get("manifest_mismatch") is True:
                lines.append("    manifest_mismatch: true")
            for key in ("missing_in_projection", "extra_in_projection", "unstamped_files"):
                values = entry.get(key)
                if isinstance(values, list) and values:
                    lines.append(f"    {key}: {len(values)}")
            mismatches = entry.get("mismatched_files")
            if isinstance(mismatches, list) and mismatches:
                lines.append(f"    mismatched_files: {len(mismatches)}")
    return "\n".join(lines)


def run_sync(repo_root: Path, scope: str) -> dict[str, object]:
    results: list[dict[str, object]] = []
    for spec in select_symlinks(scope):
        results.append(ensure_symlink(repo_root, spec))
    for spec in select_mirrors(scope):
        results.append(sync_mirror(repo_root, spec))

    status = "pass"
    if any(entry.get("status") == "error" for entry in results):
        status = "fail"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "sync",
        "scope": scope,
        "status": status,
        "results": results,
    }


def run_verify(repo_root: Path, scope: str) -> dict[str, object]:
    results: list[dict[str, object]] = []
    for spec in select_symlinks(scope):
        results.append(verify_symlink(repo_root, spec))
    for spec in select_mirrors(scope):
        results.append(verify_mirror(repo_root, spec))

    status = "pass"
    if any(entry.get("status") not in {"pass", "ok"} for entry in results):
        status = "fail"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "verify",
        "scope": scope,
        "status": status,
        "results": results,
    }


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[1]
    payload = run_sync(repo_root, args.scope) if args.mode == "sync" else run_verify(repo_root, args.scope)

    if args.manifest_out:
        manifest_path = Path(args.manifest_out)
        if not manifest_path.is_absolute():
            manifest_path = repo_root / manifest_path
        write_manifest(manifest_path, payload)

    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(render_text(payload))

    if payload["status"] == "fail":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
