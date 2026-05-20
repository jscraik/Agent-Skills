#!/usr/bin/env python3
"""Synchronize and verify canonical projection trees and aliases."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import contextlib
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
    optional_when_missing: bool = False
    follow_symlinks: bool = False
    excluded_dir_names: tuple[str, ...] = ()


SYMLINK_PROJECTIONS: tuple[SymlinkProjection, ...] = (
    SymlinkProjection(
        name="plugin-factory-plugin-creator-alias",
        alias_path="skills-system/plugin-creator",
        canonical_path="Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator",
        tags=("plugin-factory",),
    ),
    SymlinkProjection(
        name="plugin-factory-plugin-installer-alias",
        alias_path="skills-system/plugin-installer",
        canonical_path="Plugins/plugin-factory/skills/infrastructure_ops/plugin-installer",
        tags=("plugin-factory",),
    ),
)

MIRROR_PROJECTIONS: tuple[MirrorProjection, ...] = (
    MirrorProjection(
        name="cache-harness-engineering",
        source_path="Plugins/harness-engineering",
        projection_path=".agents/plugins-runtime/cache/agent-skills-local/harness-engineering",
        tags=("plugin-caches",),
        optional_when_missing=True,
        follow_symlinks=True,
        excluded_dir_names=(
            "fixtures",
            "skills",
            "team_automation",
            "code_quality_review",
            "scaffolding_templates",
            "infrastructure_ops",
            "data_fetch_analysis",
        ),
    ),
    MirrorProjection(
        name="cache-plugin-factory",
        source_path="Plugins/plugin-factory",
        projection_path=".agents/plugins-runtime/cache/agent-skills-local/plugin-factory",
        tags=("plugin-caches", "plugin-factory"),
        optional_when_missing=True,
        follow_symlinks=True,
        excluded_dir_names=(
            "fixtures",
            "skills",
            "team_automation",
            "code_quality_review",
            "scaffolding_templates",
            "infrastructure_ops",
            "data_fetch_analysis",
        ),
    ),
    MirrorProjection(
        name="cache-skill-factory",
        source_path="Plugins/skill-factory",
        projection_path=".agents/plugins-runtime/cache/agent-skills-local/skill-factory",
        tags=("plugin-caches", "skill-factory"),
        optional_when_missing=True,
        follow_symlinks=True,
        excluded_dir_names=(
            "fixtures",
            "skills",
            "team_automation",
            "code_quality_review",
            "scaffolding_templates",
            "infrastructure_ops",
            "data_fetch_analysis",
        ),
    ),
)


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the projection integrity CLI.

    Recognises positional `mode` (`sync` or `verify`) and options to select `--scope`, override `--repo-root`, write a JSON `--manifest-out`, and choose output `--format` (`text` or `json`).

    Returns:
        argparse.Namespace: Parsed arguments with attributes `mode`, `scope`, `repo_root`, `manifest_out`, and `format`.
    """
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


def default_repo_root(script_path: Path) -> Path:
    """
    Resolve the repository root for this script path.

    Prefers the nearest ancestor containing `.git` (works for normal repos and
    worktrees). Falls back to an ancestor that contains both `Infrastructure/`
    and `scripts/`, then to the top-level ancestor.
    """
    resolved = script_path.resolve()
    for candidate in resolved.parents:
        if (candidate / ".git").exists():
            return candidate
    for candidate in resolved.parents:
        if (candidate / "Infrastructure").is_dir() and (candidate / "scripts").is_dir():
            return candidate
    # Return the top-level ancestor (repository root)
    return resolved.parents[3] if len(resolved.parents) > 3 else resolved.parents[-1]


def normalize_excluded_dir_names(excluded_dir_names: Iterable[str]) -> tuple[str, ...]:
    """
    Return a stable, lower-cased tuple of directory names excluded from scans.

    Parameters:
        excluded_dir_names (Iterable[str]): Directory names to treat as ignored.

    Returns:
        tuple[str, ...]: Unique lowercase names in first-seen order.
    """
    seen: set[str] = set()
    normalized: list[str] = []
    for raw_name in excluded_dir_names:
        name = str(raw_name).strip().lower()
        if not name or name in seen:
            continue
        seen.add(name)
        normalized.append(name)
    return tuple(normalized)


