---
name: youtube-hooks-scripts
description: Create high-retention hooks and full scripts for technical YouTube videos
  tailored to topic, audience, and length. Use when the user asks for a hook, outline,
  or full script.
metadata:
  short-description: Create high-retention hooks and full scripts for technical YouTube
    videos tai...
---

# YouTube Hooks & Scripts

Purpose: Deliver the core outputs for this skill. The full guidance lives in `references/full-guide.md`.

## Scope and triggers
- Use when asked for technical YouTube hooks and long-form scripts.
- For broader product/PRD work, route to `product-spec`.

## Required inputs
- Topic, audience, and any provided transcript/notes.

## Deliverables
- Requested deliverable (hooks/scripts or titles/thumbnail text).
- Include `schema_version: 1` if you return a structured schema.

## Constraints
- Redact secrets/PII by default.
- Do not invent metrics or claims; ask for missing facts.

## Validation
- Confirm tone, audience fit, and length constraints.
- Fail fast if key inputs are missing.

## Anti-patterns
- Overlong outputs that ignore format limits.
- Generic suggestions not tied to the topic.

## Philosophy
- Favor clarity, explicit tradeoffs, and verifiable outputs.
- Encourage variation: adapt steps for different contexts and enable creative exploration.

## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.
- If context differs, customize steps to fit the situation.

## Antipatterns
- Do not add features outside the agreed scope.

## Examples
- "Provide a concise response for this task."
- "Follow the workflow and summarize outputs."

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.
