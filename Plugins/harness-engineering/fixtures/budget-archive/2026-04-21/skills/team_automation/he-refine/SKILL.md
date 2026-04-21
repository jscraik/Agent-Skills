---
name: he-refine
description: "[BETA] Improve user-facing quality of an existing feature through guided refinement and validation loops. Use when behavior works but UX, accessibility, or polish quality must be raised before review."
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Use

- Use this skill as normal for this Harness Engineering stage.
- For full stage policy, workflow details, and examples, load the archived full guide.

## Philosophy

- Refine through tight feedback loops, not speculative redesign.
- Keep polish work measurable and bounded to user-visible outcomes.

## When to use

- Use when implementation is functional but needs quality polish before final review.
- Use for browser-first refinement loops with explicit iteration gates.

## Inputs

- Current implementation state, target UX outcomes, and constraints.
- Existing QA findings, visual diffs, or usability observations.

## Outputs

- Prioritized refinement actions with acceptance criteria.
- Iteration summary and readiness recommendation.
- Include `schema_version: 1` when structured output is requested.

## Procedure

1. Evaluate current behavior against target quality criteria.
2. Apply bounded refinement iterations with clear checkpoints.
3. Report resolved gaps and remaining blockers.

## Validation

- Ensure each refinement maps to a measurable user-facing improvement.
- Ensure regression risk is checked before stage exit.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not broaden refinements into unrelated feature work.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Cosmetic churn without acceptance criteria.
- Iterating without verifying whether user-facing quality improved.

## Full Context

- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
Read when: deeper behavior or routing policy is needed.

## Subagent Routing

- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- Resolve available roles from `~/.codex/agents/manifest.json` before spawning helpers.
- Apply the mapped stage policy (`always`, `conditional`, or `manual-only`) before delegation.
- If auto-spawn is unavailable, continue inline and explicitly list the roles the user can launch manually.
- If required roles are missing from the manifest, create or install them with [../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md](../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md) before rerunning delegated coverage.
