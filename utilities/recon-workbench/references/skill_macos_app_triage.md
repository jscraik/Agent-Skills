---
name: macos_app_triage
description: Static triage for macOS .app bundles and Mach-O binaries; bundle map, signature/entitlements, imports/symbol hints.
---

Inputs:
- TARGET_LOCATOR: path to .app or Mach-O

Use probes:
- static.macos_bundle_tree
- static.macos_codesign
- static.macos_macho_imports

Notes:
- You can map the bundle file structure and infer a derived code structure (imports, symbol names if present).
- You generally cannot reconstruct the original source "project tree" from a compiled binary without debug/source artifacts.

Output:
- Produce a concise capability map (network/storage/IPC hints) with evidence paths.
