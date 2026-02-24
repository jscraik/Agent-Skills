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
import os
import re
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


def _extract_model_instructions_file(config_text: str) -> Optional[str]:
    # Very small TOML-ish parse: look for model_instructions_file = "..."
    m = re.search(r'(?m)^\s*model_instructions_file\s*=\s*"([^"]+)"\s*$', config_text)
    return m.group(1) if m else None


def _extract_default_profile(config_text: str) -> Optional[str]:
    m = re.search(r'(?m)^\s*profile\s*=\s*"([^"]+)"\s*$', config_text)
    return m.group(1) if m else None


def _extract_profile_sandbox_mode(config_text: str, profile_name: str) -> Optional[str]:
    # Rough parse: locate [profiles.<name>] and look for sandbox_mode inside until next table.
    header_re = re.compile(rf'(?m)^\[profiles\.{re.escape(profile_name)}\]\s*$')
    m = header_re.search(config_text)
    if not m:
        return None
    start = m.end()
    rest = config_text[start:]
    next_table = re.search(r'(?m)^\[[^\]]+\]\s*$', rest)
    block = rest[: next_table.start()] if next_table else rest
    mm = re.search(r'(?m)^\s*sandbox_mode\s*=\s*"([^"]+)"\s*$', block)
    return mm.group(1) if mm else None


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


def generate_report(*, codex_home: Path, out_dir: Path) -> Tuple[Path, List[Finding]]:
    findings: List[Finding] = []

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
    elif not agents_md.exists():
        findings.append(Finding(
            severity="HIGH",
            title="Missing AGENTS.md",
            detail=f"{_safe_rel(agents_md, codex_home)} not found. Create a canonical global AGENTS.md.",
        ))

    # 2) config.toml + global instructions
    config_path = codex_home / "config.toml"
    config_text = _read_text(config_path) if config_path.exists() else ""
    if not config_text:
        findings.append(Finding(
            severity="HIGH",
            title="Missing config.toml",
            detail=f"{_safe_rel(config_path, codex_home)} not found; cannot audit model_instructions_file or profile defaults.",
        ))
    else:
        mif = _extract_model_instructions_file(config_text)
        if mif:
            mif_path = Path(mif).expanduser()
            if not mif_path.exists():
                findings.append(Finding(
                    severity="HIGH",
                    title="model_instructions_file points to missing file",
                    detail=f'config.toml sets model_instructions_file="{mif}", but that path does not exist.',
                ))
            else:
                mif_text = _read_text(mif_path, limit_chars=50_000)
                if _detect_code_fence_wrapping(mif_text):
                    findings.append(Finding(
                        severity="MED",
                        title="Global instructions file is wrapped in a code fence",
                        detail=f"{mif_path} starts with ```; remove the outer code fence so the content is treated as instructions.",
                    ))
                if _contains_any(mif_text, MOJIBAKE_SIGNALS):
                    findings.append(Finding(
                        severity="MED",
                        title="Global instructions file contains mojibake",
                        detail=f"{mif_path} contains one or more mojibake sequences: {', '.join(MOJIBAKE_SIGNALS)}. Normalize to ASCII or correct UTF-8.",
                    ))

        default_profile = _extract_default_profile(config_text)
        if default_profile:
            sandbox_mode = _extract_profile_sandbox_mode(config_text, default_profile)
            if sandbox_mode == "danger-full-access":
                findings.append(Finding(
                    severity="MED",
                    title="Default profile uses danger-full-access",
                    detail=(
                        f'config.toml sets profile="{default_profile}" and that profile uses sandbox_mode="danger-full-access". '
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
    report_lines.append("1. Consolidate global guidance into `AGENTS.md` and rename `AGENTS.override.md` to a break-glass template.")
    report_lines.append("2. Fix `instructions/global.md` (remove outer code fence; normalize mojibake).")
    report_lines.append("3. Tighten `.rules`: forbid `grep`, prompt `find`, and remove allow-rules that wrap destructive ops inside `zsh -lc`.")
    report_lines.append("4. Reduce duplication: keep interaction-format rules canonical in USER_PROFILE.md; keep policy canonical in instructions/*.md.")
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
    return report_path, findings


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codex-home", default=os.environ.get("CODEX_HOME") or str(Path.home() / ".codex"))
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args(argv)

    codex_home = Path(args.codex_home).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else (codex_home / "reports" / "codex-home-audit")

    report_path, findings = generate_report(codex_home=codex_home, out_dir=out_dir)

    # Console summary
    print(f"[codex-home-audit] Wrote report: {report_path}")
    if findings:
        print("[codex-home-audit] Top findings:")
        for f in findings[:5]:
            print(f"- {f.severity}: {f.title}")
    else:
        print("[codex-home-audit] No findings.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
