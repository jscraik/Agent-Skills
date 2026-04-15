# Extended guidance

## Example Prompts

- "Design a probe set for React web app component inspection"
- "Validate the evidence paths in this findings.json"
- "Generate a SHA256 manifest for this run directory"

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Resources

### Documentation

- `README.md` - Project overview and quickstart
- `docs/reference/GOLD_STANDARD.md` - Gold Industry Standard compliance
- `AGENTS.md` - Agent instructions and workflows
- `docs/guides/SECURITY.md` - Security policy and vulnerability reporting
- `Infrastructure/config/scope.example.yaml` - Scope configuration template

### Schemas

- `Infrastructure/config/schemas/authorization.schema.json` - Authorization artifact structure
- `Infrastructure/config/schemas/probe-plan.v2.schema.json` - Probe plan validation
- `Infrastructure/config/schemas/findings.v2.schema.json` - Findings structure
- `Infrastructure/config/schemas/manifest.v2.schema.json` - Integrity manifest structure

### Probe Catalog

- `probes/catalog.json` - All available probes and probe sets

### Validation Scripts

- `Infrastructure/scripts/validate_catalog.py` - Validate probe catalog
- `Infrastructure/scripts/validate_manifest.py` - Validate integrity manifest
- `Infrastructure/scripts/validate_evidence.py` - Validate evidence paths in findings

### MCP Integration

- `Infrastructure/scripts/mcp_server.py` - MCP server for AI agent integration

## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.

## Anti-patterns
- Avoid vague guidance without concrete steps.
- Do not invent results or commands.
- Do not add features outside the agreed scope.
