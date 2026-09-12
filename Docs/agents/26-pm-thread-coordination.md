# PM Thread Coordination

Use this contract when Jamie designates one Codex thread as the Skills SDK PM
decision thread and other Codex threads as execution lanes.

## Authority

The PM thread is the decision surface for Skills SDK gate movement. Execution
threads may run repo work, write artifacts, and propose next actions, but they do
not advance the Skills SDK pipeline until the PM thread has both:

1. a validated durable reply artifact, and
2. PM delivery evidence that the artifact was reported back to the PM thread.

Chat text alone is not enough. A local artifact alone is also not enough when
the PM thread is making the next decision.

## Thread Task

Every PM-to-execution instruction should name:

- source PM thread id.
- target execution thread id.
- requested responsibility, selected capability, active dispatch tool, and
  reason selected. Dispatch through the available tool; do not consult or
  recreate the retired `~/.codex/agents/manifest.json` role registry.
- repository path and expected head, or a command to rediscover head.
- current gate and explicitly blocked next gates.
- authoritative artifacts to inspect.
- exact commands or wrapper families to use.
- required reply path.

Use `.harness/reports/thread-replies/<thread-id>/latest.json` as the latest
reply artifact.

## Thread Report

Execution threads must write `thread-report/v1` before asking the PM thread to
decide. Validate it with:

```bash
python3 Infrastructure/scripts/validation-and-linting/validate_thread_report.py .harness/reports/thread-replies/<thread-id>/latest.json --json
```

The report must include:

- `thread_id`
- `repo_head`
- `task_id`
- `status`
- `current_gate`
- `next_gate_allowed`
- `blocked_next_gates`
- exact command outcomes
- artifact assertions
- contradictions
- files changed
- lessons to carry forward
- one mechanical next action

Each lessons item must name the reusable lesson, failure pattern,
carry-forward target, deterministic guardrail, recorded location, and validation
evidence. A repair report that only says what changed, without naming what the
SDK should learn, is not a valid PM decision input.

Every execution report must retain the `thread-report/v1`
`agent_profile_selection` object. These fields describe the actual selection,
not membership in a role registry:

- `requested_role`: the responsibility requested by the coordinator.
- `selected_profile_role`: the capability or responsibility assigned.
- `profile_source`: the active dispatch tool or explicitly supplied source.
- `reason_selected`: why this selection serves the bounded task.

Each value must be a non-empty final string. `fallback_reason` is optional;
when supplied, it must also be a non-empty final string. The validator checks
the report itself without reading a home-directory or repository role registry.
Existing v1 reports retain their field names; a historical profile path is
provenance text, not current registry membership or dispatch proof.

A report with an awaiting, authorization-required, or waiting state must also
include `outbound_escalation`, `follow_up_triggered`, or
`escalation_blocked`. Passive heartbeat text is not enough: the lane must
trigger the next responsible lane or record the concrete blocker.

At least one lesson in every report must be recorded in
`.harness/memory/LEARNINGS.md`. Source, eval, validator, and evidence artifacts
can be additional recorded locations, but they do not replace the learned-fix
ledger. This keeps recurring OSS-local, SDK pipeline, Tessl, and thread-delivery
failures available to future agents before the same failure reaches the PM
thread again.

## PM Delivery Receipt

After writing a valid thread report, the execution thread must either send a PM
update or record why delivery is blocked.

The delivery receipt lives next to the report:

```text
.harness/reports/thread-replies/<thread-id>/pm-delivery.json
```

Use `thread-report-delivery/v1`:

```json
{
  "schema_version": "thread-report-delivery/v1",
  "thread_id": "<execution-thread-id>",
  "pm_thread_id": "<pm-thread-id>",
  "report_path": "latest.json",
  "delivery_method": "codex_app__send_message_to_thread",
  "delivery_status": "delivered",
  "delivered_at": "2026-06-28T18:30:00Z",
  "message_summary": "Sent PM update referencing the validated thread-report artifact.",
  "delivery_evidence": "send_message_to_thread returned threadId <pm-thread-id>"
}
```

If delivery cannot happen, set `delivery_status` to `blocked`,
`delivery_method` to `blocked_no_thread_tool`, and put the concrete blocker in
`delivery_evidence`. A blocked delivery receipt preserves the failure but does
not satisfy PM decision readiness.

Validate both the report and PM delivery receipt with:

```bash
python3 Infrastructure/scripts/validation-and-linting/validate_thread_pm_delivery.py .harness/reports/thread-replies/<thread-id>/latest.json --require-delivery --json
```

## Gate Rule

The PM thread should not use an execution thread's output as a Skills SDK gate
decision input unless `validate_thread_pm_delivery.py --require-delivery` passes
for that thread's latest report.

If the report validates but PM delivery does not, classify the lane as:

```text
status=blocked_delivery
```

Then either send the missing PM update and write `pm-delivery.json`, or keep the
gate blocked with the delivery blocker named.

## Contradictions

When a report's narrative conflicts with a receipt, the receipt wins. The report
must list the contradiction, name the owning component, and stop gate movement
until the artifact or report is repaired.
