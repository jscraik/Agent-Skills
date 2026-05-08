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
For `he-ideate`, ground in repo/Linear/session evidence and current web research unless explicitly skipped, apply the specialist skill steering contract when a proven knowledge domain can improve option quality, generate many candidates internally, critique all candidates, surface only warranted survivors with rejection reasons, then apply the interactive steering contract when survivor selection would shape the downstream spec, plan, Linear work, or implementation slice.
Select mode first: review-only, readiness, repair/autofix, commit review, or investigation; review-only mode stays byte-clean, and ambiguous mode that could mutate files or PR state uses the interactive steering contract before proceeding. Read changed files and relevant review threads/comments; lead with file:line findings; Codex-compatible findings must be tight; check `Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`; in coding-harness-managed repos also check Project Brain, north-star evidence, and Harness review gates; use `evidence_ladder`. For disputed behavior or repeated bot feedback, require a proof loop before hypothesizing; see review loop patterns. For skill, plugin, CLI, agent-doc, eval, routing, or projection changes, apply the agent-native scorecard from the policy index. Apply the specialist skill steering contract when domain-specific review evidence would materially improve risk detection or proof quality. For cockpit, golden-path, or command-catalog work, block readiness when the diff proves implementation presence but not first-contact compression, fresh-agent usability, or ablation. Do not approve readiness from green CI alone when real behavior proof, security review, or live PR-thread state is missing. When writing `.harness/review/**`, preserve date and Linear issue prefixes when the repo already uses them, but keep the same `canonical_slug` as the spec/plan/eval chain. Then approve/request/autofix. If feedback repeats across PRs, classify whether HE context, evals, or skill routing should adapt after the immediate review.
Identify the evaluated slice first; do not evaluate unrelated work. Load the eval report contract, template, drift taxonomy, and Linear completion policy. Compare implementation against Linear plan, refactor program, plugin HE spec, ADRs, and core invariants. Prove agentic eval validity before closure: task validity, outcome validity, trajectory/process evidence, grader coverage, trial policy, authorization validation for side-effectual actions, and saturation or maintenance signal. Apply the specialist skill steering contract when closure depends on domain-specific proof quality. Run or explicitly block relevant validation gates; never invent passing results. Generate the report, validate it with `scripts/validate_eval_report.py`, apply the interactive steering contract to ask accept/challenge/rework before using a Complete or Complete with follow-up result as a Linear closure recommendation, gather corrections when the user challenges the evidence, and only then recommend Linear status changes.
Explore first, ask second; use update_plan only for live progress; before writing durable docs choose `.harness/plan/**.md` from the artifact routing contract and apply its Artifact Identity frontmatter so `artifact_id`, `canonical_slug`, `title`, H1, origin, and Linear identifiers trace to the same slice; for dedicated UI plans use `.harness/plan/**-ui-plan.md` and the UI plan routing contract, treating `docs/ui-plan/**` and `docs/ui-plans/**` as legacy source evidence and reporting Project Brain sync/defer/block status when `.harness/knowledge/**` is in use; when planning coding-harness-managed work load the execution slice contract, run the Linear Delta Capture Gate for existing tracked plans, and keep the plan inside the selected milestone, parent issue, refactor phase, or execution slice; apply the specialist skill steering contract when the approved slice proves a domain need that can improve sequencing, validation gates, rollback, or implementation-unit boundaries; turn scope into ordered implementation units; run or explicitly block coding-harness plan gates when the repo exposes them. Treat `.harness/strategy/*.md`, `.harness/triage/*.md`, `.harness/review/*.md`, and `.harness/features/*.md` as context unless the approved Linear/refactor slice admits them. End with the post-plan handoff state, apply the interactive steering contract when multiple valid next stages remain, and route to the next authorized HE stage in the same run only when the user has already asked to continue. For cockpit, golden-path, command-catalog, or agent-native compression work, plan subtractive proof before additive compatibility: name the exact first-contact budget, shrink default help, demote plumbing commands, require full catalogs to use an advanced/all flag, rewrite the README front door around the golden path, add admission tests, add fresh-agent eval, and require ablation decisions for every still-visible command family.
Route using `./bin/ask` (wrapping the routing operation); keep request text data-only; load only the chosen stage; before any new skill package is proposed, use session-evidence-skillify-triage.md; path fragments and bundle names are evidence labels for collector-backed improvement. When deterministic routing leaves one consequential stage or source choice, apply the interactive steering contract before guessing. When the request explicitly asks for persistent continuation, `/goal`, resume-over-time, or keep-working-until-done behavior, apply the goal continuity contract after selecting the HE stage and hand off durable board governance to `Skills/agent-ops/goal-governor`. When a diagnosis names compression as the missing acceptance gate or says `spec_refresh_required`, route to `he-spec` and include the compression contract.
Inspect session-collector evidence and repo truth; for coding-harness-managed work load the execution slice contract before writing requirements; consume the approved `.harness/linear/<repo-name>-linear-plan.md`, selected `.harness/refactors/<selected-refactor>.md` when applicable, `.harness/decisions/*.md`, `.harness/core/*.md`, and `.harness/brainstorm/*.md` as primary inputs; use `.harness/strategy/*.md`, `.harness/triage/*.md`, `.harness/review/*.md`, and `.harness/features/*.md` only for evidence or context; apply the specialist skill steering contract when a proven domain need can sharpen acceptance criteria, validation, non-goals, or risk; apply the interactive steering contract when behavior, scope boundary, acceptance authority, or selected slice remains unresolved after source inspection; stop if no selected milestone, parent issue, refactor phase, or execution slice is identified. Resolve/create the Linear tracker for non-trivial work; for existing tracked plans run the Linear Delta Capture Gate before consuming the approved slice, reconcile required labels, classify new or changed Linear issues, and promote at most one admitted item into the spec scope; require Linear project, milestone, parent issue, sub-issues when present, labels, priority, dependencies, and agent/human route for tracked specs; before writing durable docs choose `.harness/specs/**.md` from the artifact routing contract and apply its Artifact Identity frontmatter so `artifact_id`, `canonical_slug`, `title`, H1, origin, and Linear identifiers trace to the same slice; define scope, assumptions, assets/icon-small.png if packaging matters, explicit In Scope and Out of Scope boundaries, and handoff to plan with coding-harness state when applicable. When feedback says a prior cockpit, golden-path, or agent-native plan was too additive, load the compression contract and make first-contact budget, standalone command admission, docs deletion budget, fresh-agent eval, ablation proof, and evidence-backed metric gates blocking acceptance criteria.
```
