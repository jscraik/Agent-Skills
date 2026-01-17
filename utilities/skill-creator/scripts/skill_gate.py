#!/usr/bin/env python3
"""
skill_gate.py

Gold-standard gate for Codex agent skills.

Enforces:
- Codex frontmatter validity + selection quality (WHAT + WHEN)
- Required SKILL.md sections (MUST)
- Progressive disclosure budgets (MUST)
- Contract + eval coverage (MUST)
- Basic safety hygiene (redaction language; fail-fast gating)

Usage:
  python scripts/skill_gate.py <path/to/skill-dir-or-SKILL.md>

Exit codes:
  0  pass
  1  parsing/IO error
  2  gate failed (one or more FAIL findings)

Recommended CI:
  python scripts/skill_gate.py .codex/skills/<skill-name> --format json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import yaml


class Level(IntEnum):
    INFO = 1
    WARN = 2
    FAIL = 3


@dataclass(frozen=True)
class Finding:
    level: Level
    code: str
    message: str
    evidence: str = ""


@dataclass(frozen=True)
class SkillDoc:
    path: Path
    raw: str
    frontmatter: Dict[str, Any]
    body: str
    fm_start_line: int
    fm_end_line: int


_FM_DELIM = re.compile(r"^\s*---\s*$")


def _resolve_skill_md_path(path_like: str) -> Path:
    p = Path(path_like).expanduser().resolve()
    return (p / "SKILL.md") if p.is_dir() else p


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def _parse_frontmatter(raw: str, strict_line1: bool) -> Tuple[Dict[str, Any], str, int, int]:
    lines = raw.splitlines(keepends=True)
    if not lines:
        raise ValueError("SKILL.md is empty")

    if strict_line1:
        if not _FM_DELIM.match(lines[0]):
            raise ValueError("Strict mode: frontmatter must start on line 1 with `---`.")
        start_idx = 0
    else:
        start_idx: Optional[int] = None
        for i, line in enumerate(lines):
            if line.strip():
                start_idx = i
                break
        if start_idx is None:
            raise ValueError("SKILL.md has no content")
        if not _FM_DELIM.match(lines[start_idx]):
            raise ValueError("Missing YAML frontmatter. Expected `---` as first non-empty line.")

    end_idx: Optional[int] = None
    for j in range(start_idx + 1, len(lines)):
        if _FM_DELIM.match(lines[j]):
            end_idx = j
            break
    if end_idx is None:
        raise ValueError("Unterminated YAML frontmatter. Missing closing `---`.")

    yaml_text = "".join(lines[start_idx + 1 : end_idx])
    if "\t" in yaml_text:
        raise ValueError("Frontmatter YAML must use spaces (tabs found).")

    try:
        fm_obj = yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in frontmatter: {e}") from e

    if fm_obj is None:
        fm: Dict[str, Any] = {}
    elif isinstance(fm_obj, dict):
        fm = fm_obj
    else:
        raise ValueError("Frontmatter YAML must be a mapping/object.")

    body = "".join(lines[end_idx + 1 :]).lstrip("\n")
    return fm, body, start_idx + 1, end_idx + 1


def load_skill(path_like: str, strict_line1: bool) -> SkillDoc:
    path = _resolve_skill_md_path(path_like)
    if not path.exists():
        raise FileNotFoundError(f"SKILL.md not found at: {path}")

    raw = _read_text(path)
    fm, body, fm_start, fm_end = _parse_frontmatter(raw, strict_line1=strict_line1)
    return SkillDoc(path=path, raw=raw, frontmatter=fm, body=body, fm_start_line=fm_start, fm_end_line=fm_end)


def _has_any(text: str, needles: Sequence[str]) -> bool:
    t = text.lower()
    return any(n.lower() in t for n in needles)


def _count_lines(s: str) -> int:
    return 0 if not s else s.count("\n") + 1


def _read_yaml_mapping(path: Path) -> Dict[str, Any]:
    obj = yaml.safe_load(path.read_text(encoding="utf-8"))
    if obj is None:
        return {}
    if not isinstance(obj, dict):
        raise ValueError(f"{path} must be a YAML mapping/object.")
    return obj


def _extract_h2_blocks(body: str) -> List[Tuple[str, str]]:
    matches = list(re.finditer(r"(?m)^##\s+(.+?)\s*$", body))
    blocks: List[Tuple[str, str]] = []

    for i, m in enumerate(matches):
        title = m.group(1).strip().lower()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        section_text = body[start:end].strip()
        blocks.append((title, section_text))
    return blocks


def _h2_titles(body: str) -> List[str]:
    return [t for (t, _) in _extract_h2_blocks(body)]


def _find_section_text(body: str, aliases: Sequence[str]) -> str:
    for title, text in _extract_h2_blocks(body):
        for a in aliases:
            if a.lower() in title:
                return text
    return ""


def _code_fence_blocks(body: str) -> List[str]:
    blocks: List[str] = []
    for m in re.finditer(r"```[^\n]*\n(.*?)\n```", body, flags=re.DOTALL):
        blocks.append(m.group(1))
    return blocks


def _iter_files(skill_dir: Path, rel_dir: str) -> List[Path]:
    p = skill_dir / rel_dir
    if not p.exists() or not p.is_dir():
        return []
    return sorted([c for c in p.rglob("*") if c.is_file()])


def check_codex_frontmatter(doc: SkillDoc, *, min_desc_len: int) -> List[Finding]:
    fm = doc.frontmatter
    out: List[Finding] = []

    name = fm.get("name")
    desc = fm.get("description")

    if not isinstance(name, str) or not name.strip():
        out.append(Finding(Level.FAIL, "FM_NAME_MISSING", "Missing/invalid `name` (required)."))
    else:
        if "\n" in name or "\r" in name:
            out.append(Finding(Level.FAIL, "FM_NAME_MULTILINE", "`name` must be single-line."))
        if len(name) > 100:
            out.append(Finding(Level.FAIL, "FM_NAME_TOO_LONG", f"`name` too long ({len(name)} > 100)."))
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name.strip()):
            out.append(Finding(Level.WARN, "FM_NAME_STYLE", "Consider kebab-case name (lowercase + hyphens)."))

    if not isinstance(desc, str) or not desc.strip():
        out.append(Finding(Level.FAIL, "FM_DESC_MISSING", "Missing/invalid `description` (required)."))
        return out

    if "\n" in desc or "\r" in desc:
        out.append(Finding(Level.FAIL, "FM_DESC_MULTILINE", "`description` must be single-line."))
    if len(desc) > 500:
        out.append(Finding(Level.FAIL, "FM_DESC_TOO_LONG", f"`description` too long ({len(desc)} > 500)."))
    if len(desc.strip()) < min_desc_len:
        out.append(Finding(Level.WARN, "FM_DESC_SHORT", f"Description is brief (< {min_desc_len}); expand for better discovery."))

    has_when = _has_any(desc, ["when ", "if ", "whenever ", "use this skill", "use this when", "trigger"])
    has_what = _has_any(desc, [
        "draft", "generate", "analyze", "extract", "validate", "convert", "build",
        "create", "summarize", "review", "audit", "lint", "plan", "scaffold",
    ])
    if not (has_when and has_what):
        out.append(Finding(
            Level.FAIL,
            "FM_DESC_WHAT_WHEN",
            "Description MUST include WHAT the skill does and WHEN to use it (trigger contexts).",
            evidence=f"description: {desc.strip()}",
        ))

    return out


def check_progressive_disclosure(doc: SkillDoc, *, max_lines: int, max_codeblock_lines: int) -> List[Finding]:
    out: List[Finding] = []

    total_lines = _count_lines(doc.raw)
    if total_lines > max_lines:
        out.append(Finding(
            Level.FAIL,
            "PD_SKILLMD_TOO_LONG",
            f"SKILL.md exceeds line budget ({total_lines} > {max_lines}). Move bulk content to references/ and scripts/.",
        ))

    blocks = _code_fence_blocks(doc.body)
    for i, b in enumerate(blocks, 1):
        blines = _count_lines(b)
        if blines > max_codeblock_lines:
            out.append(Finding(
                Level.WARN,
                "PD_LARGE_CODEBLOCK",
                f"Large code block detected ({blines} lines). Prefer scripts/ and reference them from SKILL.md.",
                evidence=f"codeblock #{i}: {blines} lines",
            ))

    return out


def check_required_sections(doc: SkillDoc, *, require_philosophy: bool) -> List[Finding]:
    out: List[Finding] = []
    h2s = _h2_titles(doc.body)

    required: Dict[str, List[str]] = {
        "when_to_use": ["when to use", "usage", "triggers", "invocation"],
        "inputs": ["inputs", "assumptions", "requirements"],
        "outputs": ["outputs", "deliverables", "result"],
        "procedure": ["workflow", "procedure", "steps", "process"],
        "validation": ["validation", "checks", "verify", "acceptance", "gates"],
        "antipatterns": ["anti-pattern", "anti patterns", "what to avoid", "pitfalls"],
        "constraints": ["constraints", "safety"],
    }

    if require_philosophy:
        required["philosophy"] = ["philosophy", "principles", "mental model"]

    should: Dict[str, List[str]] = {
        "examples": ["examples", "example prompts"],
    }

    def present(aliases: Sequence[str]) -> bool:
        return any(any(a.lower() in t for a in aliases) for t in h2s)

    for key, aliases in required.items():
        if not present(aliases):
            out.append(Finding(
                Level.FAIL,
                f"SEC_{key.upper()}_MISSING",
                f"Missing required section: {key.replace('_', ' ')} (add a ## heading).",
            ))

    for key, aliases in should.items():
        if not present(aliases):
            out.append(Finding(
                Level.WARN,
                f"SEC_{key.upper()}_MISSING",
                f"Missing recommended section: {key.replace('_', ' ')} (add a ## heading).",
            ))

    return out


def check_workflow_fail_fast(doc: SkillDoc, *, require_fail_fast: bool) -> List[Finding]:
    out: List[Finding] = []

    validation_text = _find_section_text(doc.body, ["validation", "checks", "verify", "gates", "acceptance"])
    if not validation_text:
        return out

    signals = ["fail fast", "do not proceed", "stop", "abort", "on failure", "if fails", "must stop", "exit early"]
    has = _has_any(validation_text, signals)

    if require_fail_fast and not has:
        out.append(Finding(
            Level.FAIL,
            "WF_FAIL_FAST_REQUIRED",
            "Validation section MUST specify fail-fast behavior (stop at first failed gate; do not proceed).",
        ))
    elif not has:
        out.append(Finding(
            Level.WARN,
            "WF_FAIL_FAST_MISSING",
            "Validation section should specify fail-fast behavior (stop at first failed gate).",
        ))

    return out


def check_redaction_language(doc: SkillDoc, *, require_redaction: bool) -> List[Finding]:
    out: List[Finding] = []

    constraints_text = _find_section_text(doc.body, ["constraints", "safety"])
    corpus = constraints_text if constraints_text else doc.body

    redaction_signals = [
        "redact", "redaction", "secrets", "tokens", "api key", "credentials",
        "pii", "personal data", "sensitive",
    ]
    has = _has_any(corpus, redaction_signals)

    if require_redaction and not has:
        out.append(Finding(
            Level.FAIL,
            "SAFE_REDACTION_REQUIRED",
            "Constraints/Safety MUST mention redaction of secrets/sensitive data by default.",
        ))
    elif not has:
        out.append(Finding(
            Level.WARN,
            "SAFE_REDACTION_MISSING",
            "Consider adding redaction guidance (secrets/tokens/PII) in Constraints/Safety.",
        ))

    return out


def check_schema_version_signal(doc: SkillDoc) -> List[Finding]:
    out: List[Finding] = []

    body = doc.body.lower()
    schema_signals = [
        "output schema", "schema.json", "json schema", "zod", "schema_version", "strict json",
        "machine-checkable", "validator", "contract",
    ]
    if _has_any(body, schema_signals):
        if "schema_version" not in body:
            out.append(Finding(
                Level.WARN,
                "OUT_SCHEMA_VERSION_MISSING",
                "Schema-bound outputs detected; consider including `schema_version` in the output contract.",
            ))
    return out


def check_path_safety(doc: SkillDoc) -> List[Finding]:
    out: List[Finding] = []

    body = doc.body

    if re.search(r"(?m)^[A-Za-z]:\\", body):
        out.append(Finding(Level.WARN, "PATH_WINDOWS", "Windows-style paths detected; prefer POSIX-style relative paths."))

    if re.search(r"(?m)^\s*/", body):
        out.append(Finding(Level.WARN, "PATH_ABSOLUTE", "Absolute paths detected; prefer repo-relative paths."))

    if re.search(r"(?m)\./", body):
        out.append(Finding(Level.WARN, "PATH_TRAVERSAL", "Parent directory traversal (`../`) mentioned; avoid in references."))

    return out


def check_contract_and_evals(skill_dir: Path, *, require_contract: bool, require_evals: bool) -> List[Finding]:
    out: List[Finding] = []
    refs_dir = skill_dir / "references"

    contract_path = refs_dir / "contract.yaml"
    evals_path = refs_dir / "evals.yaml"

    if require_contract:
        if not contract_path.exists():
            out.append(Finding(Level.FAIL, "CONTRACT_MISSING", "Missing references/contract.yaml (required for gold)."))
        else:
            try:
                contract = _read_yaml_mapping(contract_path)
                required_keys = ["purpose", "triggers", "inputs", "outputs", "non_goals", "risks"]
                missing = [k for k in required_keys if k not in contract]
                if missing:
                    out.append(Finding(Level.FAIL, "CONTRACT_KEYS_MISSING", f"contract.yaml missing keys: {', '.join(missing)}"))

                if "triggers" in contract and not isinstance(contract["triggers"], list):
                    out.append(Finding(Level.FAIL, "CONTRACT_TRIGGERS_SHAPE", "`triggers` must be a list."))
                if "inputs" in contract and not isinstance(contract["inputs"], list):
                    out.append(Finding(Level.FAIL, "CONTRACT_INPUTS_SHAPE", "`inputs` must be a list."))
                if "outputs" in contract and not isinstance(contract["outputs"], list):
                    out.append(Finding(Level.FAIL, "CONTRACT_OUTPUTS_SHAPE", "`outputs` must be a list."))
            except Exception as e:
                out.append(Finding(Level.FAIL, "CONTRACT_INVALID", f"contract.yaml invalid: {e}"))

    if require_evals:
        if not evals_path.exists():
            out.append(Finding(Level.FAIL, "EVALS_MISSING", "Missing references/evals.yaml (required for gold)."))
        else:
            try:
                obj = yaml.safe_load(evals_path.read_text(encoding="utf-8"))
                if not isinstance(obj, dict) or "cases" not in obj or not isinstance(obj["cases"], list):
                    out.append(Finding(Level.FAIL, "EVALS_SHAPE", "evals.yaml must be a mapping with `cases: [ ... ]`."))
                else:
                    cases = obj["cases"]
                    if len(cases) < 3:
                        out.append(Finding(Level.FAIL, "EVALS_TOO_FEW", "Provide at least 3 evaluation cases (happy/edge/failure)."))

                    for i, c in enumerate(cases, 1):
                        if not isinstance(c, dict):
                            out.append(Finding(Level.FAIL, "EVALS_CASE_INVALID", f"Case #{i} must be a mapping."))
                            continue
                        for k in ["name", "prompt", "acceptance"]:
                            if k not in c:
                                out.append(Finding(Level.FAIL, "EVALS_CASE_KEYS", f"Case #{i} missing `{k}`."))
                        if "acceptance" in c and not isinstance(c["acceptance"], list):
                            out.append(Finding(Level.FAIL, "EVALS_ACCEPTANCE_SHAPE", f"Case #{i} `acceptance` must be a list."))
            except Exception as e:
                out.append(Finding(Level.FAIL, "EVALS_INVALID", f"evals.yaml invalid: {e}"))

    return out


def check_repo_references(doc: SkillDoc) -> List[Finding]:
    out: List[Finding] = []
    skill_dir = doc.path.parent

    scripts = _iter_files(skill_dir, "scripts")
    refs = _iter_files(skill_dir, "references")
    assets = _iter_files(skill_dir, "assets")

    body = doc.body

    if scripts:
        names = [p.name for p in scripts]
        if not _has_any(body, ["scripts/"] + names):
            out.append(Finding(Level.WARN, "REPO_SCRIPTS_UNREFERENCED", "scripts/ exists but is not referenced in SKILL.md."))

    for rel_dir, files in [("references", refs), ("assets", assets)]:
        if files:
            names = [p.name for p in files]
            if not _has_any(body, [f"{rel_dir}/"] + names):
                out.append(Finding(Level.WARN, f"REPO_{rel_dir.upper()}_UNREFERENCED", f"{rel_dir}/ exists but is not referenced in SKILL.md."))

    return out


def _lvl_name(l: Level) -> str:
    return {Level.INFO: "INFO", Level.WARN: "WARN", Level.FAIL: "FAIL"}[l]


def run_gate(
    doc: SkillDoc,
    *,
    max_lines: int,
    max_codeblock_lines: int,
    min_desc_len: int,
    require_contract: bool,
    require_evals: bool,
    require_philosophy: bool,
    require_redaction: bool,
    require_fail_fast: bool,
) -> List[Finding]:
    findings: List[Finding] = []

    findings.extend(check_codex_frontmatter(doc, min_desc_len=min_desc_len))
    findings.extend(check_progressive_disclosure(doc, max_lines=max_lines, max_codeblock_lines=max_codeblock_lines))
    findings.extend(check_required_sections(doc, require_philosophy=require_philosophy))
    findings.extend(check_workflow_fail_fast(doc, require_fail_fast=require_fail_fast))
    findings.extend(check_redaction_language(doc, require_redaction=require_redaction))
    findings.extend(check_schema_version_signal(doc))
    findings.extend(check_path_safety(doc))

    skill_dir = doc.path.parent
    findings.extend(check_contract_and_evals(skill_dir, require_contract=require_contract, require_evals=require_evals))
    findings.extend(check_repo_references(doc))

    findings.sort(key=lambda f: (-int(f.level), f.code))
    return findings


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="skill_gate.py", description="Gold-standard gate for Codex SKILL.md quality.")
    p.add_argument("path", help="Path to a skill directory or SKILL.md file.")
    p.add_argument("--format", choices=["text", "json"], default="text")

    p.add_argument("--max-lines", type=int, default=500, help="Max allowed lines in SKILL.md (default: 500).")
    p.add_argument("--max-codeblock-lines", type=int, default=120, help="Warn if a code block exceeds this (default: 120).")
    p.add_argument("--min-description-len", type=int, default=120, help="Warn if description shorter than this (default: 120).")

    p.add_argument(
        "--strict-frontmatter-line1",
        action="store_true",
        help="Require frontmatter to start on line 1 with `---`.",
    )

    p.add_argument("--no-require-contract", action="store_true", help="Do not require references/contract.yaml.")
    p.add_argument("--no-require-evals", action="store_true", help="Do not require references/evals.yaml.")
    p.add_argument("--no-require-philosophy", action="store_true", help="Do not require a Philosophy/Principles section.")
    p.add_argument("--no-require-redaction", action="store_true", help="Do not require redaction language in Constraints/Safety.")
    p.add_argument("--require-fail-fast", action="store_true", help="Require fail-fast language in Validation section (FAIL if absent).")

    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)

    try:
        doc = load_skill(args.path, strict_line1=args.strict_frontmatter_line1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    findings = run_gate(
        doc,
        max_lines=args.max_lines,
        max_codeblock_lines=args.max_codeblock_lines,
        min_desc_len=args.min_description_len,
        require_contract=not args.no_require_contract,
        require_evals=not args.no_require_evals,
        require_philosophy=not args.no_require_philosophy,
        require_redaction=not args.no_require_redaction,
        require_fail_fast=bool(args.require_fail_fast),
    )

    failed = any(f.level == Level.FAIL for f in findings)

    if args.format == "json":
        payload = {
            "skill": str(doc.path),
            "name": doc.frontmatter.get("name"),
            "failed": failed,
            "findings": [
                {"level": _lvl_name(f.level), "code": f.code, "message": f.message, "evidence": f.evidence}
                for f in findings
            ],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Skill: {doc.frontmatter.get('name', 'unknown')}")
        print(f"Path:  {doc.path}\n")
        for f in findings:
            ev = f" | {f.evidence}" if f.evidence else ""
            print(f"{_lvl_name(f.level)} {f.code}: {f.message}{ev}")
        print("\nRESULT:", "FAIL" if failed else "PASS")

    return 2 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
