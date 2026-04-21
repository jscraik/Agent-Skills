---
name: he-plan
description: Plan execution work from specs, brainstorm outputs, bugs, or feature requests into an implementation-ready sequence. Use when the user needs the Harness Engineering planning stage before execution.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Use

- Use this skill as normal for the Harness Engineering planning stage.
- For full stage policy, workflow details, and examples, load the archived full guide.

## Philosophy

- Plans should be executable, testable, and constraint-aware.
- Resolve risk and sequencing ambiguity before coding.

## When to use

- Use when requirements exist and implementation sequencing must be defined.
- Use before `he-work` when execution tasks and verification strategy are not yet explicit.

## Inputs

- Source spec, brainstorm output, or defect scope.
- Constraints, dependencies, and risk/compliance requirements.

## Outputs

- Ordered implementation plan with validation intent per task.
- Explicit blockers, assumptions, and next-stage recommendation.
- Include `schema_version: 1` when structured output is requested.

## Procedure

1. Analyze source artifacts and execution constraints.
2. Decompose into ordered, verifiable tasks with dependency clarity.
3. Return plan readiness and next stage.

## Validation

- Ensure tasks are actionable and independently verifiable.
- Ensure dependencies, rollback, and risk controls are explicit.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not produce plan steps that depend on unstated assumptions.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Producing abstract plans without executable task boundaries.
- Omitting verification intent for critical tasks.

## Full Context

- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Assets: [./assets](./assets)
- Assets directory marker: `assets/`

## Subagent Routing

- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- Resolve available roles from `~/.codex/agents/manifest.json` before spawning helpers.
- Apply the mapped stage policy (`always`, `conditional`, or `manual-only`) before delegation.
- If auto-spawn is unavailable, continue inline and explicitly list the roles the user can launch manually.
- If required roles are missing from the manifest, route to [codex-agent-creator](../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md) and provide the exact role names to create or install.
