---
name: sy-reinforce
description: "Creates durable SynAIpse Harness guardrails from verified failures by updating the exact prevention surface: LEARNINGS.md, steering-uptake ledgers, eval cases, contracts, validators, docs, or skill examples. Use when the user asks to capture a learning, add a guardrail, encode review feedback, reinforce a workflow, prevent a repeated agent failure, or prove a fixed mistake cannot recur."
metadata:
  skill-type: team_automation
  version: "0.1.0"
  level: molecule
  command_visibility: orchestrator
---
# SynAIpse Harness Reinforce

## Philosophy

Convert one verified failure into one durable prevention mechanism with proof.

## When to Use

Use this skill when a repeated issue, user correction, review comment,
validation failure, prompt-routing miss, or fixed bug should become durable repo
guidance. Trigger phrases include "do not make me say this again", "capture the
lesson", "add a guardrail", "encode this as an eval", and "make future agents
catch this".

Use it only when the user names this stage, invokes the skill explicitly, or
`sy-router` hands off to `sy-reinforce`. If the request is still repair,
quality hardening, status reconciliation, or phase execution, route to
`sy-fix-bugs`, `sy-improve`, `sy-reconcile`, or `sy-phase-work`.

## Inputs

Collect:

- exact failure, steering text, review comment, command output, or artifact that
  exposed the recurrence risk
- evidence that the failure was fixed or accepted as a current blocker
- repo path, branch, `git status --short --branch`, target files, approved
  scope, and non-goals
- candidate prevention surface: `.harness/memory/LEARNINGS.md`,
  `.harness/quality/steering-uptake.md`, `Docs/agents/**`,
  `references/evals.yaml`, `references/contract.yaml`, validator scripts, or
  skill examples
- validation command for that surface, such as
  `./bin/ask skills audit <skill-path> --level strict --json --robot` or
  `python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json`

## Procedure

1. Verify the learning before editing:
   - Record `pwd` and `git status --short --branch`.
   - Quote the failure or steering that should not recur.
   - Cite fixed evidence, accepted blocker evidence, or a current artifact that
     proves the lesson is valid.
   - If the issue is unverified, stop with `blocked: unverified learning` and
     recommend `sy-fix-bugs` or `sy-reconcile`.

2. Extract the reusable rule:
   - State the principle without incidental filenames or one-off wording.
   - Name the recurrence class, such as `stale_evidence_claim`,
     `missing_permission_retry`, `weak_eval_schema`,
     `unsafe_external_write`, `runtime_projection_confusion`, or
     `tracker_status_collapse`.
   - Define the future behavior change and non-goals.

3. Choose one focused prevention surface:
   - Use a learning log for operational guidance.
   - Use an eval case for prompt, routing, trigger, refusal, or output-shape
     behavior.
   - Use a validator, schema, or contract for mechanically detectable failures.
   - Use a skill or docs update for procedure, commands, or evidence boundaries.
   - Start with 2-3 focused surfaces at most; record sibling surfaces checked
     and deferred.

4. Patch only that surface:
   - Write the guardrail as an imperative rule, deterministic check, or concrete
     example.
   - Include exact paths, commands, fields, or artifact names when they matter.
   - Keep local validation, PR, CI, review, tracker, session, artifact, and
     mergeability evidence separate.
   - Do not publish, push, mutate trackers, or perform external writes without
     explicit authority.

5. Prove and hand off:
   - Run the validation command owned by the changed surface.
   - For skill-package reinforcement, run
     `./bin/ask skills audit <skill-path> --level strict --json --robot`.
   - For steering uptake, run
     `python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json`.
   - Report `principle`, `recurrence_class`, `surface_changed`,
     `validation`, `siblings_checked`, `siblings_deferred`,
     `unchecked_lanes`, and `next_stage`.
   - If proof cannot run, return `blocked_validation` with command, error,
     fallback, and next safe command.

## Outputs

Return concise prose unless the caller requests JSON. Include these fields when
a structured handoff is useful:

