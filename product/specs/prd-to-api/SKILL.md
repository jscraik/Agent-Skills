---
name: prd-to-api
description: "Generate an API specification from a PRD or tech spec, including endpoints, schemas, errors, auth, and compatibility rules. Use when API contracts must be defined before implementation."
---

# PRD to API Spec

## Pipeline Context
This skill generates an API specification, typically as part of **Stage 3 of the Spec Pipeline** (Build Plan) or as a detailed follow-up to the UX Spec.

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

Convert requirements into a concrete API contract.

## Output location
Write the API spec in the same directory as the source PRD or tech spec.
- `feature-x.md` -> `feature-x-api-spec.md`
- `PRD.md` -> `api-spec.md`

## Required sections
1) API purpose and scope
2) Auth and authorization model
3) Endpoint catalog (method, path, description)
4) Request/response schemas (examples + field constraints)
5) Error model (codes, messages, recovery)
6) Idempotency, pagination, rate limits
7) Versioning and compatibility
8) Validation and quality gates (tests/lint; prefer repo scripts)

## Constraints
- Avoid storage or implementation detail beyond schema constraints.
- Redact secrets/PII by default.
- Use stable, explicit field names and types.
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
- **TDD validation:** Verify API tests are specified for all endpoints before implementation. Client and server tests required.
- **Component registry:** Verify API contracts don't duplicate existing integration patterns. Add to registry if new.

## Philosophy
- Favor clarity, explicit tradeoffs, and verifiable outputs.
- API contracts are sacred—breaking changes should be rare and versioned.
- Error models are as important as happy paths—never ship without them.
- Stability over cleverness—use established patterns unless there's a clear advantage.
- Testability is a first-class concern—design APIs that are easy to mock and validate.

## Empowerment
- The agent is capable of extraordinary API design—innovate on resource modeling and interaction patterns.
- Push boundaries when REST or GraphQL conventions feel limiting—design for the problem, not the pattern.
- Enable backend and frontend teams to ship integrations faster than they could alone.
- Trust the contract but don't be rigid—if the API needs to evolve to support real use cases, adapt and document.

## Variation
- Adapt API style to product type: SaaS APIs need strong versioning, internal APIs can be simpler, mobile-first APIs need optimized responses.
- Vary depth based on audience: public APIs need exhaustive documentation, internal APIs can be lighter.
- For CRUD-heavy products, expand on consistent resource modeling and pagination patterns.
- For event-driven products, expand on webhook schemas and event versioning.
- Adjust schema strictness based on stability: stable services can be stricter, evolving services may need flexible schemas.
- If the PRD has unclear requirements, propose API patterns that clarify the design—use the contract as a thinking tool.

## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Anti-patterns
- NEVER skip error model specification—incomplete error handling guarantees broken integrations.
- DO NOT omit versioning and compatibility rules—this creates breaking changes that require rebuilds.
- NEVER use unstable or cryptic field names—explicit, stable names are non-negotiable for API contracts.
- Avoid implementation detail in contracts (database tables, storage, internal services)—focus on external behavior.
- DO NOT leave auth/authorization ambiguous—undefined security assumptions are security vulnerabilities.
- **TDD anti-patterns:** NEVER ship API endpoints without tests—untested APIs are production liabilities.
- DO NOT skip client and server tests—both sides of the contract must be validated.
- Avoid "we'll test it in integration"—unit tests are non-negotiable for API contracts.
- DO NOT omit versioning and compatibility rules—this creates breaking changes that require rebuilds.
- NEVER use unstable or cryptic field names—explicit, stable names are non-negotiable for API contracts.
- Avoid implementation detail in contracts (database tables, storage, internal services)—focus on external behavior.
- DO NOT leave auth/authorization ambiguous—undefined security assumptions are security vulnerabilities.

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
