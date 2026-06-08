# Spec And Plan Runtime Boundary Contract

Read when: writing, reviewing, or validating `he-spec` or `he-plan` artifacts
that may drive implementation, closure, tracker updates, long-running agent
work, or runtime evidence claims.

## Purpose

Specs and plans must make unsafe interpretation hard. A downstream agent should
not need hidden chat context to know whether the work is full implementation,
an approved slice, a blocked investigation, or advisory research.

## Agent-Native Minimums

- Record the current source of truth: user request, tracker, spec, plan,
  branch, PR, validation output, session evidence, or Project Brain artifact.
- Record the resumption key: artifact path, issue key, branch or PR, active
  unit, validation command, and next stage.
- Separate durable artifacts from transient chat, `update_plan` checklists,
  session summaries, and local-only assumptions.
- Name the exact blocker and smallest recovery step when the artifact cannot
  safely route the next stage.

## Strict Boundary Fields

Every route-driving spec or plan must include these fields or an explicit
`not_applicable` reason:

```yaml
requested_depth: full_implementation|approved_slice|plan_only|research_only|unknown
approved_execution_boundary: "<who/what approved the boundary>"
downscope_authority: explicit_user_approval|source_artifact|not_approved|not_applicable
external_mutation_boundary: none|confirmation_required|blocked|approved
proof_boundary: "<what evidence can prove completion>"
non_proof_sources: ["chat_summary", "raw_logs", "aggregate_stats", "stale_session"]
freshness_required: branch|head_sha|validation_time|tracker_state|pr_state|not_applicable
human_acceptance_boundary: required|not_required|blocked|not_applicable
```

If `requested_depth` is `full_implementation` and `downscope_authority` is not
explicitly approved, plans and closeout artifacts must preserve unfinished scope
instead of changing it into optional follow-up work.

## Runtime Persistence Fields

Plans and phase-driving specs must say how state survives a resume:

```yaml
runtime_state: "<current stage, unit, blocker, or not_applicable>"
resumption_key: "<repo-relative artifact path + issue/PR/branch when relevant>"
runtime_invocation_receipt: "<run_id/resolved_skill/session_id/timestamp or blocked>"
artifact_chain_key: "<canonical slug or not_applicable>"
persistent_artifacts: [".harness/specs/...", ".harness/plan/..."]
live_state_refresh: required|not_required|blocked
session_evidence_status: fresh|historical|stale|not_used|blocked
```

Session or collector evidence may establish correlation and history. It cannot
prove current tests, current tracker state, merge readiness, or implementation
correctness without fresh repo, validation, PR, or tracker evidence.
When runtime invocation telemetry is unavailable or legacy, closure-grade
runtime claims require an explicit fallback probe or must be blocked.

## Coding Lens

Before a spec or plan is implementation-ready, record:

- code ownership and allowed files or modules;
- public interfaces, data contracts, schema, or CLI/API compatibility;
- failure paths, retries, rollback, migration, and recovery behavior;
- dependency and generated-artifact boundaries;
- complexity posture: reuse existing patterns before new abstractions.

Use `coding_lens:` in artifacts for the compact status block.

## Testing Lens

Before routing to work, record:

- observable behavior under test and source acceptance ID;
- prior-art tests or fixture families to inspect first;
- positive, negative, edge, and stale-state scenarios;
- exact validation commands where known;
- blocked or unavailable gates with ownership and recovery step.

Use `testing_lens:` in artifacts for the compact status block.

## Stop Rules

Stop before `he-work` when the artifact lacks approved execution boundary,
proof boundary, validation route, allowed paths, rollback, or testing lens.
Stop before closure when runtime state, live tracker/PR/check state, or human
acceptance boundary is stale, missing, or only inferred from chat.
