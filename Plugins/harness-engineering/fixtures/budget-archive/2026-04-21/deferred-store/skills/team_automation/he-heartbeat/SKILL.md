---
name: he-heartbeat
description: Create, review, or repair recurring Harness Engineering heartbeats that wake a thread, re-check live state, and route back into the right HE stage; use when PRs, CI, reviews, deploys, validation ladders, or compound runs need recurring follow-up until done, blocked, or cancelled.
metadata:
  skill-type: team_automation
  lifecycle-stage: heartbeat
---

# Harness Engineering Heartbeat

Use this skill when the user wants a recurring Harness Engineering control loop:
watching CI, PR readiness, CodeRabbit or Codex review threads, validation
ladders, blocked deploys, long-running compound work, or any HE lane that must
keep waking up until there is a real stop condition.

Do not use this for a one-off check. Route one-off implementation, review, or
debugging requests to the matching HE stage directly.

Do not remove important context for budget trimming; move long-form heartbeat
examples, prompt variants, and implementation notes into deferred references.

## Philosophy

`he-heartbeat` does not replace the stage that does the work. It wraps that stage
in a recurring follow-up loop with clear cadence, live-state checks, and stop
conditions.

For generic automation design, use the `codex-automation-architect` skill as the
substrate. For Harness Engineering loops, this skill adds HE-specific routing,
validation evidence, and lifecycle handoff rules.

## When To Use

Use `he-heartbeat` when the request includes one or more of these signals:

- a recurring cadence such as `every 10m`, `hourly`, `keep checking`, `monitor`,
  `heartbeat`, `wake up`, `poll`, `loop`, or `until green`
- PR or CI work that should remain open until checks are green, merged, or
  explicitly blocked
- a CodeRabbit, Codex review, Linear, deploy, or validation gate that may change
  after the current turn
- a compound HE run that needs periodic refresh against live branch, tracker, or
  review state
- a prior-session or session-collector pattern showing repeated PR, CI, review,
  Linear, validation, or `continue` loops without a durable wake-up
- a blocked lane where the right next move depends on external state changing

Avoid `he-heartbeat` when:

- the user asks for immediate one-off implementation, review, planning, or bug
  fixing with no recurrence
- the task is a generic personal reminder without a Harness Engineering stage
- the loop would run destructive commands, mutate production state, or auto-merge
  without an explicit human approval checkpoint
- there is no stop condition; ask one focused question or propose a bounded
  default before scheduling

## Required Inputs

Collect or infer:

- target: repo path, PR number, Linear issue, validation command, branch, deploy,
  or artifact path
- cadence: default to `10m` when the user asks for a heartbeat but gives no
  interval
- stage route: the HE skill that should run on each wake-up
- checks: exact status commands or surfaces to inspect
- stop conditions: done, green, merged, blocker, repeated deterministic failure,
  user cancellation, or maximum age
- reporting policy: concise thread update, artifact update, PR comment draft, or
  no write unless state changed

## Procedure

1. Confirm the request is recurring Harness Engineering work, not a one-off HE
   action or a generic reminder.
2. Identify the concrete target, cadence, live-state checks, stop conditions,
   reporting policy, and approval-sensitive operations.
3. If session evidence is used to justify the heartbeat, read
   [../../../../../../references/session-evidence-contract.md](../../../../../../references/session-evidence-contract.md)
   and cite the collector output, archive path, index count, or exact sample.
4. Select the underlying HE stage that should run on each wake-up. If stage
   selection is ambiguous, route through `he-router` before scheduling.
5. Build the durable heartbeat prompt using the contract below and the full
   prompt reference.
6. Create or describe the automation only when the runtime exposes an automation
   tool. If the tool is unavailable, report the exact blocker and provide the
   prompt for manual creation.
7. Execute the first safe live-state check immediately in the current turn.
8. Tell the user how the heartbeat will stop or when it will ask for human
   cancellation.

## Activation Contract

A heartbeat is not active until a runtime automation record exists.

When the runtime exposes an automation tool:

1. Search for an existing matching heartbeat by name, target, prompt, PR, plan,
   branch, issue, deploy, or thread context.
2. Prefer updating the existing matching heartbeat over creating a duplicate.
3. Create or update a `kind=heartbeat` automation attached to the current thread.
4. Return the automation id, name, status, cadence, destination, and target
   binding.
5. Do not describe a heartbeat as created unless automation creation or update
   succeeded.

