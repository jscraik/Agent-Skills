---
name: imagegen
description: "Use when the user asks to generate or edit images via the OpenAI Image API (for example: generate image, edit/inpaint/mask, background removal or replacement, transparent background, product shots, concept art, covers, or batch variants); run the bundled CLI (`scripts/image_gen.py`) and require `OPENAI_API_KEY` for live calls."
metadata:
  skill-type: scaffolding_templates
---

# Imagegen

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Workflow](#workflow)
- [Verification](#verification)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Remember](#remember)

## Standards snapshot (March 2026)
- Prefer deterministic, repeatable image workflows over ad hoc prompt improvisation.
- Use the bundled CLI so runs can be repeated, compared, and handed off cleanly.
- Validate output against the user’s invariants, not just aesthetic taste.

## When to use
- Generate new images for product, marketing, UI, or concept work.
- Edit existing images with masks, inpainting, background changes, cleanup, or subject-preserving tweaks.
- Run batch generation or variant exploration with explicit prompt and output control.

## When not to use
- General illustration advice with no intent to generate or edit assets.
- Requests that require a different medium entirely, such as video generation.
- Live API runs when `OPENAI_API_KEY` is unavailable and no offline fallback is acceptable.

## Required inputs
- Goal: generate, edit, or batch.
- Prompt and any must-keep invariants.
- Optional source image(s) and mask(s) for edits.
- Output requirements: size, format, transparency, count, destination path.
- Whether live API calls are allowed in the current environment.

## Deliverables
- Generated or edited image files saved to the agreed path.
- The final prompt and CLI flags used.
- A short validation note covering the key invariants and any remaining defects.

## Philosophy
- One deliberate change per iteration.
- Reproducibility beats one-off magic.
- Preserve user-specified text, branding, layout anchors, and subject identity unless the user explicitly relaxes them.

## Workflow
1. Classify the request as `generate`, `edit`, or `batch`.
2. Lock the invariants before running anything: subject, composition, text, style boundaries, and avoid list.
3. Use the bundled `scripts/image_gen.py` CLI rather than ad hoc scripts.
4. For batch work, keep inputs structured and filenames stable.
5. Inspect the result and compare it against the requested invariants, not just whether it "looks good."
6. If iteration is needed, change one variable at a time: prompt wording, mask, or output settings.

## Verification
- Confirm the output files exist at the intended location.
- Confirm subject, composition, and required text match the request closely enough to ship.
- Confirm no sensitive data, secrets, or unintended private identifiers were embedded.
- If live generation was not run, say why and what remains unverified.

## Validation
- Verify the final handoff includes output path, prompt, and CLI flags.
- Verify edits preserve the user’s stated invariants before approving a rerun.
- Use the skill `references/` material for CLI flags and prompt-shaping guidance when needed.
- Reuse bundled `scripts/` helpers instead of writing parallel one-off generators.

## Constraints
- Require `OPENAI_API_KEY` for live API calls.
- Never ask the user to paste API keys into chat.
- Prefer the OpenAI SDK-backed bundled CLI over raw HTTP or improvised helper scripts.
- Do not silently overwrite important assets without an agreed output path or naming scheme.

## Anti-patterns
- Inventing style or brand requirements the user did not request.
- Making multiple prompt changes at once and losing the causal thread.
- Returning assets without the prompt and flags needed to reproduce them.
- Treating text-in-image accuracy as optional when the user asked for specific wording.

## Examples
- "Generate a transparent PNG product shot for a landing page."
- "Edit this hero image to remove the background and keep the subject unchanged."

## See Also

| Skill | When to use together |
|---|---|
| [[sora]] | Follow static image generation with AI video generation |
| [[og-image-creator]] | Use generated images as OG image assets |
| [[nano-banana-builder]] | Integrate imagegen into Nano Banana iterative editing flows |
| [[youtube-titles-thumbnails]] | Generate thumbnail concept images for YouTube packaging |
| [[visual-explainer]] | Embed generated images as hero banners in HTML explainers |

**Topic map:** [[frontend-ui]]

## Remember
- This skill is for execution, not generic image brainstorming.
- When editing, protect invariants first and creative expansion second.
- The best handoff includes files, prompt, flags, and what still needs human taste review.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## Failure mode
- If the prompt, asset inputs, or API prerequisites are missing, stop, report the exact blocker, and fall back to preparing prompts/assets or verifying credentials before attempting image generation.
