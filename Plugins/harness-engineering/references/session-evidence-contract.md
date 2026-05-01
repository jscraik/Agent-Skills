# Session Evidence Contract

Read when: prior Codex sessions, archived sessions, repeated HE failures, or learned workflow improvements affect routing.

Use the highest-confidence available source first:

1. `~/.agents/session-collector` normalized evidence.
2. `~/.codex/archived_sessions` historical recurrence.
3. `~/.codex/session_index.jsonl` and `~/.codex/history.jsonl` phrase checks.
4. `~/.codex/sessions` current runtime state.

Route by intended outcome:

- Workflow improvement from prior runs -> `he-improve`.
- Stale compound handoff, repeated gate failure, or unclear resume state -> `he-compound-refresh`.
- Waiting on PR, CI, review, Linear, deploy, or validation state -> `he-heartbeat`.
- Concrete implementation derived from evidence -> `he-work`.
- Correctness or safety validation from evidence -> `he-technical-review`.
- Reproduction, deterministic error, or root cause -> `he-fix-bugs`.

When session evidence influences a decision, cite the collector bundle, source path, index count, or exact sample. Do not claim recurrence from memory alone.
