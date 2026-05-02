#!/usr/bin/env python3
"""Render he-plan/plan.md.tmpl into Infrastructure/references/plan-template.md."""

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
    print_diff_lines,  # noqa: F401 - re-exported for check_plan_template_drift.py
    render_from_path,
    unified_diff_lines,  # noqa: F401 - re-exported for check_plan_template_drift.py
)

DEFAULT_TEMPLATE_PATH = SKILL_DIR / "plan.md.tmpl"
DEFAULT_OUTPUT_PATH = SKILL_DIR / "references" / "plan-template.md"

DEFAULT_CONTEXT: dict[str, str] = {
    "PLAN_TITLE": "Symphony Service Implementation Plan",
    "PLAN_TYPE": "feat",
    "PLAN_STATUS": "active",
    "PLAN_DATE": "2026-04-10",
    "PLAN_ORIGIN": "docs/brainstorms/2026-04-10-symphony-requirements.md",
    "PLAN_REQUIREMENTS": "docs/brainstorms/2026-04-10-symphony-requirements.md",
    "PLAN_SPEC": "Docs/specs/2026-04-10-symphony-service-spec.md",
    "PLAN_SOURCE_SPEC": "docs/specs/2026-04-10-symphony-service-spec.md",
    "PLAN_UI_SPEC": "docs/ui-specs/2026-04-10-symphony-ops-ui-spec.md",
    "LINEAR_PROJECT": "JSC",
    "LINEAR_ISSUE": "JSC-200",
    "LINEAR_PARENT": "JSC-190",
    "LINEAR_CHILDREN": "[]",
    "LINEAR_PARENT_CHILDREN": "JSC-190 parent, no child issues yet",
    "LINEAR_STATUS": "In Progress",
    "PLAN_BRANCH": "feature/JSC-200-symphony-service",
    "PLAN_PATH": "Docs/plans/2026-04-10-feat-symphony-service-plan.md",
    "SOURCE_ACCEPTANCE_1": "SA1",
    "SOURCE_ACCEPTANCE_2": "SA2",
    "PLAN_ROUTE": "fresh",
    "PLAN_DEPTH": "deep",
    "OVERVIEW_SUMMARY": "Ship a first implementation of Symphony orchestrator behavior with deterministic retry and workspace safety.",
    "PROBLEM_FRAME": "Current issue execution is manual and inconsistent; this plan defines an auditable implementation path.",
    "REQ_1": "Poll eligible tracker work and dispatch within bounded concurrency.",
    "REQ_2": "Keep per-issue work isolated and observable.",
    "NON_GOAL_1": "Do not build a multi-tenant control plane.",
    "NON_GOAL_2": "Do not embed ticket business logic in the orchestrator.",
    "PATTERN_1": "services/symphony/orchestrator.py and existing worker lifecycle wrappers",
    "LEARNING_1": "Reuse prior retry/backoff handling from queue processors to avoid duplicate claim races.",
    "EXTERNAL_REF_1": "Linear GraphQL pagination documentation",
    "DECISION_1": "Single-authority in-memory orchestrator state",
    "DECISION_1_RATIONALE": "Simplifies idempotency and makes restart recovery tracker-driven.",
    "RESOLVED_QUESTION_1": "Should retries persist across process restart",
    "RESOLVED_ANSWER_1": "No; restart recovery is tracker + workspace based.",
    "DEFERRED_QUESTION_1": "Should we support remote SSH workers in v1",
    "DEFERRED_RATIONALE_1": "Kept as extension after core local reliability is proven.",
    "UNIT_1_NAME": "Orchestrator state and poll loop",
    "UNIT_1_GOAL": "Stand up deterministic poll->reconcile->dispatch sequencing.",
    "UNIT_1_REQUIREMENTS": "R1, R2",
    "UNIT_1_DEPENDENCIES": "None",
    "UNIT_1_CREATE_FILE": "services/symphony/orchestrator.py",
    "UNIT_1_MODIFY_FILE": "services/symphony/main.py",
    "UNIT_1_TEST_FILE": "Infrastructure/tests/symphony/test_orchestrator.py",
    "UNIT_1_APPROACH": "Introduce a single runtime-state object and serialize all mutations in the scheduler loop.",
    "UNIT_1_PATTERN": "Follow existing queue scheduler instrumentation conventions",
    "UNIT_1_TEST_SCENARIO_1": "Dispatch occurs only for active and unclaimed issues.",
    "UNIT_1_TEST_SCENARIO_2": "Terminal-state issue stops running worker and releases claim.",
    "UNIT_1_VERIFICATION": "Scheduler logs show deterministic tick stages and expected issue transitions.",
    "IMPACT_INTERACTION": "Issue tracker adapter, workspace manager, and agent runner all route through orchestrator callbacks.",
    "IMPACT_ERRORS": "Worker failure and timeout map to retry queue entries with bounded backoff.",
    "IMPACT_STATE": "Claim set and running map must stay consistent through abnormal worker exits.",
    "IMPACT_API_PARITY": "Status APIs mirror the same running/retrying state model.",
    "IMPACT_INTEGRATION": "Integration tests must cover poll, reconcile, retry timer, and shutdown behavior together.",
    "RISK_1": "Tracker API outages could starve dispatch; mitigation is skip-and-retry with operator-visible logs.",
    "DOC_NOTE_1": "Document workflow frontmatter keys and runtime reload behavior in operations docs.",
    "OWNER": "planning-agent",
    "INITIAL_EVIDENCE": "plan scaffold generated",
    "SOURCE_ORIGIN": "docs/brainstorms/2026-04-10-symphony-requirements.md",
    "SOURCE_CODE": "services/symphony/*",
    "SOURCE_ISSUES": "JSC-200",
    "SOURCE_EXTERNAL": "https://linear.app/developers/graphql",
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
    Parse command-line arguments for rendering the he-plan template.
    
    Parameters:
        argv: Sequence of command-line arguments to parse; if None, the process's argv is used.
    
    Returns:
        argparse.Namespace: Parsed arguments with attributes:
            - template: Path to the template file.
            - output: Path to the rendered markdown file.
            - vars_json: Optional path to a JSON file containing template variables.
            - var: List of inline KEY=VALUE overrides.
            - no_defaults: True when built-in defaults should not be seeded into the context.
            - stdout: True when the rendered output should be written to stdout instead of a file.
    """
    parser = argparse.ArgumentParser(description="Render he-plan/plan.md.tmpl to markdown.")
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
