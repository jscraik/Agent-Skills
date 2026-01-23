# Integration Surfaces

## Client Surfaces
- Web: React + Vite + Tailwind + TS/JS
- Apps SDK UI / OpenAI widgets

## Contract-First Integration
- REST: OpenAPI 3.1 as source of truth
- GraphQL: schema-first with typed clients
- Use codegen for TS clients

## MCP Tools
- Define tool schemas with clear inputs/outputs and error shapes
- Keep tools idempotent where possible
- Provide rate limits and auth requirements
- Follow MCP JSON-RPC conventions and protocol versioning
- Use MCP protocol versions formatted as YYYY-MM-DD; current is 2025-11-25
- Use JSON-RPC 2.0 message shapes; prefer JSON Schema 2020-12 for tool schemas

## CLI
- If CLI is required, follow create-cli conventions:
  - command tree, flags, output modes, exit codes
  - --json for machine output
  - --dry-run for safe operations

## Storybook (if UI components are affected)
- Provide mock API responses and schema-driven fixtures
- Ensure a11y and interaction states are covered

## Standards References
- Use `references/tech-standards.md` for official documentation links and specs.
