---
name: he-heartbeat
description: "WHAT: Automate HE wakeups, monitoring, until-green checks, and follow-through. Use when later thread continuation is needed."
metadata:
  skill-type: team_automation
---
# Harness Engineering Heartbeat
## Philosophy
Continue only with a clear stop rule. Heartbeats should preserve context, not create background noise.
## When to Use
Use when monitoring, wakeups, until-green loops, or follow-up automation is requested.
## Inputs
Target thread/workspace, cadence, stop condition, issue/PR/check links.
## Outputs
Return schema_version when structured. Heartbeat prompt, status, stop rule, `next_invocation`, `subagent_policy`, and next user-visible update.
## Procedure
Prefer thread heartbeat for this conversation; encode stop criteria; avoid duplicate automations.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Confirm schedule, destination, and safe prompt scope.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Constraints
Redact secrets; do not create cron workarounds for short thread follow-up. Do not remove important context for budget trimming; move deep context to references.
## Anti-Patterns
- Creating duplicate wakeups for the same PR, issue, or thread.
- Running without an explicit stop condition or next visible update.
## Examples
- "Inspect PR 154 every 30 minutes in this thread until CI is green or a blocker appears."
- "Keep watching JSC-246 after the merge queue starts and wake this thread with the next required action."
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
