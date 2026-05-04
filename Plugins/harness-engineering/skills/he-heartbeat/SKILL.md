---
name: he-heartbeat
description: "Create or repair Harness Engineering thread heartbeats when monitoring, wakeups, until-green loops, scheduled live checks, or follow-through automation must re-enter the correct HE stage."
metadata:
  skill-type: team_automation
---
# Harness Engineering Heartbeat
## Philosophy
Wake the thread with fresh state, not stale memory. Scheduling keeps cadence; the HE lifecycle still owns the work.

## When to Use
Use when monitoring, wakeups, until-green loops, or follow-up automation is requested.
## Inputs
Target thread/workspace, cadence, stop condition, issue/PR/check links, optional active thread goal.
## Outputs
Return schema_version when structured. Heartbeat prompt, status, stop rule, `next_invocation`, `subagent_policy`, and next user-visible update.
## Procedure
Prefer thread heartbeat for this conversation; encode stop criteria; avoid duplicate automations. When `/goal` is active or requested, keep the goal as the persistent objective and the heartbeat as the scheduler with live checks and stop rules.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Confirm schedule, destination, and safe prompt scope.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Constraints
Redact secrets; do not create cron workarounds for short thread follow-up. Do not remove important context for budget trimming; move deep context to references.
## Anti-patterns
- Do not create duplicate heartbeats for the same target and stop rule.
- Do not use a heartbeat prompt or `/goal` objective as a replacement for Linear, PR, validation, or lifecycle exit evidence.
- Do not schedule unattended destructive actions, merges, deploys, or tracker closure without explicit approval.
## Examples
- "Wake this thread every 30 minutes until PR #68 is green, then route to `he-work` for the merge handoff."
- "Monitor the deployment check for JSC-246 and stop once the live health query passes twice."
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Goal continuity: `Plugins/harness-engineering/references/goal-continuity.md`
