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


def _lookup_path(mapping: object, path_parts: Sequence[str]) -> object:
    current = mapping
    for part in path_parts:
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _active_config_value(
    config_data: dict,
    *,
    default_profile: Optional[str],
    path_parts: Sequence[str],
) -> Tuple[object, Optional[str]]:
    profiles_table = config_data.get("profiles")
    if default_profile and isinstance(profiles_table, dict):
        profile_table = profiles_table.get(default_profile)
        if isinstance(profile_table, dict):
            profile_value = _lookup_path(profile_table, path_parts)
            if profile_value is not None:
                return profile_value, f'profiles.{default_profile}.{".".join(path_parts)}'

    value = _lookup_path(config_data, path_parts)
    if value is not None:
        return value, ".".join(path_parts)
    return None, None


def _resolve_config_relative_path(raw_path: str, *, config_path: Path) -> Path:
    expanded = Path(raw_path).expanduser()
    if expanded.is_absolute():
        return expanded
    return config_path.parent / expanded


def _human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{num_bytes} B"


def _otel_exporter_info(value: object) -> Tuple[str, List[str]]:
    if value is None:
        return "none", []
    if isinstance(value, str):
        return value, []
    if isinstance(value, dict) and len(value) == 1:
        kind, detail = next(iter(value.items()))
        endpoints: List[str] = []
        if isinstance(detail, dict):
            endpoint = detail.get("endpoint")
            if isinstance(endpoint, str):
                endpoints.append(endpoint)
        return str(kind), endpoints
    return "custom", []


def _is_loopback_endpoint(endpoint: str) -> bool:
    return bool(re.search(r"(localhost|127\.0\.0\.1|\[::1\])", endpoint))


def _valid_plugin_segment(segment: str) -> bool:
    return bool(segment) and all(
        ch.isascii() and (ch.isalnum() or ch in "-_") for ch in segment
    )


def _load_json_file(path: Path) -> Tuple[Optional[object], Optional[str]]:
    try:
        return json.loads(_read_text(path, limit_chars=200_000)), None
    except json.JSONDecodeError as exc:
        return None, str(exc)


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


