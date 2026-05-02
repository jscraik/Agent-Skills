---
name: he-fix-bugs
description: "Debug and fix reproduced Harness Engineering defects with root-cause evidence. Use when tests, QA, CI, incidents, or regressions are failing."
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
## Constraints
Redact secrets; preserve user edits. Do not remove important context for budget trimming; move deep context to references.
## Anti-patterns
No speculative fixes, broad rewrites, or unverified success claims.
## Philosophy
Harness Engineering fixes explain cause before claiming repair.
## Examples
- User says: "Can you inspect this failing CI job and fix the regression?"
- User says: "Validate the QA bug, patch it, and keep the Linear trace."
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Assets: `assets/icon-small.png`, `assets/icon-large.png`
