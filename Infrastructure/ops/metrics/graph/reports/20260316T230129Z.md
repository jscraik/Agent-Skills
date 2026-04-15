# Graph Feedback Loop Report

Generated: 2026-03-16 23:01:30Z
Snapshot: `20260316T230129Z.json`
Previous snapshot: `20260316T041126Z.json`

## Key Signals
- Notes: **8**
- Directed edges: **30**
- Communities: **1**
- Community quality score: **0.0000**
- Top PageRank notes: [[product-strategy]], [[backend-platform]], [[agent-ops]], [[security-ops]], [[frontend-ui]]
- Top bridge notes: [[index]], [[product-strategy]], [[agent-ops]], [[backend-platform]], [[frontend-ui]]

## Drift Insights
- Notes delta vs previous snapshot: +0
- Community count delta: +0
- Top-5 PageRank overlap: 1.00
- Top-5 bridge overlap: 1.00

## Recommended Actions
- **LOW** `rec-001` (stable_state) — No urgent graph drift detected. Continue normal /reflect and /reweave cadence.  
  Reason: Current metrics are stable.

## Decision Feedback (AskQuestion / request_user_input)
- Capture user feedback for each HIGH/MEDIUM recommendation after it is attempted.
- Record outcomes with `Infrastructure/ops/Infrastructure/scripts/graph/record-feedback.sh` so the loop can learn what worked.
- Feedback log path: `./Infrastructure/ops/metrics/graph/feedback/decision-feedback.jsonl`

## Next Run
- Re-run this script after meaningful note growth or on a weekly schedule.
- Track trend by comparing reports in `Infrastructure/ops/metrics/graph/Infrastructure/reports/`.
