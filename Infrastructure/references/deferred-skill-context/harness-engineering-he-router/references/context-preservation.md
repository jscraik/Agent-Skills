# Context Preservation

1. Resolve mapped roles from `~/.codex/agents/manifest.json`, preferring `he-*` roles when available in the stage map.
2. Return outputs.
3. If still ambiguous after one clarification, return blocked with missing input.
