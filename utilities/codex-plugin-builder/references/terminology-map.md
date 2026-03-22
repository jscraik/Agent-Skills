# Claude-to-Codex Terminology Map

Use this map during conversion to avoid carrying Claude-specific naming into Codex plugins.

## Required mappings

| Claude-oriented term | Codex term | Enforcement |
| --- | --- | --- |
| `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json` | Must emit Codex manifest. Validator fails if Codex manifest is missing. |
| `commands` manifest key | `prompts` surface and or `skills` surface plus `interface.defaultPrompt` | Validator fails on legacy command keys in `plugin.json`. |
| `slash commands` | `prompts` | Reword docs/evals to Codex terminology. |

## Compatible terms (no rename needed)

| Shared term | Notes |
| --- | --- |
| `skills/` | Keep as plugin-owned skills. |
| `commands/` | Allowed as an optional curated plugin surface. Reclassify only when converting a Claude-only command pack into Codex prompts or skills. |
| `hooks` | Keep name, but enforce Codex hook event model (`SessionStart`, `Stop`). |
| `agents/` | Optional in Codex plugin packages. |
| `.mcp.json` / MCP | Keep name and ensure manifest path points to `./.mcp.json` when used. |
| `.app.json` / apps | Keep name and ensure manifest path points to `./.app.json` when used. |

## Semantic mapping guidance

- If a source "command" is now implemented as a reusable workflow file under `skills/<name>/SKILL.md`, keep it as a skill.
- If a source command is a lightweight invocation surface with little reusable process knowledge, map it to `prompts/`.
- If the target Codex experience benefits from both discoverability and reusable workflow instructions, one source command may fan out into both a prompt and a skill.
- If a curated Codex plugin already ships a first-class `commands/` directory, do not rewrite it away just to satisfy a Claude-to-Codex migration heuristic.
- Do not classify only from README labels; inspect the live tree and manifests.

## Source anchors used for this mapping
- Codex prompt discovery: `codex-rs/core/src/custom_prompts.rs` (`$CODEX_HOME/prompts`).
- Codex hooks config model: `codex-rs/hooks/src/engine/config.rs`.
- OpenAI plugin creator skill and marketplace schema:
  - `openai/plugins/.agents/skills/plugin-creator/SKILL.md`
  - `openai/plugins/.agents/plugins/marketplace.json`
- Claude plugin package layout and manifest surface:
  - `anthropics/claude-plugins-official/plugins/skill-creator/.claude-plugin/plugin.json`
