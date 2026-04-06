# Advanced CLI Patterns (2026 Update)

These patterns represent the "Gold Standard" for technical and agent-native CLIs, inspired by modern tool-calling protocols (like MCP) and high-performance developer tools.

## 1. Type-Safe Help Signatures
Move beyond traditional columnar help text. For developer-focused tools, use TypeScript-style signatures to convey requirements and types concisely.

- **Required vs Optional:** Use `?` for optional parameters.
- **Literal Types:** Show enums as literals: `format: "json" | "text" | "yaml"`.
- **JSDoc Integration:** Embed brief parameter descriptions as block comments `/** ... */`.

**Example:**
```typescript
skylink vm create(name: string, region: "us-east" | "eu-west", tags?: string[])
/**
 * @param name - Unique identifier for the VM
 * @param region - Deployment target
 */
```

## 2. Progressive Help Disclosure
For complex commands with 10+ flags, do not overwhelm the user (or the agent's context window).

- **Default View:** Show only "Required" and "Common" flags.
- **Summarization:** Replace excessive optional flags with a summary line: `// +12 optional parameters. Use --all-parameters to see more.`
- **Schema-First:** Support `--schema` to output the full machine-readable definition.

## 3. The "Minting" Pattern (Schema-to-CLI)
Design your CLI as a thin wrapper around a JSON-schema definition. 

- **Validation Parity:** Use the same JSON-schema validator for both the API and the CLI.
- **Auto-Generated Flags:** Mapping camelCase schema keys to kebab-case CLI flags should be deterministic.
- **Ad-Hoc Overrides:** Allow users to pass a raw JSON string as an argument to handle complex nested objects directly without individual flags.

## 4. Interaction Flexibility
Modern CLIs should be forgiving of different shell delimiters and user "muscle memory."

- **Multi-Delimiter Support:** Accept `key=value`, `key:value`, and `--key value` interchangeably.
- **Muscle Memory Aliases:** Maintain hidden aliases for legacy commands (e.g., `ls` for `list`) to maintain flow without cluttering the primary UI.

## 5. Agent-Native Context Discipline
Optimize for autonomous callers by strictly managing what data enters the stream.

- **Field Masking (`--fields`):** Allow the caller to request only specific keys to save tokens.
- **Binary Offloading:** Never dump binary data or images to `stdout`. Use `--save-assets <dir>` to offload large payloads to disk and return a reference path in the JSON.
- **Self-Correcting Hints:** If an agent provides an invalid flag, the error should include a `did_you_mean` field in the JSON response.
