---
name: prd-to-api-lite
description: "Generate a lite API outline from a PRD with endpoints, example requests/responses, and basic error notes. Use when a minimal contract is sufficient for demo work."
---

# PRD to API Lite

## Pipeline Context
This skill generates a minimal API outline, typically as part of **Stage 3 of the Spec Pipeline** (Build Plan) for demo-grade work.

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

Generate a minimal API outline for demo-grade builds.

## Output location
Write the outline in the same directory as the source PRD.
- `feature-x.md` -> `feature-x-api-lite.md`

## Required sections (concise)
1) Endpoint list (method + path + one-line purpose)
2) One request example per endpoint
3) One response example per endpoint
4) Auth note (if any)
5) Error summary (2-3 common errors)

## Constraints
- No full schema; use examples only.
- Redact secrets/PII by default.
- Mark assumptions explicitly.
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
- Even demo APIs should be implementable—minimal doesn't mean incomplete.
- Examples teach more than descriptions—show concrete requests and responses.
- Simplicity is a virtue—but not at the cost of ambiguity.

## Empowerment
- The agent is capable of turning vague ideas into implementable API outlines quickly.
- Use judgment to add clarity where the input is sparse—fill reasonable gaps for demo work.
- Enable rapid iteration on API design before committing to full specs.

## Variation
- Adapt depth to demo scope: simple CRUD apps need fewer endpoints, complex flows need more.
- Vary example detail: public APIs need extensive examples, internal demos can be lighter.
- For integration-heavy demos, expand on auth and error handling examples.
- For data-heavy demos, expand on request/response schema examples.

## Guiding questions (ask 2-3)
- What is the single most important integration to make real?
- Which errors must a client handle on day one?
- What is explicitly out of scope for the demo?

## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Anti-patterns
- NEVER skip auth notes—even demo APIs need clear authentication.
- DO NOT leave error examples vague—concrete errors prevent integration bugs.
- Avoid minimalism at the expense of clarity—demo APIs should still be implementable.
- DO NOT omit request/response structure—examples without structure are useless.
- NEVER invent endpoints not implied by the PRD.

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
