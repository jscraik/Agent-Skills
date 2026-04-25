---
name: he-plan
description: Create or update an execution plan from an approved spec or clarified scope. Use when work needs sequencing, validation gates, and Linear-aware task breakdown before implementation.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

## Philosophy

- Plans should be executable, testable, and constraint-aware.
- Resolve risk and sequencing ambiguity before coding.
- Stay in planning mode when directly invoked.

## When to use

- Use when requirements exist and implementation sequencing must be defined.
- Use before `he-work` when execution tasks and verification strategy are not yet explicit.
- Use when a spec, brainstorm, bug report, or raw feature description must become a durable implementation plan.

## Inputs

- Request, artifacts, repo context, and linked Linear issues.

## Outputs

- `schema_version: 1` when structured; result, validation, blockers, and next Harness Engineering action.

## Procedure

1. Resolve the best source: existing plan, requirements doc, spec, brainstorm output, Linear issue, or direct request.
2. Resume or deepen a matching current plan instead of duplicating it.
3. Carry forward problem frame, scope, requirements, and open questions from the authoritative artifact.
4. Check interface and domain readiness before task decomposition; route to `he-deepen-spec` when contracts or terms are missing.
5. Put blockers first for Linear QA issue sets, preserve issue links, and keep independent defects parallel.
6. Research local patterns only when they affect sequencing or risk.
7. Decompose into ordered, verifiable tasks with dependencies, tests, and next-stage handoff.

## Validation

- Ensure tasks are actionable and independently verifiable.
- Ensure dependencies, rollback, and risk controls are explicit.
- Ensure the plan uses the most authoritative available source and does not silently drop upstream requirements.
- Ensure new caller-facing interfaces and domain terms are specified before implementation tasks.
- Link Linear decision notes when durable tradeoffs shaped the plan.
- Ensure the chosen route (`fresh`, `resume`, or `deepen`) matches the artifact state.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not produce plan steps that depend on unstated assumptions.
- Do not turn planning into implementation, test execution, or speculative debugging.
- Do not silently convert true product blockers into technical assumptions.
- Do not create ADRs; use Linear issues or comments for durable decision capture.
- Do not remove important context for budget trimming; move it to references and index it in `../../../references/deferred-context-index.md`.

## Anti-patterns

- Producing abstract plans without executable task boundaries.
- Omitting verification intent for critical tasks.
- Planning implementation tasks around an interface that has not been designed.
- Decomposing tasks around ambiguous project terms that should have been resolved upstream.
- Replanning from scratch when a current plan should be updated.
- Routing to execution while the user is still asking for planning.
## Examples

Read when: examples or role-routing details are needed, open the archived references for this skill.
