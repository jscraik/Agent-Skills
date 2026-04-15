---
name: nano-banana-builder
description: "Build web applications that use Google's Nano Banana image APIs for generation and iterative editing workflows. Use when a user asks to prototype or ship a Nano Banana powered image product from text-to-image to multi-turn editing."
metadata:
  skill-type: scaffolding_templates
---

# Nano Banana Builder

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Model baseline](#model-baseline)
- [Philosophy](#philosophy)
- [Workflow](#workflow)
- [Validation](#validation)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [Remember](#remember)

## Standards snapshot (March 2026)
- Treat Nano Banana apps as conversational image systems, not single-shot prompt forms with branding on top.
- Keep model choice explicit because speed, quality, cost, and editing behavior differ materially.
- Design for iteration history, storage, and quota handling from the start.

## When to use
- Prototype or ship an app that uses Nano Banana image generation or editing APIs.
- Design a multi-turn image workflow with conversational refinement.
- Review a Nano Banana product flow for model fit, storage, or iteration architecture.

## When not to use
- One-off image generation with no app or workflow design in scope.
- OpenAI image tooling; use the repo’s OpenAI image skill for that surface.
- Generic frontend work unrelated to generative image product flows.

## Required inputs
- Product goal and user flow.
- Model expectations: speed-first or quality-first.
- Storage and persistence plan for outputs and conversation history.
- Platform and stack constraints.
- Cost, rate-limit, and concurrency expectations.

## Deliverables
- Product and architecture guidance for the Nano Banana flow.
- Model-selection rationale.
- State, storage, and iteration design notes.
- Validation and rollout guidance for quotas, edits, and asset persistence.

## Model baseline
Use only these image-generation model strings:
- `gemini-2.5-flash-image`
- `gemini-3-pro-image-preview`

Do not invent alternate names or date-suffixed variants.

## Philosophy
- Conversation over over-configured control panels.
- Iteration history is part of the product.
- Fast drafts and final-quality outputs are different jobs and should be designed that way.

## Workflow
1. Identify whether the app centers on generation, iterative editing, composition, or mixed workflows.
2. Choose the model intentionally:
  - `gemini-2.5-flash-image` for faster iteration and higher-throughput drafts.
  - `gemini-3-pro-image-preview` for higher-fidelity or text-heavy output.
3. Design conversation state and image persistence together so edits remain traceable.
4. Plan for storage of generated assets outside transient response payloads.
5. Add rate-limit, retry, and queue behavior before pretending the product is production-ready.
6. Validate the primary user loop end to end: prompt, generation, refinement, persistence, and recall.

## Validation
- Verify the proposed model name is one of the supported Nano Banana image models.
- Verify the design handles iterative refinement instead of only a one-shot generation path.
- Verify storage, caching, and asset persistence are explicit.
- Reuse bundled `Infrastructure/references/`, `Infrastructure/scripts/`, or `assets/` guidance when the skill folder provides them.

## Constraints
- Do not invent unsupported model names or capabilities.
- Do not treat base64-in-response as a durable storage strategy for production.
- Keep credentials, tokens, and sensitive user images redacted by default in examples and logs.
- Make cost and quota assumptions explicit before recommending architecture.

## Anti-patterns
- Building a conversational image product with no conversation state.
- Picking a model by vibe instead of latency, quality, and cost tradeoffs.
- Designing editing flows that discard prior image context every turn.
- Treating generated assets as temporary blobs with no persistence plan.

## Examples
- "Design a Nano Banana app for iterative product-shot refinement."
- "Choose between the two supported image models for a high-volume draft workflow."

## See Also

| Skill | When to use together |
|---|---|
| [[imagegen]] | Use as fallback for static image generation outside Nano Banana |
| [[sora]] | Follow image generation with AI video for richer content |
| [[chatgpt-apps]] | Integrate Nano Banana image APIs into a ChatGPT App |
| [[mcp-builder]] | Expose Nano Banana generation as MCP tools |

**Topic map:** [[frontend-ui]]

## Remember
- The core product loop is generate, inspect, refine, persist.
- Good Nano Banana products make iteration feel natural, not bolted on.
- A realistic storage and quota story is part of the feature, not follow-up work.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## Failure mode
- If the product flow, API access, or asset requirements are missing, stop, surface the exact prerequisite gap, and fall back to workflow design or setup validation before building.
