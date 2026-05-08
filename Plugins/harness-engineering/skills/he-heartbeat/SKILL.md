---
name: he-heartbeat
description: "Create bounded HE follow-up checkpoints. Use when work must resume later with stop rules."
metadata:
  skill-type: team_automation
  triggers:
    - he heartbeat
    - goal-aware scheduling
    - until-green checks
    - thread continuation
---
# Harness Engineering Heartbeat
## Philosophy
Continue only with a clear stop rule. Heartbeats should preserve context, wake the thread with fresh state, and keep scheduling separate from HE lifecycle ownership.
## When to Use
Use when monitoring, wakeups, until-green loops, or follow-up automation is requested.
## Inputs
Target thread/workspace, cadence, stop condition, issue/PR/check links, optional active thread goal.
## Outputs
Return schema_version when structured. Heartbeat prompt, status, stop rule, `next_invocation`, `subagent_policy`, slack_policy, blackboard_delta, and next user-visible update.
## Procedure
1. Prefer a thread heartbeat for this conversation.
2. Encode cadence, destination, stop criteria, live checks, and the next visible update.
3. Search for an existing matching heartbeat before creating a duplicate.
4. When `/goal` is active or requested, keep the goal as the persistent objective and the heartbeat as the scheduler.
5. For GitHub PR sweeps, identify the PR set, re-check GitHub truth, inspect CircleCI/job logs, and inspect CodeRabbit/Codex review threads.
6. Route each wake-up to the smallest safe `he-code-review` or `he-work` follow-up.
7. Use `git-project-triage` only when it is available in the Codex agent manifest; otherwise continue inline and report the delegation gap.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Confirm schedule, destination, and safe prompt scope.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Execution Boundaries
Heartbeats schedule wakeups and checks. Do not use a heartbeat prompt as authority to merge, deploy, close trackers, or perform destructive actions.
## Gotchas
- Duplicate automations create noisy state and must be avoided.
- A stop rule is mandatory before scheduling.
## Constraints
Redact secrets; do not create cron workarounds for short thread follow-up. Do not remove important context for budget trimming; move deep context to references. Keep scope tight: start with 2-3 focused surfaces and expand only when the next heartbeat needs more context.
## Anti-Patterns
- Creating duplicate wakeups for the same PR, issue, or thread.
- Running without an explicit stop condition or next visible update.
- Using a heartbeat prompt or `/goal` objective as a replacement for Linear, PR, validation, or lifecycle exit evidence.
- Scheduling unattended destructive actions, merges, deploys, or tracker closure without explicit approval.
## Examples
- "Inspect PR 154 every 30 minutes in this thread until CI is green or a blocker appears."
- "Keep watching JSC-246 after the merge queue starts and wake this thread with the next required action."
- "Rotate across the open coding-harness PRs with GitHub, CircleCI, CodeRabbit, and Codex comments; use `git-project-triage` when available, wake every 30 minutes, and stop only once the PRs are green, merged, or explicitly blocked."
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Goal continuity: `Plugins/harness-engineering/references/goal-continuity.md`
- Pragmatic operating invariants: `Plugins/harness-engineering/references/pragmatic-operating-invariants.md`
- XP operating contract: `Plugins/harness-engineering/references/xp-operating-contract.md`
