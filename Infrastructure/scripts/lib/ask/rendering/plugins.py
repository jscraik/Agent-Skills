"""Human output renderers for plugin CLI commands."""

from __future__ import annotations

from typing import Any

from ask.cli_output import print_first_validation_command


def _render_init(data: dict[str, Any]) -> None:
    print(f"✅ {data['message']}")
    print(data.get("raw_output", ""))
    folders = data.get("created_manual_folders", [])
    if folders:
        print("Created companion folders:")
        for folder in folders:
            print(f"  - {folder}")


def _render_state(data: dict[str, Any]) -> None:
    installed = data.get("installed_state", {})
    activation = data.get("activation_state", {})
    health = data.get("health_state", {})
    print(f"Plugins installed: {installed.get('plugin_count', 0)}")
    for plugin in installed.get("plugins", []):
        print(f"  - {plugin.get('name')} ({plugin.get('path')})")
    print(f"Activation entries: {activation.get('plugin_count', 0)}")
    print(f"Health status: {health.get('status', 'unknown')}")
    blockers = health.get("blockers", [])
    if blockers:
        print("Blockers:")
        for blocker in blockers:
            print(f"  - {blocker}")
    print_first_validation_command(data)


def _render_sync(data: dict[str, Any]) -> None:
    print("🔍 Dry run - would replace local-plugin runtime mirrors:" if data.get("dry_run") else f"✅ {data.get('message', 'Replaced local-plugin runtime mirrors.')}")
    print(f"Profiles: {len(data.get('profile_homes', []))}")
    print(f"Plugins: {', '.join(data.get('plugin_names', []))}")
    for report in data.get("runtime_reports", []):
        print(f"  - {report.get('runtime_root')}")
        removed = report.get("removed_entries") or []
        if removed:
            print(f"    removed: {', '.join(removed)}")
    print_first_validation_command(data)


def _render_prune(data: dict[str, Any]) -> None:
    stale = data.get("stale_enabled_plugin_ids", []) or data.get("desktop_readiness_state", {}).get("stale_enabled_plugin_ids", [])
    if data.get("dry_run"):
        print("🔍 Dry run - would prune stale plugin config:" if stale else "🔍 Dry run - no stale plugin config to prune")
    else:
        print("✅ Pruned stale plugin config" if stale else "✅ No stale plugin config to prune")
    for plugin_id in stale:
        print(f"  - {plugin_id}")
    print_first_validation_command(data)


def _render_install(args: Any, result: Any) -> None:
    data = result.data
    if data.get("dry_run"):
        print("🔍 Dry run - would install plugin:")
        print(f"   URL: {data.get('url')}")
        print(f"   Source path: {data.get('plugin_path')}")
        print(f"   Name: {data.get('plugin_name')}")
        print(f"   Target: {data.get('target_path')}")
        print_first_validation_command(data)
        print("\n💡 To actually install, run:")
        print(f"   {result.metadata.get('next_steps', ['ask plugins install <url> --path <path>'])[0]}")
        return
    print(f"✅ {data.get('message', 'Plugin installed.')}")
    if data.get("raw_output"):
        print(data["raw_output"])
    print_first_validation_command(data)


def _render_uninstall(args: Any, result: Any) -> None:
    data = result.data
    if data.get("dry_run"):
        print("🔍 Dry run - would uninstall plugin:")
        print(f"   Name: {data.get('plugin_name', args.name)}")
        print(f"   Target: {data.get('target_path')}")
        print_first_validation_command(data)
        print("\n💡 To actually uninstall, run:")
        print(f"   {result.metadata.get('next_steps', ['ask plugins uninstall <name>'])[0]}")
        return
    print(f"✅ {data.get('message', 'Plugin uninstalled.')}")
    print_first_validation_command(data)


def _render_harden(data: dict[str, Any]) -> None:
    print(f"✅ {data.get('message', 'Plugin hardening checks passed.')}")
    runs = data.get("command_runs", [])
    if runs:
        print("Checks run:")
        for run in runs:
            print(f"  - {run.get('step')}: {run.get('command')}")
    print_first_validation_command(data)


def render_plugins_human(args: Any, result: Any) -> bool:
    action = args.action
    if action in {"init", "create"}:
        _render_init(result.data)
    elif action in {"list", "status", "doctor"}:
        _render_state(result.data)
    elif action == "sync-local-runtime":
        _render_sync(result.data)
    elif action == "prune-stale-config":
        _render_prune(result.data)
    elif action in {"install", "import"}:
        _render_install(args, result)
    elif action == "uninstall":
        _render_uninstall(args, result)
    elif action == "harden":
        _render_harden(result.data)
    else:
        return False
    return True
