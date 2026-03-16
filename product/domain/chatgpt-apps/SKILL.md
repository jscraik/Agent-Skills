---
name: chatgpt-apps
description: Build, scaffold, refactor, and troubleshoot ChatGPT Apps SDK applications that combine an MCP server and widget UI. Use when Codex needs to design tools, register UI resources, wire the MCP Apps bridge or ChatGPT compatibility APIs, apply Apps SDK metadata or CSP or domain settings, or produce a docs-aligned project scaffold grounded in current OpenAI docs.
---

# ChatGPT Apps
## Overview

Scaffold ChatGPT Apps SDK apps with a docs-first, example-first workflow.

Current baseline markers:
- Prefer the OpenAI Responses API when current docs indicate it is the supported baseline for the target integration.
- Align MCP server behavior with the Model Context Protocol baseline represented by the 2025-06-18 specification line and 2025-11-25 release lineage.

Primary outputs:
- app archetype and architecture choice
- tool plan (schemas + annotations + metadata)
- scaffold guidance for MCP server + widget
- validation report + local dev steps
- deployment/submission checklist (when requested)

## Mandatory Docs-First Workflow

Use `$openai-docs` first whenever building or changing a ChatGPT Apps SDK app.

1. Fetch current Apps SDK docs before writing code:
   - `apps-sdk/build/mcp-server`
   - `apps-sdk/build/chatgpt-ui`
   - `apps-sdk/build/examples`
   - `apps-sdk/plan/tools`
   - `apps-sdk/reference`
2. For new apps, also fetch `apps-sdk/quickstart` and check official examples before inventing a custom scaffold.
3. For deploy/launch tasks, fetch:
   - `apps-sdk/deploy`
   - `apps-sdk/deploy/submission`
   - `apps-sdk/app-submission-guidelines`
4. Cite docs URLs in your response and prefer current docs when older patterns conflict.
5. If search is weak, fetch canonical pages directly and continue.

If `$openai-docs` is unavailable, use:

- `mcp__openaiDeveloperDocs__search_openai_docs`
- `mcp__openaiDeveloperDocs__fetch_openai_doc`

Read `references/apps-sdk-docs-workflow.md` for suggested doc queries and a compact checklist.
Use the other `references/*.md` docs as needed for archetypes, validation contract, search/fetch standard, upstream example selection, and `window.openai` mappings.

## Prompt Guidance

Use prompts that pair this skill with `$openai-docs`.

- `Use $chatgpt-apps with $openai-docs to scaffold a ChatGPT app for <use case> with a <TS/Python> MCP server and <React/vanilla> widget.`
- `Use $chatgpt-apps with $openai-docs to adapt the closest official Apps SDK example into a ChatGPT app for <use case>.`

When responding, ask for or infer these inputs before coding:

- use case and primary flows
- read-only vs mutating tools
- demo/internal vs production/public target
- backend/UI stack + auth needs
- CSP domains + hosting target

## Classify The App Before Choosing Code

Before choosing examples or scaffolds, select one primary archetype and state it:

- `tool-only`
- `vanilla-widget`
- `react-widget`
- `interactive-decoupled`
- `submission-ready`

Infer unless blocked. Use the archetype to choose UI need, repo layout, example source, and validation depth.

Read `references/app-archetypes.md` for the decision rubric.

## Default Starting-Point Order

Prefer in order:
1. official OpenAI examples
2. version-matched `@modelcontextprotocol/ext-apps` examples
3. `scripts/scaffold_node_ext_apps.mjs` fallback
Adapt close upstream examples instead of generating a large custom scaffold.

## Build Workflow

### 0. Classify The App Archetype

Pick one primary archetype first. Escalate to `submission-ready` only for public launch/review asks.

### 1. Plan Tools Before Code

- One job per tool with explicit schemas and constraints.
- Descriptions should start with “Use this when...”.
- Set annotations correctly (`readOnlyHint`, `destructiveHint`, `openWorldHint`, `idempotentHint` when true).
- For connector/data/sync apps, default to standard `search` + `fetch`.

Read `references/search-fetch-standard.md` when `search` and `fetch` may be relevant.

### 2. Choose an App Architecture

- Use minimal demo pattern for prototypes.
- Use decoupled data/render pattern for production.
- For decoupled apps: data tools return reusable `structuredContent`; render tools attach `_meta.ui.resourceUri` (+ optional `_meta["openai/outputTemplate"]`).

### 2a. Start From An Upstream Example When One Fits

- Check official OpenAI examples first.
- Use `@modelcontextprotocol/ext-apps` examples when lower-level MCP wiring is needed.
- Copy the smallest matching example; patch to current docs (tool metadata, CSP, URI versioning, run steps).

