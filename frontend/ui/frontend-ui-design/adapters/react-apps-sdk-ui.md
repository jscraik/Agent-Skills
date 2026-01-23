# Adapter: React + Apps SDK UI (setup + patterns)

## A) Dependencies
- @openai/apps-sdk-ui
- Tailwind v4

## B) Required global stylesheet wiring
At the top of your main stylesheet (e.g. src/main.css):
@import "tailwindcss";
@import "@openai/apps-sdk-ui/css";

/* Required so Tailwind sees class references in Apps SDK UI components. */
@source "../node_modules/@openai/apps-sdk-ui";

## C) Widget mount + data access
- Mount React into a #root element.
- Read initial data from window.openai.toolOutput.
- Persist ephemeral state via window.openai.setWidgetState.

Recommend small hooks:
- useToolOutput()
- useWidgetState()
- useOpenAiGlobals(key) for theme/displayMode/maxHeight

## D) Data handling rules
- toolOutput is authoritative; treat it as read-only.
- widgetState is for UI-only, ephemeral state; keep payload small; do not store secrets.

## E) ChatUI guardrails (when in /Users/jamiecraik/chatui)
- Prefer `@chatui/ui` wrappers before importing `@openai/apps-sdk-ui` directly.
- Do not import `@radix-ui/*` outside `packages/ui/src/primitives`.
- Do not import `lucide-react` directly; use `packages/ui/src/icons` adapter.
- Confirm the current `@openai/apps-sdk-ui` version in `packages/ui/package.json` and `packages/widgets/package.json`.
