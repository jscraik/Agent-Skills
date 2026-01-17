# Tauri backend integration reference

## Scope
Use when a desktop client is built with Tauri and a backend service or local Rust command layer is involved.

## Architecture choices
- Decide whether the desktop app uses local-only commands, remote APIs, or a hybrid.
- For hybrid, define which operations are local (device access, file I/O) vs remote (shared state, multi-user data).
- Document the trust boundary between the web UI and Rust command layer.

## IPC and command layer
- Keep command surfaces minimal and explicit.
- Validate all inputs in Rust before use.
- Return structured results with stable error codes for UI mapping.
- Avoid long-running work on the UI thread; use async Rust or background tasks.

## Security and permissions
- Use the Tauri permissions/allowlist system; do not enable broad APIs without explicit approval.
- Never pass secrets to the UI layer; keep sensitive operations in Rust or backend services.
- Sanitize file paths and URLs; avoid path traversal and unsafe protocols.

## Auth and data flow
- If the desktop app authenticates to a remote backend, define token storage, rotation, and refresh.
- Clearly document which side enforces authZ (backend) vs authN (desktop) and how claims are validated.
- Include error mapping rules between backend responses and UI states.

## Observability
- Define what logs are local-only vs sent to backend.
- Mask PII in client logs and crash reports.

## Testing
- Unit test Rust command validation paths.
- Contract test IPC payloads and error mappings.
- Include desktop-specific smoke tests for critical flows.
