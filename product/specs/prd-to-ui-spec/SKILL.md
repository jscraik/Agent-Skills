---
name: prd-to-ui-spec
description: "Generate UI specifications from PRDs or UX specs using the aStudio design system. Use when a UI spec is needed before build or mockups."
metadata:
  short-description: "UI spec from PRD/UX using aStudio tokens."
---

# PRD/UX to UI Spec (Quick Start)

## Response format (strict)
The first line of any response MUST be `## Inputs`.
Every response must include:
- `## Inputs`
- `## Outputs`
- `## When to use`

## Inputs required
- Source file path: PRD or UX spec.
- Target output path (if not provided, infer).

## Output location
Write the UI spec in the same directory as the source file.
- `feature-x.md` -> `feature-x-ui-spec.md`
- `feature-x-ux-spec.md` -> `feature-x-ui-spec.md`
- `PRD.md` -> `UI-spec.md`

## Quick Start
1) Read the source PRD/UX spec and list required UI surfaces/components.
2) Use the aStudio token sources listed in `references/guide.md`.
3) Fill the UI spec using `references/ui-spec-template.md`.
4) Include state machine diagrams for each component.
5) Add `Evidence:` or `Evidence gap:` per section.

## Procedure
1) Follow Quick Start.
2) Apply the UI review gate in `references/guide.md`.
3) Use `references/examples.md` to calibrate output quality.

## References (required)
- `references/guide.md` — Gold UI standard, token source map, review gate
- `references/ui-spec-template.md` — UI spec template
- `references/examples.md` — Example UI spec

## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.

## When to use
- Use this skill when a PRD/UX spec needs a concrete UI spec grounded in aStudio.
- If the request is outside scope, route to `prd-to-ux` or `product-spec`.

## Inputs
- User request details and any relevant files/links.

## Outputs
- UI spec file with design-token references and state diagrams.
- Include `schema_version: 1` if outputs are contract-bound.

## Validation
- Fail fast: stop at the first failed validation gate.
- Follow the review gate in `references/guide.md`.

## Philosophy
- UI specs prevent design drift by forcing explicit token and component decisions.
- Visual consistency is a system outcome, not a per-screen choice.
- The UI spec is a contract: every visual choice must be explainable and testable.
- Principle: document the "why" behind visual decisions to preserve intent.
- Guiding principles: clarity, consistency, and measurable usability over subjective taste.
- Mental model: tokens express brand intent; components express behavior; states express reality.
- Framework: tokens + components + states + accessibility = shippable UI.

## Variation
- Adapt depth based on product complexity (simple flows vs multi-surface systems).
- Expand components/state detail when risk or ambiguity is high.
- Avoid generic patterns; tailor UI spec depth to platform (web, mobile, desktop) and input model.
- If brand constraints are strong, bias toward stricter token usage; if exploratory, add explicit experiments + rollback notes.

## Empowerment
- You are empowered to push back on vague UI direction and demand token-level clarity.

## Anti-patterns
- Inventing tokens or styling not present in aStudio.
- Shipping visuals without state machine diagrams per component.
- Vague specs like "use nice spacing" or "standard colors."
- Ignoring token source map or mixing non-aStudio tokens.
- Omitting motion or state definitions for interactive components.
- NEVER skip the UI review gate.
- DO NOT introduce ad-hoc sizes or colors outside aStudio.
- NEVER omit hit-area rules, breakpoint tokens, or grid sizes.
- DO NOT ship UI specs without explicit focus, contrast, and reduced-motion rules.

## Examples (triggers)
- "Create a UI spec from this UX spec using aStudio tokens."
- "Translate this PRD into a UI spec aligned with aStudio."
- "I have a UX spec; produce a UI spec for v0 with aStudio tokens."
- "Generate a UI spec and component state diagrams from this feature doc."

## Remember
The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.
