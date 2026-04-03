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

- Window: `2026-03-25..2026-03-31`
- Baseline source: `bootstrap pending`
- Runs total: `77`
- Runs by profile:
  - `ui-ux-creative-coding`: `19`
  - `interface-craft`: `19`
  - `frontend-ui-design`: `20`
  - `react-ui-patterns`: `19`

### KPI snapshot

- Repeat failure pattern rate: `14.3%` (delta vs baseline: `n/a`)
- First-pass acceptance: `0.0%` (delta vs baseline: `n/a`)
- Iterations median / p90: `2.00` / `4.00`
- Quality uplift median: `0.158`; positive uplift rate: `100.0%`
- Critical non-regression compliance: `39.0%`
- Terminal non-regression compliance: `100.0%`
- Non-regression recovered: `61.0%`
- Budget compliance: `100.0%`
- Evaluator flip rate: `23.9%`
- Capture coverage: `100.0%` (`77/77` runs with capture artifacts)
- Confidence bucket distribution: `high=0` `medium=30` `low=47` `unknown=0`
- Injection usage rate: `2.6%` (`2/77` runs, total lessons `2`, suppressed-by-controls runs `0`)
- Rollout mode distribution: `active=77` `observe_only=0` `off=0` `other=0`
- Uplift gate decisions (promotion/auto-apply): `pass=0/0` `insufficient_data=77/77` `regressed=0/0`

## Run log

