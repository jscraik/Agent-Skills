# iOS Simulator web preview (Safari)

Last verified: 2026-01-04

Use this when you need a one-command loop to preview web/App SDK UI in iOS Simulator Safari.

## Core flow (CLI)
- Start Vite on a stable port: `vite --host --port <port> --strictPort`
- Boot simulator: `xcrun simctl boot <udid>`
- Wait for boot: `xcrun simctl bootstatus <udid> -b`
- Open URL in Safari: `xcrun simctl openurl <udid> http://127.0.0.1:<port>/`
- Screenshot: `xcrun simctl io <udid> screenshot ./path/to/snap.png`

## Recommended automation
- Wrap the steps in a single script (Node or Bash) so HMR stays running.
- Prefer a fixed device selection and deterministic screenshot paths to reduce diff noise.
- If needed, use `open -a Simulator --args -CurrentDeviceUDID <udid>` to focus the device.
- A ready-to-use script is included at `scripts/ios-web` in this skill.

## Device profiles (recommended)
Use a profiles file to lock device, orientation, status bar, and output paths.

Template: `assets/ios-web.profiles.json`

Usage:
- `scripts/ios-web --profile iphone_pro`
- `scripts/ios-web --profiles ./ios-web.profiles.json --profile iphone_se`

Profiles support:
- `device` or `udid`
- `orientation` (portrait/landscapeLeft/landscapeRight/portraitUpsideDown)
- `statusBar` overrides (time, wifi/cellular, battery)
- `snapDir` for deterministic screenshot paths
- `urlPath` for deep routes

## Video capture
For motion/scroll issues:
- `scripts/ios-web --profile iphone_pro --record 5`
- Optional output: `--record-path .ios-web/iphone_pro/record.mov`

## Schema-based UI reports (optional)
Use a codex exec wrapper to produce structured JSON reports and automate the loop:
- Wrapper script: `scripts/ui-codex` (copy into your repo as `bin/ui-codex`)
- Schema template: `assets/codex/ui_report.schema.json` (copy to `codex/ui_report.schema.json`)

## Troubleshooting
- `bootstatus` fails: older Xcode versions may not support it. Ignore the error or update Xcode.
- Vite port conflicts: use `--strictPort` and pick a free port with `--port`.
- Simulator can't reach `localhost`: use your Mac LAN IP (e.g. `http://192.168.x.x:5173`) and keep `--host` enabled.
- Status bar overrides not applying: device must be booted; try `xcrun simctl status_bar <udid> clear` then re-apply.
- Orientation not changing: Simulator rotation via AppleScript requires Accessibility permissions; rotate manually if needed.

## References
- Xcode tooling docs: https://developer.apple.com/documentation/xcode
