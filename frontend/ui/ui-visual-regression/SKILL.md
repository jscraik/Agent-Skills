---
name: ui-visual-regression
description: "Run a minimal, repeatable UI visual regression pipeline (Storybook build + Playwright capture + Argos diff) and iterate on targeted UI fixes until visual diffs pass. If design-system guidance, tokens, or component standards are needed, consult the skill.. Use when Investigating visual diffs in Storybook/Argos pipelines.."
---

# Ui Visual Regression

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md


## Overview

Run a minimal, repeatable UI visual regression pipeline (Storybook build + Playwright capture + Argos diff) and iterate on targeted UI fixes until visual diffs pass.
If design-system guidance, tokens, or component standards are needed, consult the `frontend-design` skill.

## When to use
- Investigating visual diffs in Storybook/Argos pipelines.
- Stabilizing snapshot tests and fixing layout regressions.
- Reviewing whether diffs are expected vs unintended.

## Required response headings
Every response must include these headings:
- `## When to use`
- `## Inputs`
- `## Outputs`

## Failure-mode template (out of scope)
Use this exact structure when the request is out of scope:

```md
## When to use
- This skill applies to UI visual regression workflows. The current request is out of scope.

## Outputs
- None (out of scope).

## Inputs
- None (out of scope).
```

## Philosophy
- Prefer determinism over speed; stabilize before fixing.
- Treat diffs as signals to verify intent, not defects by default.
- Minimize scope of fixes to preserve design consistency.
- Explain the why behind accepting or rejecting a diff.

## Guiding questions
- What changed, and is the change expected?
- Is the diff caused by data, timing, or layout instability?
- What is the smallest fix to restore intended visuals?
- How will we verify fixes across viewports and themes?
- Why is this evidence sufficient to update the baseline?

## Dependencies

- `frontend-design` for design tokens, accessibility requirements, and component standards.

## Workflow Decision Tree

- If Storybook build or story enumeration fails, fix build or story metadata first, then retry.
- If snapshots are flaky, stabilize test environment (fonts, animations, timing, viewport) before fixing UI.
- If Argos diffs show real regressions or expected changes, propose targeted code edits, re-run, and only accept when diffs are clean.

## Step 1: Build and Enumerate Stories

1. Use the repo's Storybook scripts if present (preferred).
2. If missing, use conventional defaults (verify package scripts first):
   - Build: `pnpm storybook:build` or `npm run storybook:build`
   - Static output: `storybook-static/`
3. Enumerate stories (use Storybook CLI, Playwright tests, or Storybook test runner depending on repo).

**Stability checklist (before capture):**
- Pin viewport sizes (desktop + small-screen).
- Disable animations/transitions in test mode.
- Ensure deterministic fonts (local or preloaded).
- Set timezone/locale.
- Avoid network flakiness (mock or fixture data).

If you need Argos-specific setup details, baseline build behavior, or diff algorithm notes, read `references/argos-quickstart-notes.md`.

## Step 2: Run Playwright Against Stories

1. Run the repo's Playwright scripts if defined (preferred).
2. Capture artifacts for debugging:
   - Screenshots (required)
   - Traces (recommended)
   - Video (optional)

**Notes:**
- Prefer headless runs in CI with the same viewport matrix used by Argos.
- Keep capture settings consistent across runs (DPR, viewport, theme).
- Stabilization checklist (Playwright):
  - Wait for fonts to load before screenshot.
  - Disable or freeze animations/transitions.
  - Await network idle or mock API responses.
  - Ensure layout is stable (no pending async rendering).

## Step 3: Upload to Argos and Review Diffs

1. Upload the Storybook build or Playwright snapshots per repo config.
2. Review Argos diff results and PR status checks.
3. Classify diffs:
   - **Expected** (new feature/update) -> update baseline only after code is correct.
   - **Unexpected** (regression) -> fix UI and re-run.

## Step 4: Propose Targeted Fixes

- Focus on minimal changes: CSS/layout, spacing, typography, tokens.
- Avoid broad refactors unless necessary to address the regression.
- Re-run the pipeline after each set of changes.
- If diffs indicate design-system violations, switch to the `frontend-design` skill to align on tokens and component standards before making further edits.

Design-system violation signals:
- Color/contrast shifts that break token usage or accessibility guidance.
- Typography drift (font family, size scale, line height, letter spacing).
- Spacing inconsistencies vs token scale.
- Component variant mismatch (wrong size/state/intent).

## Step 5: Accept Only When Clean

Acceptance criteria:
- Storybook build succeeds.
- Playwright capture completes without flake.
- Argos diffs are clean or explicitly approved as expected changes.

## Variation rules
- Vary viewport and theme coverage based on component risk.
- Use different stabilization tactics for animation vs data-driven flake.
- Prefer different diff review depth for new components vs regressions.

## Empowerment principles
- Empower reviewers with clear diff evidence and rationale.
- Empower teams to choose between patching or updating baselines when justified.

## Anti-patterns to avoid
- Updating baselines to hide regressions.
- Ignoring flake root causes and re-running until green.
- Making broad visual refactors for a single diff.

## Constraints / Safety
- Redact secrets/PII by default.
- Do not approve diffs without confirming intent.
- Avoid updating baselines when underlying data or layout is unstable.
- Keep fixes minimal unless a larger refactor is explicitly requested.

## Example prompts
- “Run the visual regression pipeline and fix the Argos diffs.”
- “Stabilize flaky Storybook snapshots.”
- “Review and classify these UI diffs as expected or regressions.”

## Evidence to Include in Final Response

- Commands run and key outputs (build, tests, Argos upload).
- Summary of diffs and reasoning for acceptance.
- Any deviations or experimental steps with risk + mitigation.

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Resources

Create resources only if the repo needs standardized helpers.

### scripts/
Place optional helpers here (e.g., `run_storybook_visuals.sh`, `argos_upload.sh`) if the project lacks stable scripts.

### references/
Use for repo-specific guidance (CI requirements, Storybook/Argos conventions, viewport matrix).
See `references/argos-quickstart-notes.md` for the user-provided Argos quickstart notes.

### assets/
Optional templates for consistent snapshots or fixture assets.

## Inputs
- User request details and any relevant files/links.


## Outputs
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.


## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.
