# Harness Engineering Deferred Context Index

This reference preserves context moved out of active `SKILL.md` entrypoints during budget hardening.

Use this file when you need detailed stage doctrine, extended examples, legacy/archive context, or full stage asset/script references that are intentionally deferred from always-loaded entrypoints.

In this index, archive means preserved deferred context used by active skills, not deprecated or inactive guidance.

## Preserved Context

- Full stage guides and preserved references remain in `fixtures/preserved-context/**`.
- `fixtures/skill-archive` remains a compatibility alias for older links only.
- Canonical contract/eval/task profiles remain in each stage under `Infrastructure/references/**`.
- Canonical subagent role policy remains in:
  - `references/routing-map.json`
  - `references/subagent-routing.md`
- Canonical deterministic stage-routing policy remains in:
  - `references/deterministic-stage-routing.md`
- Canonical domain-model routing policy remains in:
  - `references/domain-model-routing.md`
- Canonical session-evidence routing policy remains in:
  - `references/session-evidence-contract.md`
- Canonical QA intake routing policy remains in:
  - `references/qa-intake-routing.md`
- Router role-resolution policy for `he-router` requires checking `~/.codex/agents/manifest.json` and preferring `he-*` mapped roles when available in the stage map.
- The `he-router` execution contract now treats `he-*` stage-map role entries as first priority, with manifest lookups used to resolve concrete reviewer names only after stage-map preference.

## Budget Trim Preservation

The following lines were intentionally moved out of active or fixture `SKILL.md` entrypoints during context-budget hardening. They remain preserved here for auditability and historical review of the compacted flow contracts.

The QA intake routing refresh preserved these pre-insertion procedure lines:

- `2. Map service boundaries and dependency failure paths.`
- `3. Produce reliability findings with concrete blast-radius and mitigation guidance.`
- `4. Route review subagents per policy; if unavailable, continue inline and state manual role options.`
- `2. Produce a failing test first (RED), then apply the smallest fix (GREEN).`
- `3. Repeat in vertical slices and preserve traceability to accepted behavior targets.`
- `4. Route supporting subagents per policy; if unavailable, continue inline and state manual role options.`

The session-evidence routing refresh preserved these pre-insertion `he-compound` procedure lines:

- `6. If helpers are used during learning capture, they return text only; the orchestrator writes the final artifact.`
- `7. If overlap with an existing solution is high, refresh the existing doc instead of creating a duplicate.`
- ``8. Recommend `he-compound-refresh` only when adjacent stale or overlapping docs need selective follow-up beyond the current artifact.``

- Preserved step 6: If helpers are used during learning capture, they return text only; the orchestrator writes the final artifact.
- Preserved step 7: If overlap with an existing solution is high, refresh the existing doc instead of creating a duplicate.
- Preserved step 8: Recommend `he-compound-refresh` only when adjacent stale or overlapping docs need selective follow-up beyond the current artifact.

The router and work-entry compacting pass preserved these previously inline lines:

- `schema_version: 1` when structured output is requested.
- issue creation/update via `[[gh-workflow]]` or repo tracker
- Preserved step 8: Resolve mapped roles from `~/.codex/agents/manifest.json`, preferring `he-*` roles when available in the stage map.

The session-evidence and reliability refresh preserved these compacted entrypoint lines:

