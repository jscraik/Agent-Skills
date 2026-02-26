# UI Skills Shadow Results (Phase 2)

Shadow mode runs evaluator + checkpoint adversarial checks without automatic improvement writes.

## Table of Contents

- [Pilot scope](#pilot-scope)
- [Window summary](#window-summary)
- [Run log](#run-log)
- [Exit gate checks](#exit-gate-checks)

## Pilot scope

- `ui-ux-creative-coding`
- `interface-craft`
- `frontend-ui-design`
- `react-ui-patterns`

## Window summary

- Window: `2026-02-24..2026-02-26`
- Runs total: `8`
- Runs by profile:
  - `ui-ux-creative-coding`: `2`
  - `interface-craft`: `2`
  - `frontend-ui-design`: `2`
  - `react-ui-patterns`: `2`

### KPI snapshot

- Repeat failure pattern rate: `25.0%` (delta vs baseline: `n/a`)
- First-pass acceptance: `0.0%` (delta vs baseline: `n/a`)
- Iterations median / p90: `2.00` / `2.30`
- Quality uplift median: `0.141`; positive uplift rate: `100.0%`
- Critical non-regression compliance: `50.0%`
- Budget compliance: `100.0%`
- Evaluator flip rate: `37.5%`
- Capture coverage: `100.0%` (`8/8` runs with capture artifacts)
- Confidence bucket distribution: `high=0` `medium=4` `low=4` `unknown=0`
- Injection usage rate: `0.0%` (`0/8` runs, total lessons `0`, suppressed-by-controls runs `0`)
- Rollout mode distribution: `active=0` `observe_only=8` `off=0` `other=0`
- Uplift gate decisions (promotion/auto-apply): `pass=0/0` `insufficient_data=8/8` `regressed=0/0`

## Run log

| Run | Profile | Status | Stop reason | Iterations | Uplift | Non-regression | Tokens |
|---|---|---|---|---:|---:|:---:|---:|
| run_20260226T171439998828Z_331545_3e6cdb11 | interface-craft | passed | pass | 2 | +0.161 | ✅ | 231 |
| run_20260226T171440087620Z_bb9acb_3e6fbddf | frontend-ui-design | escalated | evaluator_conflict | 1 | +0.068 | ✅ | 83 |
| run_20260226T171440175092Z_5ca1db_3e71dcb4 | frontend-ui-design | passed | pass | 2 | +0.130 | ❌ | 215 |
| run_20260226T171440265063Z_82ecf7_3e74e6fc | react-ui-patterns | escalated | evaluator_conflict | 1 | +0.097 | ✅ | 85 |
| run_20260226T171440352137Z_e5ee22_3e76d9f5 | react-ui-patterns | passed | pass | 2 | +0.152 | ❌ | 221 |
| run_20260226T171439728483Z_9b592b_3e51d322 | ui-ux-creative-coding | passed | pass | 2 | +0.157 | ❌ | 235 |
| run_20260226T171439820489Z_8786fa_3e640051 | ui-ux-creative-coding | passed | pass | 2 | +0.173 | ✅ | 236 |
| run_20260226T171439910572Z_518880_3e6ae292 | interface-craft | passed | pass | 3 | +0.123 | ❌ | 412 |

## Exit gate checks

- Scoring variance + evaluator consistency observed in this window.
- Failure taxonomy and stop reasons captured per run.
- Governance/security controls remain required before promotions.

Related:
- [UI skills pilot readout](/docs/skill-graphs/pilots/ui-skills-pilot-readout.md)
