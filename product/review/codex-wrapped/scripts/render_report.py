#!/usr/bin/env python3
"""
Render a text-based usage report from stats JSON.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from typing import Any


def format_number(n: int) -> str:
    """Format large numbers with commas."""
    return f"{n:,}"


def render_box(title: str, content: str, width: int = 60) -> str:
    """Render a box with title."""
    lines = content.strip().split('\n')
    result = []
    result.append('┌' + '─' * (width - 2) + '┐')
    result.append(f'│ {title:<{width - 3}}│')
    result.append('├' + '─' * (width - 2) + '┤')
    for line in lines:
        result.append(f'│ {line:<{width - 3}}│')
    result.append('└' + '─' * (width - 2) + '┘')
    return '\n'.join(result)


def render_report(stats: dict[str, Any]) -> str:
    """Render the wrapped report."""
    lines = []

    # Header
    lines.append('')
    lines.append('╔' + '═' * 58 + '╗')
    lines.append('║' + '  🎯 YOUR AGENT USAGE REPORT'.center(58) + '║')
    lines.append('╚' + '═' * 58 + '╝')
    lines.append('')

    # All-time stats
    all_time = stats.get('all_time', {})
    hours = all_time.get('total_hours', 0)
    sessions = all_time.get('total_sessions', 0)
    messages = all_time.get('total_messages', 0)
    files = all_time.get('total_files', 0)

    all_time_content = f"""Total Focus Hours:     {hours:>8.1f}
Total Sessions:        {format_number(sessions):>8}
Total Messages:        {format_number(messages):>8}
Files Changed:         {format_number(files):>8}"""

    lines.append(render_box('📊 ALL TIME', all_time_content))
    lines.append('')

    # Last 30 days
    last_30 = stats.get('last_30_days', {})
    if last_30.get('sessions', 0) > 0:
        content = f"""Sessions:              {format_number(last_30.get('sessions', 0)):>8}
Messages:              {format_number(last_30.get('messages', 0)):>8}
Files Changed:         {format_number(last_30.get('files_changed', 0)):>8}"""
        lines.append(render_box('📅 LAST 30 DAYS', content))
        lines.append('')

    # Last 7 days
    last_7 = stats.get('last_7_days', {})
    if last_7.get('sessions', 0) > 0:
        content = f"""Sessions:              {format_number(last_7.get('sessions', 0)):>8}
Messages:              {format_number(last_7.get('messages', 0)):>8}
Files Changed:         {format_number(last_7.get('files_changed', 0)):>8}"""
        lines.append(render_box('🚀 LAST 7 DAYS', content))
        lines.append('')

    # Top file types
    top_types = stats.get('top_file_types', [])
    if top_types:
        content_lines = []
        for ft in top_types[:5]:
            ext = ft.get('extension', 'unknown')
            count = ft.get('count', 0)
            content_lines.append(f"{ext:<20} {format_number(count):>8}")
        lines.append(render_box('📝 TOP FILE TYPES', '\n'.join(content_lines)))
        lines.append('')

    # Top repos
    top_repos = stats.get('top_repos', [])
    if top_repos:
        content_lines = []
        for repo in top_repos[:5]:
            name = repo.get('repo', 'unknown')
            count = repo.get('sessions', 0)
            content_lines.append(f"{name:<30} {format_number(count):>8}")
        lines.append(render_box('📁 TOP REPOSITORIES', '\n'.join(content_lines)))
        lines.append('')

    # Footer
    generated = stats.get('generated_at', datetime.now().isoformat())
    lines.append(f"Generated: {generated[:19]}")
    lines.append('')

    return '\n'.join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render usage report from stats")
    parser.add_argument("--stats-file", "-i", required=True, help="Input stats JSON file")
    args = parser.parse_args()

    if not os.path.exists(args.stats_file):
        print(f"Stats file not found: {args.stats_file}", file=os.sys.stderr)
        os.sys.exit(1)

    with open(args.stats_file) as f:
        stats = json.load(f)

    print(render_report(stats))


if __name__ == "__main__":
    main()