This entrypoint stays concise and keeps full operational context in archived references.
- For full stage policy, workflow details, and examples, load the archived full guide.
- Preserved step 1: Load archived reliability references before analysis.
- Preserved step 4: Produce reliability findings with concrete blast-radius and mitigation guidance.
- Preserved step 5: Route review subagents per policy; if unavailable, continue inline and state manual role options.
- Refresh durable knowledge from evidence, not intuition.
- Review individual learnings before derived pattern docs.
- Prefer no-write `Keep` decisions over churn when a doc is still trustworthy.
- Use when overlapping solution docs should be consolidated with explicit evidence.
- Use when a specific learning or pattern doc is called stale, overlapping, drifted, or superseded.
- If no candidate docs exist under `docs/solutions/`, stop and report that no refresh targets were found.
- If a scope hint finds no matches, report the miss clearly; in autonomous mode, stop without guessing.
- If replacement evidence is insufficient, do not invent a successor doc. Mark the artifact stale when possible and report what evidence is missing.
- Request, artifacts, repo context, and linked Linear issues.
- `schema_version: 1` when structured; result, validation, blockers, and next Harness Engineering action.
- Preserved step 2: Discover candidate docs under `docs/solutions/`, excluding `README.md` and legacy `_archived/` content.
- Preserved step 3: Match the narrowest successful scope first: directory, frontmatter, filename, then content search.
- Preserved step 4: Investigate individual learnings before dependent pattern docs.
- Preserved step 5: Analyze the document set for overlap, contradictions, and canonical-doc opportunities before leaving duplicates in place.
- Preserved step 6: Classify each artifact or overlap cluster into exactly one maintenance outcome: `Keep`, `Update`, `Consolidate`, `Replace`, `Archive`, or `Stale`.
- Preserved step 7: In autonomous mode, apply unambiguous actions directly and stale-mark ambiguous cases instead of guessing through them.
- Preserved step 8: Finish with a full markdown report covering evidence, actions applied, and recommendations when writes could not be completed.
- Ensure each refresh claim is backed by current repository evidence.
- Ensure learnings are reviewed before dependent patterns.
- Ensure overlap analysis happens before duplicate docs are left in place.
- Performing broad doc rewrites without evidence-backed stale signals.
- "Can you inspect the compound run state and tell me which docs are stale after this refactor?"
- Preserved step 3: Select the underlying HE stage that should run on each wake-up. If stage
- Preserved step 4: Build the durable heartbeat prompt using the contract below and the full
- Preserved step 5: Create or describe the automation only when the runtime exposes an automation
- Preserved step 6: Execute the first safe live-state check immediately in the current turn.
- Preserved step 7: Tell the user how the heartbeat will stop or when it will ask for human
- Preserved step 2: Decide whether the target should use direct hard metrics, judge scoring, or hybrid gates plus judge evaluation.
- Preserved step 3: Detect and resolve `fresh` versus `resume` state before running new experiments.
- Preserved step 4: Establish a trusted baseline with the measurement harness and run the parallel-readiness probe before widening execution.
- Preserved step 5: Run bounded iterations with explicit measurement gates and isolated experiment state.
- Preserved step 6: After each experiment, write results to disk immediately, verify the write, and only then report or compare outcomes.
- Preserved step 7: Keep, revise, or discard changes based on measured outcomes and route proven results to the next stage.
- Preserved step 4: Build synchronized tasks from the governing artifact and keep task state aligned with markdown artifact state during execution.
- Preserved step 5: Implement in small verified slices, honoring execution posture signals such as `test-first` or `characterization-first`.
- Preserved step 6: Stop and update the governing artifact or linked Linear issue before continuing if execution uncovers contract drift, domain drift, hidden scope, or changed boundaries.
- Preserved step 7: Report completed work, blockers, validation evidence, and the shipping handoff package.
- Preserved step 6: Route QA session, conversational bug-report, or feedback-to-Linear requests by expected-behavior clarity: clear single/multiple defects to `he-fix-bugs`, unclear expected behavior to `he-brainstorm` or `he-spec`, issue-set sequencing to `he-plan`.
- Preserved step 7: Resolve mapped roles from `~/.codex/agents/manifest.json`, preferring `he-*` roles when available in the stage map.
- Preserved step 8: Return outputs with `selected_stage`, `matched_rule`, `confidence`, `rationale`, `recommended_next_step`, and `missing_input` only when blocked.
- Preserved step 9: If still ambiguous after applying the table, return blocked with exactly one missing input instead of guessing.

- Preserved step 2: Map service boundaries and dependency failure paths.
- Preserved step 3: Produce reliability findings with concrete blast-radius and mitigation guidance.
- Preserved step 4: Route review subagents per policy; if unavailable, continue inline and state manual role options.
- Preserved step 2: Produce a failing test first (RED), then apply the smallest fix (GREEN).
- Preserved step 3: Repeat in vertical slices and preserve traceability to accepted behavior targets.
- Preserved step 4: Route supporting subagents per policy; if unavailable, continue inline and state manual role options.

