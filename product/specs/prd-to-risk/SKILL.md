---
name: prd-to-risk
description: "Generate a risk register and mitigation plan from a PRD, covering product, security, delivery, and dependency risks. Use when risks must be explicitly enumerated and owned."
metadata:
  short-description: "Create a PRD-based risk register."
---

# PRD to Risk Register

## Pipeline Context
This skill generates a risk register, which supports **all stages of the Spec Pipeline** by identifying and mitigating risks early.

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

Produce a structured risk register from the PRD.

## Risk register template (strict)
```markdown
| Risk | Likelihood | Impact | Mitigation | Owner | Detection |
| --- | --- | --- | --- | --- | --- |
| | | | | | |
```

## Output location
Write the risk register in the same directory as the source PRD.
- `feature-x.md` -> `feature-x-risk-register.md`

## Required sections
1) Risk summary (top 3)
2) Risk table (risk, likelihood, impact, mitigation, owner)
3) Security and privacy risks
4) Delivery and dependency risks
5) Kill criteria and rollback triggers

## Constraints
- Keep mitigations concrete and testable.
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
- Run Golden Nuggets 2026 checklist in `design/product-spec/SKILL.md` (section: Golden Nuggets 2026).
- For high-impact disagreements, run LLM Council and merge outcomes per `design/product-spec/references/llm-council.md`.
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.

## Philosophy
- Favor clarity, explicit tradeoffs, and verifiable outputs.
- Risk awareness is a superpower—identify risks early or they'll identify you in production.
- Mitigation without owners is wishful thinking—every risk needs a DRI.
- Kill criteria are liberating—define them explicitly so you can fail fast.

## Empowerment
- The agent is capable of identifying risks that product and engineering teams might miss.
- Use judgment to distinguish between genuine risks and noise—prioritize impact and likelihood.
- Enable teams to ship with confidence by having a clear risk mitigation plan.
- Trust the risk register but don't be paralyzed—if risks are mitigated, proceed with confidence.

## Variation
- Adapt risk depth to product stage: discovery needs user and scope risks, production needs operational and scaling risks.
- Vary mitigation granularity: high-impact risks need detailed plans, low-impact risks need brief notes.
- For regulated products, expand on compliance and audit risks.
- For data products, expand on privacy, security, and data quality risks.
- For platform products, expand on integration and compatibility risks.

## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Anti-patterns
- NEVER skip mitigation strategies—unmitigated risks are risks, not documented concerns.
- DO NOT ignore security or privacy risks—these can kill products and harm users.
- Avoid vague mitigations like "we'll monitor it"—define specific actions, owners, and triggers.
- DO NOT omit kill criteria—undefined exit points guarantee sunk-cost failures.

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
