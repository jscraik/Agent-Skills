# Harness Engineering Deferred Context Index

HE active files must stay real plugin-owned text. Historical snapshots live
under `fixtures/**` or a dedicated archive reference; active paths must not
symlink into archives.

Use this index only when a compact stage file defers context. Do not paste
active procedure bodies here. Move durable behavior to a stage reference, link
the reference below, and let validators catch stale duplicated procedure text.

## Runtime Reference Map

- Routing and domain context:
  - `references/routing-map.json`
  - `references/deterministic-stage-routing.md`
  - `references/domain-model-routing.md`
  - `references/domain-context-contract.md`
  - `references/ubiquitous-language-contract.md`
  - `references/domain-model-production-contract.md`
  - `references/design-complexity-contract.md`
  - `references/gate-selection-contract.md`
  - `references/first-principles-contract.md`
  - `references/plugin-hook-capability-contract.md`
- Lifecycle, artifact, slice, and tracker gates:
  - `references/stage-context-contract.md`
  - `references/lifecycle-exit-contract.md`
  - `references/stage-arc-boundary-contract.md`
  - `references/spec-plan-runtime-boundary-contract.md`
  - `references/git-staging-contract.md`
  - `references/artifact-routing-contract.md`
  - `references/artifact-classification-and-traceability.md`
  - `references/execution-slice-contract.md`
  - `references/linear-tracker-gate.md`
  - `references/coding-harness-command-bridge.md`
  - `references/goal-continuity.md`
- Intake and evidence:
  - `references/qa-intake-routing.md`
  - `references/source-prompt-coverage-contract.md`
  - `references/session-evidence-contract.md`
  - `references/session-evidence-skillify-triage.md`
  - `references/session-evidence-trace-context.md`
  - `references/session-evidence-extraction.md`
  - `references/codex-provenance-contract.md`
  - `references/pr-safety-trace-contract.md`
- Review, ideation, and agent-native lenses:
  - `references/bluf-review-contract.md`
  - `references/visual-reference-contract.md`
  - `references/agent-native-audit-scorecard.md`
  - `references/brainstorm-topic-coverage-contract.md`
  - `references/document-review-finding-tiers.md`
  - `references/specialist-skill-steering-contract.md`
  - `references/pragmatic-programmer-review-contract.md`
  - `references/xp-operating-contract.md`
- Skill improvement:
  - `references/skill-improvement-loop.md`
  - `references/plugin-eval-confidence-contract.md`
- Delegation:
  - `references/subagent-routing.md`
  - `references/subagent-call-contract.md`
- Folded compatibility:
  - `references/folded-skill-context.md`

## 2026-05-24 HE Plan Hot-Path Budget Disposition

The `he-plan` entrypoint was compacted to stay under the 240-line hot-path hard
budget. The removed lines remain preserved here as reference context rather than
runtime prompt ballast:

Professional confidence review output must use these exact headings unless the
review blocks before content analysis:

1. Initial Confidence Assessment
2. Plan Intent & Scope Check
3. Issues and Loopholes Found
4. Evidence Check
5. Recommended Fixes
6. Revised Plan
7. Associated Spec Update
8. Iterative Re-review Loop
9. Final Confidence Report
10. Before / After Impact Table
11. Infographic / `$imagegen` Artifact when requested or explicitly required

Example route: for JSC-246, inspect `.harness/specs/account-settings.md` and
Linear JSC-246, then write the plan under `.harness/plan/` with validation and
rollback. Assets are packaging-only; durable plans and diagrams belong in repo
artifacts or references. Reference loading remains demand-driven: plan artifact,
handoff, depth, review, test strategy, visual, runtime boundary, subagent,
domain, ubiquitous language, BLUF, and deferred context contracts should be
opened only when the selected slice proves they matter.

## Conditional Loading Map

Load references by trigger instead of by habit:

