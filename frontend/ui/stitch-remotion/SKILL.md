---
name: stitch-remotion
description: Generate Stitch-to-Remotion walkthrough videos from screen assets. Use this skill when a user asks to transform Stitch screens into narrated or demo-style videos with transitions, overlays, and rendered exports.
---

# Stitch to Remotion Walkthrough Videos

Build polished walkthrough videos from Stitch screens using a reproducible Remotion workflow.

## When to use
- Use this skill when the request is to turn Stitch screens into a walkthrough video.
- Use this skill when the user asks for Remotion composition files, preview renders, or export-ready video.

## Inputs
- Stitch project and screen identifiers, or enough context to resolve them.
- Desired walkthrough order, messaging emphasis, and output format.
- Existing Remotion project context, or permission to scaffold one.

## Outputs
- Remotion composition files and supporting assets.
- Rendered preview/video artifact and export command summary.
- Validation notes for timing, readability, transitions, and content integrity.

## Philosophy
- Treat the video as a communication artifact, not a screen dump.
- Prefer deterministic composition structure so edits stay maintainable.
- Balance motion polish with readability and pacing.
- Which scenes are essential for user comprehension?
- What is the minimum animation needed to keep clarity high?
- Which tradeoff matters more: spectacle or understanding?

## Constraints
- Redact secrets and sensitive information in overlays, captions, and logs.
- Preserve source-accurate product behavior; do not invent unsupported flows.
- Keep motion accessible and avoid effects that reduce readability.

## Procedure
1. Discover Stitch and Remotion tool prefixes and confirm runtime availability.
2. Retrieve project screens and download screenshot assets.
3. Build or reuse a Remotion composition scaffold.
4. Sequence screens with transitions and concise overlays.
5. Run preview render and refine pacing/layout.
6. Render final output and summarize handoff commands.

## Validation
- Verify all referenced screen assets resolve.
- Verify composition renders without runtime errors.
- Verify text contrast, containment, and transition timing in preview output.
- Fail fast: stop at first blocker and report exact remediation.

## Anti-patterns
- Do not skip preview validation before final render.
- Never hardcode brittle paths when a manifest-driven approach is available.
- Do not overuse transitions that distract from content.
- Avoid repetitive, generic, cookie-cutter animation patterns.
- Warn on common pitfalls such as clipped overlays, unreadable text, and misplaced assets.

## Variation
- Vary transition style and scene duration by content complexity.
- Adapt narration overlays for technical versus product audiences.
- Customize component structure for small demos versus long walkthroughs.

## Examples
- Convert Stitch project screens into a 60s feature walkthrough.
- Rebuild an existing walkthrough with new sequence order and updated captions.

## Resource map
- Scripts: `scripts/`
- References: `references/contract.yaml`, `references/evals.yaml`, `references/task-profile.json`
- Resources: `resources/screen-slide-template.tsx`, `resources/composition-checklist.md`
- Examples: `examples/walkthrough/`

<!-- decision-feedback-protocol:v2 -->
## Decision Quality Feedback
- If post-run feedback capture is enabled, emit non-blocking `post_run_feedback` after delivering results.
- Capture `decision`, `outcome`, and `confidence`.
- Persist with `python3 utilities/skill-builder/scripts/record_skill_feedback.py`.
<!-- /decision-feedback-protocol -->