- Preserved step 2: Deepen interfaces, lifecycle behavior, and failure handling.
- Preserved step 2: Map service boundaries and dependency failure paths.
- Preserved step 2: Produce a failing test first (RED), then apply the smallest fix (GREEN).
- Preserved step 2: Reproduce and stabilize the failing behavior before proposing changes.
- Preserved step 3: Build synchronized tasks from the governing artifact and keep task state aligned with markdown artifact state during execution.
- Preserved step 3: For incoming feedback: read, clarify unclear items, verify, then respond technically.
- Preserved step 3: Produce the specification artifact with concrete acceptance criteria.
- Preserved step 3: Produce reliability findings with concrete blast-radius and mitigation guidance.
- Preserved step 3: Repeat in vertical slices and preserve traceability to accepted behavior targets.
- Preserved step 3: Resolve mapped roles from `~/.codex/agents/manifest.json`, preferring `he-*` roles when available in the stage map.
- Preserved step 3: Return readiness outcome and next stage recommendation.
- Preserved step 3: Trace backward from the symptom to the point where valid state first became invalid.
- Preserved step 4: Generate 2-3 concrete approaches when multiple plausible directions remain, then evaluate tradeoffs and recommend one.
- Preserved step 4: If source material is unclear or incomplete, run a lightweight planning bootstrap to establish enough context without leaving planning mode.
- Preserved step 4: Implement in small verified slices, honoring execution posture signals such as `test-first` or `characterization-first`.
- Preserved step 4: Return findings-first output plus open questions and next action.
- Preserved step 4: Return outputs.
- Preserved step 4: Route research and review roles per routing policy; if unavailable, continue inline and state manual role options.
- Preserved step 4: Route review subagents per policy; if unavailable, continue inline and state manual role options.
- Preserved step 4: Route supporting subagents per policy; if unavailable, continue inline and state manual role options.
- Preserved step 4: Test one hypothesis at a time, and for uncertain links require a prediction that can confirm or falsify the chain.
- Preserved step 5: Capture durable requirements only when the discussion produced decisions worth preserving.
- Preserved step 5: If still ambiguous after one clarification, return blocked with missing input.
- Preserved step 5: Present the root cause, proposed fix scope, and test recommendations before remediation when the request is diagnosis-first or confidence is still settling.
- Preserved step 5: Research local patterns and prior learnings before finalizing structure when they materially affect sequencing or risk.
- Preserved step 5: Review for correctness, regression risk, operability, protected-artifact handling, and release readiness.
- Preserved step 5: Stop and update the governing artifact before continuing if execution uncovers contract drift, hidden scope, or changed boundaries.
- Preserved step 6: Recommend the next Harness Engineering stage and stop instead of drifting into implementation planning.
- Preserved step 6: Report completed work, blockers, validation evidence, and the shipping handoff package.
- Preserved step 6: Size the plan depth to the work, then decompose into ordered, verifiable tasks with explicit dependencies, tests, and next-stage handoff.
- Preserved step 6: When remediation is in scope, check workspace safety, prefer failing-test-first validation, apply the minimal fix, and verify no regressions.

The PR 136 main-sync refresh preserved these lines removed from compact runtime and archive entrypoints:

- `Read when: examples or role-routing details are needed, open the archived references for this skill.`
- `description: Refine Harness Engineering artifacts, plans, specs, or work into clearer next actions. Use when users ask for tightening, simplification, or lifecycle flow repair.`
- `## Philosophy`
- `## Subagent Routing`
- `## Validation`
- `- Apply the mapped stage policy before spawning helpers.`
- `- Approval flow: [../../shared/references/approval-flow.md](../../shared/references/approval-flow.md)`
- `- Assets: [./assets](./assets)`
- `- Assets: `./assets``
- `- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)`
- `- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).`
- `- Do not remove important context for budget trimming; move it to references and index it in `../../../references/deferred-context-index.md`.`
- `- Do not remove important context for budget trimming; move it to references and index it in `../../references/deferred-context-index.md`.`
- `- Domain model routing: `../../../references/domain-model-routing.md``
- `- Ensure exactly one selected stage, one next invocation, request evidence, and blocked output when required inputs are missing.`
- `- Ensure new caller-facing interfaces and domain terms are specified before implementation tasks.`
- `- Fail fast: stop at first failed gate and do not proceed.`
- `- For full stage policy, workflow details, and examples, load the archived full guide.`
- `- If mapped roles are missing, continue inline and tell the user to provision the role with [$codex-agent-creator](/Users/jamiecraik/dev/agent-skills/Skills/agent-ops/codex-agent-creator/SKILL.md).`
- `- If roles are missing, continue inline and route role provisioning to `[[codex-agent-creator]]`.`
- `- Link Linear decision notes when durable tradeoffs shaped the plan.`
- `- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)`
- `- Preserve evidence, safety, and deterministic Harness Engineering routing.`
- `- QA intake routing: [../../../references/qa-intake-routing.md](../../../references/qa-intake-routing.md)`
- `- QA intake routing: `../../../references/qa-intake-routing.md``
- `- Replanning from scratch when a current plan should be updated.`
- `- Request, artifacts, repo context, and linked Linear issues.`
- `- Resolve roles from `~/.codex/agents/manifest.json` before delegation.`
- `- Routing to execution while the user is still asking for planning.`
- `- Stay in planning mode when directly invoked.`
- `- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)`
- `- Subagent routing: `../../../references/subagent-routing.md``
- `- Use when a spec, brainstorm, bug report, or raw feature description must become a durable implementation plan.`

