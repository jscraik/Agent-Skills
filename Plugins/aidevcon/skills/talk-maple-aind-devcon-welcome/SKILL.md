---
name: talk-maple-aind-devcon-welcome
description: "Summarizes Simon Maple's AI Native DevCon welcome and explains the conference framing: context window, latent space, tool pool, hallway track, attendee goals, and practical learning themes. Use when the user asks about the event opening, conference themes, AI-native development framing, or how to orient work around the talks."
metadata:
  skill-set: content-publishing
  level: reference
  skill-type: reference
  runtime-visibility: latent
---

# Welcome to AI Native DevCon

The welcome frames AI Native DevCon around three areas: context, latent capabilities, and tools, plus the practical goal of turning talks into usable learning.

## Read Order

1. Use `outline.md` for the talk thesis, concept map, and safe application boundaries.
2. Use `quote.md` when the answer needs a short supporting excerpt.
3. Use `transcript.md` only to confirm what remained after safety redaction.
4. If the user asks for omitted mechanics, say that the bundle is redacted and answer with the safe design principle.

## What This Skill Produces

- **event-theme summary**
- **three-track explanation**
- **attendee-goal checklist**
- **session-navigation guide**

## Core Workflow

When answering a factual question:

1. Identify the relevant concept from `outline.md`.
2. Answer in 2-5 sentences.
3. Add one short excerpt from `quote.md` only if it strengthens the answer.
4. State when the bundle does not cover a requested detail.

When applying the talk to the user's work:

1. Start with the three-track frame.
2. Explain how each track changes developer work.
3. Connect the frame to practical learning from talks.
4. Keep logistics separate from technical themes.
5. Do not describe automated capture mechanics.

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

User: What was the welcome about?
Response shape: Summarize the three tracks and the attendee challenge.

User: How should I use the talks?
Response shape: Suggest choosing a track, extracting patterns, and turning them into reviewed artifacts.
