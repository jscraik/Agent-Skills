#!/usr/bin/env python3
"""
skill_gate.py

Gold-standard gate for Codex agent skills.

Enforces:
- Codex frontmatter validity + selection quality (WHAT + WHEN)
- SDK/package-required fields as failures; house-style SKILL.md sections as warnings
- Progressive disclosure budgets (MUST)
- Contract + eval coverage (MUST)
- Basic safety hygiene (redaction language; fail-fast gating)

Usage:
  python Plugins/skill-factory/scripts/skill-builder/skill_gate.py <path/to/skill-dir-or-SKILL.md>

Exit codes:
  0  pass
  1  parsing/IO error
  2  gate failed (one or more FAIL findings)

Recommended CI:
  python Plugins/skill-factory/scripts/skill-builder/skill_gate.py Plugins/<plugin>/skills/<skill-name> --format json
"""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import os
import re
import sys
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))


def _reexec_gate_facade(preferred: Path, env: dict[str, str]) -> None:
    facade_path = _SCRIPT_DIR / "skill_gate.py"
    os.execve(str(preferred), [str(preferred), str(facade_path), *sys.argv[1:]], env)


try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    preferred = Path.home() / ".venvs" / "pyyaml" / "bin" / "python"
    already_reexec = os.environ.get("SKILL_CREATOR_PYYAML_REEXEC") == "1"
    if preferred.exists() and not already_reexec:
        _reexec_gate_facade(preferred, {**os.environ, "SKILL_CREATOR_PYYAML_REEXEC": "1"})

    sys.stderr.write(
        "ERROR: PyYAML is required to run skill_gate.py.\n\n"
        "Fix (recommended):\n"
        "  python Plugins/skill-factory/scripts/skill-builder/skill_gate.py <path/to/skill-dir-or-SKILL.md>\n\n"
        "Notes:\n"
        "  - Do not use Skills/skill-builder/.venv/bin/python (this repo does not ship that venv).\n"
        "  - If ~/.venvs/pyyaml doesn't exist, create a venv with PyYAML installed."
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


from yaml_frontmatter import parse_frontmatter as _parse_frontmatter_shared  # noqa: E402  # type: ignore[import]
from yaml_frontmatter import read_text as _read_text  # noqa: E402  # type: ignore[import]
from yaml_frontmatter import resolve_skill_md_path as _resolve_skill_md_path  # noqa: E402  # type: ignore[import]
from eval_signal_contract import (  # noqa: E402
    EXPECTED_SIGNAL_BUDGET_KEY,
    EXPECTED_SIGNAL_KEYS,
    parse_min_expected_signal_score,
)


def load_skill(path_like: str, strict_line1: bool) -> SkillDoc:
    path = _resolve_skill_md_path(path_like)
    if not path.exists():
        raise FileNotFoundError(f"SKILL.md not found at: {path}")

    raw = _read_text(path)
    fm, body, fm_start, fm_end = _parse_frontmatter_shared(raw, strict_line1=strict_line1)
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


# Space and colon variants support case-insensitive `contains foo` and `contains: foo` shorthand matching.
_ACCEPTANCE_STRING_PREFIXES = ("contains ", "not_contains ", "regex ", "not_regex ", "contains:", "not_contains:", "regex:", "not_regex:")
_SCAN_IGNORED_NAMES = frozenset({
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini",
})


def _is_bare_acceptance_string(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    text = value.strip()
    if not text:
        return False
    return not text.lower().startswith(_ACCEPTANCE_STRING_PREFIXES)


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


_CANONICAL_SKILLS_SDK_SECTION_ORDER: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("when_to_use", "When To Use", ("when to use", "usage", "triggers", "invocation")),
    ("inputs", "Inputs", ("inputs", "preconditions", "assumptions", "requirements")),
    ("outputs", "Outputs", ("outputs", "output format", "deliverables", "result")),
    ("workflow", "Workflow", ("workflow", "procedure", "steps", "process")),
    ("failure_mode", "Failure Mode", (
        "failure mode",
        "failure modes",
        "failure handling",
        "failure behavior",
        "repair behavior",
        "repair loop",
        "stopping conditions",
        "rollback path",
        "handoff rules",
    )),
    ("validation", "Validation", ("validation", "checks", "verify", "acceptance", "gates")),
    ("references", "References", ("references", "progressive disclosure")),
)


def _matches_section_alias(title: str, aliases: Sequence[str]) -> bool:
    normalized = re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()
    for alias in aliases:
        normalized_alias = re.sub(r"[^a-z0-9]+", " ", alias.lower()).strip()
        if normalized == normalized_alias or normalized_alias in normalized:
            return True
    return False


def check_canonical_header_order(doc: SkillDoc) -> List[Finding]:
    out: List[Finding] = []
    h2s = _h2_titles(doc.body)
    first_positions: Dict[str, Tuple[int, str, str]] = {}

    for index, title in enumerate(h2s):
        for key, canonical, aliases in _CANONICAL_SKILLS_SDK_SECTION_ORDER:
            if key not in first_positions and _matches_section_alias(title, aliases):
                first_positions[key] = (index, title, canonical)
                break

    seen: List[Tuple[str, str, int]] = []
    previous_index = -1
    previous_canonical = ""
    for key, canonical, _aliases in _CANONICAL_SKILLS_SDK_SECTION_ORDER:
        position = first_positions.get(key)
        if position is None:
            continue
        index, actual_title, _ = position
        if index < previous_index:
            actual_order = " > ".join(title for _key, title, _index in sorted(seen + [(key, actual_title, index)], key=lambda item: item[2]))
            expected_order = " > ".join(label for _key, label, _aliases in _CANONICAL_SKILLS_SDK_SECTION_ORDER if _key in first_positions)
            out.append(Finding(
                Level.FAIL,
                "SEC_CANONICAL_HEADER_ORDER",
                (
                    f"SKILL.md headers must follow the canonical Skills SDK order. "
                    f"'{actual_title}' appears before '{previous_canonical}'."
                ),
                evidence=f"actual: {actual_order}; expected: {expected_order}",
            ))
            return out
        previous_index = index
        previous_canonical = canonical
        seen.append((key, actual_title, index))

    return out


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


_TEXT_EXTENSIONS = frozenset({
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
})


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
    except (OSError, json.JSONDecodeError, re.error, ValueError) as exc:
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
        except (OSError, json.JSONDecodeError, re.error, ValueError) as exc:
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
        if path.name in _SCAN_IGNORED_NAMES:
            continue
        if ".git" in path.parts:
            continue
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
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
    # Legacy Skill Builder package layout retained for archived fixtures and
    # old evidence bundles. New skills should use skill-local references/ and scripts/.
    "Infrastructure/references/evals*.yaml",
    "Infrastructure/references/evals-v2-migration.md",
    "Infrastructure/references/destructive-commands.rules",
    "Infrastructure/references/api-security.md",
    "Infrastructure/references/best-practices.md",
    "Infrastructure/references/core-principles.md",
    "Infrastructure/references/composability.md",
    "Infrastructure/references/extended.md",
    "Infrastructure/references/governance-and-style.md",
    "Infrastructure/references/philosophy-patterns.md",
    "Infrastructure/references/security-hardening.md",
    "Infrastructure/references/prompt-injection-expected-context.json",
    "Infrastructure/scripts/skill_gate.py",
    "Infrastructure/scripts/openclaw_skill_guard.py",
    "Infrastructure/scripts/recursive_skill_loop.py",
    "Infrastructure/scripts/generate_pressure_tests.py",
    "Infrastructure/scripts/migrate_evals_v2.py",
    "Infrastructure/scripts/run_skill_evals.py",
    "Infrastructure/scripts/run_skill_graph_smoke.py",
    "Infrastructure/scripts/test_*.py",
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
__all__ = [name for name in globals() if not name.startswith("__")]
