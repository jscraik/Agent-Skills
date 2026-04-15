#!/usr/bin/env python3
"""Render skill-creator handoff-package.md.tmpl into Infrastructure/references/handoff-package-scaffold.md."""

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

DEFAULT_TEMPLATE_PATH = SKILL_DIR / "templates" / "handoff-package.md.tmpl"
DEFAULT_OUTPUT_PATH = SKILL_DIR / "references" / "handoff-package-scaffold.md"

DEFAULT_CONTEXT: dict[str, str] = {
    "SKILL_GOAL": "Provide deterministic issue-to-workspace orchestration guidance for coding agent sessions.",
    "IN_SCOPE": "Scaffold, route, and validate the core orchestration skill contract and references.",
    "OUT_OF_SCOPE": "Plugin distribution, installer wiring, and marketplace publication.",
    "DELIVERABLE_BOUNDARY": "Standalone skill package ready for skill-builder hardening.",
    "SHOULD_TRIGGER_1": "Build a skill that orchestrates issue polling with bounded concurrency.",
    "SHOULD_TRIGGER_2": "Scaffold a new skill for deterministic worker retry and reconciliation behavior.",
    "SHOULD_NOT_TRIGGER_1": "Package this as a plugin and publish marketplace metadata now.",
    "SHOULD_NOT_TRIGGER_2": "Install this skill to my global catalog only.",
    "SCRIPT_RESOURCE_1": "Infrastructure/scripts/init_skill.py (scaffold + metadata generation)",
    "REFERENCE_RESOURCE_1": "Infrastructure/references/creation-playbook.md (stage and quality checklist)",
    "ASSET_RESOURCE_1": "none",
    "METADATA_NOTE_1": "openai.yaml scaffolded by init script; lifecycle values marked for hardening.",
    "STARTER_PROMPT_1": "Create a skill that turns tracker issues into deterministic worker runs.",
    "STARTER_PROMPT_2": "Scaffold a router skill for issue-state based dispatch policies.",
    "STARTER_PROMPT_3": "Draft a skill with strict template-backed references and drift checks.",
    "RISK_OR_UNKNOWN_1": "Trigger boundaries may overlap with plugin-factory lanes without clear handoff notes.",
    "VALIDATION_COMMAND": "python3 Plugins/skill-factory/skills/skill-creator/Infrastructure/scripts/init_skill.py orchestration --path /tmp --resources references",
    "VALIDATION_RESULT": "pass",
    "VALIDATION_NOTES": "Scaffold command executes and writes template-backed SKILL.md output.",
    "AUTHORING_STAGE": "scaffold_complete",
    "HANDOFF_REASON": "Requires eval calibration and contract hardening before install/plugin handoff.",
}


def build_context(*, use_defaults: bool, json_context: dict[str, str], cli_context: dict[str, str]) -> dict[str, str]:
    return build_context_with_defaults(
        default_context=DEFAULT_CONTEXT,
        use_defaults=use_defaults,
        json_context=json_context,
        cli_context=cli_context,
    )


def render_from_paths(*, template_path: Path, context: dict[str, str]) -> str:
    return render_from_path(template_path=template_path, context=context)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render skill-creator handoff template to markdown.")
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
