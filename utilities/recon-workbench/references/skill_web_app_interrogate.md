---
name: web_app_interrogate
description: Web/React interrogation using HAR + Playwright trace and endpoint mapping (behavior-first when sourcemaps absent).
---

Inputs:
- URL
- Scenario steps (authorized)

Use probes:
- web.playwright_trace
- web.playwright_har_capture
- web.har_capture (manual fallback)

Output:
- Endpoint inventory (REST/GraphQL/WS)
- Auth mechanism observations (cookies/storage) without collecting secrets
- Feature map inferred from baseline/stimulus diffs
