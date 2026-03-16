---
name: playwright-interactive
description: Use a persistent Playwright session through `js_repl` to debug local web or Electron apps without restarting the browser on every step. Use when you need iterative UI automation, visual QA, or Electron inspection in the current workspace.
---

# Playwright Interactive

## Table of Contents
- [When to use](#when-to-use)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Philosophy](#philosophy)
- [Preflight](#preflight)
- [Workflow](#workflow)
- [Validation](#validation)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Resources](#resources)
- [Examples](#examples)

## When to use

Use this skill when:
- a local web UI needs iterative browser debugging with persistent state;
- an Electron app needs runtime inspection through Playwright's Electron launcher;
- you need repeated QA passes after code edits and do not want to recreate browser handles each turn;
- functional and visual checks need to share the same live session.

Do not use this skill when:
- a one-shot static review or single screenshot is enough;
- the task is backend-only or does not require UI interaction;
- the environment cannot support `js_repl` or Playwright setup.

## Inputs

- target workspace path;
- target runtime:
  - web app URL, or
  - Electron entrypoint;
- whether the goal is functional QA, visual QA, or both;
- whether the recent changes affect:
  - renderer only, or
  - startup, preload, or main-process behavior;
- any viewport or device expectations that matter for signoff.

## Outputs

- a persistent Playwright session plan appropriate to web or Electron;
- a QA coverage list mapping user-visible claims to checks;
- evidence notes from functional and visual QA;
- exact next-step commands or `js_repl` cells needed to continue;
- a final cleanup note when the session should be reset or closed.

## Philosophy

- Reuse handles instead of restarting the browser unless the process boundary changed.
- Separate functional QA from visual QA so each claim has explicit evidence.
- Prefer deterministic setup:
  - stable URLs
  - explicit viewports
  - reproducible reload or relaunch rules
- Keep instrumentation minimal and local to the current debugging goal.

## Preflight

Before using this skill:
- confirm `js_repl` is available;
- confirm Playwright is installed in the current workspace;
- confirm the app can be launched or is already running;
- choose the runtime path:
  - web
  - mobile web
  - native-window web
  - Electron
- write a short QA inventory before interacting:
  - requested requirements
  - user-visible claims you expect to make
  - important controls or state transitions
  - at least 2 exploratory scenarios

If `js_repl` is unavailable, stop and switch to a non-persistent browser workflow.

## Workflow

### 1) Bootstrap the persistent session

- Load Playwright once in `js_repl`.
- Keep top-level handles stable with `var`, not `const`, so later cells can reuse them.
- Use one named handle per surface:
  - `page`
  - `mobilePage`
  - `appWindow`

Minimal bootstrap:

```javascript
var chromium;
var electronLauncher;
var browser;
var context;
var page;
var mobileContext;
var mobilePage;
var electronApp;
var appWindow;

({ chromium, _electron: electronLauncher } = await import("playwright"));
console.log("Playwright loaded");
```

### 2) Choose the session mode explicitly

- Standard web:
  - use an explicit viewport for deterministic iteration and screenshots.
- Mobile web:
  - use a separate mobile context instead of resizing the desktop tab.
- Native-window web:
  - use `viewport: null` only when host-window behavior matters.
- Electron:
  - relaunch after main-process or preload changes; reload only for renderer changes.

### 3) Start or reuse the target session

For web apps:

```javascript
var TARGET_URL = "http://127.0.0.1:3000";

browser ??= await chromium.launch({ headless: false });
context ??= await browser.newContext({ viewport: { width: 1600, height: 900 } });
page ??= await context.newPage();
await page.goto(TARGET_URL, { waitUntil: "domcontentloaded" });
```

For Electron apps:

```javascript
var ELECTRON_ENTRY = ".";

electronApp ??= await electronLauncher.launch({ args: [ELECTRON_ENTRY] });
appWindow ??= await electronApp.firstWindow();
console.log(await appWindow.title());
```

If a handle is stale, set only that handle back to `undefined` and rerun the narrowest setup cell instead of resetting everything.

### 4) Decide reload versus relaunch

- renderer-only web changes:
  - reload the current page or context.
- renderer-only Electron changes:
  - reload `appWindow`.
- startup, preload, or main-process Electron changes:
  - close and relaunch the Electron app.
- when switching between explicit viewport and native-window passes:
  - close the current context and create a fresh one.

### 5) Run functional QA first

- exercise the exact user-visible claims from the QA inventory;
- check error, empty, loading, and off-happy-path states when relevant;
- keep notes tied to claims, not just raw actions;
- capture targeted screenshots only when they support a claim.

### 6) Run a separate visual QA pass

- verify viewport fit and clipping;
- confirm important states visually:
  - default
  - loading
  - error
  - expanded or modal states
- for visual signoff, capture screenshots from the stable context used for that pass.

### 7) Clean up only when the task is actually done

- close the browser or Electron session when signoff is complete;
- use `js_repl_reset` only when the kernel state itself is broken or you must start over cleanly.

## Validation

- Fail fast at the first broken gate:
  - missing `js_repl`
  - Playwright import failure
  - app not launchable
  - stale handles that cannot be recovered
- Confirm the QA inventory exists before claiming UI signoff.
- Confirm claims are backed by:
  - functional evidence
  - visual evidence when appearance matters
- If the workflow changed code, run the relevant repo checks before final completion.

## Constraints

- Redact secrets, tokens, and private content from screenshots and logs.
- Do not rely on persistent handles across workspace changes.
- Do not claim a visual fix based on one viewport when multiple viewports materially matter.
- Keep destructive browser actions out of exploratory runs unless the user asked for them.
- Prefer `127.0.0.1` over `localhost` for local servers when possible.

## Anti-patterns

- restarting the whole browser on every tiny change;
- mixing functional and visual signoff into one vague pass;
- using stale handles without checking whether the process or context changed;
- signing off without a coverage list tied to user-visible claims;
- using `js_repl_reset` as routine cleanup;
- collecting screenshots without stating what claim each image supports.

## Resources

- `references/contract.yaml` for routing and output expectations;
- `references/evals.yaml` for trigger and safety coverage;
- `agents/openai.yaml` for tool-facing metadata;
- `assets/playwright-small.svg` and `assets/playwright.png` for packaging or UI metadata if needed.

## Examples

- "Use $playwright-interactive to keep a live Playwright session open while I debug this local React app."
- "Inspect my Electron window after a preload change and tell me whether I need reload or relaunch."
- "Run a functional and visual QA pass without restarting the browser every time."

## See Also

| Skill | When to use together |
|---|---|
| [[agent-browser]] | Use agent-browser for simpler ref-based interactions |
| [[ui-visual-regression]] | Capture Playwright screenshots for regression baselines |
| [[fixing-accessibility]] | Test keyboard navigation and focus via Playwright |
| [[agentation]] | Wire Playwright automation into Agentation self-driving |

**Topic map:** [[frontend-ui]]

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
