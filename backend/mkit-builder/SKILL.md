---
name: mkit-builder
description: "Create MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools, resources, and prompts. The quality of an MCP server is measured by how well it enables LLMs to accomplish real-world tasks safely, reliably, and with predictable outputs.. Use when Use this skill when the task matches its description and triggers.."
---

# MCP Server Development Guide (Gold Standard, Dec 2025)

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md


## Overview

Create MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools, resources, and prompts. The quality of an MCP server is measured by how well it enables LLMs to accomplish real-world tasks safely, reliably, and with predictable outputs.

## philosophy
- Prioritize safe, discoverable tool surfaces with structured outputs.
- Prefer least-privilege defaults; escalate only with explicit user intent.
- Keep behavior deterministic, observable, and easy to verify.

## inputs
- Target service or API, required operations, and auth constraints.
- Desired stack and transport (TypeScript SDK/FastMCP; stdio/streamable HTTP).
- For mKit: repo path, desired change (tools/auth/billing/UI/deploy), and env setup.

## outputs
- Plan or implementation steps with file paths and tool registrations.
- Schema-backed tool definitions with annotations and error handling guidance.
- Include schema_version when describing schema-bound outputs.
- Verification steps and commands tailored to the target stack.

## constraints
- Follow GOLD standards and repo CODESTYLE guidance.
- Ask before adding dependencies or changing system-wide settings.
- Avoid secrets in code; use documented entry points and routing patterns.

## validation
- Run relevant checks (lint/typecheck/tests/inspector) or state why not run.
- For skills: run quick_validate and skill_gate; run evals when applicable.
- Stop at the first failed gate unless the user asks for full-run diagnostics.

## examples
- "Add a paid MCP tool to mKit that requires Stripe entitlement."
- "Wire a new OAuth provider into the mKit worker routes."
- "Design an MCP server for GitHub issues with typed schemas."
- "Audit an MCP server for schema and tool annotation issues."

## Scripts (when to use)
- `scripts/connections.py`: analyze or validate connector/auth flows for MCP integrations.
- `scripts/evaluation.py`: run evaluation workflows for MCP server outputs.
- `scripts/example_evaluation.xml`: sample evaluation input file.
- `scripts/requirements.txt`: dependencies for the scripts above.

Use these scripts when you need deterministic checks or repeatable evaluation steps; document inputs, outputs, and expected artifacts in your response.

## Variation rules
- Vary tool granularity by user workflows (atomic vs workflow tools).
- Use different transports by deployment context (stdio vs streamable HTTP).
- Prefer smaller payloads for latency-sensitive clients.

## Anti-patterns to avoid
- Returning unstructured output without schemas.
- Overloading tools with mixed responsibilities.
- Skipping auth or relying on implicit permissions.

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

# Gold Standard Checklist (Compact)

- Protocol compliance: latest spec, JSON Schema 2020-12, streamable HTTP or stdio
- Structured outputs: `outputSchema` + `structuredContent` + text JSON fallback
- Discoverability: consistent tool names, concise descriptions, `title`/`icons`
- Safety: read-only defaults, precise annotations, clear errors, strict auth
- Data quality: stable field names, pagination, filtering, and resource links
- Testability: schema contract tests, golden snapshots, inspector validation

---

# Process

## 🚀 High-Level Workflow

Creating a high-quality MCP server involves four main phases:

### Phase 0: Review & Fix Existing Implementations

Use this phase when the user asks to audit an MCP server, identify bugs, or propose fixes.

**Scope first:**
- Identify the stack: TypeScript SDK or FastMCP (https://github.com/punkpeye/fastmcp)
- Confirm transport (streamable HTTP vs stdio) and deployment target
- List current tools, resources, and prompts and compare to intended use cases

**Common bug patterns to check:**
- Missing/invalid `inputSchema` or `outputSchema` (not JSON Schema 2020-12)
- `structuredContent` missing or not matching `outputSchema`
- Tool annotations incorrect (readOnly/destructive/idempotent/openWorld)
- Pagination and filtering inconsistencies across list tools
- Auth bypasses (tokens accepted without `aud`/`iss` validation)
- Widget rendering issues (wrong `mimeType`, missing template URI, CSP blocked)
- Stale UI bundles due to cache and unchanged template URI

**Fix workflow:**
1) Reproduce with MCP Inspector or a minimal tool call
2) Add or correct schema contracts and structured outputs
3) Align tool metadata for discoverability and safety
4) Add regression tests (schema contract + golden snapshots)