def is_ignored(path: Path, excluded_dir_names: Iterable[str] = ()) -> bool:
    """
    Decides whether a filesystem path should be skipped by the projection scanner.

    Parameters:
        path (Path): Path to test; may be a file or directory path.

    Returns:
        True if the path's name is in IGNORED_FILE_NAMES, its suffix is in IGNORED_SUFFIXES,
        or any path component is in IGNORED_DIR_NAMES; `False` otherwise.
    """
    if path.name in IGNORED_FILE_NAMES:
        return True
    if path.suffix in IGNORED_SUFFIXES:
        return True
    dynamic_excluded = set(normalize_excluded_dir_names(excluded_dir_names))
    for part in path.parts:
        lowered = part.lower()
        if lowered in IGNORED_DIR_NAMES or lowered in dynamic_excluded:
            return True
    return False


def iter_files(
    root: Path,
    excluded_dir_names: Iterable[str] = (),
    *,
    follow_symlinks: bool = False,
) -> Iterable[Path]:
    """
    Iterate regular file paths under `root`, yielding their paths relative to `root` in sorted order.

    Parameters:
        root (Path): Directory to scan.

    Returns:
        Iterable[Path]: Relative paths (Path objects) for every non-directory file found beneath `root`, excluding entries matched by `is_ignored`, yielded in sorted order.
    """
    excluded_dirs = normalize_excluded_dir_names(excluded_dir_names)
    for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=follow_symlinks):
        dirpath_obj = Path(dirpath)
        try:
            rel_dir = dirpath_obj.relative_to(root)
        except ValueError:
            continue

        kept_dirnames: list[str] = []
        for dirname in sorted(dirnames):
            rel_child = rel_dir / dirname if rel_dir != Path(".") else Path(dirname)
            if is_ignored(rel_child, excluded_dirs):
                continue
            kept_dirnames.append(dirname)
        dirnames[:] = kept_dirnames

        for filename in sorted(filenames):
            rel_file = rel_dir / filename if rel_dir != Path(".") else Path(filename)
            if is_ignored(rel_file, excluded_dirs):
                continue
            yield rel_file


def hash_bytes(content: bytes) -> str:
    """
    Compute the SHA-256 hexadecimal digest of the given bytes.

    Parameters:
        content (bytes): Input data to hash.

    Returns:
        str: Hexadecimal SHA-256 digest of `content`.
    """
    return hashlib.sha256(content).hexdigest()


def hash_text(content: str) -> str:
    """
    Compute the SHA-256 hex digest of a text string.

    Parameters:
        content (str): Text to hash; encoded as UTF-8 before hashing.

    Returns:
        hex_digest (str): Lowercase hexadecimal SHA-256 digest of the UTF-8 encoding of `content`.
    """
    return hash_bytes(content.encode("utf-8"))


def manifest_digest(entries: dict[str, str]) -> str:
    """
    Compute a deterministic SHA-256 digest for a manifest mapping of file paths to digests.

    The entries are sorted by path and each pair is serialized as "{path}\t{digest}\n" concatenated into one byte string before hashing.

    Parameters:
        entries (dict[str, str]): Mapping from relative file path to its hex digest.

    Returns:
        manifest_digest (str): Hex-encoded SHA-256 digest of the serialized manifest.
    """
    serialized = "".join(f"{path}\t{digest}\n" for path, digest in sorted(entries.items()))
    return hash_text(serialized)


def projection_header_for(rel_source_path: str, suffix: str) -> str:
    """
    Create the canonical projection header line for a file copied from a source path.

    Parameters:
        rel_source_path (str): Relative source path to embed in the header (as shown in the header's `source=` field).
        suffix (str): File suffix (e.g. ".md", ".py") which determines header comment style.

    Returns:
        str: A single-line header string containing the `HEADER_TOKEN` and `source=<rel_source_path>` formatted as an HTML comment for `.md` files or as a `#` comment for other suffixes.
    """
    if suffix == ".md":
        return f"<!-- {HEADER_TOKEN} source={rel_source_path}; DO NOT EDIT PROJECTION COPY. -->"
    return f"# {HEADER_TOKEN} source={rel_source_path}; DO NOT EDIT PROJECTION COPY."


