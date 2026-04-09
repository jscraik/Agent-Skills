---
name: create-auth
description: Implement or migrate Better Auth in TypeScript or JavaScript apps with secure defaults. Use when the user wants Better Auth added or changed in code, not just reviewed.
metadata:
  skill-type: scaffolding_templates
---

# Create Auth

Build or migrate Better Auth integrations for TypeScript and JavaScript apps with secure defaults, incremental rollout, and explicit verification.

## Standards snapshot (March 2026)
- Start from the smallest viable auth surface, then layer features after the core flow works.
- Keep implementation and rollout aligned to `OWASP Top 10:2025` expectations for auth, session, and access-control safety.
- Prefer incremental migration over full rewrites when existing auth already exists.
- Validate live auth behavior, not just config shape.

## Philosophy
- Secure defaults come first; feature richness comes second.
- Build the smallest working auth surface before layering plugins and providers.
- Favor incremental cutovers over high-risk rewrites.

## When to use
- Adding Better Auth to a new app.
- Migrating an existing app to Better Auth.
- Adding concrete auth features such as OAuth, passkeys, 2FA, magic links, or org flows.

## When not to use
- Performing a review-only audit with no implementation work.
- Working on a non-Better-Auth authentication stack.
- Discussing product-level auth trade-offs without committing to implementation.

## Required inputs
- Framework and runtime context.
- Database adapter or storage choice.
- Desired auth features and plugins.
- Existing auth constraints, migration risks, or route structure.

## Deliverables
- Step-by-step setup or migration path.
- Required files and expected file locations.
- Schema and migration commands.
- Verification steps for sign-up, sign-in, sign-out, and session persistence.
- If requested, a structured status report with a `schema_version` field.

## Constraints
- Redact secrets, tokens, client secrets, and sensitive auth data by default.
- Do not invent provider credentials, callback URLs, or migration assumptions.
- Do not skip schema or route validation just because the config looks correct.

## Failure mode
- If the user only wants review or guidance, route to `best-practices`.
- If framework or adapter details are missing and they materially change the setup path, stop and ask for them.
- If required secrets or provider details are unavailable, block safely rather than inventing a partial setup.

## Workflow
1. Identify framework, runtime, database adapter, and current auth state.
2. Choose the smallest safe Better Auth setup for that environment.
3. Create the server config and client integration points.
4. Add routes or handlers and the requested plugins.
5. Generate or apply schema changes.
6. Validate the full auth flow before expanding feature scope.

## Implementation lanes
- New project:
  - install Better Auth
  - create auth config
  - add route handler
  - run schema setup
  - validate core flow
- Existing project without auth:
  - map current app structure
  - integrate Better Auth with minimal disruption
  - wire existing pages or flows
  - validate session behavior
- Migration:
  - audit current auth
  - plan incremental cutover
  - migrate features in batches
  - verify no session or route regressions

## Tooling and references
- Use [better-auth.com/docs](https://better-auth.com/docs) for current syntax.
- Use local references as needed:
  - `references/contract.yaml`
  - `references/evals.yaml`
- Use assets only when the task benefits from packaged auth examples or supplemental materials in `assets/`.

## Validation
- Verify sign-up, sign-in, sign-out, and session persistence.
- Verify plugin-dependent behavior after each new feature is added.
- Verify migrations or generated schema changes ran successfully.
- Fail fast at the first missing prerequisite or broken auth flow.

## Anti-patterns
- Enabling too many auth features before the base flow works.
- Skipping migrations after adding plugins.
- Disabling CSRF or origin checks without mitigations.
- Storing secrets in source control or echoing them in logs.

## Examples
- Add Better Auth to a Next.js app with Prisma.
- Migrate this existing auth flow to Better Auth incrementally.
- Add passkeys and Google OAuth to this Better Auth setup.

## See Also

| Skill | When to use together |
|---|---|
| [[security-best-practices]] | Apply secure defaults during auth implementation |
| [[1password]] | Inject auth secrets via 1Password CLI |
| [[mcp-builder]] | Secure MCP server authentication using Better Auth |
| [[security-threat-model]] | Model auth attack surface before implementing |

**Topic map:** [[security-ops]]

## Remember
Treat auth rollout like infrastructure. The core flow must work cleanly before you make it richer.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
