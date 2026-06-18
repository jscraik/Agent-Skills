# Skills SDK PU-020 Route-Truth Declutter Spec

## Problem

The SDK status command is the intended operator route truth, but the static
HTML pipeline artifact can still introduce stale next-slice claims after the
capability matrix has moved on. PU-019 is now represented as an implemented
consumer lane in the capability matrix, while the HTML still advertises PU-019
as the next slice.

## Objective

Keep one authoritative route for Skills SDK capability truth:

- ./bin/ask sdk status --json --robot remains the operator entrypoint.
- Infrastructure/config/skills-sdk/capability-matrix.v1.json remains the
  structured source for capability status.
- artifacts/recommended-skills-sdk-pipeline.html remains a projection of those
  sources, not a second planning authority.

## Scope

- Declare the SDK status command and matrix source on the static HTML
  projection.
- Replace stale PU-019 next-slice language with the PU-020 route-truth
  declutter slice.
- Add tests that fail when completed PU notes reappear as next-slice claims in
  the HTML projection.
- Add tests that require declared source artifacts to exist and include the
  generated-from spec.

## Non-Goals

- Do not add a new dashboard, registry, or eval runner.
- Do not revive rooted projection mode.
- Do not claim hosted docs, CI, PR, review-thread, tracker, or merge-readiness
  truth from the local HTML projection.
- Do not broaden SDK execution behavior beyond status and projection truth.

## Acceptance

- The HTML projection explicitly points users back to ./bin/ask sdk status
  --json --robot and the capability matrix.
- No completed PU listed in implemented capability notes is advertised as
  Next or Next slice in the HTML projection.
- The matrix generated_from path is included in source_artifacts, and every
  source artifact exists.
- Focused SDK capability status tests pass.
