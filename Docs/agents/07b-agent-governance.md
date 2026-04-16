# Agent Governance

## Table of Contents
- [Prompting contract](#prompting-contract)
- [Coordination constraints](#coordination-constraints)
- [Communication checks](#communication-checks)
- [Claude Invocation Trust Boundary](#claude-invocation-trust-boundary)
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

## Claude Invocation Trust Boundary
- Claude GitHub Actions invocation is trust-gated to `author_association` values `OWNER`, `MEMBER`, or `COLLABORATOR`.
- Applicable events: `issue_comment`, `pull_request_review_comment`, `pull_request_review`, and `issues`.
- `issues` is restricted to `opened` only; `assigned` is intentionally excluded to prevent assigner/author-association bypasses.
- Canonical policy source: `.github/workflows/claude.yml` and [AI Review Governance](/Docs/agents/11-ai-review-governance.md).

## PR approval gates
- Treat `authoring-family-gate` as a governance approval gate for skill authoring family changes.
- The gate is satisfied only when `Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh` passes for all family members.
- CI executes this gate with `SKILL_FAMILY_LOCAL_MEMORY_MODE=optional`, so missing local-memory preflight is warning-only in CI while core contract/eval/security checks remain enforced.
- Do not mark a skill-authoring-family pull request merge-ready while this gate is failing or missing.

See [CI Required Checks](/Docs/agents/12-ci-required-checks.md) for the complete PR gate dependency policy.
