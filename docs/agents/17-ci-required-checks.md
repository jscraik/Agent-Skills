# CI Required Checks

## Table of Contents
- [Purpose](#purpose)
- [Workflow gate checks](#workflow-gate-checks)
- [Dependency policy](#dependency-policy)
- [Required-check governance updates](#required-check-governance-updates)

## Purpose
This document records required CI gate behavior for pull requests and the dependency policy that protects skill-authoring-family governance.

## Workflow gate checks
Within `.github/workflows/pr-pipeline.yml`, the governance-critical checks are:
- `pr-template`
- `repo-validate`
- `authoring-family-gate`
- `harness-preflight`

`authoring-family-gate` runs:
- `bash scripts/validate_skill_authoring_family.sh`

This gate enforces contract/eval/security behavior for:
- `utilities/skill-builder`
- `skills-system/skill-creator`
- `skills-system/skill-installer`
- `skills-system/plugin-creator`

## Dependency policy
`harness-preflight` must depend on both:
- `repo-validate`
- `authoring-family-gate`

Policy intent:
- Avoid running harness checks before authoring-family contract/eval/security checks pass.
- Keep repository validation and authoring-family governance as prerequisites for downstream CI gates.

## Required-check governance updates
When job names, dependency edges, or gate responsibilities change:
1. Update `.github/workflows/pr-pipeline.yml` comments and job definitions.
2. Update `docs/agents/04-validation.md` and `docs/agents/07b-agent-governance.md`.
3. Update `docs/agents/17-ci-required-checks.md` to reflect current required check names and dependency policy.
4. Reconcile any external required-check registries (for example `.harness/ci-required-checks.json`) with workflow reality.
