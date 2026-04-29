# Session Evidence Contract

Read when: the user asks about prior Codex sessions, archived sessions, session history, `~/.codex/sessions`, `~/.codex/archived_sessions`, `~/.agents/session-collector`, repeated HE failures, or improvements learned from previous runs.

Harness Engineering consumes session evidence to choose and improve lifecycle work. It does not own the raw telemetry pipeline.

## Source Order

Use the highest-confidence available source first:

1. `~/.agents/session-collector` for normalized recent session evidence.
2. `~/.codex/archived_sessions` for durable historical recurrence.
3. `~/.codex/session_index.jsonl` and `~/.codex/history.jsonl` for fast handle and phrase frequency checks.
4. `~/.codex/sessions` for current live runtime state only.

When running the collector in constrained Codex environments, prefer a temp uv cache:

```bash
cd ~/.agents/session-collector
UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache \
uv run --python 3.12 python main.py \
  --days 30 \
  --output /private/tmp/he-session-collector-30d.json \
  --bundle-dir /private/tmp/he-session-collector-30d \
  --verbose \
  --codex-sessions-dir /Users/jamiecraik/.codex/archived_sessions \
  --codex-sessions-dir /Users/jamiecraik/.codex/sessions
```

Consume `/private/tmp/he-session-collector-30d/harness-engineering-evidence.json` for HE routing signals, `solved-problems.json` for reusable solved patterns, `index.json` for redacted session labels, and `redaction-report.json` before citing evidence in decisions.

Use raw archive scans only for narrow searches such as a known session id, exact error string, handle name, or issue phrase.

## Routing Rules

Route session-evidence requests by intended outcome:

- Plugin or workflow improvement from previous runs -> `he-improve`.
- Active compound run drift, stale handoff, repeated gate failure, or unclear resume state -> `he-compound-refresh`.
- Recurring follow-up until PR, CI, review, Linear, or validation state changes -> `he-heartbeat`.
- Concrete implementation tasks already derived from evidence -> `he-work`.
- Correctness, safety, or review-feedback validity from evidence -> `he-technical-review`.
- Bug reproduction, failing command, deterministic error, or root cause from evidence -> `he-fix-bugs`.

If the user only asks "what did we learn?" or "what keeps failing?", do the evidence pass first and route to the narrowest next HE stage after findings are known.

## Evidence Signals

Classify recurrence into explicit action, not background prose:

- Legacy `ce-*` handle drift or misspellings such as `ce-ttd` -> add router alias, migration, or eval coverage.
- Repeated `plan`, `fix`, `validate`, `continue`, or "review findings" loops -> strengthen phase boundaries and completion gates.
- Repeated catalog, routing-map, command-surface, or picker parity failures -> update source/projection/sync validation gates.
- Review-before-work mistakes -> enforce a reviewer-completion barrier before implementation starts.
- Unresolved Codex, CodeRabbit, or GitHub review threads -> route to review-thread closure before merge readiness.
- PR, CI, Linear, deploy, or validation waits -> create or record a heartbeat unless the user explicitly wants a one-off check.
- `.git` permission, `index.lock`, uv cache, or sandbox permission blockers -> classify as environment blockers with exact failing command evidence.

## Output Contract

When session evidence influences a Harness Engineering decision, include:

```yaml
schema_version: 1
evidence_sources:
  - "<collector bundle artifact or exact path>"
recurring_signals:
  - "<signal and count or sample>"
selected_he_stage: "<he-* stage>"
actions:
  - "<actionable change or validation>"
blocked:
  - "<blocker with exact command or path>"
```

Do not claim a recurrence from memory alone. Cite the source path, collector output, index count, or exact sample used.
