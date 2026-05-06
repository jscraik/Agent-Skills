"""Classification helpers for keep-codex-fast reports."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

SUBSYSTEM_PATTERNS = (
    (re.compile(r"(^|/)logs_[^/]*\.sqlite$"), "codex_event_log_sqlite"),
    (re.compile(r"(^|/)state_[^/]*\.sqlite$"), "codex_app_state_sqlite"),
    (re.compile(r"sessions/.+\.jsonl$"), "codex_session_rollout_jsonl"),
    (re.compile(r"\.log(\.|$)"), "plain_runtime_log"),
    (re.compile(r"generated_images"), "generated_media"),
    (re.compile(r"worktrees?"), "codex_worktree"),
    (re.compile(r"(^|/)\.?tmp(/|$)"), "temporary_runtime_artifact"),
)

CAUSES = {
    "codex_event_log_sqlite": "accumulated Codex log/event rows in the logs database",
    "codex_app_state_sqlite": "accumulated Codex app state, thread metadata, jobs, and agent state",
    "codex_session_rollout_jsonl": "large Codex session transcript or archived rollout history",
    "plain_runtime_log": "accumulated plain-text runtime logging",
    "codex_worktree": "Git object packs, caches, patches, or checkout files inside Codex worktrees",
    "temporary_runtime_artifact": "temporary Codex execution artifacts; inspect recency before cleanup",
    "generated_media": "generated image or media artifacts",
}


def human_size(size: int) -> str:
    units = ("B", "K", "M", "G", "T")
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f}{unit}" if unit != "B" else f"{int(value)}B"
        value /= 1024
    return f"{size}B"


def likely_subsystem(path: Path) -> str:
    text = str(path)
    for pattern, label in SUBSYSTEM_PATTERNS:
        if pattern.search(text):
            return label
    return "unknown_large_file"


def likely_cause(path: Path, subsystem: str) -> str:
    return CAUSES.get(subsystem, "unknown from metadata alone")


def describe_file(path: Path, stat: os.stat_result) -> dict[str, Any]:
    subsystem = likely_subsystem(path)
    return {
        "path": str(path),
        "size_bytes": stat.st_size,
        "size": human_size(stat.st_size),
        "modified_epoch": int(stat.st_mtime),
        "likely_subsystem": subsystem,
        "likely_cause": likely_cause(path, subsystem),
    }
