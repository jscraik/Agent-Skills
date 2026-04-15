# Adapter: ChatGPT Apps SDK Widget (UX + runtime)

## A) UX constraints (hosted in ChatGPT)
- Prefer inline for summaries and 1-2 step actions.
- Escalate to fullscreen for complex workflows.
- Avoid nested scroll; size content to the widget container.
- Inline surfaces: keep to two primary actions max.

## B) Runtime API (window.openai)
Use these as the authoritative runtime primitives:
- toolOutput: authoritative data snapshot from tool call
- toolResponseMetadata: widget-only metadata from tool `_meta`
- widgetState: persisted ephemeral UI state (draft fields, selection, expanded panels)
- setWidgetState(next): persist ephemeral UI state snapshot
- callTool(name, args): invoke tool (if widget has permission)
- requestDisplayMode({ mode }): switch inline/fullscreen/PiP when supported
- widgetSessionId: correlate widget instance with tool calls (when provided)

## C) State partitioning (mandatory)
1) Business data (authoritative): tool output / server
2) UI state (ephemeral): widgetState
3) Cross-session prefs: your backend (only if required)

Security rule:
- Keep widgetState small and free of secrets; assume persistence can be inspected.

## D) Safe write patterns
- Treat tool calls as retryable/idempotent.
- Separate read tools from write tools server-side.
- Use confirmation for destructive writes.
- After successful writes:
  - refresh data (new toolOutput)
  - reconcile widgetState (clear drafts, preserve selection if still valid)

## E) Common flows
### Inline list -> details
- Render list inline.
- On item click: set widgetState.selectedId.
- Optionally request fullscreen for deep inspection.

### Edit + Save
- Keep draft fields in widgetState.
- On Save: callTool(write_tool, payload).
- On success: refresh toolOutput and reconcile state.

### Loading/empty/error rules
- Loading: show skeleton/placeholder; keep layout stable.
- Empty: explain next best action; keep a single primary CTA.
- Error: show actionable recovery; never blame the user; allow retry; preserve drafts.

## F) Accessibility in widgets
- Keyboard: all actions reachable with Tab/Shift+Tab; Enter/Space activate.
- Focus order must be deterministic; restore focus after rerenders where possible.
- Announce async updates (e.g., "Saved", "3 results loaded") via ARIA live regions on web surfaces.

## G) Reduced motion
- If host indicates reduced motion, remove movement-based transitions; use instant or opacity-only updates.
- Avoid parallax / large motion in inline surfaces.

## H) Tool responses (size + structure)
- Always return `content` + `structuredContent` + `_meta` where applicable.
- Keep `structuredContent` under ~4k tokens for performance.
- Use `openai/closeWidget: true` in metadata when a flow should end.

## I) Widget metadata + CSP (tool schema)
- `openai/widgetDomain` for dedicated origin
- `openai/widgetDescription` and `openai/widgetPrefersBorder` for UX hints
- `openai/widgetCSP.connect_domains`, `resource_domains`, `redirect_domains`, `frame_domains`
- `openai/widgetAccessible` for widget-only tools
- `openai/visibility: "private"` for widget-only tools
- `openai/fileParams` when enabling uploads

## J) Example metadata snippet (tool schema)
Use as a reference (adapt to your tool):

```json
{
  "openai/widgetDescription": "Search results widget",
  "openai/widgetPrefersBorder": true,
  "openai/widgetDomain": "widgets.example.com",
  "openai/widgetCSP": {
    "connect_domains": [],
    "resource_domains": ["https://oaistatic.com"],
    "redirect_domains": [],
    "frame_domains": []
  }
}
```
