---
name: feature-video
description: Produce a concise feature walkthrough video and package the result for review or release workflows. Use when a user needs a demo artifact, PR-ready walkthrough, or polished clip for a shipped product change.
metadata:
  skill-type: team_automation
---

# Feature Video

## Table of Contents
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Philosophy](#philosophy)
- [Workflow](#workflow)
- [Production paths](#production-paths)
- [Validation](#validation)
- [Gotchas](#gotchas)
- [Anti-patterns](#anti-patterns)
- [References](#references)
- [See also](#see-also)

## When to use

Use this skill when:
- a feature needs a walkthrough video for a PR, release note, or team handoff;
- static screenshots are not enough to explain the user flow;
- the user wants a clear demo artifact tied to a specific product change.

Do not use this skill when:
- the request is only for title or thumbnail ideation;
- the user wants a fully synthetic AI video unrelated to the actual product flow;
- there is no stable source material for the walkthrough yet.

## Required inputs

- target feature or flow;
- source material:
  - running app,
  - Stitch screens,
  - existing Remotion project,
  - or screen recording plan;
- intended destination:
  - PR comment,
  - release artifact,
  - internal demo,
  - or handoff note.
- if the goal is a real product walkthrough recorded from a running app:
  - PR number or `current`,
  - base URL,
  - and whether draft-PR creation is acceptable if no PR exists yet.

## Deliverables

- a walkthrough video plan or rendered artifact;
- output path and the primary generation or export command;
- short PR-ready copy describing what the video shows;
- any unresolved accuracy or asset limitations.

## Failure mode

- If the feature flow is still unstable, stop and return a capture plan rather than a misleading final artifact.
- If the source assets cannot be resolved, do not invent scenes.
- If the task is really a generic video-production request, route to the narrower neighboring skill instead of stretching this one.

## Philosophy

- The best feature video explains the real user flow with the least distraction.
- Accuracy matters more than flourish.
- A review artifact should be easy to share, regenerate, and update after feedback.

## Workflow

1. Confirm the feature scope and where the video will be used.
2. Choose the production path:
   - browser-record-and-upload for real app walkthroughs tied to a PR;
   - `stitch-remotion` for Stitch-sourced walkthroughs;
   - `remotion` for custom composition work;
   - direct recording plus `gh-workflow` packaging when the artifact already exists.
3. Capture or compose the minimal flow that proves the change.
4. Export the artifact and write the short summary or PR-ready note.
5. Verify the video still matches the current product behavior before signoff.

## Production paths

- Use the browser-record-and-upload path when the user wants a walkthrough of a running product flow and the output should land in a GitHub PR. This path uses `agent-browser`, `ffmpeg`, and `gh`, supports record-only fallback plus upload-only resume, and preserves the detailed auth/upload procedure in `references/browser-pr-walkthrough.md`.
- Use `stitch-remotion` when the source of truth is Stitch screens rather than a live app.
- Use `remotion` when a custom composed explainer is needed instead of a literal browser walkthrough.
- Use an existing artifact plus `gh-workflow` when the video already exists and only packaging or PR attachment is needed.

## Validation

- Verify the walkthrough covers the intended feature, not an adjacent flow.
- Verify the artifact exists at the reported output path.
- Verify overlays, captions, or notes do not misstate the product behavior.
- For PR upload workflows, verify the uploaded URL is a native `user-attachments/assets/` GitHub video URL before editing the PR body.

## Gotchas

- Feature videos get stale quickly after UI polish or copy changes; recheck the flow against the current build before posting.
- A PR-ready note is part of the deliverable here; do not stop at the video artifact if the user asked for review packaging.

## Anti-patterns

- Shipping a stale demo after the UI has changed.
- Overproducing a cinematic video when a short accurate walkthrough would do.
- Hiding missing product readiness behind editing polish.
- Treating PR-video upload as a generic browser task without preserving session, upload validation, and cleanup safeguards.

## References

- Browser walkthrough + GitHub PR upload: `references/browser-pr-walkthrough.md`

## See Also

| Skill | When to use together |
|---|---|
| [[stitch-remotion]] | Build a walkthrough from Stitch screens |
| [[remotion]] | Create or review a custom Remotion composition |
| [[gh-workflow]] | Attach the final artifact to a PR or delivery note |
| [[sora]] | Generate synthetic video only when the request is not tied to real product footage |

**Topic map:** [[content-publishing]]
