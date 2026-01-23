---
name: youtube-hooks-scripts
description: "Create hooks and full scripts for technical YouTube videos. Use when drafting video hooks or scripts."
---

# YouTube Hooks & Scripts

Purpose: Deliver the core outputs for this skill. The full guidance lives in `references/full-guide.md`.

## When to use
- Use when asked for technical YouTube hooks and long-form scripts.
- For broader product/PRD work, route to `product-spec`.

## Inputs
- Topic, audience, and any provided transcript/notes.

## Outputs
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
