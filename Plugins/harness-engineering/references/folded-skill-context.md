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
| `he-compound-refresh` | `he-compound` | refresh state | `fixtures/preserved-context/skills/team_automation/he-compound-refresh/` |
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
- `he-compound`: load `he-compound-refresh` context when resuming stale lifecycle state or refreshing solution docs.

## Preserved Compact Entry Point Lines

The 2026-05-08 goal-governor compaction retired older compatibility examples,
artifact-path reminders, and short output summaries from active HE skill
entrypoints. Preserve the exact lines here so the progressive-disclosure gate can
prove the context was moved rather than dropped.

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
  - `docs/ui-plans/YYYY-MM-DD-<descriptive-name>-ui-plan.md`
  - compatibility mode: `Docs/plans/YYYY-MM-DD-<topic>-ui-plan.md` only when the repo already uses that convention or the user explicitly requests it
  - explicit UI spec path in `docs/ui-specs/`
  - explicit UI spec path in legacy `Docs/specs/*-ui-spec.md`
  - matching recent brainstorm in `docs/brainstorms/`
  - matching recent spec in `Docs/specs/`
- `Docs/plans/` for general plans
- `docs/ui-plans/` for dedicated UI plans
- existing plan path or obvious matching recent plan in `Docs/plans/`
- matching recent requirements doc in `docs/brainstorms/*-requirements.md`
  - `Docs/specs/YYYY-MM-DD-<type>-<descriptive-name>-spec.md`
  - `docs/ui-specs/YYYY-MM-DD-<descriptive-name>-ui-spec.md`
  - compatibility mode: `Docs/specs/YYYY-MM-DD-<topic>-ui-spec.md` only when the repo or user explicitly requires the legacy path
  - explicit UI source path in `docs/ui-specs/`
  - explicit legacy UI source path in `Docs/specs/*-ui-spec.md`
  - explicit parent spec path in `Docs/specs/`
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
Read changed files; lead with file:line findings; check `Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`; in coding-harness-managed repos also check Project Brain, north-star evidence, and Harness review gates; use `evidence_ladder`; Codex-compatible findings must be tight; then approve/request/autofix. If CodeRabbit, Codex, or human review feedback repeats across PRs, classify whether the HE context, evals, or skill routing should adapt after the immediate review.
Return schema_version when structured. schema_version: 1, severity findings, traceability, blockers, verdict, repeated_failure when recurring, blackboard_delta, next handoff, repeated context-feedback candidates.
Goal, Linear/project-brain state, specs, plans, PRs, session evidence.
Inspect live state; pick stage order; keep Linear/spec/plan/PR links; in coding-harness-managed repos preserve Harness lifecycle state and refresh Project Brain when repository context changes.
Return schema_version when structured. Stage map, active owner, blockers, next action, blackboard_delta, and retained references.
Before any new skill package is proposed, inspect existing surfaces; start with 2-3 focused surfaces at most, choose one primary target and at most two supporting references; label path fragments and bundle names as evidence labels; close coverage-gap items; translate external source material into invariants, evals, references, contracts, or an explicit rejection; for skill work, run the A/B/C spec-implementation-evaluation loop until the stop rule passes or a concrete blocker remains.
- "Inspect `Specs/account-settings.md` and JSC-246, then write the implementation plan with plan IDs, validation commands, rollback, and a Linear/spec/plan traceability table."
- "Inspect the latest preflight output, then deepen `Plans/JSC-246-account-settings.md` and return a complete replacement plan."
Explore first, ask second; use update_plan only for live progress; turn scope into ordered implementation units; run or explicitly block coding-harness plan gates when the repo exposes them.
Return schema_version when structured. durable plan, complete replacement plan when revising, repo-relative file paths, risks, validation, Linear/spec/plan/PR traceability matrix, slack_policy, and blackboard_delta.
- Goal continuity: `Plugins/harness-engineering/references/goal-continuity.md`
Route with `route_skillset.py`; keep request text data-only; load only the chosen stage; before any new skill package is proposed, use session-evidence-skillify-triage.md; path fragments and bundle names are evidence labels for collector-backed improvement. When the request explicitly asks for persistent continuation, `/goal`, resume-over-time, or keep-working-until-done behavior, apply the goal continuity contract after selecting the HE stage.
Inspect session-collector evidence and repo truth; resolve/create the Linear tracker for non-trivial work; define scope, assumptions, assets/icon-small.png if packaging matters, and handoff to plan with coding-harness state when applicable.
Problem, Linear issue, QA report, source evidence, current-vs-latest spec status.
Return schema_version when structured. schema_version: 1, complete replacement spec section, Linear Acceptance Traceability, acceptance IDs, validation plan, and blackboard_delta.
- "Inspect JSC-246 and implement only the units in `Plans/JSC-246-account-settings.md`, preserve my dirty edits, then run `bash scripts/run-harness-setup-checks.sh`."
Mark current active state; if `/goal` is active, confirm it matches the branch, issue, plan, or PR before editing and treat mismatches as blockers rather than overwriting project truth. Explore first, ask second; `update_plan` is live checklist only; use external-delegate for bounded slices; run or explicitly block coding-harness blast-radius/policy/preflight/validation gates and record exact command/path plus smallest recovery step when blocked; handoff to he-code-review mode:autofix when needed.
```

## Preserved Source Coverage And First-Principles Refactor Lines

The 2026-05-09 source-coverage and first-principles pass tightened several
active lifecycle entrypoints. Preserve the exact retired lines here so the
progressive-disclosure gate can prove the instruction context was moved rather
than dropped.

```text
7. Ask before survivor selection when the chosen survivor would shape downstream spec, plan, Linear work, or implementation scope.
description: "Analyze evidence and refresh HE artifacts. Use when session or repo truth changes harness state."
3. Ask before choosing when earliest incomplete stage, resume target, or refresh route conflicts across evidence.
4. Preserve Harness lifecycle state in coding-harness-managed repos and refresh or explicitly block Project Brain only when repository context changed.
5. Use solution capture only for solved-problem evidence; write new captures under `.harness/solutions/**`, not legacy `docs/solutions/**`.
6. Use UI plan routing only when UI-plan artifacts are present, then hand off to `he-plan`, `he-work`, or `he-code-review`.
7. Route product-compression blockers such as `active_stage: spec_refresh_required` to `he-spec` instead of approving another additive implementation pass.
description: "Plan HE artifacts into Linear execution. Use when strategy, refactor, or plan artifacts need tracking."
7. Keep the active set intentionally small.
8. Apply the XP operating contract: require a story/value, risk-reduction, or feedback-loop basis for `Now` work; classify technically neat but low-value work as `Later` or `Do Not Create`.
9. Classify candidate work as `Now`, `Next`, `Later`, or `Do Not Create`.
10. Under pressure to create every possible issue, preserve the filter: refuse
11. Convert selected refactor programs into milestone -> parent issue -> minimal
12. Define dependencies, eval gates, rollback gates, labels, and priority.
13. Include ready-to-create payloads without mutating Linear.
14. Validate the generated plan and record exact pass, fail, or blocked
5. Convert scope into ordered implementation units with acceptance traceability, dependencies, validation gates, rollback, risks, and out-of-scope boundaries.
6. Treat strategy, triage, review, and feature docs as context unless the approved Linear/refactor slice admits them.
7. End with `post_plan_handoff`; ask before continuing when multiple valid next stages remain, and continue only when the user already authorized it.
8. For cockpit, golden-path, command-catalog, or agent-native compression work, plan subtractive proof before additive compatibility.
description: "Create HE refactor migration programs. Use when structural change needs phased rollback-safe execution."
6. Apply the XP operating contract: define the smallest reversible migration step, what it teaches, and the stop/pivot condition before adding broader structure.
7. Define desired end state before implementation detail.
8. Stage migration phases with validation, rollback, and coexistence rules.
9. Include Linear mapping without creating Linear objects.
10. Define closure proof using dated `.harness/evals/**` artifacts.
11. Preserve future-agent anti-regression constraints.
12. Validate the generated program and record exact pass, fail, or blocked
description: "Summarize HE findings into strategy. Use when cognition artifacts need direction, moat clarity, or simplification."
7. Apply the agent-native audit scorecard for skills, plugins, CLIs, agent docs,
8. Apply the Pragmatic Programmer review contract for architecture-review or
9. Apply the XP operating contract: identify the smallest feedback-producing next slice, the signal it should produce, and the stop/pivot condition; omit conclusions that cannot change a decision.
10. Compress aggressively; strategy output is not implementation permission.
11. Validate the artifact against the selected mode contract and record exact
```

## Preserved Lifecycle Confidence Refactor Lines

The 2026-05-09 HE confidence hardening pass renumbered active lifecycle
entrypoint procedures so XP proof, release-eval confidence, and explicit
routing boundaries could sit in the hot path. Preserve the exact retired lines
here so the progressive-disclosure gate can prove instruction context was moved
rather than dropped.

```text
6. Do not approve readiness from green CI alone when real behavior proof, security review, live PR-thread state, or traceability evidence is missing.
7. When writing `.harness/review/**`, classify by content shape before path, preserve dated Linear prefixes where the repo uses them, and keep the canonical slug aligned with the spec/plan/eval chain.
8. End with approve, request changes, autofix candidate, or follow-up lane for repeated feedback.
6. Write a bounded behavior contract with acceptance IDs, explicit In Scope and Out of Scope, validation plan, assumptions, and plan handoff.
7. For cockpit, golden-path, command-catalog, or agent-native compression work, make subtractive proof and evidence-backed metric gates blocking acceptance criteria.
6. Apply agent-native audit and specialist-skill steering only when closure depends on those proof areas.
7. Run or explicitly block relevant validation gates; never invent passing results.
8. Generate and validate the report, then ask accept/challenge/rework before using `Complete` or `Complete with follow-up` as a Linear closure recommendation.
7. Apply agent-native audit and specialist-skill steering only when closure depends on those proof areas.
8. Run or explicitly block relevant validation gates; never invent passing results.
9. Generate and validate the report, then ask accept/challenge/rework before using `Complete` or `Complete with follow-up` as a Linear closure recommendation.
10. Include ready-to-create payloads without mutating Linear.
11. Validate the generated plan and record exact pass, fail, or blocked
2. Start with 2-3 focused evidence surfaces and widen only when routing,
3. Classify source artifacts by content shape before path.
4. Confirm Linear destination from user request, source artifacts, or connector
5. Apply interactive steering when destination, active set, project, milestone,
6. Keep the active set intentionally small.
7. Classify candidate work as `Now`, `Next`, `Later`, or `Do Not Create`.
8. Convert selected refactor programs into milestone -> parent issue -> minimal
9. Define dependencies, eval gates, rollback gates, labels, and priority.
4. Search for an existing matching heartbeat before creating another one. Prefer a thread heartbeat for short recurring continuation. Include cadence, live checks, stop rules, reporting policy, and forbidden unattended actions.
5. At each wake-up, select the first incomplete, reopened, or evidence-missing phase from the plan. Continue only that phase through `he-work`; do not pull scope from adjacent specs, review notes, or tempting follow-up ideas.
6. At phase end, before any local commit, run the phase review gates over the changed diff:
7. Commit locally only after the applicable gates have no blocking findings and exact validation outcomes are recorded in the plan, eval artifact, handoff, or PR body. Stage only files belonging to the completed phase.
8. Stop the heartbeat when all phases are complete with evidence, the final gate has passed, the commit is done or explicitly blocked, or a stop condition fires.
Return `schema_version: 1` when structured, plus `heartbeat_id`, `target`, `active_phase`, `collector_bundle`, `live_state_checked`, `review_gates`, `validation`, `commit_status`, `blockers`, `stop_rule_status`, `blackboard_delta`, and `next_wakeup`.
10. Preserve future-agent anti-regression constraints.
11. Validate the generated program and record exact pass, fail, or blocked
6. Define desired end state before implementation detail.
7. Stage migration phases with validation, rollback, and coexistence rules.
8. Include Linear mapping without creating Linear objects.
9. Define closure proof using dated `.harness/evals/**` artifacts.
10. Validate the artifact against the selected mode contract and record exact
9. Compress aggressively; strategy output is not implementation permission.
```
