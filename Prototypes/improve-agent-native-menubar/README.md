# Improve Agent Native Menu Bar Prototype

Native macOS menu-bar prototype for the improve-agent-native skill package.

It renders a Tessl-style card while keeping evidence lanes separate:

- Local skill metadata comes from Skills/agent-ops/improve-agent-native/SKILL.md.
- Local SDK quality comes from ./bin/ask skills package verify.
- Local SDK impact comes from ./bin/ask sdk eval scenario-quality --preview.
- Local SDK security comes from ./bin/ask sdk security risk-modes --preview.
- Tessl status and registry metrics come from one bounded tessl plugin info jscraik/improve-agent-native --json process per app launch, then URL probes as fallback diagnostics.

The current private Tessl plugin may require CLI authentication. When Tessl auth or URL fetch is unavailable, the popover shows that blocker instead of inventing a registry score.
For private Tessl registry metadata, launch it from a shell where the Tessl CLI can authenticate and where tessl is on PATH. You can also set TESSL_CLI or TESSL_BIN to the executable path before launch. If tessl is unavailable, the popover reports the CLI blocker instead of inventing registry data. The app does not start tessl login, does not call op run, and does not retry with a second non-JSON tessl command; a timeout or auth prompt is cached until the app is relaunched.

The app loads local SDK evidence once per app process. It does not poll in the background. Tessl CLI lookup is intentionally one-shot per app process.

Run:

  cd Prototypes/improve-agent-native-menubar
  ./Launch.command

That command builds and signs the app without launching it. Launch deliberately only after checking for stale prototype or Tessl-login processes:

  ./Launch.command --open

The launcher compiles with xcrun swiftc and creates an app bundle under
dist/Improve Agent Native.app. It intentionally avoids the default SwiftPM GUI
launch path because swift run can fail on this workstation with an XCBuild
property list initialization error. It also intentionally avoids launching the
raw executable directly; --open uses LaunchServices only.

Validation:

  HOME=/private/tmp/improve-agent-native-menubar-home XDG_CACHE_HOME=/private/tmp/improve-agent-native-menubar-xdg CLANG_MODULE_CACHE_PATH=/private/tmp/improve-agent-native-menubar-clang-cache swift build --build-system native --disable-sandbox --build-path /private/tmp/improve-agent-native-menubar-native-build

Launcher validation:

  ./Launch.command

Compile-only validation:

  CLANG_MODULE_CACHE_PATH=/private/tmp/improve-agent-native-menubar-clang-cache xcrun swiftc -parse-as-library Sources/ImproveAgentNativeMenuBar/App.swift -o /private/tmp/ImproveAgentNativeMenuBar

These checks do not prove hosted CI, Tessl private-registry access, app signing, notarization, or that the menu-bar item is visible on every desktop arrangement.
