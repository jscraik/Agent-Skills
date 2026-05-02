---
name: he-compound
description: "Plan and coordinate multi-stage Harness Engineering runs across brainstorm, spec, plan, work, review, Linear, and PR state. Use when work spans stages or needs resume control."
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
Inspect live state; pick stage order; keep Linear/spec/plan/PR links; refresh Project Brain when ~/dev/coding-harness context changes.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Check routing, stage artifacts, and handoff evidence.
## Constraints
Redact secrets; never collapse multi-stage work into one vague task. Do not remove important context for budget trimming; move deep context to references.
## Anti-patterns
No orphan stages, duplicate plans, or untracked execution.
## Philosophy
Harness Engineering compounds coordinate state, not ceremony.
## Examples
- User says: "Can you inspect this stalled multi-stage run and resume the right HE stage?"
- User says: "Help me connect project brain, Linear, spec, plan, and PR state."
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Assets: `assets/icon-small.png`, `assets/icon-large.png`
