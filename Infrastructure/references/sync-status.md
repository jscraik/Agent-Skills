# Skills Sync Status

**Canonical source**: `~/dev/agent-skills/.agents/skills`

**Codex source**: `~/dev/agent-skills/skills-codex`

## Auto-synced paths

Running `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh` automatically creates/updates:

| Tool | Path | Status |
|------|------|--------|
| **Codex** | `~/.codex/skills` | ✅ auto-synced |
| **OpenAI Agents/Codex** | `~/.agents/skills` | ✅ auto-synced |
| **OpenAI Codex (compat)** | `~/.codex/skills` | ✅ auto-synced |
| **Codex (flat)** | `~/.openai/codex/skills` | ✅ auto-synced (copy) |
| **Codex (legacy)** | `~/.codex/skills` | ✅ auto-synced |
| **Codex path file** | `~/.openai/codex/skills.txt` | ✅ auto-synced |

## Verification

```bash
ls -la ~/.codex/skills | head -n 5
ls -la ~/.agents/skills | head -n 5
ls -la ~/.codex/skills | head -n 5
ls -la ~/.openai/codex/skills | head -n 5
cat ~/.openai/codex/skills.txt
```
