---
name: ui-visual-regression
description: "Review and validate UI visual regression diffs (Storybook + Playwright capture + Argos) when snapshot changes or layout regressions appear."
metadata:
  skill-type: product_verification
---

# UI Visual Regression

Run a deterministic visual regression loop so we can separate expected UI change from actual layout or styling regressions.

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
- Prefer deterministic capture conditions over repeated reruns.
- Treat diffs as evidence to classify, not defects to auto-reject.
- Keep fixes minimal and aligned with the design system already in use.
- Only update a baseline after intent and implementation are both verified.

## When to use
- Storybook, Playwright, or Argos visual diffs need investigation.
- Snapshot tests are flaky and need stabilization.
- A PR introduces UI changes and the team needs help deciding whether diffs are expected or regressive.

## Required inputs
- The failing or changing visual regression surface:
  - Storybook build;
  - Playwright capture;
  - Argos diff;
  - or screenshots and traces from the pipeline.
- Repo commands or the existing snapshot workflow if known.
- Whether the expected outcome is “fix the regression” or “classify and justify the diff.”

## Deliverables
- A concise classification of the visual diffs.
- The minimal stabilization or UI fix plan needed next.
- Evidence from build, capture, and diff review rather than guesswork.

## Philosophy
- Stabilize before patching.
- Prefer the smallest fix that restores intended visuals.
- Make acceptance or rejection of a diff traceable to evidence.

## Failure mode
- If the issue is broader design-system work rather than regression review, route to the design-system or frontend design skill.
- If the build or story inventory is broken, stop at pipeline recovery before making UI claims.
- If the user only wants creative redesign, this is the wrong skill.

## Constraints
- Redact secrets, tokens, and private artifact URLs by default in shared outputs.
- Do not bless a baseline update without confirming design intent.
- Keep fixes scoped to the regression unless the user explicitly asks for broader refactoring.

## Workflow
1. Verify the pipeline stage that is failing:
   - Storybook build;
   - story enumeration;
   - Playwright capture;
   - Argos upload or diff review.
2. Stabilize capture conditions before interpreting diffs:
   - viewport;
   - fonts;
   - animation state;
   - locale and timezone;
   - mocked or idle data.
3. Review the diffs and classify them as:
   - expected change;
   - unexpected regression;
   - flaky or nondeterministic noise.
4. Fix the smallest likely cause:
   - layout;
   - spacing;
   - typography;
   - token drift;
   - async timing.
5. Re-run the same pipeline slice and only approve once the evidence is clean.

## Anti-patterns
- Updating baselines to hide a regression.
- Re-running flaky captures until green without addressing the instability.
- Making a broad visual rewrite for a narrow diff.

## Validation
- Fail fast: stop at the first broken build, missing story, or unstable capture prerequisite.
- Confirm Storybook build and capture both succeed before interpreting Argos output.
- Verify the final state is either diff-clean or explicitly justified as an expected change.

## References
- Contract: `references/contract.yaml`
- Evals: `references/evals.yaml`
- Argos notes: `references/argos-quickstart-notes.md`

## See Also

| Skill | When to use together |
|---|---|
| [[playwright-interactive]] | Capture screenshots for regression via Playwright |
| [[baseline-ui]] | Run baseline UI checks alongside visual regression |
| [[agent-browser]] | Use agent-browser snapshots as regression inputs |
| [[stitch-react-components]] | Catch visual regressions after Stitch-to-React conversion |

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
