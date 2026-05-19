# Codex And Session Evidence For he-spec

Read when: a spec is based on prior work, Codex sessions, local telemetry, or live Codex collaboration-mode behavior.

## Codex Lessons

Live Codex Plan Mode contributes four rules: explore repo/tracker/source facts before asking; ask only about intent or undiscoverable tradeoffs; keep durable artifacts distinct from transient `update_plan` checklists; and replace revised artifact sections completely so `he-plan` never invents behavior.

## Session Collector Lessons

`~/.agents/session-collector` emits normalized JSON from OTEL logs and Codex rollout sessions. Use it for project hints, prior-session decisions, Harness Engineering stage mentions, validation gates, recurring failures, tool-call patterns, and blockers.

Use collector summaries as evidence, not authority. If collector evidence conflicts with current repo state, current spec files, or Linear, the current source of truth wins and the conflict must be recorded.

Do not paste raw transcripts, account identifiers, secrets, or private session text into specs. Use redacted summaries and cite the collector artifact path or generated evidence summary.
