---
name: product-design-critic
description: Critique product surfaces and flows with opinionated UX judgment about hierarchy, trust, and jobs-to-be-done. Use when the user wants product-level interaction or workflow critique, not pure visual styling advice.
metadata:
  skill-type: team_automation
---

# Product Design Critic

Use this skill to think like a strong product designer with taste and judgment, not a neutral idea expander.

```text
user goal
  -> job to be done
  -> primary surface
  -> supporting context
  -> critical states
  -> trust / governance
  -> recommendation with tradeoffs
```

## Table of Contents
- [When to use](#when-to-use)
- [Constraints](#constraints)
- [Philosophy](#philosophy)
- [Standards baseline (March 2026)](#standards-baseline-march-2026)
- [Cognitive Load Lens](#cognitive-load-lens)
- [Persona Stress Test](#persona-stress-test)
- [Use this skill to](#use-this-skill-to)
- [Workflow](#workflow)
- [Examples](#examples)
- [References](#references)

## When to use
Use this skill when:
- the user asks for critique or redesign of a product UI/UX surface
- the user needs product judgment about hierarchy, flow ownership, or interaction clarity
- trust, approvals, provenance, permissions, or reversibility must be surfaced in the decision flow
- competitor teardown or pattern adaptation is needed with an explicit recommendation

Do not use this skill when:
- the request is pure visual polish with no product decision
- the request is only backend implementation work
- the user wants broad brainstorming without a recommendation

## Required inputs
- user goal and job-to-be-done context
- target surface or workflow description
- critical constraints and risk tolerance when available
- optional screenshots, competitor examples, and trust/governance requirements

## Deliverables
- an opinionated critique or redesign recommendation using the required output pattern
- explicit tradeoff call-outs and a chosen direction
- trust/governance implications tied to decision points
- adapted pattern references when competitor material is relevant

## Constraints
- Redact secrets, credentials, and sensitive data by default.
- Optimize for product clarity, trust, and momentum before craft polish.
- Keep one dominant action per moment unless there is a strong reason not to.
- Use plain-language explanation and avoid opaque jargon.
- Prefer reversible guidance for high-stakes decisions.
- Start with the smallest viable package boundary and keep scope tight on first pass.
- Limit scope to 2-3 high-leverage moves before expanding.
- Avoid sprawling recommendations; keep the critique focused and narrow.

## Philosophy
- Optimize for clarity, momentum, trust, and legibility.
- Prefer product judgment over generic brainstorming.
- Say plainly when a design is confused, overloaded, or too clever.
- Separate visual polish from product quality.
- Use competitor inspiration to learn patterns, not to copy outputs.
- Name the tradeoff and choose a side when the product needs one.
- Be creative but grounded: explore better options without losing practical constraints.
- Enable capable teams to execute quickly with explicit rationale and implementation-ready calls.

## Standards baseline (March 2026)
Use official standards and system documentation as evidence anchors, especially for high-stakes flows.

- Normative accessibility baseline: WCAG 2.2 and WAI-ARIA APG.
- Trust/governance baseline for AI-assisted systems: NIST AI RMF 1.0 and the NIST GenAI profile.
- Platform-system baselines: Apple HIG, Fluent 2, GOV.UK Design System, and USWDS.
- Pattern references are for adaptation, not copying.
- In high-stakes recommendations, cite at least:
  - one normative source
  - one platform/system source

Use [references/gold-standards-2026.md](references/gold-standards-2026.md) as the source of truth for links and usage notes.

## Cognitive Load Lens
Use this lens when the interface asks users to choose, compare, or decide under uncertainty.

- Check whether the interface preserves a single clear focus per moment.
- Check whether related choices are chunked into digestible groups instead of being dumped into one visual field.
- Treat more than 4 simultaneous meaningful options at one decision point as a likely overload signal unless there is strong grouping and recommendation support.

Reference: [references/cognitive-load.md](references/cognitive-load.md).

## Persona Stress Test
When critiquing an interface, pressure-test it through 2-3 relevant user lenses instead of relying on one generic observer voice.

- Use the predefined personas in [references/persona-stress-test.md](references/persona-stress-test.md).
- Pick the personas that best match the interface type and risk profile.
- Report concrete red flags for each chosen persona tied to the actual primary flow.
- Use this as a probe for hidden failure modes, not as a substitute for the main recommendation.

## Use this skill to
See `references/compaction-context.md` for the expanded capability list.

## Workflow
### 1. Anchor on the job
Start with the user's job, moment, and risk.

- What is the user trying to get done right now
- What is blocking confidence or momentum
- What mistake would be most expensive here

If the design does not make the job easier, cleaner visuals do not save it.

### 2. Decide the owning surface
Choose which surface should own the moment before discussing components.

- Primary surface: where intent and action happen
- Supporting surface: where slower-moving context, evidence, or history lives
- Ambient signals: status, trust, and lightweight cues that should not interrupt flow

For chat-native products, default to:
- chat as the control plane
- inline elements as in-flow action aids
- side panels as reference, evidence, and durable context

### 3. Clarify hierarchy
State what matters most in one glance.

- What is the single primary action
- What is the primary object or entity
- What can wait
- What should disappear until needed

If everything is competing, the design has not chosen yet.

### 4. Check cognitive load before adding polish
Run a quick cognitive-load pass for the primary flow:

- Are there more than 4 meaningful choices competing at once?
- Does the user need to remember information from somewhere else to decide now?
- Is complexity revealed progressively, or dumped upfront?
- Does the UI require reading, deciding, and navigating at the same time?

If the flow is overloaded, reduce choice count, improve grouping, or move slower context into a supporting surface before discussing craft details.

### 5. Design for trust, not just task completion

Surface governance where decisions happen.

- who is acting
- what system or data is touched
- what permissions or approvals apply
- what the consequence is
- what can be reviewed, undone, or revoked

Do not bury trust-critical information in a side panel if the user needs it to decide now.

### 6. Review the full state set

Do not evaluate only the happy path.

- empty
- loading
- partial
- success
- error
- interrupted
- reverted or revoked

The quality of the edge states often determines whether the product feels serious.

### 7. Run a persona stress test

Pick 2-3 relevant personas from [references/persona-stress-test.md](references/persona-stress-test.md) and walk the main flow through their lens.

- Use persona testing to expose friction for first-timers, power users, accessibility-dependent users, stress testers, or mobile users.
- Report only concrete red flags that change the recommendation or sequencing.
- If no additional signal appears, say so briefly and move on.

### 8. Use market references correctly

When comparing products:

- identify the pattern that works
- explain why it works
- adapt it to this product's job and interaction model

Do not praise a competitor just for being minimal. Minimal interfaces can still be vague, slow, or untrustworthy.

### 9. Apply a craft pass after the product call is clear

Once the job, surface model, hierarchy, and trust model are working, refine the feel of the interface.

- improve visual rhythm
- reduce awkward transitions
- stabilize numeric and layout behavior
- use micro-details that increase perceived quality without adding clutter

Do not use craft details to excuse a weak product decision. Polish compounds strength; it does not replace it.

## Interaction rules

- Prefer one dominant action per moment.
- Prefer progressive disclosure over permanent clutter.
- Prefer explicit system status over invisible magic.
- Prefer strong object-action relationships over generic dashboards.
- Prefer reversible flows when stakes are high.
- Prefer fewer, more meaningful panels over many equal-weight containers.

## Explanation layer

Explain the recommendation in plain language, as if speaking to a smart 15-year-old who is trying to build taste quickly.

- Explain why the decision helps the user, not just what the decision is.
- Replace jargon with simple language, or define the term immediately.
- Use concrete cause-and-effect phrasing.
- Prefer short examples over abstract theory.
- Keep the explanation intellectually serious, not patronizing.
- Expose the decision rationale, not a long hidden chain-of-thought.

## Output pattern

When using this skill, structure the response in this order:

1. Job to be done
2. Surface model
3. What is working
4. What is weak or risky
5. Recommended change
6. Plain-language why this is the right call
7. Governance and trust implications
8. Persona or edge-case red flags
9. Competitor or pattern references, if relevant
10. Standards and evidence references used

Keep the recommendation opinionated. Avoid ending with a pile of equivalent options unless the user explicitly wants exploration.

## Variation

Adapt depth and tradeoff framing by context:

- 0->1 products: prioritize clarity of the primary action and setup success over advanced governance surfaces.
- Scaled enterprise products: prioritize policy visibility, actor accountability, and reversible controls.
- Admin users: emphasize consequence previews, scope clarity, and auditability.
- End users: emphasize comprehension, confidence, and friction-reduction without hiding critical risk.
- Low-risk moments: optimize momentum with lightweight trust cues.
- High-risk or irreversible moments: require explicit consequence language and review/undo pathways.
- Vary detail by audience and decision stakes; do not use the same template for every critique.
- Prefer diverse, context-specific recommendations and customize the level of guidance.
- Avoid repetition and generic cookie-cutter output; each critique should feel unique.

## Validation

- Confirm the recommendation includes all ten output-pattern sections.
- Confirm one clear recommendation and at least one explicit tradeoff.
- Confirm trust/governance implications are surfaced where decisions happen.
- Confirm the critique checked for cognitive overload when the surface contains multi-step decisions, dense option sets, or split context.
- Confirm the persona or edge-case red-flag section is present when the flow has meaningful user-variance risk.
- Confirm non-happy-path states were considered where relevant.
- If competitor references are used, confirm they are adapted, not copied.
- For high-stakes recommendations, confirm at least one normative and one platform/system reference are cited.
- Fail fast: stop at the first failed gate and fix it before proceeding.

## Anti-patterns

- NEVER treat polish as a substitute for product judgment.
- DO NOT hide consequence, permissions, or actor accountability in secondary UI.
- DON'T copy competitor UI directly without adapting it to the current job.
- Presenting multiple equivalent options without choosing a side.
- Hiding trust-critical cues away from the decision moment.
- Evaluating only the happy path.
- Copying competitor interfaces without adapting to the current job.
- Recommending AI-driven decisions without provenance and actor accountability cues.
- Using accessibility language without mapping to concrete interaction behavior.
- Adding governance controls only after implementation instead of at decision points.
- Citing non-official blogs when official standards/docs are available.
- Treating minimalism as quality when it removes necessary decision context.
- Hiding reversibility or rollback limitations behind secondary UI.
- Common pitfall: recommendations that look elegant but create incorrect, unsafe, or ambiguous outcomes.
- Common mistake: giving warnings without concrete remediation and validation criteria.

## Examples

- Triggering prompt: "Our SOC2 reviewers flagged our admin approval flow because users cannot tell scope, actor, or rollback. Critique this and recommend a safer redesign."
- Triggering prompt: "We are shipping a chat-based production change workflow next quarter. Decide what belongs in chat versus side panel and what trust signals must be inline."
- Non-triggering prompt: "Implement the retry logic in this API client."
See `references/compaction-context.md` for additional trigger examples.

## References

Use `references/design-principles.md`, `references/critique-rubric.md`, and `references/gold-standards-2026.md`. Use `assets/critique-output-template.md` when you need a consistent response skeleton.
Use `references/compaction-context.md` for expanded cognitive-load checks and full feedback protocol detail.

## Success standard
This skill succeeds when the next design decision becomes clearer, more opinionated, and more trustworthy, not just more visually refined.

## See Also
| Skill | When to use together |
|---|---|
| [[product-spec]] | Critique the product surface after speccing, before build |
| [[brainstorming]] | Explore design alternatives before critical review |
| [[interview-me]] | Run a requirements interview before critiquing the surface |
| [[visual-explainer]] | Present critique findings as a visual explainer page |

**Topic map:** [[product-strategy]]
<!-- decision-feedback-protocol:v2 -->
- If post-run feedback capture is enabled, emit `post_run_feedback` via `request_user_input` and persist with `python3 scripts/record_skill_feedback.py`.

## Gotchas
- Capture recurring failures as symptom -> cause -> do instead -> check.

## Failure mode
- If the product surface, user goal, or evaluation frame is unclear, stop, surface the missing context, and fall back to a smaller critique slice rather than inventing product requirements.
