---
name: xcode-build
description: Build and manage iOS/macOS apps via XcodeBuildMCP and Xcode CLI tools. Not for interactive simulator debugging; use ios-sim-debug.
allowed-tools: Bash, Read, Grep, Glob, XcodeBuildMCP
metadata:
  short-description: Xcode build and simulator ops
---

# Xcode Build (MCP + CLI)

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md


Prefer XcodeBuildMCP tools when available. Fall back to native Xcode CLI tools
when MCP is unavailable or missing a feature. This skill consolidates build,
simulator, logging, and test workflows in one place.

## Philosophy
- Prefer deterministic builds over convenience.
- Use least-privilege toolchains and explicit destinations.
- Capture evidence (logs, xcresult) for every failure.

## Guiding questions
- What is the minimum build/test needed for this task?
- Why is this toolchain or simulator selection correct?
- What evidence do we need for verification?
- How will we avoid flakiness and environment drift?

## When to use
- Build iOS/macOS apps from the command line
- Run apps in iOS Simulator (boot, install, launch, terminate)
- Capture screenshots/video from simulators
- Stream or filter logs during debugging
- Run unit or UI tests (including targeted tests)
- Automate workflows in CI/CD
- Simulate location, push, and permissions

## When not to use
- Editing project settings or code (use Xcode)
- Swift Package dependency management (use `swift package`)
- Signing/provisioning workflows (use Xcode or fastlane)

## Inputs
- Project/workspace path and scheme.
- Target platform (iOS/macOS) and simulator/device.

## Outputs
- Build/test results and logs.
- Screenshots, videos, or xcresult bundles (if requested).

## Preference
Prefer XcodeBuildMCP for builds, simulator control, logs, screenshots, and tests.
Use direct CLI tools (`xcodebuild`, `xcrun simctl`) if MCP is unavailable or
does not support the needed operation.

## XcodeBuildMCP quick start (preferred)
Use MCP tools to standardize builds and simulator workflows:
- Discover workspaces/projects: `mcp__XcodeBuildMCP__discover_projs`
- List schemes: `mcp__XcodeBuildMCP__list_schemes`
- Set defaults once per session: `mcp__XcodeBuildMCP__session-set-defaults`
  (workspacePath/projectPath, scheme, simulatorName/useLatestOS)
- Build/run/test: `mcp__XcodeBuildMCP__build_sim`, `build_run_sim`, `test_sim`
- Simulator control: `open_sim`, `boot_sim`, `install_app_sim`, `launch_app_sim`
- Screenshots/logs: `screenshot`, `start_sim_log_cap`, `stop_sim_log_cap`

## Reference
See `references/xcodebuildmcp-workflows.md` for a concise mapping of common
workflows to XcodeBuildMCP tool calls.

## Example flows (MCP)
### Build + run on iOS Simulator
1) `discover_projs` -> `list_schemes` (if needed)
2) `session-set-defaults` (workspace/project, scheme, simulatorName/useLatestOS)
3) `open_sim` -> `boot_sim`
4) `build_run_sim` (or `build_sim` + `get_sim_app_path` + `install_app_sim` + `launch_app_sim`)

### Capture simulator logs for a run
1) `start_sim_log_cap`
2) `launch_app_sim` or `launch_app_logs_sim`
3) `stop_sim_log_cap`

### Run tests on simulator
1) `session-set-defaults`
2) `test_sim` (use `extraArgs` for result bundles if needed)

### Build + run on device
1) `list_devices`
2) `build_device` -> `get_device_app_path`
3) `install_app_device` -> `launch_app_device`

### macOS build + run
1) `build_macos` (or `build_run_macos`)
2) `get_mac_app_path` -> `launch_mac_app`

### UI automation smoke on simulator
1) `describe_ui`
2) `tap` / `type_text` / `swipe`
3) `screenshot` (optional)

## Optional accelerators (use if present)
If the project already uses these, prefer them for speed and consistency:

### Fastlane (release + CI automation)
- Use for signing, test runs, screenshots, and distribution.
- If a `Fastfile` exists, call the lane instead of re-creating the sequence.
Example:
```bash
bundle exec fastlane ios tests
bundle exec fastlane ios beta
```

### Tuist (project generation + consistency)
- If a `Tuist` config exists, generate before building:
```bash
tuist generate
```
- Then build with `xcodebuild` against the generated workspace.

### Custom scripts
- If the repo has `scripts/` or `Makefile` targets for build/test, use those first.

## Constraints / Safety
- Prefer least-privilege operations and explicit destinations.
- Do not change signing/provisioning unless explicitly requested.
- Preserve evidence (logs/xcresult) for failures.

