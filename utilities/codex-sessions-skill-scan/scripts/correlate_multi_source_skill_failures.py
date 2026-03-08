#!/usr/bin/env python3
"""
Correlate explicit skill/tool failure signals across Codex/Claude/Kimi sources.

Design goals:
- Stdlib-only
- Explicit failure signals only (avoid broad keyword noise)
- De-duplicated evidence
- Redacted snippets
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

sys.dont_write_bytecode = True

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+")
TOKEN_RE = re.compile(r"\b(?:sk-[A-Za-z0-9_-]{12,}|Bearer\s+[A-Za-z0-9._-]{12,})\b", re.I)

# Explicit-only failure classes
PATTERNS = {
    "skill_md_not_found": re.compile(r"SKILL\.md\s+not\s+found", re.I),
    "skill_frontmatter_missing": re.compile(r"SKILL\.md\s+frontmatter\s+missing", re.I),
    "skill_path_missing": re.compile(r"skill path does not exist|cannot read [^\n]{0,240}SKILL\.md", re.I),
    "tool_exec_failed": re.compile(r"exec_command failed", re.I),
    "tool_stdin_failed": re.compile(r"write_stdin failed:\s*stdin is closed for this session", re.I),
    "nonzero_exit": re.compile(r"Process exited with code ([1-9][0-9]*)", re.I),
    "tool_result_error": re.compile(r'"is_error"\s*:\s*true', re.I),
    "claude_auth_failed": re.compile(r"authentication_failed|claude auth status[^\n]{0,80}loggedin\s*=\s*false", re.I),
}

SKILL_FROM_PATH_RE = re.compile(r"/([a-z0-9-]+)/SKILL\.md", re.I)
SKILL_INVOKE_RE = re.compile(r"Using skill:\s*`?([a-z0-9][a-z0-9-]{1,63})`?", re.I)
NOISE_RE = re.compile(
    r"## Inputs\s*- since:|explicit_issues:|Correlate explicit skill/tool failure signals across|scan_codex_sessions\.py",
    re.I,
)
NONZERO_RELEVANT_RE = re.compile(
    r"SKILL\.md|agent-skills/(?:utilities|skills-system|frontend|product|backend|personas)|scan_codex_sessions|codex-sessions-skill-scan|skill-builder|quick_validate|skill_gate|run_skill_evals|command not found: (rg|fd)",
    re.I,
)
TOOL_FAILURE_RELEVANT_RE = re.compile(
    r"SKILL\.md|agent-skills/(?:utilities|skills-system|frontend|product|backend|personas)|codex-sessions-skill-scan|skill-builder|quick_validate|skill_gate|run_skill_evals",
    re.I,
)
SKILL_ERROR_CONTEXT_RE = re.compile(r"ERROR:|FileNotFoundError|Traceback|\bfail(?:ed)?\b|\bIssue\b", re.I)
PRIMARY_EXIT_RE = re.compile(r"Process exited with code (\d+)", re.I)
CODE_DUMP_RE = re.compile(r'(^|\n)\s*(?:\d+\s+)?#!/usr/bin/env python3|(^|\n)\s*"""', re.I)
PATH_LINE_LISTING_RE = re.compile(r"(?m)^\s*/[^\n]+:\d+:")


@dataclass(frozen=True)
class Issue:
    source: str
    file: Path
    pattern: str
    skill: str | None
    snippet: str


def now_local() -> dt.datetime:
    return dt.datetime.now().astimezone()


def redact(s: str) -> str:
    s = EMAIL_RE.sub("<redacted_email>", s)
    s = TOKEN_RE.sub("<redacted_token>", s)
    return s


def normalize_for_dedupe(s: str) -> str:
    s = re.sub(r"\bcall_[A-Za-z0-9]+\b", "call_<id>", s)
    s = re.sub(r"\b[0-9a-f]{8,}\b", "<hex>", s, flags=re.I)
    s = re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?", "<ts>", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def iter_recent_files(path: Path, since: dt.datetime) -> Iterator[Path]:
    since_ts = since.timestamp()
    if path.is_file():
        try:
            if path.stat().st_mtime >= since_ts:
                yield path
        except FileNotFoundError:
            return
        return

    if not path.exists():
        return

    for dirpath, _, filenames in os.walk(path):
        for name in filenames:
            if not (name.endswith(".jsonl") or name.endswith(".ndjson") or name.endswith(".json")):
                continue
            p = Path(dirpath) / name
            try:
                if p.stat().st_mtime >= since_ts:
                    yield p
            except FileNotFoundError:
                continue


