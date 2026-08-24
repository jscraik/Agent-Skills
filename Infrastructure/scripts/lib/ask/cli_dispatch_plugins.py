"""Plugin-topic command dispatch for the ask CLI."""

from ask.cli_errors import build_unknown_action_result
from ask.commands.plugins import (
    doctor_plugins_state,
    harden_plugin,
    init_plugin,
    install_plugin,
    list_plugins_state,
    prune_stale_plugin_config,
    status_plugin_state,
    sync_local_runtime_plugins,
    uninstall_plugin,
)


def dispatch_plugins(repo_root, args):
    """Run the selected plugin command."""
    handlers = {
        "list": lambda: list_plugins_state(repo_root),
        "status": lambda: status_plugin_state(repo_root, name=args.name),
        "doctor": lambda: doctor_plugins_state(repo_root),
        "sync-local-runtime": lambda: sync_local_runtime_plugins(
            repo_root, dry_run=args.dry_run
        ),
        "prune-stale-config": lambda: prune_stale_plugin_config(
            repo_root,
            dry_run=args.dry_run,
            stability_seconds=args.stability_seconds,
            stability_interval_seconds=args.stability_interval_seconds,
            verify_stable_when_clean=args.verify_stable_when_clean,
        ),
        "harden": lambda: harden_plugin(
            repo_root,
            plugin_path=args.plugin_path,
            require_marketplace=not args.no_require_marketplace,
            marketplace_path=args.marketplace_path,
            run_compat=not args.skip_compat,
            run_marketplace_audit=not args.skip_marketplace_audit,
            allow_legacy_marketplace_path=not args.strict_marketplace_path,
        ),
        "uninstall": lambda: uninstall_plugin(
            repo_root, name=args.name, dry_run=args.dry_run
        ),
    }
    if args.action in {"init", "create"}:
        return _init_plugin(repo_root, args)
    if args.action in {"install", "import"}:
        return _install_plugin(repo_root, args)
    handler = handlers.get(args.action)
    return handler() if handler else build_unknown_action_result("plugins", args.action)


def _init_plugin(repo_root, args):
    """Create a plugin with the requested companion directories."""
    companion = [
        name
        for enabled, name in (
            (args.with_scripts, "scripts"),
            (args.with_assets, "assets"),
            (args.with_references, "references"),
            (args.with_workflows, "workflows"),
        )
        if enabled
    ]
    return init_plugin(
        repo_root,
        name=args.name,
        category=args.category,
        with_marketplace=args.with_marketplace,
        companion_folders=companion,
        action=args.action,
    )


def _install_plugin(repo_root, args):
    """Install or import a plugin from its requested source."""
    return install_plugin(
        repo_root,
        url=args.url,
        plugin_path=args.path,
        name=args.name,
        ref=args.ref,
        dest=args.dest,
        validation_level=args.validation_level,
        allow_untrusted_source=args.allow_untrusted_source,
        allow_unpinned_ref=args.allow_unpinned_ref,
        sync_profile=args.sync_profile,
        require_desktop_loadable=args.require_desktop_loadable,
        dry_run=args.dry_run,
        action=args.action,
    )
