# Agent Governance

## Table of Contents
- [Prompting contract](#prompting-contract)
- [Coordination constraints](#coordination-constraints)
- [Communication checks](#communication-checks)
- [PR approval gates](#pr-approval-gates)

## Prompting contract
- Keep output concise and actionable, with minimal diffs.
- Prefer repo evidence over assumptions.
- Report unknowns before proceeding if a decision blocks progress.

## Coordination constraints
- Do not add deps or toolchain changes unless explicitly requested.
- Do not leave the workflow state ambiguous: list next action after each edit batch.

## Communication checks
- If a user names a tool or skill, verify it exists before selecting fallback behavior.
- Verify documented file paths exactly before commit (for example `.diagram/` path references).

## PR approval gates
- Treat `authoring-family-gate` as a governance approval gate for skill authoring family changes.
- The gate is satisfied only when `scripts/validate_skill_authoring_family.sh` passes for all family members.
- Do not mark a skill-authoring-family pull request merge-ready while this gate is failing or missing.

See [CI Required Checks](./12-ci-required-checks.md) for the complete PR gate dependency policy.
