#!/usr/bin/env python3
"""Reject active plugin links that resolve through archived budget fixtures."""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def path_mentions_budget_archive(path: Path | str) -> bool:
    parts = Path(path).parts
    return any(parts[i] == "fixtures" and parts[i + 1] == "budget-archive" for i in range(len(parts) - 1))


def is_active_surface(plugin_root: Path, path: Path) -> bool:
    try:
        relative = path.relative_to(plugin_root)
    except ValueError:
        return False
    return relative.parts[:1] != ("fixtures",)


def link_violates(plugin_root: Path, path: Path) -> bool:
    if not path.is_symlink() or not is_active_surface(plugin_root, path):
        return False

    link_target = os.readlink(path)
    if path_mentions_budget_archive(link_target):
        return True

    try:
        resolved = path.resolve(strict=True)
    except FileNotFoundError:
        return False
    return path_mentions_budget_archive(resolved)


def iter_plugin_roots(plugin_names: list[str]) -> list[Path]:
    if plugin_names:
        return [REPO_ROOT / "Plugins" / plugin for plugin in plugin_names]
    return sorted(path for path in (REPO_ROOT / "Plugins").iterdir() if path.is_dir())


def iter_violations(plugin_root: Path) -> list[Path]:
    if not plugin_root.exists():
        raise FileNotFoundError(f"missing plugin root: {plugin_root}")
    return sorted(path for path in plugin_root.rglob("*") if link_violates(plugin_root, path))


def copy_file_target(source: Path, destination: Path) -> None:
    mode = stat.S_IMODE(source.stat().st_mode)
    data = source.read_bytes()
    destination.unlink()
    destination.write_bytes(data)
    destination.chmod(mode)


def copy_dir_target(source: Path, destination: Path) -> None:
    parent = destination.parent
    with tempfile.TemporaryDirectory(prefix=f".{destination.name}.materialize.", dir=parent) as tmp_dir:
        tmp_path = Path(tmp_dir) / destination.name
        shutil.copytree(source, tmp_path, symlinks=False)
        destination.unlink()
        tmp_path.rename(destination)


def repair_link(path: Path) -> None:
    source = path.resolve(strict=True)
    if source.is_dir():
        copy_dir_target(source, path)
    elif source.is_file():
        copy_file_target(source, path)
    else:
        raise RuntimeError(f"unsupported link target type: {path} -> {source}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin", action="append", default=[], help="Plugin name under Plugins/. May be repeated.")
    parser.add_argument("--repair", action="store_true", help="Materialize violating active symlinks.")
    args = parser.parse_args()

    all_violations: list[Path] = []
    for plugin_root in iter_plugin_roots(args.plugin):
        all_violations.extend(iter_violations(plugin_root))

    if args.repair:
        for path in all_violations:
            repair_link(path)
        remaining: list[Path] = []
        for plugin_root in iter_plugin_roots(args.plugin):
            remaining.extend(iter_violations(plugin_root))
        if remaining:
            print("[plugin-archive-links] ERROR: repair left active archive-backed links:", file=sys.stderr)
            for path in remaining:
                print(f"  - {path} -> {os.readlink(path)}", file=sys.stderr)
            return 1
        print(f"[plugin-archive-links] repaired {len(all_violations)} active archive-backed links")
        return 0

    if all_violations:
        print("[plugin-archive-links] ERROR: active plugin links must not target fixtures/budget-archive:", file=sys.stderr)
        for path in all_violations:
            print(f"  - {path} -> {os.readlink(path)}", file=sys.stderr)
        print("[plugin-archive-links] Fix: materialize active files and keep archives as historical fixtures only.", file=sys.stderr)
        return 1

    print("[plugin-archive-links] pass: no active budget-archive links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
