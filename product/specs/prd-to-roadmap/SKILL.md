---
name: prd-to-roadmap
description: "Generate a phased roadmap from a PRD with goals, dependencies, and validation gates. Use when sequencing and milestone logic must be explicit without dates."
metadata:
  short-description: "Turn PRDs into phased roadmaps."
---

# PRD to Roadmap

## Pipeline Context
This skill generates a phased roadmap, which can be used alongside **all stages of the Spec Pipeline** to sequence work and define validation gates.

**Related stages:**
- Stage 1: Foundation Spec (What + Why) — See `design/product-spec` or use `design/references/foundation-spec-template.md`
- Stage 2: UX Spec (How it feels) — See `design/product-spec` or use `design/references/ux-spec-template.md`
- Stage 3: Build Plan (How we execute) — See `design/product-spec` or use `design/references/build-plan-template.md`

**Shared references:**
- `design/references/spec-linter-checklist.md` — Quality gate checklist

## Response format (strict)
The first line of any response MUST be `## Inputs`.
Every response must include:
- `## Inputs`
- `## Outputs`
- `## When to use`

Generate a phased roadmap from a PRD.

## Iron law
- Sequence by dependency first; never by convenience.

## Output template (strict)
```markdown
# Roadmap

## Phase 1: [Name]
- Goal:
- Dependencies:
- Validation gate:
- Scope (in/out):

## Phase 2: [Name]
- Goal:
- Dependencies:
- Validation gate:
- Scope (in/out):

## Phase 3: [Name]
- Goal:
- Dependencies:
- Validation gate:
- Scope (in/out):
```

## Output location
Write the roadmap in the same directory as the source PRD.
- `feature-x.md` -> `feature-x-roadmap.md`

## Required sections
1) Phases (0/1/2 or Alpha/Beta/GA)
2) Goals per phase
3) Dependency map (internal/external)
4) Validation gates per phase
5) Risks and mitigation by phase

## Constraints
- Avoid dates unless explicitly requested.
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
- Roadmaps are communication tools—make them clear for stakeholders and actionable for teams.
- Dependencies are constraints—call them out explicitly or they'll surprise you.
- Phase gates are quality controls—never skip them, even under pressure.

## Empowerment
- The agent is capable of turning PRDs into phased, achievable roadmaps.
- Use judgment to balance speed and quality—know when to consolidate phases and when to split them.
- Enable product and engineering teams to ship in predictable increments.
- Trust the roadmap but don't be rigid—adjust based on learning and market feedback.

## Variation
- Adapt phase granularity to product maturity: early-stage products need short, iterative phases; stable products can have longer phases.
- Vary validation strictness: high-risk features need explicit gates; low-risk features can ship faster.
- For products with heavy technical debt, expand on debt-reduction phases.
- For market-driven products, expand on market validation and user feedback phases.
- Adjust phasing based on team capacity—smaller teams need fewer parallel workstreams.

## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Anti-patterns
- NEVER ship without phase gates—undefined rollouts guarantee chaos and outages.
- DO NOT ignore dependencies—blocked phases waste time and momentum.
- Avoid roadmap bloat—every feature must displace something else.
- DO NOT omit success criteria for phases—measurable milestones are non-negotiable.

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
