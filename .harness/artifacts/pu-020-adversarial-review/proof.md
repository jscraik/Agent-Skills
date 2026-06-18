# Status

issues_found

Local code/test truth is mostly healthy: the requested focused validation passed locally with both wrapper commands and the uv pytest lane:

- `./bin/ask sdk status --json --robot` -> pass
- `./bin/skills-sdk status --json --robot` -> pass
- `uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q` -> pass, `28 passed in 0.99s`

This proves the local SDK status route can load the capability matrix, the HTML has the expected status rows, source declarations exist, source artifacts exist, and the current static artifact no longer advertises PU-019 with the exact `Next: PU-019` or `Next slice: PU-019` pattern.

It does not prove CI, PR state, review-thread state, tracker state, hosted docs, or merge readiness.

# Findings

## P2: HTML projection tests do not prove row content is projected from the matrix

The acceptance claim says `artifacts/recommended-skills-sdk-pipeline.html` remains a projection of `./bin/ask sdk status --json --robot` and `Infrastructure/config/skills-sdk/capability-matrix.v1.json` rather than a second planning authority. The current tests prove row presence, status vocabulary, runtime status, and title text, but they do not assert that each HTML row's owner surface or next-slice cell equals the runtime/matrix row.

Evidence:

- `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:88` checks matrix capability IDs equal parsed HTML row IDs.
- `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:93` checks HTML status attributes/text match matrix statuses.
- `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:100` checks runtime IDs, statuses, and titles appear in HTML rows.
- `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:113` only forbids exact completed-PU `Next` / `Next slice` advertisements derived from implemented capability `notes`.
- `Infrastructure/config/skills-sdk/capability-matrix.v1.json:301` defines the implemented `refs_ingestion` next slice, and `artifacts/recommended-skills-sdk-pipeline.html:2298` currently matches it, but that equality is not asserted.

Why this matters: a stale non-PU next-slice claim, a stale owner surface, or a stale next-slice sentence that does not use the exact `Next: PU-id` pattern could pass the acceptance tests while still making the HTML table a second planning authority. The current implementation happens to look aligned in the checked slice, but the test proof is narrower than the claim.

Smallest durable fix: extend `CapabilityStatusParser` to capture table cells by row, then assert for every capability that the HTML owner-surface cell and next-slice cell equal the runtime status row. Keep the existing completed-PU guard as an additional regression check.

# Recommendation

Keep the slice, but tighten the acceptance proof before treating it as done. The blocked mise/uv concern did not reproduce in this review when cache/state paths were pinned to temp locations; both SDK wrapper commands and the uv pytest lane passed locally. The remaining weakness is proof quality: the tests should compare the HTML row content against the runtime/matrix row for owner surface and next slice, not just status/title plus a narrow PU regex. That is the smallest fix that makes the test suite prove the route-truth declutter claim without adding a new dashboard, registry, eval runner, projection mode, plugin, or skill.

WROTE: .harness/artifacts/pu-020-adversarial-review/proof.md
