#!/usr/bin/env python3
"""
analyze_skill.py

Analyze a Codex agent skill (SKILL.md) and emit a quality score + actionable feedback.

Usage:
    ~/.venvs/pyyaml/bin/python Plugins/skill-factory/skills/code_quality_review/skill-builder/Infrastructure/scripts/analyze_skill.py <path/to/skill-dir-or-SKILL.md>

Examples:
    ~/.venvs/pyyaml/bin/python Plugins/skill-factory/skills/code_quality_review/skill-builder/Infrastructure/scripts/analyze_skill.py github/my-skill
    ~/.venvs/pyyaml/bin/python Plugins/skill-factory/skills/code_quality_review/skill-builder/Infrastructure/scripts/analyze_skill.py github/my-skill/SKILL.md

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
import datetime as dt
import json
import re
import sys
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    yaml = None

from yaml_frontmatter import parse_frontmatter as _parse_frontmatter_shared  # noqa: E402  # type: ignore[import]
from yaml_frontmatter import read_text as _read_text  # noqa: E402  # type: ignore[import]
from yaml_frontmatter import resolve_skill_md_path as _resolve_skill_md_path  # noqa: E402  # type: ignore[import]


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

def load_skill(path_like: str) -> SkillDoc:
    skill_md_path = _resolve_skill_md_path(path_like)
    if not skill_md_path.exists():
        raise FileNotFoundError(f"SKILL.md not found at: {skill_md_path}")

    raw = _read_text(skill_md_path)
    fm, body, fm_start, fm_end = _parse_frontmatter_shared(raw)
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


def _extract_h2_blocks(body: str) -> List[Tuple[str, str]]:
    matches = list(re.finditer(r"(?m)^##\s+(.+?)\s*$", body))
    blocks: List[Tuple[str, str]] = []
    for i, match in enumerate(matches):
        title = match.group(1).strip().lower()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        blocks.append((title, body[start:end].strip()))
    return blocks


def _find_section_text(body: str, aliases: Sequence[str]) -> str:
    for title, text in _extract_h2_blocks(body):
        if any(alias.lower() in title for alias in aliases):
            return text
    return ""


def _research_surface_count(text: str) -> int:
    patterns = [
        r"\bskills?\b",
        r"\bagents?\b",
        r"\bhooks?\b",
        r"\bprompts?\b",
        r"\bplugins?\b",
        r"\bapps?\b",
        r"\bmcp(?:s| servers?)?\b",
    ]
    return sum(1 for pattern in patterns if re.search(pattern, text, flags=re.IGNORECASE))


def _focus_language_count(text: str) -> int:
    phrases = [
        "smallest package",
        "smallest viable",
        "smallest boundary",
        "focused",
        "narrow",
        "2-3",
        "2–3",
        "2 to 3",
        "first pass",
        "start with",
        "limit scope",
        "avoid sprawling",
        "package boundary",
        "keep scope tight",
    ]
    return sum(1 for phrase in phrases if phrase in text.lower())


def _load_eval_cases(skill_dir: Path) -> List[Dict[str, Any]]:
    evals_path = skill_dir / "references" / "evals.yaml"
    if yaml is None or not evals_path.exists():
        return []
    try:
        obj = yaml.safe_load(evals_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(obj, dict):
        return []
    cases = obj.get("cases", [])
    if not isinstance(cases, list):
        return []
    return [case for case in cases if isinstance(case, dict)]


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


    # Prefer minimal official frontmatter: `name` + `description`.
    # Optional official keys are allowed but should remain minimal.
    extra_keys = sorted(set(fm.keys()) - {"name", "description", "license", "allowed-tools", "metadata"})
    if extra_keys:
        findings.append(
            Finding(
                "Frontmatter",
                -2,
                f"⚠️ Extra/non-official frontmatter keys present: {', '.join(extra_keys)}. Prefer official minimal frontmatter; use `agents/openai.yaml` for tool/UI metadata.",
            )
        )
        score -= 2

    # description should be a single-line scalar (no YAML block scalars)
    if isinstance(desc, str) and ("\n" in desc or "\r" in desc):
        findings.append(
            Finding(
                "Frontmatter",
                -5,
                "⚠️ `description` should be a single-line YAML scalar (no newlines / block scalars).",
            )
        )
        score -= 5

    # name (0..10)
    if isinstance(name, str) and name.strip():
        if (
            "\n" not in name
            and "\r" not in name
            and len(name) <= 64
            and bool(re.fullmatch(r"[a-z0-9-]+", name))
            and not name.startswith("-")
            and not name.endswith("-")
            and "--" not in name
        ):
            score += 10
            findings.append(Finding("Frontmatter", 10, "✅ `name` present and valid."))
        else:
            findings.append(
                Finding(
                    "Frontmatter",
                    0,
                    "❌ `name` must be single-line, <= 64 chars, and hyphen-case (lowercase letters/digits/hyphens).",
                    Severity.FAIL,
                )
            )
    else:
        findings.append(Finding("Frontmatter", 0, "❌ Missing/invalid `name`.", Severity.FAIL))

    # description (0..20)
    if isinstance(desc, str) and desc.strip():
        if "\n" in desc or "\r" in desc:
            findings.append(Finding("Frontmatter", 0, "❌ `description` must be single-line.", Severity.FAIL))
        elif len(desc) > 1024:
            findings.append(Finding("Frontmatter", 0, "❌ `description` must be <= 1024 chars.", Severity.FAIL))
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

    # NOTE:
    # Older analyzer versions penalized headings like "when to use" / "inputs" /
    # "outputs" / "failure mode". That guidance conflicted with the active
    # skill-gate requirements and with widely used skill templates in this repo.
    # We intentionally do not penalize those headings here.

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


def score_conciseness(doc: SkillDoc) -> CategoryResult:
    findings: List[Finding] = []
    score = 0
    max_score = 10

    line_count = len(doc.raw_text.splitlines())
    if line_count <= 320:
        score = 10
        findings.append(Finding("Conciseness", 10, f"✅ Concise length ({line_count} lines)."))
    elif line_count <= 360:
        score = 6
        findings.append(
            Finding(
                "Conciseness",
                6,
                f"⚠️ Slightly long ({line_count} lines). Aim for <=320; hard cap <=360.",
                Severity.WARN,
            )
        )
    else:
        findings.append(
            Finding(
                "Conciseness",
                0,
                f"❌ Too long ({line_count} lines). Reduce to <=320; hard cap <=360.",
                Severity.FAIL,
            )
        )

    return CategoryResult("Conciseness", score, max_score, findings)


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
        if _has_any(body, ["Infrastructure/scripts/"] + script_names):
            score += 5
            findings.append(Finding("Repo", 5, f"✅ `Infrastructure/scripts/` present and referenced ({len(scripts)} file(s))."))
        else:
            findings.append(Finding("Repo", 0, "⚠️ `Infrastructure/scripts/` present but not referenced in SKILL.md.", Severity.WARN))
    else:
        score += 2
        findings.append(Finding("Repo", 2, "ℹ️ No `Infrastructure/scripts/` directory (fine for instruction-only skills)."))

    # Infrastructure/references/assets (0..5)
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


def score_bundle_focus(doc: SkillDoc) -> CategoryResult:
    findings: List[Finding] = []
    max_score = 15
    score = 0

    body = doc.body
    desc = str(doc.frontmatter.get("description", ""))
    corpus = f"{desc}\n{body}"

    surfaces = _research_surface_count(corpus)
    focus_signals = _focus_language_count(corpus)

    if surfaces <= 3:
        score += 9
        findings.append(Finding("Research: Scope", 9, f"✅ Focused capability surface ({surfaces} major surface(s) mentioned)."))
    elif surfaces <= 5:
        score += 5
        findings.append(Finding("Research: Scope", 5, f"⚠️ Moderately broad capability surface ({surfaces} major surface(s)).", Severity.WARN))
    else:
        findings.append(Finding("Research: Scope", 0, f"⚠️ Broad capability surface ({surfaces} major surface(s)); tighten first-pass scope.", Severity.WARN))

    if focus_signals >= 3:
        score += 6
        findings.append(Finding("Research: Scope", 6, "✅ Explicit focus language encourages narrow first-pass packaging."))
    elif focus_signals >= 1:
        score += 3
        findings.append(Finding("Research: Scope", 3, "⚠️ Some focus language present; make package-boundary guidance more explicit.", Severity.WARN))
    else:
        findings.append(Finding("Research: Scope", 0, "⚠️ Missing explicit narrow-scope guidance such as smallest package or 2-3 modules.", Severity.WARN))

    return CategoryResult("Research: Scope Focus", min(score, max_score), max_score, findings)


def score_example_quality(doc: SkillDoc) -> CategoryResult:
    findings: List[Finding] = []
    max_score = 15
    score = 0

    examples_text = _find_section_text(doc.body, ["examples", "example prompts"])
    examples = re.findall(r"(?m)^\s*(?:[-*]|\d+\.)\s+.+$", examples_text)
    quoted_examples = re.findall(r'`[^`]{10,}`|"[^"\n]{10,}"', examples_text)
    realistic_signals = [
        "when the user asks",
        "user says",
        "github",
        "convert",
        "validate",
        "inspect",
        "scaffold",
        "migrate",
    ]
    realism_hits = sum(1 for signal in realistic_signals if signal in examples_text.lower())

    if len(examples) >= 3 or len(quoted_examples) >= 3:
        score += 10
        findings.append(Finding("Research: Examples", 10, "✅ Includes multiple worked examples or realistic trigger prompts."))
    elif len(examples) >= 2 or len(quoted_examples) >= 2:
        score += 7
        findings.append(Finding("Research: Examples", 7, "⚠️ Example coverage is decent; one more realistic example would strengthen routing.", Severity.WARN))
    elif examples_text:
        score += 3
        findings.append(Finding("Research: Examples", 3, "⚠️ Examples section exists but is thin; add 2-3 realistic prompts.", Severity.WARN))
    else:
        findings.append(Finding("Research: Examples", 0, "⚠️ No concrete examples detected; add realistic trigger prompts.", Severity.WARN))

    if realism_hits >= 3:
        score += 5
        findings.append(Finding("Research: Examples", 5, "✅ Examples appear grounded in real user requests and workflows."))
    elif realism_hits >= 1:
        score += 3
        findings.append(Finding("Research: Examples", 3, "⚠️ Some realism signals found; prefer more natural user-style prompts.", Severity.WARN))

    return CategoryResult("Research: Example Quality", min(score, max_score), max_score, findings)


def score_eval_prompt_realism(doc: SkillDoc) -> CategoryResult:
    findings: List[Finding] = []
    max_score = 15
    score = 0

    skill_dir = doc.skill_md_path.parent
    cases = _load_eval_cases(skill_dir)
    if not cases:
        findings.append(Finding("Research: Evals", 0, "⚠️ No eval cases parsed for realism scoring.", Severity.WARN))
        return CategoryResult("Research: Eval Realism", score, max_score, findings)

    skill_name = str(doc.frontmatter.get("name", "")).strip().lower()
    trigger_cases = [
        case for case in cases
        if case.get("should_trigger") is not False and str(case.get("category", "")).strip().lower() != "negative"
    ]
    if not trigger_cases:
        findings.append(Finding("Research: Evals", 0, "⚠️ No positive trigger evals detected for realism scoring.", Severity.WARN))
        return CategoryResult("Research: Eval Realism", score, max_score, findings)

    leaky = 0
    realistic = 0
    for case in trigger_cases:
        prompt = str(case.get("prompt", "")).strip().lower()
        if skill_name and skill_name in prompt:
            leaky += 1
        if any(token in prompt for token in ("please", "can you", "help me", "github", "convert", "validate", "build", "inspect")):
            realistic += 1

    leak_ratio = leaky / len(trigger_cases)
    realism_ratio = realistic / len(trigger_cases)

    if leak_ratio == 0:
        score += 8
        findings.append(Finding("Research: Evals", 8, "✅ Positive eval prompts avoid explicit skill-name leakage."))
    elif leak_ratio <= 0.33:
        score += 5
        findings.append(Finding("Research: Evals", 5, f"⚠️ Limited skill-name leakage in eval prompts ({leaky}/{len(trigger_cases)}).", Severity.WARN))
    else:
        findings.append(Finding("Research: Evals", 0, f"⚠️ Many eval prompts leak the skill name ({leaky}/{len(trigger_cases)}). Prefer natural user phrasing.", Severity.WARN))

    if realism_ratio >= 0.67:
        score += 7
        findings.append(Finding("Research: Evals", 7, "✅ Eval prompts mostly read like realistic user requests."))
    elif realism_ratio >= 0.34:
        score += 4
        findings.append(Finding("Research: Evals", 4, "⚠️ Some eval prompts feel realistic; keep reducing benchmark-only phrasing.", Severity.WARN))
    else:
        findings.append(Finding("Research: Evals", 0, "⚠️ Eval prompts look synthetic; rewrite more cases as realistic user utterances.", Severity.WARN))

    return CategoryResult("Research: Eval Realism", min(score, max_score), max_score, findings)


# -----------------------------
# Reporting
# -----------------------------

def _sev_icon(sev: Severity, *, emoji: bool) -> str:
    if not emoji:
        return ""
    return {Severity.INFO: "ℹ️", Severity.WARN: "⚠️", Severity.FAIL: "❌"}[sev]


def _utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def build_machine_payload(
    doc: SkillDoc,
    results: List[CategoryResult],
    total: int,
    max_total: int,
    *,
    min_pass: int,
) -> Dict[str, Any]:
    decision = "pass" if total >= min_pass else "fail"
    return {
        "schema_version": "1.1",
        "tool": "analyze_skill",
        "generated_at": _utc_now_iso(),
        "decision": decision,
        "exit_code": 0 if decision == "pass" else 2,
        "name": doc.frontmatter.get("name"),
        "description": doc.frontmatter.get("description"),
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


def render_machine_report(doc: SkillDoc, results: List[CategoryResult], total: int, max_total: int, *, fmt: str, min_pass: int) -> str:
    payload = build_machine_payload(doc, results, total, max_total, min_pass=min_pass)
    if fmt == "json":
        return json.dumps(payload, indent=2, ensure_ascii=False)
    elif fmt == "yaml":
        return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
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
    results.append(score_conciseness(doc))
    results.append(score_repo_integration(doc))
    results.append(score_bundle_focus(doc))
    results.append(score_example_quality(doc))
    results.append(score_eval_prompt_realism(doc))

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
    p.add_argument("--output", default=None, help="Optional path to write the rendered report.")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    if yaml is None:
        print(
            "ERROR: PyYAML is required to run analyze_skill.py.\n\n"
            "Fix:\n"
            "  ~/.venvs/pyyaml/bin/python Plugins/skill-factory/skills/code_quality_review/skill-builder/Infrastructure/scripts/analyze_skill.py <path/to/skill-dir-or-SKILL.md>\n",
            file=sys.stderr,
        )
        return 1

    try:
        doc = load_skill(args.path)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    total, max_total, results = analyze(doc)

    rendered = ""
    if args.format == "text":
        from contextlib import redirect_stdout
        from io import StringIO

        buf = StringIO()
        with redirect_stdout(buf):
            print_human_report(doc, results, total, max_total, emoji=not args.no_emoji)
        rendered = buf.getvalue()
    else:
        rendered = render_machine_report(doc, results, total, max_total, fmt=args.format, min_pass=args.min_pass)

    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + ("" if rendered.endswith("\n") else "\n"), encoding="utf-8")

    print(rendered, end="" if rendered.endswith("\n") else "\n")

    return 0 if total >= args.min_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
