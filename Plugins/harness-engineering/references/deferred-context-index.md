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
  - `references/domain-model-production-contract.md`
  - `references/design-complexity-contract.md`
  - `references/gate-selection-contract.md`
  - `references/first-principles-contract.md`
  - `references/plugin-hook-capability-contract.md`
- Lifecycle, artifact, slice, and tracker gates:
  - `references/stage-context-contract.md`
  - `references/lifecycle-exit-contract.md`
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
- Review, ideation, and agent-native lenses:
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

## Conditional Loading Map

Load references by trigger instead of by habit:

| Stage or condition | Load | Expected proof |
| --- | --- | --- |
| Any stage writes durable docs, mutates files, or hands off | `references/stage-context-contract.md`, `references/lifecycle-exit-contract.md` | compact stage context plus exit status |
| Stage choice is ambiguous | `references/routing-map.json`, `references/deterministic-stage-routing.md`, `references/interactive-steering-contract.md` | selected stage or one blocking question |
| `.harness` artifacts determine scope | `references/artifact-classification-and-traceability.md`, `references/artifact-routing-contract.md` | content-shape classification and Artifact Identity status |
| Non-trivial tracked work | `references/linear-tracker-gate.md` | resolved, created, blocked, or user-opted-out tracker status |
| Existing tracked plan or Linear-backed slice is consumed | `references/linear-delta-capture-gate.md` | delta admitted, rejected, or blocked before scope changes |
| Original prompt, external workflow, old manual method, or plugin comparison is the baseline | `references/source-prompt-coverage-contract.md` | source_prompt_status, evidence_depth, coverage_scope, not_inspected, repo-specific drift signals, authority limits, downstream_confidence, and next route |
| Coding-harness-managed repo | `references/coding-harness-command-bridge.md`, `references/execution-slice-contract.md` | command evidence or explicit blocked bridge fields |
| Stage could load broad domain, strategy, refactor, Linear, security, specialist, or eval gates | `references/gate-selection-contract.md` | smallest gate profile, required contracts, skipped contracts, and minimum proof |
| Stage would copy external process, add lifecycle surface area, expand governance, or preserve complexity without proven HE-specific failure evidence | `references/first-principles-contract.md` | first_principles_check with verified failure, smallest mechanism, decision type, rejected analogy, and proceed/ask/defer/reject/delete outcome |
| Plugin hook, `hooks/hooks.json`, `.codex-plugin/plugin.json` hook declaration, or hook-enforced guardrail appears in scope | `references/plugin-hook-capability-contract.md` | plugin_hook_capability_check with feature gate status, fallback path, portability status, side-effect class, lifecycle authority, and outcome |
| Domain-specific knowledge could sharpen output | `references/specialist-skill-steering-contract.md` | chosen specialist, skipped reason, or blocker |
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

`he-spec`:

- `references/he-spec-doctrine.md`
- `skills/he-spec/references/autoresearch-2026-05-02.md`
- `skills/he-spec/references/codex-and-session-evidence.md`
- `skills/he-spec/references/spec-artifact-contract.md`
- `skills/he-spec/references/spec-mode-rules.md`

`he-plan`:

- `references/he-plan-doctrine.md`
- `skills/he-plan/references/codex-plan-mode.md`
- `skills/he-plan/references/plan-artifact-contract.md`
- `skills/he-plan/references/planning-depth.md`
- `skills/he-plan/references/deepening-review.md`
- `skills/he-plan/references/test-strategy.md`
- `skills/he-plan/references/visual-communication.md`

`he-work`:

- `skills/he-work/references/work-execution-contract.md`
- `skills/he-work/references/codex-execution-lessons.md`
- `skills/he-work/references/handoff-and-shipping.md`
- `skills/he-work/references/execution-modes.md`

`he-fix-bugs`:

- `skills/he-fix-bugs/references/contract.yaml`
- `references/session-evidence-contract.md`
- Preserved compact context: description: "WHAT: Diagnose and fix HE test, QA, CI, incident, or regression failures. Use when reproduction and validation are required."
description: "WHAT: Diagnose and fix HE test, QA, CI, incident, or regression failures. Use when reproduction and validation are required."
- Preserved compact context: Reproduce first; inspect changed path; patch narrowly; validate exact failure path. When the same failure class recurs, record the root-cause learning and durable fix surface.
Reproduce first; inspect changed path; patch narrowly; validate exact failure path. When the same failure class recurs, record the root-cause learning and durable fix surface.

`he-heartbeat`:

- `skills/he-heartbeat/references/heartbeat-policy-index.md`
- `references/lifecycle-exit-contract.md`
- Preserved compact context: description: "WHAT: Automate HE wakeups, monitoring, until-green checks, and follow-through. Use when later thread continuation or goal-aware scheduling is needed."
description: "WHAT: Automate HE wakeups, monitoring, until-green checks, and follow-through. Use when later thread continuation or goal-aware scheduling is needed."
- Preserved compact context: Prefer thread heartbeat for this conversation; encode stop criteria; avoid duplicate automations. When `/goal` is active or requested, keep the goal as the persistent objective and the heartbeat as the scheduler with live checks and stop rules.
Prefer thread heartbeat for this conversation; encode stop criteria; avoid duplicate automations. When `/goal` is active or requested, keep the goal as the persistent objective and the heartbeat as the scheduler with live checks and stop rules.
- Preserved compact context: For GitHub PR sweeps, keep the loop concrete: identify the PR set, re-check GitHub truth, inspect CircleCI/job logs for failing checks, inspect CodeRabbit/Codex review threads, and route each wake-up to the smallest safe `he-code-review` or `he-work` follow-up. Use `git-project-triage` as a helper role only when it is available in the Codex agent manifest; if the role is missing, continue inline and report that delegation gap.
For GitHub PR sweeps, keep the loop concrete: identify the PR set, re-check GitHub truth, inspect CircleCI/job logs for failing checks, inspect CodeRabbit/Codex review threads, and route each wake-up to the smallest safe `he-code-review` or `he-work` follow-up. Use `git-project-triage` as a helper role only when it is available in the Codex agent manifest; if the role is missing, continue inline and report that delegation gap.
- Preserved compact context: Redact secrets; do not create cron workarounds for short thread follow-up. Do not remove important context for budget trimming; move deep context to references.
Redact secrets; do not create cron workarounds for short thread follow-up. Do not remove important context for budget trimming; move deep context to references.

