"""Report assembly for keep-codex-fast."""

from __future__ import annotations

import argparse
import os
import sqlite3
import time
from pathlib import Path
from typing import Any

from keep_codex_fast_classify import human_size, likely_cause, likely_subsystem
from keep_codex_fast_scan import DEFAULT_TARGETS, ScanBudget, logical_size, walk_target


def sqlite_sidecars(path: Path) -> dict[str, Any]:
    sidecars: dict[str, Any] = {}
    for suffix in ("-wal", "-shm"):
        sidecar = Path(f"{path}{suffix}")
        if sidecar.exists():
            key = suffix[1:]
            sidecars[f"{key}_size"] = human_size(logical_size(sidecar))
            sidecars[f"{key}_size_bytes"] = logical_size(sidecar)
    return sidecars


def sqlite_metadata(path: Path) -> dict[str, Any]:
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=1.0) as con:
        query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        return {
            "page_count": con.execute("PRAGMA page_count").fetchone()[0],
            "page_size": con.execute("PRAGMA page_size").fetchone()[0],
            "tables": [row[0] for row in con.execute(query).fetchall()],
        }


def sqlite_diagnostics(path: Path) -> dict[str, Any]:
    size = logical_size(path)
    result: dict[str, Any] = {"path": str(path), "size_bytes": size, "size": human_size(size)}
    try:
        result.update(sqlite_metadata(path))
    except Exception as exc:  # noqa: BLE001 - diagnostics must not fail report mode
        result["sqlite_readonly_inspection"] = f"blocked: {type(exc).__name__}: {exc}"
    result.update(sqlite_sidecars(path))
    subsystem = likely_subsystem(path)
    result["likely_subsystem"] = subsystem
    result["likely_cause"] = likely_cause(path, subsystem)
    return result


def scan_targets(codex_home: Path, args: argparse.Namespace) -> list[dict[str, Any]]:
    threshold = args.large_threshold_mb * 1024 * 1024
    targets = [codex_home, *(codex_home / name for name in DEFAULT_TARGETS)]
    return [
        walk_target(
            target,
            budget=ScanBudget(time.monotonic(), args.max_seconds_per_target, args.max_files_per_target),
            large_threshold_bytes=threshold,
            top_n=args.top_n,
        )
        for target in targets
    ]


def collect_sqlite_diagnostics(storage_targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    paths = {path for target in storage_targets for path in target.get("sqlite_candidates", [])}
    return [sqlite_diagnostics(Path(path)) for path in sorted(paths)]


def collect_large_explanations(storage_targets: list[dict[str, Any]], top_n: int) -> list[dict[str, Any]]:
    seen: set[str] = set()
    explanations: list[dict[str, Any]] = []
    for target in storage_targets:
        for item in target.get("large_files", []):
            if item["path"] not in seen:
                seen.add(item["path"])
                explanations.append({**item, "evidence": "path/name, size, mtime; no content read"})
    explanations.sort(key=lambda item: item["size_bytes"], reverse=True)
    return explanations[:top_n]


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    started = time.monotonic()
    codex_home = Path(args.codex_home or os.environ.get("CODEX_HOME", "~/.codex")).expanduser()
    storage_targets = scan_targets(codex_home, args)
    return {
        "schema_version": "keep-codex-fast.report.v3",
        "mode": "report-dry-run",
        "status": "pass",
        "codex_home": str(codex_home),
        "mutation_plan": "none",
        "created_artifacts": [],
        "limits": {
            "large_threshold_mb": args.large_threshold_mb,
            "top_n": args.top_n,
            "max_files_per_target": args.max_files_per_target,
            "max_seconds_per_target": args.max_seconds_per_target,
        },
        "storage_targets": storage_targets,
        "large_target_explanations": collect_large_explanations(storage_targets, args.top_n),
        "sqlite_diagnostics": collect_sqlite_diagnostics(storage_targets),
        "elapsed_ms": int((time.monotonic() - started) * 1000),
        "residual_risk": "metadata-only report; content, raw thread titles, and secrets were not inspected",
    }