If the runtime does not expose an automation tool, or if automation creation
fails, return `automation.status: blocked` or `automation.status: manual-only`
with the exact reason and provide the durable prompt for manual creation. Manual
prompt output is a fallback, not an active heartbeat.

Use this rule when answering whether a heartbeat is working:

```text
No automation id, no active heartbeat.
```

## Heartbeat Modes

Classify the heartbeat mode before scheduling. The mode sets the default stage,
reporting cadence, and stop posture.

| Mode | Use When | Default Stage | Default Reporting |
| --- | --- | --- | --- |
| `active_execution` | A plan or implementation lane should keep moving through phases | `he-work` | every wake-up |
| `review_readiness` | PR checks, mergeability, CodeRabbit, Codex, or approval state may change | `he-code-review` | state-change-only |
| `blocker_watch` | A known credential, permission, external CI, deploy, or environment blocker may clear | selected stage | blocker changes or repeats |
| `deploy_watch` | Release, deploy, or service health needs recurring reliability review | `he-reliability-review` | state-change-only |
| `passive_monitor` | The user wants read-only status monitoring | selected stage | state-change-only |

For `active_execution`, report a concise update on every wake-up that includes
the live state checked, the selected next unit, actions taken, validation
outcome, blocker if any, and next expected unit. Do not hide active work behind
state-change-only reporting.

## Plan Execution Heartbeats

When `heartbeat_mode` is `active_execution` for a plan-led run, include a
progress cursor in the heartbeat prompt:

- `target_plan`: absolute path to the governing plan.
- `phase_range`: the approved plan units or checkpoints.
- `state_source`: plan checklist, implementation evidence, validation evidence,
  and live git state.
- `next_step_rule`: choose the first incomplete unit with missing implementation
  or validation evidence.
- `completion_gate`: the HE stage or review pass to run after implementation
  completes.

Each wake-up must keep the plan state synchronized with implementation reality.
Do not mark a unit complete before validation evidence exists.

## Repair Diagnostics

When the user asks whether a heartbeat is working, inspect the automation
runtime before answering when a runtime automation tool is available:

1. Confirm whether a matching automation exists.
2. Confirm `kind=heartbeat`, destination or thread binding, cadence, status, and
   prompt target.
3. Report whether it is active, paused, missing, manual-only, or blocked.
4. If no automation exists, say clearly that only a manual prompt was produced
   and offer to create the heartbeat.
5. If the automation exists but is not waking, classify the runtime/tooling
   blocker with exact evidence.

## Cadence Parsing

Parse cadence in this order:

1. Leading interval token, such as `5m`, `30m`, `2h`, or `1d`.
2. Trailing `every <interval>` clause, such as `every 20m`, `every 5 minutes`,
   or `every 2 hours`.
3. Natural recurrence words, such as `hourly` or `daily`.
4. Default to `10m` only when recurrence is clearly requested.

Do not treat phrases like `check every PR` as a cadence unless a time expression
follows `every`.

## Stage Routing

Choose the underlying HE stage before creating the heartbeat:

| Live State To Recheck | Route Each Wake-Up To |
| --- | --- |
| PR readiness, mergeability, review-thread closure | `he-code-review` |
| external review feedback validity | `he-technical-review` |
| failing test, regression, reproduction, root cause | `he-fix-bugs` |
| a bug fix that must start with RED/GREEN evidence | `he-tdd` |
| approved plan or narrow implementation slice | `he-work` |
| compound workflow drift, stale state, handoff refresh | `he-compound-refresh` |
| deploy health, retries, cascading failure, SLO concern | `he-reliability-review` |
| stale branch cleanup or gone-remote follow-up | `he-prune-branches` |

If two stages are plausible, route to `he-router` first and schedule only after
the stage decision is concrete.

## Outputs

Return a concise structured summary:

```yaml
schema_version: 1
heartbeat_mode: "<active_execution | review_readiness | blocker_watch | deploy_watch | passive_monitor>"
selected_cadence: "<cadence>"
parsed_interval: "<normalized interval or default rationale>"
selected_stage: "$harness-engineering:<he-stage>"
target: "<target>"
automation:
  name: "<automation name>"
  status: "<created | updated | already-active | blocked | manual-only>"
  id: "<automation id or null>"
  kind: "heartbeat"
  destination: "thread"
  target_binding: "<current thread | explicit target thread | detached workspace>"
  active: "<true | false>"
  next_expected_wakeup: "<cadence-derived expectation>"
live_checks:
  - "<check>"
stop_conditions:
  - "<condition>"
heartbeat_prompt: "<durable prompt payload or path to generated prompt>"
immediate_run: "<pass | fail | blocked | not-run with reason>"
next_wakeup_behavior: "<what the next wake-up should do>"
```

