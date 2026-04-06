# CLI Lifecycle and Error Standards (2026 Update)

To achieve "Gold Standard" status, a CLI must manage its own evolution and provide machine-readable error surfaces that allow autonomous agents to self-correct.

## 1. Regeneration Metadata
High-performance CLIs often generate artifacts (scaffolds, clients, or binaries). These artifacts should be self-documenting.

- **The `--from` Pattern:** If your CLI generates code or config, embed the original command used to create it within the file (as a comment or metadata field). 
- **Self-Recovery:** Support a mode (e.g., `cmd generate --from <file> --dry-run`) that reads this metadata and prints the command required to recreate the artifact.
- **Traceability:** This allows agents to understand the "provenance" of a file and update it automatically when the CLI version changes.

## 2. Universal Response Envelope
Move beyond raw JSON arrays. Every machine-readable output should use a standard "Envelope" structure.

**The `CallResult` Schema:**
```json
{
  "status": "success" | "error" | "partial",
  "trace_id": "uuid-v4",
  "metadata": {
    "version": "1.2.3",
    "latency_ms": 45,
    "next_steps": ["cmd action --id 123"]
  },
  "data": { ... },
  "errors": [
    {
      "code": "VAL_001",
      "message": "Invalid region: us-north",
      "fix_suggestion": "Try 'us-east' or 'eu-west'",
      "help_url": "https://docs.link/errors/VAL_001"
    }
  ]
}
```

## 3. Interface Evolution (The "Fold" Pattern)
As a CLI grows, commands often need to be renamed or consolidated. Protect user scripts and agent loops using these strategies:

- **Muscle Memory Aliases:** When renaming `list-tools` to `list`, keep the old name as a hidden alias. It should work but not appear in the primary `--help` output.
- **Flag Migration:** Use aliases for flags during transitions (e.g., `--insecure` as a hidden alias for `--allow-http`).
- **Coercion Hardening:** Provide explicit flags like `--raw-strings` or `--no-coerce`. This prevents the CLI from "guessing" types (like turning a numeric string ID into an integer), which is a common cause of breaking changes in agent workflows.

## 4. Auth Orchestration
Design auth commands to be "Agent-Detecting."

- **Headless Handshake:** If the CLI detects it is not in a TTY, `auth login` should output a JSON object containing a `login_url` and a `poll_interval` instead of opening a browser automatically.
- **Contextual Config:** Allow `--config` and `--root` flags to be passed to all commands to override global auth state for specific agent sub-tasks.
