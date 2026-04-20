---
name: he-router
description: Route CE requests to one stage and one executable next command. Use when stage intent is unclear.
metadata:
  skill-type: team_automation
---

# CE Router

`he-router` is the lightweight entrypoint for harness-engineering stage selection.
It chooses one primary next CE stage, explains why, and returns one executable next command.

## When To Use

- Use when users ask for CE help but do not name a precise stage.
- Use when a request could fit multiple CE stages and wrong routing would waste time.
- Use before `he-compound` when orchestration need is uncertain.

## Inputs

- User request text.
- Optional artifact paths (for example `docs/ideation`, `Docs/specs`, `Docs/plans`, `docs/solutions`).
- Optional constraints (timeline, risk, rollout sensitivity).

## Outputs

- Selected stage: one of `he-compound`, `he-ideate`, `he-brainstorm`, `he-spec`, `he-deepen-spec`, `he-plan`, `he-deepen-plan`, `he-work`, `he-review`, `he-technical-review`, `he-reliability-review`, `he-tdd`, or `he-compound-refresh`.
- One sentence rationale.
- One exact next command/prompt to run.
- Subagent plan from `../../references/routing-map.json`:
  - policy (`always`, `conditional`, or `manual-only`)
  - baseline roles
  - optional risk-signal roles
  - fallback guidance when auto-spawn is unavailable

## Failure mode

- If stage intent remains materially ambiguous after one clarification, return blocked with the missing routing input.

## Routing Rules

1. If the request is lifecycle coordination or stage recovery, route to `he-compound`.
2. If the request is idea generation before picking one direction, route to `he-ideate`.
3. If one direction is chosen and needs depth/requirements shaping, route to `he-brainstorm` or `he-spec`.
4. If spec or plan exists and needs hardening, route to `he-deepen-spec` or `he-deepen-plan`.
5. If implementation is requested, route to `he-work` (or `he-tdd` if test-first intent is explicit).
6. If review/readiness/reliability checks are requested, route to the corresponding review skill.
7. If solved-problem docs need refresh only, route to `he-compound-refresh`.

Use [../../references/routing-map.json](../../references/routing-map.json) as the canonical mapping source when a request is ambiguous.

## Procedure

1. Parse explicit stage hints from the user request.
2. Detect artifact-state hints from referenced files.
3. Choose one primary stage.
4. Load stage subagent policy from `../../references/routing-map.json` and keep only roles present in `~/.codex/agents/manifest.json` (from top-level array entries or `.agents[]` entries) when available.
5. Return stage + rationale + exact next command + subagent plan.
6. If routing risk remains high, ask one blocking clarification question.

## Constraints

- Select exactly one primary stage.
- Do not implement product code in this router.
- Do not execute multiple stages in one routing response.
- Redact secrets and sensitive data from routing context.
- If subagents cannot be used automatically, still return manual launch advice that references `~/.codex/agents/manifest.json`.

## Validation

- Ensure selected stage is in the allowed CE stage set.
- Ensure next command is executable and stage-specific.
- Ensure rationale references request evidence.
- Ensure the subagent plan matches the selected stage policy in `../../references/routing-map.json`.

## References

- [references/contract.yaml](./references/contract.yaml)
- [references/evals.yaml](./references/evals.yaml)
- [references/task-profile.json](./references/task-profile.json)
- [../../references/subagent-routing.md](../../references/subagent-routing.md)
