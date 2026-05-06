"""Bounded target preparation for keep-codex-fast."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from keep_codex_fast_scan_model import ScanBudget, TargetScan
from keep_codex_fast_scan_walk import scan_directory, scan_single_file, stat_path

DEFAULT_TARGETS = (
    "sessions",
    "archived_sessions",
    "worktrees",
    "log",
    "sqlite",
    "tmp",
    ".tmp",
    "generated_images",
    "backups",
    "quarantine",
    "cache",
)


def path_kind(path: Path) -> str:
    type_checks = ((path.is_symlink, "symlink"), (path.is_dir, "directory"), (path.is_file, "file"))
    return next((label for check, label in type_checks if check()), "missing")


def logical_size(path: Path) -> int:
    stat = stat_path(path)
    return stat.st_size if stat else 0


def prepare_scan(root: Path, budget: ScanBudget, threshold: int, top_n: int) -> TargetScan:
    kind = path_kind(root)
    resolved = root.resolve(strict=False) if kind != "missing" else None
    readable = os.access(root, os.R_OK)
    scan_root = resolved if kind == "symlink" and resolved else root
    return TargetScan(root, scan_root, kind, readable, resolved, budget, threshold, top_n)


def walk_target(root: Path, *, budget: ScanBudget, large_threshold_bytes: int, top_n: int) -> dict[str, Any]:
    scan = prepare_scan(root, budget, large_threshold_bytes, top_n)
    if scan.kind != "missing" and scan.readable:
        scan_single_file(scan)
        scan_directory(scan)
    return scan.payload()