Read `references/upstream-example-workflow.md` for the selection and adaptation rubric.

### 2b. Use the Starter Script When a Low-Dependency Fallback Helps

Use `scripts/scaffold_node_ext_apps.mjs` only for quick Node + vanilla fallback when no upstream example is a better fit.
- Run only after docs fetch.
- State why fallback is chosen.
- Patch generated output to current docs and user requirements.

### 3. Scaffold the MCP Server

Generate a server that:

- Registers a widget resource/template with the MCP Apps UI MIME type (`text/html;profile=mcp-app`) or the SDK constant (`RESOURCE_MIME_TYPE`) when using `@modelcontextprotocol/ext-apps/server`
- Registers tools with clear names, schemas, titles, and descriptions
- Returns `structuredContent` (model + widget), `content` (model narration), and `_meta` (widget-only data) intentionally
- Keeps handlers idempotent or documents non-idempotent behavior explicitly
- Includes tool status strings (`openai/toolInvocation/*`) when helpful in ChatGPT

Keep `structuredContent` concise. Move large or sensitive widget-only payloads to `_meta`.

### 4. Scaffold the Widget UI

Use MCP Apps bridge first, then add `window.openai` extensions when they improve UX.
- Listen for `ui/notifications/tool-result`
- Render from `structuredContent`
- Use `tools/call` for component-initiated tool calls
- Use `ui/update-model-context` only when model-visible context should change

#### API Surface Guardrails

- Wrapper helpers (for example `app.*`) are convenience layers, not canonical API.
- Prefer documented `window.openai.*` and MCP bridge primitives in guidance.
- If wrappers are referenced, map them back to canonical APIs.

### 5. Add Resource Metadata and Security

Set resource metadata deliberately on the widget resource/template:

- `_meta.ui.csp` with exact `connectDomains` and `resourceDomains`
- `_meta.ui.domain` for app submission-ready deployments
- `_meta.ui.prefersBorder` (or OpenAI compatibility alias when needed)
- Optional `openai/widgetDescription` to reduce redundant narration

Avoid `frameDomains` unless iframe embeds are core to the product.

### 5a. Enforce A Minimum Working Repo Contract

Every generated repo should satisfy a minimal contract:
- repo shape matches archetype
- reachable `/mcp` endpoint with wired tools
- clear tool metadata and correct widget bridge usage
- `search` + `fetch` defaults for connector/data/sync scenarios
- explicit statement of what validation ran vs did not run

### 6. Validate the Local Loop

Run validation ladder in order:
1. static contract + syntax/compile + local `/mcp` health checks (when feasible)
2. MCP Inspector tool/widget checks
3. ChatGPT developer-mode test through HTTPS tunnel
4. retry/idempotency and host-event update checks
If dependencies are not installed, still run low-cost checks and call out skipped steps.

### 7. Connect and Test in ChatGPT (Developer Mode)

Include explicit ChatGPT dev setup:
- local server: `http://localhost:<port>/mcp`
- HTTPS tunnel URL + `/mcp` path
- enable Developer Mode in ChatGPT settings
- create app from remote MCP URL
- refresh app after tool/metadata updates
Prefer “app” wording while acknowledging older “connector” terminology when needed.

### 8. Plan Production Hosting and Deployment

For deployment/launch asks, provide guidance on:
- stable public HTTPS endpoint (not tunnel)
- low-latency `/mcp` streaming
- externalized secrets management
- logging/latency/error visibility + basic observability
- re-testing hosted endpoint in ChatGPT Developer Mode

### 9. Prepare Submission and Publish (Public Apps Only)

Only for public listing:
- follow `apps-sdk/deploy/submission` + `apps-sdk/app-submission-guidelines`
- keep private/internal apps in Developer Mode
- confirm org verification + Owner-role prerequisites
- require production endpoint + submission-ready CSP
- prepare metadata/screenshots/privacy/support/test artifacts
- provide review-safe demo credentials (if auth required)

## Interactive State Guidance

For long-lived/repeated widget interactions, use `references/interactive-state-sync-patterns.md` and apply:
- state snapshots + monotonic tokens (`stateVersion`, `resetCount`)
- idempotent handlers + clear `structuredContent` vs `_meta` boundaries

## Output Expectations

For direct scaffold requests, provide plan + implementation in one pass. Default response order:
1. archetype + tool/architecture plan
2. chosen upstream/fallback starting point
3. docs URLs used
4. file tree + implementation (server + widget)
5. validation results and local run/test steps
6. deployment/submission guidance (if requested)
7. risks, gaps, and follow-ups

## References

