# Plugin Contract

This package follows Codex plugin packaging requirements for first-pass conversion.

Required surfaces present:
- `.codex-plugin/plugin.json`
- `README.md`
- `LICENSE`

Required manifest metadata in `.codex-plugin/plugin.json`:
- `name`
- `version`
- `description`
- `license`
- `surfaces`

Optional integration metadata included in this pass:
- `.app.json`
- `.mcp.json`

Deferred surfaces:
- `hooks/`
- `agents/`