**Gold standard checklist:**
- Use [🧪 Review & Fix Checklist](references/review_fix_checklist.md) as the baseline for 2025 compliance.
- Use [🛠 Review & Fix Recipes](references/review_fix_recipes.md) for diagnosis and fixes.
- Use [🧭 Common Fixes Matrix](references/common_fixes_matrix.md) for quick triage.
- Use [🧱 Apps SDK Requirements](references/apps_sdk_requirements.md) for ChatGPT Apps-specific compliance.
- If Apps SDK is in scope, run an explicit Apps SDK audit (see below).

**Apps SDK audit (quick):**
- `/mcp` public HTTPS, Streamable HTTP preferred, SSE legacy only
- `text/html+skybridge` templates and `_meta["openai/outputTemplate"]`
- CSP set and minimal; widget data split (`structuredContent` vs `_meta`)
- Tool handlers idempotent and safe on retry

### Phase 0.5: mKit Boilerplate (Cloudflare Workers)

Use this path when the user asks to implement or extend the mKit MCP boilerplate.

- Load [🧰 mKit Boilerplate Guide](references/mkit_boilerplate.md) for repo-specific structure and commands.
- Confirm target outcomes: tool additions, auth provider wiring, billing enablement, Apps SDK UI pages, or deployment.
- Prefer the documented entry points and registration patterns to avoid breaking worker routing.

### Phase 1: Deep Research and Planning

#### 1.1 Understand Modern MCP Design (2025+)

**API Coverage vs. Workflow Tools:**
Balance comprehensive API endpoint coverage with specialized workflow tools. Workflow tools can be more convenient for specific tasks, while comprehensive coverage gives agents flexibility to compose operations. Performance varies by client—some clients benefit from code execution that combines basic tools, while others work better with higher-level workflows. When uncertain, prioritize comprehensive API coverage.

**Tool Naming and Discoverability:**
Clear, descriptive tool names help agents find the right tools quickly. Use consistent prefixes (e.g., `github_create_issue`, `github_list_repos`) and action-oriented naming.

**Context Management:**
Agents benefit from concise tool descriptions and the ability to filter/paginate results. Design tools that return focused, relevant data. Some clients support code execution which can help agents filter and process data efficiently.

**Actionable Error Messages:**
Error messages should guide agents toward solutions with specific suggestions and next steps.

**First-class Outputs:**
Prefer structured outputs with schemas and provide a text fallback for compatibility. Favor stable, machine-consumable fields over free-form text when possible.

**Resources and Prompts:**
Use resources for read-only data and prompts for reusable interaction patterns. Tools should do the minimum work needed and delegate context to resources where possible.

#### 1.2 Study MCP Protocol Documentation (Latest Spec)

**Navigate the MCP specification:**

Start with the sitemap to find relevant pages: `https://modelcontextprotocol.io/sitemap.xml`

Then fetch specific pages with `.md` suffix for markdown format (e.g., `https://modelcontextprotocol.io/specification/draft.md`).

Key pages to review (latest revision first):
- Specification overview and architecture
- Transport mechanisms (streamable HTTP, stdio)
- Tool, resource, and prompt definitions
- Authorization (OAuth 2.1, Protected Resource Metadata, Resource Indicators, PKCE)

#### 1.3 Study Framework Documentation

**Recommended stack:**
- **Language**: TypeScript (high-quality SDK support and good compatibility in many execution environments e.g. MCPB. Plus AI models are good at generating TypeScript code, benefiting from its broad usage, static typing and good linting tools)
- **Transport**: Streamable HTTP for remote servers, using stateless JSON (simpler to scale and maintain, as opposed to stateful sessions and streaming responses). stdio for local servers. Use SSE only for backwards compatibility.

**Load framework documentation:**

- **MCP Best Practices**: [📋 View Best Practices](references/mcp_best_practices.md) - Core guidelines (updated for 2025 spec)

**For TypeScript (recommended):**
- **TypeScript SDK**: Use WebFetch to load `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md`
- [⚡ TypeScript Guide](references/node_mcp_server.md) - TypeScript patterns and examples

**For Python:**
- **Python SDK**: Use WebFetch to load `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`
- [🐍 Python Guide](references/python_mcp_server.md) - Python patterns and examples

