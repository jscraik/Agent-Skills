"""Read-only identity proof for Jamie's explicitly selected temporary installs.

The tracked identity record is authority; runtime-local manifests are not.
This proves copied package bytes and executable modes, not SDK admission,
discovery, execution, registry provenance, or permission to install anything.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from pathlib import Path

IDENTITY_RECORD = Path("Infrastructure/GOVERNANCE/runtime-separation/transitional-installs.json")
SCHEMA = "approved-transitional-installs/v1"
DIRECTORY_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
FILE_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
MAX_FILES = 4096
MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_PACKAGE_BYTES = 128 * 1024 * 1024
MAX_DEPTH = 32


def _fingerprint(metadata: os.stat_result) -> tuple[int, ...]:
    return (metadata.st_ino, metadata.st_dev, metadata.st_size, metadata.st_mode,
            metadata.st_mtime_ns, metadata.st_ctime_ns)


def _directory_names(directory: int, remaining: list[int]) -> list[str]:
    names = []
    with os.scandir(directory) as iterator:
        for entry in iterator:
            remaining[0] -= 1
            if remaining[0] < 0:
                raise ValueError("Package entry inventory exceeds the bounded verifier")
            names.append(entry.name)
    return sorted(names)


def _inventory(directory: int, prefix: str = "", remaining: list[int] | None = None) -> list[tuple[str, tuple[int, ...]]]:
    """Enumerate descriptors without following package or resource links."""
    entries: list[tuple[str, tuple[int, ...]]] = []
    if prefix.count("/") > MAX_DEPTH:
        raise ValueError("Package directory depth exceeds the bounded verifier")
    remaining = [MAX_FILES] if remaining is None else remaining
    for name in _directory_names(directory, remaining):
        metadata = os.stat(name, dir_fd=directory, follow_symlinks=False)
        relative = f"{prefix}{name}"
        if stat.S_ISDIR(metadata.st_mode):
            child = os.open(name, DIRECTORY_FLAGS, dir_fd=directory)
            try:
                entries.extend(_inventory(child, relative + "/", remaining))
            finally:
                os.close(child)
        elif stat.S_ISREG(metadata.st_mode):
            entries.append((relative, _fingerprint(metadata)))
        else:
            raise ValueError("Package contains a link or non-regular resource")
        if len(entries) > MAX_FILES:
            raise ValueError("Package inventory exceeds the bounded verifier")
    return entries


def _open_relative(directory: int, relative: str) -> int:
    """Open a resource through pinned, non-symlink directory descriptors."""
    parts = relative.split("/")
    parent = os.dup(directory)
    try:
        for part in parts[:-1]:
            child = os.open(part, DIRECTORY_FLAGS, dir_fd=parent)
            os.close(parent)
            parent = child
        return os.open(parts[-1], FILE_FLAGS, dir_fd=parent)
    finally:
        os.close(parent)


def _hash_resource(digest: object, directory: int, relative: str, expected: tuple[int, ...]) -> None:
    descriptor = _open_relative(directory, relative)
    try:
        before = os.fstat(descriptor)
        size = expected[2]
        if not stat.S_ISREG(before.st_mode) or _fingerprint(before) != expected or size > MAX_FILE_BYTES:
            raise ValueError("Invalid, changed, or oversized resource")
        mode = b"100755" if before.st_mode & stat.S_IXUSR else b"100644"
        for value in (mode, b"blob", relative.encode("utf-8")):
            digest.update(len(value).to_bytes(8, "big"))
            digest.update(value)
        digest.update(size.to_bytes(8, "big"))
        consumed = 0
        while chunk := os.read(descriptor, 65536):
            consumed += len(chunk)
            if consumed > size:
                raise ValueError("Resource changed during verification")
            digest.update(chunk)
        after = os.fstat(descriptor)
        if consumed != size or _fingerprint(before) != _fingerprint(after):
            raise ValueError("Resource changed during verification")
    finally:
        os.close(descriptor)


def package_identity(directory: int) -> tuple[str, int]:
    """Use Foundry's mode-sensitive, length-prefixed source-tree algorithm."""
    files = _inventory(directory)
    if "SKILL.md" not in {relative for relative, _ in files}:
        raise ValueError("Package has no SKILL.md")
    if sum(metadata[2] for _, metadata in files) > MAX_PACKAGE_BYTES:
        raise ValueError("Package exceeds the bounded verifier")
    digest = hashlib.sha256()
    for relative, metadata in sorted(files, key=lambda item: item[0].encode("utf-8")):
        _hash_resource(digest, directory, relative, metadata)
    if files != _inventory(directory):
        raise ValueError("Package inventory changed during verification")
    return digest.hexdigest(), len(files)


def _approved_identity(repo_root: Path, handle: str) -> dict:
    record = json.loads((repo_root / IDENTITY_RECORD).read_text(encoding="utf-8"))
    if not isinstance(record, dict) or record.get("schema_version") != SCHEMA:
        raise ValueError("Unsupported identity record")
    packages = record.get("packages")
    if not isinstance(packages, dict):
        raise ValueError("Invalid package identity map")
    entry = packages.get(handle)
    if not isinstance(entry, dict) or entry.get("approval") != "jamie-temporary-sdk-exemption":
        raise ValueError("Package is not in the explicitly approved temporary set")
    if not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("sha256", ""))):
        raise ValueError("Approved package identity is missing")
    if not isinstance(entry.get("file_count"), int) or not entry.get("source_ref"):
        raise ValueError("Approved package provenance is missing")
    return entry


def _installed_identity(home: Path, handle: str) -> tuple[str, int]:
    parent = os.open(home, DIRECTORY_FLAGS)
    try:
        for name in (".agents", "skills", handle):
            child = os.open(name, DIRECTORY_FLAGS, dir_fd=parent)
            os.close(parent)
            parent = child
        return package_identity(parent)
    finally:
        os.close(parent)


def verify_transitional_install(*, repo_root: Path, home: Path, handle: str) -> dict:
    """Reject unknown identities; never modify home or accept runtime authority."""
    result = {"status": "fail", "classification": "unchecked_transitional_install",
              "sdk_clearance": False, "live_invocation_verified": False}
    try:
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", handle):
            raise ValueError("Unsafe skill handle")
        expected = _approved_identity(repo_root, handle)
        actual, count = _installed_identity(home, handle)
        if actual != expected["sha256"] or count != expected["file_count"]:
            raise ValueError("Installed package differs from the approved complete identity")
        result.update(status="pass", classification="verified_transitional_copy",
                      sha256=actual, file_count=count, source_ref=expected["source_ref"])
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        result["diagnostic"] = "Approved identity absent, mismatched, unsafe, or unreadable; preserve the installation."
    return result
