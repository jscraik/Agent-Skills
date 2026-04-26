---
name: he-router
description: Route ambiguous Harness Engineering requests to one lifecycle stage when users ask where to start, resume, plan, implement, review, debug, or resolve domain terminology.
metadata:
  skill-type: team_automation
---

# Harness Engineering Router

Select exactly one `harness-engineering` stage and return one exact next skill invocation.

## When To Use

- No stage is explicit.
- Multiple stages appear plausible.

## Inputs

- User request text.
- Optional artifact paths.

## Outputs

- `schema_version: 1` when structured output is requested.
- One stage from [../../references/routing-map.json](../../references/routing-map.json).
- One rationale sentence and one exact next skill invocation.
- One subagent plan with mapped roles, available/missing split, and fallback.
- One `confidence` value (`high`, `medium`, or `blocked`) and one `missing_input` value when blocked.

## Procedure

1. Parse direct `he-*` stage names, artifact state, lifecycle words, and risk words before choosing a stage because direct invocations and lifecycle state should beat broad keyword matches.
2. Apply the deterministic decision order in [../../references/deterministic-stage-routing.md](../../references/deterministic-stage-routing.md) because overlapping requests must route the same way every time.
3. Pick exactly one stage using the highest-priority matching rule from `../../references/routing-map.json`; do not merge multiple stages into one response.
4. Route explicit domain-model, ubiquitous-language, `CONTEXT.md`, glossary, or terminology requests by artifact state: fuzzy idea to `he-brainstorm`, first contract to `he-spec`, existing spec conflict to `he-deepen-spec`, execution drift to `he-work`, review drift to a review stage.
5. Route QA session, conversational bug-report, or feedback-to-Linear requests by expected-behavior clarity: clear single/multiple defects to `he-fix-bugs`, unclear expected behavior to `he-brainstorm` or `he-spec`, issue-set sequencing to `he-plan`.
6. Resolve mapped roles from `~/.codex/agents/manifest.json`, preferring `he-*` roles when available in the stage map.
7. Return outputs with `selected_stage`, `matched_rule`, `confidence`, `rationale`, `next_invocation`, and subagent policy fields.
8. If still ambiguous after applying the table, return blocked with exactly one missing input instead of guessing.

## Philosophy

- Prefer evidence-backed routing over confident guessing.
- Prefer the smallest safe stage that can unblock execution.

## Constraints

- Select exactly one primary stage.
- Do not implement product code.
- Redact secrets and sensitive data from routing context.
- If mapped roles are missing, include fallback guidance that references `[[codex-agent-creator]]`.
- Do not select `he-work` when the request says review, implemented branch, PR, go/no-go, failing test, root cause, TDD, browser polish, measured optimization, or stale branch cleanup.
- Do not remove important context for budget trimming; move it to references and index it in [../../references/deferred-context-index.md](../../references/deferred-context-index.md).

## Anti Patterns

- Selecting a stage without request or artifact evidence.
- Returning multiple primary stages.
- Omitting fallback guidance for missing mapped roles.
- Treating lifecycle stages as a loose checklist instead of a deterministic precedence table.
- Routing to implementation when the user has signaled review, diagnosis, planning, or expected-behavior ambiguity.

## Examples

- "Can you inspect this Linear issue and rough spec, then tell me whether this should go to `he-plan` or `he-work` next?"
- "The branch is implemented and CI is green; please route me to the right Harness Engineering review stage before merge."
- "The ticket says account but `CONTEXT.md` says Customer. Can you validate which Harness Engineering stage should resolve that before planning?"
- "Can you run a QA session and turn each reported bug into Linear issues?"
- "The branch is implemented and has linked Linear QA issues. Route the next stage without skipping review."
- "This bug needs a failing regression first. Route the next stage deterministically."

## Validation

- Ensure selected stage is in the HE stage set from `../../references/routing-map.json`.
- Ensure the next skill invocation is stage-specific and uses the selected `harness-engineering` skill.
- Ensure rationale and subagent plan use request evidence.
- Ensure conflict cases obey the deterministic decision order before broad keyword matches.
- Fail fast at first failed gate.

## References

- [references/contract.yaml](./references/contract.yaml)
- [references/evals.yaml](./references/evals.yaml)
- [references/task-profile.json](./references/task-profile.json)
- [../../references/subagent-routing.md](../../references/subagent-routing.md)
- [../../references/deterministic-stage-routing.md](../../references/deterministic-stage-routing.md)
Read when: routing could plausibly match more than one lifecycle stage or when step-skipping would create downstream rework.
- [../../references/deferred-context-index.md](../../references/deferred-context-index.md)
- [../../references/domain-model-routing.md](../../references/domain-model-routing.md)
Read when: routing domain-model, ubiquitous-language, `CONTEXT.md`, glossary, terminology, or Linear issue wording requests.
- [../../references/qa-intake-routing.md](../../references/qa-intake-routing.md)
Read when: routing QA sessions, conversational bug reports, or feedback-to-Linear issue requests.
