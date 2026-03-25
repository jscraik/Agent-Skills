---
name: test-browser
description: Run or plan browser-based verification for changed web surfaces using sanctioned browser automation tools. Use when a user needs deterministic QA for routes, flows, or PR scope instead of ad hoc manual browsing.
metadata:
  skill-type: product_verification
---

# Test Browser

## Table of Contents
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Philosophy](#philosophy)
- [Workflow](#workflow)
- [Validation](#validation)
- [References](#references)
- [Gotchas](#gotchas)
- [Anti-patterns](#anti-patterns)
- [See also](#see-also)

## When to use

Use this skill when:
- a web UI change needs functional browser verification;
- a PR or branch affects routes, forms, navigation, or visible interaction flows;
- you need a minimal QA matrix tied to the changed surface.

Do not use this skill when:
- a static code review is enough;
- the task is pure scraping with no QA goal;
- the environment cannot run browser automation and the user only wants implementation work.

## Required inputs

- target repo path or live URL;
- one of:
  - PR number,
  - branch name,
  - changed route list, or
  - explicit flow to verify;
- whether the goal is:
  - functional QA,
  - visual QA,
  - or both.

## Deliverables

- a scoped browser verification plan or executed QA run;
- route or flow coverage tied to the changed surface;
- screenshots, notes, or failure evidence when relevant;
- next actions for any failing step.

## Failure mode

- If the changed surface cannot be identified, stop and ask for scope rather than testing random routes.
- If the app cannot be launched or reached, report the first failing gate and the smallest unblock step.
- If browser tooling is unavailable, return a manual QA checklist instead of claiming test completion.

## Philosophy

- Browser QA should follow changed-user-surface scope, not generic click-around behavior.
- Minimal high-signal coverage beats wide shallow testing.
- Use the most deterministic automation surface available for the target app.

## Workflow

1. Identify the affected browser surface from the PR, branch, or user description.
2. Choose the operator surface:
   - `agent-browser` for deterministic live-page interaction or extraction, especially when the user wants a PR/branch-driven route sweep or a reproducible CLI browser run;
   - `playwright-interactive` for local iterative QA with persistent state;
   - `ui-visual-regression` when snapshot diffs are the primary signal.
3. Turn the changed surface into a small QA matrix:
   - entry route;
   - primary action;
   - expected result;
   - regression check.
4. If `agent-browser` is the chosen surface and the run needs concrete browser-ops detail such as install checks, headed versus headless selection, route derivation from PR or branch diff, dev-server port detection, human verification pauses, or failure-to-todo handling, open `references/agent-browser-runbook.md`.
5. Execute the checks or produce the exact next commands if execution is blocked.
6. Summarize pass/fail status with evidence.

## Validation

- Verify every claimed pass has an observable check.
- Verify every failure names the exact step, route, and expected behavior.
- Verify saved artifacts exist when screenshots or captures are promised.
- Verify the chosen browser operator matches the requested environment instead of defaulting blindly to one tool.

## References

- `references/agent-browser-runbook.md`

## Gotchas

- PR scope often understates browser impact when shared layouts, auth gates, or form components were touched indirectly.
- A passing local browser flow is not enough if the requested environment was a live or review deployment.
- A deterministic `agent-browser` runbook can be the right default for changed-route QA, but it should not erase the local skill's broader routing to `playwright-interactive` or `ui-visual-regression`.

## Anti-patterns

- Testing unrelated routes because they are easy to reach.
- Running long brittle browser sequences without intermediate checkpoints.
- Claiming “looks good” without route-specific evidence.

## See Also

| Skill | When to use together |
|---|---|
| [[agent-browser]] | Deterministic live-page interaction using snapshot refs |
| [[playwright-interactive]] | Persistent local browser QA for iterative debugging |
| [[ui-visual-regression]] | Snapshot or layout diff validation |
| [[fixing-accessibility]] | Pair route-level verification with accessibility checks on interactive surfaces |

**Topic map:** [[frontend-ui]]
