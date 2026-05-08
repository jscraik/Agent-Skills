# Harness Engineering Deferred Context Index

HE active files must stay real plugin-owned text. Historical snapshots live under `fixtures/**` or `Infrastructure/references/harness-engineering/deferred-context-index.full.md`; active paths must not symlink into archives.

Use this when compact stage files defer context. Do not trim silently: move durable behavior to a stage reference, link it here, and keep enough wording for validators and future agents.

## Runtime References

- Routing and domain context: `references/routing-map.json`, `references/deterministic-stage-routing.md`, `references/domain-model-routing.md`, `references/domain-context-contract.md`, `references/design-complexity-contract.md`
- Lifecycle, artifact, slice, and tracker gates: `references/lifecycle-exit-contract.md`, `references/artifact-routing-contract.md`, `references/execution-slice-contract.md`, `references/linear-tracker-gate.md`, `references/coding-harness-command-bridge.md`, `references/goal-continuity.md`
- Intake and evidence: `references/qa-intake-routing.md`, `references/session-evidence-contract.md`, `references/session-evidence-skillify-triage.md`
- Skill improvement: `references/skill-improvement-loop.md`
- Delegation: `references/subagent-routing.md`, `references/subagent-call-contract.md`
- Folded compatibility: `references/folded-skill-context.md`

## Stage Preserved Context

`he-plan` keeps plan-mode, synthesis, deepening, testing, handoff, and visual planning doctrine in:

- `Plugins/harness-engineering/references/he-plan-doctrine.md`
- `Plugins/harness-engineering/skills/he-plan/references/codex-plan-mode.md`
- `Plugins/harness-engineering/skills/he-plan/references/plan-artifact-contract.md`
- `Plugins/harness-engineering/skills/he-plan/references/planning-depth.md`
- `Plugins/harness-engineering/skills/he-plan/references/deepening-review.md`
- `Plugins/harness-engineering/skills/he-plan/references/test-strategy.md`
- `Plugins/harness-engineering/skills/he-plan/references/visual-communication.md`

`he-spec` keeps collaboration, session evidence, source parity, artifact templates, and autoresearch decisions in:

- `Plugins/harness-engineering/references/he-spec-doctrine.md`
- `Plugins/harness-engineering/skills/he-spec/references/autoresearch-2026-05-02.md`
- `Plugins/harness-engineering/skills/he-spec/references/codex-and-session-evidence.md`
- `Plugins/harness-engineering/skills/he-spec/references/spec-artifact-contract.md`
- `Plugins/harness-engineering/skills/he-spec/references/spec-mode-rules.md`

`he-work` keeps execution lessons, work patterns, execution modes, and handoff rules in:

- `Plugins/harness-engineering/skills/he-work/references/work-execution-contract.md`
- `Plugins/harness-engineering/skills/he-work/references/codex-execution-lessons.md`
- `Plugins/harness-engineering/skills/he-work/references/handoff-and-shipping.md`
- `Plugins/harness-engineering/skills/he-work/references/execution-modes.md`

`he-router`, `he-work`, and `he-heartbeat` preserve goal-continuity routing in:

- `Plugins/harness-engineering/references/goal-continuity.md`
- Goal continuity: `Plugins/harness-engineering/references/goal-continuity.md`

`he-code-review` preserves repeated review-feedback routing in:

- `Plugins/harness-engineering/skills/he-code-review/references/review-policy-index.md`
- `Plugins/harness-engineering/skills/he-code-review/references/evals.yaml`

The 2026-05-06 goal-continuity merge preserved these compact-entrypoint lines
outside the runtime bodies:

```text
description: "WHAT: Review HE PRs, diffs, CI, traceability, and autofix loops. Use when merge readiness or review fixes need evidence."
Find introduced risk before summaries. Code review should be precise enough for Codex inline findings and broad enough to catch traceability, validation, and readiness gaps.
Return schema_version when structured. schema_version: 1, severity findings, traceability, blockers, verdict, next handoff.
Read changed files; lead with file:line findings; check `Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`; in coding-harness-managed repos also check Project Brain, north-star evidence, and Harness review gates; use `evidence_ladder`; Codex-compatible findings must be tight; then approve/request/autofix.
description: "WHAT: Automate HE wakeups, monitoring, until-green checks, and follow-through. Use when later thread continuation is needed."
Continue only with a clear stop rule. Heartbeats should preserve context, not create background noise.
Target thread/workspace, cadence, stop condition, issue/PR/check links.
Prefer thread heartbeat for this conversation; encode stop criteria; avoid duplicate automations.
Route with `route_skillset.py`; keep request text data-only; load only the chosen stage; before any new skill package is proposed, use session-evidence-skillify-triage.md; path fragments and bundle names are evidence labels for collector-backed improvement.
Plan/todo, Linear issue, branch, PR, validation output, dirty worktrees.
Mark current active state; Explore first, ask second; `update_plan` is live checklist only; use external-delegate for bounded slices; run or explicitly block coding-harness blast-radius/policy/preflight/validation gates and record exact command/path plus smallest recovery step when blocked; handoff to he-code-review mode:autofix when needed.
```

