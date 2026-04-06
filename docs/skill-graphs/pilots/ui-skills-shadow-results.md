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

- Window: `2026-03-31..2026-04-06`
- Baseline source: `frozen_snapshot` (`2026-03-25..2026-03-31`)
- Runs total: `8`
- Runs by profile:
  - `ui-ux-creative-coding`: `2`
  - `interface-craft`: `2`
  - `frontend-ui-design`: `2`
  - `react-ui-patterns`: `2`

### KPI snapshot

- Repeat failure pattern rate: `25.0%` (delta vs baseline: `+6.7pp`)
- First-pass acceptance: `0.0%` (delta vs baseline: `+0.0pp`)
- Iterations median / p90: `2.00` / `4.30`
- Quality uplift median: `0.165`; positive uplift rate: `100.0%`
- Critical non-regression compliance: `37.5%`
- Terminal non-regression compliance: `100.0%`
- Non-regression recovered: `62.5%`
- Budget compliance: `100.0%`
- Evaluator flip rate: `8.8%`
- Capture coverage: `100.0%` (`8/8` runs with capture artifacts)
- Confidence bucket distribution: `high=0` `medium=3` `low=5` `unknown=0`
- Injection usage rate: `25.0%` (`2/8` runs, total lessons `2`, suppressed-by-controls runs `0`)
- Rollout mode distribution: `active=8` `observe_only=0` `off=0` `other=0`
- Uplift gate decisions (promotion/auto-apply): `pass=0/0` `insufficient_data=8/8` `regressed=0/0`

## Run log

| Run | Profile | Status | Stop reason | Iterations | Uplift | Non-regression | Tokens |
|---|---|---|---|---:|---:|:---:|---:|
| run_20260406T132616036114Z_cbb8d4_17b7ac4e | ui-ux-creative-coding | passed | pass | 2 | +0.046 | ❌ | 378 |
| run_20260406T132616095953Z_5b4309_17b7dfa8 | interface-craft | passed | pass | 2 | +0.064 | ❌ | 357 |
| run_20260406T132616151793Z_04dd5b_17b7fd06 | interface-craft | escalated | evaluator_conflict | 1 | +0.113 | ✅ | 157 |
| run_20260406T132616211252Z_1c1272_17b82ad5 | frontend-ui-design | passed | pass | 4 | +0.249 | ❌ | 4407 |
| run_20260406T132616265769Z_50ef7d_17b84f02 | frontend-ui-design | escalated | evaluator_conflict | 5 | +0.278 | ❌ | 5685 |
| run_20260406T132616322434Z_c6442d_17b8782b | react-ui-patterns | passed | pass | 2 | +0.158 | ❌ | 389 |
| run_20260406T132616374674Z_f93d59_17b89117 | react-ui-patterns | passed | pass | 2 | +0.172 | ✅ | 399 |
| run_20260406T132615979078Z_4270e1_17b7880e | ui-ux-creative-coding | passed | pass | 2 | +0.179 | ✅ | 394 |

## Exit gate checks

- Scoring variance + evaluator consistency observed in this window.
- Failure taxonomy and stop reasons captured per run.
- Governance/security controls remain required before promotions.

Related:
- [UI skills pilot readout](/docs/skill-graphs/pilots/ui-skills-pilot-readout.md)
