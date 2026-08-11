from __future__ import annotations

import argparse
from pathlib import Path

import ask.commands.skills as skills_commands
from ask.cli_errors import build_unknown_action_result
from ask.envelope import CallResult


def add_sdk_plugin_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = sdk_subparsers.add_parser(
        "plugin",
        help="Create, review, install, and save single skills or plugins through the Skills SDK lifecycle",
        parents=[global_parser],
    )
    subparsers = parser.add_subparsers(dest="plugin_action", required=True)
    _add_create_parser(subparsers, global_parser)
    _add_review_parser(subparsers, global_parser)
    _add_install_parser(subparsers, global_parser)
    _add_save_registry_parser(subparsers, global_parser)


def _add_create_parser(
    subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = subparsers.add_parser(
        "create",
        help="Create a single skill or plugin through the SDK facade",
        parents=[global_parser],
    )
    parser.add_argument("name", help="Skill or plugin name to create")
    parser.add_argument("--kind", choices=["skill", "plugin"], required=True)
    parser.add_argument("--category", required=True, help="Skill category or plugin destination category")
    parser.add_argument("--description", help="Required for --kind skill")
    parser.add_argument("--with-registry", action="store_true", help="Save the created artifact to the local registry/marketplace when applying")
    _add_companion_folder_flags(parser)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true", help="Plan creation without writing")
    mode.add_argument("--apply", action="store_true", help="Delegate to the bounded create command and record the SDK receipt")


def _add_companion_folder_flags(parser: argparse.ArgumentParser) -> None:
    for flag, help_text in (
        ("--with-scripts", "Add scripts directory for plugin creation"),
        ("--with-assets", "Add assets directory for plugin creation"),
        ("--with-references", "Add references directory for plugin creation"),
        ("--with-workflows", "Add workflows directory for plugin creation"),
    ):
        parser.add_argument(flag, action="store_true", help=help_text)


def _add_review_parser(
    subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = subparsers.add_parser(
        "review",
        help="Review a single skill or plugin through SDK guardrails",
        parents=[global_parser],
    )
    parser.add_argument("target", help="Skill handle/path or plugin root")
    parser.add_argument("--kind", choices=["skill", "plugin"], required=True)
    parser.add_argument("--strict", action="store_true", help="Use strict skill audit or require plugin marketplace checks")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true", help="Plan review without running checks")
    mode.add_argument("--execute", action="store_true", help="Run the bounded local review checks")


def _add_install_parser(
    subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = subparsers.add_parser(
        "install",
        help="Install a single skill or plugin through SDK guardrails",
        parents=[global_parser],
    )
    parser.add_argument("--kind", choices=["skill", "plugin"], required=True)
    parser.add_argument("--target", help="Skill handle/path for --kind skill")
    parser.add_argument("--project-root", help="Absolute marked project root for applying skill installs")
    parser.add_argument("--scope", choices=["project", "workspace", "global"], default="project")
    parser.add_argument("--url", help="Plugin source URL for --kind plugin")
    parser.add_argument("--path", help="Plugin path inside source repo for --kind plugin")
    parser.add_argument("--name", help="Plugin install name override")
    parser.add_argument("--ref", help="Pinned plugin source ref")
    parser.add_argument("--dest", default="Plugins/third-party", help="Plugin destination under Plugins/<category>")
    parser.add_argument("--validation-level", choices=["strict", "compat"], default="compat")
    parser.add_argument("--allow-untrusted-source", action="store_true")
    parser.add_argument("--allow-unpinned-ref", action="store_true")
    parser.add_argument("--sync-profile", action="store_true")
    parser.add_argument("--require-desktop-loadable", action="store_true")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true", help="Plan install without writing")
    mode.add_argument("--apply", action="store_true", help="Delegate to the bounded install command")


def _add_save_registry_parser(
    subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = subparsers.add_parser(
        "save-registry",
        help="Save a skill or plugin to the local SDK registry/marketplace",
        parents=[global_parser],
    )
    parser.add_argument("--kind", choices=["skill", "plugin"], required=True)
    parser.add_argument("--target", required=True, help="Skill path/handle or plugin root/name")
    parser.add_argument("--registry", help="Optional repo-relative registry path")
    parser.add_argument("--name", help="Explicit registry name")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true", help="Plan registry update without writing")
    mode.add_argument("--apply", action="store_true", help="Write the local registry/marketplace receipt")


def dispatch_sdk_plugin(repo_root: Path, args: argparse.Namespace) -> CallResult:
    dispatchers = {
        "create": _dispatch_create,
        "review": _dispatch_review,
        "install": _dispatch_install,
        "save-registry": _dispatch_save_registry,
    }
    handler = dispatchers.get(args.plugin_action)
    if handler is None:
        return build_unknown_action_result("sdk plugin", args.plugin_action)
    return handler(repo_root, args)


def _dispatch_create(repo_root: Path, args: argparse.Namespace) -> CallResult:
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
    return skills_commands.skills_sdk_plugin_create(
        repo_root,
        skills_commands.SkillsSdkPluginCreateRequest(
            kind=args.kind,
            name=args.name,
            category=args.category,
            description=args.description,
            with_registry=args.with_registry,
            companion_folders=companion,
            apply=args.apply,
        ),
    )


def _dispatch_review(repo_root: Path, args: argparse.Namespace) -> CallResult:
    return skills_commands.skills_sdk_plugin_review(
        repo_root,
        skills_commands.SkillsSdkPluginReviewRequest(
            kind=args.kind,
            target=args.target,
            strict=args.strict,
            execute=args.execute,
        ),
    )


def _dispatch_install(repo_root: Path, args: argparse.Namespace) -> CallResult:
    return skills_commands.skills_sdk_plugin_install(
        repo_root,
        kind=args.kind,
        target=args.target,
        project_root=args.project_root,
        scope=args.scope,
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
        apply=args.apply,
    )


def _dispatch_save_registry(repo_root: Path, args: argparse.Namespace) -> CallResult:
    return skills_commands.skills_sdk_plugin_save_registry(
        repo_root,
        kind=args.kind,
        target=args.target,
        registry=args.registry,
        name=args.name,
        apply=args.apply,
    )
