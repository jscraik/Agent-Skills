"""Scan state and small helpers for keep-codex-fast."""

from __future__ import annotations

import heapq
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from keep_codex_fast_classify import describe_file, human_size


@dataclass
class ScanBudget:
    started_at: float
    max_seconds: float
    max_files_per_target: int

    def exhausted(self, seen_files: int) -> bool:
        timed_out = time.monotonic() - self.started_at >= self.max_seconds
        return seen_files >= self.max_files_per_target or timed_out


@dataclass
class TargetScan:
    root: Path
    scan_root: Path | None
    kind: str
    readable: bool
    resolved: Path | None
    budget: ScanBudget
    large_threshold_bytes: int
    top_n: int
    started_at: float = field(default_factory=time.monotonic)
    files_seen: int = 0
    dirs_seen: int = 0
    total_size: int = 0
    session_jsonl: int = 0
    truncated: bool = False
    large_heap: list[tuple[int, str, dict[str, Any]]] = field(default_factory=list)
    recent_heap: list[tuple[float, str, dict[str, Any]]] = field(default_factory=list)
    sqlite_paths: list[Path] = field(default_factory=list)

    def observe_dir(self, names: list[str]) -> None:
        self.dirs_seen += len(names)

    def observe_file(self, path: Path, stat: os.stat_result) -> None:
        self.files_seen += 1
        self.total_size += stat.st_size
        self.session_jsonl += int(path.name.endswith(".jsonl") and "sessions" in str(self.root))
        item = describe_file(path, stat)
        is_large = stat.st_size >= self.large_threshold_bytes
        push_limited(self.large_heap, (stat.st_size, str(path), item), self.top_n, is_large)
        push_limited(self.recent_heap, (stat.st_mtime, str(path), item), min(3, self.top_n), True)
        if path.suffix in {".sqlite", ".db"} and stat.st_size >= 10 * 1024 * 1024:
            self.sqlite_paths.append(path)

    def payload(self) -> dict[str, Any]:
        return {
            "path": str(self.root),
            "kind": self.kind,
            "resolved_target": str(self.resolved) if self.resolved else None,
            "readable": self.readable,
            "size_bytes": self.total_size,
            "size": human_size(self.total_size),
            "file_count": self.files_seen,
            "directory_count": self.dirs_seen,
            "session_jsonl_count": self.session_jsonl if "sessions" in str(self.root) else None,
            "large_files": heap_items(self.large_heap),
            "recent_files": heap_items(self.recent_heap),
            "sqlite_candidates": [str(path) for path in self.sqlite_paths[: self.top_n]],
            "truncated": self.truncated,
            "scan_limit_files": self.budget.max_files_per_target,
            "elapsed_ms": int((time.monotonic() - self.started_at) * 1000),
            "evidence": evidence_label(self.kind),
        }


def push_limited(heap: list[Any], item: Any, limit: int, enabled: bool) -> None:
    if not enabled:
        return
    heapq.heappush(heap, item)
    if len(heap) > limit:
        heapq.heappop(heap)


def heap_items(heap: list[tuple[Any, str, dict[str, Any]]]) -> list[dict[str, Any]]:
    return [item for _, _, item in sorted(heap, reverse=True)]


def evidence_label(kind: str) -> str:
    labels = {
        "symlink": "symlink followed for metadata-only inspection",
        "missing": "target missing or unreadable",
    }
    return labels.get(kind, "local filesystem metadata only")