def strip_projection_header(text: str, suffix: str) -> tuple[str, bool]:
    """
    Remove a previously inserted projection header from the given file content and report whether a header was removed.

    Parameters:
        text (str): File contents to normalise.
        suffix (str): File suffix (e.g. '.md', '.py') used to select the header form.

    Returns:
        tuple[str, bool]: A pair of (normalized_text, removed) where `normalized_text` is the content with a generated projection header removed if present, and `removed` is `True` when a header was found and removed, `False` otherwise.
    """
    lines = text.splitlines(keepends=True)
    if not lines:
        return text, False

    def remove_at(index: int) -> tuple[str, bool]:
        """
        Attempt to remove a projection header line at the given line index and return the resulting text and a flag indicating whether a removal occurred.

        Parameters:
            index (int): Zero-based line index of the candidate header line.

        Returns:
            tuple[str, bool]: A pair where the first element is the resulting text and the second is `True` if a header line containing the projection header token was removed; otherwise the original text and `False`. If a header line is removed and the following line is blank, that blank line is also removed.
        """
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


def detect_projection_header(text: str, suffix: str) -> str | None:
    """
    Return the current projection header line when present.

    The detection rules mirror `strip_projection_header()` so verification can
    compare the exact generated header value, not only token presence.
    """
    lines = text.splitlines()
    if not lines:
        return None

    if suffix == ".md":
        if lines[0].strip() == "---":
            for idx in range(1, len(lines)):
                if lines[idx].strip() == "---":
                    if idx + 1 < len(lines) and HEADER_TOKEN in lines[idx + 1]:
                        return lines[idx + 1]
                    break
        if HEADER_TOKEN in lines[0]:
            return lines[0]
        return None

    if lines[0].startswith("#!"):
        if len(lines) > 1 and HEADER_TOKEN in lines[1]:
            return lines[1]
        return None

    if HEADER_TOKEN in lines[0]:
        return lines[0]
    return None


def apply_projection_header(text: str, rel_source_path: str, suffix: str) -> str:
    """
    Insert or replace the generated projection header for a given source path into the provided file text.

    Ensures the returned text contains exactly one up-to-date projection header (based on `rel_source_path`) positioned according to the file `suffix` conventions: for Markdown, the header is placed after YAML front-matter if present; for files starting with a shebang, the header follows the shebang; otherwise the header is prepended separated by a blank line.

    Parameters:
        text (str): Original file content.
        rel_source_path (str): Path to the canonical source, expressed relative to the repository root; used to build the header's `source=...` value.
        suffix (str): File extension (e.g. ".md", ".py") that selects the header placement rules.

    Returns:
        str: File content with a single, canonical projection header applied.
    """
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
    """
    Read a file and return its contents decoded as UTF-8 text.

    Returns:
        The file contents as a UTF-8 decoded string.
    """
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    """
    Write text to a file using UTF-8 encoding, preserving existing mode bits.

    Parameters:
        path (Path): Destination file path to write.
        content (str): Text content to write to the file.
    """
    existing_mode: int | None = None
    try:
        existing_mode = path.stat().st_mode & 0o777
    except OSError:
        existing_mode = None
    path.write_text(content, encoding="utf-8")
    if existing_mode is not None:
        try:
            os.chmod(path, existing_mode)
        except OSError:
            # Best effort: content updates should not fail on chmod issues.
            pass