| Stage or condition | Load | Expected proof |
| --- | --- | --- |
| Any stage accepts a task, writes durable docs, mutates files, schedules continuation, claims closure, or hands off | `references/stage-context-contract.md`, `references/stage-arc-boundary-contract.md`, `references/lifecycle-exit-contract.md`, `references/git-staging-contract.md` | compact stage context plus left/active/right arc boundary, coding/testing lens status, exit status, and git staging status for current-turn files |
| Spec or plan can route implementation, closure, runtime claims, or resume state | `references/spec-plan-runtime-boundary-contract.md` | requested depth, approved boundary, proof boundary, runtime persistence, live refresh, and coding/testing lenses |
| Non-trivial durable HE artifact is operator-facing | `references/bluf-review-contract.md` | Command Summary with one opening BLUF paragraph, No-Fog Gate, or compact not-applicable reason |
| Non-trivial artifact has flow, dependency, boundary, state, validation, rollback, UI, media, or source-of-truth complexity | `references/visual-reference-contract.md` | Mermaid/table/image reference, or compact not-needed reason |
| Stage choice is ambiguous | `references/routing-map.json`, `references/deterministic-stage-routing.md`, `references/interactive-steering-contract.md` | selected stage or one blocking question |
| `.harness` artifacts determine scope | `references/artifact-classification-and-traceability.md`, `references/artifact-routing-contract.md` | content-shape classification and Artifact Identity status |
| Non-trivial tracked work | `references/linear-tracker-gate.md` | resolved, created, blocked, or user-opted-out tracker status |
| Existing tracked plan or Linear-backed slice is consumed | `references/linear-delta-capture-gate.md` | delta admitted, rejected, or blocked before scope changes |
| Original prompt, external workflow, old manual method, or plugin comparison is the baseline | `references/source-prompt-coverage-contract.md` | source_prompt_status, evidence_depth, coverage_scope, not_inspected, repo-specific drift signals, authority limits, downstream_confidence, and next route |
| Artifact, handoff, or PR cites Codex sessions, session collector, rollout, transcript, OTEL, thread ID, turn ID, or trace ID | `references/session-evidence-trace-context.md`, `references/codex-provenance-contract.md`, `references/pr-safety-trace-contract.md` | he_trace_id, provenance source/status, redaction status, public-safe trace fields, proof limits, and no raw sensitive local IDs or paths in public text |
| Coding-harness-managed repo | `references/coding-harness-command-bridge.md`, `references/execution-slice-contract.md` | command evidence or explicit blocked bridge fields |
| Stage could load broad domain, strategy, reframe, Linear, security, specialist, or eval gates | `references/gate-selection-contract.md` | smallest gate profile, required contracts, skipped contracts, and minimum proof |
| Stage would copy external process, add lifecycle surface area, expand governance, or preserve complexity without proven HE-specific failure evidence | `references/first-principles-contract.md` | first_principles_check with verified failure, smallest mechanism, decision type, rejected analogy, and proceed/ask/defer/reject/delete outcome |
| Plugin hook, `hooks/hooks.json`, `.codex-plugin/plugin.json` hook declaration, or hook-enforced guardrail appears in scope | `references/plugin-hook-capability-contract.md` | plugin_hook_capability_check with feature gate status, fallback path, portability status, side-effect class, lifecycle authority, and outcome |
| Domain-specific knowledge could sharpen output | `references/specialist-skill-steering-contract.md` | chosen specialist, skipped reason, or blocker |
| Ubiquitous language, glossary conflicts, domain interview, or term drift shape behavior | `references/domain-model-routing.md`, `references/domain-context-contract.md`, `references/ubiquitous-language-contract.md`, `references/interactive-steering-contract.md` | canonical terms, avoided aliases, language file, one-question-at-a-time steering status, and ADR threshold outcome |
| User choice affects downstream scope | `references/interactive-steering-contract.md` | asked choice, headless assumption, or blocked state |
| Product compression is the blocker | `references/agent-native-compression-contract.md` | subtractive proof, fresh-agent eval, and ablation gate |
| HE plugin confidence or budget quality is claimed | `references/plugin-eval-confidence-contract.md` | static plugin-eval result, rooted handle proof, release eval lane, and cache-sync status |
| Lifecycle stage risks ceremony, broad scope, weak feedback, or unclear value | `references/xp-operating-contract.md` | smallest valuable slice, feedback signal, slack policy, or blocked reason |
| Review or closure touches agent-facing workflow surfaces | `references/agent-native-audit-scorecard.md` | scorecard findings or not-applicable reason |
| Solved-problem evidence should persist | `references/solution-capture-contract.md` | refreshed existing solution or new `.harness/solutions/**` capture |

## Stage Reference Map

`he-brainstorm`:

