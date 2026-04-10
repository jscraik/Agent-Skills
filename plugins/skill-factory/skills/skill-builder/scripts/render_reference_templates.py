#!/usr/bin/env python3
"""Render skill-builder reference templates."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

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
    render_from_path,
)

REF_DIR = SKILL_DIR / "references"

DEFAULT_CONTEXT: dict[str, str] = {
    "SKILL_NAME": "SKILL_NAME",
}

TEMPLATE_TARGETS: dict[str, tuple[Path, Path]] = {
    "contract": (REF_DIR / "contract.template.yaml.tmpl", REF_DIR / "contract.template.yaml"),
    "evals": (REF_DIR / "evals.template.yaml.tmpl", REF_DIR / "evals.template.yaml"),
}


def build_context(*, use_defaults: bool, json_context: dict[str, str], cli_context: dict[str, str]) -> dict[str, str]:
    return build_context_with_defaults(
        default_context=DEFAULT_CONTEXT,
        use_defaults=use_defaults,
        json_context=json_context,
        cli_context=cli_context,
    )


def render_one(*, template_path: Path, output_path: Path, context: dict[str, str]) -> None:
    rendered = render_from_path(template_path=template_path, context=context)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(ensure_trailing_newline(rendered), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render skill-builder reference templates.")
    parser.add_argument(
        "--target",
        choices=["contract", "evals", "all"],
        default="all",
        help="Template target to render.",
    )
    parser.add_argument("--vars-json", help="Optional JSON object with template variables.")
    parser.add_argument("--var", action="append", default=[], help="Inline variable override (KEY=VALUE).")
    parser.add_argument("--no-defaults", action="store_true", help="Do not pre-seed context with built-in defaults.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        json_context = load_json_context(Path(args.vars_json).expanduser().resolve()) if args.vars_json else {}
        cli_context = dict(parse_key_value(item) for item in args.var)
        context = build_context(use_defaults=not args.no_defaults, json_context=json_context, cli_context=cli_context)
        targets = TEMPLATE_TARGETS.items() if args.target == "all" else [(args.target, TEMPLATE_TARGETS[args.target])]
        for name, (template_path, output_path) in targets:
            render_one(template_path=template_path, output_path=output_path, context=context)
            print(f"[OK] Rendered {name}: {output_path}")
    except TemplateRenderError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
