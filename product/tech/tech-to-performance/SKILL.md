---
name: tech-to-performance
description: Generate a performance plan from a tech spec with budgets, load tests,
  thresholds, and monitoring. Use when performance targets must be explicit and verifiable.
metadata:
  short-description: Generate a performance plan from a tech spec with budgets, load
    tests, thresh...
---

# Tech Spec to Performance Plan

## Response format (strict)
The first line of any response MUST be `## Inputs`.
Every response must include:
- `## Inputs`
- `## Outputs`
- `## When to use`

Generate a performance plan derived from a tech spec.

## Output location
Write the performance plan in the same directory as the source tech spec.
- `feature-x-tech-spec.md` -> `feature-x-performance-plan.md`

## Required sections
1) Performance objectives (latency, throughput, availability)
2) Budgets (per endpoint or component)
3) Load and stress test plan
4) Bottleneck risks and mitigations
5) Monitoring and alerting thresholds
6) Validation and acceptance criteria

## Constraints
- Use measurable thresholds; state assumptions clearly.
- Redact secrets/PII by default.
## References
- Contract: references/contract.yaml
- Evals: references/evals.yaml

## Scope and triggers
- Use this skill when the task matches its description and triggers.
- If the request is outside scope, route to the appropriate skill.

## Required inputs
- User request details and any relevant files/links.

## Deliverables
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.

## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.

## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.

## Philosophy
- Favor clarity, explicit tradeoffs, and verifiable outputs.

## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Anti-patterns
- Avoid vague guidance without concrete steps.
- Do not invent results or commands.

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
## Required inputs
Objective: <what you received>

Plan:
1) <brief>
2) <brief>

Next step: <single request>

## Deliverables
- <what would be produced if in scope>

## Scope and triggers
- <when this skill applies>
```

## Variation
- Vary tone, depth, and structure based on context.
- Avoid repeating the same outline across outputs.

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.
