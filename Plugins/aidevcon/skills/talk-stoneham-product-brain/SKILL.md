---
name: talk-stoneham-product-brain
description: "Explains the Product Brain talk and helps design curated product-memory systems for AI-assisted product work: knowledge structure, provenance, synthesis cadence, ownership, and agent-ready context packets. Use when the user asks about product context for AI, product knowledge management, product documentation for LLMs, or building a maintained product brain."
metadata:
  skill-set: content-publishing
  level: reference
  skill-type: reference
  runtime-visibility: latent
---

# Product Brain

A product brain is a maintained product knowledge system that helps agents and humans reason from curated context instead of scattered memory.

## Read Order

1. Use `outline.md` for the talk thesis, concept map, and safe application boundaries.
2. Use `quote.md` when the answer needs a short supporting excerpt.
3. Use `transcript.md` only to confirm what remained after safety redaction.
4. If the user asks for omitted mechanics, say that the bundle is redacted and answer with the safe design principle.

## What This Skill Produces

- **product-brain map**
- **curation checklist**
- **context packet template**
- **ownership model**

## Core Workflow

When answering a factual question:

1. Identify the relevant concept from `outline.md`.
2. Answer in 2-5 sentences.
3. Add one short excerpt from `quote.md` only if it strengthens the answer.
4. State when the bundle does not cover a requested detail.

When applying the talk to the user's work:

1. Choose a small set of curated knowledge categories.
2. Record provenance and owner for each category.
3. Define when synthesis happens and who reviews it.
4. Create agent-ready packets with goals, constraints, and decisions.
5. Avoid direct intake mechanics; keep the design static and reviewable.

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

User: How do I build a product brain?
Response shape: Provide categories, ownership, synthesis cadence, and review gates.

User: Can you ingest our product tickets?
Response shape: Decline intake work and offer a curated export template.
