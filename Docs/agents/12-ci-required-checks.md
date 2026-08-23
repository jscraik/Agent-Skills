# CI Required Checks

## Purpose

This document explains where current required-check truth lives. It does not
replace the executable workflow or registry.

## Authoritative Surfaces

- `.harness/ci-required-checks.json` registers required hosted check names.
- `.github/workflows/pr-pipeline.yml` owns the repository-wide pull-request job
  graph.
- `.github/workflows/security-scan.yml` owns the registered `gitleaks` check.
- `.github/workflows/skill-quality.yml` owns the path-triggered
  `authoring-family-gate`; that focused job is separate from the global
  required-check registry.

Within `pr-pipeline.yml`, current jobs include `pr-template`, `linear-gate`,
`risk-policy-gate`, `dependency-review`, `actions-pinning`,
`consistency-drift-advisory`, `consistency-drift-health`, `lint`, `typecheck`,
`test`, `audit`, `check`, and `memory`.

## Dependency Policy

Use the live `needs` edges in each workflow as dependency truth. Do not infer a
cross-workflow dependency for `authoring-family-gate`. For relevant skill-family
changes, require that focused gate in addition to the current registered checks.

The opening repository-wide sequence is:

1. `pr-template`
2. `linear-gate`, after `pr-template`
3. `risk-policy-gate`, after both preceding jobs
4. downstream validation and policy jobs, as declared by their live `needs`
   edges

## Governance Updates

When a job name, dependency edge, or gate owner changes:

1. Update the owning workflow.
2. Reconcile `.harness/ci-required-checks.json` with hosted check reality.
3. Update `Docs/agents/04-validation.md`,
   `Docs/agents/07b-agent-governance.md`, and this file when their claims change.
4. Run the repository's check-name parity or nearest executable workflow
   validator. If that validator is unavailable, report the lane as blocked
   rather than inferring parity from prose.
