---
name: prd-to-testplan
description: "Generate a test plan and validation matrix from a PRD, mapping acceptance criteria to test types and quality gates. Use when verification strategy must be explicit before build."
---

## Test strategy
- Unit: Test individual functions and classes in isolation. Aim for >80% coverage for critical paths.
- Integration: Test component interactions and API contracts. Mock external dependencies.
- E2E: Test critical user journeys end-to-end. Limit to 5-10 scenarios per epic.
- Failure-mode: Test error handling, edge cases, and system degradation.

## TDD Workflow (non-negotiable for non-trivial work)
- Write tests BEFORE implementation for any logic with >2 branches or complex state
- Use Given/When/Then format for test clarity
- Failing tests block story completion—DO NOT merge PRs with failing tests
- Manual verification is NOT evidence—automated tests are the truth
- Refactor while keeping tests green—TDD enables fearless refactoring
## Pipeline Context
This skill generates a test plan, typically as part of **Stage 3 of the Spec Pipeline** (Build Plan) to define the testing strategy.

**Related stages:**
- Stage 1: Foundation Spec (What + Why) — See `design/product-spec` or use `design/references/foundation-spec-template.md`
- Stage 2: UX Spec (How it feels) — See `design/product-spec` or use `design/references/ux-spec-template.md`
- Stage 3: Build Plan (How we execute) — See `design/product-spec` or use `design/references/build-plan-template.md`

**Shared references:**
- `design/references/build-plan-template.md` — Build Plan template
- `design/references/spec-linter-checklist.md` — Quality gate checklist

## Response format (strict)
The first line of any response MUST be `## Inputs`.
Every response must include:
- `## Inputs`
- `## Outputs`
- `## When to use`

Produce a test plan mapped to PRD acceptance criteria.

## Output location
Write the test plan in the same directory as the source PRD.
- `feature-x.md` -> `feature-x-test-plan.md`

## Required sections
1) Scope and assumptions
2) Acceptance criteria to tests matrix
3) Test types (unit/integration/e2e/manual)
4) Test data and fixtures
5) Quality gates and commands (prefer repo scripts; otherwise use `~/.codex/instructions/tooling.md`)
6) Coverage gaps and risks

## Constraints
- Use Given/When/Then when acceptance criteria are in that style.
- Redact secrets/PII by default.
## References
- Contract: references/contract.yaml
- Evals: references/evals.yaml

## When to use
- Use this skill when the task matches its description and triggers.
- If the request is outside scope, route to the appropriate skill.

## Inputs
- User request details and any relevant files/links.

## Outputs
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.

## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.

## Validation
- If findings are disputed or high-risk, run LLM Council and merge outcomes per `design/product-spec/references/llm-council.md`.
- Run Golden Nuggets 2026 checklist in `design/product-spec/SKILL.md` (section: Golden Nuggets 2026).
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.

## Philosophy
- Favor clarity, explicit tradeoffs, and verifiable outputs.
- Test plans are contracts—every acceptance criterion must have a corresponding test.
- Quality gates are sacred—never ship without passing them.
- Coverage gaps are debt—call them out explicitly so they don't become surprises.

## Empowerment
- The agent is capable of turning acceptance criteria into comprehensive test strategies.
- Use judgment to identify risky areas that need deeper test coverage.
- Enable QA teams to ship with confidence through structured, verifiable test plans.

## Variation
- Adapt test depth to product risk: critical paths need E2E tests, internal tools need less.
- Vary automation focus: stable APIs need automated regression, experimental features need manual exploration.
- For data products, expand on data validation and edge case testing.
- For security-sensitive products, expand on auth, authorization, and input validation tests.
- Adjust test granularity based on team capacity—high-velocity teams prefer fewer, broader tests.

## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Anti-patterns
- NEVER skip validation commands—untested acceptance criteria are meaningless.
- DO NOT omit coverage gaps—missing test areas guarantee production bugs.
- Avoid test cases that aren't tied to acceptance criteria—tests without requirements are waste.
- DO NOT skip quality gates—unvalidated tests give false confidence.

## Response format (required)
The first line of any response MUST be `## Inputs`.
Every user-facing response must include these headings:
- `## Inputs`
- `## Outputs`
- `## When to use`

## Examples
- "Use this skill for a typical request in its domain."

Failure/out-of-scope template (use verbatim structure):
```markdown
## Inputs
Objective: <what you received>

Plan:
1) <brief>
2) <brief>

Next step: <single request>

## Outputs
- <what would be produced if in scope>

## When to use
- <when this skill applies>
```
