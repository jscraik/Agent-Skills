# Harness Engineering Deferred Context Index

This reference preserves context moved out of active `SKILL.md` entrypoints during budget hardening.

Use this file when you need detailed stage doctrine, extended examples, legacy/archive context, or full stage asset/script references that are intentionally deferred from always-loaded entrypoints.

## Preserved Context

- Full stage guides and archived references remain in `fixtures/skill-archive/**`.
- Canonical contract/eval/task profiles remain in each stage under `Infrastructure/references/**`.
- Canonical subagent role policy remains in:
  - `references/routing-map.json`
  - `references/subagent-routing.md`
- Canonical deterministic stage-routing policy remains in:
  - `references/deterministic-stage-routing.md`
- Canonical domain-model routing policy remains in:
  - `references/domain-model-routing.md`
- Canonical QA intake routing policy remains in:
  - `references/qa-intake-routing.md`
- Router role-resolution policy for `he-router` requires checking `~/.codex/agents/manifest.json` and preferring `he-*` mapped roles when available in the stage map.
- The `he-router` execution contract now treats `he-*` stage-map role entries as first priority, with manifest lookups used to resolve concrete reviewer names only after stage-map preference.

## Budget Trim Preservation

The following lines were intentionally moved out of active or fixture `SKILL.md` entrypoints during context-budget hardening. They remain preserved here for auditability and historical review of the compacted flow contracts.

The Harness Engineering A-grade optimization pass preserved representative removed entrypoint context here while compacting active skill bodies into progressive-disclosure entrypoints:

- `description: Review PRs, branches, diffs, and workflow artifacts for package-level go/no-go readiness with severity-ranked synthesis. Use when users need readiness synthesis rather than detailed technical-risk critique.`
- `description: "Review services, APIs, and multi-component systems for reliability risks including failure modes, cascading failures, resilience gaps, and SLO readiness. Use when the work involves new services, significant service changes, multiple external dependencies, or high blast-radius failure scenarios."`
- `description: Review diffs, PRs, specs, plans, or review-feedback items and return severity-ranked engineering findings with exact locations. Use when technical risks or feedback correctness must be verified before implementation.`
- `description: Define problem scope, requirements, and decision options before spec or plan stages. Use when the user has ambiguity in what to build, why it matters, or which direction to choose.`
- `description: Use when Harness Engineering needs to review and refresh stale `docs/solutions/` learnings and pattern docs against the current codebase, including overlap consolidation after refactors, migrations, or dependency upgrades.`
- `description: "Analyze Harness Engineering lifecycle state, plan the correct stage routing, and capture verified solved problems into durable docs/solutions knowledge. Use when the user asks to start or resume from the correct stage, or to document a verified fix as reusable team guidance."`
- `description: Deepen an existing system or UI spec so boundaries, lifecycle rules, failure handling, and validation are strong enough for planning. Use when the user wants Harness Engineering spec hardening or a requirements review pass before planning.`
- `description: Restore broken behavior by reproducing failures, identifying root cause, and delivering verified fixes. Use when the user needs regression debugging, incident triage, or bug repair from tracker or direct reports.`
- `description: Generate and rank grounded improvement ideas for the current project before committing to one direction. Use when the user wants the Harness Engineering ideation stage before brainstorming in depth, not a general product brainstorm.`
- `description: Analyze and improve an existing implementation through metric-driven, bounded iteration loops. Use when the user wants Harness Engineering optimization or tuning rather than one-shot implementation.`
- `description: Plan execution work from specs, brainstorm outputs, bugs, or feature requests into an implementation-ready sequence. Use when the user needs the Harness Engineering planning stage before execution.`
- `description: Automate stale local git branch cleanup with worktree-aware deletion and explicit confirmation gates. Use this skill when the user asks to prune local branches whose remote tracking refs are gone.`
- `description: Own the Harness Engineering spec stage by turning a brainstorm, existing spec, UI source, or feature description into an implementation-grade contract. Use when the user wants the WHAT-before-planning artifact, not a broader product-planning pipeline.`
- `description: "Execute a plan, todo list, or tightly scoped spec with traceable progress, validation, contract-drift control, UI execution gates, and optional external delegation. Use when the user wants Harness Engineering work implemented, not just planned."`
- `description: "[BETA] Improve user-facing quality of an existing feature through guided refinement and validation loops. Use when behavior works but UX, accessibility, or polish quality must be raised before review."`
- `description: Route ambiguous Harness Engineering requests to one lifecycle stage when users ask where to start, resume, plan, implement, review, debug, or resolve domain terminology.`

