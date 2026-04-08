---
name: mcp-builder
description: Create general-purpose MCP servers and tool schemas for standard integrations. Use when building MCP services without OAuth/billing/Apps UI requirements.
metadata:
  skill-type: scaffolding_templates
---

# MCP Builder

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
- Follow the Model Context Protocol line represented by the 2025-06-18 baseline and 2025-11-25 release lineage when examples differ.
- Treat `inputSchema`, `outputSchema`, and structured outputs as product surface, not optional extras.
- Default to safe, discoverable, composable tools before adding workflow-heavy abstractions.

## When to use
- Build or extend an MCP server for a standard integration.
- Design tools, resources, or prompts for a service that does not need OAuth, billing, or Apps SDK UI.
- Review an existing MCP server for schema quality, discoverability, safety, or protocol fit.

## When not to use
- Workers-hosted, auth-heavy, or billing-aware MCP products. Use [`workers-mcp`](/backend/workers-mcp/SKILL.md) when that operational surface matters.
- ChatGPT Apps SDK apps or widget/UI-integrated experiences.
- Generic backend work with no MCP contract in scope.

## Required inputs
- Target service and auth method.
- Transport choice: stdio or Streamable HTTP.
- Candidate tool list and intended schemas.
- Constraints: rate limits, network access, data sensitivity, pagination, retries, and hosting environment.

## Deliverables
- MCP server plan or scaffold shape.
- Tool/resource/prompt surface with naming, schema, and safety expectations.
- Verification plan using Inspector, sample calls, or contract tests.
- Risks and rollout notes for auth, retries, redaction, and backward compatibility.

## Philosophy
- Safe defaults first: read-only and idempotent until proven otherwise.
- Structured outputs beat prose blobs.
- Tool names should be obvious enough that another agent can find them without tribal knowledge.
- Prefer comprehensive, composable coverage before inventing narrow one-off helpers.

## Workflow
1. Clarify service scope, transport, and runtime boundary.
2. Define the tool surface with stable nouns, verbs, and schema contracts.
3. Decide what should be a tool, resource, or prompt instead of collapsing everything into one layer.
4. Encode pagination, filtering, and error semantics explicitly.
5. Keep auth least-privilege and redaction requirements visible from the first draft.
6. Validate with Inspector or equivalent sample calls before claiming the server is usable.
7. Add regression checks for schemas and representative outputs when the server is non-trivial.

## Validation
- Verify every public tool has a valid `inputSchema` and, when appropriate, an `outputSchema`.
- Verify `structuredContent` matches the documented contract.
- Verify destructive or stateful tools are explicitly marked and gated.
- Verify the skill uses bundled `references/` and `scripts/` helpers when the folder provides them.
- Reuse any skill `assets/` scaffolds rather than inventing parallel templates.

## Constraints
- Do not print secrets, tokens, or sensitive data; redact by default.
- Prefer least-privilege auth scopes and narrow host/network access.
- Do not describe unsupported protocol behavior as if it already exists.
- Avoid returning massive unstructured payloads when schemas or focused outputs are viable.

## Anti-patterns
- Tool surfaces that hide multiple unrelated actions behind one vague command.
- Shipping destructive tools without explicit confirmation and rollback guidance.
- Treating schema validation as something to do after implementation.
- Optimizing for one demo path while making real-world discovery and composability worse.

## Examples
- "Design an MCP server for a task tracker with list, get, create, and search tools."
- "Review this MCP server and tell me where the schemas and structured outputs are weak."

## See Also

| Skill | When to use together |
|---|---|
| [[workers-mcp]] | Host the MCP server on Cloudflare when cloud deployment is needed |
| [[chatgpt-apps]] | Connect the MCP server to a ChatGPT Apps SDK integration |
| [[openai-docs]] | Use official MCP schema docs when designing tool schemas |
| [[backend-engineer]] | Add MCP tools to an existing backend service |
| [[security-best-practices]] | Apply security hardening to MCP server endpoints |

**Topic map:** [[backend-platform]]

## Remember
- Good MCP servers are easy to discover, easy to trust, and easy to compose.
- Schema discipline is part of usability.
- The smallest good server is the one another agent can call correctly on the first try.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## Failure mode
- If the tool contract, auth model, or runtime target is not grounded in repo evidence, stop, report the blocker, and fall back to a contract-definition step before drafting or changing the MCP server.
