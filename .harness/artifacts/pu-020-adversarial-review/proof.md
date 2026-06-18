# Status

issues_found

Local code/test truth is mostly healthy: the requested focused validation passed locally with both wrapper commands and the uv pytest lane:

- `./bin/ask sdk status --json --robot` -> pass
- `./bin/skills-sdk status --json --robot` -> pass
- `uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q` -> pass, `28 passed in 0.99s`

This proves the local SDK status route can load the capability matrix, the HTML has the expected status rows, source declarations exist, source artifacts exist, and the current static artifact no longer advertises PU-019 with the exact `Next: PU-019` or `Next slice: PU-019` pattern.

It does not prove CI, PR state, review-thread state, tracker state, hosted docs, or merge readiness.

# Findings

## P2: External readiness lanes remain unverified

The acceptance claim says `artifacts/recommended-skills-sdk-pipeline.html` remains a projection of `./bin/ask sdk status --json --robot` and `Infrastructure/config/skills-sdk/capability-matrix.v1.json` rather than a second planning authority. The current tests now also assert owner-surface and next-slice parity; the remaining proof gaps are external readiness lanes.

Evidence:

- `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:88` checks matrix capability IDs equal parsed HTML row IDs.
- `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:93` checks HTML status attributes/text match matrix statuses.
- `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:100` checks runtime IDs, statuses, and titles appear in HTML rows.
- `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:147` checks owner-surface and next-slice parity against live SDK status.
- `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:170` rejects source-artifact PU IDs as `Next` / `Next slice` labels.

Why this matters: local projection parity does not prove CI, PR state, review-thread state, tracker state, hosted docs, or merge readiness.

Smallest durable fix: keep external readiness as a separate closeout lane and check those surfaces directly before making release or merge-readiness claims.

# Recommendation

Keep the slice, but keep readiness claims lane-separated. The blocked mise/uv concern did not reproduce in this review when cache/state paths were pinned to temp locations; both SDK wrapper commands and the uv pytest lane passed locally. The remaining weakness is external proof coverage, not local owner-surface or next-slice projection parity.

WROTE: .harness/artifacts/pu-020-adversarial-review/proof.md
