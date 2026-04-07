# Compound Engineering Comparison

Use this note when converting [`EveryInc/compound-engineering-plugin`](https://github.com/EveryInc/compound-engineering-plugin) or similar marketplace-style Claude plugin repos.

## Why this repo matters
This repo exposes conversion cases that Ars Contexta did not:

- a marketplace repo that contains multiple plugins under `plugins/`;
- provider-specific metadata beyond Claude, including `.cursor-plugin/`;
- a bundled conversion CLI and test fixtures;
- manifest-driven custom paths for commands, skills, agents, hooks, and MCP;
- inline MCP server definitions in plugin manifests;
- command semantics that have already been migrated into `skills/`.

These patterns should influence how `plugin-builder` inspects source repos before conversion.

## Source shape

Top-level repo surfaces include:
- `.claude-plugin/marketplace.json`
- `.cursor-plugin/marketplace.json`
- `.claude/commands/`
- `plugins/compound-engineering/`
- `plugins/coding-tutor/`
- `src/`
- `tests/`
- `docs/`

Important takeaway:
- the repo root is primarily a marketplace and converter implementation repo;
- the plugin payload lives under `plugins/<plugin-name>/`, not at repo root.

## New conversion patterns to capture

### 1. Marketplace repo versus plugin repo
Unlike Ars Contexta, this repository is not a single plugin package root.

Conversion rule:
- inspect the root marketplace first;
- then resolve the actual plugin package root, here `plugins/compound-engineering/`;
- do not treat root-level files like `.claude/commands/` as part of the plugin payload unless the plugin manifest explicitly points there.

### 2. Provider-specific metadata directories
This repo includes:
- `plugins/compound-engineering/.claude-plugin/plugin.json`
- `plugins/compound-engineering/.cursor-plugin/plugin.json`

Conversion rule:
- preserve provider-specific manifests as migration references only;
- do not bundle `.cursor-plugin/` into the Codex plugin package as a live runtime surface;
- do inspect them for metadata drift, counts, and alternate field conventions.

### 3. Commands may already be migrated into skills
The plugin README still documents many slash commands, but `CLAUDE.md` explicitly says commands were migrated to `skills/` in v2.39.0.

Conversion rule:
- classify by current implementation, not README labels alone;
- if the reusable workflow lives under `skills/<name>/SKILL.md`, keep it as a skill;
- only create Codex `prompts/` when the source artifact is actually prompt-like rather than a durable workflow skill.

### 4. Source commands may fan out into multiple Codex surfaces
The repo README says its Codex converter emits a prompt and skill pair for each command.

Conversion rule:
- do not assume Claude `commands/` maps to a runtime `prompts/` surface;
- map command behavior into `skills/` as the canonical runtime surface;
- when a discoverable entrypoint is needed, set `interface.defaultPrompt` on the skill-owning plugin manifest instead of emitting `prompts/`.

### 5. Custom path support in source manifests
The test fixtures demonstrate manifest fields like:
- `agents: "./custom-agents"`
- `commands: ["./custom-commands"]`
- `skills: "./custom-skills"`
- `hooks: "./custom-hooks/hooks.json"`

Conversion rule:
- inspect manifest-declared paths before assuming defaults;
- reject parent-directory escapes such as `../outside-hooks.json`;
- resolve all plugin-owned surfaces relative to the plugin root, not repo root.

### 6. Inline MCP definitions versus file-based MCP config
`plugins/compound-engineering/.claude-plugin/plugin.json` embeds `mcpServers` inline as an object, while the plugin also ships `.mcp.json`.

Conversion rule:
- detect whether MCP config is:
  - inline in the manifest,
  - file-based,
  - or both;
- when both exist, compare them and treat differences as migration-review items;
- prefer emitting a concrete `.mcp.json` in the Codex package and pointing `plugin.json` to `./.mcp.json`.

### 7. Repo implementation layer versus plugin payload
This repo ships:
- `src/commands/*.ts`
- `tests/fixtures/*`
- release and packaging files

Conversion rule:
- do not copy converter implementation or test fixtures into the target plugin package;
- use them as evidence for how the source plugin works, not as plugin runtime assets.

### 8. README counts are advisory, not authoritative
The README count table and `.cursor-plugin/plugin.json` version and counts can drift from the live tree.

Conversion rule:
- inventory the filesystem and manifests directly;
- do not trust README component counts as canonical conversion input.

## What this adds to the generic model
Compared with Ars Contexta, the generic conversion checklist should now explicitly include:

- determine whether the source is a marketplace repo or a single plugin repo;
- resolve the real plugin root before mapping surfaces;
- inspect provider-specific metadata directories such as `.cursor-plugin/`;
- inspect manifest-declared custom paths;
- detect inline MCP object definitions;
- distinguish repo-maintainer command surfaces from plugin command surfaces;
- classify command-like content semantically, not mechanically.

## Practical recommendation
For compound-engineering style repos, the safest conversion flow is:

1. Resolve root marketplace and selected plugin root.
2. Read the selected plugin manifest plus any sibling provider manifests.
3. Inventory only manifest-owned surfaces under that plugin root.
4. Compare README claims to actual tree structure, but trust the tree.
5. Normalize command-like artifacts into `skills/`, `prompts/`, or both based on current implementation semantics.
6. Convert MCP config into a stable `.mcp.json` file.
7. Preserve non-Codex provider metadata as migration references, not runtime surfaces.
