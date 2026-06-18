---
description: Sync Agent Skills Kit projections and repair Codex skill discovery
---

# /sync-skills

Rebuilds the Agent Skills Kit workspace projection and refreshes Codex runtime links when skills are missing or stale.

## When to use

- Skills are missing from Codex runtime discovery
- You added a new skill and want it live without restarting
- `~/.agents/skills` or `~/.codex/skills` points at a stale projection
- You want to verify the workspace and user sync chain is healthy

---

## Steps

// turbo
1. Refresh the workspace projection from the repo root:

```bash
./bin/ask skills sync --scope workspace --json --robot
```

// turbo
2. Refresh user runtime links:

```bash
./bin/ask skills sync --scope user --json --robot
```

// turbo
3. Verify projected runtime discovery:

```bash
./bin/ask skills list --json --robot
./bin/ask skills load-preview --json --robot
```

// turbo
4. Verify the user links resolve into this checkout:

```bash
ls -la ~/.agents/skills ~/.codex/skills
```

5. Confirm expected results:
   - Workspace sync reports success
   - User sync reports success
   - Runtime links resolve to the current checkout projection
   - No `WARN` or `REFUSED` lines in sync output

6. If skill count is 0 or a link is missing, run diagnostics:

```bash
./bin/ask repo doctor --json --robot
./bin/ask repo closeout --changed --json --robot
```

7. Restart the Codex session if runtime discovery still shows a stale skill list after sync and diagnostics pass.

---

## Invariants (do not break)

- Edit canonical skill sources under `Skills/**` or `Plugins/**/skills/**`, not generated runtime projections.
- `.agents/skills/**` is a generated runtime projection in this repo.
- `~/.agents/skills` and `~/.codex/skills` must resolve to the current approved projection.

## Error codes

| Symptom | Error | Fix |
|---------|-------|-----|
| Runtime link points at another checkout | `POLICY_FAIL` | Re-run user sync from the intended checkout |
| Skill list is stale after sync | `VALIDATION_ERROR` | Run repo doctor and inspect runtime link output |
| `./bin/ask` is unavailable | `SYSTEM_ERROR` | Run `bash scripts/bootstrap-ask.sh --json` |
| Sync output includes `REFUSED` | `POLICY_FAIL` | Stop and fix the named ownership or projection blocker |
