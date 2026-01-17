# Rust command layer reference (Tauri and desktop IPC)

## Purpose
Use this reference when defining or reviewing Rust command handlers for UI-driven actions.

## Command design
- Keep command boundaries small and explicit.
- Use `Result<T, E>` and map errors into structured responses.
- Use typed inputs (serde structs) instead of untyped JSON maps.

## Validation and safety
- Validate all user inputs (lengths, formats, enums, file paths).
- Reject unknown fields if the repo uses strict deserialization.
- Never trust UI-provided paths or URLs; validate and normalize.
- Keep secrets on the Rust side; do not pass secrets to UI state.

## Concurrency and blocking
- Avoid blocking the async runtime; use async I/O where possible.
- For CPU-heavy or blocking tasks, offload to a blocking thread pool.
- Provide progress updates if the task is long-running (status events or polling).

## Error handling
- Use consistent error codes/messages for the UI layer.
- Include actionable user-facing messages and developer-facing details separately when possible.

## Testing guidance
- Unit test command handlers (input validation + error paths).
- Mock OS/file operations when feasible.
- Ensure UI error states are covered for failure cases.
