# Improve Agent Native Menu Bar Prototype

Native macOS menu-bar prototype for the improve-agent-native skill package.

It renders a Tessl-style card while keeping evidence lanes separate:

- Local skill metadata comes from Skills/agent-ops/improve-agent-native/SKILL.md.
- Local SDK quality comes from ./bin/ask skills package verify.
- Local SDK impact comes from ./bin/ask sdk eval scenario-quality --preview.
- Local SDK security comes from ./bin/ask sdk security risk-modes --preview.
- Tessl status is shown as offline during prototype launches so the menu-bar app does not call Tessl, 1Password, or Tessl registry URLs while rendering.

The current private Tessl plugin may require CLI authentication. This prototype keeps that lane disabled and shows local SDK evidence only instead of inventing a registry score.

Run:

  cd Prototypes/improve-agent-native-menubar
  ./Launch.command

Or double-click Launch.command in Finder.

The launcher compiles with SwiftPM, creates an app bundle at
/Users/jamiecraik/.codex/usage-data/improve-agent-native-menubar/ImproveAgentNativeMenuBar.app,
and opens it with AGENT_SKILLS_ROOT pointed at this checkout. It intentionally
avoids the default SwiftPM GUI launch path because swift run can fail on this
workstation with an XCBuild property list initialization error.

Validation:

  HOME=/private/tmp/improve-agent-native-menubar-home XDG_CACHE_HOME=/private/tmp/improve-agent-native-menubar-xdg CLANG_MODULE_CACHE_PATH=/private/tmp/improve-agent-native-menubar-clang-cache swift build --build-system native --disable-sandbox --build-path /private/tmp/improve-agent-native-menubar-native-build

Launcher validation:

  NO_OPEN=1 ./Launch.command

Compile-only validation:

  CLANG_MODULE_CACHE_PATH=/private/tmp/improve-agent-native-menubar-clang-cache xcrun swiftc -parse-as-library Sources/ImproveAgentNativeMenuBar/App.swift -o /private/tmp/ImproveAgentNativeMenuBar

These checks do not prove hosted CI, Tessl private-registry access, app signing, notarization, or that the menu-bar item is visible on every desktop arrangement.
