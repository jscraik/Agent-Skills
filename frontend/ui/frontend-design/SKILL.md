---
name: frontend-design
description: Analyze broad frontend design requests and route them to the correct local UI skill after classifying intent and maturity. Use when the user asks for frontend design generally and the specific design owner is not yet clear.
metadata:
  skill-type: scaffolding_templates
---

# Frontend Design

Install a broad, deconflicted frontend design entrypoint that preserves the upstream compound-engineering `frontend-design` doctrine while routing to stronger local skills where they already exist.

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [Design-system integration](#design-system-integration)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Discovery interview](#discovery-interview)
- [Deliverables](#deliverables)
- [Design Context Handshake](#design-context-handshake)
- [Philosophy](#philosophy)
- [Variation](#variation)
- [Workflow](#workflow)
- [Routing map](#routing-map)
- [Routing matrix contract](#routing-matrix-contract)
- [Overlap matrix](#overlap-matrix)
- [Upstream preservation](#upstream-preservation)
- [Anti-patterns](#anti-patterns)
- [Validation](#validation)
- [Constraints](#constraints)
- [Examples](#examples)
- [Failure mode](#failure-mode)
- [Gotchas](#gotchas)

## Standards snapshot
- Treat React 19 as the baseline interaction model and Next.js 16 as the default full-stack React baseline when the target app uses Next.js.
- Treat Tailwind CSS v4 and semantic token usage as the default styling posture unless the host repo explicitly says otherwise.
- Hold design direction and routing recommendations to WCAG 2.2 AA outcomes, including visible focus, keyboard coverage, and readable contrast.
- Route token architecture and brand-system governance decisions through the canonical `design-system` skill rather than duplicating doctrine in this wrapper.

## Design-system integration
- Apply `frontend/ui/references/design-system-integration-contract.md` as the shared typography, spacing, iconography, and token-alignment contract.
- Keep this wrapper responsible for routing and scope classification; keep system-level visual governance in `design-system`.
- Use `frontend/ui/references/skill-routing-matrix-2026.md` as the authoritative tie-break contract when overlap exists.

## When to use
- Use when the user asks broadly for "frontend design" and the right local frontend skill is not yet obvious.
- Use when the first job is to classify the request as existing-system extension, partial-system extension, or greenfield before deciding who should own implementation guidance.
- Use for ambiguous landing pages, dashboards, app screens, admin surfaces, and design-led component work that need a coherent design plan before implementation and before a narrower skill can be chosen confidently.
- Use when you need the upstream compound-engineering `frontend-design` workflow, but adapted to this repository's richer local frontend skill graph.
- Use when context detection matters: existing design system versus partial system versus greenfield.

## When not to use
- Do not use when the request already names or clearly implies the correct narrower skill.
- Do not use for backend-only work with no UI surface.
- Do not use for token-layer or design-system changes as the primary task. Use [`design-system`](/frontend/ui/design-system/SKILL.md).
- Do not use for motion-only or polish-only refinement after the visual direction is already set. Use [`ui-ux-creative-coding`](/frontend/ui/ui-ux-creative-coding/SKILL.md).
- Do not use for straightforward production UI planning or implementation when the request is already clearly standard product UI. Use [`frontend-ui-design`](/frontend/ui/frontend-ui-design/SKILL.md).
- Do not use when the user already wants an accessible screen flow, a concrete component plan, or a visually led surface with production-ready structure. Use [`frontend-ui-design`](/frontend/ui/frontend-ui-design/SKILL.md).

## Required inputs
- Target UI surface and stack.
- Whether the work is in an existing codebase or greenfield.
- User goal, primary audience, and the critical path the interface must support.
- Any design-system, branding, accessibility, or performance constraints already known.

## Discovery interview
- Use discovery only when routing context is underspecified and the missing details block a safe handoff.
- Ask one round at a time and wait for the current answer before moving to the next round.
- Start each round with one plain-language question, then add one short `Why this matters:` line.
- Avoid dumping the whole interview plan at once; keep the turn focused on the current round only.
- Skip rounds already answered in thread context, and stop once confidence is high enough to route correctly.
- Reuse `references/discovery-interview.md` for round templates and payload examples.

## Deliverables
- Mode decision: existing-system extension, partial-system extension, or greenfield.
- Ownership decision: stay in `frontend-design` only long enough to choose the right downstream skill and planning frame.
- Boundary decision: make exactly one routing-owner call before implementation (`frontend-ui-design`, `design-system`, or `ui-ux-creative-coding`).
- One visual thesis, one content plan, and one interaction plan before implementation begins.
- Explicit routing to the narrower local skill when the task is better served by `frontend-ui-design`, `ui-ux-creative-coding`, or `design-system`.
- Visual verification notes and screenshot-first review expectation before calling the work done.
- Preserved upstream doctrine in references so none of the imported guidance is lost.
- Output contract note: when returning a structured plan, include `schema_version: 1.0` in the response payload.

## Design Context Handshake
- Before routing deeper, confirm the minimum design context exists:
  - target audience,
  - primary use case or job to be done,
  - brand personality or intended feel.
- Do not pretend codebase inspection alone can answer those three questions. Existing code can show what is there; it cannot fully reveal who the product is for or how it should feel.
- Gather context in this order:
  1. explicit user instructions already present in the thread,
  2. project docs or repo guidance that clearly define audience or tone,
  3. narrow follow-up questions only for what remains unclear.
- Ask only for missing context. Do not run a broad design interview if the essentials are already known.
- If repeated design work is likely and the user wants it, recommend persisting a compact `Design Context` section in the project's normal instruction or documentation path rather than inventing a parallel canonical surface.

## Philosophy
- Route with intent, not habit.
- Prefer the narrowest owner that can execute safely and clearly.
- Keep ambiguity-handling lightweight so routing accelerates work instead of delaying it.
- Use a clear routing framework: classify context, identify the smallest boundary, then hand off decisively.
- Make tradeoff calls explicit so we understand why one owner skill wins over another.
- Enable a confident handoff so teams feel capable, empowered, and clear on next action.
- Ask: "What decision is actually missing before implementation can proceed?"
- Ask: "Which owner can deliver this outcome with the least cross-skill thrash?"

## Variation
- Vary discovery depth by context:
  - existing-system updates: keep routing narrow and focused on compatibility;
  - partial-system surfaces: adapt recommendations around current tokens and component constraints;
  - greenfield work: allow different visual directions before choosing the implementation owner.
- Use context-specific wording so routing feels customized to the user request, not repetitive template output.
- Avoid cookie-cutter handoffs; converge on one owner only after the key ambiguity is resolved.

## Workflow
1. Detect context first.
   - Look for design tokens, CSS variables, typography, component libraries, motion libraries, spacing scales, and existing composition patterns.
   - Classify the surface as existing-system, partial-system, or greenfield.
2. Run the design context handshake.
   - Confirm audience, use case, and intended feel from instructions, repo docs, or targeted user answers.
   - If one of those is still unclear and it materially affects the design direction, stop and ask only the missing question before routing deeper.
3. Decide whether this skill should continue to own the request.
   - If the request is already standard product UI with clear deliverables, route immediately to `frontend-ui-design`.
   - If the main job is token, theme, alias, or design-system structure, route immediately to `design-system`.
   - If the visual direction is already chosen and the request is mainly about motion, rhythm, or polish, route immediately to `ui-ux-creative-coding`.
4. Write the pre-build plan.
   - Visual thesis: one sentence covering mood, material, and energy.
   - Content plan: the main information order for the page, screen, or component.
   - Interaction plan: 2-3 motions or interaction beats that materially shape the feel.
5. Route to the right implementation skill.
   - Standard product UI or redesign work: `frontend-ui-design`.
   - Motion, rhythm, and polish after direction is set: `ui-ux-creative-coding`.
   - Token architecture or design-system work: `design-system`.
6. Verify visually before completion.
   - Prefer existing browser tooling, then browser MCPs, then agent-browser, then explicit mental-review fallback.
   - Fix only glaring issues in the first verification pass unless the user asks for iteration.

## Routing map
- `frontend-design` is the umbrella and compatibility entrypoint.
- Treat it as a front door, not a long-term owner, unless the ambiguity itself is the core job.
- Use [`frontend-ui-design`](/frontend/ui/frontend-ui-design/SKILL.md) when the work is standard product UI, accessible component planning, or a visually led surface that still needs production-ready structure.
- Use [`ui-ux-creative-coding`](/frontend/ui/ui-ux-creative-coding/SKILL.md) when the visual thesis already exists and the main task is motion, interaction rhythm, or refinement.
- Use [`design-system`](/frontend/ui/design-system/SKILL.md) when tokens, aliases, mapped variables, or theme structure are the center of gravity.
- If the user already asks for one of the narrower skills by name or unmistakable scope, skip this wrapper and use the narrower skill directly.
- Read [`references/upstream-frontend-design.md`](/frontend/ui/frontend-design/references/upstream-frontend-design.md) when you need the full imported compound-engineering design doctrine, module breakdown, and litmus checks.

## Routing matrix contract
- Use [`frontend/ui/references/skill-routing-matrix-2026.md`](/frontend/ui/references/skill-routing-matrix-2026.md) before changing trigger wording or overlap examples.
- Apply the matrix tie-breaker rules exactly:
  - narrow owner beats broad owner;
  - explicit implementation verbs route to `frontend-ui-design`;
  - token-governance scope routes to `design-system`;
  - motion-only refinement routes to `ui-ux-creative-coding`.

## Overlap matrix
- Read [`references/overlap-matrix.md`](/frontend/ui/frontend-design/references/overlap-matrix.md) before widening this skill's trigger wording.
- The matrix documents the boundary between this wrapper and `frontend-ui-design`, `ui-ux-creative-coding`, and `design-system`, with examples of when to route immediately instead of triggering this umbrella.

## Upstream preservation
- This skill intentionally does not flatten the upstream CE `frontend-design` skill into a weaker summary.
- The full upstream guidance is preserved in [`references/upstream-frontend-design.md`](/frontend/ui/frontend-design/references/upstream-frontend-design.md).
- The local wrapper changes only two things:
  - deconflict broad triggering against stronger local frontend skills;
  - route broad asks into the local frontend skill graph instead of duplicating overlapping procedures.

## Anti-patterns
- NEVER keep this wrapper in control after a narrower owner is clearly identified.
- DO NOT treat routing as a full redesign brief when the user asked for concrete implementation.
- DO NOT discard an existing design system and force a fresh visual language by default.
- NEVER run a broad six-question interview when one missing context detail would unblock routing.
- DO NOT route design-system governance questions to implementation-focused UI skills.
- NEVER allow repetitive routing loops that bounce between skills without a handoff decision.
- DO NOT keep this wrapper as the long-term owner once the correct downstream skill is known.
- DO NOT convert every ambiguous ask into a long discovery thread when one focused question is enough.
- WARNING SIGN: If you cannot name the downstream owner in one sentence, routing has drifted and must be reset.
- WRONG BEHAVIOR: continuing classification output after the user requested direct implementation in a clearly scoped owner skill.

## Validation
- Confirm the skill first decides whether this is existing-system, partial-system, or greenfield work.
- Confirm the skill establishes audience, use case, and intended feel before routing into deeper design work.
- Confirm the skill does not stay in control once a narrower local owner is obvious.
- Confirm a visual thesis, content plan, and interaction plan exist before implementation recommendations begin.
- Confirm the narrower local skill is named explicitly when routing is appropriate.
- Confirm visual verification is part of the completion contract.
- Confirm trigger coverage in [`references/evals.yaml`](/frontend/ui/frontend-design/references/evals.yaml) still distinguishes this wrapper from nearby skills.
- Confirm [`references/overlap-matrix.md`](/frontend/ui/frontend-design/references/overlap-matrix.md) still matches the nearby skill descriptions after any local-skill updates.
- Confirm routing and recommendations remain compliant with `frontend/ui/references/design-system-integration-contract.md`.
- Confirm `frontend/ui/references/skill-routing-matrix-2026.md` still matches this skill's trigger language and handoff rules.
- Keep scope tight: start with one decisive route choice before expanding into broader planning.
- Fail fast: stop at the first failed gate and do not proceed to implementation recommendations until that gate is resolved.

## Constraints
- Respect existing design systems and explicit user instructions over skill defaults.
- This wrapper is routing-only; do not execute implementation steps once a narrower owner is identified.
- Do not introduce a competing design language into an established application unless the user explicitly asks for a redesign.
- Keep the wrapper install additive and deconflicted; do not weaken or duplicate existing frontend skills.
- Do not claim visual completion without a verification pass or an explicit note that verification was blocked.
- Redact secrets, tokens, API keys, credentials, and PII in examples, logs, and screenshots by default.

## Examples
- User says: "Design the frontend for this new SaaS landing page and decide whether this should route to a full UI build or a design-system extension."
- User says: "Our B2B analytics dashboard feels generic. Can you inspect the current surface, set direction first, then route to the best owner before implementation?"
- User says: "Can you improve this existing React billing screen while preserving our current token system and brand voice, then validate owner scope before implementation?"
- User says: "We need better frontend quality this sprint. Decide whether this is redesign scope or polish scope first."

## Failure mode
- If the request is actually design-system work, motion-only polish, or straightforward production UI implementation, stop routing through this umbrella skill and hand off to the narrower local skill instead.
- If the request is already concrete enough to name the downstream owner immediately, skip the wrapper and route without adding an extra planning layer.
- If the codebase context is ambiguous and the mode cannot be inferred safely, ask whether to follow the existing patterns or pursue a more distinctive visual direction.

## Gotchas
- Broad frontend design requests can false-positive into overlapping skills. Recheck `references/evals.yaml` before widening the description.
- If a request says "frontend design" but also asks for explicit states, accessibility behavior, component structure, or token changes, that narrower scope wins.
- Preserve the upstream doctrine in references when refining this wrapper. Do not compress away useful modules, litmus checks, or verification guidance.

## See Also

| Skill | When to use together |
|---|---|
| [[frontend-ui-design]] | Hand off once the request clearly becomes standard UI build or redesign work |
| [[design-system]] | Route token, alias, or system-governance work to the dedicated owner |
| [[ui-ux-creative-coding]] | Route post-direction polish and motion refinement to the narrower owner |

**Topic map:** [[frontend-ui]]
