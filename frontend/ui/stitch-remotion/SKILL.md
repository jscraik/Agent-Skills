---
name: stitch-remotion
description: Generate Stitch-to-Remotion walkthrough videos from screen assets. Use this skill when a user asks to transform Stitch screens into narrated or demo-style videos with transitions, overlays, and rendered exports.
metadata:
  skill-type: scaffolding_templates
---

# Stitch Remotion

Turn Stitch screens into a maintainable Remotion walkthrough workflow instead of a one-off stitched screen dump.

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [Design-system integration](#design-system-integration)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Variation](#variation)
- [Failure mode](#failure-mode)
- [Constraints](#constraints)
- [Workflow](#workflow)
- [Anti-patterns](#anti-patterns)
- [Validation](#validation)
- [Examples](#examples)
- [References](#references)

## Standards snapshot
- Treat the video as a communication artifact, not a stitched slideshow.
- Treat React 19 as the baseline for Remotion composition code and integration guidance.
- Prefer manifest-driven screen retrieval and deterministic composition structure.
- Hold caption readability, contrast, and motion fallback decisions to WCAG 2.2-aligned accessibility outcomes.
- Keep pacing, text readability, and source accuracy ahead of motion flourishes.
- Validate with preview output before final render.

## Design-system integration
- Apply `frontend/ui/references/design-system-integration-contract.md` for typography, spacing, iconography, and token choices used in overlays and caption layers.
- Route shared token architecture and design-language governance changes to `design-system`.
- Use `frontend/ui/references/skill-routing-matrix-2026.md` when walkthrough-video requests overlap with non-video frontend UI skill scope.

## When to use
- The user wants to turn Stitch screens into a walkthrough or demo video.
- A Remotion composition should be built or updated from Stitch screen assets.
- The task needs preview or export-ready output from a repeatable pipeline.

## Required inputs
- Stitch project and screen identifiers, or enough context to resolve them.
- Desired screen order, message focus, and output format.
- Existing Remotion project context, or permission to scaffold one.

## Deliverables
- Remotion composition files and supporting assets.
- Preview or final render output path plus the key render command.
- A short note on pacing, transitions, and any unresolved source limitations.

## Philosophy
- Motion should support comprehension, not compete with it.
- Deterministic structure keeps edits maintainable.
- The safest walkthrough is one that stays faithful to the underlying product flow.
- Ask: "Will this cut help the viewer understand the feature faster?"
- Ask: "Can this composition still be edited safely in one pass next week?"

## Variation
- Adapt walkthrough style to the audience:
  - onboarding flow: slower pacing, explicit labels, and fewer transitions;
  - internal release demo: faster pacing, concise overlays, and issue-focused beats;
  - executive recap: fewer screens, stronger narrative framing, and outcome-first captions.
- Vary composition complexity by source quality:
  - complete Stitch manifests: use deterministic sequencing and reusable scene wrappers;
  - partial assets: stage a plan-first pass and avoid pretending missing screens exist.
- Keep scope narrow: start with one reliable storyboard path before adding alternate cuts.

## Failure mode
- If Stitch assets cannot be resolved, stop before inventing scenes.
- If the user wants a broader video production workflow unrelated to Stitch assets, route to a more general Remotion or video skill.
- If there is no Remotion context and scaffolding is out of scope, stay at plan level rather than claiming build completion.

## Constraints
- Redact secrets and sensitive information in overlays, captions, and logs.
- Preserve source-accurate product behavior; do not invent unsupported flows.
- Keep motion accessible and avoid effects that reduce readability.

## Workflow
1. Confirm Stitch and Remotion tool availability.
2. Resolve and retrieve the required screen assets.
3. Build or reuse a Remotion composition scaffold.
4. Sequence screens with transitions and concise overlays.
5. Run a preview render and refine pacing or containment issues.
6. Render final output and summarize the handoff path.

## Anti-patterns
- Avoid skipping preview validation before final render.
- Do not hardcode brittle asset paths when a manifest-driven approach is available.
- Never overuse transitions that distract from the actual walkthrough content.
- Anti-pattern warning: narration overlays that claim product behaviors not visible in the source screens are incorrect and erode trust.
- Shipping a final render without proving text containment and contrast in preview output is the wrong production posture.

## Validation
- Fail fast: stop at the first missing asset, composition error, or unreadable overlay.
- Verify all referenced screen assets resolve.
- Verify the composition renders without runtime errors.
- Verify text contrast, containment, and transition timing in preview output.
- Confirm UI-adjacent typography, spacing, icon usage, and token choices align with `frontend/ui/references/design-system-integration-contract.md`.

## Examples
- "Turn these five Stitch checkout screens into a 45-second walkthrough for launch notes."
- "I only have three screen exports and rough narration. Build a safe storyboard plan before rendering."
- "Our previous walkthrough felt flashy but unclear. Rework pacing and overlays for comprehension."
- "Create an internal demo cut that highlights the new billing flow without inventing missing states."

## References
- Contract: `references/contract.yaml`
- Evals: `references/evals.yaml`
- Task profile: `references/task-profile.json`
- Resources: `resources/screen-slide-template.tsx`, `resources/composition-checklist.md`
- Examples: `examples/walkthrough/`

## See Also

| Skill | When to use together |
|---|---|
| [[stitch-loop]] | Generate the Stitch screens that feed this skill |
| [[remotion]] | For custom Remotion compositions beyond Stitch walkthroughs |
| [[design-system]] | Keep overlay and caption styling aligned with canonical token and typography governance |
| [[slides]] | Compare slide deck with Remotion video for the same content |
| [[sora]] | Use Sora for AI-generated video alternative to Remotion |

**Topic map:** [[frontend-ui]]

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
