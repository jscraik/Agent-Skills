# Current Codex Plugin Runtime Contract

This reference captures Codex plugin facts from the current `~/dev/codex`
runtime. Use it to harden plugin packages without confusing package validity
with runtime availability.

## Source Anchors

- Plugin manifest parsing:
  `/Users/jamiecraik/dev/codex/codex-rs/core-plugins/src/manifest.rs`
- Plugin loading and extraction:
  `/Users/jamiecraik/dev/codex/codex-rs/core-plugins/src/loader.rs`
- Startup sync and cache behavior:
  `/Users/jamiecraik/dev/codex/codex-rs/core-plugins/src/startup_sync.rs`
- MCP tool discovery:
  `/Users/jamiecraik/dev/codex/codex-rs/tools/src/tool_discovery.rs`
- MCP tool execution:
  `/Users/jamiecraik/dev/codex/codex-rs/tools/src/mcp_tool.rs`

## Manifest Paths

Manifest path fields such as `skills`, `mcpServers`, `apps`, and `hooks` are
plugin-root relative. Current Codex requires explicit `./...` relative paths,
rejects `..`, and rejects paths that escape the plugin root after
canonicalization.

~~~json
{
  "version": "1.0.0",
  "name": "example-plugin",
  "displayName": "Example Plugin",
  "description": "Example plugin package.",
  "skills": "./skills",
  "hooks": "./hooks/hooks.json",
  "mcpServers": "./.mcp.json",
  "apps": "./.app.json"
}
~~~

Default locations are still important when manifest fields are omitted:
`skills/`, `hooks/hooks.json`, `.mcp.json`, and `.app.json`.

## MCP Server Shape

Plugin MCP can be declared through `.mcp.json` as either:

~~~json
{
  "mcpServers": {
    "docs": {
      "command": "/absolute/path/to/server",
      "args": ["--stdio"],
      "env": {
        "EXAMPLE_MODE": "plugin"
      },
      "startup_timeout_sec": 20
    }
  }
}
~~~

or as a direct server map:

~~~json
{
  "docs": {
    "command": "/absolute/path/to/server",
    "args": ["--stdio"],
    "startup_timeout_sec": 20
  }
}
~~~

The runtime normalizes these entries into the current MCP server config. A
duplicate server name is skipped with a warning, so plugin validation should
surface name collisions explicitly.

## Hooks

Plugin-bundled hooks can be supplied as manifest hook paths, inline manifest
hook objects, or the default `hooks/hooks.json`. Command hooks should use
`PLUGIN_ROOT` and `PLUGIN_DATA` for plugin-owned files. Legacy plugin path
environment names may still be present, but new guidance should prefer the
current names.

~~~json
{
  "SessionStart": [
    {
      "type": "command",
      "command": "${PLUGIN_ROOT}/hooks/session-start.sh"
    }
  ]
}
~~~

## Proof Boundary

Plugin source validation proves the package is internally coherent. It does not
prove runtime projection, startup sync, MCP server health, hook execution, app
registration, or external provider availability. Treat those as separate gates
with their own evidence.
