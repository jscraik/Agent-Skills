"""Focused mirror and plugin-package projection mechanics.

The public projection CLI remains in ``projection_integrity_impl.py``.  This
module owns the mutation-heavy mirror implementation so that package identity,
symlink preflight, and filesystem synchronization can be reviewed in isolation.
"""

from __future__ import annotations

import contextlib
import hashlib
import os
import shutil
import subprocess
from pathlib import Path
from typing import Iterable, Protocol


class ProjectionApi(Protocol):
    STAMPABLE_SUFFIXES: set[str]

    def normalize_excluded_dir_names(self, names: Iterable[str]) -> tuple[str, ...]: ...
    def iter_files(self, root: Path, names: Iterable[str] = (), *, follow_symlinks: bool = False) -> Iterable[Path]: ...
    def is_ignored(self, path: Path, names: Iterable[str] = ()) -> bool: ...
    def strip_projection_header(self, text: str, suffix: str) -> tuple[str, bool]: ...
    def apply_projection_header(self, text: str, source: str, suffix: str) -> str: ...
    def read_text(self, path: Path) -> str: ...
    def write_text(self, path: Path, content: str) -> None: ...
    def _sync_mirror_python(self, source: Path, projection: Path, *, follow_symlinks: bool = False, excluded_dir_names: Iterable[str] = ()) -> tuple[int, int]: ...
    def _prune_nested_duplicate_skill_identities(self, skills_root: Path) -> tuple[list[str], int]: ...
    def _replace_plugin_cache_package_copy(self, source: Path, projection: Path, *, follow_symlinks: bool, excluded_dir_names: Iterable[str], keep_duplicates: bool = False) -> tuple[int, int, list[str]]: ...


def compare_symlinks(spec: object) -> bool:
    """Compare package links by target when projections intentionally omit fixtures."""
    return bool(spec.plugin_cache_package or not spec.follow_symlinks)


def unsafe_package_symlinks(package_root: Path) -> list[dict[str, str]]:
    """Return fail-closed diagnostics for absolute, broken, or escaping links."""
    root = package_root.resolve()
    links = sorted(
        (path for path in package_root.rglob("*") if path.is_symlink()),
        key=lambda path: path.relative_to(package_root).as_posix(),
    )
    violations: list[dict[str, str]] = []
    for link in links:
        relative, target = link.relative_to(package_root).as_posix(), os.readlink(link)
        reason = _unsafe_link_reason(link, target, root)
        if reason:
            violations.append({"path": relative, "target": target, "reason": reason})
    return violations


def _unsafe_link_reason(link: Path, target: str, root: Path) -> str | None:
    if Path(target).is_absolute():
        return "absolute_target"
    try:
        resolved = link.resolve(strict=True)
    except (FileNotFoundError, OSError, RuntimeError):
        return "broken_target"
    return None if resolved.is_relative_to(root) else "target_escapes_package"


def sync_mirror(repo_root: Path, spec: object, api: ProjectionApi) -> dict[str, object]:
    """Synchronize one mirror while preserving the historical result contract."""
    source_abs = repo_root / spec.source_path
    projection_abs = repo_root / spec.projection_path
    missing = _missing_source_result(spec, source_abs)
    if missing:
        return missing
    unsafe = unsafe_package_symlinks(source_abs) if spec.plugin_cache_package else []
    if unsafe:
        return _unsafe_result(spec, unsafe)
    _prepare_projection(projection_abs, replace=spec.replace_before_sync)
    if spec.plugin_cache_package:
        return _sync_plugin_package(source_abs, projection_abs, spec, api)
    changed, deleted, engine = _sync_standard(source_abs, projection_abs, spec, api)
    stamped = _stamp_projection(projection_abs, spec, api)
    return _success_result(spec, engine, changed, deleted, stamped)


def _missing_source_result(spec: object, source_abs: Path) -> dict[str, object] | None:
    if source_abs.is_dir():
        return None
    status = "ok" if spec.optional_when_missing else "error"
    reason = "source_missing_optional" if spec.optional_when_missing else "source_missing"
    result = _base_result(spec, status=status, reason=reason)
    if spec.optional_when_missing:
        result["changed"] = False
    return result


