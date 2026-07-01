# Improve Agent Native Menu Bar Prototype

Native macOS menu-bar prototype for the improve-agent-native skill package.

It renders a Tessl-style card while keeping evidence lanes separate:

- Local skill metadata comes from Skills/agent-ops/improve-agent-native/SKILL.md.
- Local SDK quality comes from ./bin/ask skills package verify.
- Local SDK impact comes from ./bin/ask sdk eval scenario-quality --preview.
- Local SDK security comes from ./bin/ask sdk security risk-modes --preview.
- Tessl status comes from tessl plugin info jscraik/improve-agent-native, then URL probes as fallback diagnostics.

The current private Tessl plugin may require CLI authentication. When Tessl auth or URL fetch is unavailable, the popover shows that blocker instead of inventing a registry score.
For private Tessl registry metadata, launch it from a shell where the Tessl CLI can authenticate. The app first uses an exported TESSL_TOKEN, then falls back to op run when 1Password CLI is available.

Run:

  cd Prototypes/improve-agent-native-menubar
  ./Launch.command

Or double-click Launch.command in Finder.

The launcher compiles with xcrun swiftc, creates a temporary app bundle at
${TMPDIR}/improve-agent-native-menubar/Improve Agent Native.app, and opens it
with AGENT_SKILLS_ROOT pointed at this checkout. It intentionally avoids the
default SwiftPM GUI launch path because swift run can fail on this workstation
with an XCBuild property list initialization error.

Validation:

  HOME=/private/tmp/improve-agent-native-menubar-home XDG_CACHE_HOME=/private/tmp/improve-agent-native-menubar-xdg CLANG_MODULE_CACHE_PATH=/private/tmp/improve-agent-native-menubar-clang-cache swift build --build-system native --disable-sandbox --build-path /private/tmp/improve-agent-native-menubar-native-build

Launcher validation:

  NO_OPEN=1 ./Launch.command

Compile-only validation:

  CLANG_MODULE_CACHE_PATH=/private/tmp/improve-agent-native-menubar-clang-cache xcrun swiftc -parse-as-library Sources/ImproveAgentNativeMenuBar/App.swift -o /private/tmp/ImproveAgentNativeMenuBar

These checks do not prove hosted CI, Tessl private-registry access, app signing, notarization, or that the menu-bar item is visible on every desktop arrangement.