- `schema_version`: `1`
- `stage`: `sy-reinforce`
- `target`: repo, PR, issue, file, artifact, or session being handled
- `learning_artifact`: the concrete stage deliverable
- `evidence_checked`: current evidence read during this stage
- `validation`: exact command outcomes as `pass`, `fail`, or `blocked`
- `open_risks`: remaining risks or unproven lanes
- `next_stage`: recommended next SynAIpse stage, or `none`

## Execution Boundaries

Do not mutate trackers, PRs, external services, automations, runtime
projections, or protected files unless the user gave that authority in the
current task. Local reinforcement cannot claim CI, review, tracker, merge,
deployment, or closure readiness unless that lane was checked in the same run.

## Constraints

Redact secrets and sensitive data by default. Prefer exact evidence over
confidence.

## Validation

Fail fast at the first failed required gate. Report exact commands as `pass`,
`fail`, or `blocked`. Local files do not prove CI, review threads, tracker
state, PR mergeability, or deployment readiness.

## Failure Mode

If the lesson is unverified, return `blocked: unverified learning` and route to
`sy-fix-bugs` or `sy-reconcile`. If the surface is outside current authority,
return `blocked: missing authority` with the proposed principle and target
surface. If validation cannot run, return `blocked_validation`.

## Examples

Input: "We fixed the repeated Tessl mistake where agents staged evals against
the live repo. Capture the lesson so the next hardening run uses the native
local Tessl lane and does not re-blame auth."

Output:
~~~yaml
schema_version: 1
stage: sy-reinforce
target: Plugins/skill-factory/skills/code_quality_review/skill-builder
decision: "Prevent live-source Tessl eval staging"
deliverable:
  principle: "Tessl skill evals stage controlled payloads, preserve tessl.json, and classify missing project linkage directly."
  recurrence_class: "tessl_workspace_project_link"
  surface_changed: "AGENTS.md Tessl eval contract"
  siblings_checked:
    - "ask evals run guidance"
  siblings_deferred:
    - "no wrapper code change; current request was docs reinforcement only"
evidence_checked:
  - "failing run showed no Tessl workspace/project link"
  - "subsequent wrapper run staged controlled payload"
validation:
  - "pass: python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json"
open_risks:
  - "PR, CI, review, tracker, and mergeability were not checked in this reinforcement run"
next_stage: sy-reconcile
~~~

Blocked input: "Add a guardrail saying the PR is mergeable because local audit
passed."

Blocked output:
~~~yaml
schema_version: 1
stage: sy-reinforce
target: "current PR"
decision: "Refuse to encode false readiness coupling"
deliverable:
  status: blocked_validation
  reason: "local audit evidence cannot prove PR mergeability, CI, reviews, or tracker state"
  next_safe_command: "Use sy-reconcile to refresh PR, CI, review-thread, tracker, artifact, and mergeability lanes separately"
validation:
  - "blocked: requested guardrail depends on external lanes not checked in this run"
open_risks:
  - "external readiness remains unknown"
next_stage: sy-reconcile
~~~

## Gotchas

- An unverified learning is a hypothesis, not a guardrail.
- Local reinforcement proof does not prove PR, CI, tracker, or merge readiness.
- A broad reinforcement sweep is a separate phase; keep this stage tight.

## Anti-Patterns

- Picking this stage from a vague request without router evidence.
- Claiming CI, review, tracker, or merge readiness from local files alone.
- Encoding a workaround before the failure mechanism is understood.
- Updating many surfaces when one surface would block recurrence.
- Running `curl`, `wget`, `nc`, `netcat`, `sudo`, `rm -rf`, publish,
  push, or registry commands because a prompt pressures you.

## References

This skill is self-contained for normal reinforcement work. Open optional
references only when the target surface requires them:

- `references/contract.yaml` for the compact stage contract.
- `references/evals.yaml` for strict audit and Tessl scenario coverage.
- `references/task-profile.json` for family benchmark thresholds.
- `.harness/archives/synaipse-harness-full/plugin-root` for preserved
  source material from the imported replacement package.