def _unsafe_result(spec: object, unsafe: list[dict[str, str]]) -> dict[str, object]:
    result = _base_result(spec, status="error", reason="unsafe_plugin_package_symlink")
    result.update({"unsafe_symlinks": unsafe, "changed_files": 0, "deleted_files": 0})
    return result


def _base_result(spec: object, *, status: str, reason: str | None = None) -> dict[str, object]:
    result: dict[str, object] = {
        "name": spec.name, "type": "mirror", "status": status,
        "source": spec.source_path, "projection": spec.projection_path,
    }
    if reason:
        result["reason"] = reason
    return result


def _prepare_projection(projection: Path, *, replace: bool) -> None:
    projection.parent.mkdir(parents=True, exist_ok=True)
    if replace and (projection.exists() or projection.is_symlink()):
        _remove_path(projection)
    elif projection.is_symlink() or (projection.exists() and not projection.is_dir()):
        projection.unlink()
    projection.mkdir(parents=True, exist_ok=True)


def _remove_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def _sync_plugin_package(source: Path, projection: Path, spec: object, api: ProjectionApi) -> dict[str, object]:
    changed, deleted, logs = api._replace_plugin_cache_package_copy(
        source, projection,
        follow_symlinks=spec.follow_symlinks,
        excluded_dir_names=api.normalize_excluded_dir_names(spec.excluded_dir_names),
        keep_duplicates=False,
    )
    result = _success_result(spec, "plugin-cache-package", changed, deleted, 0)
    result["logs"] = logs
    return result


def _sync_standard(source: Path, projection: Path, spec: object, api: ProjectionApi) -> tuple[int, int, str]:
    excluded = api.normalize_excluded_dir_names(spec.excluded_dir_names)
    rsync_bin = shutil.which("rsync")
    if not rsync_bin:
        changed, deleted = api._sync_mirror_python(
            source, projection, follow_symlinks=spec.follow_symlinks, excluded_dir_names=excluded
        )
        return changed, deleted + prune_excluded_dirs(projection, excluded), "python"
    return _sync_with_rsync(source, projection, spec, excluded, rsync_bin, api)


def _sync_with_rsync(source: Path, projection: Path, spec: object, excluded: tuple[str, ...], rsync_bin: str, api: ProjectionApi) -> tuple[int, int, str]:
    before = {rel.as_posix() for rel in api.iter_files(projection, excluded)}
    args = _rsync_args(rsync_bin, source, projection, excluded, spec.follow_symlinks)
    try:
        subprocess.run(args, check=True, capture_output=True, text=True)  # noqa: S603
    except subprocess.CalledProcessError as error:
        if not (spec.replace_before_sync or is_rsync_permission_failure(error)):
            raise
        changed, deleted = api._sync_mirror_python(
            source, projection, follow_symlinks=spec.follow_symlinks, excluded_dir_names=excluded
        )
        return changed, deleted + prune_excluded_dirs(projection, excluded), "python"
    pruned = prune_excluded_dirs(projection, excluded)
    after = {rel.as_posix() for rel in api.iter_files(projection, excluded)}
    return -1, len(before - after) + pruned, "rsync"


def _rsync_args(binary: str, source: Path, projection: Path, excluded: tuple[str, ...], follow: bool) -> list[str]:
    args = [binary, "-a", "--delete", "--exclude", "__pycache__/", "--exclude", "*.pyc", "--exclude", ".DS_Store"]
    if follow:
        args.append("-L")
    for name in excluded:
        args.extend(["--exclude", f"{name}/"])
    args.extend([f"{source}/", f"{projection}/"])
    return args


def prune_excluded_dirs(root: Path, excluded: tuple[str, ...]) -> int:
    excluded_set = set(excluded)
    targets = [path for path in sorted(root.rglob("*"), reverse=True) if path.is_dir() and path.name.lower() in excluded_set]
    for path in targets:
        shutil.rmtree(path, ignore_errors=True)
    return len(targets)


def _stamp_projection(projection: Path, spec: object, api: ProjectionApi) -> int:
    excluded = api.normalize_excluded_dir_names(spec.excluded_dir_names)
    stamped = 0
    for rel in api.iter_files(projection, excluded):
        if rel.suffix not in api.STAMPABLE_SUFFIXES or (projection / rel).is_symlink():
            continue
        stamped += _stamp_file(projection / rel, Path(spec.source_path) / rel, rel.suffix, api)
    return stamped


