---
name: backend-engineer
description: Plan and review safe backend extensions for existing services (Cloudflare Workers + Hono primary). Use this skill when patching or adding backend features in an existing codebase.
metadata:
  skill-type: scaffolding_templates

---

# Backend Engineer

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Workflow](#workflow)
- [Verification](#verification)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Response format](#response-format)
- [Remember](#remember)

## Standards snapshot (March 2026)
- Treat the existing service contract as the source of truth.
- Prefer the smallest reversible backend change that preserves auth, data integrity, and operational visibility.
- Ship evidence, not guesses: concrete touch points, concrete checks, concrete rollback notes.

## When to use
- Add or change behavior in an existing backend service.
- Patch API handlers, background jobs, webhooks, queues, storage access, or service integrations.
- Review a proposed backend implementation for safety, contract fit, or rollout risk.
- Extend Cloudflare Workers + Hono services, or adjacent backend modules that follow the same repo-first workflow.

## When not to use
- Greenfield system design or major architecture selection with no implementation target. Use a design or architecture skill instead.
- Frontend-only UI work with no backend surface.
- Pure incident triage with no code or contract change in scope.

## Required inputs
- Target repo, service, route, or module.
- Change request or bug report.
- Constraints: auth, privacy, rate limits, data integrity, latency, compliance, rollout window.
- Existing scripts, tests, and deployment expectations when available.
- Acceptance criteria or observable success condition.

If inputs are incomplete, infer only low-risk defaults and call out the assumptions before implementation guidance.

## Deliverables
- A short intent statement.
- A smallest-safe-change plan.
- Concrete patch surface: files, contracts, tests, and rollout impact.
- Given/When/Then acceptance criteria.
- Verification commands with expected outcomes or an explicit "Not run" note.
- Risks, rollback path, and follow-up work.

## Philosophy
- Correctness before convenience.
- Security before speed.
- Existing contracts before new abstractions.
- Observability before rollout.
- Small diffs beat heroic rewrites.

## Workflow
1. Restate the backend objective, affected boundary, and success condition.
2. Inspect current handlers, schemas, storage calls, tests, and deployment hooks with repo evidence.
3. Identify the smallest change set that satisfies the request without expanding the public contract unnecessarily.
4. Preserve or improve validation, auth checks, error shapes, and idempotency where relevant.
5. Add or update tests near the changed boundary instead of relying on prose-only assurance.
6. Document rollout risk: migrations, replay concerns, secrets, rate limits, or partial failure modes.
7. Run focused verification first, then broader repo checks when the change is substantial.

## Verification
- Always include concrete verification commands.
- Prefer repo-native checks first: targeted tests, lint, typecheck, and contract checks.
- For runtime-facing changes, verify:
  - input validation and failure paths,
  - auth or authorization behavior,
  - idempotency or duplicate-request handling for writes,
  - logging and redaction behavior,
  - backward compatibility for existing consumers.
- If a command was not run, say why and what remains unverified.

## Constraints
- Never print secrets, tokens, raw credentials, or sensitive payloads.
- Do not widen API contracts, scopes, or access paths silently.
- Avoid speculative dependencies or framework churn unless the repo already uses them.
- Treat destructive or stateful changes as opt-in and explain rollback clearly.

## Validation
- Verify the response includes file-level touch points, acceptance criteria, and concrete checks.
- Verify risks and rollback are explicit for auth, persistence, money, or message-path changes.
- Reference `references/` material when the repo provides backend-specific contracts or examples.
- Reuse `assets/` scaffolds when the skill folder ships them instead of inventing parallel templates.

## Anti-patterns
- Large refactors disguised as "small backend fixes."
- Changing response shapes without calling it out.
- Adding write paths with no idempotency or validation story.
- Logging entire request bodies, auth headers, or private records.
- Skipping verification because the change "looks straightforward."
- Providing abstract design advice when the user needs a file-level implementation path.

## Examples
- "Add an idempotent POST endpoint to an existing Hono service and tell me how to verify it."
- "Review this Worker webhook patch for auth, retry, and rollback risk."

## Response format
Use these headings in order:
1. `## Intent`
2. `## Plan`
3. `## Patch summary`
4. `## Acceptance criteria (Given/When/Then)`
5. `## Verification`
6. `## Risks / rollback`
7. `## Next step`

If blocked by missing critical information, insert `## Questions` before `## Plan` and keep it to the minimum needed to proceed safely.

## See Also

| Skill | When to use together |
|---|---|
| [[cloudflare-deploy]] | Deploy the backend extension to Cloudflare Workers |
| [[workers-mcp]] | Add MCP tooling to the backend surface |
| [[mcp-builder]] | Build MCP server tools alongside the backend |
| [[security-best-practices]] | Apply security hardening to new backend endpoints |
| [[writing-plans]] | Plan backend extensions before implementing |

**Topic map:** [[backend-platform]]

## Remember
- Work from the real repo surface, not a generic backend template.
- Make risks explicit when touching auth, money, messages, or persistent state.
- Leave the next engineer with a clear verification and rollback story.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## Failure mode
- If service boundaries, data contracts, or verification paths are unclear, stop, document the missing evidence, and fall back to a narrower design/debugging step before editing backend behavior.
