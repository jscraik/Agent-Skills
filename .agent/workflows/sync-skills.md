---
description: Sync agent skills to all runtimes (Antigravity, Claude Code, Codex) and repair broken slash-command discovery
---

# /sync-skills

Rebuilds the skill projection for all agent runtimes and restores Antigravity slash-command discovery when `/` shows no skills.

## When to use

- Skills are missing from the Antigravity `/` slash-command menu
- You added a new skill and want it live without restarting
- `~/.gemini/antigravity/skills` symlink is missing or stale
- MCP tools are not showing up in Antigravity
- You want to verify the full sync chain is healthy

---

## Steps

// turbo
1. Run skill sync from the repo root:
```bash
bash /Users/jamiecraik/dev/Agent-Skills/Infrastructure/scripts/sync_skills.sh
```

// turbo
2. Sync MCP config for Antigravity:
```bash
python3 /Users/jamiecraik/dev/Agent-Skills/Infrastructure/scripts/sync_mcp.py
```

// turbo
3. Verify the output links are correct:
```bash
echo "=== skills symlink ===" && ls -la ~/.gemini/antigravity/skills
echo "=== skills.txt ===" && cat ~/.gemini/antigravity/skills.txt
echo "=== skill count ===" && ls ~/.gemini/antigravity/skills/ | wc -l
```

4. Confirm results — expected:
   - `~/.gemini/antigravity/skills` → symlink to `…/Agent-Skills/skills-antigravity`
   - `skills.txt` contains the path to `skills-antigravity/`
   - Skill count ≥ 80
   - No `WARN` or `REFUSED` lines in sync output

5. If skill count is 0 or symlink is missing, run the diagnostic:
```bash
python3 /Users/jamiecraik/dev/Agent-Skills/Infrastructure/scripts/diagnose_skill.py --all 2>&1 | head -40
```

6. **Restart Antigravity** or type `/refresh` in this chat to pick up the updated skill list.

---

## Invariants (do not break)

- `skills-antigravity/` must NOT be a symlink (security guard will abort sync)
- `~/.gemini/antigravity/skills` must resolve inside the repo root
- MCP config at `~/.gemini/antigravity/mcp_config.json` must be valid JSON after step 2

## Error codes

| Symptom | Error | Fix |
|---------|-------|-----|
| `Refusing to use symlinked path` | `POLICY_FAIL` | Remove stale symlink: `rm skills-antigravity && mkdir skills-antigravity` |
| `cat: mcp_config.json: No such file or directory` | `SYSTEM_ERROR` | Re-run step 2; check `~/.codex/config.toml` exists |
| Skills count = 0 after sync | `VALIDATION_ERROR` | Check `skill_files_cmd` category dirs exist (`auth/`, `backend/`, etc.) |
| `tomli` import error | `SYSTEM_ERROR` | `pip3 install tomli` |