- `references/app-archetypes.md`
- `references/apps-sdk-docs-workflow.md`
- `references/interactive-state-sync-patterns.md`
- `references/repo-contract-and-validation.md`
- `references/search-fetch-standard.md`
- `references/upstream-example-workflow.md`
- `references/window-openai-patterns.md`
- `scripts/scaffold_node_ext_apps.mjs`

## See Also

| Skill | When to use together |
|---|---|
| [[mcp-builder]] | Build the underlying MCP server the Apps SDK connects to |
| [[workers-mcp]] | Host the MCP server on Cloudflare Workers |
| [[openai-docs]] | Reference official Apps SDK documentation |
| [[oak-api]] | Integrate Oak curriculum content into ChatGPT App workflows |
| [[fixing-metadata]] | Ensure App pages have correct meta and CSP headers |

**Topic map:** [[backend-platform]]

<!-- decision-feedback-protocol:v2 -->
## Decision Quality Feedback

For non-trivial outcomes, collect AskQuestion parity feedback (`request_user_input`) before closing:
- `decision`: `accepted|partial|rejected|deferred`
- `outcome`: `good|neutral|bad|unknown`
- `confidence`: `high|medium|low`
Persist with `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.

## Philosophy

- Prefer official OpenAI docs and examples before custom scaffolding.
- Keep app architectures minimal, explicit, and testable.
- Prioritize stable tool contracts and safe widget/server boundaries.

## When to use

- Building, refactoring, or troubleshooting ChatGPT Apps SDK apps.
- Designing MCP tools + widget interactions for ChatGPT.
- Preparing deployment or submission-ready app structures.

## Inputs

- Intended app use case and core user flow.
- Stack choices (server language, widget approach).
- Deployment target, auth requirements, and domain/CSP constraints.

## Outputs

- App archetype and implementation plan.
- Tool design + metadata recommendations.
- Scaffold or patch guidance for server/widget files.
- Validation checklist and run instructions.

## Constraints

- Use docs-first behavior and cite relevant OpenAI docs pages.
- Do not assume wrapper APIs are canonical without mapping to documented surfaces.
- Keep recommendations within ChatGPT Apps SDK + MCP scope.
- Redact secrets, tokens, API keys, credentials, PII, and other sensitive data by default.

## Validation

- Verify tool schemas, annotations, and widget metadata are coherent.
- Confirm minimum repo contract checks (shape, endpoint, tool wiring, run path).
- Call out what was validated vs not validated.
- Fail fast: stop at the first failed gate and do not proceed with risky changes.

## Anti-patterns

- Avoid skipping docs retrieval before generating or changing app code.
- DO NOT overengineer custom scaffolds when a close upstream example exists.
- NEVER treat undocumented wrapper helpers as canonical APIs.
- Common pitfall: generic template-first outputs that ignore app-specific constraints.
- Warning sign: repetitive, cookie-cutter recommendations that converge on one pattern.

## Variation and adaptation

- Vary recommendations by app archetype, risk level, and deployment context.
- Use different, context-specific approaches for prototypes vs production submissions.
- Customize tool and widget plans to the actual user flow instead of reusing generic templates.
- Aim for unique outputs and avoid repetition when requirements differ.

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, be creative, and push boundaries when it improves outcomes safely.

## Examples

- "Use $chatgpt-apps with $openai-docs to scaffold a submission-ready app with React UI and an MCP server."
- "Use $chatgpt-apps to refactor this tool-only app into a decoupled render/data architecture."

## Folded Legacy Modes (Core60)
<!-- core60-folded-modes:v1:start -->
This skill owns legacy capability from retired skills. Use these modes when requests match prior behavior.

- `production-gate` from `product/domain/chatgpt-apps-production-checklist`: Turn ChatGPT Apps implementation work into a production-ready checklist with concrete tasks, tests, widget changes, and tool-result patte...

Deep legacy details: `references/folded-legacy-modes-core60.md`.
<!-- core60-folded-modes:v1:end -->

## Quality Uplift
- Philosophy and approach: apply a clear framework, explain why, consider tradeoff decisions, and use a practical mental model for execution.
- Guiding question: Why is this the right context-specific path?
- Guiding question: What tradeoff is being made and how is risk reduced?
- Guiding question: How do we verify behavior end-to-end before completion?
- Anti-pattern warning: avoid generic or repetitive output; DO NOT hide failures; NEVER skip validation; avoid common pitfall and mistake patterns.
- Anti-pattern warning: treat incorrect or wrong assumptions as blockers, and call out anti-pattern risks explicitly.
- Variation: vary recommendations by context-specific constraints; adapt, customize, and use different approaches when constraints differ.
- Variation: prefer diverse, unique alternatives and avoid repetition or cookie-cutter template convergence.
- Empowerment: enable users to explore options confidently, be capable and creative, unlock safe choices, and empower execution.
