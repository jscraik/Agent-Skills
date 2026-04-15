#!/usr/bin/env python3
"""Check drift for plugin-creator template outputs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
FAMILY_SKILLS_DIR = SCRIPT_DIR.parents[1]
if str(FAMILY_SKILLS_DIR) not in sys.path:
    sys.path.insert(0, str(FAMILY_SKILLS_DIR))

from _template_utils import (
    TemplateRenderError,
    ensure_trailing_newline,
    load_json_context,
    parse_key_value,
    print_diff_lines,
    render_from_path,
    unified_diff_lines,
)
from render_plugin_creator_templates import (
    TEMPLATE_TARGETS,
    build_context,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check drift for plugin-creator rendered template outputs.")
    parser.add_argument(
        "--target",
        choices=["plugin_manifest", "marketplace_entry", "all"],
        default="all",
        help="Template target to check.",
    )
    parser.add_argument("--vars-json", help="Optional JSON object with template variables.")
    parser.add_argument("--var", action="append", default=[], help="Inline variable override (KEY=VALUE).")
    parser.add_argument("--no-defaults", action="store_true", help="Do not pre-seed context with built-in defaults.")
    parser.add_argument("--update", action="store_true", help="Rewrite rendered files with current template output.")
    parser.add_argument("--max-diff-lines", type=int, default=200, help="Maximum diff lines to print on drift.")
    return parser.parse_args(argv)


def _expected_text(template_path: Path, context: dict[str, str]) -> str:
    rendered = render_from_path(template_path=template_path, context=context)
    return ensure_trailing_newline(rendered)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        json_context = load_json_context(Path(args.vars_json).expanduser().resolve()) if args.vars_json else {}
        cli_context = dict(parse_key_value(item) for item in args.var)
        context = build_context(use_defaults=not args.no_defaults, json_context=json_context, cli_context=cli_context)
        targets = TEMPLATE_TARGETS.items() if args.target == "all" else [(args.target, TEMPLATE_TARGETS[args.target])]
        drift_found = False

        for name, (template_path, output_path) in targets:
            expected = _expected_text(template_path, context)
            if args.update:
                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(expected, encoding="utf-8")
                except OSError as exc:
                    raise TemplateRenderError(f"Failed to write rendered output {output_path}: {exc}") from exc
                print(f"[OK] Updated {name}: {output_path}")
                continue

            if not output_path.exists():
                drift_found = True
                print(f"[DRIFT] Missing output for {name}: {output_path}")
                continue

            try:
                actual = output_path.read_text(encoding="utf-8")
            except OSError as exc:
                raise TemplateRenderError(f"Failed to read rendered output {output_path}: {exc}") from exc
            if actual == expected:
                print(f"[OK] No drift for {name}: {output_path}")
                continue

            drift_found = True
            print(f"[DRIFT] {name} output out of date: {output_path}")
            diff_lines = unified_diff_lines(
                actual_text=actual,
                expected_text=expected,
                output_path=output_path,
                template_path=template_path,
            )
            print_diff_lines(diff_lines, max_diff_lines=args.max_diff_lines)
    except TemplateRenderError as exc:
        print(f"[ERROR] {exc}")
        return 1

    if drift_found and not args.update:
        print("Run with --update to refresh rendered baselines.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
