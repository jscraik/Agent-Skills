---
name: ui-spec-to-prompts
description: "Translate a UI spec into build-order prompts for UI generator tools (v0, Bolt, Claude). Use when a UI spec already exists and you need sequenced, self-contained prompts."
metadata:
  short-description: "UI spec -> build-order prompts."
---

# UI Spec to Build-Order Prompts

## Response format (strict)
The first line of any response MUST be `## Inputs`.
Every response must include:
- `## Inputs`
- `## Outputs`
- `## When to use`

## Pipeline Context
This skill is used after a UI spec exists (for example from `prd-to-ui-spec`) and before UI generation or implementation.
Avoid generating prompts without a UI spec; route upstream first.

## When to use
- You have a UI spec with tokens, components, and state definitions.
- You need sequential prompts for tools like v0, Bolt, or Claude UI generation.
- You want build order by dependencies (foundations -> components -> screens -> polish).

## Inputs
- UI spec file path.
- Target UI tool (v0, Bolt, Claude, Figma AI, or other).
- Target platform (web, touch-first, desktop).
- aStudio repo path (default: `/Users/jamiecraik/dev/aStudio`).
- Output location preference (default: same directory as UI spec).

## Outputs
- A build-order prompts document saved next to the UI spec.
  - Naming: `{ui-spec-basename}-ui-prompts.md` (or `UI-prompts.md` if spec is generic).
- Include `schema_version: 1` if outputs are contract-bound.

## Principles
- Tokens are the source of truth; never invent colors, spacing, or typography.
- Each prompt must be self-contained and buildable in isolation.
- Build order follows dependencies; do not skip foundations.
- Accessibility and hit-area rules are non-optional.
- State machines in the UI spec must map to prompt states and transitions.

## Philosophy
- Why: UI generation fails when context is fragmented; self-contained prompts prevent rework.
- Mental model: tokens express brand intent, components express behavior, prompts express build order.
- Framework: context + requirements + states + constraints + validation = buildable prompt.
- Principle: document the "why" behind UI choices to preserve intent across tools.

## Variation
- Vary prompt granularity based on complexity and tool limits.
- Adapt output structure to platform (web vs touch-first vs desktop).
- Avoid generic patterns; tailor prompts to domain-specific workflows.

## Build Order Strategy
1) Foundation tokens and typography scale.
2) Component library (atomic -> composite).
3) Layout shell and grid behavior.
4) Screens/views and content structure.
5) Interactions, states, and feedback.
6) Polish (motion, density modes, a11y checks).

## Prompt Template (required)
```markdown
## [Feature/Component Name]

### Context
[Where this appears, and how it fits the system]

### Requirements
- [Behavior and appearance requirements]
- [Token references for color/typography/spacing]

### Hit-Area Rules
- Mobile min target: 44x44px
- Desktop min target: 32x32px
- Min spacing between adjacent targets: 8px

### Responsive & Grid
- Breakpoint tokens and layout shifts (tokenized)
- Grid sizes: columns, gutters, margins (token-based)

### States (from UI spec)
- Default:
- Loading:
- Error:
- Success:
- Other:

### State Machine Summary
- States:
- Transitions (trigger -> state):

### Interactions
- Pointer/gesture:
- Keyboard:
- Focus behavior:

### Accessibility
- Contrast targets:
- Focus styles:
- Reduced motion:

### Constraints
- What NOT to implement in this prompt
```

## Procedure
1) Confirm the UI spec path, target tool, and platform.
2) Parse the UI spec for tokens, components, states, breakpoints, grid, and hit-area rules.
3) Identify atomic units and dependencies.
4) Sequence the build order and generate self-contained prompts.
5) Save the prompts file next to the UI spec.

## Validation
- Fail fast: stop at the first failed validation gate.
- Every token in the UI spec is referenced in at least one prompt.
- Every component has a prompt (or is explicitly out of scope).
- Hit-area rules, breakpoints, and grid sizes are included where relevant.
- States/feedback and state machine summaries are included.
- No prompt references another prompt.

## Anti-patterns
- Referencing other prompts ("as above") instead of repeating context.
- Using raw hex values or non-aStudio tokens.
- Skipping hit-area, breakpoints, or grid definitions.
- Omitting state machine coverage for interactive components.
- Generating prompts without confirming missing measurements.
- NEVER assume a tool remembers previous prompts.
- DO NOT ship prompts without explicit focus, contrast, and reduced-motion rules.
- ALWAYS include token names (no ad-hoc values).
- NEVER merge multiple unrelated features into one prompt.
- DO NOT hide missing inputs; surface gaps and request them.
- FORBIDDEN: "best effort" prompts that guess token values.
- Anti-pattern: "appropriate spacing" or "standard colors" with no token refs.
- Anti-pattern: describing visuals before listing states and interactions.
- Anti-pattern: assuming defaults instead of reading the UI spec.

## Constraints
- Redact secrets/PII by default.
- Keep `name` and `description` single-line YAML scalars (quote if needed).
- Do not add dependencies without explicit user approval.

## Examples
- "Convert this UI spec into build-order prompts for v0."
- "Generate UI prompts from this UI spec with aStudio tokens."

## Resources
- `references/contract.yaml`
- `references/evals.yaml`

## Remember
The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they do not constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.
