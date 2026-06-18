# Route-Truth Authority Adversarial Review

## Status

issues_found

## Findings

- P1: External readiness lanes remain outside the local projection proof.
  Evidence: The prior owner-surface and next-slice parity gap is now covered by `test_pipeline_artifact_authority_cells_match_live_sdk_status`, which compares parsed HTML cells against live SDK status. The remaining unverified lanes are CI, PR state, review-thread state, tracker state, hosted docs, and merge readiness.
  Recommendation: Keep the local projection parity checks, but do not treat them as proof for external readiness lanes.

- P2: The top-level PU-020 next-slice banner is manually authored outside matrix parity.
  Evidence: The HTML includes a standalone `Next slice: PU-020` block (`artifacts/recommended-skills-sdk-pipeline.html:2263-2275`). The stale-completed-PU guard rejects `Next` or `Next slice` claims for PU ids discovered from implemented capability notes (`Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:113-122`) and also for source-artifact PUs (`Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:159-177`). That protects the prior PU-019 failure mode once a PU appears in implemented notes or source artifacts, but it does not bind this banner to `generated_from`, a current route field, or a single matrix-owned next-slice declaration.
  Recommendation: Either make the banner text covered by a parity assertion against the matrix/generated_from route for this slice, or remove the standalone next-slice authority and let the capability table/projected status text carry the route.

## Recommendation

Do not treat PU-020 as fully externally ready until CI, PR, review-thread, tracker, hosted-docs, and merge-readiness lanes are checked directly. Local HTML projection parity now covers the authority-bearing matrix fields that were previously missing.

WROTE: .harness/artifacts/pu-020-adversarial-review/authority.md
