---
name: he-compound
description: "Use when HE work spans Linear, spec, plan, work, review, and PR state."
metadata:
  skill-type: team_automation
---
# Harness Engineering Compound
## When to Use
Use when work spans brainstorm/spec/plan/work/review or needs refresh/resume control.
## Inputs
Goal, Linear/project-brain state, specs, plans, PRs, session evidence.
## Outputs
Return schema_version when structured. Stage map, active owner, blockers, next action, and retained references.
## Procedure
Inspect live state; pick stage order; keep Linear/spec/plan/PR links; refresh Project Brain when repository context changes.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Check routing, stage artifacts, and handoff evidence.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Constraints
Redact secrets; never collapse multi-stage work into one vague task. Do not remove important context for budget trimming; move deep context to references.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
