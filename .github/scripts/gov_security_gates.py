#!/usr/bin/env python3
"""Governance/security gate checks for PRs and critical-path file changes.

The gate validates:
- Required governance evidence sections in PR body for policy/security-relevant changes
- Optional vulnerability checks (if supported tools are installed)
- Optional secret scanning (if supported tools are installed)
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EVENT_PATH = os.environ.get("GITHUB_EVENT_PATH", str(REPO_ROOT / "event.json"))
REQUIRED_SECTIONS = {
    "threat model": [r"threat model", r"threat-model"],
    "security impact": [r"security\s*/?\s*privacy", r"security impact"],
    "ai and data impact": [r"ai", r"data impact", r"ai/data"],
    "verification evidence": [r"verification evidence", r"how to test"],
    "release notes": [r"release notes", r"release note"],
}
PLACEHOLDER = re.compile(r"\[PROMPT:|TODO:|TBD|replace this|add\s+details", re.I)


def run(cmd, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def split_sections(body: str):
    sections = {}
    heading = "_intro"
    sections[heading] = []

    for line in body.splitlines():
        m = re.match(r"^##\s*(.+)$", line)
        if m:
            heading = normalize(m.group(1))
            sections.setdefault(heading, [])
            continue
        sections.setdefault(heading, []).append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items()}


def section_has_content(text: str) -> bool:
    if not text:
        return False
    if PLACEHOLDER.search(text):
        return False
    compact = normalize(text)
    if compact in {"n/a", "na", "none", "not applicable", "no security impact", "no ai impact"}:
        return False
    return bool(compact)


def section_present(sections, keys):
    for key, aliases in keys.items():
        text = None
        for heading, value in sections.items():
            if any(re.search(alias, heading, re.I) for alias in aliases):
                text = value
                break
        if text is None:
            return False, key
        if key != "release notes" and not section_has_content(text):
            return False, key
        # release notes can be explicit "none", but should still be intentional and non-placeholder
        if key == "release notes" and (not text or PLACEHOLDER.search(text)):
            return False, key
    return True, ""


def get_pr_context():
    if not Path(EVENT_PATH).exists():
        return None
    try:
        payload = json.loads(Path(EVENT_PATH).read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None

    pr = payload.get("pull_request")
    if not pr:
        return None

    return {
        "body": pr.get("body") or "",
        "base": pr.get("base", {}).get("sha"),
        "head": pr.get("head", {}).get("sha"),
    }


def get_changed_file_status(base_sha: str | None, head_sha: str | None):
    if not base_sha or not head_sha:
        return {}
    cp = run(["git", "diff", "--name-status", base_sha, head_sha], cwd=REPO_ROOT)
    if cp.returncode != 0:
        print("⚠️  Could not compute git diff status for changed files.")
        print(cp.stderr.strip())
        return {}

    out = {}
    for line in cp.stdout.splitlines():
        parts = line.split("	", 1)
        if len(parts) != 2:
            continue
        status, path = parts
        out[path.strip()] = status.strip()
    return out


def get_changed_files(base_sha: str | None, head_sha: str | None):
    if not base_sha or not head_sha:
        return []
    cp = run(["git", "diff", "--name-only", base_sha, head_sha], cwd=REPO_ROOT)
    if cp.returncode != 0:
        print("⚠️  Could not compute git diff for changed files.")
        print(cp.stderr.strip())
        return []
    return [line.strip() for line in cp.stdout.splitlines() if line.strip()]


def is_bootstrap_pr(changed_status: dict[str, str]) -> bool:
    """Allow one-time baseline PRs to merge while introducing the gate itself."""
    if changed_status.get('.github/scripts/gov_security_gates.py') != 'A':
        return False

    allowed_prefixes = (
        '.github/',
        'GOVERNANCE/',
        'COMPLIANCE/',
        'SECURITY/',
        'EVALUATION/',
    )
    allowed_files = {
        'CODEOWNERS',
        'SECURITY.md',
        'SUPPORT.md',
        'CONTRIBUTING.md',
        'CODE_OF_CONDUCT.md',
    }

    for path in changed_status.keys():
        if path in allowed_files:
            continue
        if not path.startswith(allowed_prefixes):
            return False
    return True


def should_gate(changed_files):
    guard_paths = [
        "GOVERNANCE/",
        "COMPLIANCE/",
        "SECURITY/",
        "EVALUATION/",
        ".github/branch-protection-manifest.md",
        ".github/workflows/gov-security-gates.yml",
        ".github/scripts/gov_security_gates.py",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/CODEOWNERS",
        "CODE_OF_CONDUCT.md",
        "CONTRIBUTING.md",
        "SUPPORT.md",
        "SECURITY.md",
        "CODEOWNERS",
    ]
    return any(any(p.startswith(g) for g in guard_paths) for p in changed_files)


def run_gitleaks_if_available():
    if not shutil.which("gitleaks"):
        print("ℹ️  gitleaks not installed; skipping secret scan.")
        return True

    report = Path("/tmp/gov-gitleaks-report.json")
    cp = run(["gitleaks", "detect", "--no-git", "--redact", "--exit-code", "1", "--report-format", "json", "--report-path", str(report), "--source", str(REPO_ROOT)])
    if cp.returncode == 0:
        print("✅ gitleaks: no findings")
        return True

    print("❌ gitleaks found issues.")
    return False


def run_dependency_scan_if_available(changed_files):
    dep_files = [
        "package.json",
        "package-lock.json",
        "pnpm-lock.yaml",
        "yarn.lock",
        "requirements.txt",
        "poetry.lock",
        "pyproject.toml",
        "Cargo.toml",
        "Cargo.lock",
    ]

    if not any(any(f.endswith(item) for item in dep_files) for f in changed_files):
        return True

    if shutil.which("pnpm") and (REPO_ROOT / "pnpm-lock.yaml").exists():
        print("Running pnpm audit (audit-level high)...")
        cp = run(["pnpm", "audit", "--audit-level", "high"], cwd=REPO_ROOT)
        if cp.returncode != 0:
            print("❌ pnpm audit reported issues.")
            print(cp.stdout)
            print(cp.stderr)
            return False
        print("✅ pnpm audit passed")
        return True

    if shutil.which("npm") and (REPO_ROOT / "package-lock.json").exists():
        print("Running npm audit (audit-level high)...")
        cp = run(["npm", "audit", "--audit-level", "high"], cwd=REPO_ROOT)
        if cp.returncode != 0:
            print("⚠️  npm audit failed; leaving as warning because toolchain may differ in CI.")
            print(cp.stdout)
            print(cp.stderr)
            return True
        print("✅ npm audit passed")
        return True

    print("ℹ️  No supported dependency scanner available for this stack.")
    return True


def has_transitional_evidence(pr_body: str) -> bool:
    if PLACEHOLDER.search(pr_body):
        return False
    text = normalize(pr_body)
    evidence_terms = ["security", "risk", "verification", "release", "data", "threat"]
    return sum(term in text for term in evidence_terms) >= 3


def check_pr_evidence(pr_body: str) -> bool:
    sections = split_sections(pr_body)
    ok, missing = section_present(sections, REQUIRED_SECTIONS)
    if ok:
        return True
    if has_transitional_evidence(pr_body):
        print("ℹ️  Transitional PR evidence detected; accepting legacy body format.")
        return True
    print(f"❌ Missing or incomplete governance section in PR body: {missing}")
    print("PR body must include the required governance headings and non-placeholder content.")
    return False


def main() -> int:
    context = get_pr_context()
    changed_files = get_changed_files(context["base"] if context else None, context["head"] if context else None) if context else []
    changed_status = get_changed_file_status(context["base"] if context else None, context["head"] if context else None) if context else {}

    print(f"🔎 Reviewed {len(changed_files)} changed file(s) in scope candidate set.")
    if not should_gate(changed_files):
        print("✅ No governance-sensitive path changes detected; skip PR evidence strict mode.")
        return 0

    failed = False
    if context and context.get("body") is not None:
        if is_bootstrap_pr(changed_status):
            print("ℹ️  Bootstrap governance PR detected; skipping strict PR evidence check once.")
        elif not check_pr_evidence(context["body"]):
            failed = True
    else:
        print("⚠️  No PR body available; skipping PR evidence check.")

    if not run_gitleaks_if_available():
        failed = True

    if not run_dependency_scan_if_available(changed_files):
        failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
