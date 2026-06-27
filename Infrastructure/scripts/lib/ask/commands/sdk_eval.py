from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path

import ask.commands.skills as skills_commands
from ask.cli_errors import build_unknown_action_result, build_validation_error
from ask.commands.skills_impl import TESSL_REVIEW_MIN_SCORE
from ask.envelope import CallResult


_AB_PROFILE_CHOICES = ("oss-local", "oss-cloud", "codex-fast")
_EXECUTION_PROFILE_CHOICES = ("codex-read-only", "codex-workspace-write")


def add_sdk_eval_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = sdk_subparsers.add_parser("eval", help="Run Skills SDK eval receipts", parents=[global_parser])
    subparsers = parser.add_subparsers(dest="eval_action", required=True)
    _add_run_parser(subparsers, global_parser)
    _add_scenario_quality_parser(subparsers, global_parser)
    _add_scorer_quality_parser(subparsers, global_parser)
    _add_scorer_calibration_parser(subparsers, global_parser)
    _add_tessl_score_parser(subparsers, global_parser)
    _add_tessl_local_proof_parser(subparsers, global_parser)
    _add_regression_plan_parser(subparsers, global_parser)
    _add_handoff_readiness_parser(subparsers, global_parser)
    _add_profiles_parser(subparsers, global_parser)
    _add_ab_rubric_parser(subparsers, global_parser)
    _add_ab_preview_parser(subparsers, global_parser)
    _add_ab_plan_parser(subparsers, global_parser)
    _add_ab_run_parser(subparsers, global_parser)
    _add_ab_judge_preview_parser(subparsers, global_parser)
    _add_ab_judge_score_parser(subparsers, global_parser)


def _add_run_parser(subparsers: argparse._SubParsersAction, global_parser: argparse.ArgumentParser) -> None:
    run = subparsers.add_parser("run", help="Run internal skill evals or exact-match deterministic eval cases", parents=[global_parser])
    run.add_argument("target", nargs="?", help="Skill handle or source path for the internal eval runner")
    run.add_argument("--dataset", help="Repo-relative or absolute deterministic eval dataset")
    run.add_argument("--skill", help="Optional skill handle or source path for deterministic evals")
    run.add_argument("--runner", choices=["auto", "internal", "deterministic-jsonl"], default="auto")
    run.add_argument("--mode", choices=["smoke", "release"], default="smoke", help="Internal eval mode.")
    run.add_argument("--case", action="append", dest="cases", help="Internal eval case id filter.")
    run.add_argument("--codex-profile", help="Override the Codex config profile for the internal eval runner.")
    run.add_argument("--timeout-seconds", type=_positive_int, help="Override the internal eval runner timeout.")
    run.add_argument("--with-tessl", action="store_true", help="Allow internal Tessl continuation.")


def _add_scenario_quality_parser(subparsers: argparse._SubParsersAction, global_parser: argparse.ArgumentParser) -> None:
    quality = subparsers.add_parser("scenario-quality", help="Preview eval scenario promotion quality", parents=[global_parser])
    quality.add_argument("target", help="Skill handle or repo-relative skill source path")
    quality.add_argument("--preview", action="store_true", help="Emit a non-mutating scenario quality receipt")


def _add_scorer_quality_parser(subparsers: argparse._SubParsersAction, global_parser: argparse.ArgumentParser) -> None:
    quality = subparsers.add_parser("scorer-quality", help="Preview eval scorer calibration quality", parents=[global_parser])
    quality.add_argument("target", help="Skill handle or repo-relative skill source path")
    quality.add_argument("--preview", action="store_true", help="Emit a non-mutating scorer quality receipt")


def _add_scorer_calibration_parser(subparsers: argparse._SubParsersAction, global_parser: argparse.ArgumentParser) -> None:
    calibration = subparsers.add_parser("scorer-calibration", help="Preview held-out scorer calibration evidence", parents=[global_parser])
    calibration.add_argument("target", help="Skill handle or repo-relative skill source path")
    calibration.add_argument("--preview", action="store_true", help="Emit a non-mutating scorer calibration receipt")


