#!/usr/bin/env python3
"""
audit_codex_home.py

Generate a dated Markdown audit report for a Codex home directory.

Safety:
- Never print secrets; do not output .env contents, auth.json, or environment values.
- Prefer metadata and small excerpts; avoid dumping large files.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple


MOJIBAKE_SIGNALS: Sequence[str] = (
    "â€”",  # em dash
    "â†’",  # arrow
    "â€",   # generic
)


@dataclass(frozen=True)
class Finding:
    severity: str  # HIGH | MED | LOW
    title: str
    detail: str


@dataclass(frozen=True)
class InstructionFileSetting:
    key: str
    raw_path: str
    profile_name: Optional[str] = None


def _read_text(path: Path, *, limit_chars: int = 200_000) -> str:
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raw = path.read_text(encoding="utf-8", errors="replace")
    return raw[:limit_chars]


def _is_nonempty(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        return bool(path.read_text(encoding="utf-8").strip())
    except UnicodeDecodeError:
        return bool(path.read_text(encoding="utf-8", errors="replace").strip())


def _parse_config_toml(config_text: str) -> Tuple[Optional[dict], Optional[str]]:
    try:
        return tomllib.loads(config_text), None
    except tomllib.TOMLDecodeError as exc:
        return None, str(exc)


def _detect_code_fence_wrapping(text: str) -> bool:
    stripped = text.lstrip()
    return stripped.startswith("```")


def _contains_any(text: str, needles: Sequence[str]) -> bool:
    return any(n in text for n in needles)


def _rules_files(codex_home: Path) -> List[Path]:
    rules_dir = codex_home / "rules"
    if not rules_dir.exists():
        return []
    return sorted([p for p in rules_dir.glob("*.rules") if p.is_file()])


def _scan_rules_for_bypass(rules_text: str) -> List[str]:
    """
    Heuristic: look for allow rules that wrap potentially destructive operations inside zsh -lc "...".
    """
    hits: List[str] = []
    # Catch patterns like: pattern=["zsh","-lc","...rm -rf ..."], decision="allow" (or decision omitted)
    for m in re.finditer(r'prefix_rule\(\s*.*?\)\s*', rules_text, flags=re.DOTALL):
        block = m.group(0)
        if "pattern" not in block:
            continue
        if re.search(r'pattern\s*=\s*\[\s*"zsh"\s*,\s*"-lc"\s*,', block) and "rm -rf" in block:
            if re.search(r'decision\s*=\s*"allow"\s*', block) or "decision" not in block:
                # Keep a single-line excerpt for the report.
                excerpt = re.sub(r"\s+", " ", block).strip()
                hits.append(excerpt[:300] + ("…" if len(excerpt) > 300 else ""))
    return hits


def _rules_has_forbid_grep(all_rules_text: str) -> bool:
    """
    Heuristic match: a rule that forbids grep/egrep/fgrep.

    Supports both:
    - pattern = ["grep", ...]
    - pattern = [["grep", "egrep", "fgrep"], ...]
    """
    has_grep_pattern = bool(
        re.search(r'pattern\s*=\s*\[\s*"grep"\s*[,|\]]', all_rules_text)
        or re.search(r'pattern\s*=\s*\[\s*\[\s*"grep"\s*,', all_rules_text)
    )
    has_forbidden = bool(re.search(r'decision\s*=\s*"forbidden"', all_rules_text))
    return has_grep_pattern and has_forbidden


def _rules_has_prompt_find(all_rules_text: str) -> bool:
    return bool(re.search(r'pattern\s*=\s*\[\s*"find"\s*[,|\]]', all_rules_text) and re.search(r'decision\s*=\s*"prompt"', all_rules_text))


def _scan_hook_command_risks(command: str) -> List[str]:
    hits: List[str] = []
    if "rm -rf" in command:
        hits.append("contains `rm -rf`")
    if "git reset --hard" in command:
        hits.append("contains `git reset --hard`")
    if re.search(r"curl\b[\s\S]{0,120}\|\s*(sh|bash)\b", command):
        hits.append("pipes `curl` to a shell")
    if re.search(r"wget\b[\s\S]{0,120}\|\s*(sh|bash)\b", command):
        hits.append("pipes `wget` to a shell")
    return hits


def _audit_hooks_file(findings: List[Finding], *, codex_home: Path) -> None:
    hooks_path = codex_home / "hooks.json"
    if not hooks_path.exists():
        return

    hooks_text = _read_text(hooks_path, limit_chars=200_000)
    try:
        parsed = json.loads(hooks_text)
    except json.JSONDecodeError as exc:
        findings.append(Finding(
            severity="HIGH",
            title="hooks.json is invalid JSON",
            detail=f"{_safe_rel(hooks_path, codex_home)} could not be parsed: {exc}",
        ))
        return

    if not isinstance(parsed, dict):
        findings.append(Finding(
            severity="HIGH",
            title="hooks.json does not contain a top-level object",
            detail=f"{_safe_rel(hooks_path, codex_home)} should parse to an object with a `hooks` field.",
        ))
        return

    hooks = parsed.get("hooks", {})
    if not isinstance(hooks, dict):
        findings.append(Finding(
            severity="HIGH",
            title="hooks.json has a non-object hooks field",
            detail=f"{_safe_rel(hooks_path, codex_home)} sets `hooks` to a non-object value, so Codex cannot discover handlers.",
        ))
        return

    supported_events = {"SessionStart", "Stop"}
    unknown_events = sorted(k for k in hooks.keys() if k not in supported_events)
    if unknown_events:
        findings.append(Finding(
            severity="LOW",
            title="hooks.json contains unknown hook events",
            detail=(
                f"{_safe_rel(hooks_path, codex_home)} defines unsupported event keys: {', '.join(unknown_events)}. "
                "Current Codex hook discovery only loads `SessionStart` and `Stop` groups."
            ),
        ))

    for event_name in ("SessionStart", "Stop"):
        groups = hooks.get(event_name, [])
        if not isinstance(groups, list):
            findings.append(Finding(
                severity="MED",
                title=f"hooks.json {event_name} entry is not a list",
                detail=(
                    f"{_safe_rel(hooks_path, codex_home)} sets hooks.{event_name} to a non-list value, "
                    "so Codex cannot iterate those handlers."
                ),
            ))
            continue

        for idx, group in enumerate(groups, start=1):
            if not isinstance(group, dict):
                findings.append(Finding(
                    severity="MED",
                    title=f"hooks.json {event_name} group is not an object",
                    detail=f"{_safe_rel(hooks_path, codex_home)} has a non-object matcher group at hooks.{event_name}[{idx}].",
                ))
                continue

            matcher = group.get("matcher")
            if matcher is not None:
                if not isinstance(matcher, str):
                    findings.append(Finding(
                        severity="MED",
                        title=f"hooks.json {event_name} matcher is not a string",
                        detail=f"{_safe_rel(hooks_path, codex_home)} uses a non-string matcher at hooks.{event_name}[{idx}].matcher.",
                    ))
                else:
                    try:
                        re.compile(matcher)
                    except re.error as exc:
                        findings.append(Finding(
                            severity="MED",
                            title=f"hooks.json {event_name} matcher is invalid",
                            detail=(
                                f"{_safe_rel(hooks_path, codex_home)} has an invalid regex matcher at hooks.{event_name}[{idx}]: "
                                f"{exc}. Codex skips groups with invalid matchers."
                            ),
                        ))

            handlers = group.get("hooks", [])
            if not isinstance(handlers, list):
                findings.append(Finding(
                    severity="MED",
                    title=f"hooks.json {event_name} handlers are not a list",
                    detail=f"{_safe_rel(hooks_path, codex_home)} uses a non-list hooks array at hooks.{event_name}[{idx}].hooks.",
                ))
                continue

            for handler_idx, handler in enumerate(handlers, start=1):
                location = f"hooks.{event_name}[{idx}].hooks[{handler_idx}]"
                if not isinstance(handler, dict):
                    findings.append(Finding(
                        severity="MED",
                        title="hooks.json handler is not an object",
                        detail=f"{_safe_rel(hooks_path, codex_home)} has a non-object handler at {location}.",
                    ))
                    continue

                handler_type = handler.get("type")
                if handler_type == "command":
                    command = handler.get("command")
                    if not isinstance(command, str) or not command.strip():
                        findings.append(Finding(
                            severity="MED",
                            title="hooks.json command hook is empty",
                            detail=(
                                f"{_safe_rel(hooks_path, codex_home)} defines an empty command hook at {location}. "
                                "Current Codex discovery skips empty hook commands."
                            ),
                        ))
                        continue

                    if handler.get("async") is True:
                        findings.append(Finding(
                            severity="MED",
                            title="hooks.json async command hook is unsupported",
                            detail=(
                                f"{_safe_rel(hooks_path, codex_home)} marks {location} as async. "
                                "Current Codex discovery skips async hooks."
                            ),
                        ))

                    risk_hits = _scan_hook_command_risks(command)
                    if risk_hits:
                        findings.append(Finding(
                            severity="HIGH",
                            title="hooks.json contains a risky auto-run command",
                            detail=(
                                f"{_safe_rel(hooks_path, codex_home)} defines `{command}` at {location}; "
                                f"it {' and '.join(risk_hits)}. Hooks run automatically, so destructive or bootstrap-style shell commands need extra scrutiny."
                            ),
                        ))

                elif handler_type == "prompt":
                    findings.append(Finding(
                        severity="MED",
                        title="hooks.json prompt hook is unsupported",
                        detail=(
                            f"{_safe_rel(hooks_path, codex_home)} defines a prompt hook at {location}. "
                            "Current Codex discovery skips prompt hooks."
                        ),
                    ))
                elif handler_type == "agent":
                    findings.append(Finding(
                        severity="MED",
                        title="hooks.json agent hook is unsupported",
                        detail=(
                            f"{_safe_rel(hooks_path, codex_home)} defines an agent hook at {location}. "
                            "Current Codex discovery skips agent hooks."
                        ),
                    ))
                else:
                    findings.append(Finding(
                        severity="MED",
                        title="hooks.json handler type is missing or unknown",
                        detail=(
                            f"{_safe_rel(hooks_path, codex_home)} uses handler type `{handler_type}` at {location}. "
                            "Current Codex hooks expect `command`, `prompt`, or `agent`."
                        ),
                    ))


def _normalize_paragraph(p: str) -> str:
    s = p.strip()
    s = re.sub(r"\s+", " ", s)
    return s


def _paragraph_hashes(text: str, *, min_len: int = 220) -> List[Tuple[str, str]]:
    """
    Return (sha1, paragraph_text) for paragraphs above min_len chars.
    """
    paras = re.split(r"\n\s*\n", text)
    out: List[Tuple[str, str]] = []
    for p in paras:
        n = _normalize_paragraph(p)
        if len(n) < min_len:
            continue
        # ignore pure headings-ish blocks
        if n.startswith("#") or n.startswith("---"):
            continue
        h = hashlib.sha1(n.encode("utf-8", errors="ignore")).hexdigest()
        out.append((h, n))
    return out


def _duplication_report(files: Sequence[Path]) -> List[Tuple[str, List[Path], str]]:
    """
    Return list of (hash, [paths], sample_text) for duplicated paragraphs.
    """
    index: dict[str, List[Tuple[Path, str]]] = {}
    for f in files:
        if not f.exists():
            continue
        text = _read_text(f)
        for h, para in _paragraph_hashes(text):
            index.setdefault(h, []).append((f, para))

    dups: List[Tuple[str, List[Path], str]] = []
    for h, items in index.items():
        paths = sorted({p for (p, _) in items})
        if len(paths) >= 2:
            sample = items[0][1]
            dups.append((h, paths, sample))

    # Sort by number of files involved, descending.
    dups.sort(key=lambda t: (-len(t[1]), -len(t[2])))
    return dups[:10]


def _safe_rel(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def _resolve_instruction_path(raw_path: str, codex_home: Path) -> Tuple[Optional[Path], Optional[Path]]:
    expanded = Path(raw_path).expanduser()
    if expanded.is_absolute():
        return expanded, None
    return None, (codex_home / expanded)


def _add_instruction_file_findings(
    findings: List[Finding],
    *,
    codex_home: Path,
    setting: InstructionFileSetting,
) -> None:
    setting_label = setting.key
    if setting.profile_name:
        setting_label = f'profiles.{setting.profile_name}.{setting.key}'

    resolved_path, home_relative_hint = _resolve_instruction_path(setting.raw_path, codex_home)
    if resolved_path is None:
        detail = (
            f'{setting_label} uses the relative path "{setting.raw_path}". Current Codex builds resolve '
            "relative instruction paths against the effective working directory, not CODEX_HOME, so a home audit "
            "cannot verify the active file statically. Prefer an absolute path or `~/...` for durable global config."
        )
        if home_relative_hint is not None:
            if home_relative_hint.exists():
                detail += (
                    f" A likely intended home-relative file exists at `{home_relative_hint}`."
                )
            else:
                detail += (
                    f" No file exists at the likely home-relative path `{home_relative_hint}`."
                )
        findings.append(Finding(
            severity="MED",
            title=f"{setting_label} uses a relative path",
            detail=detail,
        ))
        return

    if not resolved_path.exists():
        findings.append(Finding(
            severity="HIGH",
            title=f"{setting_label} points to a missing file",
            detail=f'{setting_label}="{setting.raw_path}" resolves to `{resolved_path}`, but that path does not exist.',
        ))
        return

    mif_text = _read_text(resolved_path, limit_chars=50_000)
    if _detect_code_fence_wrapping(mif_text):
        findings.append(Finding(
            severity="MED",
            title=f"{setting_label} is wrapped in a code fence",
            detail=f"`{resolved_path}` starts with ```; remove the outer code fence so the content is treated as instructions.",
        ))
    if _contains_any(mif_text, MOJIBAKE_SIGNALS):
        findings.append(Finding(
            severity="MED",
            title=f"{setting_label} contains mojibake",
            detail=f"`{resolved_path}` contains one or more mojibake sequences: {', '.join(MOJIBAKE_SIGNALS)}. Normalize to ASCII or correct UTF-8.",
        ))


def generate_report(*, codex_home: Path, out_dir: Path) -> Tuple[Path, List[Finding], List[str]]:
    findings: List[Finding] = []
    blockers: List[str] = []

    # 1) Instruction chain hazards
    agents_override = codex_home / "AGENTS.override.md"
    agents_md = codex_home / "AGENTS.md"
    if _is_nonempty(agents_override):
        findings.append(Finding(
            severity="HIGH",
            title="AGENTS.override.md shadows AGENTS.md globally",
            detail=(
                f"{_safe_rel(agents_override, codex_home)} is non-empty. Codex loads the first non-empty "
                "global instructions file at CODEX_HOME, so AGENTS.md is ignored while the override exists. "
                "Recommendation: rename override to a break-glass template and consolidate durable guidance into AGENTS.md."
            ),
        ))

    # 2) config.toml + global instructions
    config_path = codex_home / "config.toml"
    config_text = _read_text(config_path) if config_path.exists() else ""
    top_level_instruction = None
    default_profile = None
    profile_instruction = None
    deprecated_top_level_instruction = None
    deprecated_profile_instruction = None
    if not config_text:
        blockers.append("Missing config.toml")
        findings.append(Finding(
            severity="HIGH",
            title="Missing config.toml",
            detail=f"{_safe_rel(config_path, codex_home)} not found; cannot audit model_instructions_file or profile defaults.",
        ))
    else:
        config_data, config_error = _parse_config_toml(config_text)
        if config_error is not None:
            blockers.append("Invalid config.toml")
            findings.append(Finding(
                severity="HIGH",
                title="config.toml is invalid TOML",
                detail=f"{_safe_rel(config_path, codex_home)} could not be parsed: {config_error}",
            ))
            config_data = {}

        profiles_table = config_data.get("profiles") if isinstance(config_data, dict) else {}
        if not isinstance(profiles_table, dict):
            profiles_table = {}

        top_level_mif = config_data.get("model_instructions_file") if isinstance(config_data.get("model_instructions_file"), str) else None
        if top_level_mif:
            top_level_instruction = InstructionFileSetting(
                key="model_instructions_file",
                raw_path=top_level_mif,
            )
            _add_instruction_file_findings(findings, codex_home=codex_home, setting=top_level_instruction)

        deprecated_top_level = config_data.get("experimental_instructions_file") if isinstance(config_data.get("experimental_instructions_file"), str) else None
        if deprecated_top_level:
            deprecated_top_level_instruction = InstructionFileSetting(
                key="experimental_instructions_file",
                raw_path=deprecated_top_level,
            )
            findings.append(Finding(
                severity="MED",
                title="Deprecated experimental_instructions_file is still configured",
                detail=(
                    'config.toml still uses `experimental_instructions_file`. March 2026 Codex docs mark that key deprecated; '
                    "rename it to `model_instructions_file`."
                ),
            ))

        default_profile = config_data.get("profile") if isinstance(config_data.get("profile"), str) else None
        if default_profile:
            profile_table = profiles_table.get(default_profile)
            if not isinstance(profile_table, dict):
                profile_table = {}

            profile_mif = profile_table.get("model_instructions_file") if isinstance(profile_table.get("model_instructions_file"), str) else None
            if profile_mif:
                profile_instruction = InstructionFileSetting(
                    key="model_instructions_file",
                    raw_path=profile_mif,
                    profile_name=default_profile,
                )
                _add_instruction_file_findings(findings, codex_home=codex_home, setting=profile_instruction)

            deprecated_profile = profile_table.get("experimental_instructions_file") if isinstance(profile_table.get("experimental_instructions_file"), str) else None
            if deprecated_profile:
                deprecated_profile_instruction = InstructionFileSetting(
                    key="experimental_instructions_file",
                    raw_path=deprecated_profile,
                    profile_name=default_profile,
                )
                findings.append(Finding(
                    severity="MED",
                    title="Default profile still uses deprecated experimental_instructions_file",
                    detail=(
                        f'profiles.{default_profile}.experimental_instructions_file is set. March 2026 Codex docs mark that key deprecated; '
                        "rename it to `model_instructions_file`."
                    ),
                ))

        if top_level_instruction and profile_instruction and top_level_instruction.raw_path != profile_instruction.raw_path:
            findings.append(Finding(
                severity="LOW",
                title="Default profile overrides top-level model_instructions_file",
                detail=(
                    f'Top-level `model_instructions_file` points to "{top_level_instruction.raw_path}", but the default profile '
                    f'`{default_profile}` overrides it with "{profile_instruction.raw_path}". Audit and cleanup should focus on the '
                    "default-profile file because it is the active configuration for new sessions."
                ),
            ))

        sandbox_mode = None
        sandbox_mode_source = None
        if default_profile:
            profile_table = profiles_table.get(default_profile)
            if not isinstance(profile_table, dict):
                profile_table = {}
            sandbox_mode = profile_table.get("sandbox_mode") if isinstance(profile_table.get("sandbox_mode"), str) else None
            if sandbox_mode:
                sandbox_mode_source = f'profiles.{default_profile}.sandbox_mode'
        if sandbox_mode is None:
            sandbox_mode = config_data.get("sandbox_mode") if isinstance(config_data.get("sandbox_mode"), str) else None
            if sandbox_mode:
                sandbox_mode_source = "sandbox_mode"

        if sandbox_mode == "danger-full-access":
            findings.append(Finding(
                severity="MED",
                title="Active sandbox mode uses danger-full-access",
                detail=(
                    f'config.toml resolves the active sandbox mode from `{sandbox_mode_source}` to "danger-full-access". '
                    "This increases blast radius for accidental commands. Consider defaulting to workspace-write and opting into danger-full-access only when needed."
                ),
            ))

        if "127.0.0.1:4318" in config_text:
            findings.append(Finding(
                severity="LOW",
                title="OTel exporter configured to localhost (may spam connection errors)",
                detail=(
                    "config.toml references http://127.0.0.1:4318 for OTel logs/traces. "
                    "If no collector is running, Codex will log connection refused errors. Consider disabling exporter or running a collector."
                ),
            ))

    # 3) Rules scan
    rules = _rules_files(codex_home)
    if not rules:
        blockers.append("Missing rules directory or no .rules files")
        findings.append(Finding(
            severity="HIGH",
            title="Missing rules directory or no .rules files",
            detail=f"{_safe_rel(codex_home / 'rules', codex_home)} missing or empty. Rules are the best place to enforce recurring guardrails (grep/find/deps/etc.).",
        ))
    else:
        all_rules_text = "\n\n".join(_read_text(p) for p in rules)
        bypass_hits: List[str] = []
        for p in rules:
            bypass_hits.extend(_scan_rules_for_bypass(_read_text(p)))
        if bypass_hits:
            findings.append(Finding(
                severity="HIGH",
                title="Potential rules bypass: allow-rules wrapping rm -rf inside zsh -lc",
                detail=(
                    "Found allow rules that include `pattern=[\"zsh\",\"-lc\", \"...rm -rf...\"]`. "
                    "Shell wrappers can hide multiple actions if splitting fails; prefer prompting or removing these allow rules.\n"
                    "Examples:\n- " + "\n- ".join(bypass_hits[:5])
                ),
            ))

        if not _rules_has_forbid_grep(all_rules_text):
            findings.append(Finding(
                severity="MED",
                title="No explicit forbid rule for grep",
                detail="Add a forbidden rule for `grep` (and optionally egrep/fgrep) with justification 'Use rg'.",
            ))
        if not _rules_has_prompt_find(all_rules_text):
            findings.append(Finding(
                severity="LOW",
                title="No explicit prompt rule for find",
                detail="Consider prompting for `find` to encourage fd/rg --files, since find is often slow/noisy in repos.",
            ))

    has_guidance_source = (
        _is_nonempty(agents_override)
        or _is_nonempty(agents_md)
        or top_level_instruction is not None
        or profile_instruction is not None
        or deprecated_top_level_instruction is not None
        or deprecated_profile_instruction is not None
    )
    if not has_guidance_source:
        blockers.append("No global guidance source detected")
        findings.append(Finding(
            severity="HIGH",
            title="No global guidance source detected",
            detail=(
                "Found no non-empty `AGENTS.override.md`, no non-empty `AGENTS.md`, and no configured "
                "`model_instructions_file`. March 2026 Codex guidance expects at least one canonical global "
                "instruction source in CODEX_HOME."
            ),
        ))

    # 4) Duplication / drift
    dup_files = [
        codex_home / "AGENTS.md",
        codex_home / "AGENTS.override.md",
        codex_home / "USER_PROFILE.md",
        codex_home / "USER_PROFILE.detail.md",
    ]
    dups = _duplication_report([p for p in dup_files if p.exists()])
    if dups:
        top = dups[0]
        findings.append(Finding(
            severity="LOW",
            title="Duplication detected across profile/instructions files",
            detail=(
                "Detected repeated paragraphs across multiple files, increasing drift risk. "
                "Recommendation: choose a canonical owner for each block (USER_PROFILE vs AGENTS vs instructions/*).\n"
                f"Top duplicate appears in: {', '.join(_safe_rel(p, codex_home) for p in top[1])}"
            ),
        ))

    # sort: HIGH first
    order = {"HIGH": 0, "MED": 1, "LOW": 2}
    findings.sort(key=lambda f: (order.get(f.severity, 9), f.title))

    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    report_path = out_dir / f"{stamp}.md"

    report_lines: List[str] = []
    report_lines.append("# Codex Home Audit Report")
    report_lines.append("")
    report_lines.append(f"- Timestamp: {dt.datetime.now().isoformat(timespec='seconds')}")
    report_lines.append(f"- Codex home: `{codex_home}`")
    report_lines.append(f"- Report path: `{report_path}`")
    report_lines.append("")

    report_lines.append("## Summary")
    report_lines.append("")
    if blockers:
        report_lines.append(f"- Blockers detected: {len(blockers)}")
        for blocker in blockers:
            report_lines.append(f"  - {blocker}")
    if not findings:
        report_lines.append("- No findings (unexpected).")
    else:
        for f in findings[:8]:
            report_lines.append(f"- **{f.severity}**: {f.title}")
    report_lines.append("")

    report_lines.append("## Findings")
    report_lines.append("")
    for f in findings:
        report_lines.append(f"### {f.severity}: {f.title}")
        report_lines.append("")
        report_lines.append(f.detail.rstrip())
        report_lines.append("")

    report_lines.append("## Recommended next actions (manual)")
    report_lines.append("")
    report_lines.append("These are suggestions; apply only if you explicitly want to change behavior:")
    report_lines.append("")
    report_lines.append("1. Keep one canonical global guidance source: `AGENTS.md`/`AGENTS.override.md` and, if used, the active `model_instructions_file` should be deliberate and non-conflicting.")
    report_lines.append("2. Fix the active instructions file (remove outer code fence; normalize mojibake; prefer absolute or `~/...` paths over cwd-relative paths).")
    report_lines.append("3. Tighten `.rules`: forbid `grep`, prompt `find`, and remove allow-rules that wrap destructive ops inside `zsh -lc`.")
    report_lines.append("4. Reduce duplication: keep interaction-format rules canonical in USER_PROFILE.md; keep policy canonical in AGENTS/instructions sources.")
    report_lines.append("")

    report_lines.append("## Verification commands")
    report_lines.append("")
    report_lines.append("From the Codex home directory:")
    report_lines.append("")
    report_lines.append("- `./scripts/rules-check.sh`")
    report_lines.append("- `python3 ./scripts/rules-lint.py`")
    report_lines.append("- Re-run this audit after changes and compare findings.")
    report_lines.append("")

    report_lines.append("## Rollback")
    report_lines.append("")
    report_lines.append("- If instruction loading breaks: restore the original filenames (e.g. rename the override template back to `AGENTS.override.md`).")
    report_lines.append("- If rules become too strict: revert the specific `.rules` file change(s) and re-run verification.")
    report_lines.append("")

    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    return report_path, findings, blockers


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codex-home", default=os.environ.get("CODEX_HOME") or str(Path.home() / ".codex"))
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args(argv)

    codex_home = Path(args.codex_home).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else (codex_home / "reports" / "codex-home-audit")

    report_path, findings, blockers = generate_report(codex_home=codex_home, out_dir=out_dir)

    # Console summary
    print(f"[codex-home-audit] Wrote report: {report_path}")
    if blockers:
        print("[codex-home-audit] Blockers:")
        for blocker in blockers:
            print(f"- {blocker}")
    if findings:
        print("[codex-home-audit] Top findings:")
        for f in findings[:5]:
            print(f"- {f.severity}: {f.title}")
    else:
        print("[codex-home-audit] No findings.")

    return 2 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
