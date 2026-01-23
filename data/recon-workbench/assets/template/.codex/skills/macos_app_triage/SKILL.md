---
name: macos_app_triage
description: Static triage for macOS .app bundles and Mach-O binaries; bundle map,
  signature/entitlements, imports/symbol hints.
metadata:
  source_repo: https://github.com/jscraik/Agent-Skills
  source_rev: 7e31061c353c94746910d239ae122900cc5324fb-dirty
  source_dirty: 'true'
  source_dirty_paths: utilities/recon-workbench/references/evals.yaml, utilities/skill-creator/scripts/run_skill_evals.py,
    design/better-icons/
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