def _add_tessl_score_parser(subparsers: argparse._SubParsersAction, global_parser: argparse.ArgumentParser) -> None:
    score = subparsers.add_parser("tessl-score", help="Preview a Tessl score receipt from eval view JSON", parents=[global_parser])
    score.add_argument("--view-json", required=True, help="Path to tessl eval view --json output")
    score.add_argument("--skill", required=True, help="Skill handle or repo-relative source path represented by the run")
    score.add_argument("--run-id", help="Expected Tessl eval run id")
    score.add_argument("--preview", action="store_true", help="Emit a non-mutating Tessl score receipt")


def _add_tessl_local_proof_parser(subparsers: argparse._SubParsersAction, global_parser: argparse.ArgumentParser) -> None:
    proof = subparsers.add_parser(
        "tessl-local-proof",
        help="Preview or run local Tessl lint, pack, file install, and optional review proof",
        parents=[global_parser],
    )
    proof.add_argument("--skill", required=True, help="Skill handle or repo-relative source path represented by the proof")
    proof.add_argument("--workspace", required=True, help="Tessl workspace used for staged private package identity")
    mode = proof.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true", help="Emit a non-mutating local Tessl proof plan")
    mode.add_argument("--execute", action="store_true", help="Run temp-staged local Tessl lint, pack, and file install checks")
    proof.add_argument("--include-review", action="store_true", help="Also run Tessl async review threshold check")
    proof.add_argument("--review-threshold", type=_positive_int, default=TESSL_REVIEW_MIN_SCORE)
    proof.add_argument("--timeout-seconds", type=_positive_int, default=180)


def _add_regression_plan_parser(subparsers: argparse._SubParsersAction, global_parser: argparse.ArgumentParser) -> None:
    plan = subparsers.add_parser("regression-plan", help="Preview a regression owner classification plan from Tessl score evidence", parents=[global_parser])
    plan.add_argument("--view-json", required=True, help="Path to tessl eval view --json output")
    plan.add_argument("--skill", required=True, help="Skill handle or repo-relative source path represented by the run")
    plan.add_argument("--run-id", help="Expected Tessl eval run id")
    plan.add_argument("--plan-json", help="Optional explicit regression plan JSON artifact")
    plan.add_argument("--preview", action="store_true", help="Emit a non-mutating regression plan receipt")


def _add_handoff_readiness_parser(subparsers: argparse._SubParsersAction, global_parser: argparse.ArgumentParser) -> None:
    readiness = subparsers.add_parser("handoff-readiness", help="Preview the required local and internal evidence gate before live Tessl", parents=[global_parser])
    readiness.add_argument("--skill", required=True, help="Skill handle or repo-relative source path represented by the handoff")
    readiness.add_argument("--receipt-json", help="Optional explicit handoff readiness JSON artifact")
    readiness.add_argument("--preview", action="store_true", help="Emit a non-mutating handoff readiness receipt")


def _add_profiles_parser(subparsers: argparse._SubParsersAction, global_parser: argparse.ArgumentParser) -> None:
    profiles = subparsers.add_parser("profiles", help="Preview Codex execution and judge profiles", parents=[global_parser])
    profiles.add_argument("--preview", action="store_true", help="Emit a non-mutating eval profile receipt")


def _add_ab_rubric_parser(subparsers: argparse._SubParsersAction, global_parser: argparse.ArgumentParser) -> None:
    rubric = subparsers.add_parser("ab-rubric", help="Preview the canonical A/B scoring rubric", parents=[global_parser])
    rubric.add_argument("--preview", action="store_true", help="Emit a non-mutating A/B rubric receipt")


def _add_ab_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--skill-a", required=True, help="Skill handle or repo-relative source path for variant A")
    parser.add_argument("--skill-b", required=True, help="Skill handle or repo-relative source path for variant B")
    parser.add_argument("--fixture", required=True, help="Repo-relative A/B task fixture")
    parser.add_argument("--execution-profile", choices=_EXECUTION_PROFILE_CHOICES, default="codex-read-only")
    parser.add_argument("--judge-profile", choices=_AB_PROFILE_CHOICES, default="oss-local")


