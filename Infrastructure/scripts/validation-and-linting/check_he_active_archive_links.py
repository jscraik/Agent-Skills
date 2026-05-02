#!/usr/bin/env python3
"""Reject active Harness Engineering package payload regressions."""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import sys
import tempfile
from pathlib import Path


# Derive PLUGIN_ROOT as absolute path from repository root
PLUGIN_ROOT = Path(__file__).resolve().parents[2] / "Plugins" / "harness-engineering"
DISALLOWED_ACTIVE_PATHS = (
    Path("tests"),
    Path("skills/_template_utils.py"),
)


def path_mentions_budget_archive(path: Path | str) -> bool:
    """Check if path contains consecutive components 'fixtures' followed by 'budget-archive'."""
    path_obj = Path(path)
    parts = path_obj.parts
    # Check for consecutive "fixtures" and "budget-archive" components
    for i in range(len(parts) - 1):
        if parts[i] == "fixtures" and parts[i + 1] == "budget-archive":
            return True
    return False


def is_active_surface(path: Path) -> bool:
    try:
        relative = path.relative_to(PLUGIN_ROOT)
    except ValueError:
        return False
    return relative.parts[:1] != ("fixtures",)


def link_violates(path: Path) -> bool:
    if not path.is_symlink() or not is_active_surface(path):
        return False

    link_target = os.readlink(path)
    if path_mentions_budget_archive(link_target):
        return True

    try:
        resolved = path.resolve(strict=True)
    except FileNotFoundError:
        return False

    return path_mentions_budget_archive(resolved)


def iter_violations() -> list[Path]:
    if not PLUGIN_ROOT.exists():
        raise FileNotFoundError(f"missing plugin root: {PLUGIN_ROOT}")
    return sorted(path for path in PLUGIN_ROOT.rglob("*") if link_violates(path))


def iter_disallowed_active_payload() -> list[Path]:
    if not PLUGIN_ROOT.exists():
        raise FileNotFoundError(f"missing plugin root: {PLUGIN_ROOT}")

    violations: list[Path] = []
    for relative_path in DISALLOWED_ACTIVE_PATHS:
        candidate = PLUGIN_ROOT / relative_path
        if candidate.exists() or candidate.is_symlink():
            violations.append(candidate)
    return violations


def copy_file_target(source: Path, destination: Path) -> None:
    mode = stat.S_IMODE(source.stat().st_mode)
    data = source.read_bytes()
    destination.unlink()
    destination.write_bytes(data)
    destination.chmod(mode)


def copy_dir_target(source: Path, destination: Path) -> None:
    parent = destination.parent
    with tempfile.TemporaryDirectory(
        prefix=f".{destination.name}.materialize.", dir=parent
    ) as tmp_dir:
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
    parser = argparse.ArgumentParser(
        description=(
            "Check that active Harness Engineering plugin files do not resolve "
            "through fixtures/budget-archive snapshots."
        )
    )
    parser.add_argument(
        "--repair",
        action="store_true",
        help="Replace violating active symlinks with materialized files or directories.",
    )
    args = parser.parse_args()

    violations = iter_violations()
    disallowed_payload = iter_disallowed_active_payload()
    if args.repair:
        for path in violations:
            repair_link(path)
        repaired = len(violations)
        remaining = iter_violations()
        if remaining:
            print(
                "[he-archive-links] ERROR: repair left archive-backed active links:",
                file=sys.stderr,
            )
            for path in remaining:
                print(f"  - {path} -> {os.readlink(path)}", file=sys.stderr)
            return 1
        if disallowed_payload:
            print(
                "[he-archive-links] ERROR: --repair does not move dev/test package payload:",
                file=sys.stderr,
            )
            for path in disallowed_payload:
                print(f"  - {path}", file=sys.stderr)
            return 1
        print(f"[he-archive-links] repaired {repaired} archive-backed active links")
        return 0

    if violations or disallowed_payload:
        if disallowed_payload:
            print(
                "[he-archive-links] ERROR: active Harness Engineering package "
                "payload must not include dev/test helper files:",
                file=sys.stderr,
            )
            for path in disallowed_payload:
                print(f"  - {path}", file=sys.stderr)
            print(
                "[he-archive-links] Fix: keep tests/helpers under Infrastructure "
                "or another repo-owned support path outside the plugin package.",
                file=sys.stderr,
            )
        if violations:
            print(
                "[he-archive-links] ERROR: active Harness Engineering links must not "
                "target fixtures/budget-archive:",
                file=sys.stderr,
            )
            for path in violations:
                print(f"  - {path} -> {os.readlink(path)}", file=sys.stderr)
            print(
                "[he-archive-links] Fix: materialize active plugin files and keep "
                "fixtures/budget-archive as historical input only.",
                file=sys.stderr,
            )
        return 1

    print("[he-archive-links] pass: no active budget-archive links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
