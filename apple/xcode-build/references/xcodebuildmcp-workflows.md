# XcodeBuildMCP workflows (tool mapping)

Use these mappings to choose the right MCP tools before falling back to CLI.
Keep workflows short and deterministic; set session defaults once per session.

## Discovery + session setup
- Discover projects/workspaces: `mcp__XcodeBuildMCP__discover_projs`
- List schemes: `mcp__XcodeBuildMCP__list_schemes`
- Show build settings: `mcp__XcodeBuildMCP__show_build_settings`
- Set session defaults (project/workspace, scheme, simulator/device):
  `mcp__XcodeBuildMCP__session-set-defaults`

## iOS Simulator build + run
- List/boot/open simulator: `list_sims`, `boot_sim`, `open_sim`
- Build: `build_sim` (or `build_run_sim` to build + run)
- App path: `get_sim_app_path`
- Install/launch/stop: `install_app_sim`, `launch_app_sim`, `stop_app_sim`

## iOS Device build + run
- List devices: `list_devices`
- Build: `build_device`
- App path: `get_device_app_path`
- Install/launch/stop: `install_app_device`, `launch_app_device`, `stop_app_device`

## macOS build + run
- Build: `build_macos` (or `build_run_macos`)
- App path: `get_mac_app_path`
- Launch/stop: `launch_mac_app`, `stop_mac_app`

## Tests
- Simulator tests: `test_sim`
- Device tests: `test_device`
- macOS tests: `test_macos`
- Swift Package tests: `swift_package_test`

## Logs + diagnostics
- Simulator logs: `start_sim_log_cap` -> `stop_sim_log_cap`
- Device logs: `start_device_log_cap` -> `stop_device_log_cap`
- Launch + logs (sim): `launch_app_logs_sim`
- Environment health: `doctor`

## UI automation (simulator)
- Inspect UI tree: `describe_ui`
- Input actions: `tap`, `swipe`, `gesture`, `type_text`
- Keys: `key_press`, `key_sequence`
- Long press + touch: `long_press`, `touch`

## Screenshots + video
- Screenshot: `screenshot`
- Record video: `record_sim_video`

## Simulator environment overrides
- Location: `set_sim_location`, `reset_sim_location`
- Appearance: `set_sim_appearance`
- Status bar: `sim_statusbar`

## Swift Package workflows
- Build: `swift_package_build`
- Run: `swift_package_run`
- List/stop run: `swift_package_list`, `swift_package_stop`
- Clean: `swift_package_clean`

## Scaffolding
- iOS project: `scaffold_ios_project`
- macOS project: `scaffold_macos_project`

## Utilities
- Bundle ID (app): `get_app_bundle_id`
- Bundle ID (macOS): `get_mac_bundle_id`
