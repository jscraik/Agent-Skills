# Status

pass

Local code/test truth reviewed in `/Users/jamiecraik/dev/agent-skills`: the current patched state closes the previously valid route-truth authority gaps for the scoped HTML projection.

Validation evidence:
- Command: `python3 -m pytest Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q` -> blocked (ambient Xcode Python has no `pytest` module)
- Command: `UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q` -> pass (30 passed in 0.91s)
- Canonical command note: the repo-standard form for this lane is `uv run --project Infrastructure --group test python -m pytest <target>`. The `UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache uv run --python 3.12 pytest ...` command above is local fallback evidence from this iteration, not the command form to canonize in docs or CI.

This proves only local code/test truth for the capability matrix, SDK status artifact parser, and static HTML projection checks. It does not prove the separate wrapper-regression gap recorded in iteration-2-proof, CI, PR state, review-thread state, tracker state, hosted docs, or merge readiness.

# Findings

No currently valid findings.

The prior authority finding that HTML `owner_surface` and `next_slice` cells could diverge from the runtime/matrix source is fixed. `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:16`-`58` now parses the table cells for every `data-capability-id`, and `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:147`-`157` asserts each HTML row's `owner_surface` and `next_slice` exactly match the runtime status row. The current HTML row for `static_docs` matches the matrix-owned owner and next-slice text at `Infrastructure/config/skills-sdk/capability-matrix.v1.json:365`-`374` and `artifacts/recommended-skills-sdk-pipeline.html:2304`.

The prior standalone stale-next-slice risk is also fixed for this slice. The HTML no longer labels PU-020 as `Next`; it says `Current slice: PU-020` at `artifacts/recommended-skills-sdk-pipeline.html:2273` and `Current: PU-020 route-truth declutter` at `artifacts/recommended-skills-sdk-pipeline.html:2475`. The regression guard now checks source-artifact PUs as well as implemented-note PUs at `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:141`-`159`, so a future `Next slice: PU-020` claim would fail while PU-020 remains in `source_artifacts`.

Source provenance is clear enough for the current contract. The matrix keeps `generated_from` on the stable PU-008 capability-truth spec at `Infrastructure/config/skills-sdk/capability-matrix.v1.json:5`, includes the PU-020 spec and plan in `source_artifacts` at `Infrastructure/config/skills-sdk/capability-matrix.v1.json:23`-`24`, and the test requires every source artifact to exist plus requires `generated_from` to be included in source artifacts at `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:97`-`102`. The HTML also declares the SDK status command and matrix source directly at `artifacts/recommended-skills-sdk-pipeline.html:2245`-`2247`.

Fix nature: iteration 2 changed both validation and projected artifacts. Test coverage was expanded to parse and compare every capability row's authority-bearing cells; the HTML projection was recomputed so PU-020 is labelled current instead of next; and the matrix/source-artifact checks remained the source boundary. The cited `static_docs` row is an example row, while the parity assertion covers all parsed capability rows.

# Recommendation

Treat the route-truth declutter fixes as locally authority-sound for table-cell alignment and source-artifact stale-next checks in this scoped slice. The sibling proof document's wrapper-regression gap is a separate downstream proof lane, not part of this authority status. Do not broaden this result into CI, PR, review-thread, tracker, hosted-docs, or merge-readiness claims without fresh evidence from those lanes.

WROTE: .harness/artifacts/pu-020-adversarial-review/iteration-2-authority.md
