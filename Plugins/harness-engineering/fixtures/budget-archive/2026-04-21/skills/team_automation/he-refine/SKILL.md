---
name: he-refine
description: Refine Harness Engineering artifacts, plans, specs, or work into clearer action plans. Use when users ask for tightening, simplification, or lifecycle repair.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Philosophy

- Refine through tight feedback loops, not speculative redesign.
- Keep polish work measurable and bounded to user-visible outcomes.
- Keep the dev-server and browser loop stable so each refinement maps to live behavior the user can verify quickly.

## When to use

- Use when implementation is functional but needs quality polish before final review.
- Use for browser-first refinement loops with explicit iteration gates.
- Use when the fastest path is to run the feature, inspect it in the browser, and iterate directly on what the user says feels off.

## Inputs

- Request, artifacts, repo context, and linked Linear issues.

## Outputs

- `schema_version: 1` when structured; result, validation, blockers, and next Harness Engineering action.

## Procedure

1. Start from the correct branch or PR context and block if the current branch is a protected default branch.
2. Resolve dev-server startup from launch config first, then fall back to project-type and port detection when needed.
3. Start and probe the dev server before claiming readiness.
4. Open the feature in the browser and iterate in small loops: one user-noted issue, one focused fix, one quick re-check.
5. Report resolved gaps, remaining blockers, and the safest next stage.

## Validation

- Ensure each refinement maps to a measurable user-facing improvement.
- Ensure regression risk is checked before stage exit.
- Ensure branch, server, and browser readiness are verified before edits depend on live feedback.
- Ensure each iteration stays focused on explicit user feedback rather than bundled polish churn.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not broaden refinements into unrelated feature work.
- Do not polish directly on `main` or `master`.
- Do not skip server-health probing before asking the user to browse and react.
- Apply the context-disposition policy: move important still-valid context to references and index it when meaningful; intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.

## Anti-patterns

- Cosmetic churn without acceptance criteria.
- Iterating without verifying whether user-facing quality improved.
- Making multiple unrelated fixes in one loop without user confirmation.
- Treating refinement as a replacement for broader implementation or planning stages.

## Full Context

- Assets: [icon-small.png](./assets/icon-small.png), [icon-large.png](./assets/icon-large.png)

## Examples

- "Can you inspect this plan, tighten it into clear actions, and remove ambiguity before the work stage?"
- "Help me refine this UI implementation by running it, checking the page, and fixing one visible gap at a time."
- "This spec is mostly right but fuzzy. Make the acceptance criteria measurable without expanding scope."
