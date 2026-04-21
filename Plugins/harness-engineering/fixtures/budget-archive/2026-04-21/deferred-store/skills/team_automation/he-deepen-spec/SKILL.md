---
name: he-deepen-spec
description: Deepen an existing system or UI spec so boundaries, lifecycle rules, failure handling, and validation are strong enough for planning. Use when the user wants Harness Engineering spec hardening or a requirements review pass before planning.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Use

- Use this skill as normal for this Harness Engineering stage.
- For full stage policy, workflow details, and examples, load the archived full guide.

## Philosophy

- Specifications must be executable contracts, not narrative placeholders.
- Resolve ambiguity before downstream planning and delivery.

## When to use

- Use when an existing spec needs tighter boundaries, contracts, and failure behavior.
- Use before planning when specification trust is not high enough.

## Inputs

- Existing specification plus related requirements and constraints.
- Interfaces, lifecycle assumptions, and validation expectations.

## Outputs

- Deepened specification with explicit boundaries, invariants, and acceptance criteria.
- Clear readiness recommendation for planning.
- Include `schema_version: 1` when structured output is requested.

## Procedure

1. Inspect current spec for ambiguity, missing edge cases, and contract gaps.
2. Deepen interfaces, lifecycle behavior, and failure handling.
3. Return readiness outcome and next stage recommendation.

## Validation

- Ensure acceptance criteria are testable and non-goals explicit.
- Ensure operational, security, and rollback concerns are covered.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not silently alter core scope without explicit rationale.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Treating speculative assumptions as settled requirements.
- Passing specs downstream with unresolved contract gaps.

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
- If required roles are missing from the manifest, create or install them with [../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md](../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md) before rerunning delegated coverage.
