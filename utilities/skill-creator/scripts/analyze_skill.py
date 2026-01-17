#!/usr/bin/env python3
"""
analyze_skill.py

Analyze a Codex agent skill (SKILL.md) and emit a quality score + actionable feedback.

Usage:
    python analyze_skill.py <path/to/skill-dir-or-SKILL.md>

Examples:
    python analyze_skill.py .codex/skills/my-skill
    python analyze_skill.py .codex/skills/my-skill/SKILL.md

Exit codes:
    0  score >= --min-pass
    1  parsing/IO error
    2  score <  --min-pass  (useful for CI gating)

Output:
- Human-readable report (default)
- Optional machine-readable JSON/YAML via --format
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import yaml


# -----------------------------
# Data model
# -----------------------------

class Severity(IntEnum):
    INFO = 1
    WARN = 2
    FAIL = 3


@dataclass(frozen=True)
class Finding:
    category: str
    points: int
    message: str
    severity: Severity = Severity.INFO
    evidence: str = ""


@dataclass(frozen=True)
class CategoryResult:
    category: str
    score: int
    max_score: int
    findings: List[Finding]


@dataclass(frozen=True)
class SkillDoc:
    skill_md_path: Path
    raw_text: str
    frontmatter: Dict[str, Any]
    body: str
    fm_start_line: int  # 1-indexed
    fm_end_line: int    # 1-indexed (line containing closing ---)


# -----------------------------
# Parsing
# -----------------------------

_FRONTMATTER_DELIM_RE = re.compile(r"^\s*---\s*$")


def _resolve_skill_md_path(path_like: str) -> Path:
    p = Path(path_like).expanduser().resolve()
    if p.is_dir():
        return p / "SKILL.md"
    return p


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def _parse_frontmatter(raw_text: str) -> Tuple[Dict[str, Any], str, int, int]:
    lines = raw_text.splitlines(keepends=True)

    first_nonempty_idx: Optional[int] = None
    for i, line in enumerate(lines):
        if line.strip():
            first_nonempty_idx = i
            break
    if first_nonempty_idx is None:
        raise ValueError("SKILL.md is empty")

    if not _FRONTMATTER_DELIM_RE.match(lines[first_nonempty_idx]):
        raise ValueError("Missing YAML frontmatter. Expected `---` as the first non-empty line.")

    end_idx: Optional[int] = None
    for j in range(first_nonempty_idx + 1, len(lines)):
        if _FRONTMATTER_DELIM_RE.match(lines[j]):
            end_idx = j
            break
    if end_idx is None:
        raise ValueError("Unterminated YAML frontmatter. Missing closing `---`.")

    yaml_text = "".join(lines[first_nonempty_idx + 1 : end_idx])
    try:
        fm_obj = yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in frontmatter: {e}") from e

    if fm_obj is None:
        fm: Dict[str, Any] = {}
    elif isinstance(fm_obj, dict):
        fm = fm_obj
    else:
        raise ValueError("Frontmatter YAML must be a mapping/object (key: value pairs).")

    body = "".join(lines[end_idx + 1 :]).lstrip("\n")
    fm_start_line = first_nonempty_idx + 1
    fm_end_line = end_idx + 1
    return fm, body, fm_start_line, fm_end_line


def load_skill(path_like: str) -> SkillDoc:
    skill_md_path = _resolve_skill_md_path(path_like)
    if not skill_md_path.exists():
        raise FileNotFoundError(f"SKILL.md not found at: {skill_md_path}")

    raw = _read_text(skill_md_path)
    fm, body, fm_start, fm_end = _parse_frontmatter(raw)
    return SkillDoc(
        skill_md_path=skill_md_path,
        raw_text=raw,
        frontmatter=fm,
        body=body,
        fm_start_line=fm_start,
        fm_end_line=fm_end,
    )


# -----------------------------
# Helpers
# -----------------------------

_H1_H6_RE = re.compile(r"(?m)^(#{1,6})\s+(.+?)\s*$")
_H2_RE = re.compile(r"(?m)^##\s+(.+?)\s*$")


def _has_any(text: str, needles: Sequence[str]) -> bool:
    t = text.lower()
    return any(n.lower() in t for n in needles)


def _count_regex(pattern: str, text: str, flags: int = 0) -> int:
    return len(re.findall(pattern, text, flags))


def _extract_headers(body: str) -> List[Tuple[int, str]]:
    out: List[Tuple[int, str]] = []
    for m in _H1_H6_RE.finditer(body):
        level = len(m.group(1))
        title = m.group(2).strip()
        out.append((level, title))
    return out


def _extract_h2_titles(body: str) -> List[str]:
    return [m.group(1).strip().lower() for m in _H2_RE.finditer(body)]


def _iter_files(skill_dir: Path, rel_dir: str) -> List[Path]:
    p = skill_dir / rel_dir
    if not p.exists() or not p.is_dir():
        return []
    return sorted([c for c in p.rglob("*") if c.is_file()])


# -----------------------------
# Scoring checks
# -----------------------------

def score_frontmatter(doc: SkillDoc) -> CategoryResult:
    fm = doc.frontmatter
    findings: List[Finding] = []
    score = 0
    max_score = 30  # heavier weight because it drives implicit invocation

    name = fm.get("name")
    desc = fm.get("description")

    # name (0..10)
    if isinstance(name, str) and name.strip():
        if "\n" not in name and "\r" not in name and len(name) <= 100:
            score += 10
            findings.append(Finding("Frontmatter", 10, "✅ `name` present and valid."))
        else:
            findings.append(Finding("Frontmatter", 0, "❌ `name` must be single-line and <= 100 chars.", Severity.FAIL))
    else:
        findings.append(Finding("Frontmatter", 0, "❌ Missing/invalid `name`.", Severity.FAIL))

    # description (0..20)
    if isinstance(desc, str) and desc.strip():
        if "\n" in desc or "\r" in desc:
            findings.append(Finding("Frontmatter", 0, "❌ `description` must be single-line.", Severity.FAIL))
        elif len(desc) > 500:
            findings.append(Finding("Frontmatter", 0, "❌ `description` must be <= 500 chars.", Severity.FAIL))
        else:
            # Points for clarity + trigger language
            dlen = len(desc.strip())
            trigger = _has_any(desc, ["when ", "if ", "whenever ", "use this skill"])
            if dlen >= 120 and trigger:
                score += 20
                findings.append(Finding("Frontmatter", 20, "✅ `description` is detailed and includes trigger language."))
            elif dlen >= 80 and trigger:
                score += 16
                findings.append(Finding("Frontmatter", 16, "⚠️ `description` is OK; expand slightly for better selection.", Severity.WARN))
            elif trigger:
                score += 10
                findings.append(Finding("Frontmatter", 10, "⚠️ `description` has a trigger but is brief.", Severity.WARN))
            elif dlen >= 120:
                score += 12
                findings.append(Finding("Frontmatter", 12, "⚠️ `description` is detailed but lacks explicit trigger language.", Severity.WARN))
            else:
                score += 6
                findings.append(Finding("Frontmatter", 6, "⚠️ `description` is brief and lacks explicit triggers.", Severity.WARN))
    else:
        findings.append(Finding("Frontmatter", 0, "❌ Missing/invalid `description`.", Severity.FAIL))

    return CategoryResult("Frontmatter", score, max_score, findings)


def score_philosophy(body: str) -> CategoryResult:
    findings: List[Finding] = []
    score = 0
    max_score = 20

    keywords = [
        "philosophy", "approach", "principle", "principles", "mental model", "framework",
        "mindset", "why", "tradeoff", "consider", "understand",
    ]
    found = [kw for kw in keywords if kw in body.lower()]

    if len(found) >= 3:
        score += 14
        findings.append(Finding("Philosophy", 14, f"✅ Philosophy indicators found: {', '.join(found[:5])}."))
    elif len(found) >= 1:
        score += 8
        findings.append(Finding("Philosophy", 8, f"⚠️ Some philosophy indicators found: {', '.join(found[:5])}.", Severity.WARN))
    else:
        findings.append(Finding("Philosophy", 0, "❌ No clear philosophical foundation detected.", Severity.FAIL))

    # guiding questions (0..6)
    questions = _count_regex(r"\?", body)
    if questions >= 3:
        score += 6
        findings.append(Finding("Philosophy", 6, f"✅ Contains {questions} guiding questions."))
    elif questions >= 1:
        score += 3
        findings.append(Finding("Philosophy", 3, f"⚠️ Contains {questions} guiding question(s).", Severity.WARN))

    return CategoryResult("Philosophy", score, max_score, findings)


def score_antipatterns(body: str) -> CategoryResult:
    findings: List[Finding] = []
    score = 0
    max_score = 20

    body_lc = body.lower()
    anti_pattern_keywords = [
        "avoid", "never", "don't", "do not", "anti-pattern", "anti pattern",
        "mistake", "pitfall", "warning", "wrong", "incorrect",
    ]
    found = [kw for kw in anti_pattern_keywords if kw in body_lc]

    # replicate your "avoid in first 500 chars" signal as a strong proxy
    avoid_early = "avoid" in body_lc[:500]
    strong_caps = _count_regex(r"\b(NEVER|DO NOT|DON'T)\b", body)

    if len(found) >= 5 or (avoid_early and len(found) >= 2):
        score += 14
        findings.append(Finding("Anti-Patterns", 14, f"✅ Strong anti-pattern guidance detected ({len(found)} signals)."))
    elif len(found) >= 2:
        score += 8
        findings.append(Finding("Anti-Patterns", 8, f"⚠️ Some anti-pattern guidance detected ({len(found)} signals).", Severity.WARN))
    else:
        findings.append(Finding("Anti-Patterns", 0, "❌ No explicit anti-pattern warnings detected.", Severity.FAIL))

    if strong_caps:
        bonus = min(6, strong_caps * 2)
        score += bonus
        findings.append(Finding("Anti-Patterns", bonus, f"✅ Contains {strong_caps} strong warning(s) in caps."))

    return CategoryResult("Anti-Patterns", min(score, max_score), max_score, findings)


def score_variation(body: str) -> CategoryResult:
    findings: List[Finding] = []
    score = 0
    max_score = 15

    body_lc = body.lower()
    variation_keywords = [
        "vary", "variation", "different", "diverse", "context-specific", "context specific",
        "adapt", "customize", "unique", "avoid repetition", "not the same",
    ]
    found = [kw for kw in variation_keywords if kw in body_lc]

    if len(found) >= 3:
        score += 10
        findings.append(Finding("Variation", 10, f"✅ Variation encouraged: {', '.join(found[:5])}."))
    elif len(found) >= 1:
        score += 6
        findings.append(Finding("Variation", 6, f"⚠️ Some variation mentioned: {', '.join(found[:5])}.", Severity.WARN))
    else:
        findings.append(Finding("Variation", 0, "❌ No explicit variation encouragement.", Severity.FAIL))

    template_warnings = _count_regex(r"(template|repetitive|generic|cookie-cutter|converge)", body_lc)
    if template_warnings:
        bonus = min(5, template_warnings)
        score += bonus
        findings.append(Finding("Variation", bonus, f"✅ Warns against generic patterns ({template_warnings} mention(s))."))

    return CategoryResult("Variation", min(score, max_score), max_score, findings)


def score_organization(body: str) -> CategoryResult:
    findings: List[Finding] = []
    score = 0
    max_score = 10

    headers = _extract_headers(body)
    h2s = _extract_h2_titles(body)

    if len(headers) >= 5:
        score += 6
        findings.append(Finding("Organization", 6, f"✅ Well-structured with {len(headers)} headings."))
    elif len(headers) >= 2:
        score += 3
        findings.append(Finding("Organization", 3, f"⚠️ Has {len(headers)} headings.", Severity.WARN))
    else:
        findings.append(Finding("Organization", 0, "❌ Lacks clear organization (few/no headings).", Severity.FAIL))

    # lists (0..4)
    list_items = _count_regex(r"(?m)^\s*[-*]\s+", body)
    if list_items >= 10:
        score += 4
        findings.append(Finding("Organization", 4, f"✅ Contains {list_items} list items (actionable)."))
    elif list_items >= 3:
        score += 2
        findings.append(Finding("Organization", 2, f"⚠️ Some list structure ({list_items} items).", Severity.WARN))

    # sanity: presence of key structure sections
    has_when = any("when" in t for t in h2s) or _has_any(body, ["when to use", "use this skill when"])
    has_io = _has_any(body, ["## inputs", "## outputs"]) or _has_any(body, ["inputs", "outputs"])
    if has_when and has_io:
        score = min(max_score, score + 1)
        findings.append(Finding("Organization", 1, "✅ Includes 'when to use' and I/O structure."))

    return CategoryResult("Organization", min(score, max_score), max_score, findings)


def score_empowerment(body: str) -> CategoryResult:
    findings: List[Finding] = []
    score = 0
    max_score = 5

    body_lc = body.lower()
    empowering_keywords = [
        "extraordinary", "capable", "unlock", "enable", "empower",
        "creative", "innovative", "push boundaries", "explore",
    ]
    found_emp = [kw for kw in empowering_keywords if kw in body_lc]

    if len(found_emp) >= 3:
        score += 5
        findings.append(Finding("Empowerment", 5, f"✅ Empowering tone: {', '.join(found_emp[:5])}."))
    elif len(found_emp) >= 1:
        score += 3
        findings.append(Finding("Empowerment", 3, f"⚠️ Some empowering language: {', '.join(found_emp[:5])}.", Severity.WARN))
    else:
        findings.append(Finding("Empowerment", 0, "ℹ️ No explicit empowering language found.", Severity.INFO))

    # Over-constraint penalty
    rigid = _count_regex(r"\b(must|always|required|mandatory)\b", body_lc)
    if rigid > 20:
        score = max(0, score - 2)
        findings.append(Finding("Empowerment", -2, f"⚠️ Many rigid constraints ({rigid} instances).", Severity.WARN))

    return CategoryResult("Empowerment", max(0, score), max_score, findings)


def score_repo_integration(doc: SkillDoc) -> CategoryResult:
    findings: List[Finding] = []
    score = 0
    max_score = 10

    skill_dir = doc.skill_md_path.parent
    body = doc.body
    scripts = _iter_files(skill_dir, "scripts")
    refs = _iter_files(skill_dir, "references")
    assets = _iter_files(skill_dir, "assets")

    # scripts (0..5)
    if scripts:
        script_names = [p.name for p in scripts]
        if _has_any(body, ["scripts/"] + script_names):
            score += 5
            findings.append(Finding("Repo", 5, f"✅ `scripts/` present and referenced ({len(scripts)} file(s))."))
        else:
            findings.append(Finding("Repo", 0, "⚠️ `scripts/` present but not referenced in SKILL.md.", Severity.WARN))
    else:
        score += 2
        findings.append(Finding("Repo", 2, "ℹ️ No `scripts/` directory (fine for instruction-only skills)."))

    # references/assets (0..5)
    bonus = 0
    for rel_dir, files in [("references", refs), ("assets", assets)]:
        if files:
            names = [p.name for p in files]
            if _has_any(body, [f"{rel_dir}/"] + names):
                bonus += 3
                findings.append(Finding("Repo", 3, f"✅ `{rel_dir}/` present and referenced ({len(files)} file(s))."))
            else:
                findings.append(Finding("Repo", 0, f"⚠️ `{rel_dir}/` present but not referenced.", Severity.WARN))
        else:
            bonus += 1
            findings.append(Finding("Repo", 1, f"ℹ️ No `{rel_dir}/` directory."))

    score += min(5, bonus)
    return CategoryResult("Repo Integration", min(score, max_score), max_score, findings)


# -----------------------------
# Reporting
# -----------------------------

def _sev_icon(sev: Severity, *, emoji: bool) -> str:
    if not emoji:
        return ""
    return {Severity.INFO: "ℹ️", Severity.WARN: "⚠️", Severity.FAIL: "❌"}[sev]


def print_human_report(doc: SkillDoc, results: List[CategoryResult], total: int, max_total: int, *, emoji: bool) -> None:
    name = doc.frontmatter.get("name", "unknown")
    print("=" * 78)
    print(f"SKILL QUALITY ANALYSIS: {name}")
    print("=" * 78)
    print(f"\nOVERALL SCORE: {total}/{max_total}\n")

    for r in results:
        print(f"{r.category}: {r.score}/{r.max_score}")
        for f in r.findings:
            icon = _sev_icon(f.severity, emoji=emoji)
            # show points as signed
            pts = f"{f.points:+d}"
            print(f"  {icon} [{pts}] {f.message}")
        print("")

    print("=" * 78)
    print("RECOMMENDATIONS")
    print("=" * 78)

    if total >= 80:
        print("\nExcellent: the skill is likely to be selected correctly and executed reliably.\n")
    elif total >= 60:
        print("\nGood: address WARN/FAIL items above to improve consistency.\n")
    elif total >= 40:
        print("\nNeeds improvement: prioritize Frontmatter, Philosophy, and Anti-Patterns.\n")
    else:
        print("\nSignificant improvements needed: rebuild structure and clarify selection triggers.\n")


def print_machine_report(doc: SkillDoc, results: List[CategoryResult], total: int, max_total: int, *, fmt: str) -> None:
    payload = {
        "name": doc.frontmatter.get("name"),
        "path": str(doc.skill_md_path),
        "total_score": total,
        "max_total": max_total,
        "categories": [
            {
                "category": r.category,
                "score": r.score,
                "max_score": r.max_score,
                "findings": [
                    {
                        "category": f.category,
                        "points": f.points,
                        "severity": str(f.severity.name),
                        "message": f.message,
                        "evidence": f.evidence,
                    }
                    for f in r.findings
                ],
            }
            for r in results
        ],
    }

    if fmt == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif fmt == "yaml":
        print(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True))
    else:
        raise ValueError(f"Unsupported format: {fmt}")


# -----------------------------
# Main
# -----------------------------

def analyze(doc: SkillDoc) -> Tuple[int, int, List[CategoryResult]]:
    results: List[CategoryResult] = []
    results.append(score_frontmatter(doc))
    results.append(score_philosophy(doc.body))
    results.append(score_antipatterns(doc.body))
    results.append(score_variation(doc.body))
    results.append(score_organization(doc.body))
    results.append(score_empowerment(doc.body))
    results.append(score_repo_integration(doc))

    total = sum(r.score for r in results)
    max_total = sum(r.max_score for r in results)
    return total, max_total, results


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="analyze_skill.py",
        description="Analyze a Codex skill (SKILL.md) and output a quality score.",
    )
    p.add_argument("path", help="Path to a skill directory or a SKILL.md file.")
    p.add_argument(
        "--format",
        choices=["text", "json", "yaml"],
        default="text",
        help="Output format (default: text).",
    )
    p.add_argument(
        "--min-pass",
        type=int,
        default=60,
        help="Exit with code 2 if score is below this threshold (default: 60).",
    )
    p.add_argument(
        "--no-emoji",
        action="store_true",
        help="Disable emoji in text output (useful for CI logs).",
    )
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)

    try:
        doc = load_skill(args.path)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    total, max_total, results = analyze(doc)

    if args.format == "text":
        print_human_report(doc, results, total, max_total, emoji=not args.no_emoji)
    else:
        print_machine_report(doc, results, total, max_total, fmt=args.format)

    return 0 if total >= args.min_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