## Environment setup (gold standard)
```bash
# Show active Xcode toolchain
xcode-select --print-path

# Switch active Xcode toolchain
sudo xcode-select -switch /Applications/Xcode.app

# Prefer DEVELOPER_DIR for per-command toolchain selection
export DEVELOPER_DIR="/Applications/Xcode.app/Contents/Developer"

# Install command line tools (if missing)
xcode-select --install
```

### Apple silicon + Xcode Beta 26 (Mac Studio)
When multiple Xcode installs exist (stable + Beta), prefer `DEVELOPER_DIR`
to pin the toolchain for a single command or session:
```bash
export DEVELOPER_DIR="/Applications/Xcode-beta.app/Contents/Developer"
```
If you need a one-off command:
```bash
DEVELOPER_DIR="/Applications/Xcode-beta.app/Contents/Developer" xcodebuild -version
```

## Best‑practice defaults (local dev + CI)
Prefer deterministic settings, pinned toolchain, and explicit destinations.
Optimize for speed on a Mac Studio with Xcode Beta 26:
```bash
# Use Beta toolchain for this shell
export DEVELOPER_DIR="/Applications/Xcode-beta.app/Contents/Developer"

# Pick a simulator once per session
export UDID=$(xcrun simctl list devices --json | jq -r '.devices | .[].[] | select(.name=="iPhone 16 Pro" and .isAvailable==true) | .udid' | head -1)

# Fast build + run
xcrun simctl boot "$UDID" 2>/dev/null || true
xcodebuild -workspace App.xcworkspace -scheme App \
  -destination "platform=iOS Simulator,id=$UDID" \
  -derivedDataPath /tmp/build \
  build
APP_PATH=$(find /tmp/build -name "*.app" -type d | head -1)
xcrun simctl install "$UDID" "$APP_PATH"
xcrun simctl launch --console "$UDID" com.bundle.id
```

## Common tasks
```bash
# List schemes
xcodebuild -workspace App.xcworkspace -list

# Show destinations
xcodebuild -workspace App.xcworkspace -scheme App -showDestinations

# Run tests
xcodebuild -workspace App.xcworkspace -scheme App \
  -destination "platform=iOS Simulator,id=$UDID" test

# Screenshot
xcrun simctl io "$UDID" screenshot /tmp/screenshot.png

# Stream logs
/usr/bin/log stream --predicate 'processImagePath CONTAINS[cd] "AppName"'
```

## Test performance (CI-friendly)
```bash
# Build once, test many times
xcodebuild -workspace App.xcworkspace -scheme App \
  -destination "platform=iOS Simulator,id=$UDID" \
  build-for-testing

xcodebuild -workspace App.xcworkspace -scheme App \
  -destination "platform=iOS Simulator,id=$UDID" \
  test-without-building
```

```bash
# Test from a generated .xctestrun file (distributed CI)
xcodebuild test-without-building \
  -xctestrun /path/to/YourApp_iphonesimulator.xctestrun \
  -destination "platform=iOS Simulator,id=$UDID"
```

## Result bundles + xcresulttool (gold standard)
Capture `.xcresult` and parse failures, attachments, and logs.
```bash
# Run tests and save result bundle
xcodebuild -workspace App.xcworkspace -scheme App \
  -destination "platform=iOS Simulator,id=$UDID" \
  -resultBundlePath /tmp/TestResults.xcresult \
  test

# List issues (failures)
xcrun xcresulttool get --path /tmp/TestResults.xcresult --format json \
  | jq '.issues'

# List tests
xcrun xcresulttool get --path /tmp/TestResults.xcresult --format json \
  | jq '.tests'

# Extract attachments (screenshots, logs)
xcrun xcresulttool get --path /tmp/TestResults.xcresult --format json \
  | jq -r '.. | .attachments? // empty | .[] | .payloadRef?.id? // empty' \
  | while read -r ATTACH_ID; do
      xcrun xcresulttool get --path /tmp/TestResults.xcresult --id "$ATTACH_ID" \
        --output-path /tmp/xcresult_attachments
    done
```

## Hermetic CI recipe (deterministic builds)
```bash
# Pin toolchain
export DEVELOPER_DIR="/Applications/Xcode.app/Contents/Developer"

# Pin derived data + logs
export DERIVED_DATA_PATH="/tmp/build_derived_data"
export RESULT_BUNDLE_PATH="/tmp/TestResults.xcresult"
rm -rf "$DERIVED_DATA_PATH" "$RESULT_BUNDLE_PATH"

# Stable locale/timezone for reproducibility
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"
export TZ="UTC"

# Build + test with fixed paths
xcodebuild -workspace App.xcworkspace -scheme App \
  -destination "platform=iOS Simulator,id=$UDID" \
  -derivedDataPath "$DERIVED_DATA_PATH" \
  -resultBundlePath "$RESULT_BUNDLE_PATH" \
  clean test
```

