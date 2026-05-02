# Context Preservation

1. Resolve mapped roles from `~/.codex/agents/manifest.json`, preferring `he-*` roles when available in the stage map.
1. Resolve mapped roles from `~/.codex/agents/manifest.json`, preferring `he-*` roles when available in the stage map.
2. Return outputs with `selected_stage`, `matched_rule`, `confidence`, `rationale`, `next_invocation`, and subagent policy fields.
3. If still ambiguous after applying the routing table, return `blocked` with exactly one `missing_input`.
