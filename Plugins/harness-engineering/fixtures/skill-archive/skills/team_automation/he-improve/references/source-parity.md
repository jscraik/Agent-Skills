# Source Parity

Read when: validating how `he-improve` preserves the archived optimization workflow while remaining the canonical local stage for measurable tuning loops.

## Archived Source Baseline
- Optimization workflow with explicit spec, baseline, hypothesis loop, keep-or-revert decisions, and durable experiment logging.
- Dual metric modes for direct numeric measurement and rubric-based quality judgment.

## Mapping Summary
- `he-improve` is the canonical local stage name for this workflow.
- The execution model (spec + baseline + hypothesis loop + keep/revert) is preserved.
- Hard-metric and judge-metric dual mode is preserved.
- Disk-persistence discipline is preserved with local path updates.

## Harness Engineering Adaptations
- Wording is updated to Harness Engineering stage language.
- Scratch path uses `.context/harness-engineering/he-improve/...`.
- Stage routing uses plugin-canonical `../../../../../references/routing-map.json` + `../../../../../references/subagent-routing.md`.
- Missing-role guidance routes to `[[codex-agent-creator]]` instead of assuming roles are preinstalled.
- The active front door now makes spec validation, metric-mode selection, `fresh | resume` handling, measurement-harness trust gates, and write-then-verify durability explicit.

## Explicit Non-Goals In This Mapping
- This stage does not replace `he-plan` or `he-work`.
- This stage does not broaden into generic lifecycle orchestration.
- This stage does not create a new plugin; it installs one additional stage under `harness-engineering`.
