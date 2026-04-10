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

- Window: `2026-04-04..2026-04-10`
- Baseline source: `bootstrap pending`
- Runs total: `32`
- Runs by profile:
  - `ui-ux-creative-coding`: `8`
  - `interface-craft`: `8`
  - `frontend-ui-design`: `8`
  - `react-ui-patterns`: `8`

### KPI snapshot

- Repeat failure pattern rate: `25.0%` (delta vs baseline: `n/a`)
- First-pass acceptance: `0.0%` (delta vs baseline: `n/a`)
- Iterations median / p90: `2.00` / `4.90`
- Quality uplift median: `0.165`; positive uplift rate: `100.0%`
- Critical non-regression compliance: `37.5%`
- Terminal non-regression compliance: `100.0%`
- Non-regression recovered: `62.5%`
- Budget compliance: `100.0%`
- Evaluator flip rate: `8.8%`
- Capture coverage: `100.0%` (`32/32` runs with capture artifacts)
- Confidence bucket distribution: `high=0` `medium=12` `low=20` `unknown=0`
- Injection usage rate: `25.0%` (`8/32` runs, total lessons `8`, suppressed-by-controls runs `0`)
- Rollout mode distribution: `active=32` `observe_only=0` `off=0` `other=0`
- Uplift gate decisions (promotion/auto-apply): `pass=0/0` `insufficient_data=32/32` `regressed=0/0`

## Run log

| Run | Profile | Status | Stop reason | Iterations | Uplift | Non-regression | Tokens |
|---|---|---|---|---:|---:|:---:|---:|
| run_20260410T065025010349Z_5b4309_916fa81 | interface-craft | passed | pass | 2 | +0.064 | ❌ | 357 |
| run_20260410T065025126723Z_04dd5b_918d06e | interface-craft | escalated | evaluator_conflict | 1 | +0.113 | ✅ | 157 |
| run_20260410T065025246860Z_1c1272_91bad51 | frontend-ui-design | passed | pass | 4 | +0.249 | ❌ | 4407 |
| run_20260410T065025360237Z_50ef7d_91df024 | frontend-ui-design | escalated | evaluator_conflict | 5 | +0.278 | ❌ | 5685 |
| run_20260410T065025474543Z_c6442d_92082bd | react-ui-patterns | passed | pass | 2 | +0.158 | ❌ | 389 |
| run_20260410T065025587352Z_f93d59_9221174 | react-ui-patterns | passed | pass | 2 | +0.172 | ✅ | 399 |
| run_20260410T065024768042Z_4270e1_91180eb | ui-ux-creative-coding | passed | pass | 2 | +0.179 | ✅ | 394 |
| run_20260410T065024889084Z_cbb8d4_913c4e9 | ui-ux-creative-coding | passed | pass | 2 | +0.046 | ❌ | 378 |
| run_20260409T064532056345Z_cbb8d4_919c4e9 | ui-ux-creative-coding | passed | pass | 2 | +0.046 | ❌ | 378 |
| run_20260409T064532169749Z_5b4309_91cfa81 | interface-craft | passed | pass | 2 | +0.064 | ❌ | 357 |
| run_20260409T064532279715Z_04dd5b_91ed06e | interface-craft | escalated | evaluator_conflict | 1 | +0.113 | ✅ | 157 |
| run_20260409T064532394104Z_1c1272_921ad51 | frontend-ui-design | passed | pass | 4 | +0.249 | ❌ | 4407 |
| run_20260409T064532504568Z_50ef7d_923f024 | frontend-ui-design | escalated | evaluator_conflict | 5 | +0.278 | ❌ | 5685 |
| run_20260409T064532619060Z_c6442d_92682bd | react-ui-patterns | passed | pass | 2 | +0.158 | ❌ | 389 |
| run_20260409T064532730733Z_f93d59_9291174 | react-ui-patterns | passed | pass | 2 | +0.172 | ✅ | 399 |
| run_20260409T064531946744Z_4270e1_91780eb | ui-ux-creative-coding | passed | pass | 2 | +0.179 | ✅ | 394 |
| run_20260408T064527014926Z_50ef7d_946f024 | frontend-ui-design | escalated | evaluator_conflict | 5 | +0.278 | ❌ | 5685 |
| run_20260408T064527137168Z_c6442d_94982bd | react-ui-patterns | passed | pass | 2 | +0.158 | ❌ | 389 |
| run_20260408T064527254102Z_f93d59_94b1174 | react-ui-patterns | passed | pass | 2 | +0.172 | ✅ | 399 |
| run_20260408T064526421324Z_4270e1_93980eb | ui-ux-creative-coding | passed | pass | 2 | +0.179 | ✅ | 394 |
| run_20260408T064526538395Z_cbb8d4_93bc4e9 | ui-ux-creative-coding | passed | pass | 2 | +0.046 | ❌ | 378 |
| run_20260408T064526656356Z_5b4309_93efa81 | interface-craft | passed | pass | 2 | +0.064 | ❌ | 357 |
| run_20260408T064526774193Z_04dd5b_940d06e | interface-craft | escalated | evaluator_conflict | 1 | +0.113 | ✅ | 157 |
| run_20260408T064526894446Z_1c1272_943ad51 | frontend-ui-design | passed | pass | 4 | +0.249 | ❌ | 4407 |
| run_20260407T064405056266Z_04dd5b_8e4d06e | interface-craft | escalated | evaluator_conflict | 1 | +0.113 | ✅ | 157 |
| run_20260407T064405159287Z_1c1272_8e7ad51 | frontend-ui-design | passed | pass | 4 | +0.249 | ❌ | 4407 |
| run_20260407T064405259532Z_50ef7d_8e9f024 | frontend-ui-design | escalated | evaluator_conflict | 5 | +0.278 | ❌ | 5685 |
| run_20260407T064405363942Z_c6442d_8ec82bd | react-ui-patterns | passed | pass | 2 | +0.158 | ❌ | 389 |
| run_20260407T064405465228Z_f93d59_8ee1174 | react-ui-patterns | passed | pass | 2 | +0.172 | ✅ | 399 |
| run_20260407T064404758172Z_4270e1_8dc80eb | ui-ux-creative-coding | passed | pass | 2 | +0.179 | ✅ | 394 |
| run_20260407T064404855416Z_cbb8d4_8dec4e9 | ui-ux-creative-coding | passed | pass | 2 | +0.046 | ❌ | 378 |
| run_20260407T064404953569Z_5b4309_8e1fa81 | interface-craft | passed | pass | 2 | +0.064 | ❌ | 357 |

## Exit gate checks

- Scoring variance + evaluator consistency observed in this window.
- Failure taxonomy and stop reasons captured per run.
- Governance/security controls remain required before promotions.

Related:
- [UI skills pilot readout](/docs/skill-graphs/pilots/ui-skills-pilot-readout.md)
