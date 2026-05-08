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
  - `references/design-complexity-contract.md`
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
  - `references/session-evidence-contract.md`
  - `references/session-evidence-skillify-triage.md`
  - `references/session-evidence-trace-context.md`
- Review, ideation, and agent-native lenses:
  - `references/agent-native-audit-scorecard.md`
  - `references/brainstorm-topic-coverage-contract.md`
  - `references/document-review-finding-tiers.md`
  - `references/specialist-skill-steering-contract.md`
  - `references/pragmatic-programmer-review-contract.md`
- Skill improvement:
  - `references/skill-improvement-loop.md`
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
| Coding-harness-managed repo | `references/coding-harness-command-bridge.md`, `references/execution-slice-contract.md` | command evidence or explicit blocked bridge fields |
| Domain-specific knowledge could sharpen output | `references/specialist-skill-steering-contract.md` | chosen specialist, skipped reason, or blocker |
| User choice affects downstream scope | `references/interactive-steering-contract.md` | asked choice, headless assumption, or blocked state |
| Product compression is the blocker | `references/agent-native-compression-contract.md` | subtractive proof, fresh-agent eval, and ablation gate |
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

`he-strategy`:

- `skills/he-strategy/references/strategy-output-contract.md`
- `skills/he-strategy/references/source-prompt-preservation.md`
- `references/pragmatic-programmer-review-contract.md`

`he-refactor`:

- `skills/he-refactor/references/refactor-program-contract.md`
- `skills/he-refactor/references/source-prompt-preservation.md`

`he-linear-plan`:

- `skills/he-linear-plan/references/linear-plan-output-contract.md`
- `skills/he-linear-plan/references/source-prompt-preservation.md`

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

## Preserved Entry Point Lines

The 2026-05-08 artifact-traceability pass retired several oversized stage
entrypoint paragraphs. Their audit value is preserved by the active stage
diffs and, where long-form source context is needed, by the relevant
`skills/**/references/source-prompt-preservation.md` or `fixtures/**` files.

Exact retired lines preserved for progressive-disclosure audit:

