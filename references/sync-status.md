# Skills Sync Status

**Canonical source**: `/Users/jamiecraik/dev/agent-skills/skills`

## Auto-synced paths

Running `scripts/sync_skills.sh` automatically creates/updates:

| Tool | Path | Status |
|------|------|--------|
| **Claude Code** | `~/.claude/skills` | ✅ auto-synced |
| **OpenAI Codex** | `~/.agent/skills` | ✅ auto-synced |
| **OpenAI Agents/Codex** | `~/.agents/skills` | ✅ auto-synced |

## Verification

```bash
ls -la ~/.claude/skills | head -n 5
ls -la ~/.agent/skills | head -n 5
ls -la ~/.agents/skills | head -n 5
```
