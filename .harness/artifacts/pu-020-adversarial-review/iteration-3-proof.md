# Status

pass

Local code/test truth for the PU-020 route-truth declutter slice is sound in the current patched state.

Line-number references in this proof are point-in-time snapshots. Re-verify them after any change to the referenced tests, matrix, or HTML artifact; behavior claims should continue to be checked by the named tests and searches.

Validation evidence:
- Command: `python3 -m pytest Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q` -> pass (31 passed, 157 subtests passed in 0.83s)
- Command: `python3 bin/ask sdk status --json --robot` -> pass
- Command: `python3 bin/skills-sdk status --json --robot` -> pass
- Command: `rg -n "Next(?: slice)?: PU-" artifacts/recommended-skills-sdk-pipeline.html Infrastructure/config/skills-sdk/capability-matrix.v1.json .harness/specs/2026-06-17-skills-sdk-pu-020-route-truth-declutter-spec.md .harness/plan/2026-06-17-skills-sdk-pu-020-route-truth-declutter-plan.md` -> pass (no matches; rg exit 1 means no matches)

This proves only the local matrix/status/HTML/test/wrapper route. It does not prove CI, PR state, review-thread state, tracker state, hosted docs, external SDK readiness, or merge readiness.

# Findings

No currently valid findings.

The prior public-wrapper regression-proof gap is fixed. `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:129` now runs both `python3 bin/ask sdk status --json --robot` and `python3 bin/skills-sdk status --json --robot`, then asserts each public wrapper's `data.skills_sdk_status` payload matches the runtime status payload at `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:144`-`145`.

The remaining PU-020 acceptance checks are covered in the current patched state: the HTML declares the SDK status command and matrix projection source at `artifacts/recommended-skills-sdk-pipeline.html:2245`-`2247`; source artifacts must exist and include `generated_from` at `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:97`-`102`; authority-bearing HTML cells match live SDK status at `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:147`-`157`; completed-note and source-artifact PU IDs are rejected as `Next` or `Next slice` labels at `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:159`-`177`; and the HTML labels PU-020 as current, not next, at `artifacts/recommended-skills-sdk-pipeline.html:2273` and `artifacts/recommended-skills-sdk-pipeline.html:2475`.

# Recommendation

Proceed with the PU-020 route-truth declutter slice from a local proof perspective. Public wrapper parity is now regression-protected, the stale next-slice guard covers source-artifact PUs, and the HTML remains a projection of the SDK status route and capability matrix rather than a second planning authority. Keep external readiness lanes separate until CI, PR, review-thread, tracker, hosted-docs, and merge-readiness truth are checked directly.

WROTE: .harness/artifacts/pu-020-adversarial-review/iteration-3-proof.md