def generate_report(
    *,
    codex_home: Path,
    out_dir: Path,
) -> Tuple[Path, List[Finding], List[str], List[str]]:
    findings: List[Finding] = []
    blockers: List[str] = []
    inventory: List[str] = []

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
    active_sandbox_mode = None
    active_sandbox_mode_source = None
    active_network_access = None
    active_history_persistence = "save-all"
    history_max_bytes = None
    config_findings_start = len(findings)
    config_inventory_start = len(inventory)
    config_parse_failed = False
    config_parse_failure_finding: Optional[Finding] = None
    if not config_text:
        blockers.append("Missing config.toml")
        findings.append(Finding(
            severity="HIGH",
            title="Missing config.toml",
            detail=f"{_safe_rel(config_path, codex_home)} not found; cannot audit model_instructions_file or profile defaults.",
        ))
        inventory.append("Config: missing config.toml, so profile, telemetry, history, agents, skills, and state-path checks were limited.")
    else:
        config_data, config_error = _parse_config_toml(config_text)
        if config_error is not None:
            config_parse_failed = True
            blockers.append("Invalid config.toml")
            config_parse_failure_finding = Finding(
                severity="HIGH",
                title="config.toml is invalid TOML",
                detail=f"{_safe_rel(config_path, codex_home)} could not be parsed: {config_error}",
            )
            findings.append(config_parse_failure_finding)
            config_data = {}

        profiles_table = config_data.get("profiles") if isinstance(config_data, dict) else {}
        if not isinstance(profiles_table, dict):
            profiles_table = {}

        default_profile = config_data.get("profile") if isinstance(config_data.get("profile"), str) else None
        if default_profile and default_profile not in profiles_table:
            findings.append(Finding(
                severity="HIGH",
                title="Default profile points to a missing profile definition",
                detail=(
                    f'config.toml sets profile="{default_profile}", but no [profiles.{default_profile}] table exists. '
                    "That means profile-scoped overrides for instructions, sandboxing, and telemetry cannot be audited as intended."
                ),
            ))
        inventory.append(
            f"Config: parsed config.toml successfully; active default profile is `{default_profile}`."
            if default_profile
            else "Config: parsed config.toml successfully; no default profile is pinned."
        )

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

        if (
            top_level_instruction
            and profile_instruction
            and top_level_instruction.raw_path != profile_instruction.raw_path
        ):
            findings.append(Finding(
                severity="LOW",
                title="Default profile overrides top-level model_instructions_file",
                detail=(
                    f'Top-level `model_instructions_file` points to "{top_level_instruction.raw_path}", but the default profile '
                    f'`{default_profile}` overrides it with "{profile_instruction.raw_path}". Audit and cleanup should focus on the '
                    "default-profile file because it is the active configuration for new sessions."
                ),
            ))

        active_sandbox_mode, active_sandbox_mode_source = _active_config_value(
            config_data,
            default_profile=default_profile,
            path_parts=("sandbox_mode",),
        )
        active_network_access, active_network_access_source = _active_config_value(
            config_data,
            default_profile=default_profile,
            path_parts=("sandbox_workspace_write", "network_access"),
        )
        if isinstance(active_sandbox_mode, str):
            inventory.append(
                f"Sandbox: active mode is `{active_sandbox_mode}` from `{active_sandbox_mode_source}`."
            )
        else:
            inventory.append("Sandbox: no explicit sandbox_mode set in config.toml; Codex defaults apply.")
        if active_sandbox_mode == "danger-full-access":
            findings.append(Finding(
                severity="MED",
                title="Active sandbox mode uses danger-full-access",
                detail=(
                    f'config.toml resolves the active sandbox mode from `{active_sandbox_mode_source}` to "danger-full-access". '
                    "This increases blast radius for accidental commands. Consider defaulting to workspace-write and opting into danger-full-access only when needed."
                ),
            ))

        analytics_enabled, analytics_source = _active_config_value(
            config_data,
            default_profile=default_profile,
            path_parts=("analytics", "enabled"),
        )
        analytics_label = "default client setting"
        if isinstance(analytics_enabled, bool):
            analytics_label = f"`{analytics_enabled}` from `{analytics_source}`"

        otel_table, _ = _active_config_value(
            config_data,
            default_profile=default_profile,
            path_parts=("otel",),
        )
        if not isinstance(otel_table, dict):
            otel_table = {}
        otel_environment = otel_table.get("environment") if isinstance(otel_table.get("environment"), str) else "dev"
        otel_exporter_kind, otel_exporter_endpoints = _otel_exporter_info(otel_table.get("exporter"))
        otel_trace_kind, otel_trace_endpoints = _otel_exporter_info(otel_table.get("trace_exporter"))
        otel_metrics_kind, _ = _otel_exporter_info(otel_table.get("metrics_exporter"))
        otel_log_user_prompt = bool(otel_table.get("log_user_prompt") is True)
        inventory.append(
            "Telemetry: "
            f"analytics is {analytics_label}; OTel env `{otel_environment}`; "
            f"log exporter `{otel_exporter_kind}`, trace exporter `{otel_trace_kind}`, metrics exporter `{otel_metrics_kind}`."
        )

        if otel_log_user_prompt:
            findings.append(Finding(
                severity="HIGH",
                title="OTel exports raw user prompts",
                detail=(
                    "config.toml sets `otel.log_user_prompt = true`. March 2026 Codex security guidance recommends keeping this off "
                    "unless policy explicitly allows prompt retention, because prompts can include source code and sensitive data."
                ),
            ))

        exporter_endpoints = otel_exporter_endpoints + otel_trace_endpoints
        if exporter_endpoints and active_sandbox_mode == "workspace-write" and active_network_access is False:
            findings.append(Finding(
                severity="MED",
                title="OTel exporter is configured but workspace-write network access is disabled",
                detail=(
                    "Telemetry exporters are configured, but the active sandbox is `workspace-write` and "
                    f"`{active_network_access_source}` is `false`. Codex docs note OTel export cannot reach its collector "
                    "without network access."
                ),
            ))
        if exporter_endpoints:
            loopback_endpoints = [endpoint for endpoint in exporter_endpoints if _is_loopback_endpoint(endpoint)]
            if loopback_endpoints:
                findings.append(Finding(
                    severity="LOW",
                    title="OTel exporter targets a loopback collector",
                    detail=(
                        "Codex is configured to send OTel data to a loopback collector endpoint. "
                        f"Checked endpoints: {', '.join(loopback_endpoints)}. If no collector is listening, Codex will log exporter failures."
                    ),
                ))

        active_history_persistence_value, history_persistence_source = _active_config_value(
            config_data,
            default_profile=default_profile,
            path_parts=("history", "persistence"),
        )
        if isinstance(active_history_persistence_value, str):
            active_history_persistence = active_history_persistence_value
        history_max_bytes_value, history_max_bytes_source = _active_config_value(
            config_data,
            default_profile=default_profile,
            path_parts=("history", "max_bytes"),
        )
        if isinstance(history_max_bytes_value, int):
            history_max_bytes = history_max_bytes_value
        elif isinstance(history_max_bytes_value, float) and history_max_bytes_value.is_integer():
            history_max_bytes = int(history_max_bytes_value)

        history_path = codex_home / "history.jsonl"
        history_exists = history_path.exists()
        history_size = history_path.stat().st_size if history_exists and history_path.is_file() else 0
        inventory.append(
            "History: "
            f"persistence is `{active_history_persistence}`"
            + (
                f" from `{history_persistence_source}`"
                if history_persistence_source
                else " (implicit/default)"
            )
            + (
                f"; max_bytes is {_human_size(history_max_bytes)} from `{history_max_bytes_source}`."
                if history_max_bytes is not None
                else "; no explicit max_bytes cap is configured."
            )
            + (
                f" Current history file size: {_human_size(history_size)}."
                if history_exists
                else " No history.jsonl file exists yet."
            )
        )

        if history_max_bytes is not None and history_max_bytes <= 0:
            findings.append(Finding(
                severity="MED",
                title="history.max_bytes is not a positive number",
                detail=(
                    f"`{history_max_bytes_source}` is set to `{history_max_bytes}`. History caps should be positive if configured."
                ),
            ))
        if active_history_persistence != "none" and history_max_bytes is None:
            findings.append(Finding(
                severity="LOW",
                title="History persistence is enabled without a size cap",
                detail=(
                    "Codex is configured to persist local session history, but `history.max_bytes` is unset. "
                    "If you care about local retention bounds, set an explicit cap."
                ),
            ))
        if active_history_persistence == "none" and history_exists and history_size > 0:
            findings.append(Finding(
                severity="LOW",
                title="History persistence is disabled but an old history.jsonl still exists",
                detail=(
                    f"`history.persistence` is `none`, but `{_safe_rel(history_path, codex_home)}` is still present at {_human_size(history_size)}. "
                    "Codex will stop appending new transcripts, but older local transcript data remains on disk until you remove or archive it."
                ),
            ))
        if (
            active_history_persistence != "none"
            and history_max_bytes is not None
            and history_exists
            and history_size > history_max_bytes
        ):
            findings.append(Finding(
                severity="LOW",
                title="history.jsonl is larger than history.max_bytes",
                detail=(
                    f"`{_safe_rel(history_path, codex_home)}` is currently {_human_size(history_size)}, which exceeds the configured cap "
                    f"of {_human_size(history_max_bytes)}. Codex should compact on future writes, but this is worth verifying."
                ),
            ))

        cli_auth_store, cli_auth_store_source = _active_config_value(
            config_data,
            default_profile=default_profile,
            path_parts=("cli_auth_credentials_store",),
        )
        if not isinstance(cli_auth_store, str):
            cli_auth_store = "auto"
        auth_path = codex_home / "auth.json"
        inventory.append(
            "Auth state: "
            f"CLI credentials store is `{cli_auth_store}`"
            + (f" from `{cli_auth_store_source}`" if cli_auth_store_source else "")
            + (
                f"; auth.json is {'present' if auth_path.exists() else 'absent'}."
                if cli_auth_store in {"file", "auto"}
                else "; auth.json not expected because file storage is not selected."
            )
        )

        mcp_oauth_store, mcp_oauth_store_source = _active_config_value(
            config_data,
            default_profile=default_profile,
            path_parts=("mcp_oauth_credentials_store",),
        )
        if not isinstance(mcp_oauth_store, str):
            mcp_oauth_store = "auto"
        inventory.append(
            "MCP OAuth: "
            f"credential store is `{mcp_oauth_store}`"
            + (f" from `{mcp_oauth_store_source}`." if mcp_oauth_store_source else ".")
        )

        log_dir_value, log_dir_source = _active_config_value(
            config_data,
            default_profile=default_profile,
            path_parts=("log_dir",),
        )
        log_dir_path = codex_home / "log"
        if isinstance(log_dir_value, str):
            log_dir_path = _resolve_config_relative_path(log_dir_value, config_path=config_path)
        inventory.append(
            f"State paths: log_dir resolves to `{log_dir_path}`"
            + (
                f" from `{log_dir_source}`"
                if log_dir_source
                else " (default)"
            )
            + "."
        )
        if log_dir_path.exists() and not log_dir_path.is_dir():
            findings.append(Finding(
                severity="HIGH",
                title="log_dir points to a non-directory path",
                detail=(
                    f"The active log directory resolves to `{log_dir_path}`, but that path exists and is not a directory."
                ),
            ))

        sqlite_home_value, sqlite_home_source = _active_config_value(
            config_data,
            default_profile=default_profile,
            path_parts=("sqlite_home",),
        )
        sqlite_home_path = codex_home / "state"
        if isinstance(sqlite_home_value, str):
            sqlite_home_path = _resolve_config_relative_path(sqlite_home_value, config_path=config_path)
        inventory.append(
            f"State paths: sqlite_home resolves to `{sqlite_home_path}`"
            + (
                f" from `{sqlite_home_source}`"
                if sqlite_home_source
                else " (default/runtime-managed)"
            )
            + "."
        )
        if sqlite_home_path.exists() and not sqlite_home_path.is_dir():
            findings.append(Finding(
                severity="HIGH",
                title="sqlite_home points to a non-directory path",
                detail=(
                    f"The active SQLite state path resolves to `{sqlite_home_path}`, but that path exists and is not a directory."
                ),
            ))

        features_table, _ = _active_config_value(
            config_data,
            default_profile=default_profile,
            path_parts=("features",),
        )
        if not isinstance(features_table, dict):
            features_table = {}
        multi_agent_enabled = features_table.get("multi_agent")
        if not isinstance(multi_agent_enabled, bool):
            multi_agent_enabled = True

        agents_table, agents_table_source = _active_config_value(
            config_data,
            default_profile=default_profile,
            path_parts=("agents",),
        )
        if not isinstance(agents_table, dict):
            agents_table = {}
        agent_role_names = sorted(
            name for name, value in agents_table.items()
            if isinstance(value, dict)
        )
        inventory.append(
            "Agents: "
            f"multi_agent is `{multi_agent_enabled}`; found {len(agent_role_names)} named role definition(s)"
            + (
                f" in `{agents_table_source}`."
                if agents_table_source
                else "."
            )
        )

        max_threads = agents_table.get("max_threads")
        if isinstance(max_threads, int) and max_threads < 1:
            findings.append(Finding(
                severity="MED",
                title="agents.max_threads is less than 1",
                detail="`agents.max_threads` should be at least 1 if explicitly configured.",
            ))
        max_depth = agents_table.get("max_depth")
        if isinstance(max_depth, int) and max_depth < 0:
            findings.append(Finding(
                severity="MED",
                title="agents.max_depth is negative",
                detail="`agents.max_depth` should be 0 or greater.",
            ))
        job_max_runtime = agents_table.get("job_max_runtime_seconds")
        if isinstance(job_max_runtime, int) and job_max_runtime <= 0:
            findings.append(Finding(
                severity="MED",
                title="agents.job_max_runtime_seconds is not positive",
                detail="`agents.job_max_runtime_seconds` should be positive if explicitly configured.",
            ))

        if agent_role_names and not multi_agent_enabled:
            findings.append(Finding(
                severity="LOW",
                title="Agent roles are configured while multi-agent tools are disabled",
                detail=(
                    "Named agent roles exist in config.toml, but `[features].multi_agent` is false. "
                    "Those role definitions will not be usable until multi-agent tooling is enabled."
                ),
            ))

        for role_name in agent_role_names:
            role_table = agents_table.get(role_name)
            if not isinstance(role_table, dict):
                continue
            role_description = role_table.get("description")
            role_config_file = role_table.get("config_file")
            if role_description is not None and not isinstance(role_description, str):
                findings.append(Finding(
                    severity="MED",
                    title=f"agents.{role_name}.description is not a string",
                    detail=f"`agents.{role_name}.description` should be a string when set.",
                ))
            if isinstance(role_config_file, str):
                resolved_role_config = _resolve_config_relative_path(role_config_file, config_path=config_path)
                if not resolved_role_config.exists():
                    findings.append(Finding(
                        severity="HIGH",
                        title=f"agents.{role_name}.config_file points to a missing file",
                        detail=(
                            f"`agents.{role_name}.config_file` resolves to `{resolved_role_config}`, but that file does not exist. "
                            "March 2026 Codex docs resolve agent config_file paths relative to the config file that declares the role."
                        ),
                    ))
                elif resolved_role_config.is_dir():
                    findings.append(Finding(
                        severity="MED",
                        title=f"agents.{role_name}.config_file points to a directory",
                        detail=(
                            f"`agents.{role_name}.config_file` resolves to `{resolved_role_config}`, but Codex expects a TOML config file."
                        ),
                    ))
                else:
                    role_config_text = _read_text(resolved_role_config, limit_chars=80_000)
                    _, role_config_error = _parse_config_toml(role_config_text)
                    if role_config_error is not None:
                        findings.append(Finding(
                            severity="MED",
                            title=f"agents.{role_name}.config_file is not valid TOML",
                            detail=(
                                f"`agents.{role_name}.config_file` resolves to `{resolved_role_config}`, but parsing failed: {role_config_error}"
                            ),
                        ))

        skills_table, _ = _active_config_value(
            config_data,
            default_profile=default_profile,
            path_parts=("skills",),
        )
        if not isinstance(skills_table, dict):
            skills_table = {}
        skills_config = skills_table.get("config")
        if not isinstance(skills_config, list):
            skills_config = []
        user_skills_root = codex_home / "skills"
        system_skills_root = user_skills_root / ".system"
        user_skill_files = []
        if user_skills_root.is_dir():
            user_skill_files = [
                path for path in user_skills_root.rglob("SKILL.md")
                if path.is_file() and ".system" not in path.parts
            ]
        system_skill_files = list(system_skills_root.rglob("SKILL.md")) if system_skills_root.is_dir() else []
        disabled_skill_overrides = 0
        inventory.append(
            "Skills: "
            f"found {len(user_skill_files)} user skill file(s), {len(system_skill_files)} system cache skill file(s), "
            f"and {len(skills_config)} config override entr{'y' if len(skills_config) == 1 else 'ies'}."
        )

        for idx, entry in enumerate(skills_config, start=1):
            if not isinstance(entry, dict):
                findings.append(Finding(
                    severity="MED",
                    title="skills.config entry is not an object",
                    detail=f"`skills.config[{idx}]` is not a TOML table/object, so Codex cannot interpret it reliably.",
                ))
                continue
            enabled = entry.get("enabled")
            if enabled is False:
                disabled_skill_overrides += 1
            raw_path = entry.get("path")
            if not isinstance(raw_path, str) or not raw_path.strip():
                findings.append(Finding(
                    severity="MED",
                    title="skills.config entry is missing a usable path",
                    detail=f"`skills.config[{idx}]` needs a string `path` value pointing to a skill directory or `SKILL.md` file.",
                ))
                continue
            resolved_skill_path = _resolve_config_relative_path(raw_path, config_path=config_path)
            if not resolved_skill_path.exists():
                findings.append(Finding(
                    severity="HIGH",
                    title="skills.config entry points to a missing path",
                    detail=(
                        f"`skills.config[{idx}].path` resolves to `{resolved_skill_path}`, but that path does not exist."
                    ),
                ))
                continue
            skill_md_path: Optional[Path] = None
            if resolved_skill_path.is_dir():
                candidate = resolved_skill_path / "SKILL.md"
                if candidate.exists():
                    skill_md_path = candidate
            elif resolved_skill_path.is_file() and resolved_skill_path.name == "SKILL.md":
                skill_md_path = resolved_skill_path
            if skill_md_path is None:
                findings.append(Finding(
                    severity="HIGH",
                    title="skills.config entry does not resolve to a valid skill",
                    detail=(
                        f"`skills.config[{idx}].path` resolves to `{resolved_skill_path}`, but Codex expects either a skill directory "
                        "containing `SKILL.md` or a direct path to `SKILL.md`."
                    ),
                ))

        if disabled_skill_overrides:
            inventory.append(
                f"Skills: {disabled_skill_overrides} skill override entr{'y is' if disabled_skill_overrides == 1 else 'ies are'} explicitly disabled in config.toml."
            )

        hooks_path = codex_home / "hooks.json"
        if hooks_path.exists():
            parsed_hooks, hooks_error = _load_json_file(hooks_path)
            if hooks_error is None and isinstance(parsed_hooks, dict) and isinstance(parsed_hooks.get("hooks"), dict):
                hook_groups = 0
                hook_handlers = 0
                for event_name in ("SessionStart", "Stop"):
                    groups = parsed_hooks["hooks"].get(event_name, [])
                    if isinstance(groups, list):
                        hook_groups += len(groups)
                        for group in groups:
                            if isinstance(group, dict) and isinstance(group.get("hooks"), list):
                                hook_handlers += len(group["hooks"])
                inventory.append(
                    f"Hooks: hooks.json is present with {hook_groups} matcher group(s) and {hook_handlers} declared handler(s)."
                )
            else:
                inventory.append("Hooks: hooks.json is present but could not be inventoried cleanly because it is invalid or malformed.")
        else:
            inventory.append("Hooks: no hooks.json file is present in CODEX_HOME.")
        _audit_hooks_file(findings, codex_home=codex_home)

        plugins_cache_root = codex_home / "plugins" / "cache"
        plugin_count = 0
        plugin_version_count = 0
        plugins_with_skills = 0
        plugins_with_mcp = 0
        plugins_with_apps = 0
        if plugins_cache_root.is_dir():
            for marketplace_dir in sorted(p for p in plugins_cache_root.iterdir() if p.is_dir()):
                if not _valid_plugin_segment(marketplace_dir.name):
                    findings.append(Finding(
                        severity="MED",
                        title="Plugin marketplace cache directory uses an invalid segment name",
                        detail=(
                            f"`{marketplace_dir}` does not match Codex plugin marketplace segment rules "
                            "(ASCII letters, digits, `_`, `-`)."
                        ),
                    ))
                for plugin_dir in sorted(p for p in marketplace_dir.iterdir() if p.is_dir()):
                    plugin_count += 1
                    if not _valid_plugin_segment(plugin_dir.name):
                        findings.append(Finding(
                            severity="MED",
                            title="Plugin cache directory uses an invalid plugin name segment",
                            detail=(
                                f"`{plugin_dir}` does not match Codex plugin naming rules "
                                "(ASCII letters, digits, `_`, `-`)."
                            ),
                        ))
                    version_dirs = sorted(p for p in plugin_dir.iterdir() if p.is_dir())
                    plugin_version_count += len(version_dirs)
                    if len(version_dirs) > 1:
                        findings.append(Finding(
                            severity="LOW",
                            title="Plugin cache has multiple versions for one plugin",
                            detail=(
                                f"`{plugin_dir}` contains {len(version_dirs)} version directories. The current Codex plugin store "
                                "treats a plugin as active only when exactly one valid cached version is present."
                            ),
                        ))
                    if not version_dirs:
                        findings.append(Finding(
                            severity="MED",
                            title="Plugin cache entry has no version directories",
                            detail=f"`{plugin_dir}` exists but contains no version directories.",
                        ))
                    for version_dir in version_dirs:
                        manifest_path = version_dir / ".codex-plugin" / "plugin.json"
                        if not manifest_path.is_file():
                            findings.append(Finding(
                                severity="HIGH",
                                title="Cached plugin is missing its manifest",
                                detail=(
                                    f"`{version_dir}` is missing `.codex-plugin/plugin.json`, which Codex expects for plugin discovery."
                                ),
                            ))
                        else:
                            manifest_json, manifest_error = _load_json_file(manifest_path)
                            if manifest_error is not None:
                                findings.append(Finding(
                                    severity="HIGH",
                                    title="Cached plugin manifest is invalid JSON",
                                    detail=f"`{manifest_path}` could not be parsed: {manifest_error}",
                                ))
                            elif not isinstance(manifest_json, dict):
                                findings.append(Finding(
                                    severity="MED",
                                    title="Cached plugin manifest is not a JSON object",
                                    detail=f"`{manifest_path}` should parse to a JSON object.",
                                ))

                        skills_dir = version_dir / "skills"
                        if skills_dir.is_dir():
                            plugins_with_skills += 1

                        mcp_config_path = version_dir / ".mcp.json"
                        if mcp_config_path.exists():
                            plugins_with_mcp += 1
                            mcp_json, mcp_error = _load_json_file(mcp_config_path)
                            if mcp_error is not None:
                                findings.append(Finding(
                                    severity="HIGH",
                                    title="Cached plugin .mcp.json is invalid JSON",
                                    detail=f"`{mcp_config_path}` could not be parsed: {mcp_error}",
                                ))
                            elif not isinstance(mcp_json, dict):
                                findings.append(Finding(
                                    severity="MED",
                                    title="Cached plugin .mcp.json is not a JSON object",
                                    detail=f"`{mcp_config_path}` should parse to a JSON object.",
                                ))

                        app_config_path = version_dir / ".app.json"
                        if app_config_path.exists():
                            plugins_with_apps += 1
                            app_json, app_error = _load_json_file(app_config_path)
                            if app_error is not None:
                                findings.append(Finding(
                                    severity="HIGH",
                                    title="Cached plugin .app.json is invalid JSON",
                                    detail=f"`{app_config_path}` could not be parsed: {app_error}",
                                ))
                            elif not isinstance(app_json, dict):
                                findings.append(Finding(
                                    severity="MED",
                                    title="Cached plugin .app.json is not a JSON object",
                                    detail=f"`{app_config_path}` should parse to a JSON object.",
                                ))
        inventory.append(
            "Plugins: "
            + (
                f"found {plugin_count} plugin cache entr{'y' if plugin_count == 1 else 'ies'} across {plugin_version_count} version director{'y' if plugin_version_count == 1 else 'ies'}; "
                f"{plugins_with_skills} expose skills, {plugins_with_mcp} expose MCP config, and {plugins_with_apps} expose app config."
                if plugins_cache_root.is_dir()
                else "no local plugin cache directory exists yet."
            )
        )
        if config_parse_failed:
            findings[config_findings_start:] = (
                [config_parse_failure_finding]
                if config_parse_failure_finding is not None
                else []
            )
            inventory[config_inventory_start:] = [
                "Config: config.toml is invalid, so profile, telemetry, history, auth, state-path, agents, skills, hooks, and plugin cache checks were skipped."
            ]

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
        inventory.append(f"Rules: audited {len(rules)} .rules file(s) under `{_safe_rel(codex_home / 'rules', codex_home)}`.")

    has_guidance_source = (
        _is_nonempty(agents_override)
        or _is_nonempty(agents_md)
        or top_level_instruction is not None
        or profile_instruction is not None
        or deprecated_top_level_instruction is not None
        or deprecated_profile_instruction is not None
    )
    guidance_source_unknown = config_parse_failed and not (
        _is_nonempty(agents_override) or _is_nonempty(agents_md)
    )
    if not has_guidance_source and not guidance_source_unknown:
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
    inventory.append(
        "Guidance: "
        + (
            "global guidance sources could not be fully audited because config.toml is invalid."
            if guidance_source_unknown
            else
            "detected at least one global guidance source."
            if has_guidance_source
            else "no global guidance source was detected."
        )
    )

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
    report_lines.append(f"- Surfaces checked: {len(inventory)}")
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

    report_lines.append("## Surface Inventory")
    report_lines.append("")
    for line in inventory:
        report_lines.append(f"- {line}")
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
    report_lines.append("1. Keep one canonical guidance chain: `AGENTS.md`/`AGENTS.override.md` plus any active `model_instructions_file` should be deliberate, non-conflicting, and easy to trace.")
    report_lines.append("2. Review telemetry and retention posture together: keep `otel.log_user_prompt = false` unless policy allows it, route exporters only to collectors you control, and set an explicit `history.max_bytes` cap if local transcript retention matters.")
    report_lines.append("3. Validate automation surfaces end to end: remove unsupported hook types, verify named agent role config files exist, and keep skill/plugin paths resolvable from the active config layer.")
    report_lines.append("4. Tighten enforcement surfaces: forbid `grep`, prompt `find`, remove risky `zsh -lc` allow-rules, and reduce duplicated prose by choosing one canonical owner for recurring guidance.")
    report_lines.append("")

    report_lines.append("## Verification commands")
    report_lines.append("")
    report_lines.append("From the Codex home directory:")
    report_lines.append("")
    report_lines.append("- `./Infrastructure/scripts/rules-check.sh`")
    report_lines.append("- `python3 ./Infrastructure/scripts/rules-lint.py`")
    report_lines.append("- `test -f ./config.toml && python3 - <<'PY'\nimport tomllib, pathlib\npath = pathlib.Path('config.toml')\ntomllib.loads(path.read_text(encoding='utf-8'))\nprint('config.toml parses cleanly')\nPY`")
    report_lines.append("- `test ! -f ./hooks.json || jq '.' ./hooks.json >/dev/null`")
    report_lines.append("- `test ! -d ./Plugins/cache || find ./Plugins/cache -name plugin.json -path '*/.codex-plugin/*' -print`")
    report_lines.append("- Re-run this audit after changes and compare findings.")
    report_lines.append("")

    report_lines.append("## Rollback")
    report_lines.append("")
    report_lines.append("- If instruction loading breaks: restore the original filenames or config values (for example rename the override template back to `AGENTS.override.md` or restore the previous `model_instructions_file`).")
    report_lines.append("- If telemetry or retention changes create issues: revert the `[otel]`, `[history]`, or credential-store keys in `config.toml`, then confirm the Surface Inventory section returns to the expected state.")
    report_lines.append("- If hooks, agents, skills, or plugins stop loading: restore the previous `hooks.json`, agent role config file, `skills.config` entry, or plugin cache/version layout and re-run verification.")
    report_lines.append("- If rules become too strict: revert the specific `.rules` file change(s) and re-run verification.")
    report_lines.append("")

    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    return report_path, findings, blockers, inventory


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codex-home", default=os.environ.get("CODEX_HOME") or str(Path.home() / ".codex"))
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args(argv)

    codex_home = Path(args.codex_home).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else (codex_home / "reports" / "codex-home-audit")

    report_path, findings, blockers, inventory = generate_report(codex_home=codex_home, out_dir=out_dir)

    # Console summary
    print(f"[codex-home-audit] Wrote report: {report_path}")
    print(f"[codex-home-audit] Surfaces checked: {len(inventory)}")
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