description: Review PRs, branches, diffs, and workflow artifacts for package-level go/no-go readiness with severity-ranked synthesis. Use when users need readiness synthesis rather than detailed technical-risk critique.
description: "Review services, APIs, and multi-component systems for reliability risks including failure modes, cascading failures, resilience gaps, and SLO readiness. Use when the work involves new services, significant service changes, multiple external dependencies, or high blast-radius failure scenarios."
description: Review diffs, PRs, specs, plans, or review-feedback items and return severity-ranked engineering findings with exact locations. Use when technical risks or feedback correctness must be verified before implementation.
description: Define problem scope, requirements, and decision options before spec or plan stages. Use when the user has ambiguity in what to build, why it matters, or which direction to choose.
description: Use when Harness Engineering needs to review and refresh stale `docs/solutions/` learnings and pattern docs against the current codebase, including overlap consolidation after refactors, migrations, or dependency upgrades.
description: "Analyze Harness Engineering lifecycle state, plan the correct stage routing, and capture verified solved problems into durable docs/solutions knowledge. Use when the user asks to start or resume from the correct stage, or to document a verified fix as reusable team guidance."
description: Deepen an existing system or UI spec so boundaries, lifecycle rules, failure handling, and validation are strong enough for planning. Use when the user wants Harness Engineering spec hardening or a requirements review pass before planning.
description: Restore broken behavior by reproducing failures, identifying root cause, and delivering verified fixes. Use when the user needs regression debugging, incident triage, or bug repair from tracker or direct reports.
description: Generate and rank grounded improvement ideas for the current project before committing to one direction. Use when the user wants the Harness Engineering ideation stage before brainstorming in depth, not a general product brainstorm.
description: Analyze and improve an existing implementation through metric-driven, bounded iteration loops. Use when the user wants Harness Engineering optimization or tuning rather than one-shot implementation.
description: Plan execution work from specs, brainstorm outputs, bugs, or feature requests into an implementation-ready sequence. Use when the user needs the Harness Engineering planning stage before execution.
description: Automate stale local git branch cleanup with worktree-aware deletion and explicit confirmation gates. Use this skill when the user asks to prune local branches whose remote tracking refs are gone.
description: Own the Harness Engineering spec stage by turning a brainstorm, existing spec, UI source, or feature description into an implementation-grade contract. Use when the user wants the WHAT-before-planning artifact, not a broader product-planning pipeline.
description: "Execute a plan, todo list, or tightly scoped spec with traceable progress, validation, contract-drift control, UI execution gates, and optional external delegation. Use when the user wants Harness Engineering work implemented, not just planned."
description: "[BETA] Improve user-facing quality of an existing feature through guided refinement and validation loops. Use when behavior works but UX, accessibility, or polish quality must be raised before review."
description: Route ambiguous Harness Engineering requests to one lifecycle stage when users ask where to start, resume, plan, implement, review, debug, or resolve domain terminology.

The QA intake routing refresh preserved these pre-insertion procedure lines:

- `2. Map service boundaries and dependency failure paths.`
- `3. Produce reliability findings with concrete blast-radius and mitigation guidance.`
- `4. Route review subagents per policy; if unavailable, continue inline and state manual role options.`
- `2. Produce a failing test first (RED), then apply the smallest fix (GREEN).`
- `3. Repeat in vertical slices and preserve traceability to accepted behavior targets.`
- `4. Route supporting subagents per policy; if unavailable, continue inline and state manual role options.`

2. Map service boundaries and dependency failure paths.
3. Produce reliability findings with concrete blast-radius and mitigation guidance.
4. Route review subagents per policy; if unavailable, continue inline and state manual role options.
2. Produce a failing test first (RED), then apply the smallest fix (GREEN).
3. Repeat in vertical slices and preserve traceability to accepted behavior targets.
4. Route supporting subagents per policy; if unavailable, continue inline and state manual role options.

