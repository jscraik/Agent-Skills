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
  ~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/skill_gate.py <path/to/skill-dir-or-SKILL.md>

Exit codes:
  0  pass
  1  parsing/IO error
  2  gate failed (one or more FAIL findings)

Recommended CI:
  ~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/skill_gate.py ~/dev/agent-skills/.agents/skills/<skill-name> --format json
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from dataclasses import dataclass
from enum import IntEnum
import fnmatch
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    preferred = Path.home() / ".venvs" / "pyyaml" / "bin" / "python"
    already_reexec = os.environ.get("SKILL_CREATOR_PYYAML_REEXEC") == "1"
    if preferred.exists() and not already_reexec:
        env = dict(os.environ)
        env["SKILL_CREATOR_PYYAML_REEXEC"] = "1"
        os.execve(str(preferred), [str(preferred), __file__, *sys.argv[1:]], env)

    print(
        "ERROR: PyYAML is required to run skill_gate.py.\n\n"
        "Fix (recommended):\n"
        "  ~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/skill_gate.py <path/to/skill-dir-or-SKILL.md>\n\n"
        "Notes:\n"
        "  - Do not use utilities/skill-builder/.venv/bin/python (this repo does not ship that venv).\n"
        "  - If ~/.venvs/pyyaml doesn't exist, create a venv with PyYAML installed.",
        file=sys.stderr,
    )
    raise SystemExit(1)


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


_TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".json",
    ".rules",
    ".toml",
    ".ini",
    ".cfg",
    ".py",
    ".sh",
    ".bash",
    ".zsh",
    ".js",
    ".ts",
}


def _default_prompt_patterns() -> List[Dict[str, str]]:
    return [
        {
            "code": "PI_OVERRIDE",
            "regex": r"\b(ignore|disregard|forget)\b.*\b(previous|prior|system|developer)\b",
            "message": "Potential prompt-injection override language detected; ensure this is not instructing the model to bypass system/developer instructions.",
            "severity": "high",
        },
        {
            "code": "PI_ROLEPLAY",
            "regex": r"\byou are now\b|\bpretend to be\b|\bact as\b",
            "message": "Role-shifting language detected; verify it is safe and limited to user content.",
            "severity": "medium",
        },
        {
            "code": "PI_TOOL_CHAIN",
            "regex": r"\b(bypass|jailbreak|exfiltrate)\b|\boverride\s+(?:system|safety|instruction|policy|guardrail|restriction)s?\b",
            "message": "High-risk control language detected; verify this does not instruct unsafe behavior.",
            "severity": "high",
        },
        {
            "code": "PI_COMMANDS",
            "regex": r"\b(curl|wget|powershell|invoke-webrequest|nc|netcat|rm\s+-rf|chmod\s+777)\b",
            "message": "Command-like instructions detected; ensure commands are gated and safe.",
            "severity": "medium",
        },
        {
            "code": "PI_OBFUSCATION",
            "regex": r"\b(base64|b64decode|decode\(['\"]base64['\"]\)|rot13|url ?decode|hex(?:lify)?|unicode escape|zero[- ]width|invisible character)\b",
            "message": "Potential obfuscation / hidden-instruction language detected; verify it cannot bypass safety checks.",
            "severity": "high",
        },
    ]


def _local_security_config_path() -> Path:
    override = os.environ.get("CODEX_SKILL_SECURITY_CONFIG")
    if override:
        return Path(override).expanduser()
    return Path("~/.codex/skill-security/allow-block.json").expanduser()


def _load_allow_block_patterns() -> Tuple[List[re.Pattern[str]], List[Tuple[re.Pattern[str], str, str]], List[Finding]]:
    findings: List[Finding] = []
    allowlist: List[re.Pattern[str]] = []
    blocklist: List[Tuple[re.Pattern[str], str, str]] = []
    config_path = _local_security_config_path()

    if not config_path.exists():
        return allowlist, blocklist, findings

    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("allow/block config must be an object")
        allow_raw = raw.get("allowlist", [])
        block_raw = raw.get("blocklist", [])
        if not isinstance(allow_raw, list) or not isinstance(block_raw, list):
            raise ValueError("allowlist and blocklist must be lists")

        for entry in allow_raw:
            if not isinstance(entry, dict):
                raise ValueError("allowlist entries must be objects")
            regex = str(entry.get("regex", "")).strip()
            if not regex:
                raise ValueError("allowlist entries must include regex")
            allowlist.append(re.compile(regex, re.IGNORECASE | re.DOTALL))

        for entry in block_raw:
            if not isinstance(entry, dict):
                raise ValueError("blocklist entries must be objects")
            regex = str(entry.get("regex", "")).strip()
            message = str(entry.get("message", "Blocklist match")).strip()
            severity = str(entry.get("severity", "high")).strip().lower()
            if not regex:
                raise ValueError("blocklist entries must include regex")
            blocklist.append((re.compile(regex, re.IGNORECASE | re.DOTALL), message, severity))
    except Exception as exc:
        findings.append(Finding(
            Level.WARN,
            "PI_LOCAL_CONFIG",
            f"Failed to load local allow/block config; ignoring ({exc}).",
            evidence=str(config_path),
        ))
        allowlist = []
        blocklist = []

    return allowlist, blocklist, findings


