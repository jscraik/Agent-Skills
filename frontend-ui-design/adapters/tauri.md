# Adapter: Tauri desktop (web UI + Rust command layer)

## A) Surface constraints
- Treat Tauri as a desktop app with a web UI shell.
- Respect platform conventions (menus, shortcuts, window behavior).
- Avoid long-running work in the UI thread; move OS work to Rust commands.

## B) Project structure
- Web UI lives in the frontend (Vite/React/etc per repo).
- Rust backend lives in `src-tauri/`.
- Config is usually `tauri.conf.json` or `tauri.conf.toml` (use repo convention).

## C) IPC and security
- Expose the minimum command surface; validate all inputs.
- Do not pass secrets to the frontend; keep sensitive work in Rust.
- Follow the repo's permissions/allowlist setup; do not enable broad APIs without explicit request.

## D) UX requirements
- Provide keyboard shortcuts and menu items for primary actions.
- Support resize and high-DPI scaling.
- Use native file dialogs when needed (Tauri APIs).

## E) Build/run hints
- Follow repo scripts. Common patterns: `pnpm dev` for web UI and `tauri dev` or `pnpm tauri dev` for desktop.
