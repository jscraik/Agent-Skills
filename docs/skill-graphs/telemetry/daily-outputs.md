# Daily Telemetry Outputs

Daily operator artifacts for recursive loop health monitoring.

## Required outputs

- `daily-skill-health.md`
- `failure-pattern-candidates.jsonl`
- `promotion-queue.md`

## Minimum event envelope

```yaml
schema_version: "1.0"
event_id: "uuid"
ts: "ISO-8601"
run_id: "run-id"
skill_name: "kebab-case"
task_profile: "profile-id"
event_type: "run_initialized|run_state_changed|promotion_approved|failure_event"
severity: "info|warn|fail"
terminal_status: "passed|failed|escalated|aborted|null"
stop_reason: "pass|budget_exhausted|escalated|aborted|policy_failed|evaluator_conflict|dependency_missing|null"
```

## Retention + privacy

- Redact secrets/PII before storage.
- Apply TTL policy to draft artifacts.
- Limit raw trace access to authorized reviewers/operators.