## GitHub Actions (baseline)
Prefer a simple macOS runner job with explicit Xcode selection + caching:
```bash
# Example steps (pseudo)
actions/checkout
actions/cache (DerivedData or SPM cache)
sudo xcode-select -switch /Applications/Xcode-beta.app
xcodebuild -version
xcodebuild -workspace App.xcworkspace -scheme App \
  -destination "platform=iOS Simulator,id=$UDID" \
  -derivedDataPath "$DERIVED_DATA_PATH" \
  -resultBundlePath "$RESULT_BUNDLE_PATH" \
  clean test
```
Keep the workflow minimal and deterministic for fast feedback.

## Variation rules
- Vary depth by task (local smoke vs CI regression).
- Use different evidence types for flaky vs deterministic failures.
- Prefer different simulators when device-specific issues are suspected.

## Empowerment principles
- Empower users with explicit toolchain and destination choices.
- Empower reviewers with direct evidence (logs, xcresult paths).

## Anti-patterns to avoid
- Relying on implicit defaults for scheme or destination.
- Skipping result bundles when tests fail.
- Overriding user toolchain choices without approval.

## Log + test result triage recipes
Use these to quickly diagnose failures:
```bash
# Build log scan for common issues
xcodebuild ... 2>&1 | tee /tmp/build.log
rg -n "error:|fatal error:|No such module|Code signing|Provisioning|Unable to find destination" /tmp/build.log

# Inspect xcresult issues
xcrun xcresulttool get --path /tmp/TestResults.xcresult --format json | jq '.issues'
```

Common fixes:
- "No such module": ensure SPM resolved, check DerivedData or `xcodebuild -resolvePackageDependencies`.
- "Code signing": check team ID, profiles, and keychain access (see guardrails below).
- "Unable to find destination": refresh runtimes with `simctl list runtimes` and pin OS/device.

## Swift Package + DerivedData cache policy
```bash
# Resolve packages explicitly
xcodebuild -workspace App.xcworkspace -scheme App -resolvePackageDependencies

# Recommended cache paths
SPM_CACHE="$HOME/Library/Caches/org.swift.swiftpm"
DERIVED_DATA_PATH="/tmp/derived_data_$JOB_ID"
```
Cache invalidation:
- Clear DerivedData if Xcode version changes.
- Clear SPM cache if `Package.resolved` changes unexpectedly.

## Code signing guardrails (early detection)
```bash
# Show signing settings
xcodebuild -workspace App.xcworkspace -scheme App -showBuildSettings | rg -n "CODE_SIGN|DEVELOPMENT_TEAM|PROVISIONING_PROFILE"

# List identities in keychain
security find-identity -p codesigning -v
```
If CI fails on signing, prefer `CODE_SIGNING_ALLOWED=NO` for simulator builds.

## macOS build targets
```bash
# Build macOS target
xcodebuild -workspace App.xcworkspace -scheme AppMac \
  -destination "platform=macOS" build

# Find built .app
find /tmp/build -name "*.app" -path "*macosx*" -type d | head -1
```

## Simulator health checks
```bash
# Verify runtime availability
xcrun simctl list runtimes | rg -n "iOS"

# Verify device availability
xcrun simctl list devices available | rg -n "iPhone"

# Reset simulator if unstable
xcrun simctl shutdown all
xcrun simctl erase all
```

## Artifact packaging (CI-ready)
```bash
# Zip app bundle
APP_PATH=$(find /tmp/build -name "*.app" -type d | head -1)
zip -r "/tmp/App_${JOB_ID}.zip" "$APP_PATH"

# Archive xcresult
zip -r "/tmp/TestResults_${JOB_ID}.zip" "/tmp/TestResults.xcresult"
```

## Clean room derived data strategy (CI-safe)
```bash
# One build root per job
JOB_ID="${CI_JOB_ID:-local}"
DERIVED_DATA_PATH="/tmp/derived_data_$JOB_ID"
RESULT_BUNDLE_PATH="/tmp/xcresult_$JOB_ID/TestResults.xcresult"
rm -rf "$DERIVED_DATA_PATH" "$RESULT_BUNDLE_PATH"
mkdir -p "$(dirname "$RESULT_BUNDLE_PATH")"
```

