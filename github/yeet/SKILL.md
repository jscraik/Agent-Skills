---
name: yeet
description: DEPRECATED alias of gh-workflow. Convert legacy invocations when requests explicitly name yeet; immediately route to gh-workflow in pr_prepare mode.
---

# yeet (Deprecated Alias)

## Philosophy

- Keep the shortcut name while consolidating behavior in `gh-workflow`.
- Preserve compatibility for existing prompts during migration.
- Route immediately; do not duplicate operational logic.

## Variation guidance

- Keep routing deterministic but vary explanation detail by context.
- Use concise routing for direct invocations; add context notes for ambiguous requests.
- If repo/branch/auth context is missing, branch to `intake` before canonical routing.

## When to use

Use this alias only when the request explicitly invokes `yeet` or requests the one-flow stage/commit/push/open-PR action.

## Inputs

- Original user request
- Repo/branch/auth context if present

## Outputs

- Deprecation notice
- Deterministic route to `gh-workflow` mode `pr_prepare`
- Structured alias status with `schema_version: 1`

## Routing

- Target skill: `gh-workflow`
- Target mode: `pr_prepare`
- Fallback mode when context is missing: `intake`

## Compatibility window

- Alias active now
- Sunset review date: **May 12, 2026**

## Constraints

- Redact secrets, tokens, and sensitive data by default.
- Do not execute local PR workflow logic in this alias.
- Do not route to any non-canonical GH skill.

## Procedure

1. Announce this skill is a deprecated alias.
2. Route to `gh-workflow` with mode `pr_prepare`.
3. If context is missing, route with `intake` first.
4. Continue with canonical behavior only.

## Validation

Fail fast: **stop at the first failed gate**.

- Confirm route target is `gh-workflow`.
- Confirm mode is `pr_prepare`.
- Confirm no circular route to this alias.

## Anti-patterns

- Re-implementing one-shot PR prep logic in alias.
- Routing to deprecated peer aliases.
- Silent routing without deprecation notice.

## Examples

- "Yeet this branch" -> route to `gh-workflow` `pr_prepare`.

## Legacy resources

- `assets/yeet-small.svg`
- `assets/yeet.png`

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## References

- `github/gh-workflow/SKILL.md`
- `references/contract.yaml`
- `references/evals.yaml`
