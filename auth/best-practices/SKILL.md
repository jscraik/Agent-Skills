---
name: best-practices
description: Review Better Auth setups and highlight secure integration best practices. Use for audits, config guidance, or debugging flows (not full implementation). Use when the user requests this capability.
---

# Better Auth Best Practices

Review Better Auth integrations for secure defaults, configuration quality, and production-readiness without taking over full implementation.

## Standards snapshot (March 2026)
- Use Better Auth’s current docs as the syntax source of truth, but keep repo-local findings grounded in the actual integration.
- Audit the real risk surfaces first: secrets, session handling, account linking, CSRF and origin checks, provider configuration, and plugin sprawl.
- Align review output to `OWASP Top 10:2025`, especially auth, session, and access-control risks.
- Prefer the smallest safe change set over broad auth redesign advice.

## Philosophy
- Review the real integration, not an imagined ideal architecture.
- Prioritize findings that materially reduce auth and session risk.
- Prefer small, testable remediations over broad rewrites.

## When to use
- Auditing an existing Better Auth setup for security gaps.
- Reviewing configuration choices, plugins, providers, or session behavior.
- Debugging auth flows, cookie/session handling, or deployment hardening.

## When not to use
- Building a new Better Auth integration from scratch.
- Migrating an app to Better Auth with code changes as the primary task.
- Reviewing a non-Better-Auth authentication stack.

## Required inputs
- Framework and runtime context.
- Database adapter or storage choice.
- Enabled auth features such as email/password, OAuth, passkeys, or organization flows.
- Current config, plugin list, and redacted provider details.

## Deliverables
- A prioritized findings summary with risks, rationale, and suggested fixes.
- Recommended config changes and expected file locations.
- Verification steps for secure deployment and flow testing.
- If requested, a structured status report with a `schema_version` field.

## Constraints
- Redact secrets, tokens, provider credentials, and sensitive user data by default.
- Do not recommend auth-flow changes without tying them to a concrete risk or failure mode.
- Keep guidance scoped to Better Auth rather than generic auth theory.

## Failure mode
- If the integration details are missing, ask for the specific config or file context instead of offering generic auth advice.
- If the task is actually implementation or migration, route to `create-auth` instead of stretching this skill.
- If a claimed issue depends on undocumented behavior, verify against the official Better Auth docs before stating it as fact.

## Workflow
1. Identify the framework, runtime, adapter, and current auth surface.
2. Review configured providers, plugins, and environment-variable handling.
3. Check session storage, cookie settings, trusted origins, CSRF and origin controls, and account-linking behavior.
4. Map the meaningful risks to a small, prioritized findings list.
5. Return the minimal safe remediation set plus verification steps.

## Security review areas
- Environment handling:
  - `BETTER_AUTH_SECRET`
  - `BETTER_AUTH_URL`
  - provider secrets
- Core config:
  - `baseURL`
  - `secret`
  - `trustedOrigins`
  - `rateLimit`
- Session behavior:
  - cookie mode
  - secondary storage
  - session persistence
  - expiry and refresh settings
- Provider and plugin safety:
  - account linking
  - plugin scope
  - passkey, 2FA, magic-link, or SSO configuration

## Tooling and references
- Use [better-auth.com/docs](https://better-auth.com/docs) for current syntax and option semantics.
- Load repo references as needed:
  - `references/providers.md`
  - `references/explain-error.md`
  - `references/contract.yaml`
  - `references/evals.yaml`
- Use assets only when the user needs packaged reference material or supporting visuals from `assets/`.

## Validation
- Verify the findings are tied to the actual config, not a generic checklist.
- Verify sign-in, sign-out, and session persistence behavior in a non-production environment when runtime testing is available.
- Verify every recommended change has a clear reason and a verification path.
- Fail fast at the first missing context that would change the audit outcome.

## Anti-patterns
- Recommending blanket auth redesigns when a few settings are the real issue.
- Disabling CSRF or origin checks without a documented mitigation.
- Ignoring account-linking implications when multiple providers are enabled.
- Treating plugin installation as safe without reviewing its new data or session surfaces.

## Examples
- Audit my Better Auth config for security gaps.
- Review my session settings and tell me what is risky.
- Check whether this Better Auth plugin setup is production-safe.

## See Also

| Skill | When to use together |
|---|---|
| [[security-threat-model]] | Run a threat model before applying best practices |
| [[security-ownership-map]] | Identify who owns the code being hardened |
| [[create-auth]] | Apply auth-specific best practices during implementation |
| [[1password]] | Manage secrets found during best practices review |

**Topic map:** [[security-ops]]

## Remember
Stay specific. A good auth review is concrete, prioritized, and verifiable, not a wall of generic security advice.
