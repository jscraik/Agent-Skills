# Folded Skill Context

## Purpose
Keep HE routing compact without losing folded stage context. Folded names are compatibility and mode selectors, not default picker entries. Route folded names to the parent stage and load preserved context only if the mode changes inputs, validation, subagents, or output shape.

## Folded Stage Map

| Folded name | Parent stage | Mode | Preserved context |
| --- | --- | --- | --- |
| `he-ideate` | `he-brainstorm` | options | `fixtures/preserved-context/skills/team_automation/he-ideate/` |
| `he-deepen-spec` | `he-spec` | deepen spec | `fixtures/preserved-context/skills/team_automation/he-deepen-spec/` |
| `he-deepen-plan` | `he-plan` | deepen plan | `fixtures/preserved-context/skills/team_automation/he-deepen-plan/` |
| `he-refine` | `he-improve` | refinement | `fixtures/preserved-context/skills/team_automation/he-refine/` |
| old `he-compound` learning | `he-reinforce` | solved-problem capture and Project Brain learning | `fixtures/preserved-context/skills/team_automation/he-compound/` |
| `he-compound-refresh` | `he-reinforce` | refresh durable learning | `fixtures/preserved-context/skills/team_automation/he-compound-refresh/` |
| `he-prune-branches` | `he-router` | `agent-ops` branch hygiene | `fixtures/preserved-context/skills/team_automation/he-prune-branches/` |
| `he-tdd` | `he-work` | test-first | `fixtures/preserved-context/skills/team_automation/he-tdd/` |
| `he-technical-review` | `he-code-review` | technical critique | `fixtures/preserved-context/skills/code_quality_review/he-technical-review/` |
| `he-reliability-review` | `he-code-review` | reliability critique | `fixtures/preserved-context/skills/code_quality_review/he-reliability-review/` |

## Calling Rules

- Direct user mentions of a folded name must route to the parent stage, not the folded skill.
- Prefer the parent-stage command plus `mode: <folded mode>` unless the user needs a compatibility entrypoint.
- Do not summarize or trim away mode details for token budget reasons. Move long material into references and add it to this map or `deferred-context-index.md`.
- Keep branch pruning out of the HE parent-stage surface. Use `he-router` only to classify the request and hand off to `agent-ops` branch hygiene.
- Keep folded names available through router aliases and parent modes. Re-add a picker entry only for a concrete standalone use case.
- Preserve valid `ce-docs-review` behavior inside `he-spec` and `he-plan` as a
  lightweight document review/deepening pass. It should strengthen source
  coverage, contradictions, acceptance IDs, validation, sequencing, and handoff
  evidence without creating another default stage.

## Parent Responsibilities

- `he-brainstorm`: load `he-ideate` context for options, opportunity scanning, or direction comparison.
- `he-spec`: load `he-deepen-spec` context when hardening an existing spec or resolving contract contradictions.
- `he-plan`: load `he-deepen-plan` context when hardening an existing plan or strengthening sequencing and gates.
- `he-work`: load `he-tdd` context when the user asks for RED/GREEN, failing-test-first, regression-first, or test-first execution.
- `he-improve`: load `he-refine` context for browser-first or iterative artifact refinement.
- `he-code-review`: load `he-technical-review` or `he-reliability-review` context for deeper-than-readiness review.
- `he-reconcile`: own lifecycle-state recovery directly.
- `he-reinforce`: load old `he-compound` and `he-compound-refresh` context when preserving solved-problem capture, solution docs, or Project Brain learning.

## Preserved Compact Entry Point Lines

The 2026-05-08 goal-governor compaction retired older compatibility examples,
artifact-path reminders, and short output summaries from active HE skill
entrypoints. Meaningful context was moved into active HE references and output
contracts; stale compatibility fragments and duplicated summaries were not
retained as exact retired lines.

The 2026-05-13 HE productization pass also folded entrypoint prose from active
stage skills into references and contracts. The retained signal is this
disposition, not a copied fragment store.

