# Heartbeat Routing Preservation

The heartbeat routing refresh inserted a recurring-loop route before the QA and
fallback tail of the deterministic router. These prior compact-router lines are
preserved here for progressive-disclosure auditability.

- Preserved step 5: Route QA session, conversational bug-report, or feedback-to-Linear requests by expected-behavior clarity: clear single/multiple defects to `he-fix-bugs`, unclear expected behavior to `he-brainstorm` or `he-spec`, issue-set sequencing to `he-plan`.
- Preserved step 6: Resolve mapped roles from `~/.codex/agents/manifest.json`, preferring `he-*` roles when available in the stage map.
- Preserved step 7: Return outputs with `selected_stage`, `matched_rule`, `confidence`, `rationale`, `recommended_next_step`, and `missing_input` only when blocked.
- Preserved step 8: If still ambiguous after applying the table, return blocked with exactly one missing input instead of guessing.
description: Route ambiguous Harness Engineering requests to one lifecycle stage when users ask where to start, resume, plan, implement, review, debug, or resolve domain terminology.
