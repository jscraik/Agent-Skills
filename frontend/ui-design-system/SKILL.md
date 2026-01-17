---
name: ui-design-system
description: Create or update governed UI design systems across SwiftUI and React stacks. Not for app-specific UI implementation or visual regression; use frontend-ui-design or ui-visual-regression.
metadata:
  short-description: UI design system governance and architecture
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

## Stack-specific variants

### claude variant
Frontmatter:

```yaml
---
name: ui-design-system
description: Create or update a governed UI design system for Swift/SwiftUI, React/Vite/Tailwind/Storybook/Radix, and embedded Apps SDK widgets. Use when the user asks for design system governance, tokens, components, patterns, or LLM/AI UX standards across platforms.
metadata:
  short-description: UI design system governance and architecture
---
```
Body:

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