**UI (optional, separate from Apps SDK):**
- **MCP UI**: `https://github.com/MCP-UI-Org/mcp-ui.git` (optional UI components/patterns, not required for Apps SDK)
- [🧭 MCP UI vs Apps SDK](references/mcp_ui_vs_apps_sdk.md) - when to use each

#### 1.4 Plan Your Implementation

**Understand the API:**
Review the service's API documentation to identify key endpoints, authentication requirements, and data models. Use web search and WebFetch as needed.

**Tool Selection:**
Prioritize comprehensive API coverage. List endpoints to implement, starting with the most common operations.

**Auth Plan (HTTP servers):**
If the server is HTTP-based and requires auth, design for OAuth 2.1 with Protected Resource Metadata discovery and Resource Indicators. Plan for PKCE, short-lived tokens, and strict audience validation. Avoid token passthrough.

**Auth0 Implementation:**
Use [🔐 Auth + Security (Auth0)](references/auth_security_auth0.md) for concrete setup steps, validation rules, and token handling patterns.

---

### Phase 2: Implementation

#### 2.1 Set Up Project Structure

See language-specific guides for project setup:
- [⚡ TypeScript Guide](references/node_mcp_server.md) - Project structure, package.json, tsconfig.json
- [🐍 Python Guide](references/python_mcp_server.md) - Module organization, dependencies

#### 2.2 Implement Core Infrastructure

Create shared utilities:
- API client with authentication
- Error handling helpers
- Response formatting (JSON/Markdown)
- Pagination support

#### 2.3 Implement Tools

For each tool:

**Input Schema:**
- Use Zod (TypeScript) or Pydantic (Python)
- Include constraints and clear descriptions
- Add examples in field descriptions
- Ensure `inputSchema` is a valid JSON Schema object. For tools with no params, use `{ "type": "object", "additionalProperties": false }`.

**Output Schema:**
- Define `outputSchema` where possible for structured data
- Use `structuredContent` in tool responses (TypeScript SDK feature)
- Helps clients understand and process tool outputs
- For compatibility, return serialized JSON in a TextContent block alongside `structuredContent`

**Tool Description:**
- Concise summary of functionality
- Parameter descriptions
- Return type schema
- Consider `title` and `icons` for display in UIs

**Implementation:**
- Async/await for I/O operations
- Proper error handling with actionable messages
- Support pagination where applicable
- Return both text content and structured data when using modern SDKs
- Use resource links or embedded resources when a tool naturally returns documents or files

**Annotations:**
- `readOnlyHint`: true/false
- `destructiveHint`: true/false
- `idempotentHint`: true/false
- `openWorldHint`: true/false

**Capabilities (Optional but Modern):**
- Sampling: server-side tools can request client LLM completions for assistive workflows
- Elicitation: form and URL-based user input flows for secure data capture
- Tasks: long-running operations with resumable/pollable execution

---

### Phase 3: Review and Test

#### 3.1 Code Quality

Review for:
- No duplicated code (DRY principle)
- Consistent error handling
- Full type coverage
- Clear tool descriptions

#### 3.2 Build and Test

**TypeScript:**
- Run `npm run build` to verify compilation
- Test with MCP Inspector: `npx @modelcontextprotocol/inspector`

**Python:**
- Verify syntax: `python -m py_compile your_server.py`
- Test with MCP Inspector

See language-specific guides for detailed testing approaches and quality checklists. Add contract tests for JSON Schema input/output and golden snapshots for structuredContent.

---

### Phase 4: Create Evaluations

After implementing your MCP server, create comprehensive evaluations to test its effectiveness.

**Load [✅ Evaluation Guide](references/evaluation.md) for complete evaluation guidelines.**

#### 4.1 Understand Evaluation Purpose

Use evaluations to test whether LLMs can effectively use your MCP server to answer realistic, complex questions.

#### 4.2 Create 10 Evaluation Questions

To create effective evaluations, follow the process outlined in the evaluation guide:

1. **Tool Inspection**: List available tools and understand their capabilities
2. **Content Exploration**: Use READ-ONLY operations to explore available data
3. **Question Generation**: Create 10 complex, realistic questions
4. **Answer Verification**: Solve each question yourself to verify answers

#### 4.3 Evaluation Requirements

