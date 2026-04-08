#!/usr/bin/env python3
"""
generate_openai_yaml.py

Generate agents/openai.yaml for a skill based on its SKILL.md frontmatter.

Why:
- Keep SKILL.md frontmatter minimal (name + description for discovery)
- Put Codex UI metadata and MCP dependencies in agents/openai.yaml

Usage:
    python generate_openai_yaml.py <path/to/skill-dir-or-SKILL.md> [--out agents/openai.yaml]

Notes:
- This script does not add MCP dependencies automatically (leave placeholders).
- It will not overwrite an existing file unless you pass --force.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Tuple

try:
    import yaml  # type: ignore
except ModuleNotFoundError:
    yaml = None


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

    # First non-empty line must be ---
    first_nonempty: Optional[int] = None
    for i, line in enumerate(lines):
        if line.strip():
            first_nonempty = i
            break
    if first_nonempty is None:
        raise ValueError("SKILL.md is empty")

    if not _FRONTMATTER_DELIM_RE.match(lines[first_nonempty]):
        raise ValueError("Missing YAML frontmatter. Expected `---` as the first non-empty line.")

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


def format_display_name(name: str) -> str:
    # my-awesome-skill -> "My Awesome Skill"
    parts = name.replace("_", "-").split("-")
    return " ".join(p.capitalize() for p in parts if p)


def truncate_one_line(text: str, max_len: int) -> str:
    t = re.sub(r"\s+", " ", text).strip()
    if len(t) <= max_len:
        return t
    # Trim to last whole word if possible
    cut = t[: max_len - 1]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut + "…"


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Generate agents/openai.yaml from SKILL.md frontmatter.")
    p.add_argument("path", help="Path to a skill directory or SKILL.md file")
    p.add_argument("--out", default=None, help="Output path (default: <skill>/agents/openai.yaml)")
    p.add_argument("--force", action="store_true", help="Overwrite if the output file exists")
    p.add_argument("--no-policy", action="store_true", help="Do not include the policy section")
    p.add_argument("--allow-implicit", action="store_true", help="Set policy.allow_implicit_invocation=true (default false)")
    args = p.parse_args(list(argv) if argv is not None else None)
    if yaml is None:
        print("ERROR: PyYAML is required (pip install pyyaml).", file=sys.stderr)
        return 1

    skill_md = resolve_skill_md_path(args.path)
    if not skill_md.exists():
        print(f"ERROR: SKILL.md not found at: {skill_md}", file=sys.stderr)
        return 1

    fm, _body = parse_frontmatter(read_text(skill_md))

    name = fm.get("name")
    description = fm.get("description")

    if not isinstance(name, str) or not name.strip():
        print("ERROR: SKILL.md frontmatter missing a string `name`.", file=sys.stderr)
        return 1
    if not isinstance(description, str) or not description.strip():
        print("ERROR: SKILL.md frontmatter missing a string `description`.", file=sys.stderr)
        return 1

    display_name = format_display_name(name.strip())
    short_description = truncate_one_line(description.strip(), 64)

    payload: Dict[str, Any] = {
        "interface": {
            "display_name": display_name,
            "short_description": short_description,
        }
    }

    if not args.no_policy:
        payload["policy"] = {"allow_implicit_invocation": bool(args.allow_implicit)}

    # Always include a commented dependency sample in the file footer (more discoverable than empty YAML keys).
    rendered = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True).rstrip() + "\n"
    rendered += "\n# dependencies:\n#   tools:\n#     - type: \"mcp\"\n#       value: \"serverName\"\n#       description: \"MCP server description\"\n#       transport: \"streamable_http\"\n#       url: \"https://example.com/mcp\"\n"

    out_path = Path(args.out).expanduser().resolve() if args.out else (skill_md.parent / "agents" / "openai.yaml")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if out_path.exists() and not args.force:
        print(f"ERROR: {out_path} already exists. Use --force to overwrite.", file=sys.stderr)
        return 1

    out_path.write_text(rendered, encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