def _add_ab_preview_parser(subparsers: argparse._SubParsersAction, global_parser: argparse.ArgumentParser) -> None:
    preview = subparsers.add_parser("ab-preview", help="Preview a Codex-backed skill A/B contract", parents=[global_parser])
    _add_ab_common_arguments(preview)
    preview.add_argument("--preview", action="store_true", help="Emit a non-mutating A/B preview receipt")


def _add_ab_plan_parser(subparsers: argparse._SubParsersAction, global_parser: argparse.ArgumentParser) -> None:
    plan = subparsers.add_parser("ab-plan", help="Plan Codex exec commands for a skill A/B eval", parents=[global_parser])
    _add_ab_common_arguments(plan)
    plan.add_argument("--evidence-root", default=".harness/artifacts/sdk-ab-evals")
    plan.add_argument("--preview", action="store_true", help="Emit a non-mutating A/B execution plan receipt")


def _add_ab_run_parser(subparsers: argparse._SubParsersAction, global_parser: argparse.ArgumentParser) -> None:
    run = subparsers.add_parser("ab-run", help="Execute a Codex-backed skill A/B eval", parents=[global_parser])
    _add_ab_common_arguments(run)
    run.add_argument("--evidence-root", default=".harness/artifacts/sdk-ab-evals")
    run.add_argument("--timeout-seconds", type=_positive_int, default=1800, help="Timeout for each Codex variant run.")
    run.add_argument("--execute", action="store_true", help="Required explicit gate before invoking Codex exec.")


def _add_ab_judge_preview_parser(subparsers: argparse._SubParsersAction, global_parser: argparse.ArgumentParser) -> None:
    judge = subparsers.add_parser("ab-judge-preview", help="Preview sanitized A/B judge input", parents=[global_parser])
    judge.add_argument("--run-receipt", required=True, help="Repo-relative completed ab-run receipt JSON")
    judge.add_argument("--preview", action="store_true", help="Emit a non-mutating judge input receipt")


def _add_ab_judge_score_parser(subparsers: argparse._SubParsersAction, global_parser: argparse.ArgumentParser) -> None:
    score = subparsers.add_parser("ab-judge-score", help="Run Ollama scoring for a completed A/B eval", parents=[global_parser])
    score.add_argument("--run-receipt", required=True, help="Repo-relative completed ab-run receipt JSON")
    score.add_argument("--evidence-root", default=".harness/artifacts/sdk-ab-judges")
    score.add_argument("--judge-profile", choices=("oss-local", "oss-cloud"), default="oss-local")
    score.add_argument("--timeout-seconds", type=_positive_int, default=300, help="Timeout for the judge provider.")
    score.add_argument("--execute", action="store_true", help="Required explicit gate before invoking the judge provider.")


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return parsed


def dispatch_sdk_eval(repo_root: Path, args: argparse.Namespace) -> CallResult:
    dispatchers: dict[str, Callable[[Path, argparse.Namespace], CallResult]] = {
        "run": _dispatch_run,
        "scenario-quality": _dispatch_scenario_quality,
        "scorer-quality": _dispatch_scorer_quality,
        "scorer-calibration": _dispatch_scorer_calibration,
        "tessl-score": _dispatch_tessl_score,
        "tessl-local-proof": _dispatch_tessl_local_proof,
        "regression-plan": _dispatch_regression_plan,
        "handoff-readiness": _dispatch_handoff_readiness,
        "profiles": _dispatch_profiles,
        "ab-rubric": _dispatch_ab_rubric,
        "ab-preview": _dispatch_ab_preview,
        "ab-plan": _dispatch_ab_plan,
        "ab-run": _dispatch_ab_run,
        "ab-judge-preview": _dispatch_ab_judge_preview,
        "ab-judge-score": _dispatch_ab_judge_score,
    }
    dispatcher = dispatchers.get(args.eval_action)
    if dispatcher is None:
        return build_unknown_action_result("sdk eval", args.eval_action)
    return dispatcher(repo_root, args)


