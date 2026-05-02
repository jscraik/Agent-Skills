---
name: he-ideate
description: Generate and compare grounded product or engineering directions with tradeoffs. Use when users want possibilities, critique, or direction-setting before a spec.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Philosophy

- Generate options grounded in repository reality.
- Prefer ranked decisions over idea dumps.
- Generate many candidates before critique, then explain only the strongest survivors in detail.

## When to use

- Use when candidate directions need to be generated and prioritized before deeper planning.
- Use when the user wants targeted ideation for the current codebase context.
- Use when the user wants to know which directions are worth exploring before `he-brainstorm` defines any one idea in depth.

## Inputs

- Request, artifacts, repo context, and linked Linear issues.

## Outputs

- `schema_version: 1` when structured; result, validation, blockers, and next Harness Engineering action.

## Procedure

1. Clarify the decision axis, focus hint, and any issue-tracker intent before generating ideas.
2. Check for a recent matching ideation doc and decide whether to resume or start fresh.
3. Ground ideation in the repo with a shallow codebase scan and relevant existing learnings before proposing options.
4. Generate the full candidate pool before critique; do not rank or prune early.
5. Filter the merged candidate list adversarially, keep explicit rejection reasons, and rank only the survivors.
6. Route the strongest survivor to `he-brainstorm`, not directly to planning or implementation.

## Validation

- Ensure each option includes tradeoffs and feasibility notes.
- Ensure recommendation maps to an explicit next stage.
- Ensure repo grounding happened before idea generation.
- Ensure critique happened after the combined candidate pool existed, not during generation.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not present infeasible options as primary recommendations.
- Do not turn ideation into requirements, implementation tasks, or code edits.
- Do not treat issue-theme analysis as a single-bug debugging request.
- Do not remove important context for budget trimming; move it to references and index it in `../../../references/deferred-context-index.md`.

## Anti-patterns

- Listing generic ideas without codebase-specific grounding.
- Recommending a direction without explicit tradeoff analysis.
- Critiquing or ranking ideas before the combined candidate list exists.
- Routing a chosen idea straight to `he-plan` or `he-work`.

## Full Context

- Assets: [icon-small.png](./assets/icon-small.png), [icon-large.png](./assets/icon-large.png)
- Subagent call contract: [../../../references/subagent-call-contract.md](../../../references/subagent-call-contract.md)

## Examples

- "Can you generate three realistic ways to make this release flow less brittle, then rank them by tradeoff?"
- "Help me explore options for making these plugin skills easier to discover before we write a spec."
- "What directions are worth considering for this Linear theme after you inspect the repo for existing patterns?"
