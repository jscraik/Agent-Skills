#!/usr/bin/env python3
"""Render he-technical-review/finding.md.tmpl into references/finding-template.md."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
FAMILY_SKILLS_DIR = None
for parent in SCRIPT_DIR.parents:
    candidate = parent / "skills" / "_template_utils.py"
    if candidate.exists():
        FAMILY_SKILLS_DIR = parent / "skills"
        break
if FAMILY_SKILLS_DIR is None:
    raise RuntimeError(f"Unable to locate skills/_template_utils.py from {SCRIPT_DIR}")
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

DEFAULT_TEMPLATE_PATH = SKILL_DIR / "finding.md.tmpl"
DEFAULT_OUTPUT_PATH = SKILL_DIR / "references" / "finding-template.md"

DEFAULT_CONTEXT: dict[str, str] = {
    "TARGET_ARTIFACT": "pull request diff",
    "TARGET_REF": "PR #123",
    "REVIEW_MODE": "code-diff",
    "FINDING_ID": "F1",
    "SEVERITY": "P1",
    "LOCATION": "services/symphony/orchestrator.py:244",
    "WHY_IT_MATTERS": "Stale running entries can block dispatch and skew retry accounting.",
    "RECOMMENDED_FIX": "Remove stale running map entry before scheduling retry in all abnormal exits.",
    "CONFIDENCE": "0.87",
    "FINDING_ID_2": "F2",
    "SEVERITY_2": "P2",
    "LOCATION_2": "Infrastructure/tests/symphony/test_orchestrator_retries.py:88",
    "WHY_IT_MATTERS_2": "Missing terminal-transition coverage leaves regression risk.",
    "RECOMMENDED_FIX_2": "Add a reconciliation test that transitions active->terminal while retry timer is queued.",
    "CONFIDENCE_2": "0.74",
    "NO_CRITICAL_FINDINGS": "false",
    "FEEDBACK_RESPONSE_PLAN": "push_back_with_evidence",
    "FEEDBACK_RESPONSE_PLAN_RATIONALE": "Current implementation already satisfies compatibility constraints documented in the plan.",
    "QUESTION_1": "Assumes tracker refresh semantics remain consistent during pagination.",
    "NEXT_ACTION": "Fix F1 first, then rerun targeted tests and re-review the updated diff.",
    "CHANGE_SUMMARY_1": "No code changed yet; this artifact captures actionable review findings.",
    "RESIDUAL_RISK_1": "Concurrent worker exits may still race if state updates happen outside orchestrator authority.",
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
    Parse command-line arguments for rendering the finding template.
    
    Parameters:
        argv (list[str] | None): Optional list of CLI arguments to parse; if None, parses from sys.argv.
    
    Returns:
        argparse.Namespace: Parsed arguments with attributes: `template`, `output`, `vars_json`, `var` (list of KEY=VALUE strings), `no_defaults`, and `stdout`.
    """
    parser = argparse.ArgumentParser(description="Render he-technical-review/finding.md.tmpl to markdown.")
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
