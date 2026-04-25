---
name: he-brainstorm
description: Define problem scope, requirements, and decision options before spec or plan stages. Use when the user has ambiguity in what to build, why it matters, or which direction to choose.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps the full operational workflow in archived references. Use it to decide whether a structured Harness Engineering brainstorm is needed, run a right-sized clarification loop, and hand off with durable requirements when the idea is clear enough.

## Use

- Use this skill as normal for the Harness Engineering brainstorm stage.
- Use it before `he-spec` or `he-plan` when the work is still ambiguous.
- If the request is already concrete enough for planning or direct execution, keep the interaction brief and recommend the next stage instead of forcing a brainstorm.
- For full stage policy, workflow details, and examples, load the archived full guide.

## Philosophy

- Discover the right problem before proposing implementation.
- Keep options explicit, assumptions testable, and next-stage handoff safe.
- Resolve WHAT and WHY here; leave detailed HOW for later stages unless the brainstorm itself is architectural.

## When to use

- Use when scope is unclear, goals conflict, or candidate approaches need comparison.
- Use before `he-spec` or `he-plan` when requirements are not yet stable.
- Use when the user asks to brainstorm, compare directions, sharpen requirements, or decide whether the idea needs a spec.

## Inputs

- User intent, constraints, and current context artifacts.
- Relevant system boundaries, risks, and non-goals.
- If the core idea is missing, ask one direct question and do not proceed until the user supplies a feature, problem, or improvement to explore.

## Outputs

- Clarified requirements with ranked options and tradeoffs.
- Domain-language notes when project-specific terms, aliases, relationships, or ambiguities affect the decision.
- A recommendation on whether the next stage should be `he-spec`, `he-plan`, or direct execution.
- A right-sized requirements artifact when durable decisions exist.
- Explicit `spec_required`, `risk_level`, and `complexity` values for non-trivial work.
- Recommended next Harness Engineering stage.
- Include `schema_version: 1` when structured output is requested.

## Procedure

1. Assess whether brainstorming is actually needed or whether the request is already clear enough for the next stage.
2. Clarify objective, constraints, users, non-goals, and unknowns one question at a time.
3. Run a light repo/context scan before making claims about existing behavior or missing capabilities.
4. If domain language is fuzzy, read `CONTEXT-MAP.md` or `CONTEXT.md` when present, then resolve terms one focused question at a time before options harden.
5. Generate 2-3 concrete approaches when multiple plausible directions remain, then evaluate tradeoffs and recommend one.
6. Capture durable requirements and `CONTEXT.md` updates only when the discussion produced decisions worth preserving.
7. Recommend the next Harness Engineering stage and stop instead of drifting into implementation planning.

## Interaction Rules

- Ask one focused question at a time.
- Ask what the user is already thinking before steering the conversation.
- Start broad, then narrow: problem, users, value, constraints, exclusions, edge cases.
- Present options before the recommendation when alternatives are meaningful.
- Keep outputs concise and use repo-relative paths for any generated artifact references.

## Validation

- Ensure requirements and non-goals are explicit and testable.
- Ensure recommendation has rationale tied to constraints.
- Ensure any concrete claim about existing code, routes, tables, configs, or dependencies was verified against the repo or clearly labeled as an assumption.
- Ensure the brainstorm output is strong enough that the next stage does not need to invent user-facing behavior.
- Ensure canonical domain terms, avoided aliases, and unresolved ambiguities are captured or explicitly deferred before handoff.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not proceed to implementation planning when requirement ambiguity remains blocking.
- Do not force a brainstorm when the request is already well specified.
- Keep implementation details such as libraries, schemas, endpoints, and file layouts out of the requirements artifact unless the brainstorm is inherently technical.
- Use Linear issues or comments for durable decision capture; do not create ADRs.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Jumping to solution design before clarifying the actual problem.
- Asking a batch of unrelated questions in one turn.
- Returning unranked options without decision criteria.
- Writing a requirements artifact that still leaves core behavior or scope boundaries undefined.
- Treating multiple names for the same project concept as harmless instead of choosing a canonical term.

## Examples

- "When the user asks for help thinking through a new approval flow before deciding whether it needs a spec."
- "User says, `Inspect the current admin onboarding and compare a few grounded directions before we commit.`"
- "Help me brainstorm this reporting feature and validate the best next Harness Engineering stage."

## Full Context

- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
- Assets: [./assets](./assets)
- Assets directory marker: `assets/`
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Domain model routing: [../../../references/domain-model-routing.md](../../../references/domain-model-routing.md)
Read when: project terminology, `CONTEXT.md`, or Linear issue wording affects the brainstorm.

## Subagent Routing

- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- Resolve available roles from `~/.codex/agents/manifest.json` before spawning helpers.
- Apply the mapped stage policy (`always`, `conditional`, or `manual-only`) before delegation.
- If auto-spawn is unavailable, continue inline and explicitly list the roles the user can launch manually.
