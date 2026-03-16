---
name: product-design-critic
description: Use this skill when the user asks to critique or shape a software product surface, workflow, card, panel, or chat UX. It analyzes and reviews product decisions with opinionated recommendations grounded in jobs-to-be-done, hierarchy, trust/governance cues, and explicit tradeoffs beyond visual polish.
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
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Constraints](#constraints)
- [Philosophy](#philosophy)
- [Standards baseline (March 2026)](#standards-baseline-march-2026)
- [Use this skill to](#use-this-skill-to)
- [Workflow](#workflow)
- [Interaction rules](#interaction-rules)
- [Explanation layer](#explanation-layer)
- [Output pattern](#output-pattern)
- [Variation](#variation)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [References](#references)
- [Success standard](#success-standard)
- [Decision feedback protocol](#decision-feedback-protocol)

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

## Inputs

- user goal and job-to-be-done context
- target surface or workflow description
- critical constraints and risk tolerance when available
- optional screenshots, competitor examples, and trust/governance requirements

## Outputs

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

## Use this skill to

- Critique a UI or workflow.
- Design a new product surface, card, side panel, or chat experience.
- Decide what belongs inline versus in a secondary surface.
- Translate product intent into hierarchy and interaction design.
- Pressure-test governance, approvals, provenance, and trust cues.
- Map jobs-to-be-done and turn them into concrete interface behavior.
- Tear down competitor products with an eye for reusable design moves.

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

### 4. Design for trust, not just task completion

Surface governance where decisions happen.

- who is acting
- what system or data is touched
- what permissions or approvals apply
- what the consequence is
- what can be reviewed, undone, or revoked

Do not bury trust-critical information in a side panel if the user needs it to decide now.

### 5. Review the full state set

Do not evaluate only the happy path.

- empty
- loading
- partial
- success
- error
- interrupted
- reverted or revoked

The quality of the edge states often determines whether the product feels serious.

### 6. Use market references correctly

When comparing products:

- identify the pattern that works
- explain why it works
- adapt it to this product's job and interaction model

Do not praise a competitor just for being minimal. Minimal interfaces can still be vague, slow, or untrustworthy.

### 7. Apply a craft pass after the product call is clear

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
8. Competitor or pattern references, if relevant
9. Standards and evidence references used

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

- Confirm the recommendation includes all nine output-pattern sections.
- Confirm one clear recommendation and at least one explicit tradeoff.
- Confirm trust/governance implications are surfaced where decisions happen.
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
- Triggering prompt: "Use official standards, not opinion alone. Evaluate this healthcare consent UI and explain tradeoffs with references."
- Triggering prompt: "Can you inspect this permission-change flow and help me validate it against official standards before we build the final version?"
- Triggering prompt: "When the user asks for a competitor teardown, user says they need a recommendation we can migrate into our product this sprint."
- Non-triggering prompt: "Implement the retry logic in this API client."

## References

- Read [references/design-principles.md](references/design-principles.md) when you need reusable design canons, mental models, and anti-patterns.
- Read [references/critique-rubric.md](references/critique-rubric.md) when you need a sharper review checklist, teardown structure, or scoring lens.
- Read [references/interface-polish.md](references/interface-polish.md) when you want a final-pass craft checklist for details that make strong interfaces feel more refined.
- Read [references/gold-standards-2026.md](references/gold-standards-2026.md) for official standards and design-system references current as of March 2026.
- Use [assets/critique-output-template.md](assets/critique-output-template.md) when a stable response skeleton helps maintain quality and speed.

## Success standard

This skill succeeds when the next design decision becomes clearer, more opinionated, and more trustworthy, not just more visually refined.

## Decision feedback protocol

## See Also

| Skill | When to use together |
|---|---|
| [[product-spec]] | Critique the product surface after speccing, before build |
| [[brainstorming]] | Explore design alternatives before critical review |
| [[frontend-ui-design]] | Apply critique findings to UI component implementation |
| [[interview-me]] | Run a requirements interview before critiquing the surface |
| [[visual-explainer]] | Present critique findings as a visual explainer page |

<!-- decision-feedback-protocol:v2 -->
- Question timing is runtime-owned. Do not make the skill itself decide when feedback is asked.
- If post-run feedback capture is enabled, emit a non-blocking `post_run_feedback` event via Codex `request_user_input` after result delivery.
- Capture `decision`, `outcome`, and `confidence`.
- Persist feedback with `python3 scripts/record_skill_feedback.py`.