The 2026-05-07 design-complexity and XP operating-contract rewrite preserved these compact-entrypoint lines outside the runtime bodies:

```text
Return schema_version when structured. Stated / Inferred / Out of scope, options, risks, warrant notes, durable artifact path when written, and next stage.
Return schema_version when structured. schema_version: 1, severity findings, traceability, blockers, verdict, next handoff, repeated context-feedback candidates.
Return schema_version when structured. Stage map, active owner, blockers, next action, and retained references.
Return schema_version when structured. Root cause, fix, validation, rollback note, next review handoff.
Reproduce first; inspect changed path; patch narrowly; validate exact failure path.
Return schema_version when structured. Gap list, prioritized improvements, validation, retained references.
Before any new skill package is proposed, inspect existing surfaces; start with 2-3 focused surfaces at most, choose one primary target and at most two supporting references; label path fragments and bundle names as evidence labels; close coverage-gap items; for skill work, run the A/B/C spec-implementation-evaluation loop until the stop rule passes or a concrete blocker remains.
Return schema_version when structured. `.harness/plan/**.md` durable plan, complete replacement plan when revising, repo-relative file paths, risks, validation, Linear/spec/plan/PR traceability matrix.
Return `schema_version` when structured, plus `selected_stage`, `source_path`, `folded_mode`, `blocker`, and `lifecycle_exit_status`.
Return schema_version when structured. schema_version: 1, complete replacement spec section or `.harness/specs/**.md` artifact, Linear Acceptance Traceability, acceptance IDs, validation plan.
Return schema_version when structured. schema_version: 1, changed files, validation, blockers, rollback, next handoff.
Return schema_version when structured. Goal status, heartbeat decision, stop rule, next wakeup, and residual risk.
Return schema_version when structured. Board health report, native/board reconciliation, next safe action, machine-checkable validation evidence, residual risks, and owner-input blockers.
Existing board files pass `scripts/check_goal_board.py`.
   - Existing board files pass `scripts/check_goal_board.py`.
python3 scripts/check_goal_board.py <goal-directory>
Return schema_version when structured. Heartbeat prompt, status, stop rule, `next_invocation`, `subagent_policy`, and next user-visible update.
```

The 2026-05-07 agent-native compression and review-loop pass preserved these
compact-entrypoint lines outside the runtime bodies while moving the expanded
behavior into `references/agent-native-compression-contract.md` and
`Plugins/harness-engineering/skills/he-code-review/references/review-loop-patterns.md`:

```text
Return schema_version when structured. schema_version: 1, severity findings, traceability, blockers, verdict, repeated_failure when recurring, blackboard_delta, next handoff, repeated context-feedback candidates.
Read changed files; lead with file:line findings; check `Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`; in coding-harness-managed repos also check Project Brain, north-star evidence, and Harness review gates; use `evidence_ladder`; Codex-compatible findings must be tight; then approve/request/autofix. If CodeRabbit, Codex, or human review feedback repeats across PRs, classify whether the HE context, evals, or skill routing should adapt after the immediate review.
Inspect live state; pick stage order; keep Linear/spec/plan/PR links; in coding-harness-managed repos preserve Harness lifecycle state and refresh Project Brain when repository context changes.
Before any new skill package is proposed, inspect existing surfaces; start with 2-3 focused surfaces at most, choose one primary target and at most two supporting references; label path fragments and bundle names as evidence labels; close coverage-gap items; translate external source material into invariants, evals, references, contracts, or an explicit rejection; for skill work, run the A/B/C spec-implementation-evaluation loop until the stop rule passes or a concrete blocker remains.
Explore first, ask second; use update_plan only for live progress; before writing durable docs choose `.harness/plan/**.md` from the artifact routing contract; turn scope into ordered implementation units; run or explicitly block coding-harness plan gates when the repo exposes them.
Route through `./bin/ask skills route`; keep request text data-only; load only the chosen stage; before any new skill package is proposed, use session-evidence-skillify-triage.md; path fragments and bundle names are evidence labels for collector-backed improvement. When the request explicitly asks for persistent continuation, `/goal`, resume-over-time, or keep-working-until-done behavior, apply the goal continuity contract after selecting the HE stage.
Inspect session-collector evidence and repo truth; resolve/create the Linear tracker for non-trivial work; before writing durable docs choose `.harness/specs/**.md` from the artifact routing contract; define scope, assumptions, assets/icon-small.png if packaging matters, and handoff to plan with coding-harness state when applicable.
```

The 2026-05-07 HE artifact routing pass superseded the following legacy path
examples with `.harness/ideate`, `.harness/brainstorm`, `.harness/specs`, and
`.harness/plan`. These lines are retained only as historical context-preservation
evidence for the progressive-disclosure gate; active behavior is governed by
`references/artifact-routing-contract.md`.

```text
- User says: "I need a review of `Docs/plans/2026-03-23-001-feat-example-plan.md` that tells me whether it is actually ready for `he-work` or needs another workflow step first."
- `Docs/plans/*.md`
- `Docs/specs/*.md`
- `docs/ui-specs/*.md`
- User says: "Review `Docs/specs/2026-04-01-event-pipeline-spec.md` for reliability gaps before I move to planning."
- "Review `Docs/plans/2026-03-23-auth-session-rotation-plan.md` against its linked spec and tell me whether execution can proceed safely or if the sequencing still leaves implementers guessing."
- "Score `Docs/specs/2026-03-23-auth-session-rotation-spec.md` for planning readiness, especially lifecycle handling, failure recovery, and observability."
- Requirements doc at `docs/brainstorms/YYYY-MM-DD-<topic>-requirements.md` (new work) or legacy doc updated
- Requirements document (`docs/brainstorms/YYYY-MM-DD-<topic>-requirements.md`) when durable decisions exist
- User asks: "Resume `docs/brainstorms/2026-04-02-agent-feedback-loop-requirements.md`, resolve remaining blockers, then tell me the next HE stage."
- `docs/brainstorms/YYYY-MM-DD-<topic>-requirements.md`
- generated document paths must stay repo-relative (for example, `docs/brainstorms/...`), never absolute paths, because absolute paths break portability across machines and worktrees
Ensure `docs/brainstorms/` exists before writing. Use frontmatter with `title`, `date`, `status`, `spec_required`, `risk_level`, and `complexity`.
If the user references an existing brainstorm topic or document, or there is an obvious recent matching `*-requirements.md` file in `docs/brainstorms/`:
  - one or more existing artifact paths under `docs/brainstorms/`, `Docs/specs/`, `Docs/plans/`, `docs/ui-plans/`, or `docs/solutions/`
- User says: "Run `he-compound` from `docs/brainstorms/2026-04-06-queue-retry-requirements.md` and tell me the first incomplete Harness Engineering stage."
- do not recommend deleting or gitignoring Harness Engineering pipeline artifacts in `docs/brainstorms/`, `Docs/plans/`, or `docs/solutions/`
- User says: "Please deepen `Docs/plans/2026-04-07-checkout-retry-rollout-plan.md`; rollout, rollback, and verification still feel weak."
- Which plan should I deepen? You can give me the path directly from `Docs/plans/`.
- User says: "Deepen `Docs/specs/2026-03-20-feat-issue-runner-spec.md`; cancellation, retry caps, and workspace cleanup are still underspecified."
- User says: "Run max-coverage on `Docs/specs/2026-04-04-billing-reconciliation-spec.md` and include directly relevant learnings from `docs/solutions/`."
- User says: "Stress-test `docs/ui-specs/2026-03-22-checkout-ui-spec.md`; VAC coverage for keyboard, loading, and empty states is thin."
- Which spec should I deepen? You can give me a path from `Docs/specs/` or `docs/ui-specs/`.
  - `Docs/plans/YYYY-MM-DD-<type>-<descriptive-name>-plan.md`
  - compatibility mode: `Docs/plans/YYYY-MM-DD-<topic>-ui-plan.md` only when the repo already uses that convention or the user explicitly requests it
  - explicit UI spec path in `docs/ui-specs/`
  - explicit UI spec path in legacy `Docs/specs/*-ui-spec.md`
  - matching recent brainstorm in `docs/brainstorms/`
  - matching recent spec in `Docs/specs/`
- `Docs/plans/` for general plans
- existing plan path or obvious matching recent plan in `Docs/plans/`
- matching recent requirements doc in `docs/brainstorms/*-requirements.md`
  - `Docs/specs/YYYY-MM-DD-<type>-<descriptive-name>-spec.md`
  - `docs/ui-specs/YYYY-MM-DD-<descriptive-name>-ui-spec.md`
  - compatibility mode: `Docs/specs/YYYY-MM-DD-<topic>-ui-spec.md` only when the repo or user explicitly requires the legacy path
  - explicit UI source path in `docs/ui-specs/`
  - explicit legacy UI source path in `Docs/specs/*-ui-spec.md`
  - explicit parent spec path in `Docs/specs/`
  - matching recent brainstorm in `docs/brainstorms/`
  - matching recent spec in `Docs/specs/`
- "Revise `Docs/specs/2026-03-21-session-rotation-spec.md` so token expiry behavior, rollback conditions, and observability events are explicit."
- "Turn `docs/brainstorms/2026-04-07-checkout-retry-requirements.md` into an implementation-grade spec with retry caps, idempotency keys, and failure telemetry before `he-plan`."
- `Docs/specs/` for standard specs
- `docs/ui-specs/` for dedicated UI specs
- dedicated UI specs prefer `docs/ui-specs/YYYY-MM-DD-<descriptive-name>-ui-spec.md`
- standard specs default to `Docs/specs/YYYY-MM-DD-<type>-<descriptive-name>-spec.md`
- use the legacy `Docs/specs/...-ui-spec.md` form only in compatibility mode, then rely on `Infrastructure/references/spec-artifacts.md` for templates and verification
- User says: "Please implement `Docs/plans/2026-04-01-auth-session-rotation-plan.md`, validate each phase, and keep checklist state synced with shipped code."
- prefer `Docs/plans/*.md` or `docs/ui-plans/*.md` when they exist
Explore first; separate evidence from guesses; for durable tracked work resolve/create the Linear issue before handoff; in coding-harness-managed repos load the command bridge and record the Harness transition.
Return schema_version when structured. Stated / Inferred / Out of scope, options, risks, warrant notes, blackboard_delta, and next stage.
- "Inspect and review PR 154 in coding-harness against JSC-246, `Specs/JSC-246-account-settings.md`, `Plans/JSC-246-account-settings.md`, CircleCI, and CodeRabbit threads."
Select mode first: review-only, readiness, repair/autofix, commit review, or investigation; review-only mode stays byte-clean. Read changed files and relevant review threads/comments; lead with file:line findings; check `Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`; in coding-harness-managed repos also check Project Brain, north-star evidence, and Harness review gates; use `evidence_ladder`. For disputed behavior or repeated bot feedback, require a proof loop before hypothesizing; see review loop patterns. For cockpit, golden-path, or command-catalog work, block readiness when the diff proves implementation presence but not first-contact compression, fresh-agent usability, or ablation. Do not approve readiness from green CI alone when real behavior proof, security review, or live PR-thread state is missing. Then approve/request/autofix. If feedback repeats across PRs, classify whether HE context, evals, or skill routing should adapt after the immediate review.
- "Inspect `Specs/account-settings.md` and JSC-246, then write the implementation plan with plan IDs, validation commands, rollback, and a Linear/spec/plan traceability table."
- "Inspect the latest preflight output, then deepen `Plans/JSC-246-account-settings.md` and return a complete replacement plan."
Explore first, ask second; use update_plan only for live progress; turn scope into ordered implementation units; run or explicitly block coding-harness plan gates when the repo exposes them. For cockpit, golden-path, command-catalog, or agent-native compression work, plan subtractive proof before additive compatibility: name the exact first-contact budget, shrink default help, demote plumbing commands, require full catalogs to use an advanced/all flag, rewrite the README front door around the golden path, add admission tests, add fresh-agent eval, and require ablation decisions for every still-visible command family.
Return schema_version when structured. durable plan, complete replacement plan when revising, repo-relative file paths, risks, validation, Linear/spec/plan/PR traceability matrix, slack_policy, and blackboard_delta.
Inspect session-collector evidence and repo truth; resolve/create the Linear tracker for non-trivial work; define scope, assumptions, assets/icon-small.png if packaging matters, and handoff to plan with coding-harness state when applicable. When feedback says a prior cockpit, golden-path, or agent-native plan was too additive, load the compression contract and make first-contact budget, standalone command admission, docs deletion budget, fresh-agent eval, ablation proof, and evidence-backed metric gates blocking acceptance criteria.
Return schema_version when structured. schema_version: 1, complete replacement spec section, Linear Acceptance Traceability, acceptance IDs, validation plan, and blackboard_delta.
- "Inspect JSC-246 and implement only the units in `Plans/JSC-246-account-settings.md`, preserve my dirty edits, then run `bash scripts/run-harness-setup-checks.sh`."
```

The 2026-05-07 execution-slice pass preserved these compact-entrypoint lines
outside the runtime bodies while moving the expanded authority order and stop
rules into `references/execution-slice-contract.md`:

```text
Problem, Linear issue, QA report, source evidence, current-vs-latest spec status.
Return schema_version when structured. schema_version: 1, complete replacement spec section or `.harness/specs/**.md` artifact, Linear Acceptance Traceability, acceptance IDs, validation plan, and blackboard_delta.
Inspect session-collector evidence and repo truth; resolve/create the Linear tracker for non-trivial work; before writing durable docs choose `.harness/specs/**.md` from the artifact routing contract; define scope, assumptions, assets/icon-small.png if packaging matters, and handoff to plan with coding-harness state when applicable. When feedback says a prior cockpit, golden-path, or agent-native plan was too additive, load the compression contract and make first-contact budget, standalone command admission, docs deletion budget, fresh-agent eval, ablation proof, and evidence-backed metric gates blocking acceptance criteria.
Explore first, ask second; use update_plan only for live progress; before writing durable docs choose `.harness/plan/**.md` from the artifact routing contract; turn scope into ordered implementation units; run or explicitly block coding-harness plan gates when the repo exposes them. For cockpit, golden-path, command-catalog, or agent-native compression work, plan subtractive proof before additive compatibility: name the exact first-contact budget, shrink default help, demote plumbing commands, require full catalogs to use an advanced/all flag, rewrite the README front door around the golden path, add admission tests, add fresh-agent eval, and require ablation decisions for every still-visible command family.
Mark current active state; if `/goal` is active, confirm it matches the branch, issue, plan, or PR before editing and treat mismatches as blockers rather than overwriting project truth. Explore first, ask second; `update_plan` is live checklist only; use external-delegate for bounded slices; run or explicitly block coding-harness blast-radius/policy/preflight/validation gates and record exact command/path plus smallest recovery step when blocked; handoff to he-code-review mode:autofix when needed.
```

The 2026-05-08 Linear, solution-capture, Project Brain, and UI-plan routing
pass preserved these compact-entrypoint lines outside the runtime bodies while
moving the expanded behavior into `references/linear-delta-capture-gate.md`,
`references/solution-capture-contract.md`, and
`references/ui-plan-routing-contract.md`:

```text
Inspect live state; pick stage order; keep Linear/spec/plan/PR links; in coding-harness-managed repos preserve Harness lifecycle state and refresh Project Brain when repository context changes. When diagnosis says product compression is the blocker, especially `active_stage: spec_refresh_required`, route to `he-spec` with the compression contract instead of approving another additive implementation pass.
Explore first, ask second; use update_plan only for live progress; before writing durable docs choose `.harness/plan/**.md` from the artifact routing contract; when planning coding-harness-managed work load the execution slice contract and keep the plan inside the selected milestone, parent issue, refactor phase, or execution slice; turn scope into ordered implementation units; run or explicitly block coding-harness plan gates when the repo exposes them.
Explore first, ask second; use update_plan only for live progress; before writing durable docs choose `.harness/plan/**.md` from the artifact routing contract; when planning coding-harness-managed work load the execution slice contract and keep the plan inside the selected milestone, parent issue, refactor phase, or execution slice; turn scope into ordered implementation units; run or explicitly block coding-harness plan gates when the repo exposes them. Treat `.harness/strategy/*.md`, `.harness/triage/*.md`, `.harness/review/*.md`, and `.harness/features/*.md` as context unless the approved Linear/refactor slice admits them. For cockpit, golden-path, command-catalog, or agent-native compression work, plan subtractive proof before additive compatibility: name the exact first-contact budget, shrink default help, demote plumbing commands, require full catalogs to use an advanced/all flag, rewrite the README front door around the golden path, add admission tests, add fresh-agent eval, and require ablation decisions for every still-visible command family.
Inspect session-collector evidence and repo truth; for coding-harness-managed work load the execution slice contract before writing requirements; consume the approved `.harness/linear/<repo-name>-linear-plan.md`, selected `.harness/refactors/<selected-refactor>.md` when applicable, `.harness/decisions/*.md`, `.harness/core/*.md`, and `.harness/brainstorm/*.md` as primary inputs.
Inspect session-collector evidence and repo truth; for coding-harness-managed work load the execution slice contract before writing requirements; consume the approved `.harness/linear/<repo-name>-linear-plan.md`, selected `.harness/refactors/<selected-refactor>.md` when applicable, `.harness/decisions/*.md`, `.harness/core/*.md`, and `.harness/brainstorm/*.md` as primary inputs; use `.harness/strategy/*.md`, `.harness/triage/*.md`, `.harness/review/*.md`, and `.harness/features/*.md` only for evidence or context; stop if no selected milestone, parent issue, refactor phase, or execution slice is identified. Resolve/create the Linear tracker for non-trivial work; require Linear project, milestone, parent issue, sub-issues when present, labels, priority, dependencies, and agent/human route for tracked specs; before writing durable docs choose `.harness/specs/**.md` from the artifact routing contract; define scope, assumptions, assets/icon-small.png if packaging matters, explicit In Scope and Out of Scope boundaries, and handoff to plan with coding-harness state when applicable. When feedback says a prior cockpit, golden-path, or agent-native plan was too additive, load the compression contract and make first-contact budget, standalone command admission, docs deletion budget, fresh-agent eval, ablation proof, and evidence-backed metric gates blocking acceptance criteria.
Mark current active state; if `/goal` is active, confirm it matches the branch, issue, plan, or PR before editing and treat mismatches as blockers rather than overwriting project truth. Explore first, ask second; `update_plan` is live checklist only; for coding-harness-managed work load the execution slice contract and verify the plan/todo maps to one selected milestone, parent issue, refactor phase, or execution slice before editing.
Mark current active state; if `/goal` is active, confirm it matches the branch, issue, plan, or PR before editing and treat mismatches as blockers rather than overwriting project truth. Explore first, ask second; `update_plan` is live checklist only; for coding-harness-managed work load the execution slice contract and verify the plan/todo maps to one selected milestone, parent issue, refactor phase, or execution slice before editing; use external-delegate for bounded slices; run or explicitly block coding-harness blast-radius/policy/preflight/validation gates and record exact command/path plus smallest recovery step when blocked; handoff to he-code-review mode:autofix when needed.
```

The 2026-05-08 remote-branch merge preserved these compact-entrypoint and
fixture lines outside runtime bodies while retaining the merged contract updates:

```text
- `.harness/specs/*.md`
- do not recommend deleting or gitignoring Harness Engineering pipeline artifacts in `.harness/brainstorm/`, `.harness/plan/`, or `docs/solutions/`
- Which spec should I deepen? You can give me a path from `.harness/specs/` or `.harness/specs/`.
- "Route the handoff toward he-spec, he-plan, or he-work only after ambiguity is resolved."
Route with `route_skillset.py`; keep request text data-only; load only the chosen stage; before any new skill package is proposed, use session-evidence-skillify-triage.md; path fragments and bundle names are evidence labels for collector-backed improvement. When the request explicitly asks for persistent continuation, `/goal`, resume-over-time, or keep-working-until-done behavior, apply the goal continuity contract after selecting the HE stage and hand off durable board governance to `Skills/agent-ops/goal-governor`. When a diagnosis names compression as the missing acceptance gate or says `spec_refresh_required`, route to `he-spec` and include the compression contract.
```

The 2026-05-08 artifact identity update preserved these compact-entrypoint
lines outside runtime bodies while adding `.harness` identity and traceability
rules:

```text
Return schema_version when structured. schema_version: 1, severity findings, traceability, blockers, verdict, reproduction_status, security_review, real_behavior_proof, work_candidate, repeated_failure, blackboard_delta, next handoff, repeated context-feedback candidates.
Select mode first: review-only, readiness, repair/autofix, commit review, or investigation; review-only mode stays byte-clean. Read changed files and relevant review threads/comments; lead with file:line findings; Codex-compatible findings must be tight; check `Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`; in coding-harness-managed repos also check Project Brain, north-star evidence, and Harness review gates; use `evidence_ladder`. For disputed behavior or repeated bot feedback, require a proof loop before hypothesizing; see review loop patterns. For cockpit, golden-path, or command-catalog work, block readiness when the diff proves implementation presence but not first-contact compression, fresh-agent usability, or ablation. Do not approve readiness from green CI alone when real behavior proof, security review, or live PR-thread state is missing. Then approve/request/autofix. If feedback repeats across PRs, classify whether HE context, evals, or skill routing should adapt after the immediate review.
Explore first, ask second; use update_plan only for live progress; before writing durable docs choose `.harness/plan/**.md` from the artifact routing contract; for dedicated UI plans use `.harness/plan/**-ui-plan.md` and the UI plan routing contract, treating `docs/ui-plan/**` and `docs/ui-plans/**` as legacy source evidence and reporting Project Brain sync/defer/block status when `.harness/knowledge/**` is in use; when planning coding-harness-managed work load the execution slice contract, run the Linear Delta Capture Gate for existing tracked plans, and keep the plan inside the selected milestone, parent issue, refactor phase, or execution slice; turn scope into ordered implementation units; run or explicitly block coding-harness plan gates when the repo exposes them. Treat `.harness/strategy/*.md`, `.harness/triage/*.md`, `.harness/review/*.md`, and `.harness/features/*.md` as context unless the approved Linear/refactor slice admits them. For cockpit, golden-path, command-catalog, or agent-native compression work, plan subtractive proof before additive compatibility: name the exact first-contact budget, shrink default help, demote plumbing commands, require full catalogs to use an advanced/all flag, rewrite the README front door around the golden path, add admission tests, add fresh-agent eval, and require ablation decisions for every still-visible command family.
Inspect session-collector evidence and repo truth; for coding-harness-managed work load the execution slice contract before writing requirements; consume the approved `.harness/linear/<repo-name>-linear-plan.md`, selected `.harness/refactors/<selected-refactor>.md` when applicable, `.harness/decisions/*.md`, `.harness/core/*.md`, and `.harness/brainstorm/*.md` as primary inputs; use `.harness/strategy/*.md`, `.harness/triage/*.md`, `.harness/review/*.md`, and `.harness/features/*.md` only for evidence or context; stop if no selected milestone, parent issue, refactor phase, or execution slice is identified. Resolve/create the Linear tracker for non-trivial work; for existing tracked plans run the Linear Delta Capture Gate before consuming the approved slice, reconcile required labels, classify new or changed Linear issues, and promote at most one admitted item into the spec scope; require Linear project, milestone, parent issue, sub-issues when present, labels, priority, dependencies, and agent/human route for tracked specs; before writing durable docs choose `.harness/specs/**.md` from the artifact routing contract; define scope, assumptions, assets/icon-small.png if packaging matters, explicit In Scope and Out of Scope boundaries, and handoff to plan with coding-harness state when applicable. When feedback says a prior cockpit, golden-path, or agent-native plan was too additive, load the compression contract and make first-contact budget, standalone command admission, docs deletion budget, fresh-agent eval, ablation proof, and evidence-backed metric gates blocking acceptance criteria.
```

## Preservation Contract

- Active `SKILL.md` files stay concise and routing-safe.
- Removed operational prose belongs in stage-local `references/*` or `Infrastructure/references/harness-engineering/deferred-context-index.full.md`.
- `fixtures/preserved-context/**` preserves legacy full-stage guides for audit and migration comparison only.

## Plan Preserved Context

- `Plugins/harness-engineering/references/he-plan-doctrine.md`
- `Plugins/harness-engineering/skills/he-plan/references/codex-plan-mode.md`
- `Plugins/harness-engineering/skills/he-plan/references/plan-artifact-contract.md`
- `Plugins/harness-engineering/skills/he-plan/references/planning-depth.md`
- `Plugins/harness-engineering/skills/he-plan/references/deepening-review.md`
- `Plugins/harness-engineering/skills/he-plan/references/test-strategy.md`
- `Plugins/harness-engineering/skills/he-plan/references/visual-communication.md`

## Active Entrypoint Rewrite Preservation

The PR 152 review-fix pass preserved removed Goal Governor validator wording.
Goal Governor is now an independent skill at `Skills/agent-ops/goal-governor`;
active board validation examples live there:

```text
   - Existing board files pass `./bin/ask check_goal_board <goal-directory>`.
   - Existing board files pass `./bin/ask check_goal_board <goal-directory> --robot`.
   - Agent-driven runs append `--robot` to `./bin/ask check_goal_board <goal-directory>` for stable parsing.
```

The 2026-05-03 Harness Engineering tightening preserved these compact-entrypoint lines outside the runtime bodies:

```text
Explore first; separate evidence from guesses; route to he-spec, he-plan, or he-work only when ready.
description: "Use when fuzzy intent needs grounded HE options before spec, plan, or work."
Read changed files; lead with file:line findings; check `Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`; use `evidence_ladder`; Codex-compatible findings must be tight; then approve/request/autofix.
description: "Use when HE PRs, diffs, commits, CI, readiness, traceability, or autofix need review."
Inspect live state; pick stage order; keep Linear/spec/plan/PR links; refresh Project Brain when repository context changes.
description: "Use when HE work spans Linear, spec, plan, work, review, and PR state."
description: "Use when HE test, QA, CI, incident, or regression failures need reproduction and fixes."
description: "Use when HE wakeups, monitoring, until-green checks, or thread follow-through are needed."
Before any new skill package is proposed, inspect existing surfaces; label path fragments and bundle names as evidence labels; close coverage-gap items.
Redact secrets; preserve important context in references. Do not remove important context for budget trimming; move deep context to references.
description: "Use when HE hardening, optimization, polish, or capability improvement needs measurement."
Explore first, ask second; use update_plan only for live progress; turn scope into ordered implementation units.
description: "Use when approved specs or Linear issues need execution-ready HE plans before work."
- "Route this old `$he-refine` request through the current Harness Engineering surface."
- "The user asked for brainstorm and implementation in one message; decide the first lifecycle stage and preserve Linear traceability."
- "This HE request mentions a bug, plan drift, and CodeRabbit comments; pick the right stage and tell me what evidence is missing."
description: "Selects the correct Harness Engineering lifecycle stage and compatibility alias route. Use when a request is ambiguous, mixes brainstorm/spec/plan/work/review intent, references folded he-* aliases, or needs Linear/session evidence checked before loading a deeper stage."
Inspect session-collector evidence and repo truth; define scope, assumptions, assets/icon-small.png if packaging matters, and handoff to plan.
description: "Use when HE work needs Linear-backed scope, requirements, acceptance, and validation."
- For `JSC-246`, implement the approved account settings flow plan in delegate mode, keep `update_plan` as the live checklist, and return changed files plus verified slices.
- For a tiny low-risk fix, capture the current active state, make the smallest traceable edit, run the exact gate, and hand off to `he-code-review mode:autofix` if review findings remain.
Mark current active state; Explore first, ask second; `update_plan` is live checklist only; use external-delegate for bounded slices; handoff to he-code-review mode:autofix when needed.
description: "Use when approved HE plans or tiny low-risk tasks need traceable execution."
```

The 2026-05-08 Ask control-plane and proof-gate pass preserved compact
entrypoint meaning while moving active behavior into artifact-routing,
execution-slice, review-loop, and Linear-delta references. These retained lines
are context-preservation evidence for the progressive-disclosure gate:

```text
Return schema_version when structured. schema_version: 1, severity findings, traceability, blockers, verdict, repeated_failure when recurring, blackboard_delta, next handoff, repeated context-feedback candidates.
Read changed files; lead with file:line findings; check `Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`; in coding-harness-managed repos also check Project Brain, north-star evidence, and Harness review gates; use `evidence_ladder`; Codex-compatible findings must be tight; then approve/request/autofix. If CodeRabbit, Codex, or human review feedback repeats across PRs, classify whether the HE context, evals, or skill routing should adapt after the immediate review.
Return schema_version when structured. durable plan, complete replacement plan when revising, repo-relative file paths, risks, validation, Linear/spec/plan/PR traceability matrix, slack_policy, and blackboard_delta.
Return schema_version when structured. schema_version: 1, complete replacement spec section, Linear Acceptance Traceability, acceptance IDs, validation plan, and blackboard_delta.
```

The 2026-05-08 merge sync preserved the legacy dedicated UI plan path wording
from the full he-plan fixture while keeping `.harness/plan/` as the active
artifact home:

```text
- `docs/ui-plans/YYYY-MM-DD-<descriptive-name>-ui-plan.md`
- compatibility mode: `.harness/plan/YYYY-MM-DD-<topic>-ui-plan.md` only when the repo already uses that convention or the user explicitly requests it
- `docs/ui-plans/` for dedicated UI plans
```
