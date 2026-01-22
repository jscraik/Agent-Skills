---
name: prd-to-arch-lite
description: "Generate a lite architecture snapshot from a PRD with a minimal component list, primary flow, and top risks. Use when you need demo-grade architecture guidance without full governance overhead."
---

# PRD to Architecture Lite

## Pipeline Context
This skill generates a minimal architecture snapshot, typically as part of **Stage 3 of the Spec Pipeline** (Build Plan) for demo-grade work.

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

Generate a minimal architecture snapshot for demo-grade builds.

## Output location
Write the snapshot in the same directory as the source PRD.
- `feature-x.md` -> `feature-x-arch-lite.md`

## Required sections (concise)
1) Scope boundary (in/out)
2) Core components (3-7 items)
3) One primary flow (bulleted)
4) Key risks (top 3)

## Diagram
- One Mermaid flowchart for the primary flow.

## Constraints
- No deployment topology, scaling, or vendor decisions.
- Redact secrets/PII by default.
- Mark assumptions explicitly.

## Philosophy
- Favor clarity, explicit tradeoffs, and verifiable outputs.
- Even minimal architectures should be implementable—outline the core components.
- The primary flow is the backbone—never ship without it.
- Simplicity is a virtue for demos—but not at the cost of clarity.

## Empowerment
- The agent is capable of turning vague product ideas into implementable architecture snapshots quickly.
- Use judgment to identify the minimal set of components that explain the design.
- Enable rapid iteration on architecture before committing to full specs.

## Variation
- Adapt component count to complexity: simple apps need 3-5 components, complex flows may need 7-10.
- Vary flow detail: internal tools can have simple flows, customer-facing products need more detail.
- For data products, expand on data flow and transformation components.
- For API products, expand on service boundaries and contracts.

## Guiding questions (ask 2-3)
- What is the smallest set of components that explains the system?
- Where are the trust boundaries?
- What is explicitly out of scope for the demo?

## Anti-patterns
- NEVER skip component boundaries—even minimal architectures need clear separation.
- DO NOT omit the primary flow—without it, the architecture is meaningless.
- Avoid over-engineering demo architectures—minimal doesn't mean missing key elements.
- DO NOT skip top risks—ignoring risks guarantees surprises during implementation.
- NEVER invent infrastructure not implied by the PRD.

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

## Validation
- If findings are disputed or high-risk, run LLM Council and merge outcomes per `design/product-spec/references/llm-council.md`.
- Run Golden Nuggets 2026 checklist in `design/product-spec/SKILL.md` (section: Golden Nuggets 2026).
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.

## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

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
