---
name: he-fix-bugs
description: "Debug and repair validated Harness Engineering defects with bounded scope, reproduction evidence, root-cause notes, regression protection, and validation proof. Use when a bug is already evidenced and the fix should not expand into broad improvement work."
metadata:
  skill-type: team_automation
---
# Harness Engineering Fix Bugs
## Philosophy
Prove the failure before fixing it. The smallest reproduced cause gets the smallest safe patch.
## When to Use
Use when tests, QA, CI, incidents, or regressions fail.
## Inputs
Failure evidence, repro, diff, Linear/spec/plan/PR links.
## Outputs
Return schema_version when structured. Root cause, fix, validation, rollback note, repeated_failure when recurring, blackboard_delta, and next review handoff.
## Procedure
1. Reproduce the failure before patching.
2. Inspect the changed path and identify the smallest root cause.
3. Patch narrowly, preserving unrelated user edits and approved scope.
4. Validate the exact failing path before broader gates.
5. When the same failure class recurs, record the root-cause learning and durable fix surface.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Show command outcomes and remaining risk.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Execution Boundaries
Mutate only the reproduced failing path. Do not expand into unrelated cleanup, close trackers, or claim readiness without exact validation evidence.
For direct-handle use, apply the OpenAI-style design contract: classify the strongest side effect and separate read-only analysis, artifact writes, repo edits, external updates, destructive actions, and completion-gating recommendations before proceeding.
## Gotchas
- A failing label is not a reproduction.
- Recurring failures need a durable learning surface after the immediate fix.
## Constraints
Redact secrets; preserve user edits. Do not remove important context for budget trimming; move deep context to references.
## Anti-Patterns
- Guessing from the failing label without reproducing or reading the exact log.
- Expanding into unrelated cleanup while the regression remains unproven.
## Examples
- "Inspect the failing CircleCI job for JSC-246, reproduce the parser failure locally, and patch only that path."
- "The QA note says account settings regressed; validate the bug first, then fix and return exact command outcomes."
## Assets
Reference `assets/` only for skill packaging and browseability; bug evidence belongs in logs, tests, and handoff notes.
## References
- OpenAI-style plugin design: `Infrastructure/references/openai-style-plugin-design-contract.md`
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Pragmatic operating invariants: `Plugins/harness-engineering/references/pragmatic-operating-invariants.md`
- XP operating contract: `Plugins/harness-engineering/references/xp-operating-contract.md`