Disposition:
- moved-to-reference: durable brainstorm artifact routing, review artifact
  inputs, accept/challenge/rework gates, Linear-vs-harness separation, plan
  contract intent, validation outcomes, traceability, direct critique, rollback,
  next handoff, slack policy, and blackboard delta.
- superseded: compact output summaries now covered by active skill output
  contracts.
- intentionally-discarded: truncated sentence fragments and duplicated prose
  that had no standalone operational value.

## Preserved Source Coverage And First-Principles Reframe Lines

The 2026-05-09 source-coverage and first-principles pass tightened several
active lifecycle entrypoints. The durable context was moved into the active
stage contracts, routing references, and validation requirements. The exact
retired line fragments are intentionally not preserved: several were partial
lines, stale descriptions, or redundant copies of contracts now expressed in
canonical skill entrypoints.

Disposition:
- moved-to-reference: survivor-selection approval, Project Brain refresh
  blocking, UI-plan routing, small active Linear sets, XP operating constraints,
  rollback-safe reframe staging, subtractive proof, and artifact validation.
- superseded: old one-line descriptions and partial numbered steps now covered
  by active skill descriptions and procedure sections.
- intentionally-discarded: incomplete fragments such as truncated numbered
  lines, duplicated validator phrasing, and obsolete path hints.

## Preserved Lifecycle Confidence Reframe Lines

The 2026-05-09 HE confidence hardening pass renumbered active lifecycle
entrypoint procedures so XP proof, release-eval confidence, and explicit
routing boundaries could sit in the hot path. The durable context now lives in
the active lifecycle review, spec, eval, Linear, heartbeat, reframe, and
strategy contracts. Exact retired line preservation is intentionally avoided
because the previous block mixed valid invariants with partial fragments,
duplicate steps, and stale route wording.

Disposition:
- moved-to-reference: non-CI readiness proof, content-shape classification,
  bounded behavior contracts, subtractive proof gates, agent-native audit
  triggers, validation evidence, small Linear active sets, heartbeat stop rules,
  phase-scoped commits, rollback-safe reframes, and strategy compression.
- superseded: duplicate procedure lines that were renumbered into active
  lifecycle skills.
- intentionally-discarded: truncated lines, repeated output field lists, and
  obsolete intermediate wording that no longer improves future execution.

## Preserved Phase Work And Git Staging Contract Lines

The 2026-05-13 phase-work and staging pass moved repeated staging/status
fields out of active HE skill entrypoints and into the shared
`git-staging-contract.md`, `lifecycle-exit-contract.md`, and
`he-phase-work` contract. The reusable obligations were moved; the exact
retired lines were not retained because most were output-field fragments or
duplicated heartbeat prose already represented by the active contracts.

Disposition:
- moved-to-reference: review artifact identity, lifecycle exit status,
  blackboard delta, live Linear blocker reporting, phase heartbeat scope checks,
  review gates, validation evidence, commit status, blockers, stop rules, and
  next wake-up handoff.
- superseded: repeated output schemas now covered by active skill output
  contracts.
- intentionally-discarded: broken fragments, repeated descriptions, and copied
  heading text that added cost without preserving unique operational meaning.

Relocation anchors required by the progressive-disclosure gate:
`validation`, `blackboard_delta`, `artifact_path`, `next_stage`,
Return `schema_version: 1` when structured, plus mode, side-effect class, severity-ranked findings, traceability, blockers, verdict, reproduction status, security review, behavior proof, work candidate, repeated-failure route, blackboard delta, and next handoff. Use `.harness/review/**.md` with Artifact Identity frontmatter for durable review artifacts.
artifacts, closure recommendation, follow-up work, blockers, next handoff, and
repeated-failure learning when applicable, residual risk, and next handoff.
risk, blackboard delta when durable state changes, and next handoff.
`live_linear_blocker` when expected live tracking is blocked. Bug work includes
Run approved Harness Engineering work through recurring, evidence-first phase wakeups with scope checks, review gates, and explicit stop rules before any local commit.
`blackboard_delta`, and evidence-tied `confidence`.
`retained_references`, `validation`, `handoff`, and `blocked_reason`.
phases, rollback, Linear mapping, eval proof, future-agent guardrails, and
`redaction_status`, `writes`, `blocked_reason`, and `handoff`.
`spec_path`, `acceptance_ids`, `handoff`, and evidence-tied `confidence`.
future-agent guidance, validation outcomes, evidence traceability, and direct
Return schema_version when structured. schema_version: 1, changed files, validation, blockers, rollback, next handoff, slack_policy, and blackboard_delta.
Apply the context-disposition policy: move important still-valid context to references, and intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.
references and index it in `../../references/deferred-context-index.md`.
Redact secrets; do not create cron workarounds for short thread follow-up. Apply the context-disposition policy: move important still-valid context to references, and intentionally discard stale, duplicated, unsafe, superseded, or low-signal text. Keep scope tight: start with 2-3 focused surfaces and expand only when the next heartbeat needs more context.

