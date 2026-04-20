#!/usr/bin/env python3
"""Check drift between he-plan/plan.md.tmpl and rendered output."""

from __future__ import annotations

import argparse
from pathlib import Path

from render_plan_template import (
    DEFAULT_OUTPUT_PATH,
    DEFAULT_TEMPLATE_PATH,
    TemplateRenderError,
    build_context,
    ensure_trailing_newline,
    load_json_context,
    parse_key_value,
    print_diff_lines,
    render_from_paths,
    unified_diff_lines,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check drift for he-plan rendered template output.")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE_PATH), help="Path to template file.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Path to rendered markdown file.")
    parser.add_argument("--vars-json", help="Optional JSON object with template variables.")
    parser.add_argument("--var", action="append", default=[], help="Inline variable override (KEY=VALUE).")
    parser.add_argument("--no-defaults", action="store_true", help="Do not pre-seed context with built-in defaults.")
    parser.add_argument("--update", action="store_true", help="Rewrite --output with current rendered content.")
    parser.add_argument("--max-diff-lines", type=int, default=200, help="Maximum diff lines to print on drift.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    template_path = Path(args.template).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    try:
        json_context = load_json_context(Path(args.vars_json).expanduser().resolve()) if args.vars_json else {}
        cli_context = dict(parse_key_value(item) for item in args.var)
        context = build_context(use_defaults=not args.no_defaults, json_context=json_context, cli_context=cli_context)
        expected = render_from_paths(template_path=template_path, context=context)
        expected = ensure_trailing_newline(expected)
    except TemplateRenderError as exc:
        print(f"[ERROR] {exc}")
        return 1

    if args.update:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(expected, encoding="utf-8")
        print(f"[OK] Updated {output_path}")
        return 0

    if not output_path.exists():
        print(f"[DRIFT] Output file is missing: {output_path}")
        print("Run with --update to materialize the rendered baseline.")
        return 1

    actual = output_path.read_text(encoding="utf-8")
    if actual == expected:
        print(f"[OK] No drift: {output_path}")
        return 0

    diff = unified_diff_lines(
        actual_text=actual,
        expected_text=expected,
        output_path=output_path,
        template_path=template_path,
    )

    print(f"[DRIFT] {output_path} is out of date with {template_path}")
    print_diff_lines(diff, max_diff_lines=args.max_diff_lines)

    print("Run with --update to refresh the rendered baseline.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
