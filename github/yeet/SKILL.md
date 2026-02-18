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
- This alias must immediately hand off to `gh-workflow`; do not perform PR/local git actions in `yeet`.

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
4. Do not execute alias-specific logic; continue with canonical `gh-workflow` behavior only.

## Validation

Fail fast: **stop at the first failed gate**.

- Confirm route target is `gh-workflow`.
- Confirm mode is `pr_prepare`.
- Confirm no circular route to this alias.

## Anti-patterns

- Re-implementing one-shot PR prep logic in alias.
- Routing to deprecated peer aliases.
- Silent routing without deprecation notice.
- Running local stage/commit/push actions directly in `yeet`.

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

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when consistent decision-making matters more than one-off execution because project context should drive the approach.
- Principle and mindset: prioritize tradeoffs and constraints over rigid checklists; understand why each step exists.
- Ask this to keep outcomes robust: Why is this the right default, and what could change this outcome?
- How do we adapt if constraints shift?
- What evidence is needed before choosing one path over another?

## Anti-patterns and caveats
- Avoid applying this playbook generically without checking repository-specific context.
- **NEVER** skip required validation gates when behavior changes.
- **DO NOT** use this skill as a rigid replacement for engineering judgment.
- **DON'T** ignore warnings or assume one pattern fits all repos.
- Common pitfall: treating anti-patterns as optional.
- Incorrect assumptions here can lead to fragile guidance.
- Warning: wrong sequencing can create avoidable regressions.

## Variation and adaptation
- Vary the workflow by team size, risk, and deployment target.
- Use different strategies for small, medium, and large changes.
- Adapt recommendations to the specific environment and avoid repetitive templates.
- Avoid generic or cookie-cutter responses; craft context-specific alternatives.
- Keep outputs diverse and not repetitive.
- Converge on a custom path only after evidence review.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of exploring multiple options and enabling the team to make safe decisions.
- Unlock confidence by explaining options and tradeoffs clearly.
- Feel free to be creative while staying rigorous and precise.
- Push boundaries with practical alternatives when simple recipes fail.
- Enable outcomes-oriented problem solving.
