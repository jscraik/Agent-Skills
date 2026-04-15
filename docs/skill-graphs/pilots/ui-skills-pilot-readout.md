# UI Skills Pilot Readout

Use this page to record expansion-gate evidence after pilot runs.

## Table of Contents

- [Readout metadata](#readout-metadata)
- [Scorecard](#scorecard)
- [Gate decision](#gate-decision)
- [Follow-ups](#follow-ups)

## Readout metadata

- Window: `2026-04-09..2026-04-15`
- Baseline: `2026-04-07..2026-04-09` via `rolling_window`
- Total runs: `48`
- Runs per profile:
  - `ui-ux-creative-coding`: `12`
  - `interface-craft`: `12`
  - `frontend-ui-design`: `12`
  - `react-ui-patterns`: `12`
- Reviewer(s): `_pending_`

## Scorecard

- Repeat failure pattern rate delta: `+0.0pp` (target: `<= -35.0pp` reduction)
- First-pass acceptance delta: `+0.0pp` (target: `>= +20.0pp`)
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
  - first-pass acceptance delta below +20pp
  - repeat failure pattern reduction below 35%

## Follow-ups

- Owner: `_pending_`
- Due date: `_pending_`
- Tracking issue/doc: `_pending_`
