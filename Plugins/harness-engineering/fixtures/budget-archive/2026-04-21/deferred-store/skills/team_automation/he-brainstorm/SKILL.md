---
name: he-brainstorm
description: Clarify problem scope, requirements, options, and expected behavior before spec or plan stages. Use when what to build, why it matters, or the right direction is ambiguous.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps the full operational workflow in archived references. Use it to decide whether a structured Harness Engineering brainstorm is needed, run a right-sized clarification loop, and hand off with durable requirements when the idea is clear enough.

## Philosophy

- Discover the right problem before proposing implementation.
- Keep options explicit, assumptions testable, and next-stage handoff safe.
- Resolve WHAT and WHY here; leave detailed HOW for later stages unless the brainstorm itself is architectural.

## When to use

- Use when scope is unclear, goals conflict, or candidate approaches need comparison.
- Use before `he-spec` or `he-plan` when requirements are not yet stable.
- Use when the user asks to brainstorm, compare directions, sharpen requirements, or decide whether the idea needs a spec.
- Use when QA intake exposes product ambiguity that must be resolved before filing or implementing a bug.

## Inputs

- Request, artifacts, repo context, and linked Linear issues.

## Outputs

- `schema_version: 1` when structured; result, validation, blockers, and next Harness Engineering action.

## Procedure

1. Assess whether brainstorming is actually needed or whether the request is already clear enough for the next stage.
2. Clarify objective, constraints, users, non-goals, and unknowns one question at a time.
3. Run a light repo/context scan before making claims about existing behavior or missing capabilities.
4. If domain language is fuzzy, read `CONTEXT-MAP.md` or `CONTEXT.md` when present, then resolve terms one focused question at a time before options harden.
5. For QA ambiguity, clarify expected behavior first, then route clear defects to `he-fix-bugs` for Linear intake or route missing contracts to `he-spec`.
6. Generate 2-3 concrete approaches when multiple plausible directions remain, then evaluate tradeoffs and recommend one.
7. Capture durable requirements and `CONTEXT.md` updates only when the discussion produced decisions worth preserving.
8. Recommend the next Harness Engineering stage and stop instead of drifting into implementation planning.

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
- Do not remove important context for budget trimming; move it to references and index it in `../../../references/deferred-context-index.md`.

## Anti-patterns

- Jumping to solution design before clarifying the actual problem.
- Asking a batch of unrelated questions in one turn.
- Returning unranked options without decision criteria.
- Writing a requirements artifact that still leaves core behavior or scope boundaries undefined.
- Treating multiple names for the same project concept as harmless instead of choosing a canonical term.
## Examples

Read when: examples or role-routing details are needed, open the archived references for this skill.
