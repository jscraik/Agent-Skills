---
name: prd-to-accessibility
description: "Generate accessibility requirements and checks from a PRD, aligned to WCAG targets and key journeys. Use when accessibility expectations must be explicit and testable."
metadata:
  short-description: "Derive accessibility requirements from PRDs."
---

# PRD to Accessibility Spec

## Pipeline Context
This skill generates accessibility requirements, which support **Stage 2 of the Spec Pipeline** (UX Spec) by ensuring accessibility is explicit in the UX design.

**Related stages:**
- Stage 1: Foundation Spec (What + Why) — See `design/product-spec` or use `design/references/foundation-spec-template.md`
- Stage 2: UX Spec (How it feels) — See `design/product-spec` or use `design/references/ux-spec-template.md`
- Stage 3: Build Plan (How we execute) — See `design/product-spec` or use `design/references/build-plan-template.md`

**Shared references:**
- `design/references/ux-spec-template.md` — UX Spec template
- `design/references/spec-linter-checklist.md` — Quality gate checklist

## Response format (strict)
The first line of any response MUST be `## Inputs`.
Every response must include:
- `## Inputs`
- `## Outputs`
- `## When to use`

Produce accessibility requirements and validation guidance from a PRD.

## Iron law
- No visual specs or layout guidance until accessibility requirements are complete.

## Output template (strict)
```markdown
# Accessibility Spec

## Target standard and scope

## Key user journeys and assistive tech assumptions

## Requirements by component/flow

## Non-text content and media alternatives

## Keyboard, focus, and navigation rules

## Validation plan (automated + manual)

## Known limitations and risks
```

## Output location
Write the accessibility spec in the same directory as the source PRD.
- `feature-x.md` -> `feature-x-accessibility-spec.md`

## Required sections
1) Target standard (e.g., WCAG 2.2 AA) and scope
2) Key user journeys and assistive tech assumptions
3) Accessibility requirements by component/flow
4) Non-text content and media alternatives
5) Keyboard, focus, and navigation rules
6) Validation plan (automated + manual)
7) Known limitations and risks

## Constraints
- Keep requirements testable and user-visible.
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
- Accessibility is not a feature—it's a fundamental requirement for inclusive products.
- Test with real users—automated tools catch only a fraction of accessibility issues.
- Progressive enhancement is a strategy—ensure core functionality works for everyone.

## Empowerment
- The agent is capable of identifying accessibility gaps that designers and engineers might miss.
- Use judgment to prioritize accessibility requirements based on user impact and implementation effort.
- Enable teams to ship products that are usable by the widest possible audience.
- Don't be intimidated by accessibility standards—focus on user experience first, compliance follows.

## Variation
- Adapt accessibility depth to product type: consumer products need full WCAG compliance, internal tools can have baseline compliance.
- Vary assistive tech assumptions: consumer apps must support screen readers, admin panels may prioritize keyboard navigation.
- For mobile products, expand on touch target sizing and gesture accessibility.
- For data products, expand on data visualization accessibility and screen reader optimization.
- Adjust validation rigor based on audience—public products need formal audit, internal products can use lighter validation.

## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Anti-patterns
- NEVER skip keyboard navigation—inaccessible products exclude users permanently.
- DO NOT omit screen reader semantics—unlabeled interactive elements are unusable for assistive tech.
- Avoid relying on color alone—colorblind users and screen readers can't perceive color-only cues.
- DO NOT forget error and loading states—dynamic content changes without announcements confuse assistive tech users.

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
