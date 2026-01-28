# Skills Sync Status Checklist

Use this checklist to confirm that **all tools** are synced from the canonical skills directory:

**Canonical source**
- `/Users/jamiecraik/dev/agent-skills/skills`

## Expected target paths
- **Claude Code**: `~/.claude/skills` → symlink to canonical
- **Codex**: `~/.codex/skills` → symlink to canonical
- **Copilot**: `~/.copilot/skills` → symlink to canonical
- **Kimi**: `~/.config/agents/skills` → symlink to canonical (explicit)
- **Cursor**: `~/.cursor/skills` → **mirror copy** (avoid symlink issues)

## Sync commands
```bash
# 1) Standard repo sync (symlinks + SKILL.md regeneration)
/Users/jamiecraik/dev/agent-skills/scripts/sync_skills.sh

# 2) Ensure Kimi explicit skills path exists
mkdir -p ~/.config/agents
ln -sfn /Users/jamiecraik/dev/agent-skills/skills ~/.config/agents/skills

# 3) Cursor mirror (safe)
mkdir -p ~/.cursor/skills
rsync -a /Users/jamiecraik/dev/agent-skills/skills/ ~/.cursor/skills/

# 4) Cursor strict mirror (optional, removes stale skills)
rsync -a --delete /Users/jamiecraik/dev/agent-skills/skills/ ~/.cursor/skills/
```

## Verification
```bash
ls -la /Users/jamiecraik/dev/agent-skills/skills | head -n 5
ls -la ~/.claude/skills | head -n 5
ls -la ~/.codex/skills | head -n 5
ls -la ~/.copilot/skills | head -n 5
ls -la ~/.config/agents/skills | head -n 5
ls -la ~/.cursor/skills | head -n 5
```

## Notes
- Cursor may not reliably follow symlinks for skills. Prefer a **mirror copy** into `~/.cursor/skills`.
- If you need to override Kimi’s skill discovery, use `--skills-dir` in Kimi CLI.
