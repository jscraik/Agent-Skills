# Lifecycle Exit Contract

Use this at the end of every active HE stage so downstream agents know status, proof, and next step.

## Active Spine

`he-router -> he-brainstorm -> he-spec -> he-plan -> he-work -> he-code-review -> he-fix-bugs -> he-work|done`

Use `he-improve` for measured improvement, `he-compound` for cross-stage orchestration or solved-problem capture, and `he-heartbeat` for wake/re-check loops.

Folded stages are modes, not the default route:

- `he-ideate` -> `he-brainstorm`
- `he-deepen-spec` -> `he-spec`
- `he-deepen-plan` -> `he-plan`
- `he-tdd` -> `he-work`
- `he-refine` -> `he-improve`
- `he-technical-review`, `he-reliability-review` -> `he-code-review`
- `he-compound-refresh` -> `he-compound`

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
coding_harness:
  mode: coding-harness-managed|generic-he|unknown
  linear_state: S0_TRIAGE|S1_READY|S2_IN_PROGRESS|S3_IN_REVIEW|S4_DONE|S5_FAIL|unknown|not_applicable
  blocked_overlay: true|false|unknown|not_applicable
  transition_event: scoped|start|progress_tick|pr_opened|handoff_ready|merged|blocked|unblocked|fail|not_applicable
  transition_command: "<harness linear ... command, Linear action, or blocked reason>"
  project_brain_status: updated|not_applicable|blocked|not_checked
  north_star_evidence_status: pass|blocked|not_applicable|not_checked
  harness_commands_run: []
  harness_commands_blocked: []
```

For short chat responses, summarize the same fields without losing blocker, tracker, artifact, validation, or next-stage state.

## Exit Rules

- Do not hand off tracked work unless the Linear gate is `resolved`, `created`, `user_opted_out`, or explicitly `blocked`.
- Do not route to `he-plan` while behavior, acceptance criteria, or product scope is unresolved.
- Do not route to `he-work` while plan/source traceability, validation strategy, or scope boundary is missing.
- Do not claim `done` without validation evidence or a concrete reason validation is not applicable.
- Do not let a PR, branch, local plan, or session summary replace Linear as tracker of record.
- In coding-harness-managed repos, lifecycle transitions require populated or explicitly blocked Harness command bridge fields.

## Stage Minimums

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

## Coding Harness Managed Repos

When `harness.contract.json`, `.harness/`, or Harness gates are present, load `references/coding-harness-command-bridge.md`. Record Project Brain and north-star evidence using the exact bridge vocabularies: `project_brain_status` is `updated|blocked|not_checked|not_applicable`, and `north_star_evidence_status` is `pass|blocked|not_checked|not_applicable`. A blocked or not-checked status must preserve the exact missing command/path in `harness_commands_blocked` or the matching evidence field.

## Cut Policy

Prefer one active stage plus one folded mode over a niche stage. Add a first-class stage only for distinct inputs, exit evidence, and a clear routing boundary.
