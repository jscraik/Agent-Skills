#!/usr/bin/env python3
"""Render plugin-creator templates into reference sample files."""

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
    print_diff_lines,
    render_from_path,
    render_template,
    unified_diff_lines,
)

TEMPLATE_DIR = SKILL_DIR / "templates"
REFERENCE_DIR = SKILL_DIR / "references"

TEMPLATE_TARGETS: dict[str, tuple[Path, Path]] = {
    "plugin_manifest": (TEMPLATE_DIR / "plugin.json.tmpl", REFERENCE_DIR / "plugin-manifest.sample.json"),
    "marketplace_entry": (
        TEMPLATE_DIR / "marketplace-entry.json.tmpl",
        REFERENCE_DIR / "marketplace-entry.sample.json",
    ),
}

DEFAULT_CONTEXT: dict[str, str] = {
    "PLUGIN_NAME": "symphony-orchestrator",
    "PLUGIN_VERSION": "0.1.0",
    "PLUGIN_DESCRIPTION": "Coordinates issue-driven coding-agent workspaces with deterministic orchestration policy.",
    "AUTHOR_NAME": "Symphony Maintainers",
    "AUTHOR_EMAIL": "maintainers@example.com",
    "AUTHOR_URL": "https://github.com/example",
    "HOMEPAGE_URL": "https://example.com/plugins/symphony-orchestrator",
    "REPOSITORY_URL": "https://github.com/example/symphony-orchestrator",
    "LICENSE_ID": "MIT",
    "KEYWORD_1": "orchestration",
    "KEYWORD_2": "agent-workflow",
    "INTERFACE_DISPLAY_NAME": "Symphony Orchestrator",
    "INTERFACE_SHORT_DESCRIPTION": "Run issue-driven coding workflows with guardrails.",
    "INTERFACE_LONG_DESCRIPTION": "A plugin for deterministic issue polling, workspace isolation, and coding-agent orchestration.",
    "INTERFACE_DEVELOPER_NAME": "Symphony Maintainers",
    "INTERFACE_CATEGORY": "Productivity",
    "INTERFACE_WEBSITE_URL": "https://example.com/plugins/symphony-orchestrator",
    "INTERFACE_PRIVACY_URL": "https://example.com/privacy",
    "INTERFACE_TERMS_URL": "https://example.com/terms",
    "DEFAULT_PROMPT_1": "Review active issues and dispatch the highest priority task.",
    "DEFAULT_PROMPT_2": "Summarize running sessions and retry queue risk.",
    "DEFAULT_PROMPT_3": "Prepare an operator handoff for blocked orchestration runs.",
    "INTERFACE_BRAND_COLOR": "#3B82F6",
    "INSTALL_POLICY": "AVAILABLE",
    "AUTH_POLICY": "ON_INSTALL",
    "PRODUCT_1": "CODEX",
    "CATEGORY": "Productivity",
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
    parser = argparse.ArgumentParser(description="Render plugin-creator template samples.")
    parser.add_argument(
        "--target",
        choices=["plugin_manifest", "marketplace_entry", "all"],
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