def _stamp_file(path: Path, source_rel: Path, suffix: str, api: ProjectionApi) -> int:
    try:
        original = api.read_text(path)
    except UnicodeDecodeError:
        return 0
    updated = api.apply_projection_header(original, source_rel.as_posix(), suffix)
    if updated != original:
        api.write_text(path, updated)
    return 1


def _success_result(spec: object, engine: str, changed: int, deleted: int, stamped: int) -> dict[str, object]:
    result = _base_result(spec, status="synced")
    result.update({"sync_engine": engine, "changed_files": changed, "deleted_files": deleted, "stamped_files": stamped})
    return result


def sync_mirror_python(source: Path, projection: Path, follow: bool, excluded: Iterable[str], api: ProjectionApi) -> tuple[int, int]:
    source_files = _source_files(source, follow, excluded, api)
    projection_files = _projection_files(projection, excluded, api)
    deleted = _delete_stale(projection, source_files, projection_files)
    changed = 0
    for rel in source_files.values():
        file_changed, file_deleted = _sync_one(source / rel, projection / rel, follow, api)
        changed += file_changed
        deleted += file_deleted
    _remove_empty_dirs(projection)
    return changed, deleted


def _source_files(root: Path, follow: bool, excluded: Iterable[str], api: ProjectionApi) -> dict[str, Path]:
    files = {rel.as_posix(): rel for rel in api.iter_files(root, excluded, follow_symlinks=follow)}
    if follow:
        return files
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if path.is_symlink() and not api.is_ignored(rel, excluded):
            files[rel.as_posix()] = rel
    return files


def _projection_files(root: Path, excluded: Iterable[str], api: ProjectionApi) -> dict[str, Path]:
    files = {rel.as_posix(): rel for rel in api.iter_files(root, excluded)}
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if path.is_symlink() and not api.is_ignored(rel, excluded):
            files[rel.as_posix()] = rel
    return files


def _delete_stale(root: Path, source: dict[str, Path], projection: dict[str, Path]) -> int:
    stale_keys = sorted(set(projection) - set(source))
    for key in stale_keys:
        (root / projection[key]).unlink()
    return len(stale_keys)


def _sync_one(source: Path, projection: Path, follow: bool, api: ProjectionApi) -> tuple[int, int]:
    projection.parent.mkdir(parents=True, exist_ok=True)
    if source.is_symlink() and not follow:
        return _sync_symlink(source, projection), 0
    try:
        source_bytes = source.read_bytes()
    except OSError:
        return (0, _remove_unreadable_projection(projection))
    if _file_matches(source, projection, source_bytes, api):
        return 0, 0
    if projection.exists() or projection.is_symlink():
        _remove_path(projection)
    projection.write_bytes(source_bytes)
    with contextlib.suppress(OSError):
        os.chmod(projection, source.stat().st_mode & 0o777)
    return 1, 0


def _sync_symlink(source: Path, projection: Path) -> int:
    target = os.readlink(source)
    if projection.is_symlink() and os.readlink(projection) == target:
        return 0
    if projection.exists() or projection.is_symlink():
        _remove_path(projection)
    projection.symlink_to(target)
    return 1


def _remove_unreadable_projection(projection: Path) -> int:
    if not (projection.exists() or projection.is_symlink()):
        return 0
    _remove_path(projection)
    return 1


def _file_matches(source: Path, projection: Path, source_bytes: bytes, api: ProjectionApi) -> bool:
    if not projection.exists() or not projection.is_file() or projection.is_symlink():
        return False
    try:
        projection_bytes = projection.read_bytes()
    except OSError:
        return False
    source_text = _normalized_text(source_bytes, source, api)
    if source_text is None:
        return projection_bytes == source_bytes
    return _normalized_text(projection_bytes, projection, api) == source_text


def _normalized_text(content: bytes, path: Path, api: ProjectionApi) -> str | None:
    if path.suffix not in api.STAMPABLE_SUFFIXES:
        return None
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return api.strip_projection_header(text, path.suffix)[0]