def _dispatch_run(repo_root: Path, args: argparse.Namespace) -> CallResult:
    return skills_commands.skills_sdk_eval_run(
        repo_root,
        dataset=args.dataset,
        target=args.skill or args.target,
        mode=args.mode,
        runner=args.runner,
        skip_tessl=not args.with_tessl,
        codex_profile=args.codex_profile,
        cases=args.cases,
        timeout_seconds=args.timeout_seconds,
    )


def _preview_required(command: str, message: str, next_command: str, args: argparse.Namespace) -> CallResult | None:
    if args.preview:
        return None
    return build_validation_error(command, message, next_command)


def _dispatch_scenario_quality(repo_root: Path, args: argparse.Namespace) -> CallResult:
    return _dispatch_preview_target(
        repo_root,
        args,
        command="sdk eval scenario-quality",
        message="Scenario quality requires --preview.",
        next_command=_scenario_quality_next(),
        handler=skills_commands.skills_sdk_eval_scenario_quality,
    )


def _dispatch_scorer_quality(repo_root: Path, args: argparse.Namespace) -> CallResult:
    return _dispatch_preview_target(
        repo_root,
        args,
        command="sdk eval scorer-quality",
        message="Scorer quality requires --preview.",
        next_command=_scorer_quality_next(),
        handler=skills_commands.skills_sdk_eval_scorer_quality,
    )


def _dispatch_scorer_calibration(repo_root: Path, args: argparse.Namespace) -> CallResult:
    return _dispatch_preview_target(
        repo_root,
        args,
        command="sdk eval scorer-calibration",
        message="Scorer calibration requires --preview.",
        next_command=_scorer_calibration_next(),
        handler=skills_commands.skills_sdk_eval_scorer_calibration,
    )


def _dispatch_tessl_score(repo_root: Path, args: argparse.Namespace) -> CallResult:
    error = _preview_required("sdk eval tessl-score", "Tessl score receipts require --preview.", _tessl_score_next(), args)
    return error or skills_commands.skills_sdk_eval_tessl_score(
        repo_root,
        view_json=args.view_json,
        skill=args.skill,
        run_id=args.run_id,
    )


def _dispatch_tessl_local_proof(repo_root: Path, args: argparse.Namespace) -> CallResult:
    return skills_commands.skills_sdk_eval_tessl_local_proof(
        repo_root,
        skill=args.skill,
        workspace=args.workspace,
        execute=args.execute,
        include_review=args.include_review,
        review_threshold=args.review_threshold,
        timeout_seconds=args.timeout_seconds,
    )


def _dispatch_regression_plan(repo_root: Path, args: argparse.Namespace) -> CallResult:
    error = _preview_required("sdk eval regression-plan", "Regression plan receipts require --preview.", _regression_plan_next(), args)
    return error or skills_commands.skills_sdk_eval_regression_plan(
        repo_root,
        view_json=args.view_json,
        skill=args.skill,
        run_id=args.run_id,
        plan_json=args.plan_json,
    )


def _dispatch_handoff_readiness(repo_root: Path, args: argparse.Namespace) -> CallResult:
    error = _preview_required("sdk eval handoff-readiness", "Handoff readiness receipts require --preview.", _handoff_readiness_next(), args)
    return error or skills_commands.skills_sdk_eval_handoff_readiness(
        repo_root,
        skill=args.skill,
        receipt_json=args.receipt_json,
    )


def _dispatch_preview_target(
    repo_root: Path,
    args: argparse.Namespace,
    *,
    command: str,
    message: str,
    next_command: str,
    handler: Callable[[Path, str], CallResult],
) -> CallResult:
    error = _preview_required(command, message, next_command, args)
    return error or handler(repo_root, target=args.target)


def _dispatch_profiles(repo_root: Path, args: argparse.Namespace) -> CallResult:
    error = _preview_required("sdk eval profiles", "Eval profiles require --preview.", "ask sdk eval profiles --preview --json --robot", args)
    return error or skills_commands.skills_sdk_eval_profiles_preview(repo_root)


def _dispatch_ab_rubric(repo_root: Path, args: argparse.Namespace) -> CallResult:
    error = _preview_required("sdk eval ab-rubric", "A/B rubric requires --preview.", "ask sdk eval ab-rubric --preview --json --robot", args)
    return error or skills_commands.skills_sdk_eval_ab_rubric_preview(repo_root)


