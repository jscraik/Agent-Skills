---
name: he-fix-bugs
description: "Use when HE test, QA, CI, incident, or regression failures need reproduction and fixes."
metadata:
  skill-type: team_automation
---
# Harness Engineering Fix Bugs
## When to Use
Use when tests, QA, CI, incidents, or regressions fail.
## Inputs
Failure evidence, repro, diff, Linear/spec/plan/PR links.
## Outputs
Return schema_version when structured. Root cause, fix, validation, rollback note, next review handoff.
## Procedure
Reproduce first; inspect changed path; patch narrowly; validate exact failure path.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Show command outcomes and remaining risk.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Constraints
Redact secrets; preserve user edits. Do not remove important context for budget trimming; move deep context to references.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
