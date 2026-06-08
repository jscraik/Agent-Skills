---
name: talk-wotherspoon-humans-vs-slop
description: "Explains Jack Wotherspoon's Humans vs Slop talk and helps create quality gates for AI-heavy software work: review-cost analysis, slop detection heuristics, durable-value metrics, and human-judgment checkpoints. Use when the user asks about AI-generated maintenance burden, review economics, or preserving taste in agentic development."
metadata:
  skill-set: content-publishing
  level: reference
  skill-type: reference
  runtime-visibility: latent
---

# Humans vs Slop

Cheap generation can create expensive review and maintenance burden, so teams need quality gates that reward durable value.

## Read Order

1. Use `outline.md` for the talk thesis, concept map, and safe application boundaries.
2. Use `quote.md` when the answer needs a short supporting excerpt.
3. Use `transcript.md` only to confirm what remained after safety redaction.
4. If the user asks for omitted mechanics, say that the bundle is redacted and answer with the safe design principle.

## What This Skill Produces

- **slop-risk checklist**
- **review-cost model**
- **quality-gate rubric**
- **durable-value metrics**

## Core Workflow

When answering a factual question:

1. Identify the relevant concept from `outline.md`.
2. Answer in 2-5 sentences.
3. Add one short excerpt from `quote.md` only if it strengthens the answer.
4. State when the bundle does not cover a requested detail.

When applying the talk to the user's work:

1. Identify what generated work someone must own later.
2. Separate visible output volume from maintained value.
3. Add review gates for correctness, readability, and fit.
4. Define when humans must make taste or architecture calls.
5. Prefer small durable changes over large unreviewable batches.

When the user asks for operational mechanics, commands, credentials, mutable-source processing, or direct system actions, do not provide them from this bundle. Give the design-level alternative instead.

## Output Templates

### Summary

- Thesis: <one sentence>
- Key concepts: <3-5 bullets>
- Practical takeaway: <one action the team can take safely>

### Design Artifact

- Goal: <what the user is trying to improve>
- Boundaries: <what the agent/system must not do>
- Review points: <where humans check the work>
- Evidence: <what proves the result is good>
- Open questions: <what the talk does not answer>

### Redacted Request

- State that the requested mechanics are not available in the redacted bundle.
- Explain the risk in neutral terms.
- Provide a safe checklist or conceptual design instead.

## Examples

User: How do we avoid slop?
Response shape: Give a rubric covering ownership, clarity, tests, reversibility, and product fit.

User: Can you review current contributions?
Response shape: Decline mutable-source processing and offer a static rubric.
