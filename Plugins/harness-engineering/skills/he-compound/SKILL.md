---
name: he-compound
description: "WHAT: Analyze and route HE lifecycle state across Linear, stages, PRs, and Project Brain. Use when work must resume or refresh."
metadata:
  skill-type: team_automation
---
# Harness Engineering Compound
## Philosophy
Coordinate state, not ceremony. Compound should identify the earliest incomplete stage and preserve the evidence chain that lets the next agent act immediately.
## When to Use
Use when work spans brainstorm/spec/plan/work/review or needs refresh/resume control.
## Inputs
Goal, Linear/project-brain state, specs, plans, PRs, session evidence.
## Outputs
Return schema_version when structured. Stage map, active owner, blockers, next action, blackboard_delta, and retained references.
## Procedure
Inspect live state; pick stage order; keep Linear/spec/plan/PR links; in coding-harness-managed repos preserve Harness lifecycle state and refresh Project Brain when repository context changes. When diagnosis says product compression is the blocker, especially `active_stage: spec_refresh_required`, route to `he-spec` with the compression contract instead of approving another additive implementation pass.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Check routing, stage artifacts, and handoff evidence.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Constraints
Redact secrets; never collapse multi-stage work into one vague task. Do not remove important context for budget trimming; move deep context to references.
## Anti-Patterns
- Turning a multi-stage workflow into one vague implementation task.
- Refreshing Project Brain without checking whether repo context changed.
- Treating a chat summary as a replacement for Linear, spec, plan, PR, or validation links.
- Advancing to work when prior acceptance proved implementation presence but not first-contact compression.
## Examples
- "Inspect and resume the coding-harness run for JSC-246; map Linear, spec, plan, PR, Project Brain, north-star evidence, and tell me the exact next HE stage."
- "Inspect the HE compound state after PR 154 merged, update Project Brain if `.harness` changed, and capture any solved-problem doc that is now warranted."
## Assets
Reference `assets/` only for skill packaging and browseability; lifecycle state belongs in structured handoff evidence.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Coding Harness bridge: `Plugins/harness-engineering/references/coding-harness-command-bridge.md`
- Agent-native compression: `Plugins/harness-engineering/references/agent-native-compression-contract.md`
- Pragmatic operating invariants: `Plugins/harness-engineering/references/pragmatic-operating-invariants.md`
- XP operating contract: `Plugins/harness-engineering/references/xp-operating-contract.md`
