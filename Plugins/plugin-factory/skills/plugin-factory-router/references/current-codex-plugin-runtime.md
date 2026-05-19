# Current Codex Plugin Runtime Route Notes

Use these notes only to choose the correct plugin-factory lane. Do not perform
builder, installer, or runtime validation work from the router.

## Route Cues

- Manifest shape, plugin-relative paths, bundled hooks, duplicate MCP server
  names, and package compatibility concerns route to `plugin-builder`.
- Runtime visibility, projection, startup sync, cache extraction, or whether a
  plugin is available to Codex routes to `plugin-installer`.
- First-draft package shell creation routes to `plugin-creator`.
- Broad requests that mix authoring, install, runtime startup, marketplace, and
  external provider readiness need one follow-up question or a staged handoff.

## Current Runtime Boundaries

Current Codex plugin packages can expose skills, MCP servers, apps, and hooks.
Manifest paths must be plugin-root relative `./...` paths that do not escape the
plugin root. Bundled MCP may come from `.mcp.json`; bundled hooks may come from
manifest hook paths, inline hook objects, or default `hooks/hooks.json`.

Discovery or install evidence does not prove all runtime surfaces are healthy.
Keep route selection honest by naming which surface needs proof.
