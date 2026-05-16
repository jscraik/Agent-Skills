# Automation Tool Examples

Use these shapes for codex_app.automation_update calls. Keep schedules in the
tool payload; do not print raw schedule strings in user-facing prose.

## Heartbeat Follow-Up

~~~json
{
  "mode": "create",
  "kind": "heartbeat",
  "destination": "thread",
  "name": "Follow up on Codex skill hardening",
  "prompt": "Continue this thread by checking whether the requested skill hardening work has finished, then summarize blockers or next actions.",
  "rrule": "<schedule-from-tool-interpreter>",
  "status": "ACTIVE"
}
~~~

Use heartbeat automations for short-lived continuation of the current thread,
especially when the user asks to check back later or keep working here.

## Workspace Cron

~~~json
{
  "mode": "create",
  "kind": "cron",
  "executionEnvironment": "local",
  "cwds": ["/absolute/path/to/workspace"],
  "name": "Codex control-plane health check",
  "prompt": "Run the repository's documented Codex control-plane health checks and report pass, fail, or blocked outcomes with exact command evidence.",
  "rrule": "<schedule-from-tool-interpreter>",
  "status": "ACTIVE"
}
~~~

Cron automations are detached workspace jobs. Keep the prompt self-contained and
leave schedule, workspace, and execution environment in tool fields.

## Worktree Proposal With Setup

~~~json
{
  "mode": "suggested_create",
  "kind": "cron",
  "executionEnvironment": "worktree",
  "cwds": ["/absolute/path/to/workspace"],
  "localEnvironmentConfigPath": "/absolute/path/to/environment.toml",
  "name": "Agent skills readiness sweep",
  "prompt": "Review agent skill readiness in the workspace, classify blockers, and report exact validation evidence.",
  "rrule": "<schedule-from-tool-interpreter>",
  "status": "ACTIVE"
}
~~~

Use a suggested create or suggested update when a worktree automation carries a
local environment config path, so the user can review the setup before it is
saved.
