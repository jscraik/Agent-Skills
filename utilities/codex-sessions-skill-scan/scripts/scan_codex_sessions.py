#!/usr/bin/env python3
"""
scan_codex_sessions.py

Scan Codex session JSONL logs under ~/.codex/sessions (default: last 1 day)
and summarize skill usage + likely friction points (missing files, bad paths,
tool failures) with a focus on PERSONAL skills in ~/dev/agent-skills.

Design goals:
- Stdlib-only (safe to run with system python3)
- Redaction-aware: never dump full chat transcripts; only short error snippets
- Deterministic output format suitable for daily runs

Exit codes:
  0  OK (no issues found)
  1  Script error (IO/parsing)
  2  Issues found (see report)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import socket
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Optional, Sequence

# Don't generate __pycache__/ *.pyc files inside the skills repo.
sys.dont_write_bytecode = True


_SKILL_INVOKE_RE = re.compile(r"Using skill:\s*`?([a-z0-9][a-z0-9-]{1,63})`?", re.I)
_ISSUE_RE = re.compile(
    r"("
    r"No such file or directory"
    r"|can't open file"
    r"|cannot open file"
    r"|ModuleNotFoundError"
    r"|\bTraceback\b"
    r"|\berror:\b"
    r"|apply_patch verification failed"
    r"|Invalid YAML"
    r"|Unexpected key\(s\) in SKILL\.md frontmatter"
    r"|ENOENT"
    r"|EACCES"
    r"|command not found"
    r")",
    re.I,
)

# Heuristic: sometimes a skill run executes a grep-like scan (e.g. ripgrep) over
# older sessions and prints JSONL match lines that include historical error
# strings. Those strings are not failures of the *current* skill run, so treat
# them as non-issues for this daily report.
_LOOKS_LIKE_SEARCH_RESULTS_RE = re.compile(
    r'(?s)\bOutput:\s*\nmatches:\s*\d+\b.*?\.jsonl:\d+:\{"timestamp"',
    re.I,
)

# Heuristic: ignore known shell/heredoc failures from ad-hoc analyzer commands.
# Example:
#   zsh:2: z0: parameter not set
#   IndexError: no such group
# These are tooling mistakes, not skill failures.
_LOOKS_LIKE_HEREDOC_ANALYZER_FAILURE_RE = re.compile(
    r"(?s)\bzsh:\d+:\s*z0:\s*parameter not set\b.*\bIndexError:\s*no such group\b",
    re.I,
)

# Very lightweight redaction: avoid printing anything that looks like a token.
_TOKENY_RE = re.compile(r"(?i)(api[_-]?key|token|secret|bearer)\s*[:=]\s*\S+")

_COMPLEXITY_HINT_STEPS = (
    "1. Restate the objective in one sentence.",
    "2. Break into 3–5 concrete deliverables.",
    "3. Define verification for each deliverable.",
    "4. Execute incrementally and stop after each milestone.",
)

_COMPLEXITY_TRIGGER_RULES = [
    (re.compile(r"\bimplement(?:ing|ation|ed)?\b", re.I), "implement"),
    (re.compile(r"\brefactor(?:ing|ed|s)?\b", re.I), "refactor"),
    (re.compile(r"\brewrite(?:ing|ed)?\b", re.I), "rewrite"),
    (re.compile(r"\bmigrate(?:ing|d)?\b", re.I), "migrate"),
    (re.compile(r"\bintegrat(?:e|ion)\b", re.I), "integrate"),
    (re.compile(r"\bdesign(?:ing)?\b", re.I), "design"),
    (re.compile(r"\brebuild(?:ing|ed|s)?\b", re.I), "rebuild"),
    (re.compile(r"\boptimi[sz]e(?:ing|d)?\b", re.I), "optimize"),
    (re.compile(r"\boverhaul(?:ing|ed)?\b", re.I), "overhaul"),
    (re.compile(r"\bmassive\b", re.I), "massive scope"),
]


@dataclass(frozen=True)
class SkillIssue:
    session_path: Path
    line_no: int
    skill: str
    kind: str
    snippet: str


@dataclass(frozen=True)
class RepoOtelSummary:
    repo_root: Path
    trace_dir: Path
    recent_trace_files: int
    last_trace_mtime: Optional[dt.datetime]


@dataclass(frozen=True)
class ComplexityHit:
    session_path: Path
    line_no: int
    term: str
    snippet: str


@dataclass(frozen=True)
class OTelCollectorSummary:
    updated_at: Optional[str]
    services: dict[str, int]
    top_metric_names: list[tuple[str, int]]
    top_span_names: list[tuple[str, int]]


def _now_local() -> dt.datetime:
    # Local timezone is fine for a daily scan UX.
    return dt.datetime.now().astimezone()


def _iter_recent_jsonl_files(roots: Sequence[Path], since: dt.datetime) -> Iterator[Path]:
    since_ts = since.timestamp()
    for root in roots:
        for dirpath, _, filenames in os.walk(root):
            for name in filenames:
                if not name.endswith(".jsonl"):
                    continue
                p = Path(dirpath) / name
                try:
                    if p.stat().st_mtime >= since_ts:
                        yield p
                except FileNotFoundError:
                    continue


def _discover_project_sessions(project_root: Path) -> list[Path]:
    """
    Find likely session roots like `<project>/.codex/sessions` for each project under
    the provided root. This catches per-repo sessions outside the default global
    ~/.codex/sessions location.
    """
    roots: list[Path] = []
    if not project_root.is_dir():
        return roots

    for p in project_root.rglob(".codex/sessions"):
        if p.is_dir():
            roots.append(p)
    return sorted(roots)


def _parse_otel_collector_stats(stats_json: Path) -> Optional[OTelCollectorSummary]:
    """
    Parse best-effort summary data from ~/.agents/otel-collector/data/processed/stats.json.
    """
    if not stats_json.exists():
        return None

    try:
        raw = json.loads(stats_json.read_text(encoding="utf-8", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return None

    if not isinstance(raw, dict):
        return None

    services = raw.get("services")
    metrics = raw.get("top_metric_names")
    spans = raw.get("top_span_names")
    if not isinstance(services, dict) or not isinstance(metrics, dict) or not isinstance(spans, dict):
        return None

    top_metrics = sorted(((k, int(v)) for k, v in metrics.items() if isinstance(k, str) and isinstance(v, (int, float))), reverse=True, key=lambda x: x[1])[:10]
    top_spans = sorted(((k, int(v)) for k, v in spans.items() if isinstance(k, str) and isinstance(v, (int, float))), reverse=True, key=lambda x: x[1])[:10]
    updated_at = raw.get("updated_at")
    return OTelCollectorSummary(
        updated_at=updated_at if isinstance(updated_at, str) else None,
        services={k: int(v) for k, v in services.items() if isinstance(k, str) and isinstance(v, (int, float))},
        top_metric_names=top_metrics,
        top_span_names=top_spans,
    )


def _is_port_open(host: str, port: int, timeout_s: float = 0.25) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout_s):
            return True
    except OSError:
        return False


def _parse_local_endpoint(endpoint: str) -> Optional[tuple[str, int]]:
    """
    Accepts URLs like:
      http://127.0.0.1:4318/v1/logs
    Returns (host, port) or None.
    """
    m = re.match(r"^https?://([^/:]+):(\d+)(/|$)", endpoint.strip())
    if not m:
        return None
    host = m.group(1)
    try:
        port = int(m.group(2))
    except ValueError:
        return None
    return host, port


def _read_codex_otel_config(config_toml: Path) -> dict[str, str]:
    """
    Best-effort parse of ~/.codex/config.toml [otel] endpoints.
    Stdlib-only: regex over TOML.
    """
    if not config_toml.exists():
        return {}
    try:
        raw = config_toml.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}

    # Narrow to [otel] section if present.
    sec = raw
    m = re.search(r"(?m)^\[otel\]\s*$", raw)
    if m:
        sec = raw[m.end() :]
        # Stop at next section header.
        nxt = re.search(r"(?m)^\[[^\]]+\]\s*$", sec)
        if nxt:
            sec = sec[: nxt.start()]

    out: dict[str, str] = {}
    for key in ("exporter", "trace_exporter"):
        # Matches: exporter = { otlp-http = { endpoint = "http://127.0.0.1:4318/v1/logs", ... } }
        em = re.search(rf'(?m)^{key}\s*=\s*.*?endpoint\s*=\s*"([^"]+)"', sec)
        if em:
            out[key] = em.group(1).strip()
    return out


def _repo_root_from_cwd(cwd: Path) -> Optional[Path]:
    p = cwd
    try:
        p = p.resolve()
    except OSError:
        return None

    for _ in range(25):
        if (p / ".git").exists():
            return p
        if p.parent == p:
            break
        p = p.parent
    return None


def _summarize_repo_otel(repo_root: Path, since: dt.datetime) -> Optional[RepoOtelSummary]:
    """
    Treat OTLP-derived artifacts as:
      <repo>/.narrative/trace/*.agent-trace.json
    (This is where Narrative's OTLP receiver writes local trace records.)
    """
    trace_dir = repo_root / ".narrative" / "trace"
    if not trace_dir.is_dir():
        return None

    since_ts = since.timestamp()
    recent = 0
    last_mtime: Optional[float] = None
    try:
        for name in os.listdir(trace_dir):
            if not name.endswith(".agent-trace.json"):
                continue
            p = trace_dir / name
            try:
                st = p.stat()
            except FileNotFoundError:
                continue
            if st.st_mtime >= since_ts:
                recent += 1
            if last_mtime is None or st.st_mtime > last_mtime:
                last_mtime = st.st_mtime
    except OSError:
        return None

    last_dt = dt.datetime.fromtimestamp(last_mtime, tz=dt.timezone.utc).astimezone() if last_mtime else None
    return RepoOtelSummary(
        repo_root=repo_root,
        trace_dir=trace_dir,
        recent_trace_files=recent,
        last_trace_mtime=last_dt,
    )


def _extract_text_from_event(obj: dict) -> Optional[tuple[str, str, Optional[str]]]:
    typ = obj.get("type")
    payload = obj.get("payload")
    if not isinstance(payload, dict):
        return None

    if typ == "event_msg":
        msg = payload.get("message")
        return (msg, "event_msg", None) if isinstance(msg, str) and msg.strip() else None

    if typ == "response_item" and payload.get("type") == "message":
        role = payload.get("role")
        if isinstance(role, str):
            role = role.strip().lower()
        content = payload.get("content")
        if isinstance(content, list):
            parts: list[str] = []
            for seg in content:
                if isinstance(seg, dict) and isinstance(seg.get("text"), str):
                    parts.append(seg["text"])
            joined = "\n".join([p for p in parts if p.strip()]).strip()
            return (joined, "message", role) if joined else None
        if isinstance(content, str) and content.strip():
            return (content, "message", role)
        return None

    if typ == "response_item" and payload.get("type") == "function_call_output":
        out = payload.get("output")
        return (out, "tool_output", None) if isinstance(out, str) and out.strip() else None

    return None


def _safe_snippet(text: str, limit: int) -> str:
    s = text.strip().replace("\r", "")
    s = _TOKENY_RE.sub("[REDACTED]", s)
    s = s.replace("\n", "\\n")
    if len(s) <= limit:
        return s
    return s[: limit - 3] + "..."


def _skill_index_personal(agent_skills_root: Path) -> dict[str, Path]:
    """
    Map {skill_name -> SKILL.md path} for personal skills only.

    Excludes generated/system dirs:
    - skills/
    - skills-system/
    - .agents/
    - .git/
    """
    excluded = {"skills", "skills-system", ".agents", ".git", "node_modules"}
    index: dict[str, Path] = {}

    for p in agent_skills_root.rglob("SKILL.md"):
        rel = p.relative_to(agent_skills_root)
        if rel.parts and rel.parts[0] in excluded:
            continue

        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue

        if not text.startswith("---"):
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            continue
        fm = parts[1]
        m = re.search(r"^name:\s*([^\n]+)\s*$", fm, flags=re.M)
        if not m:
            continue
        name = m.group(1).strip().strip('"').strip("'")
        if not name:
            continue
        index[name] = p

    return index


def scan(
    sessions_roots: Sequence[Path],
    since: dt.datetime,
    max_samples_per_skill: int,
    agent_skills_root: Path,
    include_otel: bool,
    codex_config_toml: Path,
    include_otel_collector: bool = False,
    otel_collector_stats: Path | None = None,
) -> tuple[
    list[SkillIssue],
    list[ComplexityHit],
    Counter[str],
    Counter[str],
    Counter[str],
    dict[str, Path],
]:
    """
    Returns:
      - issues list
      - complexity hits
      - complexity hit count by term
      - skills invoked counter
      - issue counter by skill
      - skill index (personal)
    """
    skill_index = _skill_index_personal(agent_skills_root)

    invoked: Counter[str] = Counter()
    issues_by_skill: Counter[str] = Counter()
    complexity_terms: Counter[str] = Counter()
    issues: list[SkillIssue] = []
    complexity_hits: list[ComplexityHit] = []
    captured_by_skill: Counter[str] = Counter()
    captured_by_term: Counter[str] = Counter()

    # Optional: correlate recent sessions -> repo roots -> local OTLP-derived trace artifacts.
    session_cwds: set[Path] = set()

    for fpath in sorted(_iter_recent_jsonl_files(sessions_roots, since)):
        current_skill: Optional[str] = None

        try:
            with fpath.open("r", encoding="utf-8", errors="replace") as f:
                for i, line in enumerate(f, start=1):
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue
                    if not isinstance(obj, dict):
                        continue

                    if include_otel and obj.get("type") == "session_meta":
                        payload = obj.get("payload")
                        if isinstance(payload, dict):
                            cwd = payload.get("cwd")
                            if isinstance(cwd, str) and cwd.strip():
                                session_cwds.add(Path(cwd.strip()))

                    extracted = _extract_text_from_event(obj)
                    if not extracted:
                        continue
                    text, source_kind, role = extracted

                    # Prefer using the explicit "Using skill:" marker.
                    m = _SKILL_INVOKE_RE.search(text)
                    if m:
                        # Ignore nested/historical "Using skill:" strings printed by tool outputs.
                        if source_kind == "tool_output":
                            continue
                        current_skill = m.group(1).lower()
                        invoked[current_skill] += 1
                        continue

                    if source_kind == "message" and role == "user":
                        hit_terms: set[str] = set()
                        for pattern, term in _COMPLEXITY_TRIGGER_RULES:
                            if pattern.search(text):
                                hit_terms.add(term)
                        for term in hit_terms:
                            complexity_terms[term] += 1
                            if captured_by_term[term] < 3:
                                captured_by_term[term] += 1
                                complexity_hits.append(
                                    ComplexityHit(
                                        session_path=fpath,
                                        line_no=i,
                                        term=term,
                                        snippet=_safe_snippet(text, limit=240),
                                    )
                                )

                    if not current_skill:
                        continue

                    if not _ISSUE_RE.search(text):
                        continue

                    # Avoid false positives when the current skill is running a
                    # grep-like scan and printing historical matches.
                    if _LOOKS_LIKE_SEARCH_RESULTS_RE.search(text):
                        continue
                    if _LOOKS_LIKE_HEREDOC_ANALYZER_FAILURE_RE.search(text):
                        continue
                    if source_kind == "tool_output" and re.search(r"\.jsonl:\d+:\{", text):
                        continue

                    # Count every issue event (even if we cap saved samples).
                    issues_by_skill[current_skill] += 1

                    # Cap saved samples per skill.
                    if captured_by_skill[current_skill] >= max_samples_per_skill:
                        continue
                    captured_by_skill[current_skill] += 1

                    issues.append(
                        SkillIssue(
                            session_path=fpath,
                            line_no=i,
                            skill=current_skill,
                            kind="issue",
                            snippet=_safe_snippet(text, limit=240),
                        )
                    )
        except OSError:
            continue

    # Attach OTEL-derived state via function attributes to avoid widening return type too much.
    scan._session_cwds = session_cwds  # type: ignore[attr-defined]
    scan._otel_config = _read_codex_otel_config(codex_config_toml) if include_otel else {}  # type: ignore[attr-defined]
    scan._otel_collector = _parse_otel_collector_stats(otel_collector_stats) if include_otel_collector and otel_collector_stats else None  # type: ignore[attr-defined]

    return issues, complexity_hits, complexity_terms, invoked, issues_by_skill, skill_index


def _md_list(items: Iterable[str], indent: str = "") -> str:
    return "\n".join([f"{indent}- {x}" for x in items])


def render_report(
    *,
    issues: list[SkillIssue],
    complexity_hits: list[ComplexityHit],
    complexity_terms: Counter[str],
    invoked: Counter[str],
    issues_by_skill: Counter[str],
    skill_index: dict[str, Path],
    sessions_roots: Sequence[Path],
    since: dt.datetime,
    now: dt.datetime,
    max_show_skills: int,
    include_otel: bool,
    session_cwds: Sequence[Path],
    otel_config: dict[str, str],
    otel_collector: Optional[OTelCollectorSummary],
) -> str:
    total_inv = sum(invoked.values())
    total_issue_events = sum(issues_by_skill.values())
    total_issue_samples = len(issues)

    lines: list[str] = []
    lines.append("## Inputs")
    lines.append(f"- sessions_roots: `{', '.join(str(p) for p in sessions_roots)}`")
    lines.append(f"- since: `{since.isoformat()}`")
    lines.append(f"- now: `{now.isoformat()}`")
    lines.append("")
    lines.append("## Outputs")
    lines.append("- Daily skill health report (this message).")
    lines.append("- Suggested fixes (no changes applied).")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- skills_invocations: **{total_inv}**")
    lines.append(f"- skills_with_issues: **{len(issues_by_skill)}**")
    lines.append(f"- issue_events_detected: **{total_issue_events}**")
    lines.append(f"- issue_samples_captured: **{total_issue_samples}**")
    lines.append(f"- complexity_triggers_seen: **{sum(complexity_terms.values())}**")
    lines.append("")

    if complexity_terms:
        lines.append("## Complexity-word reminder triggers")
        for term, count in complexity_terms.most_common(max_show_skills):
            lines.append(f"- `{term}`: **{count}x**")
        lines.append("")
        lines.append("### Suggested step-by-step reminder")
        lines.append("- Break the request into: scope, design, implementation, validation.")
        for s in _COMPLEXITY_HINT_STEPS:
            lines.append(f"- {s}")
        lines.append("")
        lines.append("### Occurrences (actionable reminders)")
        for hit in complexity_hits[: max_show_skills]:
            lines.append(
                f"- `{hit.session_path.name}:{hit.line_no}` matched `{hit.term}` — Reminder: treat as a multi-step task."
            )
            lines.append(f"  - sample: `{hit.snippet}`")
        lines.append("")

    if include_otel:
        lines.append("## Local OTel signals (best-effort)")
        if otel_config:
            for k, endpoint in otel_config.items():
                hp = _parse_local_endpoint(endpoint)
                if hp:
                    host, port = hp
                    listening = _is_port_open(host, port)
                    lines.append(
                        f"- codex_config.{k}: `{endpoint}` (listening: **{'yes' if listening else 'no'}**)"
                    )
                else:
                    lines.append(f"- codex_config.{k}: `{endpoint}` (listening: unknown)")
        else:
            lines.append("- codex_config: no [otel] endpoints found (or config unreadable).")

        # Repo-local OTLP-derived artifacts (Narrative receiver): .narrative/trace/*.agent-trace.json
        repo_roots: set[Path] = set()
        for cwd in session_cwds:
            rr = _repo_root_from_cwd(cwd)
            if rr:
                repo_roots.add(rr)

        summaries: list[RepoOtelSummary] = []
        for rr in sorted(repo_roots):
            s = _summarize_repo_otel(rr, since)
            if s:
                summaries.append(s)

        if summaries:
            lines.append("- Repo OTLP-derived traces (Narrative):")
            for s in summaries[: max_show_skills]:
                last = s.last_trace_mtime.isoformat() if s.last_trace_mtime else "unknown"
                lines.append(
                    f"  - `{s.repo_root}`: recent_trace_files={s.recent_trace_files}, last_trace={last}"
                )
        else:
            lines.append("- Repo OTLP-derived traces: none found for repos referenced in the scanned sessions window.")

        if otel_collector:
            lines.append("- ~/.agents/otel-collector summary:")
            if otel_collector.updated_at:
                lines.append(f"  - updated_at: `{otel_collector.updated_at}`")
            lines.append(f"  - services: `{', '.join(f'{k}:{v}' for k, v in list(otel_collector.services.items())[:10])}`")
            if otel_collector.top_span_names:
                lines.append(
                    f"  - top_spans: `{', '.join(f'{k}:{v}' for k, v in otel_collector.top_span_names[:6])}`"
                )
            if otel_collector.top_metric_names:
                lines.append(
                    f"  - top_metrics: `{', '.join(f'{k}:{v}' for k, v in otel_collector.top_metric_names[:6])}`"
                )
        lines.append("")

    if invoked:
        lines.append("## Skills invoked (top)")
        for skill, count in invoked.most_common(max_show_skills):
            hint = ""
            if skill in skill_index:
                hint = f" (personal: `{skill_index[skill]}`)"
            lines.append(f"- `{skill}`: {count}{hint}")
        lines.append("")

    if not issues_by_skill:
        lines.append("## Issues")
        lines.append("None detected in the scanned window.")
        return "\n".join(lines).strip() + "\n"

    lines.append("## Issues (by skill)")
    for skill, count in issues_by_skill.most_common(max_show_skills):
        lines.append(f"### `{skill}` ({count} issue event(s))")
        if skill in skill_index:
            lines.append(f"- Personal skill path: `{skill_index[skill]}`")
        else:
            lines.append("- Personal skill path: (not found in ~/dev/agent-skills; may be system or external)")
        for it in [x for x in issues if x.skill == skill][:3]:
            lines.append(f"- Sample ({it.session_path.name}:{it.line_no}): `{it.snippet}`")
        lines.append("")

    lines.append("## Suggested fix patterns (manual)")
    lines.append(
        _md_list(
            [
                "If you see paths like `design/product-spec/...`: replace with `product/specs/product-spec/...`.",
                "If validation scripts fail with `ModuleNotFoundError: yaml`: run them with `~/.venvs/pyyaml/bin/python`.",
                "If errors show `python: command not found`: prefer explicit interpreters (`python3` for stdlib scripts; `~/.venvs/pyyaml/bin/python` for skill gates).",
                "If `~` is not expanding in a tool config: replace with an absolute path (e.g. `/home/<user>/...`).",
            ]
        )
    )
    lines.append("")

    lines.append("## Next step")
    lines.append(
        "If you want fixes applied, run this scan, then ask me to patch the referenced personal skill files "
        "and re-run `quick_validate.py` + `skill_gate.py`."
    )

    return "\n".join(lines).strip() + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sessions-root",
        type=Path,
        default=Path.home() / ".codex" / "sessions",
        help="Root directory of Codex sessions (default: ~/.codex/sessions).",
    )
    parser.add_argument(
        "--include-dev-project-sessions",
        action="store_true",
        default=True,
        help=(
            "Also scan per-project .codex/sessions directories discovered under --projects-root. "
            "Use this to include sessions for any repo under ~/dev."
        ),
    )
    parser.add_argument(
        "--no-include-dev-project-sessions",
        action="store_false",
        dest="include_dev_project_sessions",
        help="Skip per-project .codex/sessions discovery under --projects-root.",
    )
    parser.add_argument(
        "--projects-root",
        type=Path,
        default=Path.home() / "dev",
        help="Project root to discover per-project session dirs (default: ~/dev).",
    )
    parser.add_argument(
        "--days",
        type=float,
        default=1.0,
        help="Scan window in days back from now (default: 1).",
    )
    parser.add_argument(
        "--max-samples-per-skill",
        type=int,
        default=3,
        help="Max issue samples to capture per skill (default: 3).",
    )
    parser.add_argument(
        "--max-show-skills",
        type=int,
        default=20,
        help="Max skills to show in report sections (default: 20).",
    )
    parser.add_argument(
        "--agent-skills-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Root of personal agent-skills repo (default: inferred from this script).",
    )
    parser.add_argument(
        "--include-otel",
        action="store_true",
        help="Include best-effort OTel signals: Codex [otel] endpoint status and repo-local OTLP-derived trace artifacts.",
    )
    parser.add_argument(
        "--include-otel-collector",
        action="store_true",
        help="Include best-effort summary from ~/.agents/otel-collector/data/processed/stats.json.",
    )
    parser.add_argument(
        "--otel-collector-stats",
        type=Path,
        default=Path.home() / ".agents" / "otel-collector" / "data" / "processed" / "stats.json",
        help="Path to OTel collector stats.json (default: ~/.agents/otel-collector/data/processed/stats.json).",
    )
    parser.add_argument(
        "--codex-config-toml",
        type=Path,
        default=Path.home() / ".codex" / "config.toml",
        help="Path to Codex config.toml (default: ~/.codex/config.toml).",
    )
    args = parser.parse_args(argv)

    now = _now_local()
    since = now - dt.timedelta(days=args.days)

    try:
        session_roots = [args.sessions_root]
        if args.include_dev_project_sessions:
            session_roots.extend(_discover_project_sessions(args.projects_root))
        session_roots = sorted({str(p.resolve()): p for p in session_roots}.values())  # dedupe

        issues, complexity_hits, complexity_terms, invoked, issues_by_skill, skill_index = scan(
            sessions_roots=session_roots,
            since=since,
            max_samples_per_skill=args.max_samples_per_skill,
            agent_skills_root=args.agent_skills_root,
            include_otel=args.include_otel,
            codex_config_toml=args.codex_config_toml,
            include_otel_collector=args.include_otel_collector,
            otel_collector_stats=args.otel_collector_stats,
        )
    except Exception as e:  # fail fast for daily tool UX
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    session_cwds = sorted(getattr(scan, "_session_cwds", []))
    otel_config = getattr(scan, "_otel_config", {})
    otel_collector = getattr(scan, "_otel_collector", None)

    report = render_report(
        issues=issues,
        complexity_hits=complexity_hits,
        complexity_terms=complexity_terms,
        invoked=invoked,
        issues_by_skill=issues_by_skill,
        skill_index=skill_index,
        sessions_roots=session_roots,
        since=since,
        now=now,
        max_show_skills=args.max_show_skills,
        include_otel=args.include_otel,
        session_cwds=session_cwds,
        otel_config=otel_config,
        otel_collector=otel_collector,
    )
    sys.stdout.write(report)

    return 2 if issues_by_skill else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