def select_recent_files(path: Path, since: dt.datetime, max_files_per_source: int) -> list[Path]:
    files = list(iter_recent_files(path, since))
    files.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    if max_files_per_source > 0:
        files = files[:max_files_per_source]
    return files


def iter_lines_recent_window(fpath: Path, max_bytes_per_file: int) -> Iterator[str]:
    """
    Stream lines from a file; for very large files, scan only the trailing bytes.
    Keeps runs bounded for multi-GB OTel artifacts.
    """
    try:
        size = fpath.stat().st_size
    except OSError:
        return

    start = 0
    if max_bytes_per_file > 0 and size > max_bytes_per_file:
        start = max(0, size - max_bytes_per_file)

    try:
        with fpath.open("rb") as fh:
            if start:
                fh.seek(start)
                _ = fh.readline()  # drop partial line
            for bline in fh:
                try:
                    yield bline.decode("utf-8", errors="replace")
                except Exception:
                    continue
    except OSError:
        return


def extract_skill(text: str) -> str | None:
    m = SKILL_INVOKE_RE.search(text)
    if m:
        return m.group(1).lower()
    m = SKILL_FROM_PATH_RE.search(text)
    if m:
        return m.group(1).lower()
    return None


def extract_text_candidates(line: str) -> list[str]:
    """
    Prefer semantic payload fields over raw JSON lines to avoid self-match noise
    from command arguments that merely contain pattern strings.
    """
    text = line.strip()
    if not text:
        return []
    if not text.startswith("{"):
        return [text]

    try:
        obj = json.loads(text)
    except Exception:
        return [text]

    out: list[str] = []
    if isinstance(obj.get("error"), str):
        out.append(obj["error"])
    if isinstance(obj.get("toolUseResult"), str):
        out.append(obj["toolUseResult"])

    payload = obj.get("payload")
    if isinstance(payload, dict):
        ptype = payload.get("type")
        if ptype == "function_call_output" and isinstance(payload.get("output"), str):
            out.append(payload["output"])
        if isinstance(payload.get("error"), str):
            out.append(payload["error"])
        rv = payload.get("return_value")
        if isinstance(rv, dict):
            if isinstance(rv.get("output"), str):
                out.append(rv["output"])
            if rv.get("is_error") is True:
                out.append('"is_error": true')

    message = obj.get("message")
    if isinstance(message, dict):
        if isinstance(message.get("error"), str):
            out.append(message["error"])

    return [x for x in out if isinstance(x, str) and x.strip()]


def scan_source(
    source_name: str,
    root: Path,
    since: dt.datetime,
    dedupe: set[str],
    max_bytes_per_file: int,
    max_files_per_source: int,
) -> list[Issue]:
    out: list[Issue] = []

    for fpath in select_recent_files(root, since, max_files_per_source=max_files_per_source):
        for line in iter_lines_recent_window(fpath, max_bytes_per_file=max_bytes_per_file):
            candidates = extract_text_candidates(line)
            if not candidates:
                continue

            for text in candidates:
                if NOISE_RE.search(text):
                    continue

                primary_exit: int | None = None
                m_exit = PRIMARY_EXIT_RE.search(text)
                if m_exit:
                    try:
                        primary_exit = int(m_exit.group(1))
                    except ValueError:
                        primary_exit = None

                skill = extract_skill(text)
                for pname, preg in PATTERNS.items():
                    if not preg.search(text):
                        continue
                    if pname == "nonzero_exit":
                        if primary_exit is None or primary_exit == 0:
                            continue
                        if not NONZERO_RELEVANT_RE.search(text):
                            continue
                    if pname in {"tool_exec_failed", "tool_stdin_failed", "tool_result_error"} and not TOOL_FAILURE_RELEVANT_RE.search(text):
                        continue
                    if pname == "tool_exec_failed" and "Process running with session ID" in text:
                        continue
                    if pname in {"skill_md_not_found", "skill_frontmatter_missing", "skill_path_missing"}:
                        if not SKILL_ERROR_CONTEXT_RE.search(text):
                            continue
                        if primary_exit == 0 and (CODE_DUMP_RE.search(text) or PATH_LINE_LISTING_RE.search(text)):
                            continue
                    if pname == "claude_auth_failed":
                        if primary_exit == 0 and PATH_LINE_LISTING_RE.search(text):
                            continue
                        if "```diff" in text.lower():
                            continue

                    snippet = redact(text)
                    norm = normalize_for_dedupe(f"{pname}|{skill or '-'}|{snippet[:500]}")
                    key = hashlib.sha256(norm.encode("utf-8")).hexdigest()
                    if key in dedupe:
                        continue
                    dedupe.add(key)

                    out.append(
                        Issue(
                            source=source_name,
                            file=fpath,
                            pattern=pname,
                            skill=skill,
                            snippet=snippet[:220],
                        )
                    )

    return out