def _is_text_file(path: Path) -> bool:
    if path.suffix.lower() in _TEXT_EXTENSIONS or path.name == "SKILL.md":
        return True
    try:
        chunk = path.read_bytes()[:4096]
    except OSError:
        return False
    if b"\x00" in chunk:
        return False
    try:
        chunk.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def _load_prompt_patterns(
    skill_dir: Path,
) -> Tuple[List[Tuple[str, re.Pattern[str], str, str]], List[Finding]]:
    config_path = skill_dir / "references" / "prompt-injection-patterns.json"
    findings: List[Finding] = []
    patterns: List[Tuple[str, re.Pattern[str], str, str]] = []
    allowed_severity = {"low", "medium", "high"}

    if config_path.exists():
        try:
            raw = json.loads(config_path.read_text(encoding="utf-8"))
            if not isinstance(raw, list):
                raise ValueError("prompt pattern config must be a list")
            for entry in raw:
                if not isinstance(entry, dict):
                    raise ValueError("prompt pattern entries must be objects")
                code = str(entry.get("code", "")).strip()
                regex = str(entry.get("regex", "")).strip()
                message = str(entry.get("message", "")).strip()
                severity = str(entry.get("severity", "medium")).strip().lower()
                if not code or not regex or not message:
                    raise ValueError("prompt pattern entries must include code, regex, message")
                if severity not in allowed_severity:
                    findings.append(Finding(
                        Level.WARN,
                        "PI_PATTERN_CONFIG",
                        f"Invalid severity '{severity}' for {code}; defaulting to medium.",
                        evidence=str(config_path.relative_to(skill_dir)),
                    ))
                    severity = "medium"
                patterns.append((code, re.compile(regex, re.IGNORECASE | re.DOTALL), message, severity))
        except Exception as exc:
            findings.append(Finding(
                Level.WARN,
                "PI_PATTERN_CONFIG",
                f"Failed to load prompt-injection patterns; using defaults ({exc}).",
                evidence=str(config_path.relative_to(skill_dir)),
            ))
            patterns = []

    if not patterns:
        for entry in _default_prompt_patterns():
            patterns.append((
                entry["code"],
                re.compile(entry["regex"], re.IGNORECASE | re.DOTALL),
                entry["message"],
                entry["severity"],
            ))

    return patterns, findings


def _load_skillignore(skill_dir: Path) -> List[str]:
    ignore_file = skill_dir / ".skillignore"
    if not ignore_file.exists():
        return []
    lines = []
    for raw in ignore_file.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines


def _is_ignored(path: Path, skill_dir: Path, patterns: Sequence[str]) -> bool:
    rel = str(path.relative_to(skill_dir)).replace("\\", "/")
    return any(fnmatch.fnmatch(rel, pattern) for pattern in patterns)


def _iter_scan_targets(skill_dir: Path) -> List[Tuple[Path, bool]]:
    ignore_patterns = _load_skillignore(skill_dir)
    targets: List[Tuple[Path, bool]] = []
    for path in skill_dir.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts:
            continue
        if _is_ignored(path, skill_dir, ignore_patterns):
            continue
        targets.append((path, _is_text_file(path)))
    return sorted(targets, key=lambda item: str(item[0]))


def _severity_to_level(severity: str, *, fail_on_high: bool) -> Level:
    sev = (severity or "").strip().lower()
    if sev == "high" and fail_on_high:
        return Level.FAIL
    if sev in {"high", "medium", "low"}:
        return Level.WARN
    return Level.WARN


_DEFAULT_PI_EXPECTED_PATH_PATTERNS = (
    "assets/**",
    "examples/**",
    "references/evals*.yaml",
    "references/evals-v2-migration.md",
    "references/destructive-commands.rules",
    "references/api-security.md",
    "references/best-practices.md",
    "references/core-principles.md",
    "references/composability.md",
    "references/extended.md",
    "references/governance-and-style.md",
    "references/philosophy-patterns.md",
    "references/security-hardening.md",
    "references/prompt-injection-expected-context.json",
    "scripts/skill_gate.py",
    "scripts/openclaw_skill_guard.py",
    "scripts/recursive_skill_loop.py",
    "scripts/generate_pressure_tests.py",
    "scripts/migrate_evals_v2.py",
    "scripts/run_skill_evals.py",
    "scripts/run_skill_graph_smoke.py",
    "scripts/test_*.py",
    "workflows/create-new-skill.md",
)

_DEFAULT_PI_CONTEXT_SIGNALS = (
    "prompt injection",
    "adversarial",
    "jailbreak",
    "forbidden_commands",
    "security coverage",
    "red team",
    # NOTE: generic terms like "regex", "re.compile(" and "pattern" were
    # removed – they are too common in ordinary skill content and can be
    # trivially planted to suppress PI_* findings. Expected-PI context is
    # now scoped to path patterns only (see _is_expected_pi_context).
)

_DEFAULT_PI_SKIP_BINARY_GLOBS = ("assets/**",)


