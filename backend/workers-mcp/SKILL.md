---
name: workers-mcp
description: Create and deploy production-ready MCP servers on Cloudflare Workers. Use when building a Workers-hosted MCP server with auth, billing, and operational guardrails.
---

# Workers MCP

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Workflow](#workflow)
- [Validation](#validation)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [Remember](#remember)

## Standards snapshot (March 2026)
- Follow the Model Context Protocol line represented by the 2025-06-18 baseline and 2025-11-25 release lineage when examples disagree.
- Treat Cloudflare Workers, Durable Objects, D1, and Vectorize as operational choices with concrete tradeoffs, not default checkboxes.
- Keep auth, billing, and deploy safety visible from the first design pass.

## When to use
- Build or extend an MCP server that will run on Cloudflare Workers.
- Design a Workers-hosted MCP server with auth, billing, licensing, or operational controls.
- Review deployment or runtime safety for a Workers MCP surface.

## When not to use
- Standard MCP integrations that do not need Workers hosting or billing/auth complexity. Use [`mcp-builder`](/Users/jamiecraik/dev/agent-skills/backend/mcp-builder/SKILL.md).
- Frontend-only ChatGPT Apps UI work with no server/runtime ownership.
- Generic Cloudflare app deployment that is not MCP-specific.

## Required inputs
- Deployment target and environment shape: local, preview, staging, production.
- Auth requirements: provider, scopes, callback expectations, token model.
- Billing or entitlement requirements, if any.
- Data/storage plan: D1, Durable Objects, KV, R2, Vectorize.
- Expected tool surface and any operational limits.

## Deliverables
- Workers MCP architecture or scaffold plan.
- Tool schema and handler guidance aligned to the Worker runtime.
- Auth, billing, storage, and secret-management notes.
- Deploy, smoke-test, and rollback guidance.

## Philosophy
- Safe-by-default tools, explicit-by-default operations.
- Keep the edge runtime simple and observable.
- Separate protocol correctness from platform concerns so neither gets hand-waved.
- Deployment readiness matters as much as handler correctness.

## Workflow
1. Lock the hosting and environment model before discussing tools.
2. Define the MCP surface with schemas, idempotency expectations, and error handling.
3. Map operational dependencies: auth, billing, storage, secrets, queues, or background work.
4. Choose Cloudflare primitives intentionally instead of using every service by habit.
5. Validate local and preview behavior before treating production rollout as ready.
6. Document rollback, migration, and secret-rotation implications explicitly.

## Validation
- Verify the design fits the Worker runtime and does not rely on unavailable server assumptions.
- Verify every public tool has explicit schema and safety expectations.
- Verify auth, billing, and secret boundaries are described concretely.
- Verify the skill references bundled `references/`, `scripts/`, or `assets/` helpers when they exist.
- Reuse scaffolds or examples from the skill folder instead of creating parallel templates.

## Constraints
- Do not print secrets, tokens, credentials, or sensitive customer data.
- Destructive or state-changing operations must require explicit confirmation and a rollback story.
- Do not auto-deploy, migrate production data, or widen auth scope without explicit approval.
- Keep Cloudflare-specific networking, bindings, and secret assumptions explicit.

## Anti-patterns
- Treating Workers hosting as a generic Node runtime.
- Mixing auth, billing, storage, and tool design into one opaque step.
- Shipping preview-ready code and calling it production-ready without rollout checks.
- Using too many platform primitives without explaining why each one is necessary.

## Examples
- "Design a Workers-hosted MCP server with Auth0, Stripe, and D1."
- "Review this Workers MCP plan for deploy, auth, and rollback risk."

## See Also

| Skill | When to use together |
|---|---|
| [[mcp-builder]] | Build the MCP server before deploying it on Workers |
| [[cloudflare-deploy]] | Deploy the full Workers-hosted MCP stack |
| [[chatgpt-apps]] | Connect the Workers MCP server to a ChatGPT App |
| [[security-best-practices]] | Apply auth and security hardening to the MCP endpoint |
| [[openai-docs]] | Reference MCP schema and tool definitions |

**Topic map:** [[backend-platform]]

## Remember
- Platform fit is part of product fit.
- A production-ready Workers MCP server needs protocol discipline and operational discipline.
- Make rollout risk legible before someone learns it in production.