Read when: examples or role-routing details are needed, open the archived references for this skill.
description: Refine Harness Engineering artifacts, plans, specs, or work into clearer next actions. Use when users ask for tightening, simplification, or lifecycle flow repair.
- `- `schema_version: 1` when structured; result, validation, blockers, and next Harness Engineering action.`
- `1. Load archived TDD guidance and choose the first behavior slice.`
- `1. Resolve the best source: existing plan, requirements doc, spec, brainstorm output, Linear issue, or direct request.`
- `2. Apply the deterministic decision order in `../../references/deterministic-stage-routing.md` because overlapping requests must route the same way every time.`
- `2. Resume or deepen a matching current plan instead of duplicating it.`
- `3. Carry forward problem frame, scope, requirements, and open questions from the authoritative artifact.`
- `4. Check interface and domain readiness before task decomposition; route to `he-deepen-spec` when contracts or terms are missing.`
- `4. Reproduce and stabilize the failing behavior before proposing changes.`
- `5. Put blockers first for Linear QA issue sets, preserve issue links, and keep independent defects parallel.`
- `5. Trace backward from the symptom to the point where valid state first became invalid.`
- `6. Research local patterns only when they affect sequencing or risk.`
- `6. Test one hypothesis at a time, and for uncertain links require a prediction that can confirm or falsify the chain.`
- `7. Decompose into ordered, verifiable tasks with dependencies, tests, and next-stage handoff.`
- `7. Present the root cause, proposed fix scope, and test recommendations before remediation when the request is diagnosis-first or confidence is still settling.`
- `8. When remediation is in scope, check workspace safety, prefer failing-test-first validation, apply the minimal fix, and verify no regressions.`
- `Read `../shared/references/approval-flow.md` before deciding whether to continue, ask a blocker question, or stop for approval.`
- `Read when: examples or role-routing details are needed, open the archived references for this skill.`
- `This entrypoint stays concise and keeps full operational context in archived references.`
- `description: Clarify problem scope, requirements, options, and expected behavior before spec or plan stages. Use when what to build, why it matters, or the right direction is ambiguous.`
- `description: Create Harness Engineering specs that define behavior, boundaries, acceptance criteria, and Linear decision notes. Use when users ask to turn clarified requirements into a durable contract.`
- `description: Create or update an execution plan from an approved spec or clarified scope. Use when work needs sequencing, validation gates, and Linear-aware task breakdown before implementation.`
- `description: Debug Harness Engineering bugs with reproduction evidence and regression coverage. Use when defects are reproducible, QA failures have expected behavior, or bugfix validation is required.`
- `description: Execute an approved plan, todo list, or tightly scoped spec with traceable progress and validation. Use when Harness Engineering work should be implemented.`
- `description: Improve an existing Harness Engineering spec with missing behavior, boundaries, domain terms, and acceptance criteria. Use when a user asks to deepen or complete a spec before planning.`
- `description: Review Harness Engineering diffs, PRs, plans, or implemented work for merge readiness and regression risk. Use when users ask for a go/no-go review.`
- `description: Review diffs, PRs, specs, plans, or feedback for technical correctness. Use when engineering risks or review-feedback validity must be verified before implementation.`
- `description: Review reliability risks in diffs, plans, specs, or fixes. Use when failures, retries, concurrency, data integrity, or operational resilience need evidence-backed review.`
- `description: Route ambiguous Harness Engineering requests to one lifecycle stage. Use when users ask where to start, resume, plan, implement, review, debug, or resolve terminology.`

