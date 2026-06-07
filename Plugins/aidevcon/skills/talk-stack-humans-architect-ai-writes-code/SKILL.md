---
name: talk-stack-humans-architect-ai-writes-code
description: "Explains Paul Stack's architecture-first AI workflow and helps create safe design artifacts: intent documents, architecture constraints, planner/reviewer loops, UAT criteria, and agent-output review gates. Use when the user asks about humans owning architecture while agents implement, why vibes do not scale, or applying the talk to team workflow design."
metadata:
  skill-set: content-publishing
  level: reference
  skill-type: reference
  runtime-visibility: latent
---

# The Humans Architect the System, the AI Writes the Code

Humans should own intent and architecture while agents implement within explicit constraints and review gates.

## Read Order

1. Use `outline.md` for the talk thesis, concept map, and safe application boundaries.
2. Use `quote.md` when the answer needs a short supporting excerpt.
3. Use `transcript.md` only to confirm what remained after safety redaction.
4. If the user asks for omitted mechanics, say that the bundle is redacted and answer with the safe design principle.

## What This Skill Produces

- **intent document**
- **architecture-constraint list**
- **planner/reviewer loop**
- **UAT checklist**

## Core Workflow

When answering a factual question:

1. Identify the relevant concept from `outline.md`.
2. Answer in 2-5 sentences.
3. Add one short excerpt from `quote.md` only if it strengthens the answer.
4. State when the bundle does not cover a requested detail.

When applying the talk to the user's work:

1. State the system intent before implementation.
2. List architectural constraints the agent must preserve.
3. Separate planning from adversarial review.
4. Use UAT criteria as the source of truth.
5. Reject output that cannot be reviewed against intent.

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

User: How should my team use this pattern?
Response shape: Return an intent doc outline, planner responsibilities, reviewer checks, and UAT gates.

User: Can you process our current feature request?
Response shape: Decline mutable work-item processing and provide the workflow template.
