---
name: talk-moss-skills-team-workflow
description: "Explains James Moss's team-skills workflow and helps design skill governance: decomposition, ownership, versioning, eval scenarios, quality review, and lifecycle maintenance. Use when the user asks about moving from solo skill hacks to team workflow, avoiding skill sprawl, or treating skills like software."
metadata:
  skill-set: content-publishing
  level: reference
  skill-type: reference
  runtime-visibility: latent
---

# Using Skills to Pay the Bills

Team skills should be decomposed, owned, versioned, evaluated, and maintained like software artifacts.

## Read Order

1. Use `outline.md` for the talk thesis, concept map, and safe application boundaries.
2. Use `quote.md` when the answer needs a short supporting excerpt.
3. Use `transcript.md` only to confirm what remained after safety redaction.
4. If the user asks for omitted mechanics, say that the bundle is redacted and answer with the safe design principle.

## What This Skill Produces

- **team skill workflow**
- **skill decomposition plan**
- **eval scenario list**
- **maintenance checklist**

## Core Workflow

When answering a factual question:

1. Identify the relevant concept from `outline.md`.
2. Answer in 2-5 sentences.
3. Add one short excerpt from `quote.md` only if it strengthens the answer.
4. State when the bundle does not cover a requested detail.

When applying the talk to the user's work:

1. Split overloaded skills into focused capabilities.
2. Prefer extension by composition over editing shared instructions blindly.
3. Add example scenarios for each skill.
4. Assign owner and version policy.
5. Review skill quality before reuse.

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

User: How do we stop skill sprawl?
Response shape: Return a decomposition plan, owner table, and eval list.

User: Can you pull skills from a shared source?
Response shape: Decline setup actions and provide governance guidance.