def ensure_symlink(repo_root: Path, spec: SymlinkProjection) -> dict[str, object]:
    """
    Ensure the alias path under `repo_root` is a symlink pointing to the spec's canonical directory.

    If the canonical directory does not exist the function returns an error. If the alias already exists as a symlink that resolves to the canonical directory the result indicates no change. If the alias exists as a symlink pointing elsewhere, as a regular file, or as a non-managed directory it is removed and replaced by a symlink. If the alias exists as a real directory and the alias path does not start with "skills-system/", the function returns an error requiring manual migration; managed "skills-system/" directories are removed and replaced.

    Parameters:
        repo_root (Path): Repository root used to resolve the spec paths.
        spec (SymlinkProjection): Projection spec containing `name`, `alias_path`, and `canonical_path`.

    Returns:
        dict[str, object]: Result containing:
          - `name` (str): spec name.
          - `type` (str): `"symlink"`.
          - `status` (str): one of `"ok"`, `"synced"`, `"replaced"`, or `"error"`.
          - `reason` (str, optional): error code when `status == "error"` (e.g., `"canonical_missing"`, `"alias_requires_manual_migration"`).
          - `alias` (str): the spec's alias_path.
          - `canonical` (str): the spec's canonical_path.
          - `target` (str, optional): the symlink target written (relative path) or current target when `status == "ok"`.
          - `changed` (bool): `True` when the alias was created or modified, `False` when no change was needed.
    """
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

    managed_projection_alias = spec.alias_path.startswith("skills-system/")

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
            if managed_projection_alias:
                shutil.rmtree(alias_abs)
                changed = True
            else:
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
    """
    Verify that a symlink alias exists and resolves to the configured canonical directory.

    Parameters:
        repo_root (Path): Repository root used to resolve relative paths in `spec`.
        spec (SymlinkProjection): Projection spec containing `name`, `alias_path` and `canonical_path`.

    Returns:
        result (dict[str, object]): A result mapping with at least `name`, `type` ("symlink"), `status`, `alias` and `canonical`.
        - `status` is `"pass"` when the alias is a symlink that resolves to the canonical directory.
        - `status` is `"drift"` when the projection does not match; `reason` will be one of:
          - `"canonical_missing"`: canonical path is not an existing directory.
          - `"alias_missing"`: alias path does not exist.
          - `"alias_not_symlink"`: alias exists but is not a symlink.
          - `"wrong_target"`: alias is a symlink but points to a different target.
        - When present, `target` is the symlink's stored target (as read from the filesystem).
    """
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
    """
    Synchronises a source directory into its projection directory and applies generated projection headers to stampable files.

    Parameters:
        repo_root (Path): Repository root path used to resolve spec paths.
        spec (MirrorProjection): Mirror projection specification containing `name`, `source_path`, `projection_path` and `tags`.

    Returns:
        result (dict[str, object]): Operation result including:
            - `name`: projection name from the spec.
            - `type`: the literal `"mirror"`.
            - `status`: `"synced"` on success or `"error"` when the source is missing.
            - `reason`: present when `status` is `"error"` (e.g. `"source_missing"`).
            - `source`: the spec's source_path.
            - `projection`: the spec's projection_path.
            - `sync_engine`: `"rsync"` when rsync was used, otherwise `"python"`.
            - `changed_files`: number of files created/updated (or `-1` when rsync was used and precise count is not computed).
            - `deleted_files`: number of files removed from the projection because they were absent from the source.
            - `stamped_files`: number of stampable files inspected (and rewritten when their projection header changed).
    """
    source_abs = repo_root / spec.source_path
    projection_abs = repo_root / spec.projection_path
    if not source_abs.is_dir():
        if spec.optional_when_missing:
            return {
                "name": spec.name,
                "type": "mirror",
                "status": "ok",
                "reason": "source_missing_optional",
                "source": spec.source_path,
                "projection": spec.projection_path,
                "changed": False,
            }
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
    if projection_abs.is_symlink():
        projection_abs.unlink()
    elif projection_abs.exists() and not projection_abs.is_dir():
        projection_abs.unlink()
    projection_abs.mkdir(parents=True, exist_ok=True)

    excluded_dirs = normalize_excluded_dir_names(spec.excluded_dir_names)

    def _prune_excluded_dirs(root: Path, excluded: tuple[str, ...]) -> int:
        """
        Remove excluded directories from a projection tree.

        Returns:
            int: Number of pruned directories.
        """
        if not excluded:
            return 0
        excluded_set = set(excluded)
        pruned = 0
        for path in sorted(root.rglob("*"), reverse=True):
            if not path.is_dir():
                continue
            if path.name.lower() not in excluded_set:
                continue
            shutil.rmtree(path, ignore_errors=True)
            pruned += 1
        return pruned

    rsync_bin = shutil.which("rsync")
    if rsync_bin:
        before_files = {rel.as_posix() for rel in iter_files(projection_abs, excluded_dirs)}
        try:
            rsync_args = [
                rsync_bin,
                "-a",
                "--delete",
                "--exclude",
                "__pycache__/",
                "--exclude",
                "*.pyc",
                "--exclude",
                ".DS_Store",
            ]
            if spec.follow_symlinks:
                rsync_args.append("-L")
            for excluded in excluded_dirs:
                rsync_args.extend(["--exclude", f"{excluded}/"])
            rsync_args.extend([f"{source_abs}/", f"{projection_abs}/"])
            subprocess.run(  # noqa: S603
                rsync_args,
                check=True,
                capture_output=True,
                text=True,
            )
            pruned_dirs = _prune_excluded_dirs(projection_abs, excluded_dirs)
            sync_engine = "rsync"
            after_files = {rel.as_posix() for rel in iter_files(projection_abs, excluded_dirs)}
            deleted_files = len(before_files - after_files) + pruned_dirs
            changed_files = -1
        except subprocess.CalledProcessError as error:
            if _is_rsync_permission_failure(error):
                changed_files, deleted_files = _sync_mirror_python(
                    source_abs,
                    projection_abs,
                    follow_symlinks=spec.follow_symlinks,
                    excluded_dir_names=excluded_dirs,
                )
                deleted_files += _prune_excluded_dirs(projection_abs, excluded_dirs)
            else:
                raise
    else:
        changed_files, deleted_files = _sync_mirror_python(
            source_abs,
            projection_abs,
            follow_symlinks=spec.follow_symlinks,
            excluded_dir_names=excluded_dirs,
        )
        deleted_files += _prune_excluded_dirs(projection_abs, excluded_dirs)

    stamped_files = 0
    for rel in iter_files(projection_abs, excluded_dirs):
        if rel.suffix not in STAMPABLE_SUFFIXES:
            continue
        projection_file = projection_abs / rel
        if projection_file.is_symlink():
            continue
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


