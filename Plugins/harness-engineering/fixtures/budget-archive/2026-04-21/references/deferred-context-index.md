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

6. If helpers are used during learning capture, they return text only; the orchestrator writes the final artifact.
7. If overlap with an existing solution is high, refresh the existing doc instead of creating a duplicate.
8. Recommend `he-compound-refresh` only when adjacent stale or overlapping docs need selective follow-up beyond the current artifact.

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
