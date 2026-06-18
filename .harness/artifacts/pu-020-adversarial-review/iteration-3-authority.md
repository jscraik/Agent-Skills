# Status

pass

Local code/test truth in `/Users/jamiecraik/dev/agent-skills`: the current patched state is route-truth authority sound for the PU-020 declutter slice after wrapper parity was added.

Validation evidence:
- Command: `python3 -m pytest Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q` -> blocked (ambient Xcode Python has no `pytest` module)
- Command: `UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q` -> pass (31 passed in 1.22s)

This proves local source/test truth for the capability matrix, SDK status payload, static HTML projection checks, and public wrapper parity. It does not prove CI, PR state, review-thread state, tracker state, hosted-docs truth, external SDK readiness, or merge readiness.

# Findings

No currently valid route-truth authority findings.

The prior wrapper-proof gap is now closed by `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:129`, which invokes both `bin/ask sdk status --json --robot` and `bin/skills-sdk status --json --robot` through the current interpreter and asserts each wrapper emits the same `data.skills_sdk_status` payload as the underlying SDK status route. This catches wrapper execution drift and argument-passing drift, including failure to pass `--json --robot` correctly. It does not catch payload-generation logic divergence because both wrappers invoke the same SDK target, and it does not prove wrapper version compatibility outside this checkout.

The matrix and HTML remain aligned on authority boundaries. `Infrastructure/config/skills-sdk/capability-matrix.v1.json:5` keeps `generated_from` on the stable capability-truth spec, `Infrastructure/config/skills-sdk/capability-matrix.v1.json:23` and `Infrastructure/config/skills-sdk/capability-matrix.v1.json:24` include the PU-020 spec and plan as source artifacts, and `artifacts/recommended-skills-sdk-pipeline.html:2245` through `artifacts/recommended-skills-sdk-pipeline.html:2247` declare the HTML as a projection of `./bin/ask sdk status --json --robot` and the capability matrix.

The stale-next-slice risk remains covered. The static docs row is preview-only and projection-only in `Infrastructure/config/skills-sdk/capability-matrix.v1.json:365` through `Infrastructure/config/skills-sdk/capability-matrix.v1.json:374` and `artifacts/recommended-skills-sdk-pipeline.html:2304`. Targeted search command: `rg -n "Next(?: slice)?: PU-0(19|20)" artifacts/recommended-skills-sdk-pipeline.html Infrastructure/config/skills-sdk/capability-matrix.v1.json .harness/specs/2026-06-17-skills-sdk-pu-020-route-truth-declutter-spec.md .harness/plan/2026-06-17-skills-sdk-pu-020-route-truth-declutter-plan.md` -> no matches; `rg` exit 1 means the stale labels are absent. PU-019 appears only as implemented/context text and PU-020 appears as current-slice/source context.

# Recommendation

Proceed with the PU-020 route-truth declutter slice from the authority lane. The smallest durable fixes are already present: HTML declares its sources, authority-bearing table cells are compared with live SDK status, source artifacts are checked for existence, completed/source-artifact PU IDs cannot reappear as next-slice labels, and both public wrappers are regression-tested for status payload parity. Keep readiness claims lane-separated unless CI, PR, review-thread, tracker, hosted-docs, and merge-readiness surfaces are checked independently in the closeout window.

WROTE: .harness/artifacts/pu-020-adversarial-review/iteration-3-authority.md
