---
name: gh-actions-fix
description: DEPRECATED alias of gh-workflow. Convert legacy invocations when requests explicitly name gh-actions-fix; immediately route to gh-workflow in ci_diagnose mode.
---

# gh-actions-fix (Deprecated Alias)

## Philosophy

- Keep a single canonical implementation (`gh-workflow`).
- Preserve compatibility for existing prompts during migration.
- Route immediately; do not duplicate operational logic.

## Variation guidance

- Keep routing deterministic but vary explanation detail by context.
- Use concise routing for direct invocations; add context notes for ambiguous requests.
- If PR/repo context is missing, branch to `intake` before canonical routing.

## When to use

Use this alias only when the request explicitly invokes `gh-actions-fix` or equivalent wording for failing PR checks/CI diagnosis.

## Inputs

- Original user request
- PR/repo context if present

## Outputs

- Deprecation notice
- Deterministic route to `gh-workflow` mode `ci_diagnose`
- Structured alias status with `schema_version: 1`

## Routing

- Target skill: `gh-workflow`
- Target mode: `ci_diagnose`
- Fallback mode when context is missing: `intake`

## Compatibility window

- Alias active now
- Sunset review date: **May 12, 2026**

## Constraints

- Redact secrets, tokens, and sensitive data by default.
- Do not execute local CI workflow logic in this alias.
- Do not route to any non-canonical GH skill.

## Procedure

1. Announce this skill is a deprecated alias.
2. Route to `gh-workflow` with mode `ci_diagnose`.
3. If context is missing, route with `intake` first.
4. Continue with canonical behavior only.

## Validation

Fail fast: **stop at the first failed gate**.

- Confirm route target is `gh-workflow`.
- Confirm mode is `ci_diagnose`.
- Confirm no circular route to this alias.

## Anti-patterns

- Re-implementing CI diagnosis logic in alias.
- Routing to deprecated peer aliases.
- Silent routing without deprecation notice.

## Examples

- "Use gh-actions-fix on PR 123" -> route to `gh-workflow` `ci_diagnose`.

## Legacy resources

- `scripts/inspect_pr_checks.py` (retained temporarily; canonical script is in `github/gh-workflow/scripts/`)

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## References

- `github/gh-workflow/SKILL.md`
- `references/contract.yaml`
- `references/evals.yaml`
