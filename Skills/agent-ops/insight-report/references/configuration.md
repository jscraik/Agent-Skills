# Configuration Guide

Environment variables and setup options for OpenAI Codex.

## Important Corrections

**Common mistakes in Codex documentation:**

| Incorrect | Correct |
|-----------|---------|
| `codex -p "prompt"` | `codex exec "prompt"` (or `codex exec --full-auto "prompt"`) |
| `.codex/settings.json` | `~/.codex/config.toml` |
| `OPENAI_TELEMETRY_ENABLED=1` | `codex features enable general_analytics` |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `INSIGHTS_MODEL` | `qwen3-coder` | Ollama model for LLM analysis |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | unset | Default Ollama model for local inference |

**Note:** Unlike Codex, Codex does NOT use `CODEX_OTEL_ENABLED` or `OPENAI_TELEMETRY_ENABLED` environment variables. Telemetry is controlled via feature flags.

## Telemetry Setup

**Important**: OpenAI Codex runs tools server-side for security. Detailed tool executions are not stored locally.

To enable telemetry:

```bash
# Enable the analytics feature flag
codex features enable general_analytics
```

Or add to `~/.codex/config.toml`:
```toml
general_analytics = true
```

**Status:** `general_analytics` is currently under development (default: false).

### Data Location

With telemetry enabled, check these locations:
```
~/.codex/sessions/           # Session metadata + conversation events
~/.codex/agents/             # Agent-related data
~/.codex/archived_sessions/  # Archived session data
```

## Codex CLI Reference

### Interactive Mode
```bash
codex                              # Start interactive session
codex "fix the bug"               # Start with initial prompt
codex -m gpt-5.3-codex "prompt"   # Use specific model
```

### Headless/Non-Interactive Mode
```bash
# Basic headless execution
codex exec "fix lint errors"

# With auto-approval (no prompts)
codex exec --full-auto "fix lint errors"

# With specific sandbox mode
codex exec --sandbox workspace-write "prompt"

# Read from stdin
echo "fix this" | codex exec
```

### Configuration
```bash
# Override config value
codex -c model="o3" "prompt"
codex -c 'sandbox_permissions=["disk-full-read-access"]' "prompt"

# Use specific profile
codex -p profile_name "prompt"
```

### Feature Flags
```bash
# List all features
codex features list

# Enable a feature
codex features enable general_analytics
codex features enable codex_hooks

# Disable a feature
codex features disable feature_name
```

### MCP Servers
```bash
# Add an MCP server
codex mcp add server_name -- command

# Example
codex mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /path
```

## Config File: ~/.codex/config.toml

Example configuration:
```toml
model_provider = "openai"
model = "gpt-5.3-codex-spark"
approval_policy = "on-request"
sandbox_mode = "workspace-write"

# Enable telemetry
general_analytics = true

# Enable hooks (for pre-commit style automation)
codex_hooks = true

[sandbox_workspace_write]
network_access = true
writable_roots = ["/path/to/project"]

[shell_environment_policy]
inherit = "none"
include_only = ["PATH", "HOME", "USER"]
```

## Ollama Setup (for Local LLM Analysis)

### Installation
```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Or via Homebrew
brew install ollama
```

### Model Download
```bash
ollama pull qwen3-coder
ollama pull qwen3.5
ollama pull phi4
```

### Start Server
```bash
ollama serve
# Or background: brew services start ollama
```

## CLI Options for Insight Report

```bash
python3 skills/insight-report/Infrastructure/scripts/run_insight_report.py [options]

Options:
  --days N          Days of data to analyze (default: 7)
  --model MODEL     Ollama model for LLM analysis (default: qwen3-coder)
  --skip-llm        Skip LLM analysis (metrics only)
  --no-open         Don't open browser after generation
  --verbose         Show progress details
  --max-sessions N  Max sessions to analyze (default: 200)
  --max-facets N    Max sessions for LLM facet extraction (default: 50)
```

## Troubleshooting

### "No session data found"
```bash
# Check if sessions exist
ls -la ~/.codex/sessions/
ls -la ~/.codex/archived_sessions/

# Check history
wc -l ~/.codex/history.jsonl
```

### "Ollama not available"
```bash
curl http://localhost:11434/api/tags
ollama serve
# Or use --skip-llm flag
python3 ... --skip-llm
```

### Enable detailed logging
```bash
codex features enable runtime_metrics
```

## Privacy Note

OpenAI Codex's default privacy model:
- **Always available**: Session count, message count, timing data from `~/.codex/sessions/`
- **Requires feature flag**: General analytics (`general_analytics`)
- **Server-side**: Tool executions (not logged locally)
- **Always local**: LLM analysis via Ollama (no data leaves your machine)

## Key Differences from Codex

| Feature | Codex | OpenAI Codex |
|---------|-------------|--------------|
| Config file | `~/.codex/settings.json` | `~/.codex/config.toml` |
| Headless | `codex -p "prompt"` | `codex exec "prompt"` |
| Telemetry env | `CODEX_OTEL_ENABLED=1` | Feature flag: `general_analytics` |
| Tool logs | `~/.codex/projects/` | Server-side (not local) |
| Hooks | `AGENTS.md` hooks | `codex_hooks` feature flag |
