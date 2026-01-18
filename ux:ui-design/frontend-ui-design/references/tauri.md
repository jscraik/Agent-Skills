# Tauri desktop UI reference (design + security)

## Scope
Use this reference when the target surface includes Tauri desktop apps.

## Core concepts
- Tauri is a desktop shell with a web UI and a Rust backend.
- UI runs in a webview; OS access is provided via Rust commands and Tauri APIs.
- Keep UI/JS untrusted; enforce validation and permissions on the Rust side.

## IPC and command model
- Prefer small, explicit commands (one task per command).
- Validate all inputs; treat them as untrusted.
- Use structured results and errors (typed payloads; avoid stringly-typed errors).
- Avoid long-running work in the UI thread; delegate to Rust and stream progress when needed.

## Security baseline
- Use the project's permission/allowlist system (do not enable broad APIs without explicit approval).
- Avoid exposing filesystem/network access to the UI directly; keep sensitive operations in Rust.
- Sanitize file paths; never accept raw paths without validation or sandboxing rules.
- Use CSP and avoid inline scripts/styles for the web UI.

## UX expectations
- Provide keyboard shortcuts, menus, and platform-appropriate window behavior.
- Respect window resizing and high-DPI scaling.
- Prefer native file dialogs when interacting with the filesystem.

## Build/run patterns (follow repo conventions)
- Web UI: `pnpm dev` or equivalent.
- Desktop: `tauri dev` or `pnpm tauri dev` when configured.

## Output requirements
- When Tauri is in scope, include:
  - Web UI snippet (React or framework used in repo)
  - Rust command or IPC stub example
  - Security notes (permissions/allowlist and validation)
  - Desktop UX notes (menus, shortcuts, window behavior)
