---
name: ce-router
description: Route CE requests to one stage and one executable next command. Use when stage intent is unclear.
metadata:
  skill-type: team_automation
---

# CE Router

`ce-router` is the lightweight entrypoint for harness-engineering stage selection.
It chooses one primary next CE stage, explains why, and returns one executable next command.

## When To Use

- Use when users ask for CE help but do not name a precise stage.
- Use when a request could fit multiple CE stages and wrong routing would waste time.
- Use before `ce-compound` when orchestration need is uncertain.

## Inputs

- User request text.
- Optional artifact paths (for example `docs/ideation`, `Docs/specs`, `Docs/plans`, `docs/solutions`).
- Optional constraints (timeline, risk, rollout sensitivity).

## Outputs

- Selected stage: one of `ce-compound`, `ce-ideate`, `ce-brainstorm`, `ce-spec`, `ce-deepen-spec`, `ce-plan`, `ce-deepen-plan`, `ce-work`, `ce-review`, `ce-technical-review`, `ce-reliability-review`, `ce-tdd`, or `ce-compound-refresh`.
- One sentence rationale.
- One exact next command/prompt to run.

## Routing Rules

1. If the request is lifecycle coordination or stage recovery, route to `ce-compound`.
2. If the request is idea generation before picking one direction, route to `ce-ideate`.
3. If one direction is chosen and needs depth/requirements shaping, route to `ce-brainstorm` or `ce-spec`.
4. If spec or plan exists and needs hardening, route to `ce-deepen-spec` or `ce-deepen-plan`.
5. If implementation is requested, route to `ce-work` (or `ce-tdd` if test-first intent is explicit).
6. If review/readiness/reliability checks are requested, route to the corresponding review skill.
7. If solved-problem docs need refresh only, route to `ce-compound-refresh`.

Use [../../references/routing-map.json](../../references/routing-map.json) as the canonical mapping source when a request is ambiguous.

## Procedure

1. Parse explicit stage hints from the user request.
2. Detect artifact-state hints from referenced files.
3. Choose one primary stage.
4. Return stage + rationale + exact next command.
5. If routing risk remains high, ask one blocking clarification question.

## Constraints

- Select exactly one primary stage.
- Do not implement product code in this router.
- Do not execute multiple stages in one routing response.
- Redact secrets and sensitive data from routing context.

## Validation

- Ensure selected stage is in the allowed CE stage set.
- Ensure next command is executable and stage-specific.
- Ensure rationale references request evidence.

## References

- [references/contract.yaml](./references/contract.yaml)
- [references/evals.yaml](./references/evals.yaml)
- [references/task-profile.json](./references/task-profile.json)
