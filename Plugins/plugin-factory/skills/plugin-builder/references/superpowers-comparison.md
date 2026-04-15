# Superpowers Comparison

Use this note when converting [`obra/superpowers`](https://github.com/obra/superpowers) or similar multi-platform skill libraries that already ship a Codex-native install lane.

## Why this repo matters
This repo exposes conversion cases that Ars Contexta and Compound Engineering did not:

- a single repo that already supports Claude, Cursor, Codex, OpenCode, and Gemini side by side;
- Codex support documented as native skill discovery, not as a Codex plugin package;
- root-level `commands/` that are deprecated shims pointing users to skills;
- a provider-multiplexed hook implementation that emits different JSON payload shapes based on runtime detection;
- cross-platform wrapper scripts for hooks;
- agents, commands, hooks, and skills all living at repo root rather than under a nested plugin directory.

These patterns should influence how `plugin-builder` decides whether to convert, what to keep, and what to treat as migration-only glue.

## Source shape

Top-level repo surfaces include:
- `.claude-plugin/plugin.json`
- `.cursor-plugin/plugin.json`
- `.codex/INSTALL.md`
- `docs/README.codex.md`
- `.opencode/INSTALL.md`
- `gemini-extension.json`
- `agents/`
- `commands/`
- `hooks/`
- `skills/`
- `Infrastructure/tests/`

Important takeaway:
- this is not a marketplace repo with nested plugins;
- it is a single multi-platform distribution repo with provider-specific install lanes;
- Codex support already exists, but it is documented as native skill discovery through symlinks, not as `.codex-plugin/plugin.json`.

## New conversion patterns to capture

### 1. Native Codex support may already exist without a Codex plugin package
This repo ships:
- `.codex/INSTALL.md`
- `docs/README.codex.md`

Conversion rule:
- inspect whether the source already supports Codex through native skill discovery before assuming a missing `.codex-plugin/plugin.json` means "no Codex support";
- treat native-install docs as a first-class source of truth for Codex behavior;
- decide explicitly whether a Codex plugin package would replace, wrap, or merely duplicate the existing Codex lane.

### 2. Root-level multi-platform surfaces are not all plugin runtime assets
The repo mixes:
- provider manifests;
- provider install docs;
- shared `skills/`, `agents/`, `commands/`, and `hooks/`;
- test fixtures and platform adapters.

Conversion rule:
- inventory shared runtime assets from the root tree;
- keep provider install docs and adapter files as migration references unless they are still needed in the Codex package;
- do not assume every root-level file belongs in the converted plugin.

### 3. Some commands are deprecated shims, not durable prompt content
`commands/brainstorm.md` is a deprecation shim that tells the user to use the `superpowers:brainstorming` skill instead.

Conversion rule:
- inspect command contents, not just directory names;
- when a command only redirects to an existing skill, do not convert it into a fresh Codex prompt by default;
- preserve the underlying skill as the canonical surface.

### 4. Hooks may multiplex payload formats for multiple providers
`hooks/session-start` emits:
- `hookSpecificOutput.additionalContext` when `CLAUDE_PLUGIN_ROOT` is present;
- `additional_context` for other platforms.

Conversion rule:
- preserve the hook's intent, which is session-start context injection;
- do not copy provider-specific output multiplexing into Codex unchanged;
- rewrite the hook to the Codex hook contract and keep Claude/Cursor-specific branching as migration-only context.

### 5. Hook runner wrappers may be provider and OS compatibility glue
`hooks/run-hook.cmd` is a cross-platform wrapper designed around Claude Code hook invocation behavior and Windows bash detection.

Conversion rule:
- do not assume wrapper scripts belong in the Codex package;
- keep them only if the Codex runtime or target distribution path actually requires them;
- otherwise convert the real hook logic, not the provider compatibility layer.

### 6. Provider environment variables are migration clues, not Codex contracts
The hook checks `CLAUDE_PLUGIN_ROOT` to decide which payload field to emit.

Conversion rule:
- identify provider-specific env vars and path conventions during inspection;
- do not copy them into Codex manifests or hook handlers as if they were portable runtime contracts.

### 7. Existing Codex install docs can reveal discovery assumptions
`docs/README.codex.md` says Codex discovers skills from `~/.agents/skills/` at startup and installs Superpowers via a symlinked skills directory.

Conversion rule:
- capture those discovery assumptions in the conversion notes;
- distinguish "Codex skill pack" behavior from "Codex plugin package" behavior;
- if converting to a plugin package, document exactly what additional value the plugin wrapper provides beyond the existing native-skill install path.

### 8. Tests are evidence, not package payload
The repo ships tests for:
- skill triggering,
- explicit skill requests,
- subagent-driven development,
- platform integrations.

Conversion rule:
- use tests as behavioral evidence during conversion;
- do not bundle them into the Codex plugin package unless the user explicitly wants fixtures or regression assets.

## What this adds to the generic model
Compared with Ars Contexta and Compound Engineering, the generic conversion checklist should now explicitly include:

- detect whether the source already supports Codex without a Codex plugin manifest;
- separate Codex-native skill-install docs from plugin packaging requirements;
- inspect whether `commands/` are real prompts or only deprecation shims;
- inspect hook payload branching for provider-specific output fields;
- inspect wrapper scripts to determine whether they are core behavior or compatibility glue.

## Practical recommendation
For Superpowers-style repos, the safest conversion flow is:

1. Confirm whether the user wants a true Codex plugin package or just a Codex-native skill install.
2. Treat `skills/` as the main product surface and `commands/` as suspect until inspected.
3. Preserve `agents/` only when the target plugin package actually benefits from them.
4. Rewrite hooks from behavioral intent, not by copying provider-branching output fields.
5. Keep `.codex/INSTALL.md` and `docs/README.codex.md` as migration references to explain what already works today.