- `skills/he-brainstorm/references/brainstorm-workflow-details.md`
- `skills/he-brainstorm/references/discovery-interview.md`
- `skills/he-brainstorm/references/requirements-artifact-guide.md`
- `skills/he-brainstorm/references/visual-communication.md`
- `references/brainstorm-topic-coverage-contract.md`
- Preserved context: Do not turn brainstorming into execution. Do not remove important context for budget trimming; move deep context to references with a clear route.
Do not turn brainstorming into execution. Do not remove important context for budget trimming; move deep context to references with a clear route.
Do not turn brainstorming into execution. Do not remove important context for
budget trimming; move deep context to references with a clear route.

`he-spec`:

- `Plugins/synaipse-harness/references/upstream/harness-engineering/he-spec-doctrine.md`
- `Plugins/synaipse-harness/references/upstream/harness-engineering/skills/he-spec/autoresearch-2026-05-02.md`
- `Plugins/synaipse-harness/references/upstream/harness-engineering/skills/he-spec/codex-and-session-evidence.md`
- `Plugins/synaipse-harness/references/upstream/harness-engineering/skills/he-spec/spec-artifact-contract.md`
- `Plugins/synaipse-harness/references/upstream/harness-engineering/skills/he-spec/spec-mode-rules.md`

`he-plan`:

- `references/he-plan-doctrine.md`
- `skills/he-plan/references/codex-plan-mode.md`
- `skills/he-plan/references/plan-artifact-contract.md`
- `skills/he-plan/references/planning-depth.md`
- `skills/he-plan/references/deepening-review.md`
- `skills/he-plan/references/test-strategy.md`
- `skills/he-plan/references/visual-communication.md`
- Moved-to-reference, 2026-05-16: compressed entrypoint planning detail is
  preserved in the references above and governed by the context-disposition
  policy instead of being duplicated in `SKILL.md`.

`he-work`:

- `skills/he-work/references/work-execution-contract.md`
- `skills/he-work/references/codex-execution-lessons.md`
- `skills/he-work/references/handoff-and-shipping.md`
- `skills/he-work/references/execution-modes.md`

`he-code-review`:

- `skills/he-code-review/references/review-policy-index.md`
- `skills/he-code-review/references/review-loop-patterns.md`
- `skills/he-code-review/references/review-mode-contract.md`
- `references/pragmatic-programmer-review-contract.md`

`he-eval-report`:

- `skills/he-eval-report/references/eval-report-contract.md`
- `skills/he-eval-report/references/eval-report-template.md`
- `skills/he-eval-report/references/eval-report-schema.json`
- `skills/he-eval-report/references/drift-taxonomy.md`
- `skills/he-eval-report/references/linear-completion-policy.md`
- `references/source-prompt-coverage-contract.md`

`he-strategy`:

- `skills/he-strategy/references/strategy-output-contract.md`
- `skills/he-strategy/references/source-prompt-preservation.md`
- `references/source-prompt-coverage-contract.md`
- `references/pragmatic-programmer-review-contract.md`
- Moved-to-reference, 2026-05-16: compressed strategy detail is preserved in
  the stage references above and loaded only when the active strategy task
  needs it.

`he-reframe`:

- `skills/he-reframe/references/reframe-program-contract.md`
- `skills/he-reframe/references/source-prompt-preservation.md`
- `references/source-prompt-coverage-contract.md`

`he-linear-plan`:

- `skills/he-linear-plan/references/linear-plan-output-contract.md`
- `skills/he-linear-plan/references/source-prompt-preservation.md`
- `references/source-prompt-coverage-contract.md`
- Moved-to-reference, 2026-05-16: compressed Linear planning detail is
  preserved in the stage references above instead of expanding the entrypoint.

`he-phase-work`:

- `skills/he-phase-work/references/phase-gate-contract.md`
- `skills/he-phase-work/references/contract.yaml`

## Historical Context Policy

Deferred context exists to keep meaningful, still-valid HE knowledge reachable
without loading it by default. It is not a landfill for every line removed from
`SKILL.md`.

When compacting a stage entrypoint, classify removed material:

- `moved-to-reference`: valid reusable behavior preserved in a stage reference,
  shared contract, or fixture.
- `superseded`: replaced by a newer compressed rule, route, contract, or
  validator.
- `intentionally-discarded`: stale, duplicated, unsafe, inappropriate,
  contradicted by current HE guidance, or no longer part of the shipped
  contract.
- `not-context`: formatting, navigation, repeated prose, examples with no
  durable value, or low-signal explanation.

