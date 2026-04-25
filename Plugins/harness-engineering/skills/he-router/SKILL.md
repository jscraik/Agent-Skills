---
name: he-router
description: Route ambiguous Harness Engineering requests to one lifecycle stage. Use when users ask where to start, resume, plan, implement, review, debug, or resolve terminology.
metadata:
  skill-type: team_automation
---

# Harness Engineering Router

Select exactly one `harness-engineering` stage and return one exact next skill invocation.

## When To Use

- No stage is explicit.
- Multiple stages appear plausible.

## Inputs

- Request, artifacts, repo context, and linked Linear issues.

## Outputs

- `schema_version: 1` when structured; result, validation, blockers, and next Harness Engineering action.

## Procedure

1. Parse direct `he-*` stage names, artifact state, lifecycle words, and risk words before choosing a stage because direct invocations and lifecycle state should beat broad keyword matches.
2. Apply the deterministic decision order in `../../references/deterministic-stage-routing.md` because overlapping requests must route the same way every time.
3. Pick exactly one stage using the highest-priority matching rule from `../../references/routing-map.json`; do not merge multiple stages into one response.
4. Route explicit domain-model, ubiquitous-language, `CONTEXT.md`, glossary, or terminology requests by artifact state: fuzzy idea to `he-brainstorm`, first contract to `he-spec`, existing spec conflict to `he-deepen-spec`, execution drift to `he-work`, review drift to a review stage.
5. Route QA session, conversational bug-report, or feedback-to-Linear requests by expected-behavior clarity: clear single/multiple defects to `he-fix-bugs`, unclear expected behavior to `he-brainstorm` or `he-spec`, issue-set sequencing to `he-plan`.
6. Resolve mapped roles from `~/.codex/agents/manifest.json`, preferring `he-*` roles when available in the stage map.
7. Return outputs with `selected_stage`, `matched_rule`, `confidence`, `rationale`, `next_invocation`, and subagent policy fields.
8. If still ambiguous after applying the table, return blocked with exactly one missing input instead of guessing.

## Philosophy

- Prefer evidence-backed routing over confident guessing.
- Prefer the smallest safe stage that can unblock execution.

## Validation

- Ensure exactly one selected stage, one next invocation, request evidence, and blocked output when required inputs are missing.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Select exactly one primary stage.
- Do not implement product code.
- Redact secrets and sensitive data from routing context.
- If mapped roles are missing, include fallback guidance that references `[[codex-agent-creator]]`.
- Do not select `he-work` when the request says review, implemented branch, PR, go/no-go, failing test, root cause, TDD, browser polish, measured optimization, or stale branch cleanup.
- Do not remove important context for budget trimming; move it to references and index it in `../../references/deferred-context-index.md`.

## Anti Patterns

- Selecting a stage without request or artifact evidence.
- Returning multiple primary stages.
- Omitting fallback guidance for missing mapped roles.
- Treating lifecycle stages as a loose checklist instead of a deterministic precedence table.
- Routing to implementation when the user has signaled review, diagnosis, planning, or expected-behavior ambiguity.
## Examples

Read when: examples or role-routing details are needed, open the archived references for this skill.
