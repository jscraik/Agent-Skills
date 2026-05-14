# Harness Engineering Work Handoff And Shipping

Final handoff includes what changed, areas touched, validation run, Linear issue/status/comment result, governing spec/plan paths, branch/PR or blocker, completed IDs, drift updates, risks/deferrals, rollback or monitoring notes, UI screenshots when relevant, and a safe Harness Engineering trace when the work will feed a PR or cites session evidence.

Every shipped change includes concrete monitoring notes or a justified no-impact note. Useful notes: logs/searches, metrics, healthy signals, failure signals, rollback triggers, validation window, and owner.

Default meaningful code changes to Tier 2: `he-code-review mode:autofix` with `plan:` when available. Tier 1 inline self-review is only for purely additive, single-concern, pattern-following, plan-faithful slices.

Use repo commit/PR conventions. Keep commits logical, avoid WIP commits, and link PR evidence back to Linear and the governing artifacts. GitHub is delivery evidence, not the tracker of record.

## PR Safety Trace

When a change is PR-bound or cites Codex/session evidence, include a public-safe
handoff block with he_trace_id, Linear issue, spec artifact, plan artifact,
review/eval/reconcile artifacts when present, validation evidence location,
provenance source, provenance status, redaction status, and sensitive evidence
status.

PR-facing evidence-location fields must be repository-relative artifact paths,
public PR/CI URLs, artifact IDs, or hash-only tokens. Do not use absolute local
filesystem paths in PR text.

Do not include raw Codex session IDs, thread IDs, turn IDs, transcript paths,
rollout paths, rollout trace bundle paths, prompts, responses, tool payloads, or
telemetry contents in PR text. Include hashed IDs or presence flags only, and
record raw mappings only in a local artifact marked sensitive_local_only.

Validation remains separate proof. A provenance block can show correlation and
freshness; it does not prove tests passed, implementation correctness, Linear
updates, review-thread closure, or merge readiness.

Read before PR-bound handoff: ../../../references/pr-safety-trace-contract.md
and ../../../references/codex-provenance-contract.md.
