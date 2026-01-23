# Decision guide

Use this guide to choose the right rule quickly.

Questions
- Is the bottleneck network-bound or render-bound?
- Is the issue server, client, or both?
- Is the hot path on initial load or on interaction?

Mapping
- Network waterfall: prefer async-parallel, async-defer-await.
- Bundle bloat: prefer bundle-dynamic-imports, bundle-barrel-imports.
- Server latency: prefer server-parallel-fetching, server-cache-react.
- Re-render churn: prefer rerender-memo, rerender-dependencies.

Exit criteria
- Confirm the chosen rule affects the measured bottleneck.
