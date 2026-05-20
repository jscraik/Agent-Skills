# HE Product Front Door And Runtime Contract Refactor

schema_version: 1
selected_stage: he-refactor
selected_candidate: HE productization lessons from EveryInc compound-engineering plugin
status: accepted

## Refactor Classification

Structural plugin productization refactor. The candidate is high leverage because
it improves HE's first-contact usability, runtime/source boundary clarity,
artifact quality, and route validation without expanding HE into a generic
productivity suite.

## Problem Statement

Harness Engineering has strong lifecycle and closure-proof architecture, but it
still asks humans and agents to understand HE vocabulary too early. The
EveryInc compound-engineering plugin shows a better first-contact product
surface: setup-first onboarding, default prompts, grouped use cases, explicit
installed-plugin drift debugging, and authoring guidance that separates repo
authoring context from shipped runtime behavior.

## Root Cause Analysis

- HE has rich internal contracts, but the front door is still lifecycle-shaped.
- Runtime behavior, authoring guidance, generated projections, and plugin cache
  behavior are easy to confuse without an explicit doctrine.
- `.harness` artifacts can become process-heavy unless artifact content and
  process exhaust are separated.
- Existing route and authority validation is strong but does not yet enforce
  all user-facing product surfaces derived from canonical route intent.

## Evidence

- Local HE README already states the value thesis: prevent local-only progress
  from masquerading as done.
- Local `he-router` already owns `route_preview_version: 1`, authority limits,
  and closure routing to `he-eval-report`.
- Local `he-linear-plan` requires `.harness` cognition before live Linear
  mutation and blocks backlog dumping.
- EveryInc pinned source:
  - `plugins/compound-engineering/README.md`
  - `plugins/compound-engineering/.codex-plugin/plugin.json`
  - `plugins/compound-engineering/AGENTS.md`
  - `plugins/compound-engineering/skills/**`

## Architectural Impact

The target architecture keeps HE narrow:

- HE remains the harness layer for routing, status, closure proof, state
  recovery, and learning capture.
- Product usability improves through a setup/status front door and default
  prompts.
- Runtime behavior lives in shipped skills, references, scripts, and generated
  contracts, not repo-only authoring instructions.
- Generated or checked product docs prevent route-table and authority drift.

## Desired End State

Humans can start with plain intents such as "where is this work?", "is this
safe to close?", or "recover this from artifacts." Agents can run one readiness
surface, route to a stage, know the authority boundary, and avoid treating local
progress as closure. Future contributors can distinguish authored docs from
installed plugin behavior.

## Migration Strategy

Use staged additions instead of a broad rewrite:

1. Add a setup/status front door.
2. Improve product-facing README and plugin manifest prompts.
3. Add runtime-authoring and process-exhaust doctrine.
4. Add consistency validation for HE names, routes, authority blocks, and
   generated product docs.
5. Add an observed usage pulse that reports activity without claiming route
   accuracy before truth-set governance exists.

## Smallest Reversible Step

Add documentation-only front-door/default-prompt updates plus a stale runtime
projection debugging note. This gives immediate feedback without changing route
behavior.

## Execution Phases

| Phase | Objective | Affected systems | Expected risk | Feedback expected | Stop or pivot condition | Can run in parallel | Validation requirements | Rollback conditions | Linear mapping | Agent-safe | Human review required |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Product front door | README, plugin manifest, default prompts | Low | Humans understand HE entrypoints without stage names | Product copy creates unsupported claims | yes | packaging, plugin validate, markdown checks | revert doc/manifest copy | parent + child 1 | yes | no |
| 2 | Setup/status command | scripts, README, validation docs | Medium | `he-doctor` reports ready/degraded/blocked with JSON | command overlaps existing ask control plane | no | focused script tests, packaging, plugin validate | remove command and docs | child 2 | assisted | yes |
| 3 | Runtime/artifact doctrine | docs, references, skill authoring guidance | Low | runtime-vs-authoring and process-exhaust rules are explicit | doctrine duplicates AGENTS-only policy | yes | markdown checks, deferred context index | revert reference/doc additions | child 3 | yes | no |
| 4 | Drift validation | validators, generated route docs, tests | Medium | route/product surfaces fail on drift | checker becomes too broad or flaky | no | new checker tests, routing map validation | disable release-mode gate | child 4 | assisted | yes |
| 5 | Observed usage pulse | reports, telemetry schema, docs | Medium | HE value is shown by observed usage, not invented metrics | metric wording implies quality without truth set | yes | telemetry schema/redaction tests | keep report experimental | child 5 | assisted | yes |

## Linear Mapping

Create one parent issue in the canonical `agent-skills` Linear project with five
children. Do not create a separate project. Do not route to the canceled
duplicate `agent-skills` project.

## Anti-Regression Constraints

- Do not broaden HE into a generic utility plugin.
- Do not claim cross-platform runtime support without validation.
- Do not move runtime requirements into repo-only `AGENTS.md`.
- Do not let default prompts imply closure without `he-eval-report`.
- Do not create metrics that imply route correctness before a labeled truth set.

## Eval Requirements

Expected eval artifact:

```text
.harness/evals/2026-05-11-agent-skills-he-product-front-door-runtime-contract-eval.md
```

Minimum gates:

- packaging hygiene
- routing map validation
- deferred context index check
- plugin validation
- focused tests for any new scripts
- strict audit for materially changed HE skills

## Success Criteria

- HE has a setup/status entrypoint or documented equivalent.
- Manifest/default prompts make HE usable without stage vocabulary.
- Runtime-vs-authoring doctrine is visible in shipped docs or references.
- `.harness` artifact policy distinguishes evidence from process exhaust.
- Naming/route/authority/product docs are checked or generated from canonical
  route data.
- Observed usage reporting avoids unsupported quality claims.

## Safe Rollback Conditions

Rollback by reverting docs/manifest/script/checker changes independently. If a
new checker is noisy, keep the local check but remove it from release-blocking
gates until fixed.

## Future-Agent Guidance

Treat EveryInc compound-engineering as comparative product evidence, not an
upstream source of truth. Copy product lessons, not breadth. HE's durable thesis
is closure proof, resumed work recovery, and evidence-bound routing.

## Related Systems

- `Plugins/harness-engineering/README.md`
- `Plugins/harness-engineering/.codex-plugin/plugin.json`
- `Plugins/harness-engineering/skills/he-router/SKILL.md`
- `Plugins/harness-engineering/references/**`
- `Plugins/harness-engineering/scripts/**`
- `.harness/linear/**`
- `.harness/evals/**`
