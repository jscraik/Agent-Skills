# Capture Record Schema (Phase 4)

Defines the per-run post-use capture artifact for skill invocation envelope, output summary, feedback, and evidence linkage.

## Table of Contents

- [Required fields](#required-fields)
- [Feedback contract](#feedback-contract)
- [Example](#example)

## Required fields

```yaml
schema_version: "1.0"
capture_id: string                    # deterministic short id
run_id: string
profile_id: string
scope_skill: string
scope_profile: string
created_at: string                    # ISO-8601
invocation_envelope:
  invocation_id: string
  invoked_at: string                  # ISO-8601
  actor_id: string
  run_owner: string
  objective_hash: string              # sha256
  idempotency_key: string
  kill_switch_file: string
  rollback_required_file: string
output_summary:
  finished_at: string                 # ISO-8601
  terminal_status: string             # passed|failed|escalated|aborted
  stop_reason: string
  iterations_completed: int
  tokens_used: int
  duration_ms: int
feedback:
  status: string                      # worked|partly|didnt_work|missing
  note: string                        # optional, max 500 chars
  captured_at: string                 # ISO-8601
  source: string                      # cli_one_tap|none
evidence:
  evidence_packet_id: string
  evidence_packet_path: string
  completeness: object
```

## Feedback contract

- `status=missing` means no explicit one-tap feedback was provided for the run.
- `status` values (`worked|partly|didnt_work`) represent immediate post-run user/operator outcome input.
- `note` is optional and should be sanitized/redacted before downstream promotion usage.

## Example

```json
{
  "schema_version": "1.0",
  "capture_id": "9f7f3f4f7a8ce2cd",
  "run_id": "run_20260225T180100Z_12ab34",
  "profile_id": "ui-ux-creative-coding",
  "scope_skill": "ui-ux-creative-coding",
  "scope_profile": "ui",
  "created_at": "2026-02-25T18:01:05Z",
  "invocation_envelope": {
    "invocation_id": "610fc2f18a6e32d1",
    "invoked_at": "2026-02-25T18:01:00Z",
    "actor_id": "recursive-skill-loop",
    "run_owner": "shadow-cycle",
    "objective_hash": "sha256:...",
    "idempotency_key": "a76f7abf0d6de8b1cc93",
    "kill_switch_file": "",
    "rollback_required_file": ""
  },
  "output_summary": {
    "finished_at": "2026-02-25T18:01:05Z",
    "terminal_status": "passed",
    "stop_reason": "pass",
    "iterations_completed": 1,
    "tokens_used": 128,
    "duration_ms": 512
  },
  "feedback": {
    "status": "worked",
    "note": "clear and actionable output",
    "captured_at": "2026-02-25T18:01:00Z",
    "source": "cli_one_tap"
  },
  "evidence": {
    "evidence_packet_id": "e7d8b226c2c1370a",
    "evidence_packet_path": "evidence_packet.json",
    "completeness": {
      "events": true,
      "logs": false,
      "traces": true,
      "session_signals": true,
      "checks": true,
      "score": 0.8
    }
  }
}
```
