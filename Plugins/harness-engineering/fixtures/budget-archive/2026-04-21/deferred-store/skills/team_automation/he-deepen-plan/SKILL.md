---
name: he-deepen-plan
description: Deepen an existing implementation plan so sequencing, verification, and risk treatment are strong enough for execution. Use when the user wants Harness Engineering plan hardening before he-work.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Use

- Use this skill as normal for this Harness Engineering stage.
- For full stage policy, workflow details, and examples, load the archived full guide.

## Philosophy

- Strengthen execution quality before coding begins.
- Resolve sequencing and risk gaps while changes are still cheap.

## When to use

- Use when an existing plan needs sharper sequencing, testability, or risk treatment.
- Use before `he-work` when plan readiness is uncertain.

## Inputs

- Existing plan artifact plus linked specs and constraints.
- Dependencies, rollout constraints, and validation requirements.

## Outputs

- Deepened plan with explicit sequencing, checkpoints, and risk controls.
- Clear readiness recommendation for `he-work`.
- Include `schema_version: 1` when structured output is requested.

## Procedure

1. Inspect current plan for ambiguity, hidden coupling, and missing checkpoints.
2. Deepen task sequencing, validation strategy, and rollback posture.
3. Return revised readiness and next action.

## Validation

- Ensure each task has observable completion criteria.
- Ensure rollout, rollback, and dependency handling are explicit.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not introduce new scope without explicit justification.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Increasing detail without improving executable clarity.
- Deferring critical risk decisions to implementation time.

## Full Context

- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
- Assets: [icon-small.png](./assets/icon-small.png), [icon-large.png](./assets/icon-large.png)
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)

## Subagent Routing

- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- Resolve available roles from `~/.codex/agents/manifest.json` before spawning helpers.
- Apply the mapped stage policy (`always`, `conditional`, or `manual-only`) before delegation.
- If auto-spawn is unavailable, continue inline and explicitly list the roles the user can launch manually.
- If required roles are missing from the manifest, create or install them with [../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md](../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md) before rerunning delegated coverage.

## Examples

- "Can you deepen this implementation plan so every risky step has an owner, gate, and rollback?"
- "Help me turn this thin plan into an execution sequence before I start editing code."
- "This plan mentions validation, but it is vague. Tighten the order of tests, checks, and merge evidence."
- "Can you inspect the risky steps in this plan and validate that each one has a concrete gate?"
