# mKit Boilerplate Guide (Cloudflare Workers)

Use this guide when implementing or extending the mKit MCP boilerplate in
`/Users/jamiecraik/dev/mKit`.

## Purpose

mKit is a Cloudflare Workers boilerplate that ships an MCP server with OAuth 2.1,
Stripe billing, and OpenAI Apps SDK UI integration.

## Prerequisites

- Node.js 20+
- pnpm
- Wrangler CLI
- Cloudflare account
- Optional: Stripe + OAuth provider credentials

## Key entry points

- Worker entry: `src/worker/index.ts`
- MCP server: `src/worker/mcp.ts`
- Routes: `src/worker/routes.ts`

## Tool registration

- Add a file under `src/tools/free/` or `src/tools/paid/`.
- Register the tool in `src/tools/index.ts`.

## Apps SDK UI widgets

- Add an HTML file in `src/app/routes/`.
- Add the matching React component in `src/app/components/`.
- Verify the route appears in the generated manifest at build time.

## Auth providers

- Add a provider under `src/auth/`.
- Wire it into routing in `src/worker/routes.ts`.

## Billing integration

- Update `src/billing/stripe.ts`.
- Ensure paid tool registration uses `src/tools/paid/`.

## Local dev and verification

- Install dependencies: `pnpm install`
- Configure env: `cp .env.example .env` and fill required values
- Run UI + worker (separate terminals): `pnpm dev` and `pnpm dev:worker`
- Verify: `/mcp` returns a non-5xx response

## Deployment

- Build + deploy: `pnpm build-deploy`
- Verify the worker URL responds to `/mcp`.

## Helpful references in repo

- `README.md`
- `docs/architecture.md`
- `docs/development.md`
- `docs/deployment.md`
- `docs/configuration.md`
- `docs/runbook.md`
