# Codex Plugin Package Contract

Use this reference to keep package structure, manifest metadata, and integration files consistent.

## Required package root surfaces
- `.codex-plugin/plugin.json` (required)
- `README.md`
- `LICENSE`

## Optional package surfaces
- `skills/`
- `hooks/` or `hooks.json`
- `prompts/` (optional)
- `agents/` (optional)
- `scripts/`
- `assets/`
- `.mcp.json`
- `.app.json`

## Manifest metadata contract (`.codex-plugin/plugin.json`)
Required fields:
- `name`
- `version`
- `description`
- `license`
- `surfaces`

Recommended fields:
- `author`
- `homepage`
- `repository`
- `keywords`
- `interface`

## Integration files contract
- `.mcp.json`
  - Include only when MCP integration is in scope.
  - Use explicit placeholder notes if values are not finalized.
- `.app.json`
  - Include only when app integration is in scope.
  - Ensure values are clearly starter-safe when inferred.

## Hooks implementation contract
When hooks are in scope, pair this file with `references/hooks-contract.md`.

Minimum shape checks:
- Hook declaration uses supported events.
- Handler type and timeout fields are explicit.
- Unsupported/provisional behavior is labeled as provisional.

## Reporting contract
Include these keys in conversion summaries:
- `plugin_package_path`
- `manifest_validation_summary`
- `integration_file_summary`
- `hooks_validation_summary` (when hooks are in scope)
- `assumptions_and_risks`
