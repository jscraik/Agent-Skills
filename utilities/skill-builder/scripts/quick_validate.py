#!/usr/bin/env python3
"""
quick_validate.py

Fast, dependency-light validator for Agent Skill SKILL.md files.

Checks:
- YAML frontmatter exists and parses
- Required keys: name, description
- Single-line name/description (no block scalars)
- Length limits by target (portable/codex/claude)
- Optional: strict mode enforces only name+description in frontmatter
- Compat mode enforces OpenAI official frontmatter keys

This is meant to be a *quick gate* before running deeper analysis/evals.

Usage:
    python quick_validate.py <path/to/skill-dir-or-SKILL.md> [--target codex] [--mode compat]

Exit codes:
    0  valid
    1  invalid
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Tuple

try:
    import yaml  # type: ignore
except ModuleNotFoundError:
    preferred = Path.home() / ".venvs" / "pyyaml" / "bin" / "python"
    already_reexec = os.environ.get("SKILL_CREATOR_PYYAML_REEXEC") == "1"
    if preferred.exists() and not already_reexec:
        env = dict(os.environ)
        env["SKILL_CREATOR_PYYAML_REEXEC"] = "1"
        os.execve(str(preferred), [str(preferred), __file__, *sys.argv[1:]], env)
    print("ERROR: PyYAML is required (pip install pyyaml).", file=sys.stderr)
    raise SystemExit(1)


TARGET_NAME_LIMITS = {"portable": 64, "codex": 64, "claude": 64}
TARGET_DESCRIPTION_LIMITS = {"portable": 1024, "codex": 1024, "claude": 1024}

# In strict mode, default to only the required fields.
STRICT_ALLOWED_KEYS = {"name", "description"}

# In compat mode, allow OpenAI official frontmatter keys used by skills.
COMPAT_ALLOWED_KEYS = {
    "name",
    "description",
    "license",
    "compatibility",
    "allowed-tools",
    "metadata",
}

_FRONTMATTER_DELIM_RE = re.compile(r"^\s*---\s*$")


def resolve_skill_md_path(path_like: str) -> Path:
    p = Path(path_like).expanduser().resolve()
    if p.is_dir():
        return p / "SKILL.md"
    return p


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def parse_frontmatter(raw_text: str) -> Tuple[Dict[str, Any], str]:
    lines = raw_text.splitlines(keepends=True)

    # Find first non-empty line; frontmatter must start there.
    first_nonempty: Optional[int] = None
    for i, line in enumerate(lines):
        if line.strip():
            first_nonempty = i
            break
    if first_nonempty is None:
        raise ValueError("SKILL.md is empty")

    if not _FRONTMATTER_DELIM_RE.match(lines[first_nonempty]):
        raise ValueError("Missing YAML frontmatter. Expected `---` as the first non-empty line.")

    # Find closing delimiter
    end_idx: Optional[int] = None
    for j in range(first_nonempty + 1, len(lines)):
        if _FRONTMATTER_DELIM_RE.match(lines[j]):
            end_idx = j
            break
    if end_idx is None:
        raise ValueError("Unterminated YAML frontmatter. Missing closing `---`.")

    yaml_text = "".join(lines[first_nonempty + 1 : end_idx])
    fm_obj = yaml.safe_load(yaml_text) if yaml_text.strip() else {}
    if fm_obj is None:
        fm: Dict[str, Any] = {}
    elif isinstance(fm_obj, dict):
        fm = fm_obj
    else:
        raise ValueError("Frontmatter YAML must be a mapping/object (key: value pairs).")

    body = "".join(lines[end_idx + 1 :]).lstrip("\n")
    return fm, body


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}", file=sys.stderr)
    raise SystemExit(1)


def validate_frontmatter(fm: Dict[str, Any], *, target: str, mode: str) -> None:
    allowed = STRICT_ALLOWED_KEYS if mode == "strict" else COMPAT_ALLOWED_KEYS

    unknown = sorted(set(fm.keys()) - allowed)
    if unknown:
        fail(
            f"Unknown frontmatter key(s): {', '.join(unknown)}. "
            f"Allowed ({mode} mode): {', '.join(sorted(allowed))}"
        )

    name = fm.get("name")
    desc = fm.get("description")

    if not isinstance(name, str) or not name.strip():
        fail("Frontmatter must include a non-empty string `name`.")
    if "\n" in name or "\r" in name:
        fail("`name` must be a single-line YAML scalar (no newlines).")
    if len(name) > TARGET_NAME_LIMITS[target]:
        fail(f"`name` too long: {len(name)} chars (max for {target}: {TARGET_NAME_LIMITS[target]}).")
    if not re.fullmatch(r"[a-z0-9-]+", name.strip()):
        fail("`name` must be hyphen-case: lowercase letters, digits, and hyphens only.")
    if name.startswith("-") or name.endswith("-") or "--" in name:
        fail("`name` cannot start/end with hyphen or contain consecutive hyphens.")

    if not isinstance(desc, str) or not desc.strip():
        fail("Frontmatter must include a non-empty string `description`.")
    if "\n" in desc or "\r" in desc:
        fail("`description` must be a single-line YAML scalar (no newlines / block scalars).")
    if len(desc) > TARGET_DESCRIPTION_LIMITS[target]:
        fail(f"`description` too long: {len(desc)} chars (max for {target}: {TARGET_DESCRIPTION_LIMITS[target]}).")
    if any(c in desc for c in ("<", ">")):
        fail("Angle brackets `<` or `>` are not allowed in description (escape or rephrase).")

def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Quick-validate a skill's SKILL.md frontmatter.")
    p.add_argument("path", help="Path to a skill directory or SKILL.md file")
    p.add_argument("--target", choices=sorted(TARGET_NAME_LIMITS.keys()), default="codex", help="Target environment (controls length limits)")
    p.add_argument(
        "--mode",
        choices=["strict", "compat"],
        default="compat",
        help=(
            "Validation mode (default: compat). "
            "strict allows only name+description; "
            "compat allows OpenAI official keys: name, description, license, compatibility, "
            "allowed-tools, metadata."
        ),
    )
    args = p.parse_args(list(argv) if argv is not None else None)

    skill_md = resolve_skill_md_path(args.path)
    if not skill_md.exists():
        fail(f"SKILL.md not found at: {skill_md}")

    try:
        raw = read_text(skill_md)
        fm, _body = parse_frontmatter(raw)
    except Exception as e:
        fail(str(e))

    validate_frontmatter(fm, target=args.target, mode=args.mode)

    print("[OK] SKILL.md frontmatter looks valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