Ensure each question is:
- **Independent**: Not dependent on other questions
- **Read-only**: Only non-destructive operations required
- **Complex**: Requiring multiple tool calls and deep exploration
- **Realistic**: Based on real use cases humans would care about
- **Verifiable**: Single, clear answer that can be verified by string comparison
- **Stable**: Answer won't change over time

#### 4.4 Output Format

Create an XML file with this structure:

```xml
<evaluation>
  <qa_pair>
    <question>Find discussions about AI model launches with animal codenames. One model needed a specific safety designation that uses the format ASL-X. What number X was being determined for the model named after a spotted wild cat?</question>
    <answer>3</answer>
  </qa_pair>
<!-- More qa_pairs... -->
</evaluation>
```

---

# Reference Files

## 📚 Documentation Library

Load these resources as needed during development:

### Core MCP Documentation (Load First)
- **MCP Protocol**: Start with sitemap at `https://modelcontextprotocol.io/sitemap.xml`, then fetch specific pages with `.md` suffix
- **Tools spec**: Pay attention to JSON Schema 2020-12, `outputSchema`, `structuredContent`, tool `title`/`icons`, and resource links
- **Authorization spec**: OAuth 2.1, Protected Resource Metadata, Resource Indicators, PKCE, token handling
- [📋 MCP Best Practices](references/mcp_best_practices.md) - Universal MCP guidelines including:
  - Server and tool naming conventions
  - Response format guidelines (JSON vs Markdown)
  - Pagination best practices
  - Transport selection (streamable HTTP vs stdio)
  - Security and error handling standards
  - Structured outputs and schema contract testing

### SDK Documentation (Load During Phase 1/2)
- **Python SDK**: Fetch from `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`
- **TypeScript SDK**: Fetch from `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md`

### Language-Specific Implementation Guides (Load During Phase 2)
- [🐍 Python Implementation Guide](references/python_mcp_server.md) - Complete Python/FastMCP guide with:
  - Server initialization patterns
  - Pydantic model examples
  - Tool registration with `@mcp.tool`
  - Complete working examples
  - Quality checklist

- [⚡ TypeScript Implementation Guide](references/node_mcp_server.md) - Complete TypeScript guide with:
  - Project structure
  - Zod schema patterns
  - Tool registration with `server.registerTool`
  - Complete working examples
  - Quality checklist

### Evaluation Guide (Load During Phase 4)
- [✅ Evaluation Guide](references/evaluation.md) - Complete evaluation creation guide with:
  - Question creation guidelines
  - Answer verification strategies
  - XML format specifications
  - Example questions and answers
  - Running an evaluation with the provided scripts

- [🧰 mKit Boilerplate Guide](references/mkit_boilerplate.md) - Cloudflare Workers boilerplate structure, commands, and integration points
### Additional Reference Patterns
- [🔐 Auth + Security (Auth0)](references/auth_security_auth0.md) - OAuth 2.1 setup and validation
- [🧩 Tool Result Patterns](references/tool_result_patterns.md) - errors, pagination, resources, structured output
- [🧪 Review & Fix Checklist](references/review_fix_checklist.md) - gold-standard audit checklist (Dec 31 2025)
- [🛠 Review & Fix Recipes](references/review_fix_recipes.md) - diagnosis and fixes (TS SDK + FastMCP)
- [🧭 Common Fixes Matrix](references/common_fixes_matrix.md) - symptom to fix map
- [🧷 FastMCP vs TS SDK Parity](references/fastmcp_ts_parity_checklist.md) - consistency checklist
- [🧪 Test Command Recipes](references/test_command_recipes.md) - quick verification commands
- [🚀 Deployment & Distribution](references/deployment_distribution.md) - npm, tunnels, Workers, prod hosting
- [🧱 Apps SDK Requirements](references/apps_sdk_requirements.md) - OpenAI Apps SDK compliance
- [🛡 Reliability & Ops Runbook](references/reliability_ops_runbook.md) - SLOs, metrics, incident response
- [🧾 Spec vs SEP Notes](references/spec_vs_sep_notes.md) - resolve conflicts between spec and proposals

## When to use
- Use this skill when the task matches its description and triggers.
- If the request is outside scope, route to the referenced skill.


## Inputs
- User request details and any relevant files/links.


## Outputs
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.


## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.


## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.


## Philosophy
- Favor clarity, explicit tradeoffs, and verifiable outputs.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.
