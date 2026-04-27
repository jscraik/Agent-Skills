# he-heartbeat Automation Prompt Contract

Use this reference when a heartbeat needs a durable prompt that a future Codex
wake-up can execute without relying on stale thread memory.

## Required Fields

- `target`: concrete repo, branch, PR, Linear issue, deploy, validation command,
  or artifact path.
- `cadence`: human-readable recurrence, plus the parsed interval when provided.
- `route_each_wakeup_to`: exact Harness Engineering stage invocation.
- `cwd`: absolute repository path when shell or git commands are expected.
- `live_checks`: exact checks to run or surfaces to inspect before acting.
- `stop_conditions`: done, green, merged, blocked, repeated deterministic
  failure, cancellation, or max-age rules.
- `report_policy`: where and when the heartbeat should update the user.
- `safety`: approval gates and operations that must not be automated.

## Prompt Template

```yaml
heartbeat:
  target: "<target>"
  cadence: "<cadence>"
  route_each_wakeup_to: "$harness-engineering:<stage> <target>"
  cwd: "<absolute path>"
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
