# Evidence Packet Schema (Phase 4)

Defines the assembled run-local evidence packet used for confidence scoring and causal gate decisions.

## Table of Contents

- [Required fields](#required-fields)
- [Completeness scoring](#completeness-scoring)
- [Example](#example)

## Required fields

```yaml
schema_version: "1.0"
evidence_packet_id: string
run_id: string
created_at: string                    # ISO-8601
sources:
  events:
    present: bool
    path: string
    sha256: string
    size_bytes: int
  logs:
    present: bool
    paths: string[]
  traces:
    present: bool
    path: string
    sha256: string
    size_bytes: int
  session_signals:
    present: bool
    terminal_status: string
    stop_reason: string
    iterations_completed: int
    tokens_used: int
    duration_ms: int
  checks:
    present: bool
    runtime_gates_passed: bool
    provenance_complete: bool
    security_checklist_passed: bool
    run_blocker_present: bool
completeness:
  events: bool
  logs: bool
  traces: bool
  session_signals: bool
  checks: bool
  score: float                        # 0.0..1.0
```

## Completeness scoring

- `score` is the fraction of evidence classes present across:
  `events`, `logs`, `traces`, `session_signals`, `checks`.
- Missing optional debug logs is represented explicitly as `logs=false`.
- Consumers should consider both class-level booleans and overall `score`.

## Example

```json
{
  "schema_version": "1.0",
  "evidence_packet_id": "e7d8b226c2c1370a",
  "run_id": "run_20260225T180100Z_12ab34",
  "created_at": "2026-02-25T18:01:05Z",
  "sources": {
    "events": {
      "present": true,
      "path": "events.jsonl",
      "sha256": "d7f6...",
      "size_bytes": 1420
    },
    "logs": {
      "present": false,
      "paths": []
    },
    "traces": {
      "present": true,
      "path": "iteration_journal.jsonl",
      "sha256": "2a84...",
      "size_bytes": 3082
    },
    "session_signals": {
      "present": true,
      "terminal_status": "passed",
      "stop_reason": "pass",
      "iterations_completed": 1,
      "tokens_used": 128,
      "duration_ms": 512
    },
    "checks": {
      "present": true,
      "runtime_gates_passed": true,
      "provenance_complete": true,
      "security_checklist_passed": false,
      "run_blocker_present": false
    }
  },
  "completeness": {
    "events": true,
    "logs": false,
    "traces": true,
    "session_signals": true,
    "checks": true,
    "score": 0.8
  }
}
```
