# Browser PR Walkthrough

Read when: the user wants a real product walkthrough recorded from a running app and uploaded into a GitHub PR as a native inline video.

Imported from the upstream `feature-video` skill in `EveryInc/compound-engineering-plugin` commit `847ce3f156a5cdf75667d9802e95d68e6b3c53a4`, adapted from the donor's single-file workflow into the local `feature-video` wrapper.

## Purpose

Record browser interactions that demonstrate a feature, encode them into an MP4, upload the file natively to GitHub, and place the resulting inline video URL into a PR description or review surface.

## Supported modes

### Normal record-and-upload

Use when:
- a live app is available
- the walkthrough should be recorded now
- the result should end up on a PR

### Record-only fallback

Use when:
- no PR exists yet
- the user wants to capture the walkthrough now and upload later

Behavior:
- still record screenshots and encode the MP4
- skip upload and PR update
- return the local video path and run ID

### Upload-only resume

Use when:
- an MP4 already exists
- only the GitHub upload and PR update steps remain

Behavior:
- skip recording and encoding
- resolve the PR from the current branch or explicit input
- continue directly into auth, upload, and PR update

## Argument shape

Interpret the browser PR walkthrough inputs as:
- first argument: PR number, `current`, or path to an existing `.mp4`
- second argument: optional base URL, default `http://localhost:3000`

If the first argument is an existing `.mp4`, treat the run as upload-only resume and skip recording.

## Prerequisites

- a running local or staging application
- `agent-browser`
- `ffmpeg`
- `gh`
- a git repository on a feature branch
- GitHub auth that can open and edit the relevant PR

Fail early by checking tools before recording so work is not lost halfway through the flow.

## High-level flow

1. Resolve the PR target or determine whether record-only mode is needed.
2. Verify required tools.
3. Gather context from the PR or branch diff to understand what changed.
4. Propose and confirm a short shot list before recording.
5. Capture ordered screenshots with `agent-browser`.
6. Encode the screenshots into an MP4 with `ffmpeg`.
7. Authenticate to GitHub in a persisted browser session if needed.
8. Upload the video through the PR comment form's hidden file input.
9. Extract and validate the resulting `user-attachments/assets/` URL.
10. Update the PR description with a `## Demo` section.
11. Clean up only the current run's scratch directory, and ask before removing files.

## PR resolution and fallback behavior

- Accept an explicit PR number.
- Accept `current` and resolve the PR from the current branch.
- If no PR exists, ask whether to:
  1. create a draft PR and continue
  2. record only and upload later
  3. cancel

If upload-only resume is requested, treat the first argument as an existing `.mp4` path and skip recording.

## Planning the walkthrough

Create a short shot list before capture:
- opening shot
- navigation into the feature
- core interaction
- optional edge case or validation state
- success state

Keep the demo brief and focused. A short accurate walkthrough is more useful than a long cinematic clip.

## Capture rules

- Generate a per-run ID, such as a timestamp.
- Write screenshots and videos into a run-scoped scratch directory like:
  - `.context/compound-engineering/feature-video/[RUN_ID]/screenshots/`
  - `.context/compound-engineering/feature-video/[RUN_ID]/videos/`
- Number screenshots sequentially so the encode order is deterministic.
- Use concrete paths once the run ID is known rather than relying on shell variables across isolated command blocks.

## Encoding rules

Use `ffmpeg` to stitch screenshots into an MP4.

Preserve these goals:
- broad player compatibility
- bounded size
- predictable ordering

Typical defaults:
- H.264
- `yuv420p`
- width constrained to a shareable review format
- 2 seconds per frame unless the flow needs faster pacing

If the file is too large, reduce framerate, resolution, or quality before retrying upload.

## GitHub auth and upload

Use a persisted Chrome-backed `agent-browser` session for GitHub auth.

Recommended approach:
- close any stale browser session
- open a headed GitHub login page with a named session if auth is missing
- let the user complete login manually
- verify the authenticated session on a settings/profile page

Then:
- open the PR page
- save any draft textarea content before upload
- upload the video through the PR form's hidden file input
- wait for GitHub processing
- read the textarea value to extract the uploaded video URL

Preferred selectors from the donor workflow:
- file input: `#fc-new_comment_field`
- textarea: `#new_comment_field`

## Upload validation

Do not edit the PR body until the extracted value contains a native GitHub attachment URL with:
- `user-attachments/assets/`

If upload validation fails:
1. check whether the session redirected to login
2. re-auth if needed
3. wait and retry once in case GitHub is still processing
4. if it still fails, stop and report the local video path for manual upload

After extracting the URL:
- restore the user's original textarea content
- then edit the PR body through `gh`

Textarea restoration detail:
- assign the saved content back as a direct JavaScript string literal
- do not rely on `JSON.parse(...)` for the restored textarea body
- if the saved textarea was empty, restore `""`

## PR update shape

Use or replace a compact section like:

```md
## Demo

https://github.com/user-attachments/assets/[uuid]

*Automated video walkthrough*
```

## Cleanup rules

- Ask before deleting temporary files.
- If upload succeeded, it is safe to remove the current run directory.
- If upload failed or the run is record-only, remove screenshots if desired but preserve the MP4.
- Never delete other runs' scratch directories as part of cleanup.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| `ffmpeg` missing | tool not installed | install `ffmpeg` before capture |
| `agent-browser` missing | tool not installed | load `agent-browser` setup guidance |
| `gh pr view` fails | no PR on current branch | create a draft PR or switch to record-only |
| upload textarea stays empty | expired auth or slow processing | verify session, then wait and retry |
| upload redirects to login | GitHub session expired | re-run headed login flow |
| video too large | encoding too heavy | reduce framerate, resolution, or quality |
| upload URL shape is wrong | selector or upload flow drifted | inspect the current PR page and revalidate selectors |

## Local adaptation notes

The local `feature-video` skill remains the concise router and delivery wrapper.

This reference preserves the upstream concrete real-app PR-demo workflow so the wrapper can:
- route to it explicitly when needed
- keep the operational detail available without bloating `SKILL.md`
- preserve resume, auth, upload-validation, and cleanup safeguards
