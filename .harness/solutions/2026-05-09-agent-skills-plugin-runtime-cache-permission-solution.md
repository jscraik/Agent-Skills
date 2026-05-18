# Plugin Runtime Cache Permission Solution

Date: 2026-05-09
Repository: agent-skills
Lifecycle Source: he-compound
Status: implemented

## Problem

`./bin/ask skills sync --scope workspace --projection rooted --json` could refresh rooted skill projections and command handles while still warning:

```text
PLUGIN_CACHE_REFRESH_PERMISSION_BLOCKED
```

The blocked write was under:

```text
.agents/plugins-runtime/cache/agent-skills-local/harness-engineering/.codex-repo-plugin-source
```

That made the lifecycle state ambiguous: rooted projections could be current while Codex picker plugin cache copies were stale.

## Evidence

Fact:
- A no-op write probe to the cache path failed with `PermissionError: [Errno 1] Operation not permitted` in the normal sandbox.
- The same probe succeeded when the command declared write access to `.agents/plugins-runtime/cache`.
- Rooted skill projection sync can succeed independently of plugin runtime cache refresh.

Interpretation:
- The failure is a session/write-root permission boundary, not proof that canonical skill sources or rooted projections are stale.
- ASK should expose plugin runtime cache refresh as a distinct mode so agents can run normal projection sync without conflating it with cache refresh proof.

Assumption:
- Codex picker behavior still benefits from `.agents/plugins-runtime/cache/**` freshness even when generated command handles are current.

## Implemented Fix

ASK now separates the two sync concerns:

```text
./bin/ask skills sync --scope workspace --projection rooted --plugin-cache-refresh skip
./bin/ask skills sync --scope workspace --projection rooted --plugin-cache-refresh only
```

The default remains best-effort:

```text
./bin/ask skills sync --scope workspace --projection rooted --plugin-cache-refresh auto
```

When the plugin runtime cache lane is blocked, ASK reports:

```text
rerun with write access to .agents/plugins-runtime/cache.
```

The sync plan also declares the required cache write root so operators and agents can tell which permission is missing.

## Runtime Configuration

The Codex workspace writable roots were updated to include:

```text
/Users/jamiecraik/dev/agent-skills/.agents/plugins-runtime/cache
```

This is intended to make future workspace sessions able to refresh HE/plugin-factory/skill-factory local plugin runtime cache copies without ad hoc sandbox escalation.

## Future Agent Guidance

- Treat `PLUGIN_CACHE_REFRESH_PERMISSION_BLOCKED` as plugin picker cache proof failure, not automatic skill projection failure.
- Use `--plugin-cache-refresh skip` when the goal is normal rooted projection sync and cache write access is unavailable.
- Use `--plugin-cache-refresh only` after granting write access to `.agents/plugins-runtime/cache`.
- Do not hand-edit `.agents/plugins-runtime/cache/**`; it is generated runtime cache state.
- Do not claim full plugin picker freshness unless the cache refresh lane ran without the permission warning.

## Validation Expectations

Required checks:
- `python3 -m pytest Infrastructure/tests/test_ask_skills_sync_security.py -q`
- `python3 -m pytest Infrastructure/tests/test_sync_skills_shell_projection.py -q`
- `./bin/ask skills sync --scope workspace --projection rooted --plugin-cache-refresh skip --dry-run --json --robot`
- `./bin/ask skills sync --scope workspace --projection rooted --plugin-cache-refresh only --dry-run --json --robot`

If Codex config writable roots are changed, also run the config drift guard from `/Users/jamiecraik/dev/configs`:

```text
bash .codex/skills/config-drift-guard/scripts/run_guard_checks.sh
```
