# Route-Truth Authority Adversarial Review

## Status

issues_found

## Findings

- P1: HTML capability rows can still diverge from the matrix for authority-bearing fields.
  Evidence: The spec says the HTML must remain a projection and not a second planning authority (`.harness/specs/2026-06-17-skills-sdk-pu-020-route-truth-declutter-spec.md:13-19`). The matrix is the structured source and carries `generated_from`, `source_artifacts`, `owner_surface`, and `next_slice` values (`Infrastructure/config/skills-sdk/capability-matrix.v1.json:5-26`, `Infrastructure/config/skills-sdk/capability-matrix.v1.json:365-374`). The HTML declares the status command and matrix as sources (`artifacts/recommended-skills-sdk-pipeline.html:2245-2247`), but the test only compares row ids/order, status vocabulary, title text, live status ids/status/title, and section sets (`Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:88-111`, `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:156-169`). It does not assert that HTML owner-surface cells or next-slice cells equal the corresponding matrix fields. A future edit could leave `data-status` correct while changing a row's owner or next-slice text into a competing authority claim.
  Recommendation: Extend the existing HTML parser/test to extract owner-surface and next-slice cells per `data-capability-id` and assert exact equality with the matrix/runtime rows. Keep this as projection parity, not a new dashboard or registry.

- P2: The top-level PU-020 next-slice banner is manually authored outside matrix parity.
  Evidence: The HTML includes a standalone `Next slice: PU-020` block (`artifacts/recommended-skills-sdk-pipeline.html:2263-2275`). The stale-completed-PU guard only rejects `Next` or `Next slice` claims for PU ids discovered from implemented capability notes (`Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:113-122`). That protects the prior PU-019 failure mode once a PU appears in implemented notes, but it does not bind this banner to `generated_from`, a current route field, or a single matrix-owned next-slice declaration.
  Recommendation: Either make the banner text covered by a parity assertion against the matrix/generated_from route for this slice, or remove the standalone next-slice authority and let the capability table/projected status text carry the route.

## Recommendation

Do not treat PU-020 as fully authority-closed until HTML projection parity covers every authority-bearing field that operators can read as route truth: capability id, title, status, owner surface, pipeline sections, and next slice. The spec correctly names one source of truth and keeps external readiness separate, and `generated_from`/`source_artifacts` ownership is mostly clear, but the current implementation still allows manually edited HTML planning claims to drift while tests stay green.

WROTE: .harness/artifacts/pu-020-adversarial-review/authority.md
