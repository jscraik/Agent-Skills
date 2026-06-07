---
name: talk-luebken-embedding-pi-coding-agent
description: "Explains, summarizes, and turns Matthias Luebken's talk on embedding Pi-style coding agents into safe product-design artifacts: tool-contract sketches, guardrail checklists, session-record models, and malleable-software review plans. Use when the user asks about OpenClaw, Pi-style product agents, lifecycle guardrails, agent sessions, or design-level application of these primitives."
metadata:
  skill-set: content-publishing
  level: reference
  skill-type: reference
  runtime-visibility: latent
---

# A Piece of PI - Embedding The OpenClaw Coding Agent In Your Product

Embedded coding agents become product architecture when agent setup, scoped tools, lifecycle guardrails, and session records are treated as first-class design surfaces.

## Read Order

1. Use `outline.md` for the talk thesis, concept map, and safe application boundaries.
2. Use `quote.md` when the answer needs a short supporting excerpt.
3. Use `transcript.md` only to confirm what remained after safety redaction.
4. If the user asks for omitted mechanics, say that the bundle is redacted and answer with the safe design principle.

## What This Skill Produces

- **tool-contract sketch**
- **lifecycle guardrail checklist**
- **session-record model**
- **malleable-software boundary plan**

## Core Workflow

When answering a factual question:

1. Identify the relevant concept from `outline.md`.
2. Answer in 2-5 sentences.
3. Add one short excerpt from `quote.md` only if it strengthens the answer.
4. State when the bundle does not cover a requested detail.

When applying the talk to the user's work:

1. Define the product task and the human review point.
2. List the scoped capabilities the agent may use.
3. Add boundary checks before and after sensitive actions.
4. Record decisions and tool results in a session history.
5. Mark every implementation detail not present in the bundle as outside the talk.

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

User: How would Luebken design this for an internal workflow?
Response shape: Map the workflow to four primitives: setup, scoped tools, guardrails, and session records. Then propose a reviewable draft-first design.

User: Can you write the hook code?
Response shape: Decline executable implementation details and provide a guardrail specification instead.
