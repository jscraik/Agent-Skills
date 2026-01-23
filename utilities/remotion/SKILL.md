---
name: remotion-best-practices
description: "Best-practice guidance for Remotion (React video). Use when building or reviewing Remotion compositions, timing, assets, audio, captions, or rendering."
metadata:
  tags: remotion, video, react, animation, composition
  short-description: "Remotion best practices and rule index."
---

# Remotion Best Practices

## When to use
- You are writing or reviewing Remotion code and need domain-specific guidance.
- You need patterns for compositions, timing, assets, audio, captions, transitions, or Mediabunny utilities.
- You want a rule-backed checklist before implementing a Remotion feature.

## Inputs
- Question or code context (optional file paths or snippets).
- Desired topic area (optional): compositions, timing, assets, audio, captions, transitions, rendering, or mediabunny.
- Constraints (performance, render target, platform, deadlines).

## Outputs
- Rule-backed guidance with pointers to the most relevant rule files.
- Suggested patterns or code approaches grounded in the rules.
- Risks and verification steps when applicable.
- Include `schema_version: 1` if outputs are contract-bound.

## Principles
- Use the timeline as the source of truth: timing and sequencing should be explicit.
- Prefer deterministic, testable animations and asset handling.
- Keep render performance in mind; avoid unnecessary work per frame.
- Use rule files as the authoritative reference; do not invent APIs or behavior.

## Variation
- Adapt recommendations to the render target (preview vs final render) and platform constraints.
- Vary guidance based on media type (video, audio, captions, images, 3D).
- For complex compositions, expand sequencing and timing guidance with explicit tradeoffs.

## Procedure
1) Clarify the goal and constraints (composition type, duration, render target).
2) Select the most relevant rule files from `rules/`.
3) Summarize the recommended approach and key do/don'ts.
4) Call out risks and verification steps (preview, render, or test).

## Validation
- Fail fast: stop at the first failed validation gate.
- Ensure guidance maps to an existing rule file.
- If suggesting code changes, recommend a minimal verification step (preview or render).

## Anti-patterns
- Guessing Remotion behavior without a rule reference.
- Mixing timing logic across multiple sources (timeline drift).
- Heavy per-frame computation that can be precomputed.
- Skipping captions or audio handling best practices when they are required.
- DO NOT invent APIs, props, or behaviors not covered in rules or official docs.
- NEVER assume remote assets are safe without validating decode support.

## Constraints
- Redact secrets/PII by default.
- Do not add dependencies without explicit approval.
- Do not claim official API behavior unless supported by a rule or verified source.

## Rules index
Read individual rule files for detailed explanations and code examples:

- [rules/3d.md](rules/3d.md) - 3D content in Remotion using Three.js and React Three Fiber
- [rules/animations.md](rules/animations.md) - Fundamental animation skills for Remotion
- [rules/assets.md](rules/assets.md) - Importing images, videos, audio, and fonts into Remotion
- [rules/audio.md](rules/audio.md) - Using audio and sound in Remotion - importing, trimming, volume, speed, pitch
- [rules/calculate-metadata.md](rules/calculate-metadata.md) - Dynamically set composition duration, dimensions, and props
- [rules/can-decode.md](rules/can-decode.md) - Check if a video can be decoded by the browser using Mediabunny
- [rules/charts.md](rules/charts.md) - Chart and data visualization patterns for Remotion
- [rules/compositions.md](rules/compositions.md) - Defining compositions, stills, folders, default props and dynamic metadata
- [rules/display-captions.md](rules/display-captions.md) - Displaying captions in Remotion with TikTok-style pages and word highlighting
- [rules/extract-frames.md](rules/extract-frames.md) - Extract frames from videos at specific timestamps using Mediabunny
- [rules/fonts.md](rules/fonts.md) - Loading Google Fonts and local fonts in Remotion
- [rules/get-audio-duration.md](rules/get-audio-duration.md) - Getting the duration of an audio file in seconds with Mediabunny
- [rules/get-video-dimensions.md](rules/get-video-dimensions.md) - Getting the width and height of a video file with Mediabunny
- [rules/get-video-duration.md](rules/get-video-duration.md) - Getting the duration of a video file in seconds with Mediabunny
- [rules/gifs.md](rules/gifs.md) - Displaying GIFs synchronized with Remotion's timeline
- [rules/images.md](rules/images.md) - Embedding images in Remotion using the Img component
- [rules/import-srt-captions.md](rules/import-srt-captions.md) - Importing .srt subtitle files into Remotion using @remotion/captions
- [rules/lottie.md](rules/lottie.md) - Embedding Lottie animations in Remotion
- [rules/measuring-dom-nodes.md](rules/measuring-dom-nodes.md) - Measuring DOM element dimensions in Remotion
- [rules/measuring-text.md](rules/measuring-text.md) - Measuring text dimensions, fitting text to containers, and checking overflow
- [rules/sequencing.md](rules/sequencing.md) - Sequencing patterns for Remotion - delay, trim, limit duration of items
- [rules/tailwind.md](rules/tailwind.md) - Using TailwindCSS in Remotion
- [rules/text-animations.md](rules/text-animations.md) - Typography and text animation patterns for Remotion
- [rules/timing.md](rules/timing.md) - Interpolation curves in Remotion - linear, easing, spring animations
- [rules/transcribe-captions.md](rules/transcribe-captions.md) - Transcribing audio to generate captions in Remotion
- [rules/transitions.md](rules/transitions.md) - Scene transition patterns for Remotion
- [rules/trimming.md](rules/trimming.md) - Trimming patterns for Remotion - cut the beginning or end of animations
- [rules/videos.md](rules/videos.md) - Embedding videos in Remotion - trimming, volume, speed, looping, pitch

## Examples
- "How should I structure Remotion compositions for a 3-scene explainer?"
- "Best practices for audio timing and captions in Remotion?"
- "What is the right way to check video decode support before render?"

## Resources
- `references/contract.yaml`
- `references/evals.yaml`

## Remember
The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they do not constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.
