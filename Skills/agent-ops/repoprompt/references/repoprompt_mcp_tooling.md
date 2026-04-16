# RepoPrompt MCP tooling quick guide (2026-01)

Purpose: concise map of RepoPrompt MCP tools and safe usage patterns for agent workflows.

## Use MCP tools first
- Prefer RepoPrompt MCP tools for discovery, reading, and edits.
- Exception: when reading a Skill file (`*/SKILL.md`), use the native file read tool.

## Core tool set (names are the levers)
- `get_file_tree` (files/folders views)
- `get_code_structure`
- `file_search`
- `read_file`
- `manage_selection` (set/add/remove/preview/promote/demote)
- `apply_edits`, `file_actions`
- `update_plan`
- `workspace_context`, `prompt`
- `context_builder` (explicit user request; token-costly)
- `chat_send`, `chats`, `list_models`
- `manage_workspaces` (list/switch/create/delete/list_tabs/select_tab; supports open/new-window + close-window options)
- If available in your MCP build: `list_windows`, `select_window`

## Flows & hotwords
- **[DISCOVER]** `workspace_context` → `get_file_tree` → `get_code_structure` → `file_search` → `read_file` → `manage_selection op="set"` → `prompt op="set"`
- **[AGENT]** small edits via `apply_edits`/`file_actions`, then re-check selection/context.
- **[PAIR]** discuss plan (`chat_send mode=plan`), then implement iteratively.
- **[SECOND OPINION]** ask for a plan review via `chat_send mode=plan`.

## Notes
- Keep selection under ~80k tokens when possible.
- Prefer directory-first exploration (`get_code_structure` on a folder) before opening large files.
- Use `context_builder` only when you explicitly need the automated discovery pass.
