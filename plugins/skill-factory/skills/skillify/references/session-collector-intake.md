# Session-Collector Intake

Read when: session context alone is incomplete and a `session-collector` artifact is available.

## Goal
Use `session-collector.json` as corroborating evidence for workflow ordering and tool usage without blocking `skillify` when telemetry is missing.

## Default artifact path
- `/Users/jamiecraik/dev/configs/codex/usage-data/session-collector.json`

## Intake checklist
1. Confirm the artifact exists and parseable JSON.
2. Check freshness from `generated_at` and `input_window.cutoff`.
3. Use `summary.top_tool_calls`, `summary.top_project_hints`, and relevant `sessions[*]` entries to corroborate step ordering.
4. Record provenance as `thread_plus_session_collector` when telemetry was used, otherwise keep `thread_only`.
5. Keep hashed identifiers opaque; never expand or infer raw account identity from `*_hash` fields.

## Fallback behavior
- If the file is missing, stale, or ambiguous, proceed with thread-only evidence.
- Explicitly list assumptions introduced due to telemetry gaps before interview rounds.
