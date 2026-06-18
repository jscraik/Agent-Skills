# Status

issues_found

Local code/test truth is healthy for the patched route-truth slice:

- `python3 -m pytest Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q` -> pass, `13 passed, 148 subtests passed in 0.13s`
- Coordinator-provided focused lane: `python3 -m pytest Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q` -> pass, `30 passed and 155 subtests`
- Coordinator-provided wrapper lane: `python3 bin/ask sdk status --json --robot` -> pass
- Coordinator-provided wrapper lane: `python3 bin/skills-sdk status --json --robot` -> pass
- Worker spot-check wrapper lane: `python3 bin/ask sdk status --json --robot` -> pass
- Worker spot-check wrapper lane: `python3 bin/skills-sdk status --json --robot` -> pass

This proves the current local matrix/status/HTML route can load, the HTML declares the status command and matrix source, source artifacts exist, authority-bearing row cells match live SDK status, and checked stale `Next` / `Next slice` PU labels are absent for implemented-note and source-artifact PUs.

Status scope: this proof document reports `issues_found` because wrapper regression protection was still missing at iteration 2. That gap does not negate the sibling authority document's narrower `pass` for table-cell alignment and source-artifact stale-next checks; it is a separate downstream proof lane.

It does not prove CI, PR state, review-thread state, tracker state, hosted docs, external SDK readiness, or merge readiness.

# Findings

## P3: Public wrapper behavior is locally validated but not regression-protected by the HTML/status test

The second-pass fixes close the earlier proof gaps for projection parity and stale next-slice prevention. The parser now captures per-row owner-surface and next-slice cells, and the test asserts exact equality against live SDK status (`Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:16`, `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:129`). The stale-PU guard now also scans `source_artifacts`, so the previous self-stale PU-020 `Next slice` failure mode is covered (`Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:152`). The HTML now says `Current slice: PU-020` / `Current: PU-020 route-truth declutter`, not `Next` (`artifacts/recommended-skills-sdk-pipeline.html:2273`, `artifacts/recommended-skills-sdk-pipeline.html:2475`).

The remaining proof boundary is wrapper behavior. The regression test obtains runtime status by invoking `Infrastructure/bin/ask` through `sys.executable` (`Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:69`). That exercises the underlying ask command path, but it bypasses both public wrappers: `bin/ask` chooses either the current Python interpreter or uv before execing `Infrastructure/bin/ask` (`bin/ask:28`), while `bin/skills-sdk` injects the `sdk` topic before execing the same target (`bin/skills-sdk:28`). The coordinator and this worker both validated those wrapper commands locally, so this is not a current runtime failure. It is a regression-proof gap if future wrapper drift occurs while the Python target remains healthy.

Smallest durable fix: add one focused test that runs `python3 bin/ask sdk status --json --robot` and `python3 bin/skills-sdk status --json --robot`, parses both envelopes, and asserts their `data.skills_sdk_status` payloads match the runtime status payload used by the projection tests. Keep it local-only and do not claim CI, PR, hosted docs, tracker, review-thread, or merge readiness from it.

# Recommendation

Proceed after either accepting the wrapper proof as command-validation evidence for this slice or adding the small wrapper parity test above. I found no currently valid parity finding against owner surface, next-slice cells, source artifact existence, or stale `Next` / `Next slice` PU prevention in the patched state. The only remaining issue is proof placement: wrappers pass locally, but the regression test still proves the underlying Python entrypoint rather than the public `bin/ask` and `bin/skills-sdk` facades.

WROTE: .harness/artifacts/pu-020-adversarial-review/iteration-2-proof.md
