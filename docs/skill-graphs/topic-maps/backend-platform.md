---
type: moc
name: backend-platform
description: "Skills for backend engineering, API design, cloud infrastructure, authentication, and deployment — primarily Cloudflare Workers, MCP, and CI/CD pipelines."
covers:
  - backend-services
  - mcp-servers
  - cloudflare
  - auth
  - ci-cd
  - secrets
---

# Backend & Platform

> Skills for backend engineering, API design, cloud infrastructure, authentication, and deployment.

## Table of Contents
- [Backend Services & APIs](#backend-services--apis)
- [MCP Servers](#mcp-servers)
- [Cloud & Deployment](#cloud--deployment)
- [Authentication & Security (Runtime)](#authentication--security-runtime)
- [Secrets & Credentials](#secrets--credentials)
- [CI/CD & Git](#cicd--git)

---

## Backend Services & APIs

- [[backend-engineer]] — Plan and review safe backend extensions for existing services (Cloudflare Workers + Hono primary).
- [[cli-spec]] — Plan and draft CLI UX and surface area: commands, flags, help text, output formats.
- [[workers-mcp]] — Create and deploy production-ready MCP servers on Cloudflare Workers with auth, billing, and operational guardrails.
- [[mcp-builder]] — Create general-purpose MCP servers and tool schemas for standard integrations without OAuth/billing.
- [[oak-api]] — Build Oak Curriculum API-driven learning experiences, especially for child-facing ChatGPT Apps SDK workflows.

## MCP Servers

- [[workers-mcp]] — Cloudflare Workers-hosted MCP servers with auth, billing, and ops guardrails.
- [[mcp-builder]] — General-purpose MCP server scaffolding for standard integrations.
- [[chatgpt-apps]] — Build, scaffold, and troubleshoot ChatGPT Apps SDK applications combining an MCP server and widget UI.

## Cloud & Deployment

- [[cloudflare-deploy]] — Deploy applications to Cloudflare using Workers, Pages, and related platform services.
- [[cf-crawl]] — Crawl websites with Cloudflare Browser Rendering's /crawl API, export markdown or JSON results.
- [[bootstrap]] — Bootstrap a local development environment from a GitHub repository URL.
- [[fix-mise]] — Diagnose and repair mise trust/runtime failures and reconcile `~/.config/mise/config.toml`.

## Authentication & Security (Runtime)

- [[create-auth]] — Build Better Auth integrations for TS/JS apps with secure defaults.
- [[best-practices]] — Review Better Auth setups and highlight secure integration best practices.
- [[1password]] — Plan, validate, and use 1Password CLI for secret injection and auth.

## Secrets & Credentials

- [[1password]] — 1Password CLI setup for secret injection: `op run/read/inject`, env vars, `.env` files.

## CI/CD & Git

- [[circleci]] — CircleCI migration, orchestration, testing, deployment, optimization, secrets, and config policy.
- [[gh-workflow]] — GitHub lifecycle: intake, issue fixing, PR prep, review, CI diagnosis, and server-side merge.
- `github:github` (plugin) — Connector-first GitHub triage and PR/issue orientation.
- [[release]] — Create and publish a new project release (semver) via `just release X.Y.Z`.
- [[using-git-worktrees]] — Create and validate Codex/Claude CLI git worktree workflows with safe branch/sync strategies.

---

## Cross-links

- Planning a new backend? [[brainstorming]] → [[backend-engineer]] → [[cli-spec]].
- Deploying an MCP server? [[mcp-builder]] or [[workers-mcp]] → [[cloudflare-deploy]].
- Setting up auth? [[create-auth]] → [[best-practices]] → [[1password]] for secrets.
- Topic maps: [[frontend-ui]] | [[security-ops]] | [[agent-ops]] | [[product-strategy]]
