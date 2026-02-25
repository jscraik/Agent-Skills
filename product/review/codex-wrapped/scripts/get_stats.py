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
    existing = [p.resolve() for p in candidates if p.exists() and p.is_dir()]
    existing.sort(key=lambda p: len(str(p)))
    pruned: list[Path] = []
    for path in existing:
        if any(path == root or str(path).startswith(str(root) + os.sep) for root in pruned):
            continue
        pruned.append(path)
    return pruned


def parse_timestamp(line: str, tz: timezone, now: datetime) -> datetime | None:
    """Extract timestamp from log line if present."""
    # Try ISO format
    iso_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:?\d{2})?)', line)
    if iso_match:
        try:
            parsed = datetime.fromisoformat(iso_match.group(1).replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=tz)
            return parsed.astimezone(tz)
        except ValueError:
            pass

    # Try common log format
    log_match = re.search(r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})', line)
    if log_match:
        try:
            parsed = datetime.strptime(log_match.group(1), '%b %d %H:%M:%S').replace(
                year=now.year,
                tzinfo=tz,
            )
            if parsed > now + timedelta(days=1):
                parsed = parsed.replace(year=now.year - 1)
            return parsed
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

    seen_log_files: set[Path] = set()
    for log_dir in log_dirs:
        for log_file in log_dir.rglob("*.log*"):
            resolved_file = log_file.resolve()
            if resolved_file in seen_log_files:
                continue
            seen_log_files.add(resolved_file)
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
                    repo_mentions_in_file: set[str] = set()
                    for line in content.splitlines():
                        lower = line.lower()
                        line_ts = parse_timestamp(line, tz=tz, now=now) or mtime
                        in_7d = line_ts >= cutoff_7d
                        in_30d = line_ts >= cutoff_30d

                        if any(k in lower for k in ['user:', 'assistant:', 'tool:']):
                            total_messages += 1
                            if in_7d:
                                messages_7d += 1
                                messages_30d += 1
                            elif in_30d:
                                messages_30d += 1

                        file_changes = re.findall(
                            r'(?:modified|created|deleted|changed)[\s:]+([^\s]+\.\w+)',
                            line,
                            re.IGNORECASE,
                        )
                        for changed in file_changes:
                            total_files += 1
                            if in_7d:
                                files_7d += 1
                                files_30d += 1
                            elif in_30d:
                                files_30d += 1
                            ext = Path(changed).suffix.lower() or 'no_extension'
                            file_types[ext] += 1

                        repo_matches = re.findall(
                            r'(?:/|\s)([\w-]+)/([\w-]+)\.(?:git|md|json|js|ts|py)',
                            line,
                        )
                        for org, repo in repo_matches:
                            repo_mentions_in_file.add(f"{org}/{repo}")

                    for repo_name in repo_mentions_in_file:
                        repos[repo_name] += 1

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
