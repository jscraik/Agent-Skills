---
name: prd-clarifier
description: "Analyze and refine PRDs via structured Q&A and a tracked session log. Use when asked to resolve PRD ambiguities, gaps, or clarification questions."
---

# PRD Clarifier

## Pipeline Context
This skill refines PRDs via structured Q&A, which supports **all stages of the Spec Pipeline** by resolving ambiguities and gaps.

**Related stages:**
- Stage 1: Foundation Spec (What + Why) — See `design/product-spec` or use `design/references/foundation-spec-template.md`
- Stage 2: UX Spec (How it feels) — See `design/product-spec` or use `design/references/ux-spec-template.md`
- Stage 3: Build Plan (How we execute) — See `design/product-spec` or use `design/references/build-plan-template.md`

**Shared references:**
- `design/references/spec-linter-checklist.md` — Quality gate checklist
- `design/references/prompts.md` — Socratic reviewer prompt

Refine PRDs by asking targeted questions and recording answers in a session log stored alongside the source PRD.

## Response format (strict)
The first line of any response MUST be `## Inputs`.
Every response must include:
- `## Inputs`
- `## Outputs`
- `## When to use`

Template:
```markdown
## Inputs
...

## Outputs
...

## When to use
...
```

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

## Initialization protocol (mandatory, in order)
1) Identify the PRD file location.
2) Create a tracking document in the same directory.
   - Name: `{prd-basename}-clarification-session.md`
3) Ask for depth preference using the AskUserQuestion tool.
4) Update the tracking document with the selected depth + total questions.

### Tracking document template
```markdown
# PRD Clarification Session

**Source PRD**: [filename]
**Session Started**: [date/time]
**Depth Selected**: [TBD - pending user selection]
**Total Questions**: [TBD]
**Progress**: 0/[TBD]

---

## Session Log

[Questions and answers will be appended here]
```

### Depth question (AskUserQuestion)
```json
{
  "questions": [{
    "question": "What depth of PRD analysis would you like?",
    "header": "Depth",
    "multiSelect": false,
    "options": [
      {"label": "Quick (5 questions)", "description": "Rapid surface-level review of critical ambiguities only"},
      {"label": "Medium (10 questions)", "description": "Balanced analysis covering key requirement areas"},
      {"label": "Long (20 questions)", "description": "Comprehensive review with detailed exploration"},
      {"label": "Ultralong (35 questions)", "description": "Exhaustive deep-dive leaving no stone unturned"}
    ]
  }]
}
```

Depth mapping:
- Quick = 5
- Medium = 10
- Long = 20
- Ultralong = 35

## Questioning strategy
- Prioritize critical-path items, high ambiguity, integration points, edge cases, and non-functional requirements.
- After each answer, reassess for new ambiguities and adapt.
- Ask one clear question at a time; avoid compound questions.

## Guiding questions (use 3-5 every session)
- What must be true for this to work on day one?
- What breaks if data is messy, late, or missing?
- What is the smallest believable MVP?
- What is explicitly out of scope for V1?
- What is the primary success metric + 1 guardrail?

## Question categories (cover across the session)
1) User/stakeholder clarity
2) Functional requirements
3) Non-functional requirements
4) Technical constraints
5) Edge cases and error handling
6) Data requirements and privacy
7) Business rules
8) Acceptance criteria
9) Scope boundaries
10) Dependencies and risks

## Execution rules
- Create the tracking document before any questions.
- Always use AskUserQuestion; include 2-4 options.
- Ask the full number of questions for the chosen depth.
- Update the tracking document after every answer.

## Session completion
1) Summarize key clarifications.
2) List remaining ambiguities.
3) Suggest priority order for unresolved items.
4) Offer to update the PRD.

## Output format for session log
Append each Q&A in the tracking doc as:
```markdown
## Question N
**Category**: [area]
**Ambiguity Identified**: [gap]
**Question Asked**: [question]
**User Response**: [answer]
**Requirement Clarified**: [resolution]
```

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
- If critical ambiguity remains after the session, run LLM Council and merge outcomes per `design/product-spec/references/llm-council.md`.
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.

## Philosophy
- Favor clarity, explicit tradeoffs, and verifiable outputs.

## Empowerment
- You are capable of challenging scope creep and forcing explicit tradeoffs.
- Enable clarity by pushing past “good enough” answers.
- You are empowered to pause and re-scope if answers conflict.
- Use the clarifier to prevent rework and defend focus.
- You are authorized to insist on evidence or mark an explicit Evidence gap.

## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Variation
- Vary depth by risk: regulated or safety-critical features require Long/Ultralong.
- Vary depth by certainty: exploratory ideas use shorter depth with explicit assumptions.
- For integrations, prioritize data contracts and failure modes early.

## Anti-patterns
- Avoid vague guidance without concrete steps.
- Do not invent results or commands.
- NEVER finalize without an explicit MVP vs later split.
- DO NOT proceed without a measurable success metric.
- NEVER accept "we'll figure it out later" as a requirement.
- DO NOT skip ambiguity resolution for integration points.
- NEVER skip security/privacy questions when data is involved.
- DO NOT let unresolved contradictions pass without escalation.

## Examples
- "Clarify the PRD for the onboarding flow."

## Response format (required)
The first line of any response MUST be `## Inputs`.
Every user-facing response must include these headings:
- `## Inputs`
- `## Outputs`
- `## When to use`
