---
name: talk-sloan-harness-engineering-beyond-code
description: "Summarizes Rob Sloan's harness-engineering talk and creates safe design artifacts for agent context beyond code: product-intent packets, design constraints, acceptance criteria, context ownership, and review gates. Use when the user asks about making non-code context agent-ready or improving AI work with product/design intent."
metadata:
  skill-set: content-publishing
  level: reference
  skill-type: reference
  runtime-visibility: latent
---

# Harness Engineering Beyond Code

Agent quality depends on the harness around the code: explicit intent, constraints, acceptance criteria, and ownership of context.

## Read Order

1. Use `outline.md` for the talk thesis, concept map, and safe application boundaries.
2. Use `quote.md` when the answer needs a short supporting excerpt.
3. Use `transcript.md` only to confirm what remained after safety redaction.
4. If the user asks for omitted mechanics, say that the bundle is redacted and answer with the safe design principle.

## What This Skill Produces

- **context packet**
- **acceptance-criteria checklist**
- **design-constraint summary**
- **harness audit**

## Core Workflow

When answering a factual question:

1. Identify the relevant concept from `outline.md`.
2. Answer in 2-5 sentences.
3. Add one short excerpt from `quote.md` only if it strengthens the answer.
4. State when the bundle does not cover a requested detail.

When applying the talk to the user's work:

1. State the product intent in one paragraph.
2. List non-code constraints separately from code constraints.
3. Turn vague goals into acceptance criteria.
4. Name the owner of each context area.
5. Define review gates before agent output is accepted.

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

User: What context should I give an agent?
Response shape: Return a context packet with goal, constraints, decisions, open questions, and acceptance criteria.

User: Can you connect to our design tool?
Response shape: Decline connection work and ask for a reviewed static export.
