---
name: ux-spec-to-prompts
description: "Generate build-order UI prompts from UX specs or PRDs. Use when a spec must be split into self-contained prompts for UI tools."
---

# UX Spec to Build-Order Prompts

## Response format (strict)
The first line of any response MUST be `## Inputs`.
Every response must include:
- `## Inputs`
- `## Outputs`
- `## When to use`

Transform UX specs into a sequence of self-contained prompts ordered by dependency.

## Build order
1) Foundation
2) Layout shell
3) Core components
4) Interactions
5) States and feedback
6) Polish

## Prompt structure (each prompt)
```markdown
## [Feature Name]

### Context
[Where this fits]

### Requirements
- [Behavior/appearance]

### States
- Default: [description]

### Interactions
- [User interactions]

### Constraints
- [What NOT to include]
- Redact secrets/PII by default.
```
## Process
1) Identify atomic units (screens, components, interactions, states).
2) Map dependencies.
3) Sequence by dependency.
4) Write self-contained prompts (no cross-references).

## Self-containment rules
- Include all context, measurements, states, interactions for that prompt.
- Do not reference other prompts.

## Output format
```markdown
# Build-Order Prompts: [Project Name]

## Overview
[1-2 sentences]

## Build Sequence
1. [Prompt name] - [brief]
2. [Prompt name] - [brief]

---

## Prompt 1: [Feature Name]
[Full prompt]

---

## Prompt 2: [Feature Name]
[Full prompt]
```

## Quality checklist
- Every measurement captured
- Every state captured
- Every interaction captured
- No cross-prompt references
- Dependencies respected

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
