# Widget runtime patterns (Apps SDK)

Last verified: 2026-01-01

## State partitioning
- Business data (authoritative): server/tool output
- UI state (ephemeral): widgetState
- Cross-session preferences: your backend (if required)

## Safe defaults
- Treat tool calls as retryable (idempotent).
- Separate read tools from write tools on the server.
- Use confirmation for destructive writes.

## Common flows
### Inline list -> details
- Render list inline.
- On item click: set widgetState.selectedId
- Optionally request fullscreen for deep inspection.

### Edit + Save
- Keep draft in widgetState.
- On Save: callTool(write_tool, payload)
- On success: refresh data and reconcile state.
