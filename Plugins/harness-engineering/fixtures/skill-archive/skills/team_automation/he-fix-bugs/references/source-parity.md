# Source Parity

Read when: validating how `he-fix-bugs` preserves the archived root-cause-first debugging workflow while remaining the canonical local bug stage.

## Archived Source Baseline
- Root-cause-first debugging workflow with explicit intake, reproduction, diagnosis, fix, and close phases.
- Archived investigation and anti-pattern reference set preserved under this skill package.

## Mapping Summary
- `he-fix-bugs` is the canonical local stage name for this workflow.
- The root-cause-first workflow shape (intake, reproduce, diagnose, fix, close) is preserved.
- Anti-pattern and investigation reference material is preserved and adapted to local routing.

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
- The active front door now makes tracker intake, diagnosis-only vs diagnose-and-fix scope, causal-chain validation, and failing-test-first remediation explicit.

## Explicit Non-Goals In This Mapping
- This stage does not replace `he-plan` or `he-work`.
- This stage does not replace lifecycle orchestration in `he-compound`.
- This stage does not retain legacy standalone `reproduce-bug` or `systematic-debugging` skill packages.
