# Claude-to-Codex Terminology Map

Use this map during conversion to avoid carrying Claude-specific naming into Codex plugins.

## Required mappings

| Claude-oriented term | Codex term | Enforcement |
| --- | --- | --- |
| `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json` | Must emit Codex manifest. Validator fails if Codex manifest is missing. |
| `commands` manifest key | `skills` surface plus optional `interface.defaultPrompt` | Validator fails on legacy command keys in `plugin.json`. |
| `slash commands` | `skills` | Reword docs/evals to skill terminology. |
| `prompts/` | `skills/` plus optional `interface.defaultPrompt` | Treat legacy prompt packs as migration input, not a runtime package surface. |

## Compatible terms (no rename needed)

| Shared term | Notes |
| --- | --- |
| `skills/` | Keep as plugin-owned skills. |
| `hooks` | Keep name, but enforce Codex hook event model (`SessionStart`, `Stop`). |
| `agents/` | Optional in Codex plugin packages. |
| `.mcp.json` / MCP | Keep name and ensure manifest path points to `./.mcp.json` when used for real MCP wiring. Do not use it for recommendation-only MCP lists. |
| `.app.json` / apps | Keep name and ensure manifest path points to `./.app.json` when used for real app integrations. |

## Semantic mapping guidance

- If a source "command" is now implemented as a reusable workflow file under `skills/<name>/SKILL.md`, keep it as a skill.
- If a source command is a lightweight invocation surface with little reusable process knowledge, fold the user-facing entry text into a `skills/<name>/SKILL.md` and optionally mirror a short starter phrase in `interface.defaultPrompt`.
- If the target Codex experience benefits from both discoverability and reusable workflow instructions, keep the workflow in `skills/` and use `interface.defaultPrompt` only as a lightweight entry hint.
- Convert `commands/`, `slash-commands/`, and `prompts/` into `skills/` during migration rather than preserving those directories as runtime surfaces.
- Do not classify only from README labels; inspect the live tree and manifests.
- Treat `assets/` as optional package storage. Only add manifest image fields after the referenced files exist.

## Source anchors used for this mapping
- Codex prompt discovery: `codex-rs/core/src/custom_prompts.rs` (`$CODEX_HOME/prompts`).
- Codex hooks config model: `codex-rs/hooks/src/engine/config.rs`.
- OpenAI plugin creator skill and marketplace schema:
  - `openai/plugins/.agents/skills/plugin-creator/SKILL.md`
  - `openai/plugins/.agents/plugins/marketplace.json`
- Claude plugin package layout and manifest surface:
  - `anthropics/claude-plugins-official/plugins/skill-creator/.claude-plugin/plugin.json`
