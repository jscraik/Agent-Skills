#!/usr/bin/env python3
"""Render plugin-builder templates into reference sample files."""

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

TEMPLATE_DIR = SKILL_DIR / "templates"
REFERENCE_DIR = SKILL_DIR / "references"

DEFAULT_TEMPLATE_PATH = TEMPLATE_DIR / "hooks.json.tmpl"
DEFAULT_OUTPUT_PATH = REFERENCE_DIR / "hooks.template.json"

DEFAULT_CONTEXT: dict[str, str] = {
    "SESSION_START_MATCHER": ".*",
    "SESSION_START_COMMAND": "./Infrastructure/scripts/hooks/session_start_check.sh",
    "SESSION_START_TIMEOUT_SECONDS": "30",
    "SESSION_START_STATUS_MESSAGE": "Validating session startup contract",
    "STOP_MATCHER": ".*",
    "STOP_COMMAND": "./Infrastructure/scripts/hooks/stop_guard.sh",
    "STOP_TIMEOUT_SECONDS": "15",
    "STOP_STATUS_MESSAGE": "Evaluating stop hook guardrails",
}


def build_context(*, use_defaults: bool, json_context: dict[str, str], cli_context: dict[str, str]) -> dict[str, str]:
    """
    Build a template context by merging provided contexts with optional defaults.
    
    Parameters:
    	use_defaults (bool): Whether to seed the context with DEFAULT_CONTEXT
    	json_context (dict[str, str]): Context loaded from a JSON file
    	cli_context (dict[str, str]): Context from CLI variable overrides
    
    Returns:
    	dict[str, str]: A merged context dictionary for template rendering
    """
    return build_context_with_defaults(
        default_context=DEFAULT_CONTEXT,
        use_defaults=use_defaults,
        json_context=json_context,
        cli_context=cli_context,
    )


def render_from_paths(*, template_path: Path, context: dict[str, str]) -> str:
    """
    Render a template file with the provided context variables.
    
    Returns:
        str: Rendered template content.
    """
    return render_from_path(template_path=template_path, context=context)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """
    Parse command-line arguments for rendering plugin-builder hooks templates.
    
    Parameters:
        argv (list[str] | None): Argument list to parse; if None, defaults to process arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments with attributes:
            - template (str): Path to the template file.
            - output (str): Path to the rendered output file.
            - vars_json (str | None): Path to an optional JSON file with template variables.
            - var (list[str]): Inline variable overrides as `KEY=VALUE` strings.
            - no_defaults (bool): Whether to disable seeding with built-in defaults.
            - stdout (bool): Whether to print rendered output to stdout instead of writing a file.
    """
    parser = argparse.ArgumentParser(description="Render plugin-builder hooks template sample.")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE_PATH), help="Path to template file.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Path to rendered output file.")
    parser.add_argument("--vars-json", help="Optional JSON object with template variables.")
    parser.add_argument("--var", action="append", default=[], help="Inline variable override (KEY=VALUE).")
    parser.add_argument("--no-defaults", action="store_true", help="Do not pre-seed context with built-in defaults.")
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print rendered output to stdout instead of writing file.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """
    Render a plugin-builder hooks template using configuration from files and command-line arguments.
    
    Loads template variables from a JSON file and CLI overrides, merges them with optional defaults, renders the template, and writes the output to a file or stdout.
    
    Parameters:
        argv: Optional list of command-line arguments; if None, uses sys.argv.
    
    Returns:
        Exit code: 0 on successful render and output, 1 if template rendering fails.
    """
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
