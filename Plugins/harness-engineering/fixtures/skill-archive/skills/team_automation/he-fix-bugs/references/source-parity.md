# Source Parity

Read when: validating how `he-fix-bugs` maps donor behavior while becoming the canonical local bug workflow.

## Donor Source
- Repository: `EveryInc/compound-engineering-plugin`
- Commit: `9497a00d90bdedf6d1741aa4cf1287fb139ed990`
- Path: `plugins/compound-engineering/skills/ce-debug`

## Mapping Summary
- Donor skill name `ce-debug` -> local stage name `he-fix-bugs`.
- Donor root-cause-first workflow (intake, reproduce, diagnose, fix, close) is preserved.
- Donor anti-pattern and investigation reference material is preserved and adapted to local routing.

## Folded Local Skill Contributions
- `Skills/agent-ops/reproduce-bug` contributed tracker-first intake expectations:
  - Linear-first support with GitHub parity,
  - explicit reproduction-status contract,
  - evidence-oriented output schema.
- `Skills/agent-ops/systematic-debugging` contributed:
  - explicit diagnosis-before-remediation posture,
  - blocked/partial completion discipline,
  - safe minimal-change execution guidance.

## Harness Engineering Adaptations
- Wording and stage references use Harness Engineering naming consistently.
- Lifecycle handoff options route to `he-work`, `he-brainstorm`, and `he-compound`.
- Subagent policy uses plugin-canonical routing map and fallback behavior.
- Missing-role guidance routes to `[[codex-agent-creator]]`.

## Explicit Non-Goals In This Mapping
- This stage does not replace `he-plan` or `he-work`.
- This stage does not replace lifecycle orchestration in `he-compound`.
- This stage does not retain legacy standalone `reproduce-bug` or `systematic-debugging` skill packages.
