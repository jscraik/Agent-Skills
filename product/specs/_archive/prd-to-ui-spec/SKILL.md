---
name: prd-to-ui-spec
description: Generate UI specifications from PRDs or UX specs using the aStudio design
  system. Use when a UI spec is needed before build or mockups.
knowledge_graph_profile: references/task-profile.json
---

# PRD/UX to UI Spec (Quick Start)

## Response format (strict)
The first line of any response MUST be `## Inputs`.

## Cognitive Support / Plain-Language
- Optimize for low cognitive load (TBI support): one task at a time, explicit steps.
- Use plain language first; define jargon in parentheses.
- Keep steps short and checklist-driven where possible.
- Externalize state: decisions, assumptions, and the next step.
- Provide ELI5 explanations for non-trivial logic.
- Ask one question at a time; prefer multiple-choice when possible.

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

## Scope and triggers
- Use this skill when a PRD/UX spec needs a concrete UI spec grounded in aStudio.
- If the request is outside scope, route to `product-spec`.

## Required inputs
- User request details and any relevant files/links.

## Deliverables
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
- Avoid generic patterns; tailor UI spec depth to platform (web, touch-first, desktop) and input model.
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

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when consistent decision-making matters more than one-off execution because project context should drive the approach.
- Principle and mindset: prioritize tradeoffs and constraints over rigid checklists; understand why each step exists.
- Ask this to keep outcomes robust: Why is this the right default, and what could change this outcome?
- How do we adapt if constraints shift?
- What evidence is needed before choosing one path over another?

## Anti-patterns and caveats
- Avoid applying this playbook generically without checking repository-specific context.
- **NEVER** skip required validation gates when behavior changes.
- **DO NOT** use this skill as a rigid replacement for engineering judgment.
- **DON'T** ignore warnings or assume one pattern fits all repos.
- Common pitfall: treating anti-patterns as optional.
- Incorrect assumptions here can lead to fragile guidance.
- Warning: wrong sequencing can create avoidable regressions.

## Variation and adaptation
- Vary the workflow by team size, risk, and deployment target.
- Use different strategies for small, medium, and large changes.
- Adapt recommendations to the specific environment and avoid repetitive templates.
- Avoid generic or cookie-cutter responses; craft context-specific alternatives.
- Keep outputs diverse and not repetitive.
- Converge on a custom path only after evidence review.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of exploring multiple options and enabling the team to make safe decisions.
- Unlock confidence by explaining options and tradeoffs clearly.
- Feel free to be creative while staying rigorous and precise.
- Push boundaries with practical alternatives when simple recipes fail.
- Enable outcomes-oriented problem solving.

<!-- decision-feedback-protocol:v1 -->
**Decision feedback protocol (required):**
- For non-trivial outcomes, collect user feedback via AskQuestion parity (`request_user_input`) before closing the run.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- If available, persist with `ops/scripts/graph/record-feedback.sh`; otherwise append a JSONL record to `ops/metrics/skill-feedback/decision-feedback.jsonl` in the active workspace.
<!-- /decision-feedback-protocol -->
