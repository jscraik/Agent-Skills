---
name: macos-spm-packager
description: "Bootstrap a complete SwiftPM macOS app folder, then build, package, and run it without Xcode. Use for the starter layout and + for packaging and release details.. Use when Creating a SwiftPM-based macOS app without Xcode.."
---

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

# macOS SwiftPM App Packaging (No Xcode)

## Overview
Bootstrap a complete SwiftPM macOS app folder, then build, package, and run it without Xcode. Use `assets/templates/bootstrap/` for the starter layout and `references/packaging.md` + `references/release.md` for packaging and release details.

## Philosophy
- Prefer explicit, scriptable packaging over opaque tooling.
- Keep signing and notarization steps reproducible.
- Minimize moving parts; use the provided templates.

## When to use
- Creating a SwiftPM-based macOS app without Xcode.
- Packaging an app bundle via scripts.
- Adding signing/notarization/appcast steps outside Xcode.

## Inputs
- App name, bundle ID, version/build numbers.
- Whether signing/notarization is required.

## Outputs
- Packaged .app bundle and zip (if requested).
- Optional appcast and notarized artifacts.

## Two-Step Workflow
1) Bootstrap the project folder
   - Copy `assets/templates/bootstrap/` into a new repo.
   - Rename `MyApp` in `Package.swift`, `Sources/MyApp/`, and `version.env`.
   - Customize `APP_NAME`, `BUNDLE_ID`, and versions.

2) Build, package, and run the bootstrapped app
   - Copy scripts from `assets/templates/` into your repo (for example, `Scripts/`).
   - Build/tests: `swift build` and `swift test`.
   - Package: `Scripts/package_app.sh`.
   - Run: `Scripts/compile_and_run.sh` (preferred) or `Scripts/launch.sh`.
   - Release (optional): `Scripts/sign-and-notarize.sh` and `Scripts/make_appcast.sh`.
   - Tag + GitHub release (optional): create a git tag, upload the zip/appcast to the GitHub release, and publish.

## Templates
- `assets/templates/package_app.sh`: Build binaries, create the .app bundle, copy resources, sign.
- `assets/templates/compile_and_run.sh`: Dev loop to kill running app, package, launch.
- `assets/templates/build_icon.sh`: Generate .icns from an Icon Composer file (requires Xcode install).
- `assets/templates/sign-and-notarize.sh`: Notarize, staple, and zip a release build.
- `assets/templates/make_appcast.sh`: Generate Sparkle appcast entries for updates.
- `assets/templates/setup_dev_signing.sh`: Create a stable dev code-signing identity.
- `assets/templates/launch.sh`: Simple launcher for a packaged .app.
- `assets/templates/version.env`: Example version file consumed by packaging scripts.
- `assets/templates/bootstrap/`: Minimal SwiftPM macOS app skeleton (Package.swift, Sources/, version.env).

## Notes
- Keep entitlements and signing configuration explicit; edit the template scripts instead of reimplementing.
- Remove Sparkle steps if you do not use Sparkle for updates.
- Sparkle relies on the bundle build number (`CFBundleVersion`), so `BUILD_NUMBER` in `version.env` must increase for each update.
- For menu bar apps, set `MENU_BAR_APP=1` when packaging to emit `LSUIElement` in Info.plist.

## Variation rules
- Vary depth by release scope (dev build vs notarized release).
- Skip Sparkle/appcast when not needed.

## Anti-patterns to avoid
- Hardcoding signing identities into scripts.
- Shipping unsigned builds when notarization is required.
- Modifying templates without updating version.env usage.

## Example prompts
- “Scaffold a SwiftPM macOS app and package it without Xcode.”
- “Add notarization to the packaging scripts.”
- “Generate an appcast for Sparkle updates.”

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.


## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.
