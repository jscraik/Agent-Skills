# UI Skills Shadow Results (Phase 2)

Shadow mode runs the full bounded loop (generate/evaluate/diagnose/improve/re-score) with checkpoint adversarial checks, without automatic canonical promotion writes.

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

- Window: `2026-02-14..2026-02-20`
- Runs total: `8`
- Runs by profile:
  - `ui-ux-creative-coding`: `5`
  - `interface-craft`: `1`
  - `frontend-ui-design`: `1`
  - `react-ui-patterns`: `1`

### KPI snapshot

- Repeat failure pattern rate: `12.5%` (delta vs baseline: `n/a`)
- First-pass acceptance: `25.0%` (delta vs baseline: `n/a`)
- Iterations median / p90: `2.00` / `4.30`
- Quality uplift median: `0.141`; positive uplift rate: `100.0%`
- Critical non-regression compliance: `62.5%`
- Budget compliance: `87.5%`
- Evaluator flip rate: `24.4%`

## Run log

| Run | Profile | Status | Stop reason | Iterations | Uplift | Non-regression | Tokens |
|---|---|---|---|---:|---:|:---:|---:|
| run_20260220T195545Z_8799c2 | ui-ux-creative-coding | passed | pass | 1 | +0.040 | ✅ | 44 |
| run_20260220T150021Z_518880 | interface-craft | passed | pass | 2 | +0.132 | ✅ | 219 |
| run_20260220T150021Z_82ecf7 | react-ui-patterns | passed | pass | 1 | +0.097 | ✅ | 85 |
| run_20260220T150021Z_9b592b | ui-ux-creative-coding | passed | pass | 2 | +0.092 | ❌ | 235 |
| run_20260220T150021Z_bb9acb | frontend-ui-design | passed | pass | 3 | +0.151 | ❌ | 427 |
| run_20260220T144736Z_425b7a | ui-ux-creative-coding | passed | pass | 2 | +0.187 | ❌ | 181 |
| run_20260220T144710Z_425b7a | ui-ux-creative-coding | passed | pass | 5 | +0.304 | ✅ | 959 |
| run_20260220T144703Z_425b7a | ui-ux-creative-coding | failed | budget_exhausted | 4 | +0.277 | ✅ | 645 |

## Exit gate checks

- Scoring variance + evaluator consistency observed in this window.
- Failure taxonomy and stop reasons captured per run.
- Governance/security controls remain required before promotions.

Related:
- [UI skills pilot readout](/docs/skill-graphs/pilots/ui-skills-pilot-readout.md)