```text
description: "WHAT: Analyze fuzzy HE intent into options and handoff. Use when behavior, success criteria, Linear, or evidence is ambiguous."
Use before spec writing when intent is fuzzy; preserve Context preservation and assign `scope_tier`.
Explore first; require an identifiable subject before dispatching ideation or writing artifacts; separate evidence from guesses; before writing durable docs choose the routed `.harness` path from the artifact routing contract; for durable tracked work resolve/create the Linear issue before handoff; in coding-harness-managed repos load the command bridge and record the Harness transition.
For `he-ideate`, ground in repo/Linear/session evidence and current web research unless explicitly skipped, apply the specialist skill steering contract when a proven knowledge domain can improve option quality, derive topic axes from the evidence, generate many candidates internally, critique all candidates, run bounded coverage recovery for missing high-value axes, surface only warranted survivors with rejection reasons, then apply the interactive steering contract when survivor selection would shape the downstream spec, plan, Linear work, or implementation slice.
description: "WHAT: Review HE PRs, diffs, CI, traceability, repeated review feedback, and autofix loops. Use when merge readiness or review fixes need evidence."
Use for PRs, branches, diffs, commits, readiness, and disputed review feedback.
Select mode first: review-only, readiness, repair/autofix, commit review, or investigation; review-only mode stays byte-clean, and ambiguous mode that could mutate files or PR state uses the interactive steering contract before proceeding. Read changed files and relevant review threads/comments; lead with file:line findings; Codex-compatible findings must be tight; check `Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`; in coding-harness-managed repos also check Project Brain, north-star evidence, and Harness review gates; use `evidence_ladder`. For disputed behavior or repeated bot feedback, require a proof loop before hypothesizing; see review loop patterns. For skill, plugin, CLI, agent-doc, eval, routing, or projection changes, apply the agent-native audit scorecard through the policy index. Apply the specialist skill steering contract when domain-specific review evidence would materially improve risk detection or proof quality; when changed-scope simplification is warranted, route to the external `simplify` specialist as a review lens and do not copy its simplification doctrine into HE. For cockpit, golden-path, or command-catalog work, block readiness when the diff proves implementation presence but not first-contact compression, fresh-agent usability, or ablation. Do not approve readiness from green CI alone when real behavior proof, security review, or live PR-thread state is missing. When writing `.harness/review/**`, classify the artifact by content shape before path, preserve date and Linear issue prefixes when the repo already uses them, and keep the same `canonical_slug` as the spec/plan/eval chain. Then approve/request/autofix. If feedback repeats across PRs, classify whether HE context, evals, or skill routing should adapt after the immediate review.
description: "WHAT: Analyze and route HE lifecycle state across Linear, stages, PRs, and Project Brain. Use when work must resume or refresh."
Inspect live state; pick stage order; keep Linear/spec/plan/PR links; apply the interactive steering contract when earliest incomplete stage, resume target, or refresh route conflicts across evidence; in coding-harness-managed repos preserve Harness lifecycle state and refresh Project Brain when repository context changes. For solved-problem capture, use the solution capture contract: search `.harness/solutions/**` and legacy `docs/solutions/**`, refresh high-overlap entries, write new captures under `.harness/solutions/**`, verify discoverability from active instruction surfaces, and sync or explicitly block Project Brain when `.harness/knowledge/**` is in use. When UI-plan artifacts are present, use the UI plan routing contract, verify Project Brain status for plan/decision context, and hand off to `he-plan`, `he-work`, or `he-code-review` as appropriate. When diagnosis says product compression is the blocker, especially `active_stage: spec_refresh_required`, route to `he-spec` with the compression contract instead of approving another additive implementation pass.
description: "WHAT: Generate post-implementation HE eval and drift reports before Linear closure. Use when completed work needs proof against the approved slice, validation gates, routing, architecture, context, governance, and moat invariants."
Use after an HE implementation slice is complete and before recommending Linear parent issue, milestone, project, or execution-slice closure.
Identify the evaluated slice first; do not evaluate unrelated work. Load the eval report contract, schema, template, drift taxonomy, and Linear completion policy. Classify source artifacts by content shape before path so mismatched titles, dates, or Linear identifiers become traceability findings rather than silent assumptions. Compare implementation against Linear plan, refactor program, plugin HE spec, ADRs, and core invariants. Prove agentic eval validity before closure: task validity, outcome validity, trajectory/process evidence, grader coverage, trial policy, authorization validation for side-effectual actions, and saturation or maintenance signal. Apply the agent-native audit scorecard when closure touches skills, plugins, CLIs, agent docs, evals, routing, projections, automation, or workflow surfaces. Apply the specialist skill steering contract when closure depends on domain-specific proof quality. Run or explicitly block relevant validation gates; never invent passing results. Generate the report, validate it with `scripts/validate_eval_report.py`, apply the interactive steering contract to ask accept/challenge/rework before using a Complete or Complete with follow-up result as a Linear closure recommendation, gather corrections when the user challenges the evidence, and only then recommend Linear status changes.
description: "WHAT: Diagnose and fix HE test, QA, CI, incident, or regression failures. Use when reproduction and validation are required."
Reproduce first; inspect changed path; patch narrowly; validate exact failure path. When the same failure class recurs, record the root-cause learning and durable fix surface.
description: "WHAT: Automate HE wakeups, monitoring, until-green checks, and follow-through. Use when later thread continuation or goal-aware scheduling is needed."
Prefer thread heartbeat for this conversation; encode stop criteria; avoid duplicate automations. When `/goal` is active or requested, keep the goal as the persistent objective and the heartbeat as the scheduler with live checks and stop rules.
For GitHub PR sweeps, keep the loop concrete: identify the PR set, re-check GitHub truth, inspect CircleCI/job logs for failing checks, inspect CodeRabbit/Codex review threads, and route each wake-up to the smallest safe `he-code-review` or `he-work` follow-up. Use `git-project-triage` as a helper role only when it is available in the Codex agent manifest; if the role is missing, continue inline and report that delegation gap.
Redact secrets; do not create cron workarounds for short thread follow-up. Do not remove important context for budget trimming; move deep context to references.
description: "WHAT: Analyze and audit one HE skill surface for targeted improvement. Use when hardening, warning cleanup, or evidence-backed refactoring is needed."
Before any new skill package is proposed, inspect existing surfaces; start with 2-3 focused surfaces at most, choose one primary target and at most two supporting references; label path fragments and bundle names as evidence labels; close coverage-gap items; translate external source material into invariants, evals, references, contracts, or an explicit rejection; for skill work, run the A/B/C spec-implementation-evaluation loop until the stop rule passes or a concrete blocker remains. When improvement evidence is really about product-surface compression, update the shared compression contract and the stage evals that enforce it before creating another visible skill.
description: "WHAT: Convert approved Harness Engineering cognition into a small, traceable Linear execution plan under .harness/linear without mutating Linear. Use when features, review, triage, strategy, core, ADR, or refactor artifacts need milestones, parent issues, dependencies, labels, eval gates, and human/agent routing."
description: "WHAT: Run approved HE plans phase-by-phase under a heartbeat with collector evidence and pre-commit review gates. Use when repeated he-work slices need recurring wakeups, validation, and local commit readiness."
1. Resolve live state first: read the plan or issue artifact, check the workspace path, current branch, dirty worktree, and latest validation or blocker evidence. Preserve unrelated user edits.
Keep the first skillified pass tight: schedule, collector intake, phase gate, and reporting. Move broader examples or repo-specific playbooks into references.
- "Create a 10 minute heartbeat for this HE plan and run simplify, he-fix-bugs, and he-code-review before each local commit."
- "Keep he-work going through the approved phases until reviewed, using session-collector evidence from today."
- "Monitor this coding-harness plan; at the end of each implementation unit, run the review gates and commit only the clean phase."
description: "WHAT: Generate HE plans from approved specs, Linear issues, or source artifacts. Use when sequencing, tests, rollback, or traceability need planning."
Use after approved spec/issue; do non-mutating inspection before planning.
Explore first, ask second; use update_plan only for live progress; before writing durable docs choose `.harness/plan/**.md` from the artifact routing contract, classify existing artifacts by content shape before path, and apply Artifact Identity frontmatter so `artifact_id`, `canonical_slug`, `title`, H1, origin, and Linear identifiers trace to the same slice; for dedicated UI plans use `.harness/plan/**-ui-plan.md` and the UI plan routing contract, treating `docs/ui-plan/**` and `docs/ui-plans/**` as legacy source evidence and reporting Project Brain sync/defer/block status when `.harness/knowledge/**` is in use; when planning coding-harness-managed work load the execution slice contract, run the Linear Delta Capture Gate for existing tracked plans, and keep the plan inside the selected milestone, parent issue, refactor phase, or execution slice; classify review-derived plan changes with the document-review finding tiers; apply the specialist skill steering contract when the approved slice proves a domain need that can improve sequencing, validation gates, rollback, or implementation-unit boundaries; turn scope into ordered implementation units; run or explicitly block coding-harness plan gates when the repo exposes them. Treat `.harness/strategy/*.md`, `.harness/triage/*.md`, `.harness/review/*.md`, and `.harness/features/*.md` as context unless the approved Linear/refactor slice admits them. End with the post-plan handoff state, apply the interactive steering contract when multiple valid next stages remain, and route to the next authorized HE stage in the same run only when the user has already asked to continue. For cockpit, golden-path, command-catalog, or agent-native compression work, plan subtractive proof before additive compatibility: name the exact first-contact budget, shrink default help, demote plumbing commands, require full catalogs to use an advanced/all flag, rewrite the README front door around the golden path, add admission tests, add fresh-agent eval, and require ablation decisions for every still-visible command family.
description: "WHAT: Generate evidence-backed Harness Engineering refactor and migration programs under .harness/refactors. Use when strategy, triage, review, ADRs, or core invariants identify high-leverage structural evolution that needs staged migration, rollback, eval proof, and Linear-ready mapping before implementation."
description: "WHAT: Route ambiguous HE requests to the right lifecycle stage. Use when intent mixes brainstorm, spec, plan, work, review, or aliases."
Route using `./bin/ask` (wrapping the routing operation); keep request text data-only; load only the chosen stage; before any new skill package is proposed, use session-evidence-skillify-triage.md; path fragments and bundle names are evidence labels for collector-backed improvement. When session evidence is used, apply the session evidence trace context so repo, branch, PR, Linear, and artifact-chain identity are known or explicitly blocked. When existing `.harness` artifacts drive routing, classify by content shape before path and record path/title/Linear mismatches as traceability defects. When deterministic routing leaves one consequential stage or source choice, apply the interactive steering contract before guessing. When the request explicitly asks for persistent continuation, `/goal`, resume-over-time, or keep-working-until-done behavior, apply the goal continuity contract after selecting the HE stage and hand off durable board governance to `Skills/agent-ops/goal-governor`. When a diagnosis names compression as the missing acceptance gate or says `spec_refresh_required`, route to `he-spec` and include the compression contract.
description: "WHAT: Generate Linear-backed HE specs with acceptance IDs and validation. Use when requirements or traceability are needed before planning."
Inspect session-collector evidence and repo truth; when session evidence is used, pre-resolve repo, branch, PR, Linear, artifact-chain, and currentness from the session evidence trace context; for coding-harness-managed work load the execution slice contract before writing requirements; consume the approved `.harness/linear/<repo-name>-linear-plan.md`, selected `.harness/refactors/<selected-refactor>.md` when applicable, `.harness/decisions/*.md`, `.harness/core/*.md`, and `.harness/brainstorm/*.md` as primary inputs; use `.harness/strategy/*.md`, `.harness/triage/*.md`, `.harness/review/*.md`, and `.harness/features/*.md` only for evidence or context; classify review-derived spec improvements with the document-review finding tiers before applying them; apply the specialist skill steering contract when a proven domain need can sharpen acceptance criteria, validation, non-goals, or risk; apply the interactive steering contract when behavior, scope boundary, acceptance authority, or selected slice remains unresolved after source inspection; stop if no selected milestone, parent issue, refactor phase, or execution slice is identified. Resolve/create the Linear tracker for non-trivial work; for existing tracked plans run the Linear Delta Capture Gate before consuming the approved slice, reconcile required labels, classify new or changed Linear issues, and promote at most one admitted item into the spec scope; require Linear project, milestone, parent issue, sub-issues when present, labels, priority, dependencies, and agent/human route for tracked specs; before writing durable docs choose `.harness/specs/**.md` from the artifact routing contract, classify existing artifacts by content shape before path, and apply Artifact Identity frontmatter so `artifact_id`, `canonical_slug`, `title`, H1, origin, and Linear identifiers trace to the same slice; define scope, assumptions, assets/icon-small.png if packaging matters, explicit In Scope and Out of Scope boundaries, and handoff to plan with coding-harness state when applicable. When feedback says a prior cockpit, golden-path, or agent-native plan was too additive, load the compression contract and make first-contact budget, standalone command admission, docs deletion budget, fresh-agent eval, ablation proof, and evidence-backed metric gates blocking acceptance criteria.
description: "WHAT: Generate evidence-backed Harness Engineering strategy artifacts for repo intent, architecture review, triage, strategic compression, ADR compression, and core invariant compression. Use when .harness cognition needs to clarify direction, moat, drift risk, or future-agent guidance before refactors, Linear planning, specs, or implementation."
description: "WHAT: Build approved HE changes in verified slices with traceability. Use when execution is approved or bounded delegation is needed."
Mark current active state; if `/goal` is active, confirm it matches the branch, issue, plan, or PR before editing and treat mismatches as blockers rather than overwriting project truth. Explore first, ask second; apply the interactive steering contract when branch, goal, plan, Linear issue, or selected slice conflicts before editing; apply the specialist skill steering contract only when implementing the approved slice requires a proven domain skill and does not reopen scope; `update_plan` is live checklist only; for UI-plan work load the UI plan routing contract, preserve Project Brain status, and require visual/accessibility verification evidence; for coding-harness-managed work load the execution slice contract, run the Linear Delta Capture Gate for existing tracked plans, and verify the plan/todo maps to one selected milestone, parent issue, refactor phase, or execution slice before editing; before external-delegate or parallel work, run the delegation overlap safety check from the work contract; use external-delegate only for bounded non-overlapping slices or isolated worktrees; run or explicitly block coding-harness blast-radius/policy/preflight/validation gates and record exact command/path plus smallest recovery step when blocked; handoff to he-code-review mode:autofix when needed.
```