## Heartbeat Prompt Shape

Build the recurring prompt as a durable instruction block with `target`,
`cadence`, `route_each_wakeup_to`, `cwd`, `live_checks`, `stop_conditions`,
`report_policy`, and `safety`. Use
`./references/automation-prompt-contract.md` for the full prompt template.

The prompt must tell the next wake-up agent to:

1. Re-read live state first: branch, PR, checks, review threads, Linear status,
   or validation output as relevant.
2. Compare current state with the previous heartbeat note if one exists.
3. Invoke or follow the selected HE stage for the next action.
4. Post a concise update only when state changes, action was taken, or a blocker
   is reached.
5. Stop or ask the user to cancel the automation when the stop condition is met.

## Immediate Run

After creating or describing the heartbeat, execute the first check immediately
inside the current turn when safe. Do not wait for the first scheduled wake-up to
discover an already-green, already-blocked, or misrouted target.

If the current environment lacks an automation tool, output the exact heartbeat
prompt and say automation creation is blocked by missing tool access.

## Stop Rules

Stop the loop or tell the user to cancel it when:

- the target PR is merged, closed, or no longer exists
- required checks are green and the remaining blocker is human approval
- a deterministic credential, permission, or environment failure repeats twice
  with the same root cause
- the requested work completes and no live gate remains
- the automation target becomes ambiguous or the branch has moved unexpectedly
- the user changes the goal or asks to stop

## Constraints

- Redact secrets, tokens, private keys, and sensitive customer data from
  heartbeat prompts, reports, and artifacts by default.
- Do not auto-merge PRs, approve review threads, run destructive cleanup, mutate
  production, or change tracker state without explicit user approval.
- Do not schedule a heartbeat when the target, stage route, or stop condition is
  unknown; ask one focused question or return a blocked summary.
- Do not rely on stale thread memory; every wake-up must read live state first.
- Prefer state-change reports over noisy repeated updates unless the user asked
  for every wake-up report.

## Failure mode

If live state cannot be read, do not continue from stale thread context. Report
the missing surface, the exact command or API that failed, and the next safe
manual action.

## Gotchas

- A heartbeat is not approval to merge, deploy, delete, or close work.
- A green check suite can still be blocked by unresolved review conversations or
  human approval policy.
- Repeated identical credential or permission failures should stop the loop
  instead of consuming more wake-ups.

## Validation

Before claiming a heartbeat is ready:

- verify the target path, PR, issue, or command exists when it is locally
  inspectable
- verify the underlying HE stage is named in the prompt
- verify cadence, stop conditions, and reporting policy are explicit
- verify the prompt requires fresh live-state reads before action
- verify session-derived heartbeat decisions cite the evidence source
- verify destructive actions and auto-merge are gated behind explicit approval

## Examples

- User says: "Can you keep checking GitHub PR 137 every 10m until CI and
  CodeRabbit are green?" Select `he-code-review`, verify PR and check surfaces,
  and stop at green, merged, or approval-only state.
- User says: "Wake this thread hourly and inspect Linear before refreshing the
  compound run." Select `he-compound-refresh`, read branch/tracker state first,
  and report only changed blockers.
- User says: "Please validate this deploy check every 15m and stop if the same
  health blocker repeats." Select `he-reliability-review`, capture exact failure
  evidence, and stop after the repeated deterministic blocker.
- User says: "Sessions show we keep saying continue while PR reviews are still
  open." Select the review-stage heartbeat, cite the session evidence, and stop
  at review-thread closure, green checks, merged, or blocked.

## Anti-Patterns

- Scheduling "keep working" with no concrete target or stop condition.
- Hiding credentials, permission, or environment blockers behind repeated
  retries.
- Treating review approval, merge, destructive cleanup, or production mutation
  as safe unattended actions.
- Converting a one-off review, plan, or fix request into a recurring automation.
- Letting a heartbeat continue after the branch, PR, or artifact target moved.

## Full Context

Read `./references/automation-prompt-contract.md` when writing a new heartbeat
prompt, reviewing a heartbeat prompt, or repairing a drifted loop.
Use `Plugins/harness-engineering/references/deferred-context-index.md` to locate
deferred Harness Engineering context before expanding this root skill body.
Read [../../../../../../references/session-evidence-contract.md](../../../../../../references/session-evidence-contract.md)
when prior sessions or collector output justify creating, repairing, or rejecting
a heartbeat.