`he-code-review`:

- `skills/he-code-review/references/review-policy-index.md`
- `skills/he-code-review/references/review-loop-patterns.md`
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
- Preserved compact context: he-strategy synthesizes evidence into strategic direction but does not grant implementation permission; preserve assumptions, confidence limits, coverage gaps, and downstream admission gates.
Strategy artifacts are cognition compression, not ceremony. They should make a

`he-refactor`:

- `skills/he-refactor/references/refactor-program-contract.md`
- `skills/he-refactor/references/source-prompt-preservation.md`
- `references/source-prompt-coverage-contract.md`
- Preserved compact context: he-refactor turns validated strategy/spec findings into scoped refactor programs with source evidence, authority limits, validation gates, rollback points, and downstream traceability.
new abstraction.

`he-linear-plan`:

- `skills/he-linear-plan/references/linear-plan-output-contract.md`
- `skills/he-linear-plan/references/source-prompt-preservation.md`
- `references/source-prompt-coverage-contract.md`
- Preserved compact context: he-linear-plan converts selected HE work into a small Now/Next/Later/Do Not Create Linear execution plan with dependencies, eval gates, rollback gates, payload status, closure proof, and explicit mutation authority.
2. If the user asks for architecture review, strategy, refactor program, spec,

`he-phase-heartbeat`:

- `skills/he-phase-heartbeat/references/phase-gate-contract.md`
- `skills/he-phase-heartbeat/references/contract.yaml`
- Preserved compact context: he-phase-heartbeat schedules approved phase continuation only after live state, collector evidence, scope, review gates, validation, stop rules, and commit authority are proven; cadence is not authority.
# Harness Engineering Phase Heartbeat

## Historical Context Policy

Historical compact-entrypoint lines from prior compression passes belong in:

- `fixtures/budget-archive/**`
- `fixtures/preserved-context/**`
- stage `references/source-prompt-preservation.md` files

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

The 2026-05-10 Linear and recurrence routing pass tightened several stage
frontmatter descriptions and moved mutation/recurrence details into the active
stage bodies plus eval fixtures. The following retired trigger and boundary
lines are preserved only as audit context for progressive-disclosure validation:

```text
description: "Analyze HE options and choose survivor routes. Use when direction is unsettled before spec or plan work."
description: "Review HE diffs for closure risk. Use when PR, commit, or readiness evidence is needed."
Use when handling PRs, branches, diffs, commits, readiness, and disputed review feedback.
Return schema_version when structured. schema_version: 1, severity findings, traceability, blockers, verdict, reproduction_status, security_review, real_behavior_proof, work_candidate, repeated_failure, blackboard_delta, next handoff, repeated context-feedback candidates. If writing a durable review artifact, use `.harness/review/**.md` with Artifact Identity frontmatter.
Return schema_version when structured. Stage map, active owner, blockers, next action, blackboard_delta, retained references, `.harness/solutions/**` capture status, and Project Brain status.
description: "Debug validated HE defects narrowly. Use when evidence proves a bug and scope must stay bounded."
description: "Create bounded HE follow-up checkpoints. Use when work must resume later with stop rules."
description: "Review and improve HE skills from evidence. Use when eval, review, or usage findings require changes."
description: "Convert approved HE cognition into a small Linear execution plan. Use when strategy, refactor, plan, or source-prompt evidence needs scoped tracking."
backlog noise or accidental Linear mutation.
Do not use to create Linear objects immediately, generate strategy, write
refactor programs, produce specs/plans, implement work, or validate closure.
   or mutation authority cannot be proven.
15. Include ready-to-create payloads without mutating Linear.
mutate Linear, create projects, create labels, or expand the active issue set
from this skill. Do not remove important context for budget trimming; move deep
context to references.
Generate ready-to-create Linear plans only. Do not create initiatives, projects,
milestones, issues, dependencies, labels, or status updates without explicit
post-plan approval.
description: "Plan approved HE phase heartbeats. Use when recurring phase execution needs gates and stop conditions."
description: "Create traceable HE execution plans. Use when approved intent needs implementation units and validation gates."
Use when after approved spec/issue; do non-mutating inspection before planning.
description: "Analyze and route HE lifecycle requests. Use when stage, artifact path, or specialist route is uncertain."
description: "Create evidence-backed HE specs. Use when approved intent needs acceptance criteria before implementation."
Use when requirements are needed before plan/work; Explore first and ask second.
4. Resolve or block the Linear tracker; run the Linear Delta Capture Gate for existing tracked plans before admitting changed Linear work into scope.
description: "Build approved HE plan slices. Use when a bounded plan authorizes code changes and validation."
```
