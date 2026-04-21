# Source Parity

Read when: validating how `he-improve` maps donor behavior from Compound Engineering `ce-optimize`.

## Donor Source
- Repository: `EveryInc/compound-engineering-plugin`
- Commit: `d8436b9a3c5b5370e51ec168a251ccb45f0d826e`
- Path: `plugins/compound-engineering/skills/ce-optimize`

## Mapping Summary
- Donor skill name `ce-optimize` -> local stage name `he-improve`.
- Donor execution model (spec + baseline + hypothesis loop + keep/revert) preserved.
- Donor hard-metric and judge-metric dual mode preserved.
- Donor disk-persistence discipline preserved with local path updates.

## Harness Engineering Adaptations
- Wording is updated to Harness Engineering stage language.
- Scratch path moved from `.context/compound-engineering/ce-optimize/...` to `.context/harness-engineering/he-improve/...`.
- Stage routing uses plugin-canonical `../../../../../references/routing-map.json` + `../../../../../references/subagent-routing.md`.
- Missing-role guidance routes to `[[codex-agent-creator]]` instead of assuming roles are preinstalled.

## Explicit Non-Goals In This Mapping
- This stage does not replace `he-plan` or `he-work`.
- This stage does not broaden into generic lifecycle orchestration.
- This stage does not create a new plugin; it installs one additional stage under `harness-engineering`.
