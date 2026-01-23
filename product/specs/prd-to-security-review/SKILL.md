---
name: prd-to-security-review
description: "Generate a security review from a PRD. Use when security requirements, threats, and mitigations must be explicit before build."
metadata:
  short-description: "Threat model + controls from a PRD."
---

# PRD to Security Review

## Pipeline Context
This skill generates a security review, which supports **all stages of the Spec Pipeline** by identifying security considerations early.

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

Generate a security review artifact from a PRD.

## Iron law
- Threat model and trust boundaries must be completed before listing controls.

## Output location
Write the security review in the same directory as the source PRD.
- `feature-x.md` -> `feature-x-security-review.md`

## Required sections
1) Assets and trust boundaries
2) Threat model (STRIDE-style or equivalent)
3) Abuse cases and mitigations
4) AuthN/AuthZ requirements
5) Data handling and privacy controls
6) Logging and monitoring expectations
7) Validation and security test plan

## Constraints
- Avoid implementation details; focus on controls and verification.
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
- For high-risk or disputed findings, run LLM Council and merge outcomes per `design/product-spec/references/llm-council.md`.
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.

## Philosophy
- Favor clarity, explicit tradeoffs, and verifiable outputs.
- Security is not a feature—it's a foundation that affects every other decision.
- Threat modeling is non-negotiable—never ship without identifying and mitigating risks.
- Least privilege is the default—avoid broad permissions unless explicitly justified.

## Empowerment
- The agent is capable of identifying security risks that product and engineering teams might miss.
- Use judgment to prioritize risks based on impact and likelihood—don't be overwhelmed by edge cases.
- Enable teams to ship with confidence by having a clear security review and mitigation plan.
- Don't be the security blocker—focus on actionable, high-impact controls and enable shipping.

## Variation
- Adapt security depth to product sensitivity: consumer products need privacy focus, B2B products need auth and authorization rigor.
- Vary threat modeling scope: public APIs need abuse case modeling, internal tools need data handling controls.
- For data products, expand on data encryption, retention, and access controls.
- For payment products, expand on PCI compliance, fraud detection, and financial security controls.
- Adjust validation strictness based on audience: public products need formal audit, internal products can use lighter review.

## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Anti-patterns
- NEVER skip threat modeling—undefined security assumptions are vulnerabilities.
- DO NOT ignore data flow and trust boundaries—unmapped data exfiltration is a nightmare waiting to happen.
- Avoid vague mitigations like "we'll monitor it"—define specific controls, tests, and owners.
- DO NOT omit authentication/authorization—undefined auth is open doors for attackers.

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