2. Deepen interfaces, lifecycle behavior, and failure handling.
2. Map service boundaries and dependency failure paths.
2. Produce a failing test first (RED), then apply the smallest fix (GREEN).
2. Reproduce and stabilize the failing behavior before proposing changes.
3. Build synchronized tasks from the governing artifact and keep task state aligned with markdown artifact state during execution.
3. For incoming feedback: read, clarify unclear items, verify, then respond technically.
3. Produce the specification artifact with concrete acceptance criteria.
3. Produce reliability findings with concrete blast-radius and mitigation guidance.
3. Repeat in vertical slices and preserve traceability to accepted behavior targets.
3. Resolve mapped roles from `~/.codex/agents/manifest.json`, preferring `he-*` roles when available in the stage map.
3. Return readiness outcome and next stage recommendation.
3. Trace backward from the symptom to the point where valid state first became invalid.
4. Generate 2-3 concrete approaches when multiple plausible directions remain, then evaluate tradeoffs and recommend one.
4. If source material is unclear or incomplete, run a lightweight planning bootstrap to establish enough context without leaving planning mode.
4. Implement in small verified slices, honoring execution posture signals such as `test-first` or `characterization-first`.
4. Return findings-first output plus open questions and next action.
4. Return outputs.
4. Route research and review roles per routing policy; if unavailable, continue inline and state manual role options.
4. Route review subagents per policy; if unavailable, continue inline and state manual role options.
4. Route supporting subagents per policy; if unavailable, continue inline and state manual role options.
4. Test one hypothesis at a time, and for uncertain links require a prediction that can confirm or falsify the chain.
5. Capture durable requirements only when the discussion produced decisions worth preserving.
5. If still ambiguous after one clarification, return blocked with missing input.
5. Present the root cause, proposed fix scope, and test recommendations before remediation when the request is diagnosis-first or confidence is still settling.
5. Research local patterns and prior learnings before finalizing structure when they materially affect sequencing or risk.
5. Review for correctness, regression risk, operability, protected-artifact handling, and release readiness.
5. Stop and update the governing artifact before continuing if execution uncovers contract drift, hidden scope, or changed boundaries.
6. Recommend the next Harness Engineering stage and stop instead of drifting into implementation planning.
6. Report completed work, blockers, validation evidence, and the shipping handoff package.
6. Size the plan depth to the work, then decompose into ordered, verifiable tasks with explicit dependencies, tests, and next-stage handoff.
6. When remediation is in scope, check workspace safety, prefer failing-test-first validation, apply the minimal fix, and verify no regressions.

## Stage Archive Paths

- `he-router`: `skills/he-router/references/*` (active canonical), plus router policy in `references/routing-map.json`.
- Domain-model workflow: `references/domain-model-routing.md`
- QA intake workflow: `references/qa-intake-routing.md`
- Deterministic stage routing: `references/deterministic-stage-routing.md`
- `he-code-review`: `fixtures/skill-archive/skills/code_quality_review/he-code-review/`
- `he-reliability-review`: `fixtures/skill-archive/skills/code_quality_review/he-reliability-review/`
- `he-technical-review`: `fixtures/skill-archive/skills/code_quality_review/he-technical-review/`
- `he-brainstorm`: `fixtures/skill-archive/skills/team_automation/he-brainstorm/`
- `he-compound`: `fixtures/skill-archive/skills/team_automation/he-compound/`
- `he-compound-refresh`: `fixtures/skill-archive/skills/team_automation/he-compound-refresh/`
- `he-deepen-plan`: `fixtures/skill-archive/skills/team_automation/he-deepen-plan/`
- `he-deepen-spec`: `fixtures/skill-archive/skills/team_automation/he-deepen-spec/`
- `he-fix-bugs`: `fixtures/skill-archive/skills/team_automation/he-fix-bugs/`
- `he-ideate`: `fixtures/skill-archive/skills/team_automation/he-ideate/`
- `he-improve`: `fixtures/skill-archive/skills/team_automation/he-improve/`
- `he-plan`: `fixtures/skill-archive/skills/team_automation/he-plan/`
- `he-prune-branches`: `fixtures/skill-archive/skills/team_automation/he-prune-branches/`
- `he-refine`: `fixtures/skill-archive/skills/team_automation/he-refine/`
- `he-spec`: `fixtures/skill-archive/skills/team_automation/he-spec/`
- `he-tdd`: `fixtures/skill-archive/skills/team_automation/he-tdd/`
- `he-work`: `fixtures/skill-archive/skills/team_automation/he-work/`

## Preservation Contract

- Active `SKILL.md` files should remain concise and routing-safe.
- Context trimmed for token budget must be linked here or in stage-local `references/*`.
- Do not delete archived context; move and link it.
