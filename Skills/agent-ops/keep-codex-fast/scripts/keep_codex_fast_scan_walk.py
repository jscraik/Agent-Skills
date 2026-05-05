"""Directory walking helpers for keep-codex-fast."""

from __future__ import annotations

import os
from pathlib import Path

from keep_codex_fast_scan_model import TargetScan


def stat_path(path: Path, *, follow: bool = True) -> os.stat_result | None:
    try:
        return path.stat() if follow else path.lstat()
    except OSError:
        return None


def scan_single_file(scan: TargetScan) -> None:
    if not scan.scan_root or not scan.scan_root.is_file():
        return
    stat = stat_path(scan.scan_root)
    if stat:
        scan.observe_file(scan.scan_root, stat)


def scan_directory(scan: TargetScan) -> None:
    if not scan.scan_root or not scan.scan_root.is_dir():
        return
    for dirpath, dirnames, filenames in os.walk(scan.scan_root, followlinks=False):
        scan.observe_dir(dirnames)
        if scan_files(scan, dirpath, filenames):
            return


def scan_files(scan: TargetScan, dirpath: str, filenames: list[str]) -> bool:
    for filename in filenames:
        if scan.budget.exhausted(scan.files_seen):
            scan.truncated = True
            return True
        path = Path(dirpath) / filename
        stat = stat_path(path)
        if stat:
            scan.observe_file(path, stat)
    return False
