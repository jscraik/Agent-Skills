# Claude-to-Codex Terminology Map

Use this map during conversion to avoid carrying Claude-specific naming into Codex plugins.

## Required mappings

| Claude-oriented term | Codex term | Enforcement |
| --- | --- | --- |
| `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json` | Must emit Codex manifest. Validator fails if Codex manifest is missing. |
| `commands/` | `prompts/` | Must map command content to prompt files for Codex custom prompts. |
| `slash commands` | `prompts` | Reword docs/evals to Codex terminology. |
| `commands` manifest key | `prompts` surface + `interface.defaultPrompt` | Validator fails on legacy command keys in `plugin.json`. |

## Compatible terms (no rename needed)

| Shared term | Notes |
| --- | --- |
| `skills/` | Keep as plugin-owned skills. |
| `hooks` | Keep name, but enforce Codex hook event model (`SessionStart`, `Stop`). |
| `agents/` | Optional in Codex plugin packages. |
| `.mcp.json` / MCP | Keep name and ensure manifest path points to `./.mcp.json` when used. |
| `.app.json` / apps | Keep name and ensure manifest path points to `./.app.json` when used. |

## Source anchors used for this mapping
- Codex prompt discovery: `codex-rs/core/src/custom_prompts.rs` (`$CODEX_HOME/prompts`).
- Codex hooks config model: `codex-rs/hooks/src/engine/config.rs`.
- OpenAI plugin creator skill and marketplace schema:
  - `openai/plugins/.agents/skills/plugin-creator/SKILL.md`
  - `openai/plugins/.agents/plugins/marketplace.json`
- Claude plugin package layout and manifest surface:
  - `anthropics/claude-plugins-official/plugins/skill-creator/.claude-plugin/plugin.json`

