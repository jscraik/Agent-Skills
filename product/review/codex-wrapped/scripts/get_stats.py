#!/usr/bin/env python3
"""
Compute Codex/Claude Code usage statistics from local logs.

Outputs JSON with:
- last_7_days: sessions, messages, files_changed
- last_30_days: sessions, messages, files_changed
- all_time: total_sessions, total_hours, total_messages, total_files
- top_file_types: list of {extension, count}
- top_repos: list of {repo, count}
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def find_log_dirs() -> list[Path]:
    """Find potential agent log directories."""
    candidates = [
        Path.home() / ".codex" / "logs",
        Path.home() / ".codex",
        Path.home() / ".claude" / "logs",
        Path.home() / ".claude",
    ]
    return [p for p in candidates if p.exists() and p.is_dir()]


def parse_timestamp(line: str) -> datetime | None:
    """Extract timestamp from log line if present."""
    # Try ISO format
    iso_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', line)
    if iso_match:
        try:
            return datetime.fromisoformat(iso_match.group(1))
        except ValueError:
            pass

    # Try common log format
    log_match = re.search(r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})', line)
    if log_match:
        try:
            return datetime.strptime(log_match.group(1), '%b %d %H:%M:%S')
        except ValueError:
            pass

    return None


def analyze_logs(log_dirs: list[Path], tz: timezone) -> dict[str, Any]:
    """Analyze log files and compute statistics."""
    now = datetime.now(tz)
    cutoff_7d = now - timedelta(days=7)
    cutoff_30d = now - timedelta(days=30)

    sessions_7d = 0
    sessions_30d = 0
    total_sessions = 0

    messages_7d = 0
    messages_30d = 0
    total_messages = 0

    files_7d = 0
    files_30d = 0
    total_files = 0

    file_types = Counter()
    repos = Counter()

    first_seen = now
    last_seen = datetime.min.replace(tzinfo=tz)

    for log_dir in log_dirs:
        for log_file in log_dir.rglob("*.log*"):
            if log_file.is_file():
                try:
                    stat = log_file.stat()
                    mtime = datetime.fromtimestamp(stat.st_mtime, tz=tz)

                    # Session detection via file modification
                    if mtime >= cutoff_7d:
                        sessions_7d += 1
                        sessions_30d += 1
                    elif mtime >= cutoff_30d:
                        sessions_30d += 1

                    total_sessions += 1
                    first_seen = min(first_seen, mtime)
                    last_seen = max(last_seen, mtime)

                    # Parse content
                    content = log_file.read_text(encoding='utf-8', errors='ignore')

                    # Count messages (heuristic: lines with common patterns)
                    msg_count = len([l for l in content.split('\n')
                                   if any(k in l.lower() for k in ['user:', 'assistant:', 'tool:'])])

                    if mtime >= cutoff_7d:
                        messages_7d += msg_count
                        messages_30d += msg_count
                    elif mtime >= cutoff_30d:
                        messages_30d += msg_count
                    total_messages += msg_count

                    # Extract file changes
                    file_changes = re.findall(r'(?:modified|created|deleted|changed)[\s:]+([^\s]+\.\w+)', content, re.IGNORECASE)

                    if mtime >= cutoff_7d:
                        files_7d += len(file_changes)
                        files_30d += len(file_changes)
                    elif mtime >= cutoff_30d:
                        files_30d += len(file_changes)
                    total_files += len(file_changes)

                    # Track file types
                    for f in file_changes:
                        ext = Path(f).suffix.lower() or 'no_extension'
                        file_types[ext] += 1

                    # Extract repo names from paths
                    repo_matches = re.findall(r'(?:/|\s)([\w-]+)/([\w-]+)\.(?:git|md|json|js|ts|py)', content)
                    for org, repo in repo_matches:
                        repos[f"{org}/{repo}"] += 1

                except (OSError, IOError):
                    continue

    # Estimate focus hours (simplistic: 5 min per session minimum)
    total_hours = max(total_sessions * 5 / 60, (last_seen - first_seen).total_seconds() / 3600 if total_sessions > 0 else 0)

    return {
        "generated_at": now.isoformat(),
        "last_7_days": {
            "sessions": sessions_7d,
            "messages": messages_7d,
            "files_changed": files_7d,
        },
        "last_30_days": {
            "sessions": sessions_30d,
            "messages": messages_30d,
            "files_changed": files_30d,
        },
        "all_time": {
            "total_sessions": total_sessions,
            "total_hours": round(total_hours, 1),
            "total_messages": total_messages,
            "total_files": total_files,
            "first_session": first_seen.isoformat() if total_sessions > 0 else None,
            "last_session": last_seen.isoformat() if total_sessions > 0 else None,
        },
        "top_file_types": [{"extension": k, "count": v} for k, v in file_types.most_common(5)],
        "top_repos": [{"repo": k, "sessions": v} for k, v in repos.most_common(5)],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute agent usage statistics")
    parser.add_argument("--output", "-o", required=True, help="Output JSON file path")
    parser.add_argument("--timezone", help="Timezone name (default: system)")
    args = parser.parse_args()

    tz = timezone.utc
    if args.timezone:
        try:
            import zoneinfo
            tz = zoneinfo.ZoneInfo(args.timezone)
        except Exception:
            pass

    log_dirs = find_log_dirs()
    if not log_dirs:
        print("No agent log directories found.", file=os.sys.stderr)
        os.sys.exit(1)

    stats = analyze_logs(log_dirs, tz)

    with open(args.output, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"Stats written to {args.output}")


if __name__ == "__main__":
    main()