Only the `moved-to-reference` disposition belongs in this index. The other
dispositions may be mentioned in review notes or change summaries when useful,
but they should not be pasted into deferred context.

## Preserved Entry Point Lines

Preserved entrypoint lines from earlier compression rounds are intentionally
stored in archival fixtures and stage-specific preservation references, not in
this active router index.

Authoritative preservation locations:

- `fixtures/budget-archive/**`
- `fixtures/preserved-context/**`
- stage-specific source-prompt preservation references

Historical compact-entrypoint lines from prior compression passes belong in:

- `fixtures/budget-archive/**`
- `fixtures/preserved-context/**`
- stage-specific source-prompt preservation references

Do not duplicate active `SKILL.md` procedure text here. If future agents need
an old line for migration evidence, link the historical fixture path and state
why it matters instead of copying the line.

## Drift Signals

- The same reference appears twice under different labels.
- Preserved text copies active stage procedure instead of linking archival context.
- A preserved line contradicts the current stage entrypoint.
- This file grows faster than the referenced stage contracts.
- A validator, eval, or skill entrypoint treats this index as source of truth
  instead of a context router.

## Retired Entry Point Audit Notes

The 2026-05-08 artifact-traceability pass retired several oversized stage
entrypoint paragraphs. Their audit value is preserved by active stage diffs,
the relevant `skills/**/references/source-prompt-preservation.md` files, and
fixtures. Keep this index as a router only; do not paste retired procedure text
back into this file.

## 2026-05-12 BLUF Productization Disposition Notes

The BLUF productization pass compressed several stage entrypoints. Meaningful
behavior was moved to stage references, artifact contracts, and the BLUF review
contract. BLUF now means one opening Bottom Line Up Front paragraph, not a
section-by-section template.

Disposition:

- `moved-to-reference`: durable artifact routing, Linear mutation gates,
  closure proof, review shape, and strategy/reframe/Linear output rules are
  preserved in the Stage Reference Map above and the linked stage references.
- `superseded`: exact numbered procedure fragments were replaced by compact
  stage procedures plus shared BLUF, visual-reference, source-prompt, Linear,
  and lifecycle contracts.
- `intentionally-discarded`: incomplete line fragments and prompt snippets that
  no longer form valid operational guidance are not preserved here.
- `not-context`: numbering artifacts and partial copied lines are omitted.

## 2026-05-16 HE Stage Compression Evidence

The local skill-review hardening pass compressed several HE stage entrypoints
while preserving their reusable procedures in stage references and shared
contracts. The exact historical lines below are retained as move evidence for
the progressive-disclosure gate; current agents should follow the linked
contracts, not this audit note.

Moved-to-reference evidence is archived under `fixtures/budget-archive/**`
and `fixtures/preserved-context/**`. This active router keeps only the current
reference destinations below.

Moved-to-reference evidence:

Produce one of: strategy memo, architecture recommendation, refactor strategy,
Strategy artifacts are cognition compression, not ceremony. Turn verified repo
Write a dated `.harness/linear/**-linear-plan.md` artifact or return

Current routes:

- he-plan contracts:
  `Plugins/synaipse-harness/references/upstream/harness-engineering/skills/he-plan/plan-artifact-contract.md`,
  `Plugins/synaipse-harness/references/upstream/harness-engineering/skills/he-plan/planning-depth.md`,
  and
  `Plugins/synaipse-harness/references/upstream/harness-engineering/skills/he-plan/post-plan-handoff.md`.
- he-strategy contracts:
  `Plugins/synaipse-harness/references/upstream/harness-engineering/skills/he-strategy/strategy-output-contract.md`
  and the shared first-principles/domain context contracts.
- he-linear-plan contracts:
  `Plugins/synaipse-harness/references/upstream/harness-engineering/skills/he-linear-plan/linear-plan-output-contract.md`,
  `Plugins/synaipse-harness/references/upstream/harness-engineering/skills/he-linear-plan/linear-filing-rule.md`,
  and
  `Plugins/synaipse-harness/references/upstream/harness-engineering/closure-mutation-contract.md`.

## 2026-05-18 HE Entrypoint Follow-Up Disposition

The PR #181 follow-up kept `he-linear-plan`, `he-plan`, and `he-strategy`
entrypoints compact after branch stacking moved their detailed procedures into
stage references. The removed hot-path lines are not discarded; they are routed
through the contracts below so future agents can load deep context deliberately.

