# Apps SDK: State Management (Condensed)

## State categories
- Business data (authoritative): backend/MCP.
- UI state (ephemeral): widget instance only.
- Cross-session state (durable): backend storage.

## Widget state
- Use widget state APIs/hooks for UI state.
- Reapply UI state on new data snapshots.

## Cross-session
- Store preferences and durable data in backend.
