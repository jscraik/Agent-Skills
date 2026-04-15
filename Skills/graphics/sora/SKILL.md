---
name: "sora"
description: "Generate, remix, manage, or download videos through OpenAI's Sora API using the bundled CLI. Use when the user wants AI video generation or asset retrieval, not traditional video editing."
metadata:
  skill-type: scaffolding_templates
---

# Sora

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Workflow](#workflow)
- [Validation](#validation)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [Remember](#remember)

## Standards snapshot (March 2026)
- Prefer the bundled CLI so Sora runs stay reproducible and easy to hand off.
- Treat async job state, downloads, and prompt iteration as part of the workflow, not follow-up chores.
- Keep Sora requests inside the current safety and access envelope: valid API access, under-18-safe content, and no real-person or copyrighted-character requests.

## When to use
- Generate a new Sora video from a prompt.
- Remix, poll, list, download, or delete Sora jobs through the bundled CLI.
- Run batch video generation with explicit prompt and output control.

## When not to use
- Static image generation or editing with no video workflow.
- Open-ended storyboard ideation with no intention to run the Sora CLI.
- Live API calls when `OPENAI_API_KEY` or Sora access is unavailable.

## Required inputs
- Prompt or prompt file.
- Intent: create, remix, poll, list, download, delete, or batch.
- Optional reference image and any invariants to preserve.
- Output requirements: model, size, duration, variant count, local destination.

## Deliverables
- Requested video assets or job-state results.
- Final prompt and CLI flags used.
- A short validation note covering duration, size, and critical invariants.

## Philosophy
- One clear job type per run: create, remix, inspect, or download.
- Preserve invariants explicitly during remixes.
- Make prompt iteration deliberate instead of piling on uncontrolled changes.

## Workflow
1. Classify the request: create, remix, status/download, or batch.
2. Collect prompt, model, size, duration, and any reference media or invariants.
3. Use the bundled `Infrastructure/scripts/sora.py` CLI rather than ad hoc scripts.
4. For structured prompt files, avoid double augmentation.
5. Poll async jobs until they reach a usable terminal state when the user needs assets now.
6. Download requested outputs to a stable local path and report exactly what was saved.
7. Iterate with one targeted prompt or remix change at a time.

## Validation
- Require `OPENAI_API_KEY` and Sora API access before live calls.
- Verify outputs match requested duration, size, and key creative invariants closely enough to ship.
- Verify generated assets are saved locally before considering the job complete.
- Reuse skill `Infrastructure/references/`, `Infrastructure/scripts/`, and any packaged `assets/` helpers instead of inventing parallel wrappers.

## Constraints
- Never request or print secrets, tokens, or private URLs.
- Enforce under-18-safe content guidance.
- Do not use copyrighted characters, copyrighted music, or real people.
- Keep reference images and downloaded assets treated as potentially sensitive user material.

## Anti-patterns
- Mixing job creation, polling, and prompt debugging into one vague step.
- Asking the user to paste API keys into chat.
- Treating Sora’s async flow like a synchronous image API.
- Returning "done" before assets are actually downloaded when the user asked for files.

## Examples
- "Generate a 4-second Sora clip for a product teaser and download the video."
- "Remix this Sora job but keep the shot and only change the lighting."

## See Also

| Skill | When to use together |
|---|---|
| [[imagegen]] | Generate static images as storyboard reference before Sora |
| [[remotion]] | Compare Sora (AI-driven) with Remotion (code-driven) for video |
| [[nano-banana-builder]] | Use Nano Banana for images; Sora for the video component |
| [[youtube-hooks-scripts]] | Script the video before generating with Sora |

**Topic map:** [[frontend-ui]]

## Remember
- Sora work is job-based, async, and stateful.
- The handoff should always say what was created, where it was saved, and what prompt/flags produced it.
- Safety constraints are part of the feature, not a disclaimer at the end.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## Failure mode
- If prompt inputs, API access, or generation job state cannot be verified, stop, report the exact blocker, and fall back to setup validation or prompt preparation before retrying video generation.
