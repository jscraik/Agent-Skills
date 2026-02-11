---
name: gh-address-comments
description: DEPRECATED alias of gh-workflow. Convert legacy invocations when requests explicitly name gh-address-comments; immediately route to gh-workflow in pr_review_comments mode.
---

# gh-address-comments (Deprecated Alias)

## Philosophy

- Keep a single canonical implementation (`gh-workflow`).
- Preserve compatibility for existing prompts during migration.
- Route immediately; do not duplicate operational logic.

## Variation guidance

- Keep routing deterministic but vary explanation detail by context.
- Use concise routing for direct invocations; add context notes for ambiguous requests.
- If PR/repo context is missing, branch to `intake` before canonical routing.

## When to use

Use this alias only when the request explicitly invokes `gh-address-comments` or asks to process PR review comments.

## Inputs

- Original user request
- PR/repo context if present

## Outputs

- Deprecation notice
- Deterministic route to `gh-workflow` mode `pr_review_comments`
- Structured alias status with `schema_version: 1`

## Routing

- Target skill: `gh-workflow`
- Target mode: `pr_review_comments`
- Fallback mode when context is missing: `intake`

## Compatibility window

- Alias active now
- Sunset review date: **May 12, 2026**

## Constraints

- Redact secrets, tokens, and sensitive data by default.
- Do not execute local comment-handling workflow logic in this alias.
- Do not route to any non-canonical GH skill.

## Procedure

1. Announce this skill is a deprecated alias.
2. Route to `gh-workflow` with mode `pr_review_comments`.
3. If context is missing, route with `intake` first.
4. Continue with canonical behavior only.

## Validation

Fail fast: **stop at the first failed gate**.

- Confirm route target is `gh-workflow`.
- Confirm mode is `pr_review_comments`.
- Confirm no circular route to this alias.

## Anti-patterns

- Re-implementing comment triage/fix logic in alias.
- Routing to deprecated peer aliases.
- Silent routing without deprecation notice.

## Examples

- "Use gh-address-comments on this PR" -> route to `gh-workflow` `pr_review_comments`.

## Legacy resources

- `scripts/fetch_comments.py` (retained temporarily; canonical script is in `github/gh-workflow/scripts/`)

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## References

- `github/gh-workflow/SKILL.md`
- `references/contract.yaml`
- `references/evals.yaml`
