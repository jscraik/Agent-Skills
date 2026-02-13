# ChatGPT Apps lessons matrix (P0/P1/P2)

This matrix maps each lesson to concrete execution outputs:
- **Tasks** (what to implement)
- **Tests** (what to verify)
- **Widget changes** (UI/runtime updates)
- **Tool-output patterns** (structured result contracts)

## P0 — Ship correctness

1. **Context visibility boundaries**
   - Tasks: classify all fields as model-visible, widget-only, or user-only.
   - Tests: assert sensitive fields never leak into model-visible payloads.
   - Widget changes: split render state from model context state.
   - Tool-output patterns: typed shared fields in `structuredContent`; widget-only data in `_meta`.

2. **Front-load first response payload**
   - Tasks: avoid N+1 hydration patterns in common path.
   - Tests: first meaningful render via ≤1 main tool call.
   - Widget changes: render from first result, then progressively enhance.
   - Tool-output patterns: include complete initial state in first result.

3. **Model visibility into UI selection state**
   - Tasks: sync minimal selected IDs/current view state to model context.
   - Tests: selection-follow-up query resolves correct entity.
   - Widget changes: track stable selected IDs.
   - Tool-output patterns: include stable IDs and selected context tokens.

4. **Explicit API routing by interaction type**
   - Tasks: separate wrappers for tool calls, follow-up message posts, and model-context updates.
   - Tests: contract tests per route path.
   - Widget changes: central bridge module.
   - Tool-output patterns: envelope with `kind`, `entities`, `uiHints`, `nextActions`.

## P1 — Production readiness

5. **Multi-mode adaptive UI**
   - Tasks: inline/PiP/fullscreen mode requirements.
   - Tests: visual checks for clipping/safe areas.
   - Widget changes: adaptive containers and safe-area handling.
   - Tool-output patterns: optional mode-specific `uiHints`.

6. **Embedded UI consistency**
   - Tasks: enforce shared design tokens/components.
   - Tests: lint checks for non-token styling.
   - Widget changes: consistent wrappers and typography spacing.
   - Tool-output patterns: typed content, no HTML-in-string rendering hacks.

7. **Language-first filtering (LOV params)**
   - Tasks: define LOV schemas and mapping hints for natural language.
   - Tests: NL phrase to enum/filter mapping accuracy checks.
   - Widget changes: lightweight chip-based refinements.
   - Tool-output patterns: selected filters + LOV options in structured results.

8. **File-in/file-out interaction paths**
   - Tasks: upload, processing, and downloadable output wiring.
   - Tests: upload-to-preview-to-download E2E path.
   - Widget changes: dropzone, progress, preview states.
   - Tool-output patterns: file handles/refs instead of raw blobs.

9. **CSP/domain policy readiness**
   - Tasks: validate connect/resource/frame/redirect domains.
   - Tests: CI gate for all network domains used by widget.
   - Widget changes: centralize networking layer.
   - Tool-output patterns: metadata/resource origins align with policy.

10. **Metadata and annotation publishability flags**
   - Tasks: checklist for `widgetDomain`, tool annotations, `widgetAccessible`, private tool handling.
   - Tests: static validation of required flags and consistency.
   - Widget changes: controlled navigation/open-in-app flows.
   - Tool-output patterns: explicit capabilities/safety hint fields.

## P2 — Iteration speed and DX

11. **Hot reload iteration loop**
   - Tasks: dev hot-reload and cache-busting scaffolding.
   - Tests: rebuild triggers live update in dev loop.
   - Widget changes: isolate side effects and hot-reload entrypoint.
   - Tool-output patterns: not required.

12. **Local emulator over ChatGPT-only testing**
   - Tasks: replay tool-result notifications and bridge events locally.
   - Tests: emulator-first UI tests; ChatGPT integration smoke only.
   - Widget changes: bridge abstraction supports emulator stubs.
   - Tool-output patterns: golden result fixtures per screen.

13. **Mobile testing path**
   - Tasks: tunnel-ready/mobile-access config.
   - Tests: mobile smoke for load + core interactions.
   - Widget changes: touch targets, scrolling, safe areas.
   - Tool-output patterns: optional compact-layout hints.

14. **Hook-based frontend abstractions**
   - Tasks: standard hooks for tool calls/results/widget state/locale.
   - Tests: hook unit tests + typing contracts.
   - Widget changes: consistent store/data-flow pipeline.
   - Tool-output patterns: strongly typed result shapes.

15. **Package into reusable tooling**
   - Tasks: scaffolds, validators, test harness, and flow-map generators.
   - Tests: golden template CI for lint/unit/emulator/integration.
   - Widget changes: convention-over-configuration folder layout.
   - Tool-output patterns: canonical versioned result envelope.
