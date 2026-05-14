# Session Evidence Contract

Read when: prior Codex sessions, archived sessions, repeated HE failures, or learned workflow improvements affect routing.

Use the highest-confidence available source first:

1. `~/.agents/session-collector` normalized evidence.
2. `~/.codex/archived_sessions` historical recurrence.
3. `~/.codex/session_index.jsonl` and `~/.codex/history.jsonl` phrase checks.
4. `~/.codex/sessions` current runtime state.

When `~/.agents/session-collector` is available, prefer normalized inventory and
targeted extraction over raw transcript scanning. The minimum useful inventory
row includes `platform`, `file`, `size`, `ts`, `session`, `cwd`, `branch`,
`last_ts`, `match_count`, `keyword_matches`, and `_meta.parse_errors` when
parsing was lossy. Use narrow extraction modes such as `skeleton`, `errors`, or
`he-signals`; avoid broad summarization unless a source artifact or user request
requires it. Detailed extraction rules: [session evidence extraction](session-evidence-extraction.md).

Interpret collector output conservatively:

- Confirm every `selected_he_stage` against `stage_invocation_templates` in [routing map](routing-map.json) before treating it as a stage. Unknown `he-*` tokens remain `unmapped_signal` evidence until a route is added intentionally.
- Treat broad blocker labels such as `approval_required`, `network`, `missing_file`, `permission`, and `timeout` as context until corroborated by the same command family, repo/plugin family, validation gate, or exact artifact path.
- Prefer grouped evidence with session count, candidate count, validation gates, and sanitized labels over raw frequency totals.
- When many rows share the same broad blocker set, classify the improvement as evidence-classifier hygiene unless exact samples prove a product workflow issue.

Route by intended outcome:

- Workflow improvement from prior runs -> `he-improve`.
- Coverage-gap, workflow-capture, or skillify candidate from collector evidence -> `he-improve` first, then [session evidence skillify triage](session-evidence-skillify-triage.md); only invoke `skill-factory:skillify` after triage returns `skillify-new-skill`.
- Stale lifecycle handoff, repeated gate failure, or unclear resume state -> `he-reconcile`.
- Solved repeated failure or stale learning document -> `he-reinforce`.
- Waiting on PR, CI, review, Linear, deploy, or validation state -> `he-heartbeat`.
- Concrete implementation derived from evidence -> `he-work`.
- Correctness or safety validation from evidence -> `he-technical-review`.
- Reproduction, deterministic error, or root cause -> `he-fix-bugs`.

Treat noncanonical `he-*` text found in collector output as evidence labels until confirmed in the HE routing map. Do not create skills from path fragments, bundle names, or broad blocker words.

When session evidence influences a decision, cite the collector bundle, source path, index count, or exact sample. Do not claim recurrence from memory alone.
