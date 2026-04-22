# Source Parity

Read when: validating that `he-prune-branches` preserves the current Harness Engineering cleanup workflow and branch-hygiene constraints.

## Review Baseline
- Active stage: `Plugins/harness-engineering/skills/team_automation/he-prune-branches/`
- Canonical discovery helper: `scripts/clean-gone`
- Routing contract: `../../../../../references/routing-map.json`

## Mapping Summary
- `he-prune-branches` preserves the local cleanup flow:
  - discover stale local branches with `scripts/clean-gone`,
  - show the full candidate set before any deletion,
  - require one explicit yes/no confirmation for the whole set,
  - remove associated non-root worktrees before branch deletion,
  - report branch-level outcomes and final totals.
- The stage keeps deterministic gone-branch discovery through the local `scripts/clean-gone` helper.

## Harness Engineering Adaptations
- Lifecycle wording and routing remain aligned to Harness Engineering stages.
- Stage-level routing and fallback are aligned to `../../../../../references/routing-map.json`.
- Subagent fallback and missing-role guidance route to `[[codex-agent-creator]]`.
- Validation explicitly protects the main repository worktree from accidental removal.

## Explicit Non-Goals In This Mapping
- This stage does not replace lifecycle orchestration in `he-compound`.
- This stage does not replace implementation work in `he-work`.
- This stage does not perform multi-repo governance cleanup in one pass.