def render_report(issues: list[Issue], since: dt.datetime, now: dt.datetime) -> str:
    lines: list[str] = []
    lines.append("## Inputs")
    lines.append(f"- since: `{since.isoformat()}`")
    lines.append(f"- now: `{now.isoformat()}`")
    lines.append("")

    if not issues:
        lines.append("## Summary")
        lines.append("- explicit_issues: **0**")
        lines.append("- affected_skills: **0**")
        lines.append("- repeated_failures: **0**")
        lines.append("")
        lines.append("## Result")
        lines.append("No explicit multi-source skill/tool failures detected in the scanned window.")
        return "\n".join(lines) + "\n"

    by_pattern = Counter(i.pattern for i in issues)
    by_skill = Counter(i.skill for i in issues if i.skill)
    by_source = Counter(i.source for i in issues)

    lines.append("## Summary")
    lines.append(f"- explicit_issues: **{len(issues)}**")
    lines.append(f"- affected_skills: **{len(by_skill)}**")
    lines.append(f"- repeated_failures: **{sum(1 for _, c in by_pattern.items() if c > 1)}**")
    lines.append("")

    lines.append("## Failure classes (top)")
    for k, v in by_pattern.most_common(12):
        lines.append(f"- `{k}`: {v}")
    lines.append("")

    lines.append("## Affected skills (top)")
    if by_skill:
        for k, v in by_skill.most_common(12):
            lines.append(f"- `{k}`: {v}")
    else:
        lines.append("- none mapped")
    lines.append("")

    lines.append("## Sources")
    for k, v in by_source.most_common():
        lines.append(f"- `{k}`: {v}")
    lines.append("")

    lines.append("## Samples (redacted)")
    for it in issues[:10]:
        lines.append(f"- `{it.pattern}` `{it.file.name}`: `{it.snippet}`")

    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=float, default=7.0)
    parser.add_argument(
        "--max-bytes-per-file",
        type=int,
        default=100_000_000,
        help="Maximum bytes to scan per file (default: 100MB; scans tail on larger files).",
    )
    parser.add_argument(
        "--max-files-per-source",
        type=int,
        default=200,
        help="Maximum recent files to scan per source (default: 200).",
    )
    parser.add_argument("--codex-sessions", type=Path, default=Path.home() / ".codex" / "sessions")
    parser.add_argument("--codex-archived", type=Path, default=Path.home() / ".codex" / "archived_sessions")
    parser.add_argument("--codex-history", type=Path, default=Path.home() / ".codex" / "history.jsonl")
    parser.add_argument("--otel-logs", type=Path, default=Path.home() / ".codex" / "state" / "otel-collector" / "logs.ndjson")
    parser.add_argument("--otel-traces", type=Path, default=Path.home() / ".codex" / "state" / "otel-collector" / "traces.ndjson")
    parser.add_argument("--claude-projects", type=Path, default=Path.home() / ".claude" / "projects")
    parser.add_argument("--claude-history", type=Path, default=Path.home() / ".claude" / "history.jsonl")
    parser.add_argument("--kimi-sessions", type=Path, default=Path.home() / ".kimi" / "sessions")
    args = parser.parse_args(argv)

    now = now_local()
    since = now - dt.timedelta(days=args.days)

    sources = [
        ("codex_sessions", args.codex_sessions),
        ("codex_archived_sessions", args.codex_archived),
        ("codex_history", args.codex_history),
        ("otel_logs", args.otel_logs),
        ("otel_traces", args.otel_traces),
        ("claude_projects", args.claude_projects),
        ("claude_history", args.claude_history),
        ("kimi_sessions", args.kimi_sessions),
    ]

    dedupe: set[str] = set()
    issues: list[Issue] = []
    for name, path in sources:
        issues.extend(
            scan_source(
                name,
                path,
                since,
                dedupe,
                max_bytes_per_file=args.max_bytes_per_file,
                max_files_per_source=args.max_files_per_source,
            )
        )

    sys.stdout.write(render_report(issues, since, now))
    return 2 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
