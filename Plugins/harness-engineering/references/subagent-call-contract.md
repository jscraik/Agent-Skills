# Subagent Call Contract

Harness Engineering stages must resolve helper roles through the same path before calling or recommending subagents.

## Required Flow
1. Load the selected stage policy from `Plugins/harness-engineering/references/routing-map.json`.
2. Read available roles from `~/.codex/agents/manifest.json`, supporting both a top-level array and an object with `.agents[]`.
3. Use the exact role names from `routing-map.json`; do not add `he-*` aliases or rename roles before lookup.
4. Call `spawn_agent(agent_type=<role>)` only for roles present in the manifest and allowed by the selected stage policy.
5. If spawning is unavailable, unsafe, or roles are missing, continue inline and tell the user which roles were mapped, available, and missing.
6. Route missing role creation or installation to `[[codex-agent-creator]]` before rerunning delegated coverage.

## Trigger Rules
- `always`: call available baseline roles when spawning is safe.
- `conditional`: call available mapped roles only when the user requested delegation or risk signals justify specialist coverage.
- `manual-only`: do not call helpers automatically; recommend exact roles when delegation would help.

## Traceability Fields
Each stage closeout should include these fields or equivalent prose:

- `subagent_policy`
- `roles_used`
- `roles_recommended`
- `roles_missing`
- `git_staging_status` when the stage wrote artifacts
