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

- Window: `2026-04-06..2026-04-12`
- Baseline source: `frozen_snapshot` (`2026-04-05..2026-04-11`)
- Runs total: `48`
- Runs by profile:
  - `ui-ux-creative-coding`: `12`
  - `interface-craft`: `12`
  - `frontend-ui-design`: `12`
  - `react-ui-patterns`: `12`

### KPI snapshot

- Repeat failure pattern rate: `25.0%` (delta vs baseline: `+0.0pp`)
- First-pass acceptance: `0.0%` (delta vs baseline: `+0.0pp`)
- Iterations median / p90: `2.00` / `5.00`
- Quality uplift median: `0.165`; positive uplift rate: `100.0%`
- Critical non-regression compliance: `37.5%`
- Terminal non-regression compliance: `100.0%`
- Non-regression recovered: `62.5%`
- Budget compliance: `100.0%`
- Evaluator flip rate: `8.8%`
- Capture coverage: `100.0%` (`48/48` runs with capture artifacts)
- Confidence bucket distribution: `high=0` `medium=18` `low=30` `unknown=0`
- Injection usage rate: `25.0%` (`12/48` runs, total lessons `12`, suppressed-by-controls runs `0`)
- Rollout mode distribution: `active=48` `observe_only=0` `off=0` `other=0`
- Uplift gate decisions (promotion/auto-apply): `pass=0/0` `insufficient_data=48/48` `regressed=0/0`

## Run log

| Run | Profile | Status | Stop reason | Iterations | Uplift | Non-regression | Tokens |
|---|---|---|---|---:|---:|:---:|---:|
| run_20260412T064420106973Z_50ef7d_925f024 | frontend-ui-design | escalated | evaluator_conflict | 5 | +0.278 | ❌ | 5685 |
| run_20260412T064420226688Z_c6442d_92882bd | react-ui-patterns | passed | pass | 2 | +0.158 | ❌ | 389 |
| run_20260412T064420341042Z_f93d59_92a1174 | react-ui-patterns | passed | pass | 2 | +0.172 | ✅ | 399 |
| run_20260412T064419504123Z_4270e1_91980eb | ui-ux-creative-coding | passed | pass | 2 | +0.179 | ✅ | 394 |
| run_20260412T064419624036Z_cbb8d4_91bc4e9 | ui-ux-creative-coding | passed | pass | 2 | +0.046 | ❌ | 378 |
| run_20260412T064419747082Z_5b4309_91efa81 | interface-craft | passed | pass | 2 | +0.064 | ❌ | 357 |
| run_20260412T064419865434Z_04dd5b_920d06e | interface-craft | escalated | evaluator_conflict | 1 | +0.113 | ✅ | 157 |
| run_20260412T064419988886Z_1c1272_923ad51 | frontend-ui-design | passed | pass | 4 | +0.249 | ❌ | 4407 |
| run_20260411T063348089335Z_1c1272_91ead51 | frontend-ui-design | passed | pass | 4 | +0.249 | ❌ | 4407 |
| run_20260411T063348205332Z_50ef7d_920f024 | frontend-ui-design | escalated | evaluator_conflict | 5 | +0.278 | ❌ | 5685 |
| run_20260411T063348323211Z_c6442d_92382bd | react-ui-patterns | passed | pass | 2 | +0.158 | ❌ | 389 |
| run_20260411T063348436763Z_f93d59_9251174 | react-ui-patterns | passed | pass | 2 | +0.172 | ✅ | 399 |
| run_20260411T063347630118Z_4270e1_91480eb | ui-ux-creative-coding | passed | pass | 2 | +0.179 | ✅ | 394 |
| run_20260411T063347744899Z_cbb8d4_916c4e9 | ui-ux-creative-coding | passed | pass | 2 | +0.046 | ❌ | 378 |
| run_20260411T063347860332Z_5b4309_919fa81 | interface-craft | passed | pass | 2 | +0.064 | ❌ | 357 |
| run_20260411T063347973328Z_04dd5b_91bd06e | interface-craft | escalated | evaluator_conflict | 1 | +0.113 | ✅ | 157 |
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

## Exit gate checks

- Scoring variance + evaluator consistency observed in this window.
- Failure taxonomy and stop reasons captured per run.
- Governance/security controls remain required before promotions.

Related:
- [UI skills pilot readout](/docs/skill-graphs/pilots/ui-skills-pilot-readout.md)