def normalize_stamped_content(content: bytes, path: Path) -> bytes:
    """
    Normalise content of stampable files by removing a generated projection header.

    If the file's suffix is listed in STAMPABLE_SUFFIXES and the bytes decode as UTF-8,
    the returned bytes are the UTF-8 encoding of the text with any projection header removed.
    If the suffix is not stampable or UTF-8 decoding fails, the original bytes are returned.

    Parameters:
        content (bytes): File content to normalise.
        path (Path): File path used to determine the file suffix for stampable detection.

    Returns:
        bytes: Normalised bytes with the projection header removed for stampable UTF-8 text files,
               or the original bytes otherwise.
    """
    if path.suffix not in STAMPABLE_SUFFIXES:
        return content
    try:
        text = content.decode("utf-8")
        normalized, _ = strip_projection_header(text, path.suffix)
        return normalized.encode("utf-8")
    except UnicodeDecodeError:
        return content


def _sync_mirror_python(
    source_abs: Path,
    projection_abs: Path,
    *,
    follow_symlinks: bool = False,
    excluded_dir_names: Iterable[str] = (),
) -> tuple[int, int]:
    """
    Synchronise a projection directory to match a source directory using pure-Python file operations.

    Performs file-by-file sync: deletes projection files that are absent from source, copies regular files, replicates symlinks, treats files with stampable suffixes as equal when their contents match after stripping a generated projection header, preserves permission bits on a best-effort basis, and removes now-empty directories in the projection.

    Parameters:
        source_abs (Path): Absolute path to the source directory to mirror.
        projection_abs (Path): Absolute path to the projection directory to update.

    Returns:
        tuple[int, int]: A pair `(changed_files, deleted_files)` where `changed_files` is the number of files created or updated in the projection and `deleted_files` is the number of projection files removed because they no longer exist in the source.
    """
    changed_files = 0
    deleted_files = 0
    source_files = {
        rel.as_posix(): rel
        for rel in iter_files(
            source_abs,
            excluded_dir_names,
            follow_symlinks=follow_symlinks,
        )
    }
    projection_files = {
        rel.as_posix(): rel for rel in iter_files(projection_abs, excluded_dir_names)
    }

    for rel_key in sorted(set(projection_files) - set(source_files)):
        stale = projection_abs / projection_files[rel_key]
        stale.unlink()
        deleted_files += 1

    def _normalize_stamped_text(content: bytes, path: Path) -> str | None:
        """
        Return UTF-8 decoded text with any projection header removed for stampable files.

        Parameters:
            content (bytes): Raw file bytes to decode and normalise.
            path (Path): File path used to determine stampable suffix.

        Returns:
            str | None: The decoded text with a projection header stripped when the file
            suffix is in STAMPABLE_SUFFIXES and decoding succeeds; `None` otherwise.
        """
        if path.suffix not in STAMPABLE_SUFFIXES:
            return None
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            return None
        normalized, _ = strip_projection_header(text, path.suffix)
        return normalized

    for rel in source_files.values():
        source_file = source_abs / rel
        projection_file = projection_abs / rel
        projection_file.parent.mkdir(parents=True, exist_ok=True)
        if source_file.is_symlink() and not follow_symlinks:
            source_target = os.readlink(source_file)
            if projection_file.is_symlink() and os.readlink(projection_file) == source_target:
                continue
            if projection_file.exists() or projection_file.is_symlink():
                if projection_file.is_symlink():
                    projection_file.unlink()
                elif projection_file.is_dir():
                    shutil.rmtree(projection_file)
                else:
                    projection_file.unlink()
            projection_file.symlink_to(source_target)
            changed_files += 1
            continue

        try:
            source_bytes = source_file.read_bytes()
        except OSError:
            # Broken source symlink or unreadable file: do not mirror stale content.
            if projection_file.exists() or projection_file.is_symlink():
                if projection_file.is_symlink():
                    projection_file.unlink()
                elif projection_file.is_dir():
                    shutil.rmtree(projection_file)
                else:
                    projection_file.unlink()
                deleted_files += 1
            continue
        normalized_source = _normalize_stamped_text(source_bytes, source_file)
        if projection_file.exists() and projection_file.is_file() and not projection_file.is_symlink():
            try:
                projection_bytes = projection_file.read_bytes()
            except OSError:
                # Unreadable projection file: will be recreated below
                pass
            else:
                if normalized_source is not None:
                    normalized_projection = _normalize_stamped_text(projection_bytes, projection_file)
                    if normalized_projection is not None and normalized_projection == normalized_source:
                        continue
                elif projection_bytes == source_bytes:
                    continue
        if projection_file.exists() or projection_file.is_symlink():
            if projection_file.is_symlink():
                projection_file.unlink()
            elif projection_file.is_dir():
                shutil.rmtree(projection_file)
            else:
                projection_file.unlink()
        projection_file.write_bytes(source_bytes)
        with contextlib.suppress(OSError):
            # Best-effort permission copy: content sync remains valid if chmod is denied.
            os.chmod(projection_file, source_file.stat().st_mode & 0o777)
        changed_files += 1

    for path in sorted(projection_abs.rglob("*"), reverse=True):
        if path.is_dir() and not path.is_symlink():
            try:
                path.rmdir()
            except OSError:
                continue
    return changed_files, deleted_files


