---
name: tech-to-data
description: "Generate a data specification from a tech spec covering schemas, lifecycle, retention, and access controls. Use when data contracts must be explicit before implementation."
---

# Tech Spec to Data Spec

## Response format (strict)
The first line of any response MUST be `## Inputs`.
Every response must include:
- `## Inputs`
- `## Outputs`
- `## When to use`

Produce a data specification derived from a tech spec.

## Output location
Write the data spec in the same directory as the source tech spec.
- `feature-x-tech-spec.md` -> `feature-x-data-spec.md`

## Required sections
1) Data entities and schema tables
2) Field constraints and indexes
3) Data sources and contracts
4) Lifecycle and retention
5) Migration and backfill plan
6) Privacy and access controls

## Constraints
- Use explicit types and constraints.
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
