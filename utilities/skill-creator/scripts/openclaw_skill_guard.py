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
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List


@dataclass
class Finding:
    level: str  # critical|warn|info
    code: str
    message: str
    file: str | None = None
    line: int | None = None


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


# NOTE: This guard is intentionally heuristic. The goal is:
# - keep "critical" for patterns with high likelihood of turning into security issues
# - keep "warn" for patterns that are often safe but deserve review and constraints
#
# This repo contains many script-backed skills that shell out to trusted CLIs
# (for example: `gh`, `git`, `yt-dlp`). That should not fail the entire guard by
# default. We flag that as WARN, and reserve CRITICAL for shell injection vectors
# (Python subprocess shell mode / Node exec*) and dynamic code execution (eval/exec).
PATTERNS = [
    # High-risk command execution patterns.
    ("critical", "security.shell_true", re.compile(r"\bshell\s*=\s*True\b")),
    ("critical", "security.os_system", re.compile(r"\bos\.system\(")),
    ("critical", "security.node_exec", re.compile(r"\bexecSync\(")),
    ("critical", "security.node_exec", re.compile(r"\bchild_process\.(exec|execSync)\b")),

    # Dynamic code execution.
    ("critical", "security.eval_usage", re.compile(r"\beval\(")),
    ("critical", "security.exec_usage", re.compile(r"(?<![A-Za-z0-9_])exec\(")),

    # Often-safe patterns that still deserve review.
    ("warn", "security.subprocess_usage", re.compile(r"\bsubprocess\.(run|Popen|call|check_call|check_output)\(")),
    ("warn", "security.node_child_process", re.compile(r"\bnode:child_process\b|\bchild_process\.(?:spawn|spawnSync|exec|execSync)\b|\bspawnSync\(|\bspawn\(")),
    (
        "warn",
        "security.network_usage",
        re.compile(
            r"\b(?:"
            r"requests\.(?:get|post|put|patch|delete|request)\(|"
            r"httpx\.(?:get|post|put|patch|delete|request|Client)\(|"
            r"axios\.(?:get|post|put|patch|delete|request)\(|"
            r"fetch\(\s*[\"'`](?:https?:)?//|"
            r"curl\s+-[A-Za-z]"
            r")"
        ),
    ),

    # Exfil risk: env reading + network usage near each other.
    ("critical", "security.env_harvesting", re.compile(r"(os\.environ|getenv\(|process\.env).{0,160}(requests\.|fetch\(|axios\.|httpx\.|curl)")),
]


def _line_text(text: str, idx: int) -> str:
    start = text.rfind("\n", 0, idx) + 1
    end = text.find("\n", idx)
    if end == -1:
        end = len(text)
    return text[start:end]


def _should_skip_match(code: str, line_text: str) -> bool:
    stripped = line_text.strip()
    if not stripped:
        return True
    if stripped.startswith("#"):
        return True
    # Avoid self-referential false positives from regex definition tables.
    if "re.compile(" in line_text:
        return True
    if code in {"security.network_usage", "security.node_child_process"} and "pattern" in stripped.lower():
        return True
    return False


def iter_code_files(skill_dir: Path) -> Iterable[Path]:
    for rel in ("scripts",):
        d = skill_dir / rel
        if not d.exists():
            continue
        for f in d.rglob("*"):
            if f.suffix.lower() in {".py", ".js", ".ts", ".sh"} and f.is_file():
                yield f


def security_checks(skill_dir: Path) -> List[Finding]:
    out: List[Finding] = []
    files = list(iter_code_files(skill_dir))
    if not files:
        out.append(Finding("info", "security.no_scripts", "No executable scripts found; static security scan skipped"))
        return out

    for f in files:
        txt = f.read_text(encoding="utf-8", errors="ignore")
        for level, code, rx in PATTERNS:
            for m in rx.finditer(txt):
                line_text = _line_text(txt, m.start())
                if _should_skip_match(code, line_text):
                    continue
                out.append(
                    Finding(
                        level,
                        code,
                        f"Matched pattern: {rx.pattern}",
                        str(f.relative_to(skill_dir)),
                        _line_no(txt, m.start()),
                    )
                )

    if not out:
        out.append(Finding("info", "security.clean", "No risky patterns detected in scanned scripts"))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="OpenClaw-style skill readiness + security scanner")
    ap.add_argument("skill_dir")
    ap.add_argument("--mode", choices=["readiness", "security", "both"], default="both")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    args = ap.parse_args()

    skill_dir = Path(args.skill_dir).expanduser().resolve()
    findings: List[Finding] = []

    if args.mode in {"readiness", "both"}:
        findings.extend(readiness_checks(skill_dir))
    if args.mode in {"security", "both"}:
        findings.extend(security_checks(skill_dir))

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
            print(f"{f.level.upper()} {f.code}: {f.message}{loc}")

    return 2 if critical else 0


if __name__ == "__main__":
    raise SystemExit(main())
