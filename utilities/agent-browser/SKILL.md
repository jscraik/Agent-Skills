---
name: agent-browser
description: "Inspect and automate browser pages deterministically with the `agent-browser` CLI. Use when the user wants ref-based navigation, extraction, clicks, fills, or screenshots, not general browsing advice."
metadata:
  skill-type: product_verification

---

# Agent Browser

Use the `agent-browser` CLI for deterministic browser automation through accessibility snapshots and ref-based interaction.

Merged with preserved upstream references and templates from `EveryInc/compound-engineering-plugin` at pinned ref `0fdc25a36cabea4ce9e2ae47ff69c1a9a2de8f0b`; see [`artifacts/agent-browser-merge-import-2026-03-23.txt`](../../artifacts/agent-browser-merge-import-2026-03-23.txt) for provenance and hashes.

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
- Explicit signposts into deep-dive references or templates when the task needs more than the core snapshot workflow.

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
- Deep-dive references:
  - `references/commands.md` — read when you need full command coverage, flags, or less common subcommands.
  - `references/authentication.md` — read when login, saved state, OAuth, 2FA, or credential handling matters.
  - `references/session-management.md` — read when using named sessions, persistence, or concurrent browser workflows.
  - `references/snapshot-refs.md` — read when refs invalidate unexpectedly or DOM changes make interactions flaky.
  - `references/profiling.md` — read when the task is performance analysis or Chrome DevTools profiling.
  - `references/proxy-support.md` — read when traffic must go through a proxy or geo-routed network path.
  - `references/video-recording.md` — read when you need demo capture or recorded debugging evidence.
- Ready-to-use templates:
  - `templates/form-automation.sh` — use for form flows with validation checkpoints.
  - `templates/authenticated-session.sh` — use for login-once and reuse-state workflows.
  - `templates/capture-workflow.sh` — use for extraction and screenshot capture runs.
- Use assets only when the task benefits from bundled browser skill materials in `assets/`.

## Reference usage contract
- Treat this wrapper as the routing layer, not the full browser doctrine.
- Keep the core snapshot workflow here, but preserve richer command, auth, and session guidance in `references/`.
- When advice depends on nuanced behavior, cite the specific reference or template instead of compressing it into generic instructions.
- If you import or improve this skill again, preserve high-value browser context by signposting it rather than deleting it for brevity.

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
- Authentication or session nuance goes missing -> wrapper stayed short but references were not consulted -> open `references/authentication.md` or `references/session-management.md` before improvising a login flow.
- Browser refs stop working after navigation -> stale snapshot state -> re-run `snapshot -i` and use `references/snapshot-refs.md` if the invalidation pattern is unclear.

## Failure mode
- If page state, selectors, or browser session prerequisites are missing, stop, describe the failing step, and fall back to a narrower inspection or snapshot flow before automating further.
