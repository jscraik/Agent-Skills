---
name: he-router
description: Choose the Harness Engineering lifecycle stage for ambiguous requests. Use when the user is unsure whether to spec, plan, work, review, debug, or schedule follow-up.
metadata:
  skill-type: team_automation
---

# Harness Engineering Router

Choose one Harness Engineering lifecycle stage.

## Philosophy

- Use the user request, artifact state, and Linear evidence as the routing source.
- Prefer the smallest stage that safely unblocks the user.
- Keep routing separate from implementation.

## When to use

- No stage is explicit.
- Multiple stages appear plausible.
- The user asks where to start, resume, plan, implement, review, debug, schedule a heartbeat, or resolve domain terminology.

## Required inputs

- User request text.
- Optional artifact paths, issue state, branch state, or prior session evidence.

## Deliverables

- `schema_version: 1` when structured output is requested.
- One selected stage.
- One rationale sentence.
- One recommended next step.
- `confidence` and `missing_input` when blocked.

## Procedure

1. Parse direct `he-*` stage names, artifact state, lifecycle words, and risk words before broad keyword matches.
2. Translate folded stage names through [folded skill context](../../references/folded-skill-context.md) before selecting a stage.
3. Apply the deterministic decision order in [deterministic stage routing](../../references/deterministic-stage-routing.md).
4. Pick exactly one stage from [routing map](../../references/routing-map.json).
4. Route domain-language conflicts through [domain model routing](../../references/domain-model-routing.md).
5. Route QA or feedback sessions through [QA intake routing](../../references/qa-intake-routing.md).
6. Route prior-session or repeated-failure requests through [session evidence contract](../../references/session-evidence-contract.md).

## Output contract

Return `schema_version: 1` when structured output is requested, plus `selected_stage`, `matched_rule`, `confidence`, `rationale`, `recommended_next_step`, and `missing_input` when blocked.

## Constraints

- Select exactly one primary stage.
- Do not implement product code.
- Do not select `he-work` for review, PR, go/no-go, failing test, root-cause, TDD, browser-polish, optimization, or stale-branch cleanup requests.
- Redact secrets and sensitive data.
- Do not remove important context for budget trimming; move it to references and index it in [deferred context index](../../references/deferred-context-index.md).

## Anti-patterns

- Do not treat ambiguous review or failing-test language as implementation work.
- Do not create a plan when a spec is missing.
- Do not route stale-branch cleanup through feature work.
- Do not invent Linear state when the issue status is absent.

## Progressive Disclosure

Never drop required context for brevity; move it into references or deferred context and link it here.

- Local contract, evals, and task profile: `references/`
- Shared HE routing references: `Plugins/harness-engineering/references/`
- Folded stage alias map: `Plugins/harness-engineering/references/folded-skill-context.md`
- Archived router context: `Infrastructure/references/deferred-skill-context/harness-engineering-he-router/`

## Validation

Ensure the selected stage exists in the HE stage set, the recommendation is stage-specific, and conflict cases obey deterministic routing before broad keyword matches.
Fail fast when the selected stage is absent from the routing map, required artifact evidence is missing, or lifecycle cues conflict; stop at the first failed gate and report the blocker.

## Examples

- `Can you turn JSC-224 into acceptance criteria from Docs/research/linear-notes.md?` -> `he-spec`
- `Build Docs/plans/2026-04-29-linear-traceability-plan.md.` -> `he-work`
- `Review PR 153 against JSC-224 and Docs/plans/2026-04-29-linear-traceability-plan.md.` -> `he-code-review`
- `Check back later when JSC-224 leaves Blocked.` -> `he-heartbeat`

## Failure mode

If required evidence is missing, return the missing input and the most likely stage with low confidence.

## Gotchas

- `review`, `PR`, `go/no-go`, and `failing test` requests are not implementation requests.
- Linear issue references are routing evidence, not a substitute for artifact checks.
- Session evidence requests need prior-session or repeated-failure context before choosing a stage.