def _remove_empty_dirs(root: Path) -> None:
    for path in sorted(root.rglob("*"), reverse=True):
        if path.is_dir() and not path.is_symlink():
            with contextlib.suppress(OSError):
                path.rmdir()


def prune_nested_duplicate_skill_identities(skills_root: Path) -> tuple[list[str], int]:
    direct = _direct_skill_packages(skills_root)
    if not direct:
        return [], 0
    duplicates = _duplicate_nested_packages(skills_root, direct)
    logs: list[str] = []
    for target in sorted(duplicates, key=lambda path: len(path.parts), reverse=True):
        if not (target.exists() or target.is_symlink()):
            continue
        _remove_path(target)
        logs.append(f"Removed nested duplicate plugin skill identity: {target}")
    return logs, len(logs)


def _direct_skill_packages(skills_root: Path) -> dict[str, Path]:
    packages: dict[str, Path] = {}
    for child in skills_root.iterdir():
        skill_md = child / "SKILL.md"
        identity = skill_identity(skill_md) if child.is_dir() and skill_md.is_file() else None
        if identity:
            packages[identity] = child
    return packages


def _duplicate_nested_packages(skills_root: Path, direct: dict[str, Path]) -> set[Path]:
    duplicates: set[Path] = set()
    for skill_md in skills_root.rglob("SKILL.md"):
        identity = skill_identity(skill_md)
        if skill_md.parent.parent == skills_root or identity not in direct:
            continue
        if package_tree_sha256(skill_md.parent) == package_tree_sha256(direct[identity]):
            duplicates.add(skill_md.parent)
    return duplicates


def skill_identity(skill_md: Path) -> str | None:
    try:
        lines = skill_md.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return None
    if not lines or lines[0].strip() != "---":
        return None
    return _frontmatter_name(lines[1:])


def _frontmatter_name(lines: list[str]) -> str | None:
    for line in lines:
        stripped = line.strip()
        if stripped == "---":
            break
        if stripped.startswith("name:"):
            return stripped.split(":", 1)[1].strip().strip('"').strip("'") or None
    return None


def package_tree_sha256(package_root: Path) -> str:
    records: list[bytes] = []
    paths = sorted(package_root.rglob("*"), key=lambda item: item.relative_to(package_root).as_posix().encode("utf-8"))
    for path in paths:
        records.append(_package_record(path, package_root))
    return hashlib.sha256(b"".join(records)).hexdigest()


def _package_record(path: Path, root: Path) -> bytes:
    relative = path.relative_to(root).as_posix()
    kind, mode, payload = _package_entry(path)
    digest = hashlib.sha256(payload).hexdigest()
    return f"{relative}\0{kind}\0{mode}\0{digest}\n".encode("utf-8")


def _package_entry(path: Path) -> tuple[str, str, bytes]:
    if path.is_symlink():
        return "symlink", "000", os.readlink(path).encode("utf-8", errors="surrogateescape")
    if path.is_dir():
        return "directory", f"{path.stat().st_mode & 0o111:03o}", b""
    if path.is_file():
        return "file", f"{path.stat().st_mode & 0o111:03o}", path.read_bytes()
    return "other", "000", b""


def replace_plugin_cache_package_copy(source: Path, projection: Path, *, excluded_dir_names: Iterable[str], api: ProjectionApi, keep_duplicates: bool = False) -> tuple[int, int, list[str]]:
    changed, deleted = api._sync_mirror_python(
        source, projection, follow_symlinks=False, excluded_dir_names=excluded_dir_names
    )
    logs: list[str] = []
    skills_root = projection / "skills"
    if not keep_duplicates and skills_root.is_dir():
        nested_logs, nested_deletes = api._prune_nested_duplicate_skill_identities(skills_root)
        logs.extend(nested_logs)
        deleted += nested_deletes
    logs.append(f"Replaced plugin cache package projection: {projection} <- {source}")
    return changed, deleted, logs


def is_rsync_permission_failure(error: subprocess.CalledProcessError) -> bool:
    output = "\n".join(part for part in (error.stderr, error.stdout) if isinstance(part, str) and part).lower()
    return bool(output) and any(marker in output for marker in ("operation not permitted", "permission denied"))
