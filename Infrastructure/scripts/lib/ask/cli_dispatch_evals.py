"""Evaluation-topic command dispatch for the ask CLI."""

from ask.cli_errors import build_unknown_action_result
from ask.commands.evals import (
    benchmark_portfolio,
    dashboard_report,
    eval_closeout_doctor,
    macro_eval_report,
    prepare_tessl_scenario_generation,
    run_evals,
)


def dispatch_evals(repo_root, args):
    """Run the selected evaluation command."""
    handlers = {
        "benchmark": lambda: benchmark_portfolio(repo_root),
        "dashboard": lambda: dashboard_report(repo_root),
        "macro-report": lambda: _macro_report(repo_root, args),
        "prepare-tessl-scenarios": lambda: prepare_tessl_scenario_generation(
            repo_root,
            path=args.path,
            workspace=args.tessl_workspace,
            dry_run=not args.execute,
        ),
    }
    if args.action == "run":
        return _run_evals(repo_root, args)
    if args.action == "closeout" and args.closeout_action == "doctor":
        return eval_closeout_doctor(repo_root, args.path)
    handler = handlers.get(args.action)
    return handler() if handler else build_unknown_action_result("evals", args.action)


def _run_evals(repo_root, args):
    """Run an evaluation with the selected provider and receipt options."""
    return run_evals(
        repo_root,
        args.path,
        mode=args.mode,
        dashboard=not args.no_dashboard,
        runner=args.runner,
        skip_tessl=True if args.skip_tessl else None,
        allow_tessl_project_save=args.allow_tessl_project_save,
        tessl_live_private=args.tessl_live_private,
        tessl_workspace=args.tessl_workspace,
        tessl_live_dry_run=args.tessl_live_dry_run,
        handoff_readiness_path=args.handoff_readiness,
        model=args.model,
        codex_profile=args.profile,
        cases=args.case,
        timeout_seconds=args.timeout_seconds,
    )


def _macro_report(repo_root, args):
    """Build a macro report with its optional summaries glob."""
    kwargs = {"output_dir": args.output_dir}
    if args.summaries_glob:
        kwargs["summaries_glob"] = args.summaries_glob
    return macro_eval_report(repo_root, **kwargs)