def _is_rsync_permission_failure(error: subprocess.CalledProcessError) -> bool:
    """
    Detect whether an rsync CalledProcessError indicates a permission-style failure appropriate for falling back to a Python sync.

    Parameters:
        error (subprocess.CalledProcessError): The exception raised by a failed rsync invocation; its stdout/stderr will be inspected.

    Returns:
        bool: `True` if the combined stdout/stderr contains permission-related messages such as "operation not permitted" or "permission denied", `False` otherwise.
    """
    output = "\n".join(
        part for part in (error.stderr, error.stdout) if isinstance(part, str) and part
    ).lower()
    if not output:
        return False
    return any(
        marker in output
        for marker in ("operation not permitted", "permission denied")
    )


def verify_mirror(repo_root: Path, spec: MirrorProjection) -> dict[str, object]:
    """
    Verify that a projection directory mirrors its source directory and report any drift.

    Performs a path-by-path comparison between `spec.source_path` and `spec.projection_path` (relative to `repo_root`), normalising stampable text files by removing the generated projection header before comparison, and computes manifest digests for both sides.

    Parameters:
        repo_root (Path): Repository root used to resolve the spec's paths.
        spec (MirrorProjection): Mirror projection specification with `source_path` and `projection_path`.

    Returns:
        dict: A result payload containing at least the keys:
          - `name` (str): projection name from the spec.
          - `type` (str): always `"mirror"`.
          - `source` / `projection` (Path): the spec paths.
          - `status` (`"pass"` or `"drift"`): overall verification outcome.
          - `policy` (str): verification policy identifier (`"hash-manifest-plus-path-diff"`).
          - `missing_in_projection` (list[str]): files present in source but not projection.
          - `extra_in_projection` (list[str]): files present in projection but not source.
          - `mismatched_files` (list[dict]): entries describing per-file mismatches with `path`, `reason`, and SHA-256 values.
          - `unstamped_files` (list[str]): stampable files in the projection missing the generated header.
          - `checked_files` (int): number of files compared from the source.
          - `source_manifest_sha256` / `projection_manifest_sha256` (str): manifest digests used for comparison.
          - `manifest_mismatch` (bool): whether the two manifests differ.
    """
    source_abs = repo_root / spec.source_path
    projection_abs = repo_root / spec.projection_path
    result: dict[str, object] = {
        "name": spec.name,
        "type": "mirror",
        "source": spec.source_path,
        "projection": spec.projection_path,
    }
    if not source_abs.is_dir():
        if spec.optional_when_missing:
            result.update({"status": "pass", "reason": "source_missing_optional"})
        else:
            result.update({"status": "drift", "reason": "source_missing"})
        return result
    if projection_abs.is_symlink():
        result.update(
            {
                "status": "drift",
                "reason": "projection_symlinked",
                "projection_symlink_target": os.readlink(projection_abs),
            }
        )
        return result
    if not projection_abs.exists():
        if spec.optional_when_missing:
            result.update({"status": "pass", "reason": "projection_missing_optional"})
        else:
            result.update({"status": "drift", "reason": "projection_missing"})
        return result
    if not projection_abs.is_dir():
        result.update({"status": "drift", "reason": "projection_not_directory"})
        return result

    excluded_dirs = normalize_excluded_dir_names(spec.excluded_dir_names)
    source_files = {
        rel.as_posix(): rel
        for rel in iter_files(
            source_abs,
            excluded_dirs,
            follow_symlinks=spec.follow_symlinks,
        )
    }
    projection_files = {
        rel.as_posix(): rel for rel in iter_files(projection_abs, excluded_dirs)
    }
    source_manifest_hashes: dict[str, str] = {}
    for rel_key, rel in source_files.items():
        source_file = source_abs / rel
        if source_file.is_symlink() and not spec.follow_symlinks:
            source_manifest_hashes[rel_key] = hash_text(f"symlink:{os.readlink(source_file)}")
        else:
            try:
                source_manifest_hashes[rel_key] = hash_bytes(source_file.read_bytes())
            except OSError:
                source_manifest_hashes[rel_key] = hash_text("unreadable_source")
    projection_manifest_hashes: dict[str, str] = {}
    for rel_key, rel in projection_files.items():
        projection_file = projection_abs / rel
        if projection_file.is_symlink() and not spec.follow_symlinks:
            projection_manifest_hashes[rel_key] = hash_text(f"symlink:{os.readlink(projection_file)}")
            continue
        try:
            projection_bytes = projection_file.read_bytes()
        except OSError:
            projection_manifest_hashes[rel_key] = hash_text("unreadable_projection")
            continue
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

        if (source_file.is_symlink() or projection_file.is_symlink()) and not spec.follow_symlinks:
            if source_file.is_symlink() and projection_file.is_symlink():
                source_target = os.readlink(source_file)
                projection_target = os.readlink(projection_file)
                if source_target != projection_target:
                    mismatched_files.append(
                        {
                            "path": rel_key,
                            "reason": "symlink_target_mismatch",
                            "source_sha256": hash_text(f"symlink:{source_target}"),
                            "projection_sha256": hash_text(f"symlink:{projection_target}"),
                        }
                    )
            else:
                source_kind = "symlink" if source_file.is_symlink() else "file"
                projection_kind = "symlink" if projection_file.is_symlink() else "file"
                mismatched_files.append(
                    {
                        "path": rel_key,
                        "reason": "symlink_kind_mismatch",
                        "source_sha256": hash_text(source_kind),
                        "projection_sha256": hash_text(projection_kind),
                    }
                )
            continue

        try:
            source_bytes = source_file.read_bytes()
        except OSError:
            projection_sha = hash_text("missing")
            if projection_file.exists():
                try:
                    projection_sha = hash_bytes(projection_file.read_bytes())
                except OSError:
                    projection_sha = hash_text("unreadable_projection")
            mismatched_files.append(
                {
                    "path": rel_key,
                    "reason": "unreadable_file",
                    "source_sha256": hash_text("unreadable_source"),
                    "projection_sha256": projection_sha,
                }
            )
            continue
        try:
            projection_bytes = projection_file.read_bytes()
        except OSError:
            mismatched_files.append(
                {
                    "path": rel_key,
                    "reason": "unreadable_file",
                    "source_sha256": hash_bytes(source_bytes),
                    "projection_sha256": hash_text("unreadable_projection"),
                }
            )
            continue

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

            expected_header = projection_header_for((Path(spec.source_path) / rel).as_posix(), rel.suffix)
            header_line = detect_projection_header(projection_text, rel.suffix)
            normalized_projection, had_header = strip_projection_header(projection_text, rel.suffix)
            if not had_header or header_line != expected_header:
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
    """
    Select symlink projection specifications matching the given scope.

    Parameters:
        scope (str): Scope name used to filter projections; use "all" to select every configured symlink projection.

    Returns:
        selected (tuple[SymlinkProjection, ...]): Tuple of symlink projection specifications whose `tags` contain the provided scope (or all projections when `scope` is "all").
    """
    if scope == "all":
        return SYMLINK_PROJECTIONS
    return tuple(spec for spec in SYMLINK_PROJECTIONS if scope in spec.tags)


