# Codex Plugin Package Contract

Use this contract to keep plugin scaffolds and conversions aligned with the enforced JSON specs.

## Required package root surfaces
- `.codex-plugin/plugin.json` (required)
- `README.md` (required)
- `LICENSE` (required)

## Required support surfaces
- `references/operational-spec.md` (required)
- `references/deconflict-report.md` (recommended when overlap review finds an exact or similar sibling plugin)

`references/operational-spec.md` must provide:
- a transition table as the source of truth;
- explicit failure states for validation, blocked, policy, timeout, system, and plugin failures;
- a Mermaid diagram derived strictly from the transition table;
- plugin contract metadata, plugin registry, capability map, idempotency, invariants, dry-run simulation, transition tracing, and log fields.

## Deconflict review
- Before creating a new plugin package, compare it against the existing local plugin directory.
- Prefer merge, fold, or improvement work when an existing package already serves the same job.
- Treat unexplained duplicate-intent packages as a packaging smell even when the manifest is otherwise valid.

## Optional package surfaces
- `skills/`
- `hooks/` or `hooks.json`
- `prompts/` (optional)
- `agents/` (optional)
- `scripts/`
- `assets/`
- `.mcp.json`
- `.app.json`

## Plugin JSON sample spec

```json
{
  "name": "plugin-name",
  "version": "1.2.0",
  "description": "Brief plugin description",
  "author": {
    "name": "Author Name",
    "email": "author@example.com",
    "url": "https://github.com/author"
  },
  "homepage": "https://docs.example.com/plugin",
  "repository": "https://github.com/author/plugin",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],
  "skills": "./skills/",
  "hooks": "./hooks.json",
  "mcpServers": "./.mcp.json",
  "apps": "./.app.json",
  "interface": {
    "displayName": "Plugin Display Name",
    "shortDescription": "Short description for subtitle",
    "longDescription": "Long description for details page",
    "developerName": "OpenAI",
    "category": "Productivity",
    "capabilities": ["Interactive", "Write"],
    "websiteURL": "https://openai.com/",
    "privacyPolicyURL": "https://openai.com/policies/row-privacy-policy/",
    "termsOfServiceURL": "https://openai.com/policies/row-terms-of-use/",
    "defaultPrompt": "Starter prompt for trying a plugin",
    "brandColor": "#3B82F6",
    "composerIcon": "./assets/icon.png",
    "logo": "./assets/logo.png",
    "screenshots": [
      "./assets/screenshot1.png",
      "./assets/screenshot2.png",
      "./assets/screenshot3.png"
    ]
  }
}
```

## Plugin field guide

### Top-level fields
- `name` (`string`): Plugin identifier (kebab-case, no spaces). Required if `plugin.json` is provided and used as manifest name and component namespace.
- `version` (`string`): Plugin semantic version.
- `description` (`string`): Short purpose summary.
- `author` (`object`): Publisher identity.
  - `name` (`string`): Author or team name.
  - `email` (`string`): Contact email.
  - `url` (`string`): Author or team homepage or profile URL.
- `homepage` (`string`): Documentation URL for plugin usage.
- `repository` (`string`): Source code URL.
- `license` (`string`): License identifier (for example `MIT`, `Apache-2.0`).
- `keywords` (`array[string]`): Search and discovery tags.
- `skills` (`string`): Relative path to skill directories or files.
- `hooks` (`string`): Hook config path.
- `mcpServers` (`string`): MCP config path.
- `apps` (`string`): App manifest path for plugin integrations.
- `interface` (`object`): Interface and UX metadata block for plugin presentation.

### `interface` fields
- `displayName` (`string`): User-facing title shown for the plugin.
- `shortDescription` (`string`): Brief subtitle used in compact views.
- `longDescription` (`string`): Longer description used on details screens.
- `developerName` (`string`): Human-readable publisher name.
- `category` (`string`): Plugin category bucket.
- `capabilities` (`array[string]`): Capability list from implementation.
- `websiteURL` (`string`): Public website for the plugin.
- `privacyPolicyURL` (`string`): Privacy policy URL.
- `termsOfServiceURL` (`string`): Terms of service URL.
- `defaultPrompt` (`string`): Starter prompt shown in composer context.
- `brandColor` (`string`): Theme color for the plugin card.
- `composerIcon` (`string`): Path to icon asset.
- `logo` (`string`): Path to logo asset.
- `screenshots` (`array[string]`): Screenshot asset paths.
  - Screenshot entries must be PNG filenames under `./assets/`.
  - File paths must remain relative to plugin root.

### Path conventions and defaults
- Path values should be relative and begin with `./`.
- `skills`, `hooks`, and `mcpServers` are supplemented on top of default component discovery; they do not replace defaults.
- Custom path values must follow plugin root convention and naming rules.
- This scaffold writes `.codex-plugin/plugin.json` and treats it as the canonical manifest location.

## Marketplace JSON sample spec

`marketplace.json` lives at `<repo-root>/.agents/plugins/marketplace.json`.

```json
{
  "name": "openai-curated",
  "plugins": [
    {
      "name": "linear",
      "source": {
        "source": "local",
        "path": "./plugins/linear"
      },
      "installPolicy": "AVAILABLE",
      "authPolicy": "ON_INSTALL",
      "category": "Productivity"
    }
  ]
}
```

## Marketplace field guide

### Top-level fields
- `name` (`string`): Marketplace identifier or catalog name.
- `plugins` (`array`): Ordered plugin entries. The order controls render order.

### Plugin entry fields
- `name` (`string`): Plugin identifier. Must match folder name and `plugin.json` `name`.
- `source` (`object`): Plugin source descriptor.
  - `source` (`string`): Use `local` for this workflow.
  - `path` (`string`): Relative plugin path, always `./plugins/<plugin-name>`.
- `installPolicy` (`string`): Availability policy.
  - Allowed values: `NOT_AVAILABLE`, `AVAILABLE`, `INSTALLED_BY_DEFAULT`
  - Default for new entries: `AVAILABLE`
- `authPolicy` (`string`): Authentication timing policy.
  - Allowed values: `ON_INSTALL`, `ON_USE`
  - Default for new entries: `ON_INSTALL`
- `category` (`string`): Display category bucket.

### Marketplace generation rules
- Always include `installPolicy`, `authPolicy`, and `category` on each generated or updated plugin entry.
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
- a plugin that declares custom paths for `commands`, `skills`, `agents`, `hooks`, or `mcpServers`;
- a plugin that embeds `mcpServers` inline instead of using only `./.mcp.json`.

Use `scaffold --from-source-path ...` when you want the scaffold to auto-create likely Codex surfaces from the inspected source plugin root.
The scaffold also emits `references/operational-spec.md` for every plugin package it creates.
When overlap review is relevant, the scaffold also emits `references/deconflict-report.md`.

## Claude-to-Codex conversion requirement

When the source plugin is Claude-oriented, apply `references/terminology-map.md` during conversion.

Minimum enforced mapping:
- `.claude-plugin/plugin.json` -> `.codex-plugin/plugin.json`
- `commands/` and slash-command terminology -> `prompts/`
