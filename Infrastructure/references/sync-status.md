# Skills Sync Status

**Canonical source**: `~/dev/agent-skills/.agents/skills`

**Antigravity source**: `~/dev/agent-skills/skills-antigravity`

## Auto-synced paths

Running `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh` automatically creates/updates:

| Tool | Path | Status |
|------|------|--------|
| **Claude Code** | `~/.claude/skills` | ✅ auto-synced |
| **OpenAI Agents/Codex** | `~/.agents/skills` | ✅ auto-synced |
| **OpenAI Codex (compat)** | `~/.codex/skills` | ✅ auto-synced |
| **Antigravity (flat)** | `~/.gemini/antigravity/skills` | ✅ auto-synced (copy) |
| **Antigravity (legacy)** | `~/.antigravity/skills` | ✅ auto-synced |
| **Antigravity path file** | `~/.gemini/antigravity/skills.txt` | ✅ auto-synced |

## Verification

```bash
ls -la ~/.claude/skills | head -n 5
ls -la ~/.agents/skills | head -n 5
ls -la ~/.codex/skills | head -n 5
ls -la ~/.gemini/antigravity/skills | head -n 5
cat ~/.gemini/antigravity/skills.txt
```
