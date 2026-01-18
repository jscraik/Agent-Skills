# Extended Guidance

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

## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.

## Examples
- See `references/extra.md` for extended examples and notes.

## Procedure
1) Confirm objective.
2) Gather required inputs.
3) Execute steps.
4) Validate output.

## Antipatterns
- Do not add features outside the agreed scope.