## Simulator runtime pinning (stable matrix)
Use explicit device + OS runtime to avoid drift:
```bash
# List runtimes and device types
xcrun simctl list runtimes
xcrun simctl list devicetypes

# Create pinned runtime simulator
SIM_NAME="iPhone 16 Pro (iOS 18.0)"
DEVICE_TYPE="com.apple.CoreSimulator.SimDeviceType.iPhone-16-Pro"
RUNTIME="com.apple.CoreSimulator.SimRuntime.iOS-18-0"
UDID=$(xcrun simctl create "$SIM_NAME" "$DEVICE_TYPE" "$RUNTIME")
```

## Dual Xcode workflow (stable + beta in parallel)
Use `DEVELOPER_DIR` to select per-command toolchain without global switching:
```bash
# Stable Xcode
DEVELOPER_DIR="/Applications/Xcode.app/Contents/Developer" \
  xcodebuild -version

# Beta Xcode
DEVELOPER_DIR="/Applications/Xcode-beta.app/Contents/Developer" \
  xcodebuild -version
```

## Simulator runtime pinning with Beta runtimes
```bash
# Beta runtime example (use exact runtime identifier from `simctl list runtimes`)
DEVELOPER_DIR="/Applications/Xcode-beta.app/Contents/Developer" \
  xcrun simctl list runtimes

DEVELOPER_DIR="/Applications/Xcode-beta.app/Contents/Developer" \
  xcrun simctl create "iPhone 16 Pro (iOS 26 Beta)" \
  "com.apple.CoreSimulator.SimDeviceType.iPhone-16-Pro" \
  "com.apple.CoreSimulator.SimRuntime.iOS-26-0"
```

## Environment preflight (reproducible builds)
Capture machine + toolchain info before builds:
```bash
sw_vers
uname -m
xcodebuild -version
xcrun simctl list runtimes
xcrun simctl list devices available
```

## SwiftUI performance diagnostics (advanced)
Use Instruments for performance issues; add compiler flags only when needed.
```bash
# Enable Swift performance diagnostics (compile-time hints)
xcodebuild -workspace App.xcworkspace -scheme App \
  OTHER_SWIFT_FLAGS="\\$(inherited) -Xfrontend -debug-time-function-bodies" \
  -destination "platform=iOS Simulator,id=$UDID" build
```
Then profile with Instruments (Time Profiler, SwiftUI, Core Animation).

## Parallelization and job control (Mac Studio)
```bash
xcodebuild -workspace App.xcworkspace -scheme App \
  -destination "platform=iOS Simulator,id=$UDID" \
  -parallelizeTargets -jobs 8 build
```
Tune `-jobs` to available CPU cores; avoid oversubscription.

## xcbeautify (optional log clarity)
If `xcbeautify` is available, pipe logs for readability:
```bash
xcodebuild ... | xcbeautify
```

## Failure signature map (quick fixes)
- "No such module": run `xcodebuild -resolvePackageDependencies`, clear DerivedData.
- "Undefined symbols": check target membership + link flags.
- "Provisioning profile": verify team ID + keychain identities.
- "Unable to boot device": erase + recreate simulator runtime.
## UI automation
Use XCUITest (native, stable, works with the accessibility tree). See:
- `XCUITEST_GUIDE.md`

## Example prompts
- “Build and run this iOS app on the latest simulator.”
- “Capture simulator logs for this failing test.”
- “Run the UI tests for scheme X on iOS Simulator.”

## References (load only when needed)
Core:
- `CLI_REFERENCE.md`
- `XCUITEST_GUIDE.md`

Deep command references:
- `references/xcodebuild.md`
- `references/simctl.md`
- `references/logging.md`
- `references/workflows.md`

Authoritative CLI guidance:
- Apple TN2339 (Command Line FAQ): https://developer.apple.com/library/archive/technotes/tn2339/_index.html

## Output format (agent default)
When using this skill, always provide:
1) Exact commands to run
2) A repeatable script version (bash)
3) Diagnostic checks + remediation steps if a command fails

## Troubleshooting (quick fixes)
- "No scheme found": run `xcodebuild -list` and verify `-workspace` vs `-project`.
- "Unable to find destination": use `-showDestinations` and pick exact destination.
- App not found: use `-derivedDataPath` and search it for `.app`.
- Simulator stuck: `xcrun simctl shutdown all` then `boot $UDID`.

## Legacy MCP mapping (only for comparisons)
CLI tools replace XcodeBuildMCP:
- build → `xcodebuild ... build`
- list sims → `xcrun simctl list devices`
- screenshot → `xcrun simctl io $UDID screenshot`
- tap/type → XCUITest

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

