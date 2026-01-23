# Web / React probes

## Static inspection
- Browser DevTools Sources panel (pretty-print bundles)
- Identify source maps if present and permitted
- Search for endpoints, feature flags, and route tables

## React component inspection (authorized only)
- Use React Developer Tools to inspect component tree and props.
- Capture evidence artifacts (tree, props, DOM snapshots) with explicit permission.
- Follow `references/react_fiber_authorized.md` for verification loops and limits.

## Network inspection
- DevTools Network panel; export HAR for evidence
- Observe REST/GraphQL/WebSocket traffic
- Use repeatable scenarios for baseline vs stimulus

## Automation (optional)
- Playwright for deterministic scenarios and traces
- Capture screenshots and network logs as artifacts

## Notes
- Do not bypass auth or scrape private data.
- Treat minified bundles as untrusted; rely on evidence from runtime behavior.
