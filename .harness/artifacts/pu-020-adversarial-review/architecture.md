# Status

issues_found

Local code/test truth: the focused SDK status commands and tests pass when the uv cache is routed to a sandbox-writable temp path.

- Command: ./bin/ask sdk status --json --robot -> pass
- Command: ./bin/skills-sdk status --json --robot -> pass
- Command: UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q -> pass (28 passed, 120 subtests passed)
- Command: uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q -> blocked by sandbox cache access to /Users/jamiecraik/.cache/uv, then retried with temp UV_CACHE_DIR

External readiness truth: I did not verify live CI, PR state, review-thread state, tracker state, hosted docs, or merge readiness. The local HTML projection does not prove those lanes.

# Findings

## P2: The slice removes stale PU-019 planning but creates a new self-stale Next claim

The spec says the static HTML must remain a projection and not a second planning authority (.harness/specs/2026-06-17-skills-sdk-pu-020-route-truth-declutter-spec.md:13). The implementation still places PU-020 in "Next" copy inside the projection: artifacts/recommended-skills-sdk-pipeline.html:2273 says "Next slice: PU-020", and artifacts/recommended-skills-sdk-pipeline.html:2475 says "Next: PU-020 route-truth declutter".

That is a small wording issue now, but it becomes the same route-truth failure immediately after this slice lands: a completed declutter slice will still be advertised as next. The new guard only harvests completed PU IDs from implemented capability notes and rejects those under "Next" (Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py:113). PU-020 is stored in generated_from/source_artifacts, not implemented capability notes (Infrastructure/config/skills-sdk/capability-matrix.v1.json:5 and Infrastructure/config/skills-sdk/capability-matrix.v1.json:23), so the guard will not catch the stale PU-020 "Next" labels.

Smallest durable fix: rename those HTML labels from "Next" to "Current slice" or "Route-truth sync", or remove the PU-specific next banner entirely and let the status table own next_slice values. Add a focused test that extracts the PU ID from runtime_status["generated_from"] and rejects "Next" or "Next slice" labels for that PU in the HTML projection.

## P2: generated_from makes a declutter spec look like the whole matrix owner

The objective names Infrastructure/config/skills-sdk/capability-matrix.v1.json as the structured source for capability status and the HTML as its projection (.harness/specs/2026-06-17-skills-sdk-pu-020-route-truth-declutter-spec.md:15). The plan then moves matrix generated_from to the PU-020 declutter spec (.harness/plan/2026-06-17-skills-sdk-pu-020-route-truth-declutter-plan.md:17), and the current matrix now exposes that as the top-level generated_from value (Infrastructure/config/skills-sdk/capability-matrix.v1.json:5).

That worsens artifact ownership because a narrow cleanup spec now appears to generate or own the entire capability matrix, including older implemented lifecycle, review, plugin-readiness, rollback, install, and placeholder rows. This hides the larger SDK architecture issue the slice is trying to avoid: the matrix is both route truth and an accumulating planning ledger, while generated_from can only point at one document.

Smallest durable fix: keep generated_from pointed at the stable capability-truth/matrix contract, or split provenance into generated_from for the matrix contract and last_updated_by or projection_update_source for PU-020. Keep the PU-020 spec and plan in source_artifacts for auditability, but do not make the declutter spec the apparent owner of the whole status surface.

# Recommendation

Proceed with the declutter direction only after tightening the two ownership edges above. The implementation does not add a new dashboard, registry, eval runner, rooted projection mode, or external readiness claim, and the local focused checks pass. The remaining risk is not a big SDK rewrite; it is that the status surface still carries planning language and single-field provenance that will age badly. The smallest durable fix is wording plus one test for the current generated_from PU, and a provenance split that keeps the matrix owner distinct from the latest cleanup slice.

WROTE: .harness/artifacts/pu-020-adversarial-review/architecture.md