The `he-heartbeat` routing refresh preserved the prior `he-router` tail steps
before inserting the recurring-loop route:

- `5. Route QA session, conversational bug-report, or feedback-to-Linear requests by expected-behavior clarity: clear single/multiple defects to `he-fix-bugs`, unclear expected behavior to `he-brainstorm` or `he-spec`, issue-set sequencing to `he-plan`.`
- `6. Resolve mapped roles from `~/.codex/agents/manifest.json`, preferring `he-*` roles when available in the stage map.`
- `7. Return outputs with selected_stage, matched_rule, confidence, rationale, recommended_next_step, and missing_input only when blocked.`
- `8. If still ambiguous after applying the table, return blocked with exactly one missing input instead of guessing.`

The `he-heartbeat` prompt-contract refresh preserved the previous fixture
reference wording before replacing it with package-relative paths:

- `Infrastructure/references/automation-prompt-contract.md`
- `` `Infrastructure/references/automation-prompt-contract.md` for the full prompt``
- `template.`
- ``Read `Infrastructure/references/automation-prompt-contract.md` when writing a``
- `new heartbeat prompt, reviewing a heartbeat prompt, or repairing a drifted loop.`

```text
`Infrastructure/references/automation-prompt-contract.md` for the full prompt
template.
Read `Infrastructure/references/automation-prompt-contract.md` when writing a
new heartbeat prompt, reviewing a heartbeat prompt, or repairing a drifted loop.
```

Exact moved-line preservation for the progressive-disclosure gate:

```text
## Philosophy
## Subagent Routing
## Validation
- Apply the mapped stage policy before spawning helpers.
- Approval flow: [../../shared/references/approval-flow.md](../../shared/references/approval-flow.md)
- Assets: [./assets](./assets)
- Assets: `./assets`
- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).
- Do not remove important context for budget trimming; move it to references and index it in `../../../references/deferred-context-index.md`.
- Do not remove important context for budget trimming; move it to references and index it in `../../references/deferred-context-index.md`.
- Domain model routing: `../../../references/domain-model-routing.md`
- Ensure exactly one selected stage, one next invocation, request evidence, and blocked output when required inputs are missing.
- Ensure new caller-facing interfaces and domain terms are specified before implementation tasks.
- Fail fast: stop at first failed gate and do not proceed.
- For full stage policy, workflow details, and examples, load the archived full guide.
- If mapped roles are missing, continue inline and tell the user to provision the role with [$codex-agent-creator](/Users/jamiecraik/dev/agent-skills/Skills/agent-ops/codex-agent-creator/SKILL.md).
- If roles are missing, continue inline and route role provisioning to `[[codex-agent-creator]]`.
- Link Linear decision notes when durable tradeoffs shaped the plan.
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- Preserve evidence, safety, and deterministic Harness Engineering routing.
- QA intake routing: [../../../references/qa-intake-routing.md](../../../references/qa-intake-routing.md)
- QA intake routing: `../../../references/qa-intake-routing.md`
- Replanning from scratch when a current plan should be updated.
- Request, artifacts, repo context, and linked Linear issues.
- Resolve roles from `~/.codex/agents/manifest.json` before delegation.
- Routing to execution while the user is still asking for planning.
- Stay in planning mode when directly invoked.
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Subagent routing: `../../../references/subagent-routing.md`
- Use when a spec, brainstorm, bug report, or raw feature description must become a durable implementation plan.
- `schema_version: 1` when structured; result, validation, blockers, and next Harness Engineering action.
- Preserved step 1: Load archived TDD guidance and choose the first behavior slice.
- Preserved step 1: Resolve the best source: existing plan, requirements doc, spec, brainstorm output, Linear issue, or direct request.
- Preserved step 2: Apply the deterministic decision order in `../../references/deterministic-stage-routing.md` because overlapping requests must route the same way every time.
- Preserved step 2: Resume or deepen a matching current plan instead of duplicating it.
- Preserved step 3: Carry forward problem frame, scope, requirements, and open questions from the authoritative artifact.
- Preserved step 4: Check interface and domain readiness before task decomposition; route to `he-deepen-spec` when contracts or terms are missing.
- Preserved step 4: Reproduce and stabilize the failing behavior before proposing changes.
- Preserved step 5: Put blockers first for Linear QA issue sets, preserve issue links, and keep independent defects parallel.
- Preserved step 5: Trace backward from the symptom to the point where valid state first became invalid.
- Preserved step 6: Research local patterns only when they affect sequencing or risk.
- Preserved step 6: Test one hypothesis at a time, and for uncertain links require a prediction that can confirm or falsify the chain.
- Preserved step 7: Decompose into ordered, verifiable tasks with dependencies, tests, and next-stage handoff.
- Preserved step 7: Present the root cause, proposed fix scope, and test recommendations before remediation when the request is diagnosis-first or confidence is still settling.
- Preserved step 8: When remediation is in scope, check workspace safety, prefer failing-test-first validation, apply the minimal fix, and verify no regressions.
Read `../shared/references/approval-flow.md` before deciding whether to continue, ask a blocker question, or stop for approval.
Read when: examples or role-routing details are needed, open the archived references for this skill.
This entrypoint stays concise and keeps full operational context in archived references.
description: Clarify problem scope, requirements, options, and expected behavior before spec or plan stages. Use when what to build, why it matters, or the right direction is ambiguous.
description: Create Harness Engineering specs that define behavior, boundaries, acceptance criteria, and Linear decision notes. Use when users ask to turn clarified requirements into a durable contract.
description: Create or update an execution plan from an approved spec or clarified scope. Use when work needs sequencing, validation gates, and Linear-aware task breakdown before implementation.
description: Debug Harness Engineering bugs with reproduction evidence and regression coverage. Use when defects are reproducible, QA failures have expected behavior, or bugfix validation is required.
description: Execute an approved plan, todo list, or tightly scoped spec with traceable progress and validation. Use when Harness Engineering work should be implemented.
description: Improve an existing Harness Engineering spec with missing behavior, boundaries, domain terms, and acceptance criteria. Use when a user asks to deepen or complete a spec before planning.
description: Review Harness Engineering diffs, PRs, plans, or implemented work for merge readiness and regression risk. Use when users ask for a go/no-go review.
description: Review diffs, PRs, specs, plans, or feedback for technical correctness. Use when engineering risks or review-feedback validity must be verified before implementation.
description: Review reliability risks in diffs, plans, specs, or fixes. Use when failures, retries, concurrency, data integrity, or operational resilience need evidence-backed review.
description: Route ambiguous Harness Engineering requests to one lifecycle stage. Use when users ask where to start, resume, plan, implement, review, debug, or resolve terminology.
```

