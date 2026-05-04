# Lifecycle Exit Contract

Use this contract at the end of every active Harness Engineering stage. The goal is simple: a downstream agent should know whether it can continue, what proof exists, and what must happen next.

## Active Spine

The active lifecycle spine is:

`he-router -> he-brainstorm -> he-spec -> he-plan -> he-work -> he-code-review -> he-fix-bugs -> he-work|done`

Use `he-improve` only when existing behavior needs a measured improvement loop. Use `he-compound` only when the user needs orchestration across several spine stages or durable solved-problem capture. Use `he-heartbeat` only when the thread must wake later and re-check live state.

Use Codex `/goal` as optional continuity state for long-running work, not as a lifecycle stage. Goals must point back to the active tracker/artifact/branch/PR chain and follow `references/goal-continuity.md`.

Folded stages are modes, not the default route:

- `he-ideate` folds into `he-brainstorm`.
- `he-deepen-spec` folds into `he-spec`.
- `he-deepen-plan` folds into `he-plan`.
- `he-tdd` folds into `he-work`.
- `he-refine` folds into `he-improve`.
- `he-technical-review` and `he-reliability-review` fold into `he-code-review`.
- `he-compound-refresh` folds into `he-compound`.

## Required Status Shape

When structured output is requested, or when handing off to another HE stage, emit:

```yaml
schema_version: 1
he_stage: he-router|he-brainstorm|he-spec|he-plan|he-work|he-code-review|he-fix-bugs|he-improve|he-compound|he-heartbeat
mode: "<stage mode or folded mode>"
tracker_status: resolved|created|blocked|not_applicable|user_opted_out
artifact_status: none|drafted|updated|validated|not_applicable
traceability_status: pass|blocked|not_applicable
validation_status: pass|fail|blocked|not_run_with_reason|not_applicable
exit_status: ready_for_next_stage|blocked|done
next_stage: he-brainstorm|he-spec|he-plan|he-work|he-code-review|he-fix-bugs|he-improve|he-compound|he-heartbeat|done
missing_inputs: []
evidence:
  linear: "<issue key/url or blocker>"
  artifacts: ["<repo-relative paths>"]
  validation: ["<command -> pass|fail|blocked>"]
  pr: "<PR URL or not_applicable>"
```

For short chat responses, summarize the same fields in prose without losing blocker, tracker, artifact, validation, and next-stage state.

## Exit Rules

- Do not hand off non-trivial tracked work unless the Linear tracker gate is `resolved`, `created`, `user_opted_out`, or explicitly `blocked`.
- Do not route to `he-plan` while behavior, acceptance criteria, or product scope is unresolved.
- Do not route to `he-work` while plan/source traceability, validation strategy, or scope boundary is missing for non-trivial work.
- Do not claim `done` without validation evidence or a concrete reason validation is not applicable.
- Do not let a PR, branch, local plan, or session summary replace Linear as tracker of record.
- Do not mark an active thread goal complete until this exit contract is satisfied or explicitly blocked for every requirement in the goal.

## Stage-Specific Minimums

- `he-router`: selected stage, confidence, matched rule, missing input if blocked.
- `he-brainstorm`: problem frame, scope tier, spec decision, Linear tracker state for durable handoff, next stage.
- `he-spec`: accepted behavior contract, stable acceptance IDs, Linear Work Item Contract, next planning slice.
- `he-plan`: stable units, dependencies, tests, rollback, Linear/spec/plan/PR traceability matrix.
- `he-work`: changed slices, completed IDs, validation evidence, drift notes, PR/Linear handoff.
- `he-code-review`: findings, readiness verdict, evidence ladder, next action.
- `he-fix-bugs`: reproduction, root cause, fix/verification status, regression test recommendation.
- `he-improve`: baseline, measured delta, accepted/rejected experiment, rollback posture.
- `he-compound`: mode, earliest incomplete stage, stage exit evidence, next exact stage.
- `he-heartbeat`: live checks, cadence, stop conditions, next stage when the heartbeat wakes.
- Active goal: objective alignment, status, completion/blocker evidence, and the next HE stage when the goal remains active.

## Cut Policy

Prefer one active stage plus one folded mode over selecting a niche stage directly. Add a new first-class stage only when it has distinct required inputs, distinct exit evidence, and a routing boundary a fresh agent can explain in one sentence.
