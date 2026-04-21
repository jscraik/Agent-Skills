# Source Parity

Read when: validating how `he-refine` maps donor behavior from the upstream `ce-polish-beta` stage.

## Donor Source
- Repository: `EveryInc/compound-engineering-plugin`
- Commit: `d8436b9a3c5b5370e51ec168a251ccb45f0d826e`
- Path: `plugins/compound-engineering/skills/ce-polish-beta`

## Mapping Summary
- Donor skill name `ce-polish-beta` -> local stage name `he-refine`.
- Donor flow (branch guard -> launch config check -> framework fallback -> browser loop) preserved.
- Donor helper scripts preserved with the same invocation contract:
  - `read-launch-json.sh`
  - `detect-project-type.sh`
  - `resolve-package-manager.sh`
  - `resolve-port.sh`
- Donor reference set for framework-specific startup behavior preserved.

## Harness Engineering Adaptations
- User-facing wording is updated to Harness Engineering stage language.
- Stage naming follows local lifecycle conventions (`he-*`).
- Stage routing uses plugin-canonical `../../../../../references/routing-map.json` and `../../../../../references/subagent-routing.md`.
- Missing-role guidance routes to `[[codex-agent-creator]]` instead of assuming role availability.

## Explicit Non-Goals In This Mapping
- This stage does not replace `he-work` for broad implementation.
- This stage does not replace `he-improve` for metric-heavy optimization loops.
- This stage does not introduce plugin-level lifecycle orchestration logic (that remains in `he-compound` and `he-router`).