def select_mirrors(scope: str) -> tuple[MirrorProjection, ...]:
    """
    Select mirror projection specs matching the given scope.

    If `scope` is "all" returns all defined mirror projections; otherwise returns only
    those projections whose `tags` contain the provided scope string.

    Parameters:
        scope (str): Scope tag to filter by, or `"all"` to select every mirror projection.

    Returns:
        tuple[MirrorProjection, ...]: MirrorProjection specs matching the scope.
    """
    if scope == "all":
        return MIRROR_PROJECTIONS
    return tuple(spec for spec in MIRROR_PROJECTIONS if scope in spec.tags)


def write_manifest(path: Path, payload: dict[str, object]) -> None:
    """
    Write a JSON manifest file to the given path, creating parent directories as required.

    Parameters:
        path (Path): Destination filesystem path for the manifest; parent directories will be created if missing.
        payload (dict[str, object]): JSON-serialisable mapping to be written; formatted with an indent of 2 and a trailing newline.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def render_text(payload: dict[str, object]) -> str:
    """
    Render a human-readable summary report from a verification/sync payload.

    Produces a multi-line text report containing top-level metadata (schema_version, mode, scope, status) and a concise per-result listing with name, type and status. For entries whose status is "drift" or "error" the report includes an optional reason, a manifest mismatch marker, and counts of any listed discrepancies (`missing_in_projection`, `extra_in_projection`, `unstamped_files`, `mismatched_files`).

    Parameters:
        payload (dict[str, object]): Report payload produced by run_sync/run_verify containing keys
            like `schema_version`, `mode`, `scope`, `status` and an optional `results` list of
            per-item result dictionaries.

    Returns:
        str: The rendered multi-line text report.
    """
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
    """
    Run synchronization for all configured symlink and mirror projections filtered by scope.

    Parameters:
        repo_root (Path): Filesystem root used to resolve projection canonical/source and alias/projection paths.
        scope (str): Projection scope to process; e.g. "all", "skill-factory", "plugin-factory", "plugin-caches".

    Returns:
        payload (dict): Report payload containing:
            - `schema_version` (str): schema identifier.
            - `generated_at` (str): ISO 8601 UTC timestamp of report generation.
            - `mode` (str): the string "sync".
            - `scope` (str): the scope passed to the function.
            - `status` (str): overall outcome, `"pass"` when no entry had `status == "error"`, otherwise `"fail"`.
            - `results` (list[dict]): per-projection result dictionaries produced by `ensure_symlink` and `sync_mirror`.
    """
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
    """
    Run verification across selected symlink and mirror projections and assemble a report payload.

    Parameters:
        repo_root (Path): Repository root used to resolve projection paths.
        scope (str): Scope selector for projections; `"all"` runs all projections, otherwise only projections whose tags include this value.

    Returns:
        dict[str, object]: Report payload containing:
            - `schema_version` (str): fixed schema identifier.
            - `generated_at` (str): ISO8601 UTC timestamp of the run.
            - `mode` (str): the string `"verify"`.
            - `scope` (str): the provided scope argument.
            - `status` (str): overall status; `"pass"` when all items are `pass`/`ok`, otherwise `"fail"`.
            - `results` (list[dict[str, object]]): per-projection verification results produced by `verify_symlink` and `verify_mirror`.
    """
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
    """
    Run the projection integrity CLI workflow and return an appropriate process exit code.

    Performs the selected mode (`sync` or `verify`) against the repository root, optionally writes a JSON manifest, emits the report in JSON or human-readable text, and returns an exit code reflecting overall success.

    Returns:
        exit_code (int): `1` when the generated payload has `status == "fail"`, `0` otherwise.
    """
    args = parse_args()
    repo_root = Path(args.repo_root).resolve() if args.repo_root else default_repo_root(Path(__file__))
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