def _load_expected_pi_context(
    skill_dir: Path,
) -> Tuple[List[str], List[str], List[str], List[Finding]]:
    findings: List[Finding] = []
    cfg_path = skill_dir / "references" / "prompt-injection-expected-context.json"
    if not cfg_path.exists():
        return (
            list(_DEFAULT_PI_EXPECTED_PATH_PATTERNS),
            list(_DEFAULT_PI_CONTEXT_SIGNALS),
            list(_DEFAULT_PI_SKIP_BINARY_GLOBS),
            findings,
        )

    try:
        raw = json.loads(cfg_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("expected object")
        raw_paths = raw.get("path_patterns", _DEFAULT_PI_EXPECTED_PATH_PATTERNS)
        raw_signals = raw.get("context_signals", _DEFAULT_PI_CONTEXT_SIGNALS)
        raw_binary = raw.get("skip_binary_globs", _DEFAULT_PI_SKIP_BINARY_GLOBS)

        if not isinstance(raw_paths, list) or not all(isinstance(x, str) and x.strip() for x in raw_paths):
            raise ValueError("path_patterns must be a non-empty string list")
        if not isinstance(raw_signals, list) or not all(isinstance(x, str) and x.strip() for x in raw_signals):
            raise ValueError("context_signals must be a non-empty string list")
        if not isinstance(raw_binary, list) or not all(isinstance(x, str) and x.strip() for x in raw_binary):
            raise ValueError("skip_binary_globs must be a non-empty string list")

        return list(raw_paths), list(raw_signals), list(raw_binary), findings
    except Exception as exc:
        findings.append(
            Finding(
                Level.WARN,
                "PI_EXPECTED_CONTEXT_CONFIG",
                f"Failed to load expected PI context config; using defaults ({exc}).",
                evidence=str(cfg_path.relative_to(skill_dir)),
            )
        )
        return (
            list(_DEFAULT_PI_EXPECTED_PATH_PATTERNS),
            list(_DEFAULT_PI_CONTEXT_SIGNALS),
            list(_DEFAULT_PI_SKIP_BINARY_GLOBS),
            findings,
        )


def _is_expected_pi_context(
    code: str,
    rel_path: str,
    text: str,
    path_patterns: Sequence[str],
    context_signals: Sequence[str],
) -> bool:
    rel = rel_path.replace("\\", "/")
    if any(fnmatch.fnmatch(rel, pat) for pat in path_patterns):
        return True

    # Content-signal bypass removed: generic terms like "pattern" or "regex"
    # are easily planted to suppress PI_* findings in arbitrary files.
    # Expected PI context is now path-scoped only.
    _ = (code, text, context_signals)
    return False


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
        if "<" in name or ">" in name:
            out.append(Finding(Level.FAIL, "FM_NAME_XML_TAGS", "`name` must not include `<` or `>` characters."))
        if len(name) > 100:
            out.append(Finding(Level.FAIL, "FM_NAME_TOO_LONG", f"`name` too long ({len(name)} > 100)."))
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name.strip()):
            out.append(Finding(Level.WARN, "FM_NAME_STYLE", "Consider kebab-case name (lowercase + hyphens)."))

    if not isinstance(desc, str) or not desc.strip():
        out.append(Finding(Level.FAIL, "FM_DESC_MISSING", "Missing/invalid `description` (required)."))
        return out

    if "\n" in desc or "\r" in desc:
        out.append(Finding(Level.FAIL, "FM_DESC_MULTILINE", "`description` must be single-line."))
    if "<" in desc or ">" in desc:
        out.append(Finding(Level.FAIL, "FM_DESC_XML_TAGS", "`description` must not include `<` or `>` characters."))
    if len(desc) > 500:
        out.append(Finding(Level.FAIL, "FM_DESC_TOO_LONG", f"`description` too long ({len(desc)} > 500)."))
    if len(desc.strip()) < min_desc_len:
        out.append(Finding(Level.WARN, "FM_DESC_SHORT", f"Description is brief (< {min_desc_len}); expand for better discovery."))

    has_when = _has_any(desc, ["when ", "if ", "whenever ", "use this skill", "use this when", "trigger"])
    has_what = _has_any(desc, [
        "draft", "generate", "analyze", "extract", "validate", "convert", "build",
        "create", "summarize", "review", "audit", "lint", "plan", "scaffold",
        # Common action verbs that are valid "what" signals for skills in this repo.
        "deploy", "debug", "diagnose", "troubleshoot", "automate", "control",
        "install", "download", "render",
    ])
    if not (has_when and has_what):
        out.append(Finding(
            Level.FAIL,
            "FM_DESC_WHAT_WHEN",
            "Description MUST include WHAT the skill does and WHEN to use it (trigger contexts).",
            evidence=f"description: {desc.strip()}",
        ))

    # Heuristic: avoid putting step-by-step workflow text in `description`.
    # The description is primarily for discovery/selection; workflows belong in the body/references.
    workflowy_terms = [
        "step", "steps", "first", "second", "third", "then", "next", "after", "before",
        "finally", "workflow", "procedure", "checklist",
    ]
    hits = [t for t in workflowy_terms if t in desc]
    if len(hits) >= 2 or re.search(r"\b(1\)|2\)|3\)|first|second|third|then|next|finally)\b", desc):
        out.append(Finding(
            Level.WARN,
            "FM_DESC_WORKFLOWY",
            "Description looks workflow-like. Prefer outcome + trigger keywords in `description`; keep procedures in the body/references.",
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

    repo_root: Optional[Path] = None
    for base in [doc.path.parent, *doc.path.parent.parents]:
        if (base / ".git").exists():
            repo_root = base
            break

    traversal_refs = sorted(set(re.findall(r"\.\./[A-Za-z0-9._/\-]+", body)))
    unresolved_or_external: List[str] = []
    for rel in traversal_refs:
        resolved = (doc.path.parent / rel).resolve()
        if repo_root and resolved.exists() and resolved.is_relative_to(repo_root):
            continue
        unresolved_or_external.append(rel)

    if unresolved_or_external:
        sample = ", ".join(unresolved_or_external[:3])
        out.append(
            Finding(
                Level.WARN,
                "PATH_TRAVERSAL",
                "Parent traversal path(s) unresolved or outside repo root; prefer repo-relative in-repo paths.",
                evidence=sample,
            )
        )

    return out



def check_script_security(skill_dir: Path, doc: SkillDoc) -> List[Finding]:
    """
    Heuristic safety checks for script-backed skills.

    Goals:
    - catch accidental secret/env echo
    - discourage implicit network dependency
    - encourage explicit confirmation for destructive operations
    """
    out: List[Finding] = []
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists() or not scripts_dir.is_dir():
        return out

    script_files: List[Path] = []
    for ext in ("*.py", "*.sh", "*.bash", "*.zsh", "*.js", "*.ts"):
        script_files.extend(sorted(scripts_dir.glob(ext)))

    if not script_files:
        return out

    body_l = doc.body.lower()
    mentions_network = _has_any(body_l, ["network", "internet", "offline", "allow-network", "no network"])
    mentions_network_allowlist = _has_any(
        body_l,
        [
            "allowlist",
            "allowed domains",
            "allowed hosts",
            "domain allowlist",
            "host allowlist",
            "network allowlist",
        ],
    )
    mentions_confirm = _has_any(body_l, ["--confirm", "--force", "dry-run", "destructive"])

    # Patterns: keep tight to avoid false positives.
    env_echo_patterns = [
        re.compile(r"print\s*\(\s*os\.environ", re.IGNORECASE),
        re.compile(r"pprint\s*\(\s*os\.environ", re.IGNORECASE),
        re.compile(r"logging\.\w+\s*\(\s*os\.environ", re.IGNORECASE),
        re.compile(r"console\.log\s*\(\s*process\.env", re.IGNORECASE),
    ]
    secret_echo_patterns = [
        re.compile(
            r"(print|logging\.\w+|console\.log)\s*\([^)]*(os\.environ|getenv\(|process\.env)[^)]*(API_KEY|TOKEN|SECRET|PASSWORD|PRIVATE_KEY)",
            re.IGNORECASE,
        ),
        re.compile(
            r"(print|logging\.\w+|console\.log)\s*\([^)]*(API_KEY|TOKEN|SECRET|PASSWORD|PRIVATE_KEY)[^)]*(os\.environ|getenv\(|process\.env)",
            re.IGNORECASE,
        ),
    ]
    network_patterns = [
        re.compile(r"^\s*import\s+requests\b", re.MULTILINE),
        re.compile(r"^\s*from\s+requests\b", re.MULTILINE),
        re.compile(r"^\s*import\s+httpx\b", re.MULTILINE),
        re.compile(r"^\s*import\s+aiohttp\b", re.MULTILINE),
        re.compile(r"urllib\.request\.urlopen", re.IGNORECASE),
        re.compile(r"\bcurl\b", re.IGNORECASE),
        re.compile(r"\bwget\b", re.IGNORECASE),
    ]
    network_url_patterns = [
        re.compile(r"https?://[A-Za-z0-9.\-_/:%?=&#+]+", re.IGNORECASE),
    ]
    destructive_patterns = [
        re.compile(r"shutil\.rmtree", re.IGNORECASE),
        re.compile(r"\.unlink\s*\(", re.IGNORECASE),
        re.compile(r"os\.remove\s*\(", re.IGNORECASE),
        re.compile(r"os\.rmdir\s*\(", re.IGNORECASE),
        re.compile(r"\brm\s+-rf\b", re.IGNORECASE),
        re.compile(r"\bgit\s+push\b", re.IGNORECASE),
        re.compile(r"\bnpm\s+publish\b", re.IGNORECASE),
    ]
    untrusted_input_patterns = [
        re.compile(r"\bsys\.argv\b", re.IGNORECASE),
        re.compile(r"\bargparse\.ArgumentParser\b", re.IGNORECASE),
        re.compile(r"\binput\s*\(", re.IGNORECASE),
        re.compile(r"\bstdin\b", re.IGNORECASE),
        re.compile(r"\bprocess\.argv\b", re.IGNORECASE),
        re.compile(r"\breadline\s*\(", re.IGNORECASE),
    ]
    shell_sink_patterns = [
        re.compile(r"\bos\.system\s*\(", re.IGNORECASE),
        re.compile(r"\bsubprocess\.(run|Popen|call|check_output)\s*\([^\)]*shell\s*=\s*True", re.IGNORECASE | re.DOTALL),
        re.compile(r"\bchild_process\.(exec|execSync)\s*\(", re.IGNORECASE),
        re.compile(r"\bexecSync\s*\(", re.IGNORECASE),
    ]
    command_sink_patterns = [
        re.compile(r"\bsubprocess\.(run|Popen|call|check_output)\s*\(", re.IGNORECASE),
        re.compile(r"\bchild_process\.(spawn|spawnSync|exec|execSync)\s*\(", re.IGNORECASE),
        re.compile(r"\bspawn(Sync)?\s*\(", re.IGNORECASE),
    ]
    sanitizer_patterns = [
        re.compile(r"\bshlex\.quote\s*\(", re.IGNORECASE),
        re.compile(r"\bshell\s*=\s*False\b", re.IGNORECASE),
        re.compile(r"\bsubprocess\.(run|Popen|call|check_output)\s*\(\s*\[", re.IGNORECASE),
    ]

    for f in script_files:
        txt = _read_text(f)

        if any(p.search(txt) for p in env_echo_patterns):
            out.append(Finding(
                Level.FAIL,
                "SAFE_ENV_ECHO",
                "Script appears to print environment variables. Never echo env vars or secrets.",
                evidence=str(f.relative_to(skill_dir)),
            ))

        if any(p.search(txt) for p in secret_echo_patterns):
            out.append(Finding(
                Level.FAIL,
                "SAFE_SECRET_ECHO",
                "Script appears to log/print secret-like values (API_KEY/TOKEN/SECRET/PASSWORD). Redact or remove.",
                evidence=str(f.relative_to(skill_dir)),
            ))

        uses_network = any(p.search(txt) for p in network_patterns)
        if uses_network and not mentions_network:
            out.append(Finding(
                Level.WARN,
                "SAFE_NETWORK_UNDECLARED",
                "Network usage detected in scripts but SKILL.md does not explicitly describe network requirements/constraints. Default to offline; gate behind --allow-network if needed.",
                evidence=str(f.relative_to(skill_dir)),
            ))
        if uses_network and not mentions_network_allowlist:
            out.append(Finding(
                Level.WARN,
                "SAFE_NETWORK_ALLOWLIST",
                "Network usage detected in scripts without an explicit domain/host allowlist policy in SKILL.md.",
                evidence=str(f.relative_to(skill_dir)),
            ))
        if uses_network and any(p.search(txt) for p in network_url_patterns) and not mentions_network_allowlist:
            out.append(Finding(
                Level.WARN,
                "SAFE_NETWORK_URL_ALLOWLIST",
                "Hard-coded URL(s) detected in scripts; document explicit allowed domains/hosts in SKILL.md.",
                evidence=str(f.relative_to(skill_dir)),
            ))

        is_destructive = any(p.search(txt) for p in destructive_patterns)
        if is_destructive and not mentions_confirm and not _has_any(txt.lower(), ["--dry-run", "--confirm", "--force", "dry_run", "confirm", "force"]):
            out.append(Finding(
                Level.WARN,
                "SAFE_DESTRUCTIVE_GUARD",
                "Potentially destructive operations detected in scripts without an obvious dry-run/confirm guard. Prefer --dry-run default and require --confirm/--force.",
                evidence=str(f.relative_to(skill_dir)),
            ))

        has_untrusted_input = any(p.search(txt) for p in untrusted_input_patterns)
        has_shell_sink = any(p.search(txt) for p in shell_sink_patterns)
        has_command_sink = any(p.search(txt) for p in command_sink_patterns)
        has_sanitizer = any(p.search(txt) for p in sanitizer_patterns)

        if has_untrusted_input and has_shell_sink:
            out.append(Finding(
                Level.FAIL,
                "SAFE_UNTRUSTED_TO_SHELL",
                "Untrusted input source combined with shell-style command execution detected. Avoid shell mode/os.system/exec* on user-controlled input.",
                evidence=str(f.relative_to(skill_dir)),
            ))
        elif has_untrusted_input and has_command_sink and not has_sanitizer:
            out.append(Finding(
                Level.WARN,
                "SAFE_UNTRUSTED_TO_COMMAND",
                "Untrusted input appears to flow into command execution without clear sanitization/argument-list hardening.",
                evidence=str(f.relative_to(skill_dir)),
            ))

    return out


def check_prompt_injection_signals(skill_dir: Path, doc: SkillDoc, *, pi_high_fail: bool) -> List[Finding]:
    out: List[Finding] = []

    patterns, config_findings = _load_prompt_patterns(skill_dir)
    out.extend(config_findings)
    allowlist, blocklist, local_findings = _load_allow_block_patterns()
    out.extend(local_findings)
    expected_paths, context_signals, skip_binary_globs, expected_findings = _load_expected_pi_context(skill_dir)
    out.extend(expected_findings)

    def _scan(text: str, evidence: str) -> None:
        for pattern, message, severity in blocklist:
            if pattern.search(text):
                out.append(Finding(_severity_to_level(severity, fail_on_high=pi_high_fail), "PI_BLOCKLIST", f"[{severity}] {message}", evidence=evidence))

        for code, pattern, message, severity in patterns:
            if any(allow.search(evidence) for allow in allowlist):
                continue
            if _is_expected_pi_context(code, evidence, text, expected_paths, context_signals):
                continue
            if pattern.search(text):
                out.append(Finding(_severity_to_level(severity, fail_on_high=pi_high_fail), code, f"[{severity}] {message}", evidence=evidence))

    _scan(doc.raw, "SKILL.md")

    for path, is_text in _iter_scan_targets(skill_dir):
        rel_path = str(path.relative_to(skill_dir))
        # Pattern definition files contain attack strings intentionally.
        if path.name == "prompt-injection-patterns.json":
            continue
        if not is_text:
            if any(fnmatch.fnmatch(rel_path, pat) for pat in skip_binary_globs):
                continue
            out.append(Finding(
                Level.WARN,
                "PI_BINARY_ATTACHMENT",
                "Binary attachment detected; manual review required (prompt scan skipped).",
                evidence=rel_path,
            ))
            continue
        if path.name == "SKILL.md":
            continue
        _scan(_read_text(path), rel_path)

    return out


def check_security_eval_coverage(skill_dir: Path, *, require_security_evals: bool) -> List[Finding]:
    """
    Ensure eval suites include adversarial security coverage.

    Focus:
    - at least one negative (non-trigger) case
    - at least one pressure/adversarial PI case
    - at least one deterministic safety guard for high-risk commands
    """
    out: List[Finding] = []
    evals_path = skill_dir / "references" / "evals.yaml"
    if not evals_path.exists():
        return out

    try:
        obj = yaml.safe_load(evals_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        out.append(Finding(Level.WARN, "SEC_EVALS_PARSE", f"Could not parse evals.yaml for security coverage checks: {exc}"))
        return out

    if not isinstance(obj, dict) or not isinstance(obj.get("cases"), list):
        return out

    cases = [c for c in obj.get("cases", []) if isinstance(c, dict)]
    if not cases:
        return out

    pi_terms = (
        "prompt injection",
        "jailbreak",
        "ignore previous",
        "ignore system",
        "override system",
        "bypass safety",
        "exfiltrate",
        "hidden instruction",
    )
    risky_commands = ("rm -rf", "curl", "wget", "netcat", "nc", "powershell", "invoke-webrequest")

    def _contains_risky_command(text: str) -> bool:
        for command in risky_commands:
            if command == "nc":
                if re.search(r"(^|[\s;&|])nc($|[\s;&|])", text):
                    return True
                continue
            if command in text:
                return True
        return False

    has_negative = False
    has_pressure = False
    has_pi_prompt_case = False
    has_risky_command_guard = False

    for c in cases:
        category = str(c.get("category", "")).strip().lower()
        should_trigger = c.get("should_trigger")
        prompt = str(c.get("prompt", "")).lower()
        acceptance = c.get("acceptance", [])
        deterministic_checks = c.get("deterministic_checks", {})

        if category == "negative" or should_trigger is False:
            has_negative = True
        if category == "pressure":
            has_pressure = True
        if any(term in prompt for term in pi_terms):
            has_pi_prompt_case = True

        # Check deterministic forbidden commands and textual acceptance guards.
        forbidden_cmds: List[str] = []
        if isinstance(deterministic_checks, dict):
            raw_forbidden = deterministic_checks.get("forbidden_commands", [])
            if isinstance(raw_forbidden, list):
                forbidden_cmds = [str(x).lower() for x in raw_forbidden]
            elif isinstance(raw_forbidden, str):
                forbidden_cmds = [raw_forbidden.lower()]
        if any(_contains_risky_command(cmd) for cmd in forbidden_cmds):
            has_risky_command_guard = True

        if isinstance(acceptance, list):
            for a in acceptance:
                text = str(a).lower()
                if _contains_risky_command(text):
                    has_risky_command_guard = True
                    break

    missing: List[Tuple[str, str]] = []
    if not has_negative:
        missing.append(("SEC_EVALS_NEGATIVE_MISSING", "No negative/non-trigger security case detected in evals.yaml. Add `category: negative` or `should_trigger: false` coverage."))
    if not has_pressure:
        missing.append(("SEC_EVALS_PRESSURE_MISSING", "No pressure/adversarial case detected in evals.yaml. Add at least one `category: pressure` case."))
    if not has_pi_prompt_case:
        missing.append(("SEC_EVALS_PI_CASE_MISSING", "No prompt-injection/jailbreak-style prompt detected in evals.yaml. Add one adversarial PI prompt case."))
    if not has_risky_command_guard:
        missing.append(("SEC_EVALS_COMMAND_GUARD_MISSING", "No deterministic risky-command guard detected. Add forbidden command checks (e.g., curl/wget/rm -rf/netcat)."))

    level = Level.FAIL if require_security_evals else Level.WARN
    for code, message in missing:
        out.append(Finding(level, code, message, evidence="references/evals.yaml"))

    return out


def check_research_scope_focus(doc: SkillDoc) -> List[Finding]:
    out: List[Finding] = []
    corpus = f"{doc.frontmatter.get('description', '')}\n{doc.body}"
    surfaces = _research_surface_count(corpus)
    focus_signals = _focus_language_count(corpus)

    if surfaces >= 6 and focus_signals == 0:
        out.append(Finding(
            Level.WARN,
            "RESEARCH_SCOPE_OVERBUNDLED",
            "Skill/package scope looks broad across many surfaces without explicit narrowing guidance. Prefer the smallest viable package boundary first.",
            evidence=f"surfaces={surfaces}",
        ))
    elif surfaces >= 4 and focus_signals <= 1:
        out.append(Finding(
            Level.WARN,
            "RESEARCH_SCOPE_BROAD",
            "Skill/package scope may be too broad for a first pass. Add explicit guidance like 'start with 2-3 focused surfaces' or 'keep scope tight'.",
            evidence=f"surfaces={surfaces}",
        ))

    return out


def check_research_example_quality(doc: SkillDoc) -> List[Finding]:
    out: List[Finding] = []
    examples_text = _find_section_text(doc.body, ["examples", "example prompts"])
    if not examples_text:
        return out

    examples = re.findall(r"(?m)^\s*(?:[-*]|\d+\.)\s+.+$", examples_text)
    quoted_examples = re.findall(r'`[^`]{10,}`|"[^"\n]{10,}"', examples_text)
    if len(examples) + len(quoted_examples) < 2:
        out.append(Finding(
            Level.WARN,
            "RESEARCH_EXAMPLES_THIN",
            "Examples section is present but thin. Add 2-3 realistic trigger prompts or worked examples.",
            evidence="## Examples",
        ))

    realism_signals = ("when the user asks", "user says", "github", "convert", "validate", "inspect", "migrate")
    realism_hits = sum(1 for signal in realism_signals if signal in examples_text.lower())
    if realism_hits == 0:
        out.append(Finding(
            Level.WARN,
            "RESEARCH_EXAMPLES_SYNTHETIC",
            "Examples look abstract or template-like. Prefer realistic user requests and concrete workflows.",
            evidence="## Examples",
        ))

    return out


def check_research_eval_prompt_realism(doc: SkillDoc) -> List[Finding]:
    out: List[Finding] = []
    skill_dir = doc.path.parent
    evals_path = skill_dir / "references" / "evals.yaml"
    if not evals_path.exists():
        return out

    try:
        obj = yaml.safe_load(evals_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        out.append(Finding(Level.WARN, "RESEARCH_EVALS_PARSE", f"Could not parse evals.yaml for realism checks: {exc}"))
        return out

    if not isinstance(obj, dict) or not isinstance(obj.get("cases"), list):
        return out

    skill_name = str(doc.frontmatter.get("name", "")).strip().lower()
    cases = [case for case in obj["cases"] if isinstance(case, dict)]
    trigger_cases = [
        case for case in cases
        if case.get("should_trigger") is not False and str(case.get("category", "")).strip().lower() != "negative"
    ]
    if not trigger_cases:
        return out

    leaky = 0
    realistic = 0
    for case in trigger_cases:
        prompt = str(case.get("prompt", "")).strip().lower()
        if skill_name and skill_name in prompt:
            leaky += 1
        if any(token in prompt for token in ("please", "can you", "help me", "github", "convert", "validate", "build", "inspect")):
            realistic += 1

    if leaky / len(trigger_cases) > 0.5:
        out.append(Finding(
            Level.WARN,
            "RESEARCH_EVALS_LEAKY",
            "Most positive eval prompts mention the skill name directly. Prefer natural user phrasing to test real routing behavior.",
            evidence=f"leaky={leaky}/{len(trigger_cases)}",
        ))

    if realistic / len(trigger_cases) < 0.34:
        out.append(Finding(
            Level.WARN,
            "RESEARCH_EVALS_UNREALISTIC",
            "Positive eval prompts look synthetic. Rewrite more prompts as realistic user utterances.",
            evidence=f"realistic={realistic}/{len(trigger_cases)}",
        ))

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
                    if "schema_version" in obj and not isinstance(obj["schema_version"], (str, int, float)):
                        out.append(Finding(Level.FAIL, "EVALS_SCHEMA_VERSION_SHAPE", "`schema_version` must be a scalar when provided."))
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

                        # v2 optional fields (backward compatible)
                        if "id" in c and not isinstance(c["id"], str):
                            out.append(Finding(Level.FAIL, "EVALS_CASE_ID_SHAPE", f"Case #{i} `id` must be a string when provided."))
                        if "should_trigger" in c and not isinstance(c["should_trigger"], bool):
                            out.append(Finding(Level.FAIL, "EVALS_SHOULD_TRIGGER_SHAPE", f"Case #{i} `should_trigger` must be boolean when provided."))
                        if "prepend_skill" in c and not isinstance(c["prepend_skill"], bool):
                            out.append(Finding(Level.FAIL, "EVALS_PREPEND_SKILL_SHAPE", f"Case #{i} `prepend_skill` must be boolean when provided."))
                        if "output_schema" in c and not isinstance(c["output_schema"], str):
                            out.append(Finding(Level.FAIL, "EVALS_OUTPUT_SCHEMA_SHAPE", f"Case #{i} `output_schema` must be a string path when provided."))

                        if "category" in c:
                            allowed_categories = {"happy", "edge", "negative", "pressure"}
                            if not isinstance(c["category"], str) or c["category"].strip().lower() not in allowed_categories:
                                out.append(Finding(
                                    Level.FAIL,
                                    "EVALS_CATEGORY_INVALID",
                                    f"Case #{i} `category` must be one of: {', '.join(sorted(allowed_categories))}.",
                                ))

                        if "deterministic_checks" in c and not isinstance(c["deterministic_checks"], dict):
                            out.append(Finding(
                                Level.FAIL,
                                "EVALS_DETERMINISTIC_CHECKS_SHAPE",
                                f"Case #{i} `deterministic_checks` must be a mapping when provided.",
                            ))
                        if "budgets" in c and not isinstance(c["budgets"], dict):
                            out.append(Finding(
                                Level.FAIL,
                                "EVALS_BUDGETS_SHAPE",
                                f"Case #{i} `budgets` must be a mapping when provided.",
                            ))
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


def _lvl_name(level: Level) -> str:
    return {Level.INFO: "INFO", Level.WARN: "WARN", Level.FAIL: "FAIL"}[level]


def _utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _build_json_payload(doc: SkillDoc, findings: Sequence[Finding], *, failed: bool) -> Dict[str, Any]:
    exit_code = 2 if failed else 0
    return {
        "schema_version": "1.1",
        "tool": "skill_gate",
        "generated_at": _utc_now_iso(),
        "skill": str(doc.path),
        "skill_path": str(doc.path),
        "name": doc.frontmatter.get("name"),
        "decision": "fail" if failed else "pass",
        "exit_code": exit_code,
        "failed": failed,
        "findings": [
            {"level": _lvl_name(f.level), "code": f.code, "message": f.message, "evidence": f.evidence}
            for f in findings
        ],
    }


def _find_repo_root(path: Path) -> Optional[Path]:
    resolved = path.expanduser().resolve()
    current = resolved if resolved.is_dir() else resolved.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def _sarif_artifact_uri(path: Path) -> str:
    resolved = path.expanduser().resolve()
    repo_root = _find_repo_root(resolved)
    if repo_root is not None:
        try:
            return resolved.relative_to(repo_root).as_posix()
        except ValueError:
            pass
    cwd = Path.cwd().resolve()
    try:
        return resolved.relative_to(cwd).as_posix()
    except ValueError:
        return resolved.name


def _build_sarif_payload(doc: SkillDoc, findings: Sequence[Finding], *, failed: bool) -> Dict[str, Any]:
    rules = []
    seen_codes = set()
    for finding in findings:
        if finding.code in seen_codes:
            continue
        seen_codes.add(finding.code)
        level = _lvl_name(finding.level).lower()
        rules.append(
            {
                "id": finding.code,
                "name": finding.code,
                "shortDescription": {"text": finding.message},
                "properties": {"defaultSeverity": level},
            }
        )
    results = []
    uri = _sarif_artifact_uri(doc.path)
    for finding in findings:
        level = _lvl_name(finding.level).lower()
        results.append(
            {
                "ruleId": finding.code,
                "level": {"info": "note", "warn": "warning", "fail": "error"}[level],
                "message": {"text": finding.message + (f" | {finding.evidence}" if finding.evidence else "")},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": uri},
                        }
                    }
                ],
            }
        )
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "skill_gate",
                        "informationUri": "https://github.com/openai/skills",
                        "rules": rules,
                    }
                },
                "invocations": [{"executionSuccessful": not failed}],
                "results": results,
            }
        ],
    }


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
    require_security_evals: bool,
    pi_high_fail: bool,
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
    findings.extend(check_script_security(skill_dir, doc))
    findings.extend(check_prompt_injection_signals(skill_dir, doc, pi_high_fail=pi_high_fail))
    findings.extend(check_security_eval_coverage(skill_dir, require_security_evals=require_security_evals))
    findings.extend(check_research_scope_focus(doc))
    findings.extend(check_research_example_quality(doc))
    findings.extend(check_research_eval_prompt_realism(doc))
    findings.extend(check_contract_and_evals(skill_dir, require_contract=require_contract, require_evals=require_evals))
    findings.extend(check_repo_references(doc))

    findings.sort(key=lambda f: (-int(f.level), f.code))
    return findings


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="skill_gate.py", description="Gold-standard gate for Codex SKILL.md quality.")
    p.add_argument("path", help="Path to a skill directory or SKILL.md file.")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--output", default=None, help="Optional path to write the rendered report.")
    p.add_argument("--sarif-out", default=None, help="Optional path to write SARIF 2.1.0 findings for CI/code scanning.")

    p.add_argument("--max-lines", type=int, default=360, help="Max allowed lines in SKILL.md (default: 360).")
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
    p.add_argument(
        "--require-security-evals",
        action="store_true",
        help="Fail when adversarial security eval coverage is missing (negative/pressure/PI/command-guard checks).",
    )
    p.add_argument(
        "--pi-high-fail",
        action="store_true",
        help="Treat high-severity prompt-injection pattern matches as FAIL instead of WARN.",
    )

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
        require_security_evals=bool(args.require_security_evals),
        pi_high_fail=bool(args.pi_high_fail),
    )

    failed = any(f.level == Level.FAIL for f in findings)

    rendered = ""
    if args.format == "json":
        payload = _build_json_payload(doc, findings, failed=failed)
        rendered = json.dumps(payload, indent=2, ensure_ascii=False)
    else:
        lines = [f"Skill: {doc.frontmatter.get('name', 'unknown')}", f"Path:  {doc.path}", ""]
        for f in findings:
            ev = f" | {f.evidence}" if f.evidence else ""
            lines.append(f"{_lvl_name(f.level)} {f.code}: {f.message}{ev}")
        lines.extend(["", f"RESULT: {'FAIL' if failed else 'PASS'}"])
        rendered = "\n".join(lines)

    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + ("\n" if not rendered.endswith("\n") else ""), encoding="utf-8")

    if args.sarif_out:
        sarif_path = Path(args.sarif_out).expanduser().resolve()
        sarif_path.parent.mkdir(parents=True, exist_ok=True)
        sarif_payload = _build_sarif_payload(doc, findings, failed=failed)
        sarif_path.write_text(json.dumps(sarif_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(rendered)

    return 2 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
