---
description: iOS Simulator UI fix (snapshot → patch → re-snapshot)
argument-hint: ISSUE="<what's wrong>" [PROFILE=<profile>] [PATH=<route>] [FOCUS="<component>"] [FILES="<paths>"]
---

You are working in a React + Vite + Tailwind repo.

## Goal
Fix the iOS Simulator Safari UI issue described in: $ISSUE

## Inputs (may be empty)
- ISSUE: $ISSUE
- PROFILE: $PROFILE
- PATH: $PATH
- FOCUS: $FOCUS
- FILES: $FILES

## Defaults
- If PROFILE is empty, use `iphone_pro`.
- If PATH is empty, use `/`.

## Constraints
- Minimal, targeted change. Avoid refactors.
- Prefer Tailwind utilities over ad-hoc CSS.
- No new dependencies unless explicitly requested.
- Verify with the fastest available checks from `package.json` (lint/typecheck/test).

## Workflow
1) Reproduce on iOS Simulator Safari.
   - If `bin/ios-web` exists, use it to open the simulator to the correct route and to take screenshots.
   - If `bin/ui-codex` exists, you can use it for a fully scripted loop, but still validate visually.

2) Capture a BEFORE screenshot and inspect it.
   - Default path: `.ios-web/before/<profile>.png`

3) Diagnose the most likely root cause.
   - Safe-area / notch overlap
   - `100vh` / viewport unit issues
   - Overflow causing horizontal scroll
   - Fixed header/footer overlapping content
   - `position: sticky` inside an overflow container
   - Font sizing / line-height differences on iOS
   If FILES is provided, start investigation there: $FILES

4) Implement the smallest fix that addresses the issue.

5) Run checks (only those that exist in `package.json`):
   - lint
   - typecheck
   - tests

6) Capture an AFTER screenshot and inspect it.
   - Default path: `.ios-web/after/<profile>.png`

7) Report back:
   - Root cause (1–2 sentences)
   - What changed (files + brief diff summary)
   - Commands run + results
   - Screenshot paths (before/after)
   - Remaining risks / next actions
