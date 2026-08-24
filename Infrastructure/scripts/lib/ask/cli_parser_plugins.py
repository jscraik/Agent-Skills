"""Plugin command parser registration."""

from __future__ import annotations

import argparse


def _add_init_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("name", help="Name of the new plugin")
    parser.add_argument(
        "--category",
        default="third-party",
        help="Plugin category under Plugins/ (default: third-party)",
    )
    for flag, help_text in (
        ("--with-marketplace", "Add to local marketplace"),
        ("--with-scripts", "Add scripts directory"),
        ("--with-assets", "Add assets directory"),
        ("--with-references", "Add references directory"),
        ("--with-workflows", "Add workflows directory"),
    ):
        parser.add_argument(flag, action="store_true", help=help_text)


def _add_install_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("url", help="GitHub URL of the plugin source")
    parser.add_argument(
        "--path", required=True, help="Plugin directory path inside source repo"
    )
    parser.add_argument("--name", help="Override installed plugin name")
    parser.add_argument(
        "--ref", help="Pinned Git ref to install (recommended: commit SHA)"
    )
    parser.add_argument(
        "--dest",
        default="Plugins/third-party",
        help="Destination directory relative to repo root",
    )
    parser.add_argument(
        "--validation-level",
        choices=["strict", "compat"],
        default="compat",
        help="Installer validation depth",
    )
    _add_install_policy_arguments(parser)


def _add_install_policy_arguments(parser: argparse.ArgumentParser) -> None:
    for flag, help_text in (
        ("--allow-untrusted-source", "Allow non-allowlisted source repos"),
        ("--allow-unpinned-ref", "Allow non-SHA refs"),
        ("--sync-profile", "Refresh Codex profile plugin mirrors"),
        ("--require-desktop-loadable", "Fail unless Desktop-loadable"),
    ):
        parser.add_argument(flag, action="store_true", help=help_text)
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview installation without writing"
    )


def _add_runtime_commands(actions, global_parser: argparse.ArgumentParser) -> None:
    actions.add_parser(
        "list", help="List plugin lifecycle state", parents=[global_parser]
    )
    status = actions.add_parser(
        "status", help="Show state for one plugin", parents=[global_parser]
    )
    status.add_argument("name", help="Plugin name")
    actions.add_parser(
        "doctor", help="Run read-only plugin diagnostics", parents=[global_parser]
    )
    sync = actions.add_parser(
        "sync-local-runtime",
        help="Replace copied local-plugin runtime mirrors from canonical Plugins/",
        parents=[global_parser],
    )
    sync.add_argument(
        "--dry-run", action="store_true", help="Preview runtime sync without writing"
    )


def _add_prune_command(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "prune-stale-config",
        help="Remove stale enabled local plugin IDs",
        parents=[global_parser],
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview config pruning without writing"
    )
    parser.add_argument(
        "--stability-seconds",
        type=float,
        default=10.0,
        help="Seconds to watch for stale IDs",
    )
    parser.add_argument(
        "--stability-interval-seconds",
        type=float,
        default=0.5,
        help="Seconds between checks",
    )
    parser.add_argument(
        "--verify-stable-when-clean",
        action="store_true",
        help="Watch even when already clean",
    )


def _add_create_install_commands(
    actions, global_parser: argparse.ArgumentParser
) -> None:
    specs = (
        ("init", "Initialize a new plugin scaffold", _add_init_arguments),
        ("create", "Alias for plugins init", _add_init_arguments),
        ("install", "Install a plugin from GitHub", _add_install_arguments),
        ("import", "Alias for plugins install", _add_install_arguments),
    )
    for action, help_text, configure in specs:
        parser = actions.add_parser(action, help=help_text, parents=[global_parser])
        configure(parser)


def _add_uninstall_command(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "uninstall", help="Uninstall a plugin and sync config", parents=[global_parser]
    )
    parser.add_argument("name", help="Name of plugin to uninstall")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview uninstallation without making changes",
    )


def _add_harden_command(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "harden", help="Run plugin-builder hardening checks", parents=[global_parser]
    )
    parser.add_argument(
        "plugin_path", help="Plugin path to harden (for example: Plugins/my-plugin)"
    )
    parser.add_argument(
        "--marketplace-path",
        default="Plugins/marketplace.json",
        help="Marketplace manifest path",
    )
    parser.add_argument(
        "--skip-compat", action="store_true", help="Skip audit-compat step"
    )
    parser.add_argument(
        "--skip-marketplace-audit",
        action="store_true",
        help="Skip audit-marketplace step",
    )
    parser.add_argument(
        "--no-require-marketplace",
        action="store_true",
        help="Do not require a matching marketplace entry",
    )
    parser.add_argument(
        "--strict-marketplace-path",
        action="store_true",
        help="Disallow legacy marketplace path override",
    )


def add_plugin_commands(subparsers, global_parser: argparse.ArgumentParser) -> None:
    """Register plugin-management commands."""
    plugins_parser = subparsers.add_parser(
        "plugins", help="Plugin management", parents=[global_parser]
    )
    actions = plugins_parser.add_subparsers(dest="action")
    _add_runtime_commands(actions, global_parser)
    _add_prune_command(actions, global_parser)
    _add_create_install_commands(actions, global_parser)
    _add_uninstall_command(actions, global_parser)
    _add_harden_command(actions, global_parser)
