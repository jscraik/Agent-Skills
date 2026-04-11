# UI Skills Pilot Readout

Use this page to record expansion-gate evidence after pilot runs.

## Table of Contents

- [Readout metadata](#readout-metadata)
- [Scorecard](#scorecard)
- [Gate decision](#gate-decision)
- [Follow-ups](#follow-ups)

## Readout metadata

- Window: `2026-04-05..2026-04-11`
- Baseline: `_bootstrap pending_`
- Total runs: `40`
- Runs per profile:
  - `ui-ux-creative-coding`: `10`
  - `interface-craft`: `10`
  - `frontend-ui-design`: `10`
  - `react-ui-patterns`: `10`
- Reviewer(s): `_pending_`

## Scorecard

- Repeat failure pattern rate delta: `n/a` (target: `<= -35.0pp` reduction)
- First-pass acceptance delta: `n/a` (target: `>= +20.0pp`)
- Iterations median / p90: `2.00` / `5.00` (target: `<=2 / <=4`)
- Quality uplift median: `0.165` (target: `>= +0.120`)
- Critical non-regression compliance: `37.5%` (target: `100.0%`)
- Terminal non-regression compliance: `100.0%` (monitor recovery separately)
- Non-regression recovered: `62.5%` (intermediate failures that still finished clean)
- Budget compliance: `100.0%` (target: `>=95.0%`)
- Capture coverage: `100.0%` (target: `>=95.0%`)
- Injection usage rate: `25.0%` (target: pilot-defined; monitor suppression count `0`)
- Reviewer overhead median / p90: `n/a / n/a` (not captured in MVP telemetry yet)

## Gate decision

- Decision: `HOLD`
- Reason:
  - critical non-regression compliance below 100%
  - baseline window unavailable for delta KPIs

## Follow-ups

- Owner: `_pending_`
- Due date: `_pending_`
- Tracking issue/doc: `_pending_`
