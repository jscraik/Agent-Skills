# Extended guidance

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
