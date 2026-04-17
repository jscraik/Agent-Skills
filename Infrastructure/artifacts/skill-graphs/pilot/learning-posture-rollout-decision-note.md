# Learning Posture Pilot Rollout Decision Note

Date: 2026-03-11
Owner: jamiecraik
Scope: Phase P10 rollout decision for learning-preserving pilot

## Decision

Decision: `revise contract before expansion`

Rollout posture: keep pilot-only; do not expand to additional skills yet.

## Evidence Snapshot

- Conformance summary artifact exists and is schema-valid:
  - `Infrastructure/artifacts/skill-graphs/pilot/learning-posture-pilot-conformance-summary.json`
- Per-pilot telemetry artifacts now exist and are machine-diffable:
  - `Infrastructure/artifacts/skill-graphs/pilot/telemetry/*.json`
- Canonical pilot eval reruns completed, but all 4 pilot eval gates failed (exit code `2`):
  - `Skills/skill-builder`
  - `frontend/tools/agentation`
  - `Skills/systematic-debugging`
  - `interview/interview-me`
- `Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py --strict` passed.
  - Evidence timestamp (UTC): `2026-03-11T10:29:12.729871Z`
  - Evidence artifact: `Infrastructure/artifacts/skill-graphs/pilot/learning-posture-pilot-conformance-summary.json`
- `Infrastructure/scripts/skill-graph/verify_recursive_skill_graph_artifacts.py --strict --run-state-check` failed (`legacy_partial` and `missing_mandatory` historical run artifacts).
  - Evidence timestamp (UTC): `2026-03-11T10:29:12.729871Z`
  - Evidence artifacts:
    - `Infrastructure/artifacts/skill-graphs/graph-adapter/notes/blocker--parity-legacy-partial.md`
    - `Infrastructure/artifacts/skill-graphs/graph-adapter/notes/blocker--parity-missing-mandatory.md`

## Risk/Blocker Summary

- Pilot conformance remains `blocked` because eval coverage did not pass.
- Telemetry coverage ratio is currently `0.0` for all pilots in the latest rerun outputs, so telemetry is also `blocked`.
- Historical run-artifact strict verification still fails and blocks full validation signoff.

## Next Gate to Reopen Expansion

1. Re-run canonical pilot evals with successful runner exits and passing scorecards for all four pilots.
2. Re-run summary generation + schema validation and confirm conformance reaches at least `partial` with non-zero telemetry coverage.
3. Resolve or explicitly exempt historical run-artifact strict failures, then rerun:
   - `python3 Infrastructure/scripts/skill-graph/verify_recursive_skill_graph_artifacts.py --strict --run-state-check`
4. Re-run final validation bundle and reissue this decision note as `pilot-only` or `expand`.
