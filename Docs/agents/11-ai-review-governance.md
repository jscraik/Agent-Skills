# AI Review Governance

## Purpose

This document defines focused review expectations for AI-centered skill
infrastructure. Hosted required-check truth remains owned by
[CI Required Checks](/Docs/agents/12-ci-required-checks.md).

## Authoring-Family Review Scope

Changes to `skill-factory-router`, `skill-creator`, `skill-installer`,
`skill-builder`, or `plugin-creator` must preserve the focused
`authoring-family-gate` in `.github/workflows/skill-quality.yml`.

The gate runs:

```bash
bash Infrastructure/scripts/validate_skill_authoring_family.sh
```

Reviewers should require current-candidate evidence for contract and benchmark
parity, security and prompt-injection cases, structural eval coverage, and
projection integrity. In CI, `SKILL_FAMILY_LOCAL_MEMORY_MODE=optional` makes
only the Local Memory preflight advisory.

## Workflow Ownership

- `.github/workflows/pr-pipeline.yml` owns repository-wide pull-request jobs.
- `.github/workflows/skill-quality.yml` owns the path-triggered skill-quality and
  authoring-family jobs.
- `.harness/ci-required-checks.json` owns the registered required-check names.

Do not infer a dependency between separate workflows unless the live workflow
or required-check registry encodes it.

## Approval Expectations

- Do not call a relevant skill-authoring-family change ready while its focused
  gate is failing, missing, or stale for the current candidate.
- Keep local validation, hosted checks, review state, and merge readiness as
  separate evidence lanes.
- When workflow names or dependencies change, update the owning workflow,
  required-check registry, and this guidance in one validated change.
