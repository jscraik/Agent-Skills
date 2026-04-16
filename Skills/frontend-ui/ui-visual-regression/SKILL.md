---
name: ui-visual-regression
description: Review and validate Storybook, Playwright, and Argos visual regression diffs. Use when the user wants snapshot-change triage or layout regression analysis, not broad frontend QA.
metadata:
  skill-type: product_verification
---

# UI Visual Regression

Run a deterministic visual regression loop so we can separate expected UI change from actual layout or styling regressions.

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
- Prefer deterministic capture conditions over repeated reruns.
- Treat diffs as evidence to classify, not defects to auto-reject.
- Treat React 19 and Next.js 16 rendering behavior as the baseline when classifying hydration, layout, or style regressions in those stacks.
- Treat Tailwind CSS v4 token usage as the baseline when triaging utility drift versus intended visual changes.
- Hold acceptance to WCAG 2.2 AA expectations for focus visibility, contrast, and keyboard-operable states in changed surfaces.
- Keep fixes minimal and aligned with the design system already in use.
- Only update a baseline after intent and implementation are both verified.

## Design-system integration
- Apply `frontend/ui/Infrastructure/references/design-system-integration-contract.md` when classifying typography, spacing, iconography, and token drift.
- Route shared token architecture and design-language decisions to `design-system` after regression triage is complete.
- Use `frontend/ui/Infrastructure/references/skill-routing-matrix-2026.md` when regression asks broaden into redesign or implementation ownership decisions.

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
- Use a clear framework: isolate capture noise first, then classify intent versus regression.
- Make tradeoff decisions explicit so we understand why deterministic capture beats quick baseline churn.
- Ask: "Is this diff showing product intent, or is it exposing capture noise?"
- Ask: "What is the minimum reliable change that makes this lane trustworthy again?"
- Ask: "Why would we accept this baseline if we cannot explain the visual delta with evidence?"

## Variation
- Adapt the investigation depth to risk:
  - for one-story cosmetic drift, classify and fix only that story lane;
  - for multi-surface drift, isolate one deterministic repro before broad edits;
  - for release-blocking regressions, prioritize rollback-safe stabilization before visual polish.
- Vary capture hardening by stack:
  - Storybook-first repos: lock stories, fonts, and viewport before Argos triage;
  - Playwright-first repos: lock navigation timing and fixture state before baseline decisions.
- Keep scope narrow by default: fix one failing lane, re-run, then expand only if evidence still spreads.

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
- Avoid updating baselines to hide a regression.
- Do not re-run flaky captures until green without addressing the instability.
- Never make a broad visual rewrite for a narrow diff.
- Anti-pattern warning: treating every diff as a design failure without checking deterministic capture conditions first is the wrong triage approach.
- Merging screenshot updates without an explicit reasoned classification for each changed surface is incorrect regression governance.

## Validation
- Fail fast: stop at the first broken build, missing story, or unstable capture prerequisite.
- Confirm Storybook build and capture both succeed before interpreting Argos output.
- Verify the final state is either diff-clean or explicitly justified as an expected change.
- Confirm any visual-literal, typography, spacing, or icon corrections align with `frontend/ui/Infrastructure/references/design-system-integration-contract.md`.

## Examples
- "Argos shows spacing drift in only the billing card. Is this token drift or a flaky snapshot?"
- "Our Playwright screenshots fail only in CI after font loading. Help me stabilize capture settings before we touch CSS."
- "Storybook snapshots changed for all button states after a refactor. Classify what is expected and what should block merge."
- "I need a review note explaining why two diffs are intentional so we can approve baseline updates confidently."

## References
- Contract: `Infrastructure/references/contract.yaml`
- Evals: `Infrastructure/references/evals.yaml`
- Argos notes: `Infrastructure/references/argos-quickstart-notes.md`
- Asset preview: `assets/ui-visual-regression.png`

## See Also

| Skill | When to use together |
|---|---|
| [[playwright-interactive]] | Capture screenshots for regression via Playwright |
| [[baseline-ui]] | Run baseline UI checks alongside visual regression |
| [[design-system]] | Resolve confirmed token, typography, spacing, or icon drift at the system layer |
| [[agent-browser]] | Use agent-browser snapshots as regression inputs |
| [[react-components]] | Catch visual regressions after Stitch-to-React conversion |

**Topic map:** [[frontend-ui]]

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 Skills/skill-builder/Infrastructure/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
