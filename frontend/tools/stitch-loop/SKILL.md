---
name: stitch-loop
description: Run iterative autonomous website-building loops with Stitch using a baton file and multi-pass page generation. Use when the user wants Stitch to keep building or refining a site over repeated passes, not one-shot UI extraction.
allowed-tools:
  - "stitch*:*"
  - "chrome*:*"
  - "Read"
  - "Write"
  - "Bash"
metadata:
  skill-type: scaffolding_templates
---

# Stitch Loop

Run a baton-driven Stitch website build loop where each pass produces one coherent page and a valid next step.

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Failure mode](#failure-mode)
- [Constraints](#constraints)
- [Workflow](#workflow)
- [Anti-patterns](#anti-patterns)
- [Validation](#validation)
- [References](#references)

## Standards snapshot
- Each iteration must end with a valid refreshed baton.
- Preserve site continuity by consulting `SITE.md` and `DESIGN.md` before generation.
- Prefer one page per pass and keep integration deterministic.
- Verify visual output when the browser toolchain is available.

## When to use
- The user wants iterative autonomous website building with Stitch.
- The workflow is baton-driven through `next-prompt.md`.
- Each run should generate one page, integrate it, and queue the next task.

## Required inputs
- A valid `next-prompt.md` baton with a `page` field.
- Project context files such as `SITE.md`, `DESIGN.md`, and optionally `stitch.json`.
- Access to Stitch MCP tools and optional browser verification tools.

## Deliverables
- Integrated page artifact for the current baton target.
- Updated state docs such as `SITE.md` and the next baton.
- Optional verification screenshots or notes when browser checks run.

## Philosophy
- Small, handoff-ready iterations scale better than broad autonomous sweeps.
- Baton continuity matters as much as page output.
- Generated pages should inherit the project’s design system rather than drifting per run.

## Failure mode
- If the baton is missing, malformed, or lacks a target page, stop before generation.
- If required context files are absent, pause and report the missing project state.
- If the user wants one-off Stitch generation rather than iterative baton flow, use a more direct Stitch workflow instead.

## Constraints
- Redact secrets and sensitive data by default in prompts, logs, and exported notes.
- Do not skip baton refresh; loop continuity is mandatory.
- Do not regenerate sitemap-complete pages unless explicitly asked.

## Workflow
1. Read `next-prompt.md` and resolve the current target page.
2. Read `SITE.md` and `DESIGN.md` before generating anything.
3. Confirm the target page is not already complete in the sitemap.
4. Generate the page with Stitch and retrieve the resulting HTML and screenshot assets.
5. Integrate the page into the site structure and wire navigation.
6. Update `SITE.md` and write the next valid baton before finishing.
7. If browser verification is available, compare the integrated page against the generated output and capture evidence.

## Anti-patterns
- Ending an iteration without a valid new baton.
- Recreating pages that already exist in the sitemap.
- Leaving placeholder navigation links after integration.

## Validation
- Fail fast: stop at the first invalid baton, missing context file, or broken Stitch generation step.
- Verify the current page was integrated into the expected site location.
- Verify `SITE.md` and `next-prompt.md` were both updated.
- If browser verification runs, confirm the rendered page is close enough to the generated reference to continue the loop safely.

## References
- Contract: `references/contract.yaml`
- Evals: `references/evals.yaml`
- Baton file: `next-prompt.md`
- Project state: `SITE.md`, `DESIGN.md`, `stitch.json`

## See Also

| Skill | When to use together |
|---|---|
| [[stitch-react-components]] | Convert Stitch outputs to React components |
| [[stitch-remotion]] | Turn Stitch screens into narrated video walkthroughs |
| [[ui-cloner]] | Clone a UI design into Stitch for iterative generation |
| [[frontend-ui-design]] | Review and polish Stitch-generated UI |

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
