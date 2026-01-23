---
name: prd-to-qa-cases
description: "Generate QA test cases from PRD acceptance criteria using Given/When/Then and expected results. Use when QA coverage needs explicit, auditable cases."
metadata:
  short-description: "Translate PRDs into QA test cases."
---

# PRD to QA Cases

## Pipeline Context
This skill generates QA test cases, typically as part of **Stage 3 of the Spec Pipeline** (Build Plan) to define detailed test coverage.

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

Generate QA test cases from acceptance criteria.

## Traceability matrix (required)
```markdown
| Acceptance Criteria | Test Case ID | Test Type | Status |
| --- | --- | --- | --- |
| | | | |
```

## Test case template (Given/When/Then)
```markdown
**Test Case ID:** TC-001
**Given** ...
**When** ...
**Then** ...
```

## Output location
Write QA cases in the same directory as the source PRD.
- `feature-x.md` -> `feature-x-qa-cases.md`

## Required sections
1) Test case list (Given/When/Then + expected result)
2) Coverage map (criteria -> cases)
3) Manual vs automated split
4) Data and environment prerequisites

## Constraints
- Keep each test case atomic and independent.
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
- Given/When/Then is a contract—test cases must be executable and unambiguous.
- Atomic tests are maintainable—avoid interdependencies that make debugging impossible.
- Edge cases matter more than happy paths—bugs live in the shadows.

## Empowerment
- The agent is capable of turning acceptance criteria into comprehensive, executable test cases.
- Use judgment to identify high-risk user flows that need deeper test coverage.
- Enable QA teams to ship with confidence through structured, verifiable test suites.

## Variation
- Adapt test granularity to product stability: stable features need fewer regression tests, experimental features need exploratory tests.
- Vary automation focus: API-heavy products need automated integration tests, UX-heavy products need manual exploratory tests.
- For data products, expand on data validation and boundary condition tests.
- For security products, expand on auth, authorization, and attack surface tests.
- Adjust test case detail based on team skills—junior QA teams need more explicit steps.

## Guiding questions (ask 2-3)
- What is the most critical user journey to protect?
- Which acceptance criteria have the highest risk of regression?
- What failures would be catastrophic in production?

## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Anti-patterns
- NEVER skip Given/When/Then structure—vague test cases are untestable and unmaintainable.
- DO NOT create dependent test cases—each test must be atomic and independent.
- Avoid testing happy paths only—edge cases and error states reveal the most bugs.
- DO NOT omit expected results—tests without assertions are meaningless.
- NEVER ship QA cases that do not map to acceptance criteria.

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