## Stage Archive Paths

- `he-router`: `skills/he-router/references/*` (active canonical), plus router policy in `references/routing-map.json`.
- Domain-model workflow: `references/domain-model-routing.md`
- QA intake workflow: `references/qa-intake-routing.md`
- Deterministic stage routing: `references/deterministic-stage-routing.md`
- `he-code-review`: `fixtures/preserved-context/skills/code_quality_review/he-code-review/`
- `he-reliability-review`: `fixtures/preserved-context/skills/code_quality_review/he-reliability-review/`
- `he-technical-review`: `fixtures/preserved-context/skills/code_quality_review/he-technical-review/`
- `he-brainstorm`: `fixtures/preserved-context/skills/team_automation/he-brainstorm/`
- `he-compound`: `fixtures/preserved-context/skills/team_automation/he-compound/`
- `he-compound-refresh`: `fixtures/preserved-context/skills/team_automation/he-compound-refresh/`
- `he-deepen-plan`: `fixtures/preserved-context/skills/team_automation/he-deepen-plan/`
- `he-deepen-spec`: `fixtures/preserved-context/skills/team_automation/he-deepen-spec/`
- `he-fix-bugs`: `fixtures/preserved-context/skills/team_automation/he-fix-bugs/`
- `he-ideate`: `fixtures/preserved-context/skills/team_automation/he-ideate/`
- `he-improve`: `fixtures/preserved-context/skills/team_automation/he-improve/`
- `he-plan`: `fixtures/preserved-context/skills/team_automation/he-plan/`
- `he-prune-branches`: `fixtures/preserved-context/skills/team_automation/he-prune-branches/`
- `he-refine`: `fixtures/preserved-context/skills/team_automation/he-refine/`
- `he-spec`: `fixtures/preserved-context/skills/team_automation/he-spec/`
- `he-tdd`: `fixtures/preserved-context/skills/team_automation/he-tdd/`
- `he-work`: `fixtures/preserved-context/skills/team_automation/he-work/`

