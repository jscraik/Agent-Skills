# Plugin JSON sample spec

```json
{
  "schema_version": 1,
  "name": "plugin-name",
  "version": "0.1.0",
  "description": "Brief plugin description",
  "author": {
    "name": "Author Name"
  },
  "license": "MIT",
  "keywords": ["plugin", "plugin-name", "incubating"],
  "governance": {
    "lifecycle_state": "incubating",
    "maturity": "experimental",
    "owner": "Author Name",
    "review_cadence": "monthly",
    "last_reviewed": "2026-03-24",
    "metadata_source": "plugin_manifest"
  },
  "skills": "./skills/",
  "mcpServers": "./.mcp.json",
  "interface": {
    "displayName": "Plugin Display Name",
    "shortDescription": "Short description for subtitle",
    "longDescription": "Incubating plugin scaffold for this package",
    "developerName": "Author Name",
    "category": "Productivity",
    "capabilities": ["Interactive", "Read"],
    "defaultPrompt": [
      "Help me evaluate whether this plugin is ready to move beyond incubating."
    ],
    "brandColor": "#3B82F6"
  }
}
```

## Field guide

### Top-level fields

- `name` (`string`): Plugin identifier (kebab-case, no spaces). Required if `plugin.json` is provided and used as manifest name and component namespace.
- `schema_version` (`integer`): Plugin manifest schema version for repo-native tooling.
- `version` (`string`): Plugin semantic version. Scaffolds start at `0.1.0`.
- `description` (`string`): Short purpose summary.
- `author` (`object`): Publisher identity.
  - `name` (`string`): Author or team name.
- `license` (`string`): License identifier (for example `MIT`, `Apache-2.0`).
- `keywords` (`array` of `string`): Search/discovery tags.
- `governance` (`object`): Lifecycle metadata for the plugin package.
  - `lifecycle_state` (`string`): Initial lifecycle state. Phase-one default: `incubating`.
  - `maturity` (`string`): Initial maturity level. Phase-one default: `experimental`.
  - `owner` (`string`): Primary maintainer or owner string.
  - `review_cadence` (`string`): Review expectation such as `monthly` or `quarterly`.
  - `last_reviewed` (`string`): ISO date for the most recent lifecycle review.
  - `metadata_source` (`string`): Use `plugin_manifest` for plugin-package authority.
- `skills` (`string`, optional): Relative path to skill directories/files when the plugin ships skills.
- `hooks` (`string`, optional): Hook config path when hooks exist.
- `mcpServers` (`string`, optional): MCP config path when MCP servers exist.
- `apps` (`string`, optional): App manifest path when app integrations exist.
- `interface` (`object`): Interface/UX metadata block for plugin presentation.

### `interface` fields

- `displayName` (`string`): User-facing title shown for the plugin.
- `shortDescription` (`string`): Brief subtitle used in compact views.
- `longDescription` (`string`): Longer description used on details screens. Starter scaffolds should stay honest about incubating status rather than pretending the plugin is production-ready.
- `developerName` (`string`): Human-readable publisher name.
- `category` (`string`): Plugin category bucket.
- `capabilities` (`array` of `string`): Capability list from implementation.
- `defaultPrompt` (`array` of `string`): Starter prompts shown in composer/UX context.
  - Include at most 3 strings. Entries after the first 3 are ignored and will not be included.
  - Each string is capped at 128 characters. Longer entries are truncated.
  - Prefer one honest incubating-stage prompt over multiple speculative marketing prompts in the scaffold.
- `brandColor` (`string`): Theme color for the plugin card.

### Path conventions and defaults

- Path values should be relative and begin with `./`.
- `skills`, `hooks`, and `mcpServers` are supplemented on top of default component discovery; they do not replace defaults.
- Custom path values must follow the plugin root convention and naming/namespacing rules.
- This repo’s scaffold writes `.codex-plugin/plugin.json`; treat that as the manifest location this skill generates.
- Do not emit broad `[TODO: ...]` placeholder blocks in the scaffold manifest. Require owner, review cadence, and description up front, then keep the rest of the starter metadata honest about incubating status.

# Marketplace JSON sample spec

`marketplace.json` depends on where the plugin should live:

- Repo plugin: `<repo-root>/.agents/plugins/marketplace.json`
- Local plugin: `~/.agents/plugins/marketplace.json`

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
- `interface` (`object`, optional): Marketplace presentation metadata.
- `plugins` (`array`): Ordered plugin entries. This order determines how Codex renders plugins.

### `interface` fields

- `displayName` (`string`, optional): User-facing marketplace title.

### Plugin entry fields

- `name` (`string`): Plugin identifier. Match the plugin folder name and `plugin.json` `name`.
- `source` (`object`): Plugin source descriptor.
  - `source` (`string`): Use `local` for this repo workflow.
  - `path` (`string`): Relative plugin path based on the marketplace root.
    - Repo plugin: `./plugins/<plugin-name>`
    - Local plugin in `~/.agents/plugins/marketplace.json`: `./.codex/plugins/<plugin-name>`
- `policy` (`object`): Marketplace policy block. Always include it.
  - `installation` (`string`): Availability policy.
    - Allowed values: `NOT_AVAILABLE`, `AVAILABLE`, `INSTALLED_BY_DEFAULT`
    - Default for new entries: `AVAILABLE`
  - `authentication` (`string`): Authentication timing policy.
    - Allowed values: `ON_INSTALL`, `ON_USE`
    - Default for new entries: `ON_INSTALL`
  - `products` (`array` of `string`, optional): Product override for this plugin entry. Omit it unless product gating is explicitly requested.
- `category` (`string`): Display category bucket. Always include it.

### Marketplace generation rules

- `displayName` belongs under the top-level `interface` object, not individual plugin entries.
- When creating a new marketplace file from scratch, seed `interface.displayName` alongside top-level `name`.
- Always include `policy.installation`, `policy.authentication`, and `category` on every generated or updated plugin entry.
- Treat `policy.products` as an override and omit it unless explicitly requested.
- Append new entries unless the user explicitly requests reordering.
- Replace an existing entry for the same plugin only when overwrite is intentional.
- Choose marketplace location to match the plugin destination:
  - Repo plugin: `<repo-root>/.agents/plugins/marketplace.json`
  - Local plugin: `~/.agents/plugins/marketplace.json`
