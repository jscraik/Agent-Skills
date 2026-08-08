from __future__ import annotations

import argparse

from ask.skills_sdk.lenses import KNOWN_TASK_INTENTS
from ask.skills_sdk.placeholder_lifecycle import SURFACES


def add_project_mutation_parsers(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    improve = sdk_subparsers.add_parser(
        "improve",
        help="Run a project-local skill improvement lifecycle gate",
        parents=[global_parser],
    )
    improve.add_argument("target", help="Project-local SKILL.md source path")
    improve.add_argument("--project-root", required=True, help="Absolute marked project root containing skills-sdk.json")
    improve.add_argument("--evals", action="store_true", help="Run the SDK internal eval lane before recording the decision")
    improve.add_argument("--mode", choices=["smoke", "release"], default="smoke", help="Eval mode when --evals is set")
    improve.add_argument("--codex-profile", help="Override the Codex config profile for the internal eval lane")
    improve.add_argument("--preview", action="store_true", help="Plan the improvement lifecycle evidence without writes")
    improve.add_argument("--apply", action="store_true", help="Write owner-repo registry, event, and receipt evidence")

    install = sdk_subparsers.add_parser("install", help="Preview or apply a bounded Skills SDK project install", parents=[global_parser])
    install.add_argument("target", help="Skill handle or repo-relative skill source path")
    install.add_argument("--preview", action="store_true", help="Plan the install without performing writes")
    install.add_argument("--apply", action="store_true", help="Perform a real project install")
    install.add_argument("--project-root", help="Absolute marked project root for --apply installs")
    install.add_argument("--scope", choices=["project", "workspace", "global"], default="project", help="Install scope to model in the preview; real installs only support project")

    rollback = sdk_subparsers.add_parser("rollback", help="Preview or apply receipt-proven Skills SDK project rollback", parents=[global_parser])
    rollback.add_argument("--receipt", required=True, help="Path to a Skills SDK project install receipt")
    rollback.add_argument("--preview", action="store_true", help="Plan rollback without performing writes")
    rollback.add_argument("--apply", action="store_true", help="Perform rollback in an explicit project root")
    rollback.add_argument("--project-root", help="Absolute marked project root for live validation or apply")

    uninstall = sdk_subparsers.add_parser("uninstall", help="Preview or apply receipt-proven Skills SDK project uninstall", parents=[global_parser])
    uninstall.add_argument("skill_id", help="Installed skill id to resolve through skills.lock.json")
    uninstall.add_argument("--preview", action="store_true", help="Plan uninstall without performing writes")
    uninstall.add_argument("--apply", action="store_true", help="Perform uninstall in an explicit project root")
    uninstall.add_argument("--project-root", required=True, help="Absolute marked project root containing skills.lock.json")


def add_lifecycle_status_parsers(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    lifecycle = sdk_subparsers.add_parser(
        "lifecycle",
        help="Emit honest placeholder lifecycle receipts for unavailable V1.0 surfaces",
        parents=[global_parser],
    )
    lifecycle.add_argument("--surface", choices=list(SURFACES), help="Limit output to one lifecycle surface")
    lifecycle.add_argument(
        "--risk-tier",
        choices=["low", "medium", "high", "privileged", "published"],
        default="medium",
        help="Risk tier used to decide whether unavailable adapters block",
    )
    sdk_subparsers.add_parser("status", help="Report the Skills SDK capability truth matrix", parents=[global_parser])


def add_project_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = sdk_subparsers.add_parser("project", help="Inspect read-only Skills SDK project conformance", parents=[global_parser])
    subparsers = parser.add_subparsers(dest="project_action", required=True)
    for project_action in ("status", "doctor"):
        project_parser = subparsers.add_parser(project_action, help=f"Run read-only Skills SDK project {project_action}", parents=[global_parser])
        project_parser.add_argument("--project-root", required=True, help="Absolute marked project root to inspect without mutation")


def add_lenses_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = sdk_subparsers.add_parser("lenses", help="List, explain, validate, or select generic SDK lenses", parents=[global_parser])
    subparsers = parser.add_subparsers(dest="lenses_action", required=True)
    list_parser = subparsers.add_parser("list", help="List the shared SDK lens catalog", parents=[global_parser])
    explain = subparsers.add_parser("explain", help="Explain one shared SDK lens", parents=[global_parser])
    explain.add_argument("lens_id", help="Lens id, for example lens.progressive-disclosure")
    validate = subparsers.add_parser("validate", help="Validate the shared SDK lens catalog", parents=[global_parser])
    select = subparsers.add_parser("select", help="Select shared SDK lenses for a task using deterministic signals", parents=[global_parser])
    select.add_argument("--prompt", required=True, help="Task prompt or summary to route through lenses")
    select.add_argument("--skill", help="Optional skill handle or path receiving the lenses")
    select.add_argument("--intent", "--task-intent", dest="task_intent", choices=list(KNOWN_TASK_INTENTS), help="Optional normalized task intent; inferred from prompt when omitted")
    select.add_argument("--repo-file", action="append", default=[], help="Repo-relative file signal to include in selection; repeat for multiple files")
    select.add_argument("--max-lenses", type=int, default=4, help="Maximum selected lenses to return")
    parser.add_argument("--registry", help="Optional repo-relative or absolute lens registry path")
    for registry_parser in (list_parser, explain, validate, select):
        registry_parser.add_argument("--registry", default=argparse.SUPPRESS, help="Optional repo-relative or absolute lens registry path")


def add_determinism_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = sdk_subparsers.add_parser("determinism", help="Find skill guidance that can become deterministic SDK checks", parents=[global_parser])
    subparsers = parser.add_subparsers(dest="determinism_action", required=True)
    audit = subparsers.add_parser("audit", help="Audit skills for prompt-only rules that can become validators, schemas, or selectors", parents=[global_parser])
    audit.add_argument("--scope", choices=["skills"], default="skills", help="Audit scope; currently scans canonical skill source roots")
    audit.add_argument("--path", action="append", default=[], help="Skill directory or SKILL.md path to audit; repeat for multiple paths")
    audit.add_argument("--limit", type=int, help="Limit returned candidates after deterministic priority sorting")


def add_review_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = sdk_subparsers.add_parser("review", help="Plan read-only SDK reviews using deterministic lens selection", parents=[global_parser])
    subparsers = parser.add_subparsers(dest="review_action", required=True)
    plan = subparsers.add_parser("plan", help="Emit a schema-backed read-only review plan receipt", parents=[global_parser])
    plan.add_argument("--target", required=True, help="Repo path or handle to review")
    plan.add_argument("--intent", "--task-intent", dest="task_intent", choices=list(KNOWN_TASK_INTENTS), required=True, help="Normalized review intent used for lens selection")
    plan.add_argument("--prompt", help="Optional review prompt or summary")
    plan.add_argument("--repo-file", action="append", default=[], help="Repo-relative file signal to include in review routing; repeat for multiple paths")
    plan.add_argument("--max-lenses", type=int, default=4, help="Maximum selected lenses to include in the review plan")
    plan.add_argument("--receipt-out", help="Optional repo-local path for writing the review plan receipt")

    handoff = subparsers.add_parser("handoff", help="Emit a schema-backed read-only review handoff receipt from a review plan receipt", parents=[global_parser])
    handoff.add_argument("--plan", required=True, help="Repo-local review plan receipt path")
    handoff.add_argument("--target", required=True, help="Repo path or handle from the source review plan")
    handoff.add_argument("--intent", "--task-intent", dest="task_intent", choices=list(KNOWN_TASK_INTENTS), required=True, help="Normalized review intent from the source review plan")
    handoff.add_argument("--receipt-out", help="Optional repo-local path for writing the review handoff receipt")

    execute = subparsers.add_parser("execute", help="Materialize required local review artifacts from a review handoff receipt", parents=[global_parser])
    execute.add_argument("--handoff", required=True, help="Repo-local review handoff receipt path")
    execute.add_argument("--receipt-out", help="Optional repo-local path for writing the review execution receipt")
    verify = subparsers.add_parser("verify", help="Verify required local artifacts from a review handoff receipt without external readiness claims", parents=[global_parser])
    verify.add_argument("--handoff", required=True, help="Repo-local review handoff receipt path")
    verify.add_argument("--receipt-out", help="Optional repo-local path for writing the review verification receipt")
