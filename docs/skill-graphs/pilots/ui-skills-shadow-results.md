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

- Window: `2026-04-02..2026-04-08`
- Baseline source: `bootstrap pending`
- Runs total: `16`
- Runs by profile:
  - `ui-ux-creative-coding`: `4`
  - `interface-craft`: `4`
  - `frontend-ui-design`: `4`
  - `react-ui-patterns`: `4`

### KPI snapshot

- Repeat failure pattern rate: `25.0%` (delta vs baseline: `n/a`)
- First-pass acceptance: `0.0%` (delta vs baseline: `n/a`)
- Iterations median / p90: `2.00` / `4.50`
- Quality uplift median: `0.165`; positive uplift rate: `100.0%`
- Critical non-regression compliance: `37.5%`
- Terminal non-regression compliance: `100.0%`
- Non-regression recovered: `62.5%`
- Budget compliance: `100.0%`
- Evaluator flip rate: `8.8%`
- Capture coverage: `100.0%` (`16/16` runs with capture artifacts)
- Confidence bucket distribution: `high=0` `medium=6` `low=10` `unknown=0`
- Injection usage rate: `25.0%` (`4/16` runs, total lessons `4`, suppressed-by-controls runs `0`)
- Rollout mode distribution: `active=16` `observe_only=0` `off=0` `other=0`
- Uplift gate decisions (promotion/auto-apply): `pass=0/0` `insufficient_data=16/16` `regressed=0/0`

## Run log

| Run | Profile | Status | Stop reason | Iterations | Uplift | Non-regression | Tokens |
|---|---|---|---|---:|---:|:---:|---:|
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
