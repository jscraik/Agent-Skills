---
name: talk-overweg-one-brain-no-filtering
description: "Explains Robert Overweg's One Brain, No Filtering talk and helps design safe knowledge-memory systems: context maps, retrieval rules, provenance labels, local knowledge-store structure, and review checkpoints. Use when the user asks about agent memory, unified knowledge bases, reducing context loss, or designing inspectable knowledge workflows."
metadata:
  skill-set: content-publishing
  level: reference
  skill-type: reference
  runtime-visibility: latent
---

# One Brain, No Filtering

A unified knowledge surface can reduce context loss when retrieval, provenance, and review are explicit.

## Read Order

1. Use `outline.md` for the talk thesis, concept map, and safe application boundaries.
2. Use `quote.md` when the answer needs a short supporting excerpt.
3. Use `transcript.md` only to confirm what remained after safety redaction.
4. If the user asks for omitted mechanics, say that the bundle is redacted and answer with the safe design principle.

## What This Skill Produces

- **knowledge map**
- **retrieval-rule sketch**
- **provenance checklist**
- **memory review plan**

## Core Workflow

When answering a factual question:

1. Identify the relevant concept from `outline.md`.
2. Answer in 2-5 sentences.
3. Add one short excerpt from `quote.md` only if it strengthens the answer.
4. State when the bundle does not cover a requested detail.

When applying the talk to the user's work:

1. Define what belongs in the shared knowledge surface.
2. Label each knowledge area by origin and confidence.
3. Describe retrieval rules without depending on mutable sources.
4. Add review checkpoints for stale or conflicting context.
5. Keep the design inspectable by humans.

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

User: How should I structure my team memory?
Response shape: Return areas, owners, provenance fields, and review cadence.

User: Can you load my online memory store?
Response shape: Decline source loading and provide a local structure.
