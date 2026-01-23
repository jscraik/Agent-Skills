---
name: ui-design-system
description: "Create or update a governed UI design system (tokens, components, governance). Use when establishing or revising a multi-platform design system."
---

# UI Design System

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

## Overview
Design a complete, multi-platform UI design system that covers governance, foundations, tokens, components, patterns, tooling, and LLM/AI UX.

## Philosophy
- The system is a contract: tokens and components must be governed, not ad-hoc.
- Accessibility and safety are defaults, not opt-ins.
- Patterns beat one-off components for user trust and consistency.

## Guiding Questions
- What products and surfaces are in scope (web, iOS, embedded widgets)?
- What brand constraints and accessibility targets apply?
- Which token standard and theming modes are required?
- What component and pattern gaps exist today?
- What QA/release gates must be enforced?

## Workflow
1) Scope and governance
- Define charter, principles, owners, contribution model, lifecycle, and release policy.

2) Foundations
- Brand, accessibility, layout, typography, motion, content rules.

3) Tokens and theming
- Decide token standard, layering, categories, themes, and platform outputs.

4) Components and patterns
- Define component taxonomy, documentation standard, and LLM UX patterns.

5) Tooling and QA
- Storybook/docs, visual regression, a11y checks, linting, and CI gates.

6) Distribution
- Package layout, versioning, deprecation, and migration plan.

## Output Format
- Context summary (1-3 bullets)
- System map: governance → foundations → tokens → components → patterns → tooling
- Required artifacts (docs, token files, packages, demos)
- Risks and open questions
- Next actions (short list)

## Variation Rules
- Adjust depth to match scope (single surface vs multi-platform).
- Prioritize embedded constraints when Apps SDK widgets are in scope.
- Avoid repeating the same component list; tailor to the product domain and AI flows.
- Vary outputs by audience (designers vs engineers) and maturity (MVP vs full system).

## Anti-Patterns to Avoid
- Treating the design system as just a component library.
- Hardcoding values instead of tokens.
- Ignoring AI/LLM UX patterns and safety states.
- Shipping without accessibility and visual regression gates.
- Defining tokens without a naming convention or deprecation plan.
- Building components before tokens and foundations are approved.

## Empowerment Principles
- Provide a “minimum viable system” path and a “gold standard” path.
- Offer tradeoffs when timelines or staffing are constrained.

## Trigger Examples
- Create a full design system for SwiftUI + React + Tailwind + embedded widgets.
- Define DTCG token architecture and package layout for our Apps SDK UI.
- Establish AI/LLM interaction patterns and QA gates for our UI system.

## References
- For detailed inventory, standards, and stack-specific guidance, open:
  `references/ui-design-system-reference.md`

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## When to use
- Use this skill when the task matches its description and triggers.
- If the request is outside scope, route to the referenced skill.


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


## Anti-patterns
- Avoid vague guidance without concrete steps.
- Do not invent results or commands.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.
