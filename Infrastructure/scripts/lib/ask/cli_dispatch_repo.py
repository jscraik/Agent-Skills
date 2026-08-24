"""Repository-topic command dispatch for the ask CLI."""

from ask.cli_errors import build_unknown_action_result
from ask.commands.repo import (
    DoctorCatalogOptions,
    check_hub_stability,
    doctor_catalog,
    provider_audit,
    repo_attach_detached_head,
    repo_closeout,
    repo_doctor,
    repo_status,
    repo_surface,
    repo_validate,
    repo_yaml_inspect,
)


def dispatch_repo(repo_root, args):
    """Run the selected repository command."""
    handlers = {
        "status": lambda: repo_status(
            repo_root, verbose=args.verbose, baseline_path=args.baseline_path
        ),
        "validate": lambda: repo_validate(
            repo_root,
            ephemeral=args.ephemeral,
            fail_fast=args.fail_fast,
            scope=args.scope,
            changed_files=args.changed_files or [],
        ),
        "yaml-inspect": lambda: repo_yaml_inspect(
            repo_root, args.path, query=args.query
        ),
        "check-stability": lambda: check_hub_stability(
            repo_root, changed_files=args.changed_files or []
        ),
        "doctor": lambda: repo_doctor(repo_root),
        "closeout": lambda: repo_closeout(
            repo_root, changed=args.changed, strict=args.strict
        ),
        "doctor-catalog": lambda: doctor_catalog(
            repo_root, DoctorCatalogOptions(strict=args.strict)
        ),
        "provider-audit": lambda: provider_audit(repo_root),
        "attach-detached-head": lambda: repo_attach_detached_head(
            repo_root, branch_prefix=args.branch_prefix
        ),
        "surface": lambda: repo_surface(repo_root, strict=args.strict),
    }
    handler = handlers.get(args.action)
    return handler() if handler else build_unknown_action_result("repo", args.action)
