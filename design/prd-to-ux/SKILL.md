---
name: prd-to-ux
description: "Generate UX specifications from PRDs, feature specs, or product requirements for mockup tools. Use when preparing UX foundations before visual design."
---

# PRD to UX Translation

## Pipeline Context
This skill implements **Stage 2 of the Spec Pipeline** (UX Spec). It converts a Foundation Spec into a detailed UX specification that removes ambiguity and prepares the spec for implementation planning.

**Related stages:**
- Stage 1: Foundation Spec (What + Why) — See `design/product-spec` or use `design/references/foundation-spec-template.md`
- Stage 3: Build Plan (How we execute) — See `design/product-spec` or use `design/references/build-plan-template.md`

**Shared references:**
- `design/references/ux-spec-template.md` — UX Spec template (primary output)
- `design/references/spec-linter-checklist.md` — Quality gate checklist
- `design/references/prompts.md` — UX ambiguity killer prompt

## Response format (strict)
The first line of any response MUST be `## Inputs`.
Every response must include:
- `## Inputs`
- `## Outputs`
- `## When to use`

Translate requirements into UX foundations via six forced passes. Do not produce visual specs until all passes are complete.

## Output location
Write the UX specification to a file in the same directory as the source PRD.
- `feature-x.md` -> `feature-x-ux-spec.md`
- `PRD.md` -> `UX-spec.md`

## Iron law
No visual specs until all six passes complete.

## The six passes (execute in order)

### Pass 1: Mental model
```markdown
## Pass 1: Mental Model

**Primary user intent:** [one sentence]

**Likely misconceptions:**
- [misconception]

**UX principle to reinforce/correct:** [principle]
```

### Pass 2: Information architecture
```markdown
## Pass 2: Information Architecture

**All user-visible concepts:**
- [concept]

**Grouped structure:**

### [Group Name]
- [Concept]: [Primary/Secondary/Hidden]
- Rationale: [one sentence]
```

### Pass 3: Affordances
```markdown
## Pass 3: Affordances

| Action | Visual/Interaction Signal |
|--------|---------------------------|
| [Action] | [Signal] |

**Affordance rules:**
- If user sees X, they should assume Y
```

### Pass 4: Cognitive load
```markdown
## Pass 4: Cognitive Load

**Friction points:**
| Moment | Type | Simplification |
|--------|------|----------------|
| [Where] | Choice/Uncertainty/Waiting | [How to reduce] |

**Defaults introduced:**
- [Default]: [Rationale]
```

### Pass 5: State design
```markdown
## Pass 5: State Design

### [Element/Screen]

| State | User Sees | User Understands | User Can Do |
|-------|-----------|------------------|-------------|
| Empty | | | |
| Loading | | | |
| Success | | | |
| Partial | | | |
| Error | | | |
```

### Pass 6: Flow integrity
```markdown
## Pass 6: Flow Integrity

**Flow risks:**
| Risk | Where | Mitigation |
|------|-------|------------|
| [Risk] | [Location] | [Guardrail/Nudge] |

**Visibility decisions:**
- Must be visible: [List]
- Can be implied: [List]

**UX constraints:** [Rules]
```

## Then: Visual specifications
Only after all passes, write visual specs (layout, components, interactions, responsive behavior).

## Output template
```markdown
# UX Specification: [Product Name]

## Pass 1: Mental Model
...

## Pass 2: Information Architecture
...

## Pass 3: Affordances
...

## Pass 4: Cognitive Load
...

## Pass 5: State Design
...

## Pass 6: Flow Integrity
...

---

## Visual Specifications
...
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
- If findings are disputed or high-risk, run LLM Council and merge outcomes per `design/product-spec/references/llm-council.md`.
- Run Golden Nuggets 2026 checklist in `design/product-spec/SKILL.md` (section: Golden Nuggets 2026).
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.
- **Component registry:** Verify all UI components exist in the registry/design system. Custom components must be documented and added to registry.

## Philosophy
- Favor clarity, explicit tradeoffs, and verifiable outputs.
- Mental model alignment is the foundation—never skip it.
- Six-pass sequence is non-negotiable for removing ambiguity.
- Context matters: adapt each pass to the product type and user sophistication.
- NEVER ship UX without explicit state design for all key screens.
- **Design system first:** Prefer existing UI components from the registry. Custom implementations should be rare and justified.
- **Tests validate affordances:** UX acceptance criteria must be testable. If you can't write a Given/When/Then test for it, the UX is too vague.
- Mental model alignment is the foundation—never skip it.
- Six-pass sequence is non-negotiable for removing ambiguity.
- Context matters: adapt each pass to the product type and user sophistication.
- NEVER ship UX without explicit state design for all key screens.

## Empowerment
- The agent is capable of extraordinary UX work—use judgment to adapt the six passes to complex domains.
- Push boundaries when the six-pass framework feels limiting—innovate on mental models and affordances.
- Enable designers and product teams to see their requirements more clearly than they could alone.
- Trust the process but don't be rigid—if the six-pass sequence reveals gaps, expand or iterate.
- **Component registry:** Enable teams to reuse battle-tested UI components instead of reinventing. Custom components must be justified.

## Variation
- Adapt the six-pass sequence to product type: SaaS tools need strong IA, mobile apps need tight state design, dashboards need clear affordances.
- Vary depth based on scope: discovery PRDs may need lighter passes; production-ready specs need exhaustive coverage.
- For highly visual products, expand Pass 3 (Affordances) and Pass 5 (State Design) with interaction patterns.
- For information-dense products, expand Pass 2 (Information Architecture) with grouping hierarchies.
- Adjust mental model depth based on user sophistication: expert users need less hand-holding, novice users need stronger reinforcement.
- If a pass reveals critical gaps, run additional iterations before proceeding—quality over rigid sequencing.

## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Anti-patterns
- NEVER skip the six-pass sequence or produce visual specs before completing all passes—this guarantees ambiguous UX decisions that require rebuilds.
- DO NOT invent visual specs or component details without grounding them in the six forced passes.
- NEVER assume users will understand implicit affordances—explicitly state what is clickable, editable, or destructive.
- Avoid generic UX patterns without domain consideration—adapt the six passes to the specific product type (SaaS, mobile, dashboard, etc.).
- DO NOT omit state design for screens with 3+ states—incomplete state design guarantees broken error/edge cases.
- **Component registry anti-patterns:** NEVER create custom UI components without checking the registry first. Custom components create divergence and maintenance burden.

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
