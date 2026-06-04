---
name: sy-router
description: "Routes ambiguous SynAIpse Harness requests by applying route rules, asking for one missing input when needed, and returning a structured next-stage handoff. Use when a request could match two or more Harness stages or mixes artifacts, PR/review, validation, tracker, session, heartbeat, branch cleanup, or specialist routing."
metadata:
  version: "0.1.0"
  level: router
  skill-type: team_automation
  command_visibility: none
  runtime_visibility: hidden
---

# Skill: SynAIpse Harness Router

## Purpose

Choose one next SynAIpse Harness stage, folded mode, or blocker from current
evidence. Do not perform the selected stage's work.

## Philosophy

Prefer a reversible route with clear evidence over a confident guess.

## When to Use

- The request asks which SynAIpse stage should run next.
- Multiple stage signals appear together, such as spec plus PR review, Linear
  closure plus missing validation, or phase work plus stale evidence.
- Old or folded wording appears, such as sy-tdd, sy-refine,
  sy-technical-review, or sy-prune-branches.
- The user asks for routing across tracker state, prior sessions, closure proof,
  waits, branch hygiene, gate selection, or specialist fit.

## Do Not Use When

- The user explicitly invokes one valid non-router sy-* stage.
- The task is outside SynAIpse Harness routing.
- A selected stage already owns implementation, mutation, installs, deploys,
  branch cleanup, or completion claims.

## Inputs

Required: user request and current workspace root.

Optional: artifact paths, tracker IDs, session evidence, PR/review state,
validation output, constraints, and available specialist roles.

## Outputs

Return one compact object with exactly one of selected_stage or blocker.

~~~yaml
route_preview_version: 1
schema_version: sy-router.route-preview.v1
selected_stage: sy-eval-report
matched_rule: closure-proof-eval
source_path: Plugins/synaipse-harness/references/routing-map.json
confidence: medium
authority_limit: route-only
why_not:
  sy-work: implementation appears complete, but closure proof is missing
collector_freshness: unknown
missing_input: latest validation artifact path
recommended_next_step: "Run $synaipse-harness:sy-eval-report with current validation evidence."
safe_to_continue: false
handoff_payload:
  external_writes_allowed: false
~~~

For blocked routes, replace selected_stage with blocker, blocked_reason,
blocker_taxonomy, and one missing_input.

## Procedure

1. Inspect only the 2-3 surfaces needed to decide the route.
2. Apply routing-map.json and deterministic decision order before keyword
   matching.
3. Classify freshness before intent when prior-session, collector,
   repeated-failure, or coverage-gap evidence is involved.
4. Select one stage or blocker. If two stages remain equally valid, return one
   missing_input instead of guessing.
5. Record the matched rule, rejected stages, authority limit, freshness,
   confidence, and next invocation.
6. Load selected-stage context only after routing is decided.

## Minimal Decision Tree

1. If the request asks what stage is next or mixes stages, use sy-router.
2. If work is done but closure proof, drift proof, validation summary, or
   tracker completion is missing, return sy-eval-report.
3. If the user asks to build or change code from an approved plan/spec, return
   sy-work; if the failure is already reproduced, return sy-fix-bugs.
4. If the user asks to create planning artifacts, route in this order:
   sy-strategy, sy-reframe, sy-trace-plan, sy-tracker-plan, sy-spec, then
   sy-execution-plan, based on the first missing artifact.
5. If state is stale, contradictory, or resumed from old evidence, return
   sy-reconcile or block for one live refresh input.

## Failure Mode

Capture the exact failing command, fix the smallest canonical source that caused
it, rerun the failed gate, and report what the rerun proves.

## Constraints

- Preserve repo, artifact, tracker, PR, validation, and session identity.
- Use one recovery action for blockers.
- Redact secrets, credentials, tokens, private transcripts, and sensitive
  personal data by default.

## Execution Boundaries

Router authority is read-only classification and handoff. It must not edit code,
write artifacts, mutate tracker/GitHub state, install packages, deploy, read
secrets, prune branches, or claim completion.

Ask once or block when consequential ambiguity remains.

## Gotchas

- Folded aliases are modes, not missing skills.
- Plugin Eval or audit success does not prove live PR, tracker, CI, or runtime
  readiness.
- A selected stage owns its own deeper context.

## Anti-Patterns

- Writing artifacts, mutating trackers, pruning branches, or claiming completion
  from a router response.
- Returning a multi-stage plan when one selected stage or one blocker is needed.
- Collapsing session evidence, local validation, PR state, CI, reviews, and
  tracker state into one proof lane.

## Context Routes

- Deterministic route table: Plugins/synaipse-harness/references/routing-map.json
- Route priority and folded aliases:
  Plugins/synaipse-harness/references/deterministic-stage-routing.md
- Gate selection: Plugins/synaipse-harness/references/gate-selection-contract.md
- Domain terms: Plugins/synaipse-harness/references/domain-model-routing.md
- Stage boundaries: ../../references/stage-arc-boundary-contract.md
- Deferred context index: ../../references/deferred-context-index.md

## Validation Gates

Fail fast and stop at the first failed gate.

~~~bash
./bin/ask skills audit Plugins/synaipse-harness/skills/sy-router --level strict --json --robot
./bin/ask evals run Plugins/synaipse-harness/skills/sy-router --mode smoke --json --robot
./bin/ask skills external-review Plugins/synaipse-harness/skills/sy-router --audit-level compat --json --robot
~~~

The audit proves local skill shape. Smoke evals prove scenario behavior when the
runner emits evidence. External review runs Plugin Eval plus local Tessl lint and
review; it does not prove current PR, tracker, CI, or runtime state.

## Examples

- Request: "JSC-244 has a draft spec, Linear notes, and an open PR; choose
  plan, work, review, or eval." Expected: one selected stage, rejected stages,
  missing proof, and no implementation.
- Request: "PR 153 merged but Linear is still In Review; route closure without
  closing Linear." Expected: sy-eval-report, no external writes, and a
  validation-evidence handoff.
- Request: "Clean stale branches while checking whether phase work can
  continue." Expected: block or route the dominant stage; do not prune branches.
