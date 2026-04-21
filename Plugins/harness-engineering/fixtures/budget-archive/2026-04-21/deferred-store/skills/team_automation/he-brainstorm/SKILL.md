---
name: he-brainstorm
description: Define problem scope, requirements, and decision options before spec or plan stages. Use when the user has ambiguity in what to build, why it matters, or which direction to choose.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Use

- Use this skill as normal for the Harness Engineering brainstorm stage.
- For full stage policy, workflow details, and examples, load the archived full guide.

## Philosophy

- Discover the right problem before proposing implementation.
- Keep options explicit and assumptions testable.

## When to use

- Use when scope is unclear, goals conflict, or candidate approaches need comparison.
- Use before `he-spec` or `he-plan` when requirements are not yet stable.

## Inputs

- User intent, constraints, and current context artifacts.
- Relevant system boundaries, risks, and non-goals.

## Outputs

- Clarified requirements with ranked options and tradeoffs.
- Recommended next Harness Engineering stage.
- Include `schema_version: 1` when structured output is requested.

## Procedure

1. Clarify objective, constraints, and unknowns.
2. Generate options and evaluate tradeoffs against constraints.
3. Recommend direction and next stage transition.

## Validation

- Ensure requirements and non-goals are explicit and testable.
- Ensure recommendation has rationale tied to constraints.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not proceed to implementation planning when requirement ambiguity remains blocking.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Jumping to solution design before clarifying the actual problem.
- Returning unranked options without decision criteria.

## Full Context

- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)

## Subagent Routing

- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- Resolve available roles from `~/.codex/agents/manifest.json` before spawning helpers.
- Apply the mapped stage policy (`always`, `conditional`, or `manual-only`) before delegation.
- If auto-spawn is unavailable, continue inline and explicitly list the roles the user can launch manually.
