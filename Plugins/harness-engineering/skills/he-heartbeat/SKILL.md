---
name: he-heartbeat
description: "Create and validate Harness Engineering follow-up loops. Use when monitoring, wakeups, until-green checks, or continued thread follow-through is requested."
metadata:
  skill-type: team_automation
---
# Harness Engineering Heartbeat
## When to Use
Use when monitoring, wakeups, until-green loops, or follow-up automation is requested.
## Inputs
Target thread/workspace, cadence, stop condition, issue/PR/check links.
## Outputs
Return schema_version when structured. Heartbeat prompt, status, stop rule, and next user-visible update.
## Procedure
Prefer thread heartbeat for this conversation; encode stop criteria; avoid duplicate automations.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Confirm schedule, destination, and safe prompt scope.
## Constraints
Redact secrets; do not create cron workarounds for short thread follow-up. Do not remove important context for budget trimming; move deep context to references.
## Anti-patterns
No infinite loops, vague reminders, or silent failure states.
## Philosophy
Harness Engineering heartbeats keep live work honest.
## Examples
- User says: "Can you keep checking this PR until CI is green?"
- User says: "Wake this thread later and continue from the same evidence."
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
