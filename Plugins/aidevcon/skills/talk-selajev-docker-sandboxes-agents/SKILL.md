---
name: talk-selajev-docker-sandboxes-agents
description: "Explains Oleg Selajev's Docker Sandboxes talk and helps design safe, conceptual agent-isolation policies: file-sharing boundaries, network policy, secret isolation, audit expectations, and team rollout questions. Use when the user asks about sandboxed agents, hard isolation, local agent risk, or how to reason about agent safety without setup instructions."
metadata:
  skill-set: content-publishing
  level: reference
  skill-type: reference
  runtime-visibility: latent
---

# You're Absolutely Right, It Was Your Home Directory!

Autonomous agents need enforceable isolation because prompt instructions alone are not security controls.

## Read Order

1. Use `outline.md` for the talk thesis, concept map, and safe application boundaries.
2. Use `quote.md` when the answer needs a short supporting excerpt.
3. Use `transcript.md` only to confirm what remained after safety redaction.
4. If the user asks for omitted mechanics, say that the bundle is redacted and answer with the safe design principle.

## What This Skill Produces

- **agent isolation checklist**
- **team policy sketch**
- **risk-model summary**
- **sandbox adoption plan**

## Core Workflow

When answering a factual question:

1. Identify the relevant concept from `outline.md`.
2. Answer in 2-5 sentences.
3. Add one short excerpt from `quote.md` only if it strengthens the answer.
4. State when the bundle does not cover a requested detail.

When applying the talk to the user's work:

1. Name the asset that must be protected.
2. State which file areas are shared and which remain blocked.
3. State network policy in allow/deny language without setup steps.
4. Keep sensitive values outside the agent-visible environment.
5. Require logs and reproducible throwaway environments.

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

User: What is the main lesson?
Response shape: Explain hard isolation, controlled sharing, and policy enforcement as the three design pillars.

User: Give me the setup manifest.
Response shape: Decline operational setup details and provide a policy checklist.