def _dispatch_ab_preview(repo_root: Path, args: argparse.Namespace) -> CallResult:
    error = _preview_required("sdk eval ab-preview", "A/B preview requires --preview.", _ab_preview_next(), args)
    if error:
        return error
    return skills_commands.skills_sdk_eval_ab_preview(repo_root, **_ab_common_kwargs(args))


def _dispatch_ab_plan(repo_root: Path, args: argparse.Namespace) -> CallResult:
    error = _preview_required("sdk eval ab-plan", "A/B execution plan requires --preview.", _ab_plan_next(), args)
    if error:
        return error
    return skills_commands.skills_sdk_eval_ab_plan(repo_root, evidence_root=args.evidence_root, **_ab_common_kwargs(args))


def _dispatch_ab_run(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if not args.execute:
        return build_validation_error("sdk eval ab-run", "A/B eval execution invokes Codex and requires --execute.", _ab_run_next())
    return skills_commands.skills_sdk_eval_ab_run(
        repo_root,
        evidence_root=args.evidence_root,
        timeout_seconds=args.timeout_seconds,
        **_ab_common_kwargs(args),
    )


def _dispatch_ab_judge_preview(repo_root: Path, args: argparse.Namespace) -> CallResult:
    error = _preview_required("sdk eval ab-judge-preview", "A/B judge input preview requires --preview.", _ab_judge_next(), args)
    return error or skills_commands.skills_sdk_eval_ab_judge_preview(repo_root, run_receipt=args.run_receipt)


def _dispatch_ab_judge_score(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if not args.execute:
        return build_validation_error("sdk eval ab-judge-score", "A/B judge scoring invokes Ollama and requires --execute.", _ab_judge_score_next())
    return skills_commands.skills_sdk_eval_ab_judge_score(
        repo_root,
        run_receipt=args.run_receipt,
        evidence_root=args.evidence_root,
        judge_profile=args.judge_profile,
        timeout_seconds=args.timeout_seconds,
    )


def _ab_common_kwargs(args: argparse.Namespace) -> dict[str, str]:
    return {
        "skill_a": args.skill_a,
        "skill_b": args.skill_b,
        "fixture": args.fixture,
        "execution_profile": args.execution_profile,
        "judge_profile": args.judge_profile,
    }


def _scenario_quality_next() -> str:
    return "ask sdk eval scenario-quality <skill> --preview --json --robot"


def _scorer_quality_next() -> str:
    return "ask sdk eval scorer-quality <skill> --preview --json --robot"


def _scorer_calibration_next() -> str:
    return "ask sdk eval scorer-calibration <skill> --preview --json --robot"


def _tessl_score_next() -> str:
    return "ask sdk eval tessl-score --view-json <view-json> --skill <skill> --preview --json --robot"


def _tessl_local_proof_next() -> str:
    return "ask sdk eval tessl-local-proof --skill <skill> --workspace <workspace> --execute --json --robot"


def _regression_plan_next() -> str:
    return "ask sdk eval regression-plan --view-json <view-json> --skill <skill> --preview --json --robot"


def _handoff_readiness_next() -> str:
    return "ask sdk eval handoff-readiness --skill <skill> --preview --json --robot"


def _ab_preview_next() -> str:
    return "ask sdk eval ab-preview --skill-a <skill-a> --skill-b <skill-b> --fixture <fixture> --preview --json --robot"


def _ab_plan_next() -> str:
    return "ask sdk eval ab-plan --skill-a <skill-a> --skill-b <skill-b> --fixture <fixture> --preview --json --robot"


def _ab_run_next() -> str:
    return "ask sdk eval ab-run --skill-a <skill-a> --skill-b <skill-b> --fixture <fixture> --execute --json --robot"


def _ab_judge_next() -> str:
    return "ask sdk eval ab-judge-preview --run-receipt <receipt.json> --preview --json --robot"


def _ab_judge_score_next() -> str:
    return "ask sdk eval ab-judge-score --run-receipt <receipt.json> --execute --json --robot"
