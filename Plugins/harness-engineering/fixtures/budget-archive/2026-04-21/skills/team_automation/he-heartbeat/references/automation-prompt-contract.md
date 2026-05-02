# he-heartbeat Automation Prompt Contract

Use this reference when a heartbeat needs a durable prompt that a future Codex
wake-up can execute without relying on stale thread memory.

## Required Fields

- `target`: concrete repo, branch, PR, Linear issue, deploy, validation command,
  or artifact path.
- `cadence`: human-readable recurrence, plus the parsed interval when provided.
- `heartbeat_mode`: one of `active_execution`, `review_readiness`,
  `blocker_watch`, `deploy_watch`, or `passive_monitor`.
- `route_each_wakeup_to`: exact Harness Engineering stage invocation.
- `cwd`: absolute repository path when shell or git commands are expected.
- `live_checks`: exact checks to run or surfaces to inspect before acting.
- `stop_conditions`: done, green, merged, blocked, repeated deterministic
  failure, cancellation, or max-age rules.
- `report_policy`: where and when the heartbeat should update the user.
- `safety`: approval gates and operations that must not be automated.
- `activation`: whether a runtime heartbeat automation must exist, plus the
  duplicate-handling policy.
- `progress_cursor`: required for plan-led active execution; describes the
  state source and next-step rule.

## Prompt Template

```yaml
heartbeat:
  target: "<target>"
  cadence: "<cadence>"
  heartbeat_mode: "<active_execution | review_readiness | blocker_watch | deploy_watch | passive_monitor>"
  route_each_wakeup_to: "$harness-engineering:<stage> <target>"
  cwd: "<absolute path>"
  activation:
    requires_runtime_automation: true
    duplicate_policy: "update-existing"
    status_evidence: "<automation id, status, destination, and cadence>"
  progress_cursor:
    source: "<plan checklist | issue | PR thread | artifact path>"
    next_step_rule: "<how the next wake-up selects work>"
    completion_gate: "<optional final HE stage or review gate>"
  live_checks:
    - "<check 1>"
    - "<check 2>"
  stop_conditions:
    - "<condition 1>"
    - "<condition 2>"
  report_policy: "<state-change-only | every wake-up | blocker-only>"
  safety:
    - "read live state before acting"
    - "do not auto-merge"
    - "do not run destructive commands without explicit approval"
```

## Wake-Up Procedure

1. Read the target live state.
2. Classify the target as `done`, `actionable`, `waiting`, or `blocked`.
3. If `done`, report the result and stop or ask the user to cancel the
   automation.
4. If `blocked`, report exact blocker evidence and stop after the same
   deterministic blocker repeats twice.
5. If `actionable`, invoke or follow the selected HE stage.
6. If `waiting`, report only when the user requested every wake-up updates or
   when the state changed since the previous heartbeat.

For `active_execution`, report every wake-up with the live state checked, the
selected next unit, the action taken, validation outcome, blocker if any, and the
next expected unit. Do not use state-change-only reporting for active
implementation loops.

## Activation Evidence

Do not call a heartbeat active unless a runtime automation record exists. When
the runtime exposes an automation tool, create or update a `kind=heartbeat`
automation attached to the current thread and capture its id, status,
destination, and cadence. If automation creation is unavailable or fails, label
the output as `manual-only` or `blocked` and include the exact reason.

Before creating a heartbeat, look for an existing matching heartbeat and update
it instead of creating a duplicate.

## Routing Examples

- PR check monitor: `route_each_wakeup_to:
  "$harness-engineering:he-code-review PR <number>"`
- failing validation loop: `route_each_wakeup_to:
  "$harness-engineering:he-fix-bugs <command/failure>"`
- compound run refresh: `route_each_wakeup_to:
  "$harness-engineering:he-compound-refresh <artifact or state>"`
- deploy reliability watch: `route_each_wakeup_to:
  "$harness-engineering:he-reliability-review <deploy/status target>"`

## Anti-Patterns

- scheduling a broad "keep working" prompt with no target or stop condition
- using stale prior output instead of rechecking live state
- treating review approval, merge, destructive cleanup, or production mutation
  as safe unattended actions
- converting a one-off HE request into a recurring automation
- hiding credential, permission, or environment blockers behind repeated retries
