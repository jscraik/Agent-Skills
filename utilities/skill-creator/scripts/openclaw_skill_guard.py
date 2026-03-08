#!/usr/bin/env python3
"""OpenClaw-style skill operational-readiness + security-risk guard.

Usage:
  python scripts/openclaw_skill_guard.py <skill-dir> [--mode readiness|security|both] [--format text|json]

Exit codes:
  0 pass (no critical findings)
  2 fail (critical readiness/security findings)
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Pattern


@dataclass
class Finding:
    level: str  # critical|warn|info
    code: str
    message: str
    file: str | None = None
    line: int | None = None
    remediation: str | None = None


@dataclass(frozen=True)
class Rule:
    level: str
    code: str
    message: str
    pattern: Pattern[str]
    requires_context: Pattern[str] | None = None
    remediation: str | None = None


@dataclass(frozen=True)
class SourceRule:
    level: str
    code: str
    message: str
    pattern: Pattern[str]
    requires_context: Pattern[str] | None = None
    remediation: str | None = None


SCANNABLE_EXTENSIONS = {".py", ".js", ".ts", ".sh"}
DEFAULT_MAX_SCAN_FILES = 500
DEFAULT_MAX_FILE_BYTES = 1024 * 1024


def has_nested_repetition(source: str) -> bool:
    """Conservative regex guard against nested repetition bombs."""
    frames = [{"last_repeated": False, "contains_repetition": False}]
    in_char_class = False
    i = 0
    while i < len(source):
        ch = source[i]
        if ch == "\\":
            i += 2
            frames[-1]["last_repeated"] = False
            continue
        if in_char_class:
            if ch == "]":
                in_char_class = False
            i += 1
            continue
        if ch == "[":
            in_char_class = True
            frames[-1]["last_repeated"] = False
            i += 1
            continue
        if ch == "(":
            frames.append({"last_repeated": False, "contains_repetition": False})
            i += 1
            continue
        if ch == ")":
            if len(frames) > 1:
                frame = frames.pop()
                frames[-1]["last_repeated"] = bool(frame["contains_repetition"])
                if frame["contains_repetition"]:
                    frames[-1]["contains_repetition"] = True
            i += 1
            continue
        quant = None
        if ch in {"*", "+", "?"}:
            quant = 1
        elif ch == "{":
            j = i + 1
            while j < len(source) and source[j].isdigit():
                j += 1
            if j > i + 1 and j < len(source) and source[j] in {",", "}"}:
                if source[j] == ",":
                    j += 1
                    while j < len(source) and source[j].isdigit():
                        j += 1
                if j < len(source) and source[j] == "}":
                    quant = (j - i) + 1
        if quant:
            if frames[-1]["last_repeated"]:
                return True
            frames[-1]["last_repeated"] = True
            frames[-1]["contains_repetition"] = True
            i += quant
            continue
        frames[-1]["last_repeated"] = False
        i += 1
    return False


def compile_safe_regex(source: str, flags: int = 0, *, allow_nested: bool = False) -> Pattern[str]:
    if not allow_nested and has_nested_repetition(source):
        raise ValueError(f"Unsafe regex (nested repetition): {source}")
    return re.compile(source, flags)


def _line_no(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


def readiness_checks(skill_dir: Path) -> List[Finding]:
    out: List[Finding] = []
    skill_md = skill_dir / "SKILL.md"
    refs = skill_dir / "references"

    if not skill_md.exists():
        out.append(Finding("critical", "readiness.skill_md_missing", "Missing SKILL.md"))
        return out

    text = skill_md.read_text(encoding="utf-8", errors="ignore")
    if "name:" not in text or "description:" not in text:
        out.append(Finding("critical", "readiness.frontmatter_invalid", "SKILL.md frontmatter missing name/description", "SKILL.md"))

    if not refs.exists():
        out.append(Finding("warn", "readiness.references_missing", "Missing references/ directory"))
    else:
        if not (refs / "contract.yaml").exists():
            out.append(Finding("warn", "readiness.contract_missing", "Missing references/contract.yaml"))
        if not (refs / "evals.yaml").exists():
            out.append(Finding("warn", "readiness.evals_missing", "Missing references/evals.yaml"))

    scripts = skill_dir / "scripts"
    if scripts.exists():
        py_or_js = list(scripts.rglob("*.py")) + list(scripts.rglob("*.js")) + list(scripts.rglob("*.ts"))
        if not py_or_js:
            out.append(Finding("info", "readiness.scripts_empty", "scripts/ exists but has no .py/.js/.ts files"))

    out.append(Finding("info", "readiness.checked", "Operational readiness checks completed"))
    return out


LINE_RULES: List[Rule] = [
    Rule(
        "critical",
        "security.shell_true",
        "Shell mode execution detected (`shell=True`).",
        compile_safe_regex(r"\bshell\s*=\s*True\b"),
        remediation="Use argument lists with `shell=False` and explicit command allowlists.",
    ),
    Rule(
        "critical",
        "security.os_system",
        "os.system execution detected.",
        compile_safe_regex(r"\bos\.system\("),
        remediation="Replace os.system with subprocess argument lists and input validation.",
    ),
    Rule(
        "critical",
        "security.node_exec",
        "Node exec/execSync execution detected.",
        compile_safe_regex(r"\b(child_process\.(exec|execSync)|execSync)\b"),
        remediation="Prefer spawn/spawnSync with fixed argv and strict input validation.",
    ),
    Rule(
        "critical",
        "security.dynamic_code_execution",
        "Dynamic code execution detected (`eval`/`exec`/`new Function`).",
        compile_safe_regex(r"\b(eval\(|(?<![A-Za-z0-9_])exec\(|new\s+Function\s*\()"),
        remediation="Remove dynamic execution and replace with static dispatch logic.",
    ),
    Rule(
        "warn",
        "security.subprocess_usage",
        "subprocess command execution detected; review for input hardening.",
        compile_safe_regex(r"\bsubprocess\.(run|Popen|call|check_call|check_output)\("),
        requires_context=compile_safe_regex(r"\bsubprocess\b"),
        remediation="Ensure argv lists, `shell=False`, and strict input sanitization are used.",
    ),
    Rule(
        "warn",
        "security.node_child_process",
        "Node child_process usage detected; review for command injection risk.",
        compile_safe_regex(r"\b(node:child_process|child_process\.(?:spawn|spawnSync|exec|execSync)|spawnSync\(|spawn\()"),
        remediation="Ensure command/argv are fixed or validated and avoid shell wrappers.",
    ),
]

SOURCE_RULES: List[SourceRule] = [
    SourceRule(
        "warn",
        "security.network_usage",
        "Network calls detected in scripts.",
        compile_safe_regex(
            r"\b(?:requests\.(?:get|post|put|patch|delete|request)\(|httpx\.(?:get|post|put|patch|delete|request|Client)\(|axios\.(?:get|post|put|patch|delete|request)\(|fetch\(\s*[\"'`](?:https?:)?//|curl\s+-[A-Za-z])",
            allow_nested=True,
        ),
        remediation="Document and enforce explicit network allowlists and offline defaults.",
    ),
    SourceRule(
        "critical",
        "security.env_harvesting",
        "Environment access combined with network send detected.",
        compile_safe_regex(r"(os\.environ|getenv\(|process\.env).{0,200}(requests\.|fetch\(|axios\.|httpx\.|curl)", re.DOTALL),
        remediation="Avoid sending env-derived data over network; explicitly redact and isolate secrets.",
    ),
]


def _line_text(text: str, idx: int) -> str:
    start = text.rfind("\n", 0, idx) + 1
    end = text.find("\n", idx)
    if end == -1:
        end = len(text)
    return text[start:end]


def _should_skip_match(_code: str, line_text: str) -> bool:
    stripped = line_text.strip()
    if not stripped:
        return True
    if stripped.startswith("#"):
        return True
    return False


def _is_path_inside(base: Path, candidate: Path) -> bool:
    base_resolved = base.resolve()
    candidate_resolved = candidate.resolve()
    rel = os.path.relpath(candidate_resolved, base_resolved)
    return rel == "." or (not rel.startswith("..") and not os.path.isabs(rel))


def iter_code_files(skill_dir: Path, *, max_files: int, max_file_bytes: int) -> Iterable[Path]:
    count = 0
    for rel in ("scripts",):
        d = (skill_dir / rel).resolve()
        if not d.exists():
            continue
        for f in d.rglob("*"):
            if count >= max_files:
                return
            if not f.is_file():
                continue
            if f.suffix.lower() not in SCANNABLE_EXTENSIONS:
                continue
            if f.name == "openclaw_skill_guard.py":
                continue
            if f.name.startswith("test_") or f.name.endswith("_test.py") or f.name.endswith(".test.py"):
                continue
            if "/node_modules/" in f.as_posix() or "/." in f.as_posix().replace("/..", "/"):
                continue
            if not _is_path_inside(d, f):
                continue
            try:
                if f.stat().st_size > max_file_bytes:
                    continue
            except OSError:
                continue
            yield f
            count += 1


def scan_source(text: str, rel_file: str) -> List[Finding]:
    out: List[Finding] = []

    for rule in LINE_RULES:
        if rule.requires_context and not rule.requires_context.search(text):
            continue
        for m in rule.pattern.finditer(text):
            line_text = _line_text(text, m.start())
            if _should_skip_match(rule.code, line_text):
                continue
            if rule.code == "security.subprocess_usage":
                window = text[max(0, m.start() - 120) : min(len(text), m.end() + 240)]
                if re.search(r"\bshell\s*=\s*False\b", window):
                    continue
                if re.search(r"\bsubprocess\.(run|Popen|call|check_call|check_output)\s*\(\s*\[", window):
                    continue
            out.append(
                Finding(
                    rule.level,
                    rule.code,
                    rule.message,
                    rel_file,
                    _line_no(text, m.start()),
                    remediation=rule.remediation,
                )
            )
            break

    for rule in SOURCE_RULES:
        if rule.requires_context and not rule.requires_context.search(text):
            continue
        m = rule.pattern.search(text)
        if not m:
            continue
        out.append(
            Finding(
                rule.level,
                rule.code,
                rule.message,
                rel_file,
                _line_no(text, m.start()),
                remediation=rule.remediation,
            )
        )

    return out


def security_checks(skill_dir: Path, *, max_files: int, max_file_bytes: int) -> List[Finding]:
    out: List[Finding] = []
    skill_root = skill_dir.resolve()
    files = list(iter_code_files(skill_root, max_files=max_files, max_file_bytes=max_file_bytes))
    if not files:
        out.append(Finding("info", "security.no_scripts", "No executable scripts found; static security scan skipped"))
        return out

    for f in files:
        txt = f.read_text(encoding="utf-8", errors="ignore")
        try:
            rel_file = str(f.resolve().relative_to(skill_root))
        except ValueError:
            rel_file = str(f.name)
        out.extend(scan_source(txt, rel_file))

    if not out:
        out.append(Finding("info", "security.clean", "No risky patterns detected in scanned scripts"))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="OpenClaw-style skill readiness + security scanner")
    ap.add_argument("skill_dir")
    ap.add_argument("--mode", choices=["readiness", "security", "both"], default="both")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--max-files", type=int, default=DEFAULT_MAX_SCAN_FILES)
    ap.add_argument("--max-file-bytes", type=int, default=DEFAULT_MAX_FILE_BYTES)
    args = ap.parse_args()

    skill_dir = Path(args.skill_dir).expanduser().resolve()
    findings: List[Finding] = []

    if args.mode in {"readiness", "both"}:
        findings.extend(readiness_checks(skill_dir))
    if args.mode in {"security", "both"}:
        findings.extend(
            security_checks(
                skill_dir,
                max_files=max(1, args.max_files),
                max_file_bytes=max(1, args.max_file_bytes),
            )
        )

    critical = [f for f in findings if f.level == "critical"]
    warn = [f for f in findings if f.level == "warn"]
    info = [f for f in findings if f.level == "info"]

    payload = {
        "skill": skill_dir.name,
        "summary": {"critical": len(critical), "warn": len(warn), "info": len(info)},
        "findings": [asdict(f) for f in findings],
    }

    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(f"OpenClaw skill guard: {skill_dir.name}")
        print(f"Summary: {len(critical)} critical · {len(warn)} warn · {len(info)} info")
        for f in findings:
            loc = f" ({f.file}:{f.line})" if f.file else ""
            remediation = f" | Remediation: {f.remediation}" if f.remediation else ""
            print(f"{f.level.upper()} {f.code}: {f.message}{loc}{remediation}")

    return 2 if critical else 0


if __name__ == "__main__":
    raise SystemExit(main())