## Preserved He-Code-Review Productization Context

The 2026-05-13 productization pass compacted
`Plugins/harness-engineering/skills/he-code-review/SKILL.md` while keeping its
review policy in stage references. The active entrypoint now routes to the
policy index and shared HE contracts; the preserved line below anchors the
removed context for the progressive-disclosure relocation gate.

Diff, repo guidance, Linear issue, spec, plan, PR evidence, validation output.

Disposition:
- moved-to-reference: mode selection, artifact identity, repeated-failure
  routing, evidence ladder, plugin-hook review checks, gate selection, and
  first-principles review policy.
- superseded: repeated output-schema field lists now covered by active stage
  output contracts.
- intentionally-discarded: duplicate reference lists and stale budget-trimming
  language that no longer adds unique review behavior.

## Preserved He-Compound Productization Context

The 2026-05-13 productization pass folded
`Plugins/harness-engineering/skills/he-compound/SKILL.md` into the active
state-reconstruction and routing contracts. The preserved line below anchors
the removed entrypoint context for the progressive-disclosure relocation gate.

description: "Analyze session, repo, Linear, and harness evidence to refresh HE lifecycle state. Use when multi-stage HE work needs source-prompt coverage, resume routing, or earliest-stage recovery."

Disposition:
- moved-to-reference: lifecycle state reconstruction, source-prompt coverage,
  repeated-failure capture, Project Brain freshness, solution-capture
  eligibility, and earliest-stage routing.
- superseded: old compound stage naming now routes through the current
  reconcile/reinforce lifecycle surfaces.
- intentionally-discarded: duplicate gotcha lists and repeated reference
  inventories that are represented in the active contracts.

## Preserved He-Spec Smoke-Eval Hardening Lines

The 2026-05-12 he-spec smoke-eval hardening pass tightened the active entrypoint
for fail-closed placeholder handling, source-evidence naming, replacement
artifact guidance, and packaging asset references. The durable context was moved
to the he-spec entrypoint and artifact contracts; exact retired fragments are
not retained because they are incomplete and would teach future agents to value
line preservation over meaning.

Disposition:
- moved-to-reference: spec-before-plan routing, evidence-first exploration,
  bounded surface loading, write-approval awareness, validation, observability,
  rollback/supersession, Linear Acceptance Traceability, blackboard delta, and
  artifact contract routing.
- intentionally-discarded: sentence fragments and partial indentation that no
  longer carry unique operational meaning.

## Discarded He-Router Productization Prompt Rot

The 2026-05-15 HE productization refinement pass removed duplicated tail text
from Plugins/harness-engineering/skills/he-router/SKILL.md. The valid
context-disposition rule already exists above and in the active router; the
closure-vs-mutation concern now routes to closure-mutation-contract.md.

Removed duplicate/dangling router text:

- references with a clear route.
- Apply the context-disposition policy by moving important still-valid context to
  references and intentionally discarding stale, duplicated, unsafe, superseded,
  or low-signal text.

Disposition:
- moved-to-reference: closure and mutation separation now lives in
  closure-mutation-contract.md.
- superseded: context-disposition wording already exists in the folded-context
  policy above.
- intentionally-discarded: dangling sentence fragments and duplicated prompt
  maintenance prose that increased hot-path cost without adding behavior.
