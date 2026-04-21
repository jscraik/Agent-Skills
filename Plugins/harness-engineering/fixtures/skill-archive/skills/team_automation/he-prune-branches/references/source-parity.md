# Source Parity

Read when: validating how `he-prune-branches` maps donor behavior while keeping Harness Engineering naming and routing conventions.

## Donor Source
- Repository: `EveryInc/compound-engineering-plugin`
- Commit: `9497a00d90bdedf6d1741aa4cf1287fb139ed990`
- Path: `plugins/compound-engineering/skills/ce-clean-gone-branches`

## Mapping Summary
- Donor skill name `ce-clean-gone-branches` -> local stage name `he-prune-branches`.
- Donor workflow preserved:
  - discover with `scripts/clean-gone`,
  - explicit yes/no confirmation on the full candidate set,
  - worktree removal before branch deletion,
  - per-branch outcome reporting.
- Donor `scripts/clean-gone` helper preserved for deterministic gone-branch discovery.

## Harness Engineering Adaptations
- Wording and lifecycle references use Harness Engineering naming consistently.
- Stage-level routing and fallback are aligned to `../../../../../references/routing-map.json`.
- Subagent fallback and missing-role guidance routes to `[[codex-agent-creator]]`.

## Explicit Non-Goals In This Mapping
- This stage does not replace lifecycle orchestration in `he-compound`.
- This stage does not replace implementation work in `he-work`.
- This stage does not perform multi-repo governance cleanup in one pass.
