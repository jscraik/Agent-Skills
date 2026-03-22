# Codex Plugin Package Contract

Use this contract to keep plugin scaffolds and conversions aligned with:
- the current `openai/codex` runtime manifest loader;
- the curated `openai/plugins` repository layout and examples;
- the pinned upstream `plugin-creator` skill in `openai/plugins`.

## Runtime-required package surface
- `.codex-plugin/plugin.json` is the only package file the current Codex runtime requires.
- `plugin.json` should include a non-empty kebab-case `name`.
- `skills`, `mcpServers`, and `apps` path values must start with `./` and stay within the plugin root.
- `interface.defaultPrompt` currently validates as:
  - a single string, or
  - a list of strings,
  - with at most 3 entries and 128 characters per entry.

## Curated and repo-level conventions

These are valid and common, but they are not part of the minimal runtime contract:
- `README.md`
- `LICENSE`
- `references/operational-spec.md`
- `references/deconflict-report.md`
- `hooks.json`
- `commands/`
- `agents/`
- `assets/`
- `.mcp.json`
- `.app.json`

This builder still scaffolds several of those files by default because they are useful for local packaging and they appear in curated `openai/plugins` examples, but the validator should not reject a plugin solely because those helper files are absent.

## Source reconciliation notes
- The local draft spec in `codex_plugins_spec.md` describes `interface.defaultPrompt` as a string or a list of `{title, prompt}` objects.
- The current `openai/codex` source accepts a string or a list of strings, so this builder validates the runtime-compatible form.
- The local draft spec also describes `mcpServers` as a directory path, while curated upstream plugins and current builder defaults commonly use `./.mcp.json`.
- When sources disagree, prefer current runtime behavior first, then curated `openai/plugins` examples.

## Deconflict review
- Before creating a new plugin package, compare it against the existing local plugin directory.
- Prefer merge, fold, or improvement work when an existing package already serves the same job.
- Treat unexplained duplicate-intent packages as a packaging smell even when the manifest is otherwise valid.

## Runtime manifest example

```json
{
  "name": "plugin-name",
  "description": "Brief plugin description",
  "skills": "./skills/",
  "mcpServers": "./.mcp.json",
  "apps": "./.app.json",
  "interface": {
    "displayName": "Plugin Display Name",
    "shortDescription": "One-line summary",
    "longDescription": "Longer plugin description",
    "developerName": "OpenAI",
    "category": "Design",
    "capabilities": ["Interactive", "Read", "Write"],
    "websiteURL": "https://example.com",
    "privacyPolicyURL": "https://example.com/privacy",
    "termsOfServiceURL": "https://example.com/terms",
    "defaultPrompt": "Inspect a design and implement it in code.",
    "brandColor": "#0D99FF",
    "composerIcon": "./assets/icon.png",
    "logo": "./assets/logo.png",
    "screenshots": []
  }
}
```

## Curated manifest example

The curated `openai/plugins` repo commonly adds richer metadata on top of the runtime shape:

```json
{
  "name": "plugin-name",
  "version": "0.1.0",
  "description": "Brief plugin description",
  "author": {
    "name": "Author Name",
    "email": "author@example.com",
    "url": "https://example.com"
  },
  "homepage": "https://docs.example.com/plugin",
  "repository": "https://github.com/org/repo",
  "license": "MIT",
  "keywords": ["plugin", "example"],
  "skills": "./skills/",
  "hooks": "./hooks.json",
  "mcpServers": "./.mcp.json",
  "apps": "./.app.json",
  "interface": {
    "displayName": "Plugin Display Name",
    "defaultPrompt": "Try this plugin"
  }
}
```

## Manifest field guide

### Top-level fields
- `name` (`string`): required by this builder. Use kebab-case and keep it aligned with the folder name.
- `description` (`string`): optional runtime summary.
- `skills` (`string`): optional relative path to plugin skills.
- `mcpServers` (`string`): optional relative path. Current curated examples use `./.mcp.json`.
- `apps` (`string`): optional relative path. Current curated examples use `./.app.json`.
- `interface` (`object`): optional UI metadata block.
- `hooks` (`string`): optional curated metadata path. Curated examples use `./hooks.json`.
- `version`, `author`, `homepage`, `repository`, `license`, `keywords`: optional curated metadata fields. They are common in `openai/plugins` but are not required by the current runtime manifest loader.