`he-linear-plan` preserved context: Linear is execution state; `.harness`
is cognition and proof. Convert approved HE cognition into the smallest useful
Linear execution slice with destination proof, duplicate checks, project/cycle
evidence, labels, priority, dependencies, eval gates, rollback gates, human and
agent routes, and explicit `linear_mutation_status`. Ready-to-create payloads
are not applied Linear changes. Mutate Linear only after explicit post-plan
approval, known destination, and a small confirmed object set. If destination,
duplicate state, decision evidence, ADR readiness, or live tooling is missing,
return `needs_human_triage`, `Later`, `Do Not Create`, or
`linear_mutation_status: blocked` instead of creating tracker volume. Refuse
one-issue-per-observation requests and collapse observations into the smallest
useful milestone, parent issue, bug issue, or sub-issue set. For non-trivial
Linear plans, apply BLUF and visual-reference contracts, include
`schema_version: 1`, `selected_stage: he-linear-plan`, evidence traceability,
Target Linear Destination, Existing Project Match, Now/Next/Later/Do Not Create,
`decision_artifact_status`, `required_confirmation`, `live_linear_blocker`,
and git staging status when local artifacts are written. Bug work keeps
`issue_type: bug`, repro, expected and actual behavior, affected surface,
severity, and validation evidence. Do not create projects, labels, issue sets,
dependencies, or status updates without explicit approval; connector or auth
failure returns a blocked payload with exact object assumptions.
Moved line evidence:
Linear is execution state; `.harness` is cognition and proof. Turn approved HE

Disposition:

- `he-linear-plan` moved-to-reference: Linear output shape, filing rules,
  source-prompt preservation, closure and mutation boundaries, subagent policy,
  and package checks live in
  `Plugins/synaipse-harness/references/upstream/harness-engineering/skills/he-linear-plan/**`,
  `references/closure-mutation-contract.md`, and
  `references/subagent-call-contract.md`.
  Relocation evidence:
Use when approved `.harness` cognition needs Linear routing: target project,
- `he-plan` moved-to-reference: plan artifact shape, planning depth,
  post-plan handoff, source evidence, validation, rollback, enforcement
  contracts, and generated-artifact checks live in
  `Plugins/synaipse-harness/references/upstream/harness-engineering/skills/he-plan/**`
  and the shared lifecycle contracts.
  Relocation evidence:
Plans are execution contracts, not chat checklists. They preserve source
- `he-strategy` moved-to-reference: strategy output shape, first-principles
  framing, domain context, migration phase selection, rollback posture, and
  next-stage routing live in `references/skills/he-strategy/**` and the
  shared source-prompt and lifecycle contracts.
  Relocation evidence:
Strategy artifacts are cognition compression, not ceremony. Turn verified repo

## 2026-05-18 PR 175 Main Reconciliation Evidence

The PR 175 main reconciliation preserved folded Harness Engineering stage
context in the shared reference map and folded-context contracts. The exact
historical lines below are retained only as move evidence for the
progressive-disclosure gate; current agents should follow active stage
references, routing maps, and shared contracts.

Moved-to-reference evidence:

description: "Generate closure-grade HE eval and drift proof for one execution slice. Use when Linear, milestone, or source-prompt closure needs validation evidence."
description: "Plan and run approved Harness Engineering phase work with a 10-minute heartbeat, evidence checkpoints, review gates, staging rules, tracker-update boundaries, and safe continuation rules. Use when a bounded plan, issue, or PR needs recurring phase execution without autonomous closure."
description: "Coordinate approved Harness Engineering phase work with a 10 minute he-heartbeat scheduler, per-phase he-work execution, phase gates, Linear updates, scoped git staging, and final eval/reinforcement/reconciliation closeout. Use when an approved plan needs recurring phase execution with reviewable evidence."
description: "Create bounded Harness Engineering execution plans from approved specs or issue slices. Use when work needs ordered implementation units, explicit scope boundaries, rollback posture, traceability, and validation gates before code changes."
description: "Create evidence-backed HE reframe migration programs. Use when structural drift, routing ambiguity, or source-prompt gaps need phased rollback-safe execution."
description: "Create bounded, evidence-backed Harness Engineering specs from approved intent. Use when a selected issue, milestone, reframe phase, or execution slice needs acceptance criteria, traceability, risk gates, and validation boundaries before planning or implementation."
