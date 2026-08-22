# Go/No-Go Summary (2026-02-25)

## Table of Contents

- [Decision](#decision)
- [Evidence snapshot](#evidence-snapshot)
- [Rollback drill results](#rollback-drill-results)
- [Next actions](#next-actions)

## Decision

- **Result:** `HOLD` (no-go for broad active rollout)
- **Recorded evidence:** the 2026-02-25 shadow dashboard snapshot (retired
  generated output) recorded this decision.

## Evidence snapshot

- Current runs in decision window: `8` (required `40`)
- First-pass acceptance rate: `25.0%`
- Repeat failure rate: `12.5%`
- Capture coverage: `0.0%`
- Injection usage: `0.0%`
- Uplift decision counts (promotion): `unknown=8` (no usable uplift sample yet)

Blocking reasons:
- Insufficient sample size and per-profile coverage.
- Critical non-regression compliance below required threshold.
- Budget compliance below required threshold.
- Baseline window unavailable for delta KPI comparison.

## Rollback drill results

Evidence: the 2026-02-25 rollback-drill snapshot and
`/docs/skill-graphs/pilots/rollback-drill.md`

- `baseline_active` → exit `0`, blocker `none`
- `kill_switch` → exit `4`, blocker `kill_switch_activated`
- `rollback_required` → exit `5`, blocker `run_rollback_required`
- `rollout_off` → exit `5`, blocker `run_rollforward_blocked`

## Next actions

1. Increase pilot volume to satisfy sample and per-profile thresholds.
2. Regenerate shadow dashboard after additional runs.
3. Require non-`unknown` uplift decision counts before enabling broad active rollout.