### `interface` fields
- All `interface` fields are optional.
- `capabilities` must be an array of strings when present.
- `screenshots` must be an array of relative plugin paths when present.
- `composerIcon` and `logo` must be relative plugin paths when present.
- `defaultPrompt` should follow the runtime-compatible shape documented above.

### Path conventions and defaults
- Path values should be relative and begin with `./`.
- Declared manifest paths must stay inside the plugin root.
- If a manifest declares `skills`, `hooks`, `mcpServers`, or `apps`, the referenced path should exist.
- Current curated examples and this builder both prefer:
  - `./skills/`
  - `./hooks.json`
  - `./.mcp.json`
  - `./.app.json`

## Marketplace JSON example

`marketplace.json` lives at `<repo-root>/.agents/plugins/marketplace.json`.

```json
{
  "name": "openai-curated",
  "interface": {
    "displayName": "ChatGPT Official"
  },
  "plugins": [
    {
      "name": "linear",
      "source": {
        "source": "local",
        "path": "./plugins/linear"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
```

## Marketplace field guide

### Top-level fields
- `name` (`string`): marketplace identifier or catalog name.
- `interface.displayName` (`string`): user-facing marketplace title.
- `plugins` (`array`): ordered plugin entries. Order controls render order.

### Plugin entry fields
- `name` (`string`): plugin identifier. Keep it aligned with the folder name and manifest `name`.
- `source.source` (`string`): use `local`.
- `source.path` (`string`): always `./plugins/<plugin-name>`.
- `policy.installation` (`string`): one of `NOT_AVAILABLE`, `AVAILABLE`, `INSTALLED_BY_DEFAULT`.
- `policy.authentication` (`string`): one of `ON_INSTALL`, `ON_USE`.
- `category` (`string`): recommended and emitted by this builder, but accepted as optional for compatibility with existing curated entries that omit it.
- `policy.products` (`array`): optional override. Only add it when the user explicitly asks for product gating.

### Marketplace generation rules
- Always include marketplace `interface.displayName`.
- Scaffolds should emit `policy.installation`, `policy.authentication`, and `category` on each generated or updated plugin entry.
- Validators should accept legacy flat `installPolicy` and `authPolicy` during migration.
- Append new entries unless the user explicitly requests reordering.
- Replace an existing entry for the same plugin only when overwrite is intentional.

## Enforced script commands

```bash
python3 utilities/codex-plugin-builder/scripts/plugin_builder.py inspect-source <path/to/source-repo-or-plugin>
python3 utilities/codex-plugin-builder/scripts/plugin_builder.py inspect-local <plugin-name> --path plugins
python3 utilities/codex-plugin-builder/scripts/plugin_builder.py scaffold <plugin-name> --path plugins --with-marketplace
python3 utilities/codex-plugin-builder/scripts/plugin_builder.py scaffold <plugin-name> --path plugins --from-source-path <path/to/source-repo-or-plugin> --with-marketplace
python3 utilities/codex-plugin-builder/scripts/plugin_builder.py validate <path/to/plugin> --require-marketplace --marketplace-path .agents/plugins/marketplace.json
python3 utilities/codex-plugin-builder/scripts/plugin_builder.py validate <path/to/plugin> --show-terminology-map
```

## Source inspection support

Use `inspect-source` before conversion when the input may be:
- a marketplace repo with nested plugins;
- a provider-converter repo with multiple manifest formats;
- a plugin that declares custom paths for `commands`, `skills`, `agents`, `hooks`, `mcpServers`, or `apps`;
- a plugin that embeds `mcpServers` inline instead of using only `./.mcp.json`.

Use `scaffold --from-source-path ...` when you want the scaffold to auto-create likely Codex surfaces from the inspected source plugin root.
The scaffold also emits `references/operational-spec.md` for locally created packages.
When overlap review is relevant, the scaffold also emits `references/deconflict-report.md`.

## Claude-to-Codex conversion requirement

When the source plugin is Claude-oriented, apply `references/terminology-map.md` during conversion.

Minimum enforced mapping:
- `.claude-plugin/plugin.json` -> `.codex-plugin/plugin.json`
- legacy manifest command keys -> `prompts/`, `skills/`, and or `interface.defaultPrompt`
