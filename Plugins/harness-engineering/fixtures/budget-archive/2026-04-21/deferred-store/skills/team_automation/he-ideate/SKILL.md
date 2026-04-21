---
name: he-ideate
description: Generate and rank grounded improvement ideas for the current project before committing to one direction. Use when the user wants the Harness Engineering ideation stage before brainstorming in depth, not a general product brainstorm.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Use

- Use this skill as normal for this Harness Engineering ideation stage.
- For full stage policy, workflow details, and examples, load the archived full guide.

## Philosophy

- Generate options grounded in repository reality.
- Prefer ranked decisions over idea dumps.

## When to use

- Use when candidate directions need to be generated and prioritized before deeper planning.
- Use when the user wants targeted ideation for the current codebase context.

## Inputs

- Problem statement, user outcome goals, and constraints.
- Existing artifacts and system context that bound viable options.

## Outputs

- Ranked option set with tradeoffs and confidence.
- Recommended next stage and rationale.
- Include `schema_version: 1` when structured output is requested.

## Procedure

1. Clarify decision axis and constraints.
2. Generate bounded options using repository evidence.
3. Rank options and recommend a next-stage transition.

## Validation

- Ensure each option includes tradeoffs and feasibility notes.
- Ensure recommendation maps to an explicit next stage.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not present infeasible options as primary recommendations.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Listing generic ideas without codebase-specific grounding.
- Recommending a direction without explicit tradeoff analysis.

## Full Context

- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)

## Subagent Routing

- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- `he-ideate` conditional role: `issue-intelligence-analyst`.
- Resolve available roles from `~/.codex/agents/manifest.json` before spawning helpers.
- Apply the mapped stage policy (`always`, `conditional`, or `manual-only`) before delegation.
- If auto-spawn is unavailable, continue inline and explicitly list the roles the user can launch manually.
- If required roles are missing from the manifest, route to [codex-agent-creator](../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md) and provide the exact role names to create or install.
