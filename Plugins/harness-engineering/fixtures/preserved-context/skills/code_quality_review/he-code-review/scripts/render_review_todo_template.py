#!/usr/bin/env python3
"""Render he-code-review/review-todo.md.tmpl into references/review-todo-template.md."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
FAMILY_SKILLS_DIR = SCRIPT_DIR.parents[1]
for candidate in [FAMILY_SKILLS_DIR, *(parent / "skills" for parent in SCRIPT_DIR.parents)]:
    if (candidate / "_template_utils.py").exists():
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
        break

from _template_utils import (  # noqa: E402
    TemplateRenderError,
    build_context as build_context_with_defaults,
    ensure_trailing_newline,
    load_json_context,
    parse_key_value,
    print_diff_lines,  # noqa: F401 - re-exported for check_review_todo_template_drift.py
    render_from_path,
    unified_diff_lines,  # noqa: F401 - re-exported for check_review_todo_template_drift.py
)

DEFAULT_TEMPLATE_PATH = SKILL_DIR / "review-todo.md.tmpl"
DEFAULT_OUTPUT_PATH = SKILL_DIR / "references" / "review-todo-template.md"

DEFAULT_CONTEXT: dict[str, str] = {
    "TODO_STATUS": "pending",
    "TODO_PRIORITY": "P2",
    "TODO_ID": "003",
    "TODO_TAG": "quality",
    "TODO_DEPENDENCY": "none",
    "TODO_TITLE": "stabilize-orchestrator-state-reconciliation",
    "PROBLEM_STATEMENT": "Reconciliation can leave stale running entries after worker failures, causing duplicate or blocked dispatch.",
    "FINDING_1": "Retry queue entries are created without clearing stale running metadata in one failure path.",
    "FINDING_2": "Terminal-state transitions are not always reflected before slot calculations.",
    "AFFECTED_FILE_1": "services/symphony/orchestrator.py",
    "AFFECTED_FILE_2": "Infrastructure/tests/symphony/test_orchestrator_retries.py",
    "EVIDENCE_1": "Review trace from he-code-review finding set P1/P2 batch",
    "OPTION_A_NAME": "Minimal corrective patch",
    "OPTION_A_APPROACH": "Fix stale-entry cleanup in the failure/retry transition only.",
    "OPTION_A_PROS": "Low risk and fast to ship.",
    "OPTION_A_CONS": "May leave hidden coupling in other transitions.",
    "OPTION_A_EFFORT": "small",
    "OPTION_A_RISK": "medium",
    "OPTION_B_NAME": "Consolidated state-transition helper",
    "OPTION_B_APPROACH": "Centralize running/claimed/retry mutations in one helper used by all exit paths.",
    "OPTION_B_PROS": "Reduces future drift and improves auditability.",
    "OPTION_B_CONS": "Touches more code paths and tests.",
    "OPTION_B_EFFORT": "medium",
    "OPTION_B_RISK": "medium",
    "RECOMMENDED_ACTION": "Implement Option B and extend tests to cover abnormal exit + terminal refresh ordering.",
    "AC_1": "No stale running entry remains after abnormal worker exit.",
    "AC_2": "Retry scheduling and slot math remain consistent under terminal transitions.",
    "AC_3": "Regression tests cover both failure and terminal reconciliation paths.",
    "TODO_DATE": "2026-04-10",
    "REVIEWER": "he-code-review",
    "WORK_LOG_NOTE": "Initial triage complete; ready for implementation planning.",
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
    """
    Parse command-line arguments for the review-todo renderer.
    
    Parameters:
        argv (list[str] | None): Optional list of arguments to parse (typically sys.argv[1:]). If None, arguments are read from the environment.
    
    Returns:
        argparse.Namespace: Parsed arguments with attributes:
            - template: Path to the template file.
            - output: Path to the rendered markdown file.
            - vars_json: Optional path to a JSON file containing template variables.
            - var: List of inline KEY=VALUE overrides.
            - no_defaults: True if built-in default context should be disabled.
            - stdout: True if rendered output should be printed to stdout.
    """
    parser = argparse.ArgumentParser(description="Render he-code-review/review-todo.md.tmpl to markdown.")
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
