---
name: agent-browser
description: Use this skill to extract page state and automate web interactions with the agent-browser CLI (navigate, snapshot, click, fill, screenshot). Use this when you need deterministic browser automation or scraping via ref-based elements.
metadata:
  skill-type: product_verification
---

# Agent Browser

Use the `agent-browser` CLI for deterministic browser automation through accessibility snapshots and ref-based interaction.

## Standards snapshot (March 2026)
- Prefer snapshot-driven refs over brittle selectors.
- Re-snapshot after navigation or meaningful DOM changes.
- Keep browser actions observable: every click, fill, or wait should have a verification point.
- Use isolated sessions when parallel flows or risky state changes would interfere with each other.

## When to use
- Interacting with live web pages or forms through the CLI.
- Capturing screenshots, PDFs, or structured snapshots.
- Scraping or validating page state with deterministic steps.

## When not to use
- Browser tasks that require a different sanctioned browser automation surface.
- Long destructive flows against production systems.
- Generic browsing with no need for deterministic automation or snapshots.

## Required inputs
- Target URL or session context.
- Intended actions such as open, click, fill, wait, or extract.
- Desired output artifacts such as text, screenshots, PDFs, or JSON snapshots.

## Deliverables
- Verified action results and page-state evidence.
- Saved artifacts when requested.
- Extracted content or next-step instructions based on snapshot evidence.
- If requested, a structured status report with a `schema_version` field.

## Philosophy
- Accessibility-first refs are the default because they are more stable than ad hoc selectors.
- Browser automation should be incremental and verifiable.
- Minimal sequences with checkpoints are safer than long speculative chains.

## Constraints
- Redact secrets, tokens, session identifiers, and private URLs in logs and outputs by default.
- Avoid interacting with sensitive accounts or destructive controls without explicit approval.
- Reconfirm page state after any action that may have changed the DOM.

## Workflow
1. Verify `agent-browser` is installed and usable.
2. Open the target URL or attach to the named session.
3. Run `snapshot -i`, preferably with `--json` when parsing matters.
4. Interact using refs such as `@e1`, `@e2`, and re-snapshot after changes.
5. Save screenshots, PDFs, or extracted text when requested.
6. Stop at the first failed step and inspect the updated snapshot before continuing.

## Core pattern
1. `open`
2. `snapshot -i`
3. `click` or `fill` using refs
4. `wait` if needed
5. `snapshot -i` again

## Tooling and references
- Use `agent-browser` as the primary operator surface.
- Prefer `snapshot -i --json` for parseable automation steps.
- Use session isolation when parallel browser flows are needed.
- Reference files:
  - `references/contract.yaml`
  - `references/evals.yaml`
  - `references/task-profile.json`
- Use assets only when the task benefits from bundled browser skill materials in `assets/`.

## Validation
- Verify installation before use.
- Verify each meaningful step with a fresh snapshot or expected page-state change.
- Verify saved artifacts exist when requested.
- Fail fast at the first broken browser step.

## Anti-patterns
- Clicking without a fresh snapshot after navigation.
- Using brittle selectors when refs are available.
- Running long sequences with no verification checkpoints.
- Treating a changed DOM like a stable continuation of the previous step.

## Examples
- Open this site, search for a result, and capture the page state.
- Use refs to fill this form and save a screenshot of the confirmation screen.
- Extract the visible text from this page using snapshot evidence.

## See Also

| Skill | When to use together |
|---|---|
| [[playwright-interactive]] | Use for iterative UI automation when Playwright is better |
| [[ui-visual-regression]] | Capture snapshots with agent-browser for regression checks |
| [[fixing-accessibility]] | Probe ARIA and keyboard behaviour via browser automation |
| [[agentation]] | Wire agent-browser actions into Agentation self-driving mode |
| [[atlas]] | Use Atlas for macOS ChatGPT app control vs agent-browser for web |

**Topic map:** [[frontend-ui]]

## Remember
The snapshot is the source of truth. If you have not re-read the page state, you are guessing.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## Failure mode
- If page state, selectors, or browser session prerequisites are missing, stop, describe the failing step, and fall back to a narrower inspection or snapshot flow before automating further.
