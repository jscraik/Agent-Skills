# Extended guidance

### Core MCP Documentation (Load First)
- **MCP Protocol**: Start with sitemap at `https://modelcontextprotocol.io/sitemap.xml`, then fetch specific pages with `.md` suffix
- **Tools spec**: Pay attention to JSON Schema 2020-12, `outputSchema`, `structuredContent`, tool `title`/`icons`, and resource links
- **Authorization spec**: OAuth 2.1, Protected Resource Metadata, Resource Indicators, PKCE, token handling
- [📋 MCP Best Practices](./reference/mcp_best_practices.md) - Universal MCP guidelines including:
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
- [🐍 Python Implementation Guide](./reference/python_mcp_server.md) - Complete Python/FastMCP guide with:
  - Server initialization patterns
  - Pydantic model examples
  - Tool registration with `@mcp.tool`
  - Complete working examples
  - Quality checklist

- [⚡ TypeScript Implementation Guide](./reference/node_mcp_server.md) - Complete TypeScript guide with:
  - Project structure
  - Zod schema patterns
  - Tool registration with `server.registerTool`
  - Complete working examples
  - Quality checklist

### Evaluation Guide (Load During Phase 4)
- [✅ Evaluation Guide](./reference/evaluation.md) - Complete evaluation creation guide with:
  - Question creation guidelines
  - Answer verification strategies
  - XML format specifications
  - Example questions and answers
  - Running an evaluation with the provided scripts

### Additional Reference Patterns
- [🔐 Auth + Security (Auth0)](./reference/auth_security_auth0.md) - OAuth 2.1 setup and validation
- [🧩 Tool Result Patterns](./reference/tool_result_patterns.md) - errors, pagination, resources, structured output
- [🧪 Review & Fix Checklist](./reference/review_fix_checklist.md) - gold-standard audit checklist (Dec 31 2025)
- [🛠 Review & Fix Recipes](./reference/review_fix_recipes.md) - diagnosis and fixes (TS SDK + FastMCP)
- [🧭 Common Fixes Matrix](./reference/common_fixes_matrix.md) - symptom to fix map
- [🧷 FastMCP vs TS SDK Parity](./reference/fastmcp_ts_parity_checklist.md) - consistency checklist
- [🧪 Test Command Recipes](./reference/test_command_recipes.md) - quick verification commands
- [🚀 Deployment & Distribution](./reference/deployment_distribution.md) - npm, tunnels, Workers, prod hosting
- [🧱 Apps SDK Requirements](./reference/apps_sdk_requirements.md) - OpenAI Apps SDK compliance
- [🛡 Reliability & Ops Runbook](./reference/reliability_ops_runbook.md) - SLOs, metrics, incident response
- [🧾 Spec vs SEP Notes](./reference/spec_vs_sep_notes.md) - resolve conflicts between spec and proposals

## Scope and triggers
- Use this skill when the task matches its description and triggers.
- If the request is outside scope, route to the referenced skill.


## Required inputs
- User request details and any relevant files/links.


## Deliverables
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


## Anti-patterns
- Avoid vague guidance without concrete steps.
- Do not invent results or commands.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.

---

## References
- `references/contract.yaml`
- `references/evals.yaml`

## Philosophy
- Prefer clarity, explicit tradeoffs, and verifiable outputs.

## Anti-patterns
- Inventing results or skipping validation steps.
- Proceeding without required inputs or scope confirmation.
