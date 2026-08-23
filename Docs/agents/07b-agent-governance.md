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

- Treat `authoring-family-gate` in `.github/workflows/skill-quality.yml` as the
  focused governance gate for skill-authoring-family changes.
- The gate is satisfied only when
  `bash Infrastructure/scripts/validate_skill_authoring_family.sh` passes for
  the current candidate.
- CI executes this gate with `SKILL_FAMILY_LOCAL_MEMORY_MODE=optional`, so a
  missing Local Memory preflight is advisory while the remaining contract,
  eval, security, and projection checks stay enforced.
- Keep focused authoring-family evidence separate from the repository-wide
  required-check registry.

See [CI Required Checks](/Docs/agents/12-ci-required-checks.md) for the complete PR gate dependency policy.
