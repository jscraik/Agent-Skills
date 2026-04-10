#!/usr/bin/env python3
"""Render ce-spec/spec.md.tmpl into a concrete markdown specification.

Use when:
- you need a deterministic scaffold from the canonical Symphony template;
- you want strict variable replacement that fails when required placeholders are missing.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
FAMILY_SKILLS_DIR = SCRIPT_DIR.parents[1]
if str(FAMILY_SKILLS_DIR) not in sys.path:
    sys.path.insert(0, str(FAMILY_SKILLS_DIR))

from _template_utils import (  # noqa: E402
    TemplateRenderError,
    build_context as build_context_with_defaults,
    ensure_trailing_newline,
    load_json_context,
    parse_key_value,
    print_diff_lines,
    render_from_path,
    unified_diff_lines,
)

DEFAULT_TEMPLATE_PATH = SKILL_DIR / "spec.md.tmpl"
DEFAULT_OUTPUT_PATH = SKILL_DIR / "references" / "spec-template.md"

DEFAULT_CONTEXT: Dict[str, str] = {
    "SPEC_TITLE": "Symphony Service Specification",
    "SPEC_TYPE": "feat",
    "SPEC_STATUS": "draft",
    "SPEC_DATE": "2026-04-10",
    "SPEC_ORIGIN": "docs/brainstorms/symphony-service-brainstorm.md",
    "SPEC_RISK": "high",
    "SPEC_DEPTH": "full",
    "UI_REQUIRED": "false",
    "SPEC_STATUS_LINE": "Draft v1 (language-agnostic)",
    "SPEC_PURPOSE_LINE": "Define a service that orchestrates coding agents to get project work done.",
}


def build_context(*, use_defaults: bool, json_context: Dict[str, str], cli_context: Dict[str, str]) -> Dict[str, str]:
    return build_context_with_defaults(
        default_context=DEFAULT_CONTEXT,
        use_defaults=use_defaults,
        json_context=json_context,
        cli_context=cli_context,
    )


def render_from_paths(*, template_path: Path, context: Dict[str, str]) -> str:
    return render_from_path(template_path=template_path, context=context)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render ce-spec/spec.md.tmpl to markdown.")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE_PATH), help="Path to template file.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Path to rendered markdown file.")
    parser.add_argument("--vars-json", help="Optional JSON object with template variables.")
    parser.add_argument("--var", action="append", default=[], help="Inline variable override (KEY=VALUE).")
    parser.add_argument("--no-defaults", action="store_true", help="Do not pre-seed context with built-in defaults.")
    parser.add_argument("--stdout", action="store_true", help="Print rendered output to stdout instead of writing file.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    template_path = Path(args.template).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    try:
        json_context = load_json_context(Path(args.vars_json).expanduser().resolve()) if args.vars_json else {}
        cli_context = dict(parse_key_value(item) for item in args.var)
        context = build_context(use_defaults=not args.no_defaults, json_context=json_context, cli_context=cli_context)
        rendered = render_from_paths(template_path=template_path, context=context)
    except TemplateRenderError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    if args.stdout:
        sys.stdout.write(ensure_trailing_newline(rendered))
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(ensure_trailing_newline(rendered), encoding="utf-8")
    print(f"[OK] Rendered {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
