# RepoPrompt CLI tooling quick guide (2026-01)

Purpose: concise rp-cli usage patterns for agent workflows and automation.

## Prefer rp-cli exec mode
- Run commands as: `rp-cli -e '<command>'`
- If your harness exposes `rp_exec`, treat examples below as the `cmd` string (omit `rp-cli -e`).

## Window + tab routing (multi-window safe)
- Always list windows first: `windows`
- List compose tabs: `workspace tabs` (or `tabs`)
- Prefer opening a workspace in a new window: `workspace switch "<name>" --new-window`
- Avoid in-place switching unless explicitly safe (can clobber selection/prompt/context).
- If results look wrong, assume wrong workspace/root: run `tree` (no args) to confirm roots, then re-open the correct workspace in a new window.
- Single-window mode: open another window (or `workspace switch "<name>" --new-window`), then re-run `windows`.
- After any window open/close, re-run `windows` and re-bind in your harness if needed.

## Core commands (high-level first)
### Explore
- `tree [path] [--folders] [--mode full|selected]`
- `search <pattern> [path] [--extensions ...] [--context-lines N]`
- `read <path> [start] [limit]`
- `structure <path> ... [--scope selected]` (alias: `map`)

### Curate context
- `select set <paths...>` / `select add/remove/clear/get`
- `context` / `context --all`
- `prompt get|set|append|clear|export|presets`

### Edit
- `edit <path> <search> <replace> [--all]`
- Use `edit` for targeted replacements; avoid bulk rewrites unless necessary.

### Chat / review
- `chat <message>` (continue) / `plan <message>` / `review <message>`
- `chats` / `chats log <chat_id>`
- `models` (list presets)
- `builder [instructions] [--response-type plan|question|clarify]`

### Workspaces / tabs
- `workspace list`
- `workspace create <name> [--switch] [--new-window] [--folder-path <path>]`
- `workspace delete <name> [--close-window]`
- `workspace tab <name>`

## Output hygiene
- If output is large, redirect within the command (e.g., `tree --folders > /tmp/rp_tree.txt`) and read only what you need.
- Prefer 120–200 line reads for files.

## Minimal defaults
- Start with `tree --folders` for orientation.
- Use `search` before opening large files.
- Keep selection tight before `context`.
