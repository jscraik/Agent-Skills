---
name: cloudflare-deploy
description: Deploy applications and infrastructure to Cloudflare using Workers, Pages, and related platform services. Use when the user asks to deploy, host, publish, or set up a project on Cloudflare.
---

# Cloudflare Deploy

Route deployment and platform setup work to the correct Cloudflare product with authenticated, product-aware guidance.

## Standards snapshot (March 2026)
- Choose the Cloudflare product based on runtime, state, and delivery needs before giving commands.
- Verify authentication before any deploy or publish instruction.
- Keep product routing explicit: Workers, Pages, Durable Objects, D1, R2, Queues, AI, and networking all have different operating models.
- Prefer the narrowest correct product path over platform-general advice.

## Philosophy
- Route first, then recommend commands.
- Cloudflare advice should be product-specific, not platform-generic.
- Authenticated, minimal next steps beat sprawling platform tours.

## When to use
- Deploying or publishing a project on Cloudflare.
- Choosing between Cloudflare platform products for a new deployment.
- Setting up runtime, storage, AI, networking, or security components on Cloudflare.

## When not to use
- Working on non-Cloudflare deployment targets.
- Performing framework implementation work with no deployment or platform decision.
- Troubleshooting unrelated hosting providers.

## Required inputs
- The deployment goal: host, publish, route traffic, store data, run AI, or secure an app.
- The app shape: static site, full-stack app, edge function, workflow, container, or multi-tenant platform.
- Current repo or project context.
- Available Cloudflare auth and account context.

## Deliverables
- A product route recommendation or a deployment path.
- Exact next-step references for the chosen product family.
- Auth and prerequisite checks before deploy commands.
- If requested, a structured status report with a `schema_version` field.

## Constraints
- Redact secrets, API tokens, account identifiers, and sensitive deployment details by default.
- Do not imply a deploy was executed when auth, network, or policy blocked it.
- Do not mix guidance across incompatible Cloudflare product families.

## Failure mode
- If auth is missing, stop with the exact `wrangler` preflight needed.
- If the product category is unclear, route to the smallest decision tree instead of guessing.
- If network or sandbox policy blocks deploy execution, report that blocker explicitly rather than implying the deploy was attempted.

## Authentication preflight
Run before `wrangler deploy`, `wrangler pages deploy`, or equivalent project commands:

```bash
npx wrangler whoami
```

If unauthenticated:
- local interactive flow: `wrangler login`
- CI or automation: provide `CLOUDFLARE_API_TOKEN`

## Routing workflow
1. Determine whether the need is compute, storage, AI, networking, security, media, or IaC.
2. Choose the specific Cloudflare product family.
3. Load the relevant reference subtree for that product.
4. Verify auth and product-specific prerequisites.
5. Return the exact next deploy or setup steps for that path.

## Product routing
- Compute and runtime:
  - `references/workers/`
  - `references/pages/`
  - `references/durable-objects/`
  - `references/workflows/`
  - `references/containers/`
- Storage and data:
  - `references/kv/`
  - `references/d1/`
  - `references/r2/`
  - `references/queues/`
  - `references/hyperdrive/`
- AI and ML:
  - `references/workers-ai/`
  - `references/vectorize/`
  - `references/agents-sdk/`
  - `references/ai-gateway/`
- Networking and security:
  - `references/tunnel/`
  - `references/spectrum/`
  - `references/turnstile/`
  - `references/waf/`
  - `references/api-shield/`
- IaC and tooling:
  - `references/wrangler/`
  - `references/terraform/`
  - `references/pulumi/`
  - `references/miniflare/`

## Tooling and references
- Use `wrangler` as the primary operator surface when command execution is in scope.
- Load only the product references needed for the current route.
- Core reference files:
  - `references/contract.yaml`
  - `references/evals.yaml`
  - `agents/openai.yaml`

## Validation
- Verify the selected product family matches the user’s actual deployment need.
- Verify auth and prerequisite state before deploy instructions.
- Verify the response names the right reference subtree for follow-on detail.
- Fail fast at the first auth or product-selection blocker.

## Anti-patterns
- Recommending Workers for every Cloudflare task by default.
- Mixing platform setup guidance across incompatible product families.
- Giving deploy commands before checking auth.
- Claiming deploy execution when sandbox or network policy prevented it.

## Examples
- Which Cloudflare product should I use for this edge API plus queue pipeline?
- Help me deploy this app to Pages and wire the right storage products.
- I need Cloudflare-hosted AI inference plus vector search. What should I set up?

## See Also

| Skill | When to use together |
|---|---|
| [[workers-mcp]] | Deploy MCP server as part of the Cloudflare stack |
| [[cf-crawl]] | Run Cloudflare Browser Rendering crawls on the deployed site |
| [[backend-engineer]] | Extend the backend before deploying |
| [[fixing-metadata]] | Fix OG/meta tags on deployed pages |
| [[verification-before-completion]] | Verify deployment is healthy before completing |

**Topic map:** [[backend-platform]]

## Remember
Cloudflare is a platform family, not one product. Route first, then go deep.
