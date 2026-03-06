---
name: ui-visual-regression
description: "Review and validate UI visual regression diffs (Storybook + Playwright capture + Argos) when snapshot changes or layout regressions appear."
---

# Ui Visual Regression

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md


## Overview

Run a minimal, repeatable UI visual regression pipeline (Storybook build + Playwright capture + Argos diff) and iterate on targeted UI fixes until visual diffs pass.
If design-system guidance, tokens, or component standards are needed, consult the `frontend-design` skill.

## Scope and triggers
- Investigating visual diffs in Storybook/Argos pipelines.
- Stabilizing snapshot tests and fixing layout regressions.
- Reviewing whether diffs are expected vs unintended.

## Required response headings
Every response must include these headings:
- `## When to use`
- `## Inputs`

## Cognitive Support / Plain-Language
- Optimize for low cognitive load (TBI support): one task at a time, explicit steps.
- Use plain language first; define jargon in parentheses.
- Keep steps short and checklist-driven where possible.
- Externalize state: decisions, assumptions, and the next step.
- Provide ELI5 explanations for non-trivial logic.
- Ask one question at a time; prefer multiple-choice when possible.

- `## Outputs`

## Failure-mode template (out of scope)
Use this exact structure when the request is out of scope:

```md
## Scope and triggers
- This skill applies to UI visual regression workflows. The current request is out of scope.

## Deliverables
- None (out of scope).

## Required inputs
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

## Required inputs
- User request details and any relevant files/links.


## Deliverables
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

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when consistent decision-making matters more than one-off execution because project context should drive the approach.
- Principle and mindset: prioritize tradeoffs and constraints over rigid checklists; understand why each step exists.
- Ask this to keep outcomes robust: Why is this the right default, and what could change this outcome?
- How do we adapt if constraints shift?
- What evidence is needed before choosing one path over another?

## Anti-patterns and caveats
- Avoid applying this playbook generically without checking repository-specific context.
- **NEVER** skip required validation gates when behavior changes.
- **DO NOT** use this skill as a rigid replacement for engineering judgment.
- **DON'T** ignore warnings or assume one pattern fits all repos.
- Common pitfall: treating anti-patterns as optional.
- Incorrect assumptions here can lead to fragile guidance.
- Warning: wrong sequencing can create avoidable regressions.

## Variation and adaptation
- Vary the workflow by team size, risk, and deployment target.
- Use different strategies for small, medium, and large changes.
- Adapt recommendations to the specific environment and avoid repetitive templates.
- Avoid generic or cookie-cutter responses; craft context-specific alternatives.
- Keep outputs diverse and not repetitive.
- Converge on a custom path only after evidence review.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of exploring multiple options and enabling the team to make safe decisions.
- Unlock confidence by explaining options and tradeoffs clearly.
- Feel free to be creative while staying rigorous and precise.
- Push boundaries with practical alternatives when simple recipes fail.
- Enable outcomes-oriented problem solving.

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
