# Session-Collector Intake

Read when: session context alone is incomplete and a `session-collector` artifact is available.

## Goal
Use `session-collector.json` as corroborating evidence for workflow ordering and tool usage without blocking `skillify` when telemetry is missing.

## Artifact resolution order
1. Repo-tracked path (e.g., `artifacts/session-collector.json`)
2. Environment variable `SESSION_COLLECTOR_PATH`
3. Package scripts default location
4. Common defaults (e.g., `~/.config/codex/usage-data/session-collector.json`)

**Example path:** `~/.config/codex/usage-data/session-collector.json` (user-specific; adjust to local environment)

## Intake checklist
1. Confirm the artifact exists and parseable JSON.
2. Check freshness from `generated_at` and `input_window.cutoff`.
3. Use `summary.top_tool_calls`, `summary.top_project_hints`, and relevant `sessions[*]` entries to corroborate step ordering.
4. Record provenance as `thread_plus_session_collector` when telemetry was used, otherwise keep `thread_only`.
5. Keep hashed identifiers opaque; never expand or infer raw account identity from `*_hash` fields.

## Fallback behavior
- If the file is missing, stale, or ambiguous, proceed with thread-only evidence.
- Explicitly list assumptions introduced due to telemetry gaps before interview rounds.