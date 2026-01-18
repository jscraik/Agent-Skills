# React + Apps SDK UI (setup + patterns)

Last verified: 2026-01-04

## Install
- Follow the Apps SDK UI kit docs for install and Tailwind setup/version.
- Prefer exact pins unless the repo standardizes ranges; follow existing
  package.json constraints and do not change versions without explicit approval.
  Upgrade only via an explicit version bump + changelog.

## Official docs (authoritative)
- https://developers.openai.com/apps-sdk
- https://developers.openai.com/apps-sdk/build/chatgpt-ui/
- https://openai.github.io/apps-sdk-ui/

## Global stylesheet
Example only (verify with Apps SDK UI kit docs). At the top of your main stylesheet (e.g. src/main.css):

@import "tailwindcss";
@import "@openai/apps-sdk-ui/css";
/* If required by your Tailwind config, include the UI kit source in content. */

## Widget runtime notes
Your widget runs inside ChatGPT and reads globals from `window.openai`.
Use the Apps SDK UI docs for the authoritative list of APIs and behavior.

Keep widgetState payload small and free of secrets.
Avoid storing PII or credentials in widgetState.
toolResponseMetadata is the tool `_meta` payload; only the widget sees it.
Anything you pass to `setWidgetState` is shown to the model; keep it focused and
well under 4k tokens for performance.
The tool response metadata supports:
- `openai/closeWidget` = true to close the widget from the tool response
- `openai/widgetSessionId` for correlating a widget instance with tool calls

## Accessibility requirements
- Ensure focus order is explicit for widget UI.
- Provide reduced-motion alternatives for any animation.
- Respect `prefers-contrast` and `prefers-reduced-motion` where applicable.

## Performance guidelines
- Defer heavy work to tool calls; keep render lightweight.
- Avoid nested scrolling in widgets; prefer fullscreen for complex flows.

## OpenAI Apps SDK UI notes (verify with docs)
The items below are illustrative and may drift. Always reconcile with the
official docs at the time of implementation.
- Components render inside an iframe and communicate via `window.openai`.
- `window.openai` globals include:
  - `toolInput`, `toolOutput`, `toolResponseMetadata`
  - `widgetState`, `setWidgetState(state)` (stores a new snapshot synchronously)
  - `theme`, `displayMode`, `maxHeight`, `safeArea`, `view`, `userAgent`, `locale`
- Runtime APIs include:
  - `callTool(name, args)` (tool must allow component-initiated calls)
  - `sendFollowUpMessage({ prompt })`
  - `uploadFile(file)` and `getFileDownloadUrl({ fileId })`
  - `requestDisplayMode(...)`, `requestModal(...)`, `notifyIntrinsicHeight(...)`
  - `openExternal({ href })`
- Widget state is per-widget instance (message_id/widgetId). It persists only when
  the user submits through widget controls (inline/PiP/fullscreen composer). If the
  user types in the main chat composer, the widget runs fresh with a new widgetState.
- `toolOutput` mirrors tool `structuredContent`; keep it concise.
- `toolResponseMetadata` is private to the widget.
- `uploadFile` currently supports image/png, image/jpeg, image/webp.
- Prefer a `useOpenAiGlobal` hook or the docs’ helper pattern for subscriptions.
