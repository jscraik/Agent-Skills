---
schema_version: 1
artifact_id: harness-media-guidance
artifact_type: he-media-guidance
canonical_slug: harness-media-guidance
title: Harness Media Guidance
harness_stage: he-artifact
status: active
date: 2026-05-09
traceability_required: false
---

# Harness Media Guidance

Generated images that support Harness Engineering specs, plans, reviews, evals,
or phase heartbeats should be preserved here after generation.

For future image generations like plan before/after infographics:

- leave the original generated image in `/Users/jamiecraik/.codex/generated_images/`;
- copy the selected PNG into `.harness/media/`;
- use a dated, descriptive filename tied to the plan or slice;
- add a sidecar Markdown artifact with purpose, source cache path, repository
  path, and linked plan/spec/review/eval context;
- reference the repository copy from HE artifacts rather than the generated-image
  cache.
