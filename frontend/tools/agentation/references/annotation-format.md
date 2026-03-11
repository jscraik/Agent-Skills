# Agentation annotation format reference

Status: curated reference for the canonical `frontend/tools/agentation` skill.
Updated: 2026-03-11.

## Purpose

Use this document as the stable reference for Agentation's annotation data model, lifecycle, and copied-output expectations.

This is the right source when we need to answer questions like:
- what fields make an annotation actionable for an agent;
- which lifecycle states must be preserved;
- how threaded replies fit into the workflow;
- what copied markdown should include so an agent can locate the right UI element.

## Provenance

This reference is derived from:
- the user-provided Agentation AFS excerpt captured on 2026-03-11;
- the public Agentation article at [benji.org/agentation](https://benji.org/agentation), which describes structured output, source detection, and agent-facing feedback formatting;
- current public self-driving/install references recorded in `references/public-sources.md`.

Because the primary marketing domain was not a stable authority during this update, treat this file as the local durable summary of the stable contract rather than relying on homepage prose.

## Stable model

### Required annotation fields

These fields are the minimum actionable core:
- `id`
- `comment`
- `elementPath`
- `timestamp`
- `x`
- `y`
- `element`

Interpretation:
- `elementPath` is the primary locator.
- `x` and `y` are UI-location hints, not a substitute for semantic element identity.
- `comment` is the human request the agent must interpret.

### Recommended context fields

These materially improve agent accuracy:
- `url`
- `boundingBox`

When available, treat them as first-class evidence for narrowing the search space.

### Optional context fields

Useful enrichment fields include:
- `reactComponents`
- `cssClasses`
- `computedStyles`
- `accessibility`
- `nearbyText`
- `selectedText`
- `isFixed`
- `isMultiSelect`
- `fullPath`
- `nearbyElements`
- `intent`
- `severity`

These fields help the agent choose the right debugging or implementation strategy, but the absence of one field should not make the annotation unusable if the required core is present.

## Lifecycle contract

Preserve these status values exactly:
- `pending`
- `acknowledged`
- `resolved`
- `dismissed`

Operational meaning:
- `pending`: waiting for review or work.
- `acknowledged`: seen and actively being worked.
- `resolved`: addressed and closed.
- `dismissed`: intentionally not being applied.

Do not collapse or rename these statuses in skill prose, evals, or generated artifacts without an explicit versioned contract change.

### Threaded replies

Annotations may carry a `thread` of back-and-forth messages.
Use that thread for:
- clarification requests;
- agent progress updates;
- human follow-up or approval.

This means Agentation is not just a one-shot comment emitter. It supports conversational resolution.

## Event envelope expectations

For streaming or replay-friendly flows, treat the event envelope as having these stable properties:
- `type`
- `timestamp`
- `sessionId`
- `sequence`
- `payload`

The important invariant is that `sequence` is monotonic and usable for ordering and replay detection.

## Copied output expectations

When Agentation output is copied into a chat-based coding workflow, the output should preserve enough structure for an agent to find the right target quickly.

High-value copied fields include:
- selector or path
- source file and line when available
- classes
- React component path when available
- nearby or selected text
- bounding box for ambiguous layout issues
- issue text or feedback comment

The copied output may be formatted as markdown, but it should remain machine-tractable and agent-friendly.

## How this should shape the skill

### SKILL.md

Use this reference when describing:
- lifecycle states;
- thread/reply behavior;
- copied-output expectations;
- what counts as a complete end-to-end verification story.

### contract.yaml

Keep output claims aligned with:
- lifecycle status vocabulary;
- threaded reply semantics;
- structured copied output.

### evals.yaml

Add or preserve cases that check:
- lifecycle-state literacy;
- thread/reply understanding;
- structured-output guidance for agent consumption.

## Change-control rule

If future public Agentation docs materially change the annotation object, lifecycle, or output tiers, update this file first, then update the skill, contract, and evals from here.