| Run | Profile | Status | Stop reason | Iterations | Uplift | Non-regression | Tokens |
|---|---|---|---|---:|---:|:---:|---:|
| run_20260331T152827531388Z_4270e1_1632580e | ui-ux-creative-coding | passed | pass | 2 | +0.179 | ✅ | 394 |
| run_20260331T152827612936Z_5b4309_16328fa8 | interface-craft | passed | pass | 2 | +0.064 | ❌ | 357 |
| run_20260331T152827697664Z_1c1272_1632bad5 | frontend-ui-design | passed | pass | 4 | +0.249 | ❌ | 4407 |
| run_20260331T152827779313Z_c6442d_1632e82b | react-ui-patterns | passed | pass | 2 | +0.158 | ❌ | 389 |
| run_20260331T152813334763Z_1c1272_161e7ad5 | frontend-ui-design | passed | pass | 4 | +0.249 | ❌ | 4407 |
| run_20260331T151852050720Z_5b4309_114cefa8 | interface-craft | passed | pass | 2 | +0.064 | ❌ | 357 |
| run_20260331T151852142690Z_1c1272_114d2ad5 | frontend-ui-design | passed | pass | 4 | +0.249 | ❌ | 1385 |
| run_20260331T151852236494Z_c6442d_114d582b | react-ui-patterns | passed | pass | 2 | +0.158 | ❌ | 389 |
| run_20260331T151851936706Z_4270e1_114cb80e | ui-ux-creative-coding | passed | pass | 2 | +0.179 | ✅ | 394 |
| run_20260331T151815127679Z_4270e1_1112780e | ui-ux-creative-coding | passed | pass | 2 | +0.179 | ✅ | 394 |
| run_20260331T151815243207Z_5b4309_1112bfa8 | interface-craft | passed | pass | 2 | +0.064 | ❌ | 357 |
| run_20260331T151815347202Z_1c1272_1112ead5 | frontend-ui-design | passed | pass | 4 | +0.249 | ❌ | 1385 |
| run_20260331T151815442395Z_c6442d_1113182b | react-ui-patterns | passed | pass | 2 | +0.158 | ❌ | 389 |
| run_20260331T145040232925Z_4270e1_2dd980eb | ui-ux-creative-coding | passed | pass | 2 | +0.179 | ✅ | 394 |
| run_20260331T145040392381Z_5b4309_2ddefa81 | interface-craft | passed | pass | 2 | +0.064 | ❌ | 357 |
| run_20260331T145040546695Z_1c1272_2de1ad51 | frontend-ui-design | passed | pass | 4 | +0.249 | ❌ | 1385 |
| run_20260331T145040697904Z_c6442d_2de482bd | react-ui-patterns | passed | pass | 2 | +0.158 | ❌ | 389 |
| run_20260331T143754115936Z_4270e1_1056f80e | ui-ux-creative-coding | passed | pass | 2 | +0.179 | ✅ | 394 |
| run_20260331T143754207808Z_5b4309_10575fa8 | interface-craft | passed | pass | 2 | +0.064 | ❌ | 357 |
| run_20260331T143754291331Z_1c1272_10578ad5 | frontend-ui-design | passed | pass | 4 | +0.249 | ❌ | 1385 |
| run_20260331T143754373532Z_c6442d_1058f82b | react-ui-patterns | passed | pass | 2 | +0.158 | ❌ | 389 |
| run_20260331T143705500263Z_4270e1_f67680eb | ui-ux-creative-coding | passed | pass | 2 | +0.179 | ✅ | 394 |
| run_20260331T143705631166Z_e0cea3_f67cd447 | interface-craft | passed | pass | 2 | +0.080 | ❌ | 393 |
| run_20260331T143705716005Z_1c1272_f681ad51 | frontend-ui-design | passed | pass | 4 | +0.249 | ❌ | 1385 |
| run_20260331T143705798653Z_f4298e_f6846cbf | react-ui-patterns | escalated | evaluator_conflict | 1 | +0.068 | ✅ | 191 |
| run_20260331T143338402916Z_4270e1_d61080eb | ui-ux-creative-coding | passed | pass | 2 | +0.179 | ✅ | 394 |
| run_20260331T143338495120Z_5b4309_d616fa81 | interface-craft | passed | pass | 2 | +0.064 | ❌ | 357 |
| run_20260331T143338576793Z_1c1272_d619ad51 | frontend-ui-design | passed | pass | 4 | +0.249 | ❌ | 1385 |
| run_20260331T143338663201Z_c6442d_d61d82bd | react-ui-patterns | passed | pass | 2 | +0.158 | ❌ | 389 |
| run_20260331T143101029285Z_4270e1_bff780eb | ui-ux-creative-coding | passed | pass | 2 | +0.179 | ✅ | 394 |
| run_20260331T143101103918Z_5b4309_bffafa81 | interface-craft | passed | pass | 2 | +0.064 | ❌ | 357 |
| run_20260331T143101180026Z_2ac1a9_bffd74d5 | frontend-ui-design | escalated | evaluator_conflict | 5 | +0.248 | ✅ | 1574 |
| run_20260331T143101254668Z_c6442d_c00082bd | react-ui-patterns | passed | pass | 2 | +0.158 | ❌ | 389 |
| run_20260331T142550018594Z_9b592b_6bcdd322 | ui-ux-creative-coding | passed | pass | 2 | +0.138 | ❌ | 236 |
| run_20260331T142550100545Z_518880_6bd4e292 | interface-craft | passed | pass | 3 | +0.124 | ❌ | 412 |
| run_20260331T142550175622Z_bb9acb_6bd7bddf | frontend-ui-design | passed | pass | 4 | +0.245 | ❌ | 880 |
| run_20260331T142550250609Z_82ecf7_6bdae6fc | react-ui-patterns | escalated | evaluator_conflict | 1 | +0.094 | ✅ | 85 |
| run_20260331T141227072955Z_fc4e0c_15c57efe | react-ui-patterns | passed | pass | 2 | +0.118 | ❌ | 216 |
| run_20260331T141227147051Z_75196b_15c59f5e | react-ui-patterns | passed | pass | 3 | +0.147 | ❌ | 421 |
| run_20260331T141227221095Z_231f82_15c5b397 | react-ui-patterns | passed | pass | 3 | +0.195 | ❌ | 433 |

## Exit gate checks

- Scoring variance + evaluator consistency observed in this window.
- Failure taxonomy and stop reasons captured per run.
- Governance/security controls remain required before promotions.

Related:
- [UI skills pilot readout](/docs/skill-graphs/pilots/ui-skills-pilot-readout.md)
