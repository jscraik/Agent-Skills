# Context Preservation

- Preserved step 1: Resolve mapped roles from `~/.codex/agents/manifest.json`, preferring `he-*` roles when available in the stage map.
- Preserved step 2: Return outputs with `selected_stage`, `matched_rule`, `confidence`, `rationale`, `recommended_next_step`, and `missing_input` only when blocked.
- Preserved step 3: If still ambiguous after applying the routing table, return `blocked` with exactly one `missing_input`.
