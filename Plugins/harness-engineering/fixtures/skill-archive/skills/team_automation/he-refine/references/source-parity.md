# Source Parity

Read when: validating how `he-refine` preserves the archived browser-first refinement workflow while remaining the canonical local stage for conversational polish loops.

## Archived Source Baseline
- Browser-first refinement workflow with explicit branch guard, launch-config preference, framework fallback, and iterate-in-browser loop.
- Scripted startup helpers and framework-specific reference material preserved under this skill package.

## Mapping Summary
- `he-refine` is the canonical local stage name for this workflow.
- The flow (branch guard -> launch config check -> framework fallback -> browser loop) is preserved.
- Helper scripts are preserved with the same invocation contract:
  - `read-launch-json.sh`
  - `detect-project-type.sh`
  - `resolve-package-manager.sh`
  - `resolve-port.sh`
- The framework-specific startup reference set is preserved.

## Harness Engineering Adaptations
- User-facing wording is updated to Harness Engineering stage language.
- Stage naming follows local lifecycle conventions (`he-*`).
- Stage routing uses plugin-canonical `../../../../../references/routing-map.json` and `../../../../../references/subagent-routing.md`.
- Missing-role guidance routes to `[[codex-agent-creator]]` instead of assuming role availability.
- The active front door now makes branch/PR targeting, launch-config-first startup, server probing, browser-loop iteration, and focused next-stage routing explicit.

## Explicit Non-Goals In This Mapping
- This stage does not replace `he-work` for broad implementation.
- This stage does not replace `he-improve` for metric-heavy optimization loops.
- This stage does not introduce plugin-level lifecycle orchestration logic (that remains in `he-compound` and `he-router`).
