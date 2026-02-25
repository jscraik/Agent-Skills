# Daily Telemetry Outputs

Daily operator artifacts for recursive loop health monitoring.

## Required outputs

- `daily-skill-health.md`
- `failure-pattern-candidates.jsonl`
- `promotion-queue.md`

`promotion-queue.md` entries should include:
- run id + profile id
- confidence score + confidence bucket
- evidence completeness score
- candidate lesson count
- rollout mode + injected lesson count

`daily-skill-health.md` should include:
- capture coverage (`capture_record` written / total runs)
- confidence bucket counts (`high|medium|low|unknown`)
- injection usage rate (runs with injected lessons / total runs)
- suppression count (runs where retrieval occurred but injection was disabled by controls)
- uplift gate decision counts (`pass|hold|insufficient_data|regressed`) for promotion and auto-apply paths

## Minimum event envelope

```yaml
schema_version: "1.0"
event_id: "uuid"
ts: "ISO-8601"
run_id: "run-id"
skill_name: "kebab-case"
task_profile: "profile-id"
event_type: "run_initialized|run_state_changed|promotion_approved|failure_event|run_blocked"
severity: "info|warn|fail"
terminal_status: "passed|failed|escalated|aborted|null"
stop_reason: "pass|budget_exhausted|escalated|aborted|policy_failed|evaluator_conflict|dependency_missing|null"
blocker_code: "run_rollforward_blocked|run_rollback_required|kill_switch_activated|evaluator_conflict|null"
```

Required per run:
- `events.jsonl` must exist (always-on output).
- At least one `run_state_changed` event must be present.
- Approved decisions must emit `promotion_approved`.
- Blocked/rejected control paths must emit `run_blocked` with non-null `blocker_code`.

## Retention + privacy

- Redact secrets/PII before storage.
- Apply TTL policy to draft artifacts.
- Limit raw trace access to authorized reviewers/operators.
