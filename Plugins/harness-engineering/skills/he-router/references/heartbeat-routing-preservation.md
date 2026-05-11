# Heartbeat Routing Preservation

Preserved router lines from the heartbeat routing refresh.

- Route QA or feedback-to-Linear by clarity: clear defects to `he-fix-bugs`,
  unclear behavior to `he-brainstorm`/`he-spec`, issue sequencing to `he-plan`.
- Resolve mapped roles from `~/.codex/agents/manifest.json` using canonical
  role names from `Plugins/harness-engineering/references/routing-map.json`.
- Return outputs with `selected_stage`, `matched_rule`, `confidence`,
  `rationale`, `next_invocation`, and subagent policy fields.
- If still ambiguous, return blocked with exactly one missing input.
