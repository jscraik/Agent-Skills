---
name: web_app_interrogate
description: Web/React interrogation using HAR + Playwright trace and endpoint mapping
  (behavior-first when sourcemaps absent).
metadata:
  source_repo: https://github.com/jscraik/Agent-Skills
  source_rev: 7e31061c353c94746910d239ae122900cc5324fb-dirty
  source_dirty: 'true'
  source_dirty_paths: utilities/recon-workbench/references/evals.yaml, utilities/skill-creator/scripts/run_skill_evals.py,
    design/better-icons/
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
