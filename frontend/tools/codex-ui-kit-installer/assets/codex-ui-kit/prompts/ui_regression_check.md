---
description: UI regression check (compare baseline vs current screenshots)
argument-hint: BASELINE=<path> CURRENT=<path> [FOCUS="<what to inspect>"]
---

Compare two UI screenshots and list regressions.

## Inputs
- BASELINE: $BASELINE
- CURRENT: $CURRENT
- FOCUS: $FOCUS

## Task
1) Open and compare BASELINE vs CURRENT.
2) Describe differences that look like regressions (layout, spacing, clipping, colors, typography, safe-area, scroll behavior).
3) Classify each difference:
   - severity: `blocker | major | minor`
   - likely cause: CSS/layout vs component logic vs data/state
   - likely file areas (components/styles/routes)
5) Output a short checklist of what to verify after fixing.

If FOCUS is provided, prioritize it: $FOCUS
