# Skills SDK PU-020 Route-Truth Declutter Plan

## First-Principles Gate

- User outcome: a cold agent or operator can ask what is true and what is next
  for the Skills SDK without reconciling the CLI, matrix, and static HTML by
  hand.
- Copied assumption to avoid: a new dashboard, registry, or eval runner would
  make the SDK workflow clearer.
- Smallest durable mechanism: keep the existing SDK status command authoritative
  and make projections prove they are projections.

## Slice

1. Mark the HTML pipeline artifact with the source command and source matrix.
2. Replace stale PU-019 next-slice copy with PU-020 route-truth declutter copy.
3. Keep matrix generated_from pointed at the stable capability-truth contract
   and include this PU-020 spec and plan in source_artifacts.
4. Add deterministic tests for projection source declaration, source artifact
   existence, completed-PU next-slice drift, and static-doc projection-only
   behavior.

## Validation

- ./bin/ask sdk status --json --robot
- ./bin/skills-sdk status --json --robot
- uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q

## Follow-Up Boundary

After this declutter slice passes, the next SDK expansion can add no-network
fixture coverage and runtime projection proof for vendored capsule
discoverability. That follow-up should reuse the same status route instead of
creating a parallel planning surface.
