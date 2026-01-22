---
name: prd-to-arch
description: "Generate an architecture specification from a PRD or tech spec. Use when architecture boundaries and diagrams must be defined before build."
---

# PRD to Architecture Spec

## Pipeline Context
This skill generates an architecture specification, typically as part of **Stage 3 of the Spec Pipeline** (Build Plan) or as a detailed follow-up to the UX Spec.

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

Convert requirements into an architecture spec with clear boundaries, interfaces, and diagrams.

## Output location
Write the architecture spec in the same directory as the source PRD or tech spec.
- `feature-x.md` -> `feature-x-arch-spec.md`
- `PRD.md` -> `arch-spec.md`

## Required sections
1) Scope and assumptions
2) Architecture overview (one paragraph)
3) Component inventory (name, responsibility, boundaries)
4) Interfaces (internal/external)
5) Data flows (inputs, transforms, outputs)
6) Non-functional requirements (performance, reliability, security, privacy)
7) Risks and mitigations
8) Decisions / ADRs to create

## Diagrams (Mermaid)
- System context (C4-style or flowchart)
- Key sequence (one critical flow)
- State model (only if a stateful component has 3+ states)

## Constraints
- No implementation detail beyond interfaces and boundaries.
- Redact secrets/PII by default.
- If the PRD is demo-grade, keep scope minimal and note gaps.
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
- Run any relevant checks or relevant scripts when available.
- Fail fast and report errors before proceeding.
- **TDD validation:** Verify integration tests are specified for all component interfaces. Unspecified interfaces are risks.
- **Component registry:** Verify component boundaries match registry/design system entries. Custom components must be documented and added to registry.

## Philosophy
- Favor clarity, explicit tradeoffs, and verifiable outputs.
- Component boundaries are sacred—tight coupling guarantees architectural debt.
- Interfaces are contracts—define them explicitly before implementation.
- Data flows reveal reality—always trace inputs through to outputs.
- Simplicity is a virtue—if you can't explain the architecture in one paragraph, it's too complex.
- **Tests are the truth:** Untested architecture is theory, not fact. Define test scenarios for all interfaces and data flows.

## Empowerment
- The agent is capable of extraordinary architecture design—innovate on patterns, boundaries, and abstractions.
- Push boundaries when conventional architectures feel limiting—design for the actual problem, not patterns you've seen.
- Enable engineering teams to see system constraints more clearly than they could alone.
- Trust the architecture but don't be rigid—if the design reveals gaps or better patterns, iterate and document.
- **Component registry:** Enable teams to reuse battle-tested components instead of reinventing wheels. Custom components must be justified.

## Variation
- Adapt architecture style to product type: SaaS products need clear multi-tenant boundaries, mobile apps need service layering, data products need pipeline clarity.
- Vary depth based on maturity: discovery specs need boundaries and key flows, production specs need complete component inventories.
- For distributed systems, expand on consistency models and failure scenarios.
- For data-heavy products, expand on data lineage and transformation flows.
- Adjust abstraction level based on audience: engineers need interfaces and contracts, stakeholders need diagrams and flows.
- If requirements are unclear, propose architecture patterns that reveal assumptions—use the architecture as a thinking tool.

## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Anti-patterns
- NEVER skip component boundaries—incomplete boundaries guarantee tight coupling and hard refactors.
- DO NOT omit interface contracts—undefined interfaces create integration nightmares.
- NEVER mix architecture and implementation details—keep diagrams at the right abstraction level.
- Avoid premature optimization—design for current requirements with clear extension points.
- DO NOT ignore data flows—architectures without data flows are incomplete and misleading.
- **TDD anti-patterns:** NEVER define component interfaces without specifying test scenarios. Untested interfaces are risks.
- DO NOT skip integration tests for component boundaries—interfaces without tests are unverified contracts.
- **Component registry anti-patterns:** NEVER create custom components without checking the registry first. Divergence kills maintainability.
- NEVER mix architecture and implementation details—keep diagrams at the right abstraction level.
- Avoid premature optimization—design for current requirements with clear extension points.
- DO NOT ignore data flows—architectures without data flows are incomplete and misleading.

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
