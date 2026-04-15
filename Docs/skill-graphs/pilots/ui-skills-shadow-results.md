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

- Window: `2026-04-09..2026-04-15`
- Baseline source: `rolling_window` (`2026-04-07..2026-04-09`)
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
| run_20260415T080207080529Z_4270e1_92180eb | ui-ux-creative-coding | passed | pass | 2 | +0.179 | ✅ | 394 |
| run_20260415T080207208381Z_cbb8d4_923c4e9 | ui-ux-creative-coding | passed | pass | 2 | +0.046 | ❌ | 378 |
| run_20260415T080207332207Z_5b4309_926fa81 | interface-craft | passed | pass | 2 | +0.064 | ❌ | 357 |
| run_20260415T080207452364Z_04dd5b_928d06e | interface-craft | escalated | evaluator_conflict | 1 | +0.113 | ✅ | 157 |
| run_20260415T080207575005Z_1c1272_92bad51 | frontend-ui-design | passed | pass | 4 | +0.249 | ❌ | 4407 |
| run_20260415T080207704735Z_50ef7d_92df024 | frontend-ui-design | escalated | evaluator_conflict | 5 | +0.278 | ❌ | 5685 |
| run_20260415T080207835547Z_c6442d_93082bd | react-ui-patterns | passed | pass | 2 | +0.158 | ❌ | 389 |
| run_20260415T080207958259Z_f93d59_9321174 | react-ui-patterns | passed | pass | 2 | +0.172 | ✅ | 399 |
| run_20260414T080113088052Z_4270e1_91280eb | ui-ux-creative-coding | passed | pass | 2 | +0.179 | ✅ | 394 |
| run_20260414T080113215773Z_cbb8d4_914c4e9 | ui-ux-creative-coding | passed | pass | 2 | +0.046 | ❌ | 378 |
| run_20260414T080113334093Z_5b4309_917fa81 | interface-craft | passed | pass | 2 | +0.064 | ❌ | 357 |
| run_20260414T080113449366Z_04dd5b_91ad06e | interface-craft | escalated | evaluator_conflict | 1 | +0.113 | ✅ | 157 |
| run_20260414T080113568206Z_1c1272_91dad51 | frontend-ui-design | passed | pass | 4 | +0.249 | ❌ | 4407 |
| run_20260414T080113687304Z_50ef7d_91ff024 | frontend-ui-design | escalated | evaluator_conflict | 5 | +0.278 | ❌ | 5685 |
| run_20260414T080113805620Z_c6442d_92282bd | react-ui-patterns | passed | pass | 2 | +0.158 | ❌ | 389 |
| run_20260414T080113923109Z_f93d59_9241174 | react-ui-patterns | passed | pass | 2 | +0.172 | ✅ | 399 |
| run_20260413T081921163303Z_c6442d_91e82bd | react-ui-patterns | passed | pass | 2 | +0.158 | ❌ | 389 |
| run_20260413T081921414441Z_f93d59_9201174 | react-ui-patterns | passed | pass | 2 | +0.172 | ✅ | 399 |
| run_20260413T081920417414Z_4270e1_90f80eb | ui-ux-creative-coding | passed | pass | 2 | +0.179 | ✅ | 394 |
| run_20260413T081920519358Z_cbb8d4_911c4e9 | ui-ux-creative-coding | passed | pass | 2 | +0.046 | ❌ | 378 |
| run_20260413T081920625530Z_5b4309_914fa81 | interface-craft | passed | pass | 2 | +0.064 | ❌ | 357 |
| run_20260413T081920731856Z_04dd5b_916d06e | interface-craft | escalated | evaluator_conflict | 1 | +0.113 | ✅ | 157 |
| run_20260413T081920845569Z_1c1272_919ad51 | frontend-ui-design | passed | pass | 4 | +0.249 | ❌ | 4407 |
| run_20260413T081920967414Z_50ef7d_91bf024 | frontend-ui-design | escalated | evaluator_conflict | 5 | +0.278 | ❌ | 5685 |
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

## Exit gate checks

- Scoring variance + evaluator consistency observed in this window.
- Failure taxonomy and stop reasons captured per run.
- Governance/security controls remain required before promotions.

Related:
- [UI skills pilot readout](/docs/skill-graphs/pilots/ui-skills-pilot-readout.md)
