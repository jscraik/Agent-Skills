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
- Generate many candidates before critique, then explain only the strongest survivors in detail.

## When to use

- Use when candidate directions need to be generated and prioritized before deeper planning.
- Use when the user wants targeted ideation for the current codebase context.
- Use when the user wants to know which directions are worth exploring before `he-brainstorm` defines any one idea in depth.

## Inputs

- Problem statement, user outcome goals, and constraints.
- Existing artifacts and system context that bound viable options.
- Optional focus hint, path, subsystem, or volume override such as `top 3`.
- Optional issue-tracker intent when issue themes or bug patterns should shape the ideation set.

## Outputs

- Ranked option set with tradeoffs and confidence.
- Recommended next stage and rationale.
- Explicit ideation route: `fresh` or `resume`.
- Durable ideation artifact path when ideas are written or updated in `docs/ideation/`.
- Include `schema_version: 1` when structured output is requested.

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
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Listing generic ideas without codebase-specific grounding.
- Recommending a direction without explicit tradeoff analysis.
- Critiquing or ranking ideas before the combined candidate list exists.
- Routing a chosen idea straight to `he-plan` or `he-work`.

## Examples

- "When the user asks, `Inspect this repo and tell me which improvements are genuinely worth exploring before we brainstorm one.`"
- "Help me focus on the auth area and compare the strongest ideas, not just the easiest tasks."
- "Please resume the recent ideation doc if it still fits; otherwise start fresh and rank only the best survivors."

## Full Context

- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
- Assets: [./assets](./assets)
- Assets directory marker: `assets/`
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)

## Subagent Routing

- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- `he-ideate` conditional role: `issue-intelligence-analyst`.
- Resolve available roles from `~/.codex/agents/manifest.json` before spawning helpers.
- Apply the mapped stage policy (`always`, `conditional`, or `manual-only`) before delegation.
- If auto-spawn is unavailable, continue inline and explicitly list the roles the user can launch manually.
- If required roles are missing from the manifest, route to [codex-agent-creator](../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md) and provide the exact role names to create or install.
