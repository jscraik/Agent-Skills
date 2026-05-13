# Lifecycle Exit Contract

Use this at the end of every active HE stage so downstream agents know status, proof, and next step.

## Active Spine

`he-router -> he-brainstorm -> he-spec -> he-plan -> he-work -> he-code-review -> he-fix-bugs -> he-work|done`

Use `he-improve` for measured improvement, `he-reconcile` for cross-stage state reconciliation, `he-reinforce` for solved-problem capture or learning refresh, and `he-heartbeat` for wake/re-check loops.

Folded stages are modes, not the default route:

- `he-ideate` -> `he-brainstorm`
- `he-deepen-spec` -> `he-spec`
- `he-deepen-plan` -> `he-plan`
- `he-tdd` -> `he-work`
- `he-refine` -> `he-improve`
- `he-technical-review`, `he-reliability-review` -> `he-code-review`
- `he-compound` state refresh -> `he-reconcile`
- `he-compound-refresh` or solved-problem compound -> `he-reinforce`

## Durable Artifact Routing

HE stage markdown belongs in the repo-local Harness surface:

| Stage or mode | Artifact root |
| --- | --- |
| `he-ideate` folded mode | `.harness/ideate/**.md` |
| `he-brainstorm` | `.harness/brainstorm/**.md` |
| `he-spec` | `.harness/specs/**.md` |
| `he-plan` | `.harness/plan/**.md` |

Legacy `Docs/`, `Specs/`, `Plans/`, or `docs/brainstorms/` paths may be read as
source evidence, but new durable docs for these stages should be written under
the matching `.harness` root and listed in `evidence.artifacts`.

## Required Status Shape

When structured output is requested, or when handing off to another HE stage, emit:

```yaml
schema_version: 1
he_stage: he-router|he-brainstorm|he-spec|he-plan|he-work|he-code-review|he-fix-bugs|he-improve|he-reconcile|he-reinforce|he-heartbeat
mode: "<stage mode or folded mode>"
tracker_status: resolved|created|blocked|not_applicable|user_opted_out
artifact_status: none|drafted|updated|validated|not_applicable
traceability_status: pass|blocked|not_applicable
validation_status: pass|fail|blocked|not_run_with_reason|not_applicable
git_staging_status: staged|blocked|not_applicable
staged_paths: []
unstaged_unrelated_paths: []
gate_profile:
  risk_class: trivial|standard|domain_sensitive|architecture_sensitive|closure_sensitive|security_sensitive|mixed|not_applicable
  proven_risks: []
  required_contracts: []
  skipped_contracts: []
  minimum_proof_required:
    continue_to_next_stage: "<proof needed before handoff or not_applicable>"
    safe_to_close: "<proof needed before completion or not_applicable>"
    block_next_stage: "<condition that blocks handoff or not_applicable>"
domain_language:
  status: stable|ambiguous|conflicted|not_applicable
  canonical_terms: []
  avoided_aliases: []
  unresolved_terms: []
  context_file: CONTEXT.md|CONTEXT-MAP.md|domain-context-contract.md|not_applicable
  context_map:
    source_of_truth: user_request|linear|spec|plan|worktree|pr|validation|project_brain|heartbeat|goal|session_evidence|not_applicable
  translated_from: []
  relationship: source_of_truth|translation|handoff|evidence_only|stale_snapshot|not_applicable
  conflict_status: none|blocked|resolved|not_applicable
  conflict_rule: stop|refresh|prefer_source|record_blocker|not_applicable
domain_model:
  status: stable|ambiguous|conflicted|not_applicable
  bounded_context: ""
  core_domain_relevance: core|supporting|generic|unknown|not_applicable
  closure_impact: blocks_spec|blocks_plan|blocks_work|blocks_review|blocks_eval|none
exit_status: ready_for_next_stage|blocked|done
next_stage: he-brainstorm|he-spec|he-plan|he-work|he-code-review|he-fix-bugs|he-improve|he-reconcile|he-reinforce|he-heartbeat|done
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

For short chat responses, summarize the same fields without losing blocker, tracker, artifact, validation, git staging, or next-stage state.

## Exit Rules

- Do not hand off tracked work unless the Linear gate is `resolved`, `created`, `user_opted_out`, or explicitly `blocked`.
- Do not route to `he-plan` while behavior, acceptance criteria, or product scope is unresolved.
- Do not route to `he-work` while plan/source traceability, validation strategy, or scope boundary is missing.
- Do not claim `done` without validation evidence or a concrete reason validation is not applicable.
- Do not finish after writing artifacts without applying `git-staging-contract.md` or reporting why staging is blocked or not applicable.
- Do not let a PR, branch, local plan, or session summary replace Linear as tracker of record.
- Do not let external review, CI, session, or user wording change HE domain meaning without translation through `domain-context-contract.md`.
- When `domain_model.status` is ambiguous or conflicted, do not harden the next lifecycle stage until the owning artifact records the bounded context and closure_impact.
- In coding-harness-managed repos, lifecycle transitions require populated or explicitly blocked Harness command bridge fields.
- Do not load broad domain, strategy, refactor, Linear, security, specialist, or eval gates unless `gate_profile` proves the risk class and required contracts.
- Do not claim release confidence while lifecycle evals time out; scope the claim to static wiring or route timeout repair.

## Stage Minimums

- `he-router`: selected stage, confidence, matched rule, missing input if blocked.
- `he-brainstorm`: problem frame, scope tier, spec decision, Linear tracker state for durable handoff, `.harness/brainstorm` or folded `.harness/ideate` artifact when written, next stage.
- `he-spec`: accepted behavior contract for one selected milestone, parent issue, refactor phase, or execution slice; stable acceptance IDs; Linear Work Item Contract; `.harness/specs` artifact; explicit In Scope and Out of Scope boundaries; next planning slice.
- `he-plan`: stable units, dependencies, tests, rollback, `.harness/plan` artifact, Linear/spec/plan/PR traceability matrix, and proof the plan stays inside the selected execution slice.
- `he-work`: changed slices, completed IDs, validation evidence, drift notes, PR/Linear handoff, and proof the implementation stayed inside the selected execution slice.
- `he-code-review`: findings, readiness verdict, evidence ladder, next action.
- `he-fix-bugs`: reproduction, root cause, fix/verification status, regression test recommendation.
- `he-improve`: baseline, measured delta, accepted/rejected experiment, rollback posture.
- `he-reconcile`: mode, earliest incomplete stage, stage exit evidence, next exact stage.
- `he-reinforce`: solved status, selected learning artifact, Project Brain status, discoverability, and validation evidence.
- `he-heartbeat`: live checks, cadence, stop conditions, next stage when the heartbeat wakes.

## Coding Harness Managed Repos

When `harness.contract.json`, `.harness/`, or Harness gates are present, load `references/coding-harness-command-bridge.md`. Record Project Brain and north-star evidence using the exact bridge vocabularies: `project_brain_status` is `updated|blocked|not_checked|not_applicable`, and `north_star_evidence_status` is `pass|blocked|not_checked|not_applicable`. A blocked or not-checked status must preserve the exact missing command/path in `harness_commands_blocked` or the matching evidence field.

## Cut Policy

Prefer one active stage plus one folded mode over a niche stage. Add a first-class stage only for distinct inputs, exit evidence, and a clear routing boundary.