## Preservation Contract

- Active `SKILL.md` files should remain concise and routing-safe.
- Context trimmed for token budget must be linked here or in stage-local `references/*`.
- Do not delete archived context; move and link it.

## Archive: PR 145 Progressive Disclosure Additions

- `he-brainstorm` requirements artifact guide: `deferred-store/skills/he-brainstorm/SKILL.md` lines 48-52 and 66-68 preserve the requirements contract in `fixtures/preserved-context/skills/he-brainstorm/references/requirements-artifact-guide.md`.
- `he-brainstorm` workflow details: `deferred-store/skills/he-brainstorm/SKILL.md` lines 54-69 preserve stage sequencing in `fixtures/preserved-context/skills/he-brainstorm/references/brainstorm-workflow-details.md`.
- `he-brainstorm` discovery interview: `deferred-store/skills/he-brainstorm/SKILL.md` lines 56-64 preserve clarification behavior in `fixtures/preserved-context/skills/he-brainstorm/references/discovery-interview.md`.
- `he-brainstorm` document review pass: `deferred-store/skills/he-brainstorm/SKILL.md` lines 80-88 preserve handoff validation in `fixtures/preserved-context/skills/he-brainstorm/references/document-review-pass.md`.
- `he-spec` full spec guide: `deferred-store/skills/he-spec/SKILL.md` lines 20 and 63 point to `fixtures/preserved-context/skills/he-spec/SKILL.full.md`.
- `he-spec` artifact contract: `deferred-store/skills/he-spec/SKILL.md` lines 21 and 63 point to `fixtures/preserved-context/skills/he-spec/references/spec-artifacts.md`.
- `he-spec` mode rules: `deferred-store/skills/he-spec/SKILL.md` line 22 points to `fixtures/preserved-context/skills/he-spec/references/spec-modes.md`.
- `he-spec` subagent routing: `deferred-store/skills/he-spec/SKILL.md` lines 23 and 31-38 point to `references/subagent-routing.md`.

The PR 145 review-fix pass preserved representative removed lines for the changed compact entrypoints:

```text
3. Collect repository evidence from the diff, changed files, linked artifacts, validations, and local review context before reaching for external references.
2. Clarify objective, constraints, users, non-goals, and unknowns one question at a time.
automation_status: "<created | needs-user-action | blocked>"
- Optional related Linear QA issues and their blocker relationships.
1. Load the archived full guide and references before drafting.
3. Read the relevant `CONTEXT.md` when domain terms govern behavior, and keep implementation names aligned unless the plan explicitly says otherwise.
```
- `references/review-modes.md`, `references/findings-and-todos.md`, `references/contract.yaml`
- start `he-work` (with `[[he-tdd]]` posture if TDD) or hand to `[[gh-workflow]]` for issue creation
- hand the completed spec to `he-plan` when the user wants execution sequencing

## PR 145 Active Entrypoint Preservation

- `he-spec` full spec guide: `fixtures/budget-archive/2026-04-21/deferred-store/skills/he-spec/SKILL.md` lines 20 and 63 point to `fixtures/preserved-context/skills/he-spec/SKILL.full.md`.
- `he-spec` artifact contract: `fixtures/budget-archive/2026-04-21/deferred-store/skills/he-spec/SKILL.md` lines 21 and 63 point to `fixtures/preserved-context/skills/he-spec/references/spec-artifacts.md`.
- `he-spec` mode rules: `fixtures/budget-archive/2026-04-21/deferred-store/skills/he-spec/SKILL.md` line 22 points to `fixtures/preserved-context/skills/he-spec/references/spec-modes.md`.
- `he-spec` subagent routing: `fixtures/budget-archive/2026-04-21/deferred-store/skills/he-spec/SKILL.md` lines 23 and 31-38 point to `references/subagent-routing.md`.
- `he-code-review` preserved full guide: `fixtures/preserved-context/skills/he-code-review/SKILL.full.md` retains readiness-review routing, modes, acceptance criteria, and review-thread synthesis details for the concise runtime entrypoint.
